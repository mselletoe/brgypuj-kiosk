import serial
import time

# ─────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────
PORT = "COM12"    # Change if different
BAUD = 115200


# ─────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────
def send_at(ser, command, wait=1):
    """Send an AT command and return the response."""
    ser.write((command + "\r\n").encode())
    time.sleep(wait)
    response = ser.read(ser.inWaiting()).decode(errors="ignore")
    print(f">> {command}")
    print(f"<< {response.strip()}")
    print()
    return response


# ─────────────────────────────────────────
# TEST 1 — Basic connection only
# Check if Python can talk to the module
# ─────────────────────────────────────────
def basic_connection():
    print("========== TEST 1: Basic Connection ==========")
    try:
        with serial.Serial(PORT, BAUD, timeout=5) as ser:
            time.sleep(2)
            response = send_at(ser, "AT")
            if "OK" in response:
                print("✅ Module is responding!")
            else:
                print("❌ No response — check COM port or cable")
    except serial.SerialException as e:
        print(f"❌ Could not open port {PORT}: {e}")


# ─────────────────────────────────────────
# TEST 2 — SIM and signal check
# Check if SIM is detected and has signal
# ─────────────────────────────────────────
def sim_and_signal():
    print("========== TEST 2: SIM + Signal Check ==========")
    try:
        with serial.Serial(PORT, BAUD, timeout=5) as ser:
            time.sleep(2)

            # SIM status
            cpin = send_at(ser, "AT+CPIN?")
            if "READY" in cpin:
                print("✅ SIM detected and ready")
            else:
                print("❌ SIM not ready — check SIM card")

            # Signal strength
            csq = send_at(ser, "AT+CSQ")
            try:
                value = int(csq.split("+CSQ:")[1].split(",")[0].strip())
                if value == 99:
                    print("❌ Signal unknown — check antenna")
                elif value < 10:
                    print(f"⚠️  Signal very weak ({value}) — move antenna near window")
                elif value < 15:
                    print(f"⚠️  Signal weak ({value}) — SMS may be unreliable")
                else:
                    print(f"✅ Signal good ({value})")
            except:
                print("⚠️  Could not parse signal value")

    except serial.SerialException as e:
        print(f"❌ Could not open port {PORT}: {e}")


# ─────────────────────────────────────────
# TEST 3 — Full diagnostic
# Complete status of module, SIM, network
# ─────────────────────────────────────────
def full_diagnostic():
    print("========== TEST 3: Full Diagnostic ==========")
    try:
        with serial.Serial(PORT, BAUD, timeout=5) as ser:
            time.sleep(2)

            send_at(ser, "AT")               # Basic check
            send_at(ser, "AT+CGMR")          # Firmware version
            send_at(ser, "AT+CGSN")          # IMEI
            send_at(ser, "AT+CPIN?")         # SIM status
            send_at(ser, "AT+CSQ")           # Signal strength
            send_at(ser, "AT+CREG?")         # Network registration
            send_at(ser, "AT+COPS?")         # Operator info
            send_at(ser, "AT+CSCA?")         # SMSC number
            send_at(ser, "AT+CNMP?")         # Network mode

            print("✅ Full diagnostic complete — check results above")

    except serial.SerialException as e:
        print(f"❌ Could not open port {PORT}: {e}")


# ─────────────────────────────────────────
# TEST 4 — Reset module
# Sends AT+CRESET and waits for PB DONE
# ─────────────────────────────────────────
def reset_module():
    print("========== TEST 4: Reset Module ==========")
    try:
        with serial.Serial(PORT, BAUD, timeout=30) as ser:
            time.sleep(2)
            print(">> AT+CRESET")
            ser.write(("AT+CRESET\r\n").encode())

            print("⏳ Waiting for module to restart...")
            start = time.time()
            buffer = ""

            # Wait up to 30 seconds for PB DONE
            while time.time() - start < 30:
                if ser.inWaiting():
                    chunk = ser.read(ser.inWaiting()).decode(errors="ignore")
                    buffer += chunk
                    print(chunk, end="", flush=True)
                    if "PB DONE" in buffer:
                        print("\n✅ Module restarted successfully!")
                        return
                time.sleep(0.5)

            print("\n⚠️  Timeout — PB DONE not received. Module may still be booting.")

    except serial.SerialException as e:
        print(f"❌ Could not open port {PORT}: {e}")


# ─────────────────────────────────────────
# RUN TESTS — comment/uncomment as needed
# ─────────────────────────────────────────
if __name__ == "__main__":
    # basic_connection()
    sim_and_signal()
    # full_diagnostic()
    # reset_module()