import serial
import time

# Configure serial connection
port = "COM5"
baud_rate = 9600

# Open serial connection
ser = serial.Serial(port, baud_rate, timeout=2)
time.sleep(0.5)  # Wait for connection to stabilize

print("Reading temperature from Cryocon 22C - Channel A")
print("-" * 40)

# Read temperature
for i in range(5):
    # Send command to read Channel A temperature
    ser.reset_input_buffer()
    ser.write(b'INPUT? A\r\n')
    time.sleep(0.05)  # Wait for response
    
    # Read response
    response = ser.readline().decode('utf-8', errors='ignore').strip()
    
    # Print with timestamp
    print(f"Reading {i+1}: Temperature = {response}")
    
    # Wait 1 second before next reading
    if i < 2:  # Don't wait after the last reading
        time.sleep(0.2)  # Already waited 0.3s above

# Close connection
ser.close()
print("-" * 40)
print("Done!")
