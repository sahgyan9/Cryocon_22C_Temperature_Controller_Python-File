"""Quick 10-second temperature monitoring test"""
import serial
import time
from datetime import datetime

port = "COM5"
ser = serial.Serial(port, 9600, timeout=2)
time.sleep(0.5)

def query(cmd):
    ser.reset_input_buffer()
    ser.write(f'{cmd}\r\n'.encode())
    time.sleep(0.05)
    return ser.readline().decode('utf-8', errors='ignore').strip()

print("=" * 60)
print("     10-SECOND TEMPERATURE MONITORING TEST")
print("=" * 60)
print(f"\nDevice: {query('*IDN?')}")
print(f"\n{'Time':^12} {'Elapsed':^10} {'Temp A (K)':^15} {'Heater %':^10}")
print("-" * 50)

start = time.time()
readings = []

for i in range(10):
    elapsed = time.time() - start
    temp = query("INPUT? A")
    heater = query("LOOP 1:OUTP?")
    
    try:
        temp_val = float(temp)
        readings.append(temp_val)
    except:
        temp_val = 0
    
    print(f"{datetime.now().strftime('%H:%M:%S'):^12} {elapsed:^10.1f} {temp:^15} {heater:^10}")
    time.sleep(1.0)

ser.close()

print("-" * 50)
if readings:
    print(f"Average: {sum(readings)/len(readings):.3f} K")
    print(f"Min: {min(readings):.3f} K  |  Max: {max(readings):.3f} K")
print("\n[OK] Test complete!")
