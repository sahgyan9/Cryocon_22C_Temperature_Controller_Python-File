"""
Query Cryocon 22C Temperature Controller Information
This script queries various settings to help setup LabVIEW program
"""
import serial
import time

# Configure serial connection
port = "COM5"
baud_rate = 9600

def send_command(ser, cmd, wait_time=0.05):
    """Send command and return response"""
    ser.reset_input_buffer()
    ser.write(f'{cmd}\r\n'.encode())
    if wait_time > 0:
        time.sleep(wait_time)
    response = ser.readline().decode('utf-8', errors='ignore').strip()
    return response

try:
    # Open serial connection
    ser = serial.Serial(port, baud_rate, timeout=2)
    time.sleep(0.5)  # Wait for connection to stabilize
    
    print("=" * 60)
    print("CRYOCON 22C TEMPERATURE CONTROLLER - SYSTEM INFO")
    print("=" * 60)
    
    # Device Identification
    print("\n--- Device Identification ---")
    print(f"*IDN?: {send_command(ser, '*IDN?')}")
    
    # Input Channel A Info
    print("\n--- Input Channel A ---")
    print(f"Temperature (INPUT? A): {send_command(ser, 'INPUT? A')}")
    print(f"Units (INPUT A:UNITS?): {send_command(ser, 'INPUT A:UNITS?')}")
    print(f"Sensor Type (INPUT A:SENTYPE?): {send_command(ser, 'INPUT A:SENTYPE?')}")
    print(f"Sensor Name (INPUT A:NAME?): {send_command(ser, 'INPUT A:NAME?')}")
    
    # Input Channel B Info
    print("\n--- Input Channel B ---")
    print(f"Temperature (INPUT? B): {send_command(ser, 'INPUT? B')}")
    print(f"Units (INPUT B:UNITS?): {send_command(ser, 'INPUT B:UNITS?')}")
    print(f"Sensor Type (INPUT B:SENTYPE?): {send_command(ser, 'INPUT B:SENTYPE?')}")
    print(f"Sensor Name (INPUT B:NAME?): {send_command(ser, 'INPUT B:NAME?')}")
    
    # Control Loop 1 Info
    print("\n--- Control Loop 1 ---")
    print(f"Setpoint (LOOP 1:SETPT?): {send_command(ser, 'LOOP 1:SETPT?')}")
    print(f"Source (LOOP 1:SOURCE?): {send_command(ser, 'LOOP 1:SOURCE?')}")
    print(f"Type (LOOP 1:TYPE?): {send_command(ser, 'LOOP 1:TYPE?')}")
    print(f"Range (LOOP 1:RANGE?): {send_command(ser, 'LOOP 1:RANGE?')}")
    print(f"P Gain (LOOP 1:PGAIN?): {send_command(ser, 'LOOP 1:PGAIN?')}")
    print(f"I Gain (LOOP 1:IGAIN?): {send_command(ser, 'LOOP 1:IGAIN?')}")
    print(f"D Gain (LOOP 1:DGAIN?): {send_command(ser, 'LOOP 1:DGAIN?')}")
    print(f"Output Power (LOOP 1:OUTP?): {send_command(ser, 'LOOP 1:OUTP?')}")
    print(f"Max Power (LOOP 1:PMAX?): {send_command(ser, 'LOOP 1:PMAX?')}")
    
    # Control Loop 2 Info
    print("\n--- Control Loop 2 ---")
    print(f"Setpoint (LOOP 2:SETPT?): {send_command(ser, 'LOOP 2:SETPT?')}")
    print(f"Source (LOOP 2:SOURCE?): {send_command(ser, 'LOOP 2:SOURCE?')}")
    print(f"Type (LOOP 2:TYPE?): {send_command(ser, 'LOOP 2:TYPE?')}")
    print(f"Range (LOOP 2:RANGE?): {send_command(ser, 'LOOP 2:RANGE?')}")
    
    # Control Status
    print("\n--- Control Status ---")
    print(f"Control Enable (CONTROL?): {send_command(ser, 'CONTROL?')}")
    
    # System Info
    print("\n--- System Info ---")
    print(f"Firmware Rev (SYSTEM:FWREV?): {send_command(ser, 'SYSTEM:FWREV?')}")
    print(f"System Name (SYSTEM:NAME?): {send_command(ser, 'SYSTEM:NAME?')}")
    
    print("\n" + "=" * 60)
    print("Query Complete!")
    print("=" * 60)
    
    # Close connection
    ser.close()
    
except serial.SerialException as e:
    print(f"Serial Error: {e}")
except Exception as e:
    print(f"Error: {e}")
