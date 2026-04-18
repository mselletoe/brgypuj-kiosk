import serial
import time
from datetime import datetime

# ─────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────
PORT = "COM12"
BAUD = 115200
DEFAULT_RECIPIENT = "+639152893228"
READ_DELAY = 1


# ─────────────────────────────────────────
# UTILITIES
# ─────────────────────────────────────────
def ts():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")


def log(direction, msg):
    print(f"{ts()} {direction} {msg}")


def read_response(ser, delay=READ_DELAY):
    time.sleep(delay)
    data = ser.read(ser.in_waiting or 1)
    return data.decode(errors="ignore").strip()


def send_at(ser, command, wait=READ_DELAY):
    ser.write((command + "\r\n").encode())
    time.sleep(wait)

    response = read_response(ser)

    log(">>", command)
    log("<<", response)

    return response


# ─────────────────────────────────────────
# MODEM SETUP
# ─────────────────────────────────────────
def wait_network(ser, timeout=30):
    log("..", "Waiting for network registration")

    start = time.time()

    while time.time() - start < timeout:
        resp = send_at(ser, "AT+CREG?")

        if ",1" in resp or ",5" in resp:
            log("OK", "Network registered")
            return True

        time.sleep(2)

    log("ERR", "Network NOT registered")
    return False


def setup_sms(ser):
    log("..", "Configuring SMS mode")

    ser.reset_input_buffer()

    send_at(ser, "AT")
    send_at(ser, "AT+CMGF=1")          # Text mode
    send_at(ser, 'AT+CSCS="GSM"')      # Charset
    send_at(ser, "AT+CSMP=17,167,0,0") # SMS settings

    # SMART already has correct SMSC from your diagnostics
    smsc = send_at(ser, "AT+CSCA?")

    if "ERROR" in smsc:
        log("WARN", "SMSC error detected (not forcing overwrite for SMART)")


# ─────────────────────────────────────────
# SMS SENDING
# ─────────────────────────────────────────
def send_sms(message, recipient=DEFAULT_RECIPIENT):
    log("==", "SMS TEST START")

    try:
        with serial.Serial(PORT, BAUD, timeout=10) as ser:
            time.sleep(2)

            setup_sms(ser)

            if not wait_network(ser):
                log("ERR", "Aborting SMS (no network)")
                return

            ser.reset_input_buffer()

            resp = send_at(ser, f'AT+CMGS="{recipient}"', wait=2)

            # extra safety check (some modems delay ">")
            if ">" not in resp:
                time.sleep(2)
                resp += read_response(ser)

            if ">" not in resp:
                log("ERR", "No CMGS prompt received")
                return

            log("..", "Sending message")

            ser.write((message + "\x1A").encode())  # CTRL+Z

            # IMPORTANT: wait longer for modem to process SMS
            time.sleep(8)

            result = read_response(ser, delay=2)

            log("==", "RESPONSE")
            print(result)

            if "+CMGS:" in result:
                log("OK", "SMS SENT SUCCESSFULLY")
            else:
                log("ERR", "SMS FAILED")

    except serial.SerialException as e:
        log("ERR", f"Serial error: {e}")


# ─────────────────────────────────────────
# RUN
# ─────────────────────────────────────────
if __name__ == "__main__":
    send_sms("SMS API Test 432")