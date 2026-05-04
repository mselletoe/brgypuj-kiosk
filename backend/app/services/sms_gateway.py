"""
app/services/sms_gateway.py

Hardware SMS gateway driver for the A7670E GSM modem.
Communicates via AT commands over a serial connection.
Supports bulk sending with configurable retries, inter-message delays,
and signal strength checking before dispatch.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import List, Dict, Any

import serial

from app.core.config import settings

log = logging.getLogger(__name__)


# =================================================================================
# AT COMMAND HELPERS
# =================================================================================

def _ts() -> str:
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")


def _send_at(ser: serial.Serial, command: str, wait: float = 1.0) -> str:
    ser.write((command + "\r\n").encode())
    time.sleep(wait)
    raw = ser.read(ser.in_waiting or 1).decode(errors="ignore")
    log.debug("%s >> %s", _ts(), command)
    log.debug("%s << %s", _ts(), raw.strip())
    return raw


def _signal_ok(ser: serial.Serial) -> bool:
    csq = _send_at(ser, "AT+CSQ")
    try:
        value = int(csq.split("+CSQ:")[1].split(",")[0].strip())
        if value == 99:
            log.warning("%s Signal unknown (antenna issue?)", _ts())
            return False
        if value < 10:
            log.warning("%s Signal very weak (%d) — SMS may fail", _ts(), value)
            return False
        log.info("%s Signal ok (%d)", _ts(), value)
        return True
    except (IndexError, ValueError):
        log.warning("%s Could not parse CSQ response: %s", _ts(), csq)
        return False


# =================================================================================
# GATEWAY CLASS
# =================================================================================

class A7670EGateway:
    def __init__(
        self,
        port:        str   = None,
        baud:        int   = None,
        smsc:        str   = None,
        retries:     int   = None,
        send_wait:   float = None,
        inter_delay: float = None,
    ):
        self.port        = port        or getattr(settings, "SMS_PORT",        "/dev/ttyUSB1")
        self.baud        = baud        or getattr(settings, "SMS_BAUD",        115200)
        self.smsc        = smsc        or getattr(settings, "SMS_SMSC",        "+639180000101")
        self.retries     = retries     or getattr(settings, "SMS_RETRIES",     3)
        self.send_wait   = send_wait   or getattr(settings, "SMS_SEND_WAIT",   30.0)
        self.inter_delay = inter_delay or getattr(settings, "SMS_INTER_DELAY", 5.0)

    def _open(self) -> serial.Serial:
        ser = serial.Serial(self.port, self.baud, timeout=5)
        time.sleep(2)

        resp = _send_at(ser, "AT")
        if "OK" not in resp:
            ser.close()
            raise RuntimeError(f"Modem on {self.port} did not respond to AT")

        cpin = _send_at(ser, "AT+CPIN?")
        if "READY" not in cpin:
            ser.close()
            raise RuntimeError(f"SIM not ready: {cpin.strip()}")

        _send_at(ser, "AT+CMGF=1")
        # NOTE: Do NOT call AT+CSCA here.
        # The SMSC is already correctly stored on the SIM (as Unicode hex).
        # Overwriting it with a raw ASCII string corrupts it and causes send failures.

        return ser

    def _send_one(self, ser: serial.Serial, number: str, message: str) -> bool:
        for attempt in range(1, self.retries + 1):
            log.info("%s Attempt %d/%d → %s", _ts(), attempt, self.retries, number)

            ser.reset_input_buffer()
            ser.reset_output_buffer()

            # Step 1: Send AT+CMGS and wait explicitly for the '>' prompt.
            # Do NOT use a fixed sleep — the prompt can arrive after a variable delay.
            ser.write(f'AT+CMGS="{number}"\r\n'.encode())

            prompt_buf      = ""
            prompt_deadline = time.time() + 10  # up to 10s for '>'
            got_prompt      = False

            while time.time() < prompt_deadline:
                if ser.inWaiting():
                    prompt_buf += ser.read(ser.inWaiting()).decode(errors="ignore")
                if ">" in prompt_buf:
                    got_prompt = True
                    break
                time.sleep(0.2)

            if not got_prompt:
                log.warning(
                    "%s No '>' prompt received for %s (attempt %d) — buffer: %r",
                    _ts(), number, attempt, prompt_buf,
                )
                if attempt < self.retries:
                    time.sleep(5)
                continue

            # Step 2: Send message body + Ctrl-Z (0x1A)
            ser.write((message + chr(26)).encode())

            # Step 3: Poll for +CMGS: confirmation.
            # Do not bail on ERROR mid-stream — the modem sometimes echoes
            # intermediate status lines containing "ERROR" before the final
            # +CMGS: confirmation arrives.
            deadline = time.time() + self.send_wait
            buffer   = ""

            while time.time() < deadline:
                if ser.inWaiting():
                    chunk   = ser.read(ser.inWaiting()).decode(errors="ignore")
                    buffer += chunk
                    log.debug("%s << %s", _ts(), chunk.strip())

                if "+CMGS:" in buffer:
                    log.info("%s ✅ Sent to %s (attempt %d)", _ts(), number, attempt)
                    return True

                # Only treat ERROR as terminal once we've had enough time
                # for +CMGS: to arrive (i.e. after at least 5 seconds of waiting).
                if "ERROR" in buffer and (time.time() - (deadline - self.send_wait)) > 5:
                    log.warning(
                        "%s ERROR in buffer for %s (attempt %d): %r",
                        _ts(), number, attempt, buffer.strip(),
                    )
                    break

                time.sleep(0.3)

            log.warning("%s ❌ Attempt %d failed for %s", _ts(), attempt, number)
            if attempt < self.retries:
                time.sleep(5)

        log.error("%s FAILED all %d attempts for %s", _ts(), self.retries, number)
        return False

    def send_bulk(
        self,
        phone_numbers: List[str],
        message: str,
        on_progress=None,
    ) -> Dict[str, Any]:
        sent     = 0
        failed   = 0
        failures = []
        total    = len(phone_numbers)

        log.info("%s Starting bulk send: %d recipient(s)", _ts(), total)

        try:
            ser = self._open()
        except Exception as exc:
            log.error("%s Could not open modem: %s", _ts(), exc)
            if on_progress:
                on_progress(0, total, None, False, error=str(exc))
            return {
                "sent":     0,
                "failed":   total,
                "failures": phone_numbers,
                "error":    str(exc),
            }

        try:
            if not _signal_ok(ser):
                log.warning("%s Proceeding despite weak signal (will attempt anyway)", _ts())

            for i, number in enumerate(phone_numbers, 1):
                log.info("%s --- %d of %d: %s ---", _ts(), i, total, number)
                ok = self._send_one(ser, number, message)
                if ok:
                    sent += 1
                else:
                    failed += 1
                    failures.append(number)

                if on_progress:
                    on_progress(i, total, number, ok)

                if i < total:
                    log.info("%s ⏳ Waiting %ss before next...", _ts(), self.inter_delay)
                    time.sleep(self.inter_delay)

        finally:
            ser.close()

        log.info("%s Bulk send complete — ✅ %d sent, ❌ %d failed", _ts(), sent, failed)
        return {"sent": sent, "failed": failed, "failures": failures}


# =================================================================================
# SINGLETON ACCESSOR
# =================================================================================

_gateway: A7670EGateway | None = None


def get_gateway() -> A7670EGateway:
    global _gateway
    if _gateway is None:
        _gateway = A7670EGateway()
    return _gateway