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
        self.port = port or getattr(settings, "SMS_PORT", "/dev/ttyUSB1")
        self.baud        = baud        or getattr(settings, "SMS_BAUD",        115200)
        self.smsc        = smsc        or getattr(settings, "SMS_SMSC",        "+639180000101")
        self.retries     = retries     or getattr(settings, "SMS_RETRIES",     3)
        self.send_wait   = send_wait   or getattr(settings, "SMS_SEND_WAIT",   15.0)
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
        _send_at(ser, f'AT+CSCA="{self.smsc}"')

        return ser

    def _send_one(self, ser: serial.Serial, number: str, message: str) -> bool:
        for attempt in range(1, self.retries + 1):
            log.info(
                "%s Attempt %d/%d → %s",
                _ts(), attempt, self.retries, number,
            )

            ser.reset_input_buffer()
            ser.reset_output_buffer()

            _send_at(ser, f'AT+CMGS="{number}"', wait=4)
            ser.write((message + chr(26)).encode())  

            deadline = time.time() + self.send_wait
            buffer   = ""
            while time.time() < deadline:
                if ser.inWaiting():
                    buffer += ser.read(ser.inWaiting()).decode(errors="ignore")
                if "+CMGS:" in buffer:
                    log.info("%s ✅ Sent to %s (attempt %d)", _ts(), number, attempt)
                    return True
                if "ERROR" in buffer:
                    break
                time.sleep(0.5)

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