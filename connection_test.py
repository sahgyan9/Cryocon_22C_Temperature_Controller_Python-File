import serial
import time

PORT = "COM5"
BAUD = 9600

def q(ser, cmd):
    ser.reset_input_buffer()
    ser.write((cmd + "\r\n").encode())
    time.sleep(0.15)
    return ser.readline().decode("utf-8", errors="ignore").strip()

print("=" * 55)
print("  CRYOCON 22C - CONNECTION TEST")
print("=" * 55)

try:
    ser = serial.Serial(PORT, BAUD, timeout=3)
    time.sleep(0.5)
    print("Port       : " + PORT + "  [OPEN]")
    print("Device IDN : " + q(ser, "*IDN?"))
    print("Firmware   : " + q(ser, "SYSTEM:FWREV?"))
    print("Temp A     : " + q(ser, "INPUT? A") + " K")
    print("Temp B     : " + q(ser, "INPUT? B") + " K")
    print("Loop1 Type : " + q(ser, "LOOP 1:TYPE?"))
    print("Loop1 Setpt: " + q(ser, "LOOP 1:SETPT?"))
    print("Control?   : " + q(ser, "CONTROL?"))
    print("=" * 55)
    print("[OK] Connection successful!")
    ser.close()
except serial.SerialException as e:
    print("[ERROR] " + str(e))
