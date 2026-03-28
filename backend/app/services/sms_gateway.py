"""
app/services/sms_gateway.py
──────────────────────────────────────────────────────────────────────────────
A7670E serial modem gateway for the SMS Announcement feature.

Wraps the AT-command logic proven in test_v1.py / test_v2.py into a
production-ready class that sms_service.py calls via _dispatch_sms().

Configuration (set in your .env / settings):
    SMS_PORT        COM12          # Windows  | /dev/ttyUSB0 on Linux/RPi
    SMS_BAUD        115200
    SMS_SMSC        +639180000101  # Smart PH SMSC  |  +63917000000 Globe
    SMS_RETRIES     3              # per-number retry attempts
    SMS_SEND_WAIT   15             # seconds to wait for +CMGS: reply
    SMS_INTER_DELAY 5              # seconds between numbers in a bulk send
──────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import List, Dict, Any

import serial  # pyserial

from app.core.config import settings  # adjust import to your project layout

log = logging.getLogger(__name__)


# ============================================================================
# Internal helpers
# ============================================================================

def _ts() -> str:
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")


def _send_at(ser: serial.Serial, command: str, wait: float = 1.0) -> str:
    """
    Write an AT command to the modem and return its raw response.
    Mirrors the send_at() helper from test_v1.py / test_v2.py.
    """
    ser.write((command + "\r\n").encode())
    time.sleep(wait)
    raw = ser.read(ser.inWaiting()).decode(errors="ignore")
    log.debug("%s >> %s", _ts(), command)
    log.debug("%s << %s", _ts(), raw.strip())
    return raw


def _signal_ok(ser: serial.Serial) -> bool:
    """Return True if signal strength is usable (CSQ >= 10 and != 99)."""
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


# ============================================================================
# Public gateway class
# ============================================================================

class A7670EGateway:
    """
    Manages a single serial connection to the A7670E LTE modem and sends
    SMS messages one at a time (the modem is single-channel).

    Usage (called automatically by sms_service._dispatch_sms):
        gateway = A7670EGateway()
        result  = gateway.send_bulk(phone_numbers, message)
        # result → {"sent": N, "failed": M}
    """

    def __init__(
        self,
        port:        str   = None,
        baud:        int   = None,
        smsc:        str   = None,
        retries:     int   = None,
        send_wait:   float = None,
        inter_delay: float = None,
    ):
        self.port        = port        or getattr(settings, "SMS_PORT",        "COM12")
        self.baud        = baud        or getattr(settings, "SMS_BAUD",        115200)
        self.smsc        = smsc        or getattr(settings, "SMS_SMSC",        "+639180000101")
        self.retries     = retries     or getattr(settings, "SMS_RETRIES",     3)
        self.send_wait   = send_wait   or getattr(settings, "SMS_SEND_WAIT",   15.0)
        self.inter_delay = inter_delay or getattr(settings, "SMS_INTER_DELAY", 5.0)

    # ------------------------------------------------------------------ #
    # Private helpers                                                      #
    # ------------------------------------------------------------------ #

    def _open(self) -> serial.Serial:
        """Open the serial port and initialise the modem."""
        ser = serial.Serial(self.port, self.baud, timeout=5)
        time.sleep(2)  # give the modem time to settle after open

        # Basic handshake
        resp = _send_at(ser, "AT")
        if "OK" not in resp:
            ser.close()
            raise RuntimeError(f"Modem on {self.port} did not respond to AT")

        # SIM check
        cpin = _send_at(ser, "AT+CPIN?")
        if "READY" not in cpin:
            ser.close()
            raise RuntimeError(f"SIM not ready: {cpin.strip()}")

        # Text mode + SMSC
        _send_at(ser, "AT+CMGF=1")
        _send_at(ser, f'AT+CSCA="{self.smsc}"')

        return ser

    def _send_one(self, ser: serial.Serial, number: str, message: str) -> bool:
        """
        Send a single SMS, retrying up to self.retries times.
        Returns True on success, False after all retries fail.
        """
        for attempt in range(1, self.retries + 1):
            log.info(
                "%s Attempt %d/%d → %s",
                _ts(), attempt, self.retries, number,
            )
            _send_at(ser, f'AT+CMGS="{number}"', wait=2)
            ser.write((message + chr(26)).encode())  # chr(26) = Ctrl+Z = send

            # Wait for +CMGS: reply (may take up to send_wait seconds)
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
                time.sleep(5)  # back-off before retry

        log.error("%s FAILED all %d attempts for %s", _ts(), self.retries, number)
        return False

    # ------------------------------------------------------------------ #
    # Public interface                                                     #
    # ------------------------------------------------------------------ #

    def send_bulk(
        self,
        phone_numbers: List[str],
        message: str,
    ) -> Dict[str, Any]:
        """
        Send `message` to every number in `phone_numbers`.

        Returns:
            {"sent": int, "failed": int, "failures": List[str]}
        """
        sent     = 0
        failed   = 0
        failures = []

        log.info(
            "%s Starting bulk send: %d recipient(s)",
            _ts(), len(phone_numbers),
        )

        try:
            ser = self._open()
        except Exception as exc:
            log.error("%s Could not open modem: %s", _ts(), exc)
            return {
                "sent":     0,
                "failed":   len(phone_numbers),
                "failures": phone_numbers,
                "error":    str(exc),
            }

        try:
            # Optional: abort if signal is too weak
            if not _signal_ok(ser):
                log.warning(
                    "%s Proceeding despite weak signal (will attempt anyway)",
                    _ts(),
                )

            for i, number in enumerate(phone_numbers, 1):
                log.info(
                    "%s --- %d of %d: %s ---",
                    _ts(), i, len(phone_numbers), number,
                )
                ok = self._send_one(ser, number, message)
                if ok:
                    sent += 1
                else:
                    failed += 1
                    failures.append(number)

                # Inter-message delay (skip after the last one)
                if i < len(phone_numbers):
                    log.info("%s ⏳ Waiting %ss before next...", _ts(), self.inter_delay)
                    time.sleep(self.inter_delay)

        finally:
            ser.close()

        log.info(
            "%s Bulk send complete — ✅ %d sent, ❌ %d failed",
            _ts(), sent, failed,
        )
        return {"sent": sent, "failed": failed, "failures": failures}


# ============================================================================
# Module-level singleton (import and reuse across requests)
# ============================================================================

_gateway: A7670EGateway | None = None


def get_gateway() -> A7670EGateway:
    """Return the shared gateway instance (lazy-initialised)."""
    global _gateway
    if _gateway is None:
        _gateway = A7670EGateway()
    return _gateway