import serial
import time

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
PORT = "COM12"
BAUD = 115200


# ─────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────
def send_at(ser, command, wait=1):
    ser.write((command + "\r\n").encode())
    time.sleep(wait)
    response = ser.read(ser.inWaiting()).decode(errors="ignore")
    print(f">> {command}")
    print(f"<< {response.strip()}\n")
    return response


def wait_network(ser, timeout=30):
    print("⏳ Waiting for network registration...")
    start = time.time()

    while time.time() - start < timeout:
        resp = send_at(ser, "AT+CREG?", wait=1)

        if ",1" in resp or ",5" in resp:
            print("✅ Network registered")
            return True

        time.sleep(2)

    print("❌ Network NOT registered")
    return False


# ─────────────────────────────────────────
# TEST 1
# ─────────────────────────────────────────
def basic_connection():
    print("========== TEST 1 ==========")
    with serial.Serial(PORT, BAUD, timeout=5) as ser:
        time.sleep(2)
        send_at(ser, "AT")


# ─────────────────────────────────────────
# TEST 2
# ─────────────────────────────────────────
def sim_and_signal():
    print("========== TEST 2 ==========")

    with serial.Serial(PORT, BAUD, timeout=5) as ser:
        time.sleep(2)

        send_at(ser, "AT+CPIN?")
        send_at(ser, "AT+CSQ")
        send_at(ser, "AT+CREG?")
        wait_network(ser)


# ─────────────────────────────────────────
# TEST 3
# ─────────────────────────────────────────
def full_diagnostic():
    print("========== TEST 3 ==========")

    with serial.Serial(PORT, BAUD, timeout=5) as ser:
        time.sleep(2)

        cmds = [
            "AT",
            "AT+CGMR",
            "AT+CGSN",
            "AT+CPIN?",
            "AT+CSQ",
            "AT+CREG?",
            "AT+COPS?",
            "AT+CSCA?",
            "AT+CNMP?"
        ]

        for c in cmds:
            send_at(ser, c)


# ─────────────────────────────────────────
# TEST 4
# ─────────────────────────────────────────
def reset_module():
    print("========== TEST 4 ==========")

    with serial.Serial(PORT, BAUD, timeout=30) as ser:
        time.sleep(2)

        ser.write(b"AT+CRESET\r\n")

        buffer = ""
        start = time.time()

        while time.time() - start < 30:
            if ser.inWaiting():
                buffer += ser.read(ser.inWaiting()).decode(errors="ignore")
                print(buffer, end="")

                if "PB DONE" in buffer:
                    print("\n✅ Reset complete")
                    return

            time.sleep(0.5)


# ─────────────────────────────────────────
# RUN
# ─────────────────────────────────────────
if __name__ == "__main__":
    sim_and_signal()