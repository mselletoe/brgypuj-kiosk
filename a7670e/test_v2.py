import serial
import time
from datetime import datetime

# ─────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────
PORT      = "COM12"             # Check Device Manager for correct COM port
BAUD      = 115200
RECIPIENT = "+639152893228"     # Single target phone number
SMSC      = "+639180000101"     # Smart SMSC | Globe: +63917000000

# Multiple recipients — add/remove numbers as needed
RECIPIENTS = [
    "+639457217155",    #ALLEAH
    "+639452017662",    #EMILY
    "+639152893228",    #KEANNO
    "+639673884442",    #KURU
    "+639954629650",    #LEI
    "+639565363411",    #OMIT
    "+639619082462",    #EMAN
    "+639683511548",    #BRENTY
    "+639509736143",    #IRISH
    "+639615329603",    #SEAN
    "+639455160881",    #JAMAE
    "+639488412621",    #JUSTINE
    "+639054616199",    #KENJO
    "+639771262133",    #BASTI
    "+639054148351",    #KENNY
    "+639774628138",    #MAYEL
    "+639212004733",    #MILDRED
]


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
# VERSION 1 — Basic send
# Simplest possible SMS, no extras
# ─────────────────────────────────────────
def basic(message="hi"):
    print(f"\n{ts()} ========== VERSION 1: Basic Send ==========")
    try:
        with serial.Serial(PORT, BAUD, timeout=5) as ser:
            time.sleep(2)
            send_at(ser, "AT")
            send_at(ser, "AT+CMGF=1")
            send_at(ser, f'AT+CMGS="{RECIPIENT}"', wait=2)
            print(f"{ts()} Sending message...")
            ser.write((message + chr(26)).encode())
            time.sleep(10)
            response = ser.read(ser.inWaiting()).decode(errors="ignore")
            print(f"{ts()} Response: {response.strip()}")
            print(f"{ts()} " + ("✅ SUCCESS" if "+CMGS:" in response else "❌ FAILED"))
    except serial.SerialException as e:
        print(f"{ts()} ❌ Port error: {e}")


# ─────────────────────────────────────────
# VERSION 2 — With SMSC + signal check
# Sets SMSC and verifies signal before send
# ─────────────────────────────────────────
def with_smsc(message="Hello from A7670E! (v2)"):
    print(f"\n{ts()} ========== VERSION 2: With SMSC + Signal Check ==========")
    try:
        with serial.Serial(PORT, BAUD, timeout=5) as ser:
            time.sleep(2)
            send_at(ser, "AT")
            send_at(ser, "AT+CMGF=1")
            send_at(ser, f'AT+CSCA="{SMSC}"')

            # Check signal before sending
            csq = send_at(ser, "AT+CSQ")
            try:
                value = int(csq.split("+CSQ:")[1].split(",")[0].strip())
                if value == 99 or value < 10:
                    print(f"{ts()} ⚠️  Signal too weak ({value}) — SMS may fail")
                else:
                    print(f"{ts()} ✅ Signal ok ({value}) — proceeding")
            except:
                print(f"{ts()} ⚠️  Could not read signal")

            send_at(ser, f'AT+CMGS="{RECIPIENT}"', wait=2)
            print(f"{ts()} Sending message...")
            ser.write((message + chr(26)).encode())
            time.sleep(15)
            response = ser.read(ser.inWaiting()).decode(errors="ignore")
            print(f"{ts()} Response: {response.strip()}")
            print(f"{ts()} " + ("✅ SUCCESS" if "+CMGS:" in response else "❌ FAILED"))
    except serial.SerialException as e:
        print(f"{ts()} ❌ Port error: {e}")


# ─────────────────────────────────────────
# VERSION 3 — With retry logic
# Retries up to 3 times if send fails
# ─────────────────────────────────────────
def with_retry(message="Hello from A7670E! (v3)", retries=3):
    print(f"\n{ts()} ========== VERSION 3: With Retry ==========")
    try:
        with serial.Serial(PORT, BAUD, timeout=5) as ser:
            time.sleep(2)
            send_at(ser, "AT")
            send_at(ser, "AT+CMGF=1")
            send_at(ser, f'AT+CSCA="{SMSC}"')

            for attempt in range(1, retries + 1):
                print(f"{ts()} --- Attempt {attempt} of {retries} ---")
                send_at(ser, f'AT+CMGS="{RECIPIENT}"', wait=2)
                print(f"{ts()} Sending message...")
                ser.write((message + chr(26)).encode())
                time.sleep(15)
                response = ser.read(ser.inWaiting()).decode(errors="ignore")
                print(f"{ts()} Response: {response.strip()}")
                if "+CMGS:" in response:
                    print(f"{ts()} ✅ SUCCESS on attempt {attempt}")
                    return
                print(f"{ts()} ❌ Attempt {attempt} failed — retrying in 5s...")
                time.sleep(5)

            print(f"{ts()} ❌ FAILED after all retries")
    except serial.SerialException as e:
        print(f"{ts()} ❌ Port error: {e}")


# ─────────────────────────────────────────
# VERSION 4 — Full diagnostic + send
# Runs full checks then sends SMS
# ─────────────────────────────────────────
def full(message="helloooooo"):
    print(f"\n{ts()} ========== VERSION 4: Full Diagnostic + Send ==========")
    try:
        with serial.Serial(PORT, BAUD, timeout=5) as ser:
            time.sleep(2)

            # Diagnostics
            send_at(ser, "AT")
            send_at(ser, "AT+CPIN?")     # SIM status
            send_at(ser, "AT+CSQ")       # Signal
            send_at(ser, "AT+CREG?")     # Registration
            send_at(ser, "AT+COPS?")     # Operator
            send_at(ser, "AT+CSCA?")     # SMSC

            # Send
            send_at(ser, "AT+CMGF=1")
            send_at(ser, f'AT+CSCA="{SMSC}"')
            send_at(ser, f'AT+CMGS="{RECIPIENT}"', wait=2)
            print(f"{ts()} Sending message...")
            ser.write((message + chr(26)).encode())
            time.sleep(20)
            response = ser.read(ser.inWaiting()).decode(errors="ignore")
            print(f"{ts()} Response: {response.strip()}")
            print(f"{ts()} " + ("✅ SUCCESS" if "+CMGS:" in response else "❌ FAILED"))
    except serial.SerialException as e:
        print(f"{ts()} ❌ Port error: {e}")


# ─────────────────────────────────────────
# VERSION 5 — Send to multiple numbers
# Sends same message to all in RECIPIENTS
# ─────────────────────────────────────────
def send_multiple(message="Test message sent from 4602 Kiosk System."):
    print(f"\n{ts()} ========== VERSION 5: Multiple Recipients ==========")
    print(f"{ts()} 📋 Sending to {len(RECIPIENTS)} number(s)...\n")

    results = []

    try:
        with serial.Serial(PORT, BAUD, timeout=5) as ser:
            time.sleep(2)
            send_at(ser, "AT")
            send_at(ser, "AT+CMGF=1")
            send_at(ser, f'AT+CSCA="{SMSC}"')

            for i, number in enumerate(RECIPIENTS, 1):
                print(f"{ts()} --- Sending to {number} ({i} of {len(RECIPIENTS)}) ---")
                send_at(ser, f'AT+CMGS="{number}"', wait=2)
                print(f"{ts()} Sending message...")
                ser.write((message + chr(26)).encode())
                time.sleep(15)
                response = ser.read(ser.inWaiting()).decode(errors="ignore")
                print(f"{ts()} Response: {response.strip()}")

                if "+CMGS:" in response:
                    print(f"{ts()} ✅ Sent to {number}")
                    results.append((number, "✅ SUCCESS"))
                else:
                    print(f"{ts()} ❌ Failed to send to {number}")
                    results.append((number, "❌ FAILED"))

                # Small delay between messages
                if i < len(RECIPIENTS):
                    print(f"{ts()} ⏳ Waiting 5s before next recipient...\n")
                    time.sleep(5)

    except serial.SerialException as e:
        print(f"{ts()} ❌ Port error: {e}")
        return

    # Summary
    print(f"\n{ts()} ========== SUMMARY ==========")
    for number, status in results:
        print(f"{ts()} {status} — {number}")
    print(f"{ts()} Done. {sum(1 for _, s in results if '✅' in s)}/{len(results)} sent successfully.")


# ─────────────────────────────────────────
# RUN — comment/uncomment version to test
# ─────────────────────────────────────────
if __name__ == "__main__":
    basic()
    # with_smsc()
    # with_retry()
    # full()
    # send_multiple()