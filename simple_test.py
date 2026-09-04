"""Simple test to verify Cryocon 22C communication"""
import serial
import time

port = "COM5"
baud_rate = 9600

print("Connecting to Cryocon 22C...")
ser = serial.Serial(port, baud_rate, timeout=2)
time.sleep(0.5)

def query(cmd):
    ser.reset_input_buffer()
    ser.write(f'{cmd}\r\n'.encode())
    time.sleep(0.05)
    return ser.readline().decode('utf-8', errors='ignore').strip()

print("\n=== DEVICE INFO ===")
print(f"Identity: {query('*IDN?')}")

print("\n=== TEMPERATURES ===")
print(f"Channel A: {query('INPUT? A')} K")
print(f"Channel B: {query('INPUT? B')} K")

print("\n=== LOOP 1 SETTINGS ===")
print(f"Setpoint: {query('LOOP 1:SETPT?')}")
print(f"Source: {query('LOOP 1:SOURCE?')}")
print(f"Type: {query('LOOP 1:TYPE?')}")
print(f"P Gain: {query('LOOP 1:PGAIN?')}")
print(f"I Gain: {query('LOOP 1:IGAIN?')}")
print(f"D Gain: {query('LOOP 1:DGAIN?')}")
print(f"Heater Output: {query('LOOP 1:OUTP?')}%")

print("\n=== CONTROL STATUS ===")
print(f"Control: {query('CONTROL?')}")

ser.close()
print("\nDone!")
