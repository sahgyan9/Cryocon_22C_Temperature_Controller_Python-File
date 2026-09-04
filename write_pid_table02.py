import serial, time, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

PORT = "COM5"
BAUD = 9600

def q_multiline(ser, cmd, wait=2.0):
    ser.reset_input_buffer()
    ser.write((cmd + "\r\n").encode())
    time.sleep(wait)
    chunks = []
    deadline = time.time() + 4.0
    while time.time() < deadline:
        n = ser.in_waiting
        if n > 0:
            chunks.append(ser.read(n).decode("utf-8", errors="ignore"))
            time.sleep(0.15)
        elif chunks:
            break
        else:
            time.sleep(0.1)
    return "".join(chunks).strip()

def q(ser, cmd, wait=0.25):
    ser.reset_input_buffer()
    ser.write((cmd + "\r\n").encode())
    time.sleep(wait)
    return ser.readline().decode("utf-8", errors="ignore").strip()

# ─── Revised PID Table 02 ─────────────────────────────────────────
#
# Covers 77 K – 475 K in exactly 16 entries (Cryocon 22C table limit).
#
# TWO OPERATING ZONES:
# ┌─────────────────────────────────────────────────────────────────┐
# │ ZONE 1 : 300 K – 475 K  (NO active cooling)                    │
# │   • I = 30–45  →  ~5× lower than original (165–250)            │
# │     Prevents integrator windup during 2 K/min ramps            │
# │   • D = 55–70  →  increased for damping without cooling         │
# │   • P = 2.0–3.0 → slightly higher for faster high-T response   │
# ├─────────────────────────────────────────────────────────────────┤
# │ ZONE 2 : 77 K – 300 K   (LN₂ active cooling present)          │
# │   • I = 50–65  →  moderate; needed to overcome LN₂ load        │
# │     Safe because ramp range is small and LN₂ limits overshoot  │
# │   • D = 20–52  →  keeps oscillation damped against active cool  │
# │   • P = 1.0–2.0 → conservative; LN₂ provides natural stability │
# │   • Range = HI throughout (fights strong LN₂ cooling load)      │
# │   • Range = MID at 77 K (at LN₂ temp, almost no heat needed)   │
# └─────────────────────────────────────────────────────────────────┘
#
# Why both zones use the SAME table:
#   Without cooling at 77–300 K → low error, low windup risk; I=50–65 is fine
#   With LN₂ at 300–475 K       → not applicable (LN₂ evaporates <350 K)
#
# Row   Setpt(K)    P      I      D     Range
entries = [
    # ── ZONE 1: No active cooling (300 K → 475 K) ─────────────────
    (475,  3.0,   45,   70,  "HI"),   # High T: max radiation loss, needs responsive P+D
    (450,  2.9,   43,   68,  "HI"),
    (425,  2.7,   40,   65,  "HI"),
    (400,  2.6,   38,   63,  "HI"),
    (375,  2.4,   36,   60,  "HI"),
    (350,  2.3,   34,   58,  "HI"),
    (325,  2.1,   32,   55,  "HI"),
    (300,  2.0,   30,   52,  "HI"),   # ← crossover row (both zones meet here)
    # ── ZONE 2: LN₂ active cooling (77 K → 300 K) ─────────────────
    (275,  2.0,   55,   50,  "HI"),   # Higher I to hold against LN₂ cooling load
    (250,  1.9,   58,   47,  "HI"),
    (225,  1.8,   60,   44,  "HI"),
    (200,  1.7,   62,   41,  "HI"),
    (175,  1.6,   62,   38,  "HI"),
    (150,  1.5,   60,   33,  "HI"),
    (120,  1.3,   56,   27,  "HI"),
    ( 77,  1.0,   50,   20,  "MID"),  # At LN₂ boiling point: minimal heat needed
]


ser = serial.Serial(PORT, BAUD, timeout=3)
time.sleep(0.5)

print("=" * 68)
print("  CRYOCON 22C - WRITING PID TABLE 02")
print("=" * 68)
print("  Device : " + q(ser, "*IDN?"))
print("  Temp A : " + q(ser, "INPUT? A") + " K")
print("  Table 2 before write - entries: " + q(ser, "PIDTABLE 2:NENTRY?"))
print()
print(f"  Writing {len(entries)} entries to PID Table 2...")
print()

# Build the multi-line table command
# Format per manual:
#   PIDTABLE <index>:TABLE\r\n
#   <name>\r\n
#   <setpt> <P> <I> <D> <Range>\r\n  (one per line)
#   ;\r\n

cmd_lines = ["PIDTABLE 2:TABLE"]
cmd_lines.append("PID Table 2")
for (sp, p, i, d, rng) in entries:
    cmd_lines.append(f" {sp:6.2f}  {p:5.2f}  {i:6.2f}  {d:5.2f}  {rng}")
cmd_lines.append(";")

full_cmd = "\r\n".join(cmd_lines) + "\r\n"

print("  Command being sent:")
print("  " + "-" * 60)
for line in cmd_lines:
    print("  " + line)
print("  " + "-" * 60)
print()

# Send the command
ser.reset_input_buffer()
ser.write(full_cmd.encode())
time.sleep(3.0)   # Give controller time to process all lines

# Read any response
resp = ""
if ser.in_waiting:
    resp = ser.read(ser.in_waiting).decode("utf-8", errors="ignore").strip()

print("  Controller response after write: [" + resp + "]")
print()

# ── VERIFY: Read Table 2 back ─────────────────────────────────────
print("=" * 68)
print("  VERIFYING PID TABLE 02 (reading back from controller)")
print("=" * 68)

nentries = q(ser, "PIDTABLE 2:NENTRY?")
print("  Entries stored in Table 2: " + nentries)
print()

raw = q_multiline(ser, "PIDTABLE 2:TABLE?", wait=2.0)

print("  Raw read-back:")
print("  " + "-" * 62)
print(raw)
print("  " + "-" * 62)
print()

# Parse readback
lines = raw.replace("\r", "").split("\n")
readback = []
for line in lines:
    line = line.strip()
    if not line or line == ";" or not line[0].isdigit() and not line[0] == " ":
        continue
    parts = line.split()
    if len(parts) >= 5:
        try:
            readback.append((float(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]), parts[4]))
        except ValueError:
            pass

print(f"  {'Row':^4} {'Setpt (K)':^12} {'P':^8} {'I':^10} {'D':^8} {'Range':^8}  Status")
print("  " + "-" * 65)

ok_count = 0
fail_count = 0
for idx, (exp, got) in enumerate(zip(entries, readback)):
    sp_ok  = abs(exp[0] - got[0]) < 0.1
    p_ok   = abs(exp[1] - got[1]) < 0.01
    i_ok   = abs(exp[2] - got[2]) < 0.1
    d_ok   = abs(exp[3] - got[3]) < 0.1
    rng_ok = exp[4].upper() == got[4].upper()
    all_ok = all([sp_ok, p_ok, i_ok, d_ok, rng_ok])
    status = "[OK]" if all_ok else "[MISMATCH]"
    if all_ok: ok_count += 1
    else: fail_count += 1
    print(f"  {idx+1:^4} {got[0]:^12.2f} {got[1]:^8.4f} {got[2]:^10.2f} {got[3]:^8.2f} {got[4]:^8}  {status}")

if len(readback) < len(entries):
    print(f"\n  [!] Only {len(readback)} of {len(entries)} entries were stored (controller limit may be 16)")
    fail_count += len(entries) - len(readback)

print("  " + "-" * 65)
print(f"  Verified: {ok_count} OK   {fail_count} issues   ({len(readback)} entries stored)")

print()
if ok_count == len(readback) and len(readback) > 0:
    print("  [SUCCESS] PID Table 02 written and verified!")
    if len(readback) < len(entries):
        print(f"  [NOTE] Controller accepted {len(readback)}/{len(entries)} entries (16-entry max per table)")
else:
    print("  [WARNING] Some entries may not have written correctly.")

ser.close()
print()
print("[OK] Disconnected.")
