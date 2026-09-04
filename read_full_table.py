import serial, time, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

PORT = "COM5"
BAUD = 9600

def q_multiline(ser, cmd, wait=1.5):
    ser.reset_input_buffer()
    ser.write((cmd + "\r\n").encode())
    time.sleep(wait)
    # Read everything available
    chunks = []
    deadline = time.time() + 3.0
    while time.time() < deadline:
        n = ser.in_waiting
        if n > 0:
            chunks.append(ser.read(n).decode("utf-8", errors="ignore"))
            time.sleep(0.1)
        elif chunks:
            break
        else:
            time.sleep(0.1)
    return "".join(chunks).strip()

def q(ser, cmd, wait=0.2):
    ser.reset_input_buffer()
    ser.write((cmd + "\r\n").encode())
    time.sleep(wait)
    return ser.readline().decode("utf-8", errors="ignore").strip()

ser = serial.Serial(PORT, BAUD, timeout=3)
time.sleep(0.5)

print("=" * 70)
print("  CRYOCON 22C - FULL PID TABLE 01 READ")
print("=" * 70)
print("  Device : " + q(ser, "*IDN?"))
print("  Temp A : " + q(ser, "INPUT? A") + " K")
print("  LOOP 1 TABLE assigned (TABLEIX): " + q(ser, "LOOP 1:TABLEIX?"))
print()

# Read the full table 1 content
raw = q_multiline(ser, "PIDTABLE 1:TABLE?", wait=2.0)

print("  Raw response from PIDTABLE 1:TABLE?:")
print("  " + "-" * 60)
print(raw)
print("  " + "-" * 60)

# Parse the response
lines = raw.replace("\r", "").split("\n")
entries = []
for line in lines:
    line = line.strip()
    parts = line.split()
    # Valid entry has at least 5 fields: setpoint P I D Range
    if len(parts) >= 5:
        try:
            setpt = float(parts[0])
            p = float(parts[1])
            i = float(parts[2])
            d = float(parts[3])
            rng = parts[4]
            entries.append((setpt, p, i, d, rng))
        except ValueError:
            pass  # skip non-numeric lines (like table name)

print()
print("  PARSED PID TABLE 01 ENTRIES:")
print(f"  {'#':^4} {'Setpt (K)':^12} {'P':^10} {'I':^10} {'D':^10} {'Range':^8}")
print("  " + "-" * 58)
for idx, (sp, p, i, d, rng) in enumerate(entries):
    print(f"  {idx:^4} {sp:^12.2f} {p:^10.4f} {i:^10.4f} {d:^10.4f} {rng:^8}")
print("  " + "-" * 58)
print(f"  Total entries: {len(entries)}")

# Also check table 2
print()
print("  PIDTABLE 2 - current entries: " + q(ser, "PIDTABLE 2:NENTRY?"))
print("  PIDTABLE 2 NAME: " + q(ser, "PIDTABLE 2:NAME?"))

ser.close()
print()
print("[OK] Done.")
