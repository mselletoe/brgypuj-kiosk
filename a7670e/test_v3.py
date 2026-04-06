import serial
import time
from datetime import datetime

# ─────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────
PORT      = "COM12"
BAUD      = 115200
RECIPIENT = "+639603718944"


# ─────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────
def ts():
    """Return current timestamp string."""
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

def send_at(ser, command, wait=1):
    """Send an AT command and return the response."""
    ser.write((command + "\r\n").encode())
    time.sleep(wait)
    response = ser.read(ser.inWaiting()).decode(errors="ignore")
    print(f"{ts()} >> {command}")
    print(f"{ts()} << {response.strip()}")
    print()
    return response


# ─────────────────────────────────────────
# VERSION 6 — Send basic message only
# Stripped down: no SMSC, no retries,
# no diagnostics — just AT + send
# ─────────────────────────────────────────
def send_basic(message="Hello!", recipient=RECIPIENT):
    print(f"\n{ts()} ========== VERSION 6: Send Basic ==========")
    try:
        with serial.Serial(PORT, BAUD, timeout=5) as ser:
            time.sleep(2)
            send_at(ser, "AT")
            send_at(ser, "AT+CMGF=1")
            send_at(ser, f'AT+CMGS="{recipient}"', wait=2)
            print(f"{ts()} Sending message...")
            ser.write((message + chr(26)).encode())
            time.sleep(10)
            response = ser.read(ser.inWaiting()).decode(errors="ignore")
            print(f"{ts()} Response: {response.strip()}")
            if "+CMGS:" in response:
                print(f"{ts()} ✅ SUCCESS — Message sent to {recipient}")
            else:
                print(f"{ts()} ❌ FAILED — No confirmation received")
    except serial.SerialException as e:
        print(f"{ts()} ❌ Port error: {e}")


# ─────────────────────────────────────────
# RUN
# ─────────────────────────────────────────
if __name__ == "__main__":
    send_basic("good morning")