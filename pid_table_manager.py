"""
Cryocon 22C - PID Table Manager
================================
Step 1: Connect & read PID Table 01 (company pre-set, up to 300K)
Step 2: Read & display all entries from Table 01
Step 3: Write same values to Table 02, extended to 450K
Step 4: Confirm Table 02 values by reading them back
"""

import serial
import time
import sys

PORT = "COM5"
BAUD = 9600

def query(ser, cmd, delay=0.1):
    ser.reset_input_buffer()
    ser.write(f'{cmd}\r\n'.encode())
    time.sleep(delay)
    return ser.readline().decode('utf-8', errors='ignore').strip()

def send(ser, cmd, delay=0.15):
    ser.write(f'{cmd}\r\n'.encode())
    time.sleep(delay)

def connect():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=3,
                            bytesize=serial.EIGHTBITS,
                            parity=serial.PARITY_NONE,
                            stopbits=serial.STOPBITS_ONE)
        time.sleep(0.5)
        return ser
    except serial.SerialException as e:
        print(f"[ERROR] Cannot open {PORT}: {e}")
        sys.exit(1)

def read_pid_table(ser, table_num, max_entries=20):
    entries = []
    print(f"\n  Reading PID Table {table_num:02d} ...")
    print(f"  {'Entry':^6} {'Temp (K)':^12} {'P':^10} {'I':^10} {'D':^10}")
    print("  " + "-"*52)
    for idx in range(max_entries):
        t_resp = query(ser, f"PIDITBL {table_num}:{idx}:TEMP?")
        p_resp = query(ser, f"PIDITBL {table_num}:{idx}:PGAIN?")
        i_resp = query(ser, f"PIDITBL {table_num}:{idx}:IGAIN?")
        d_resp = query(ser, f"PIDITBL {table_num}:{idx}:DGAIN?")
        try:
            temp_val = float(t_resp.replace('K','').strip())
        except (ValueError, AttributeError):
            break
        if temp_val <= 0:
            break
        try:
            p_val = float(p_resp)
            i_val = float(i_resp)
            d_val = float(d_resp)
        except ValueError:
            p_val = i_val = d_val = 0.0
        entries.append({'temp': temp_val, 'P': p_val, 'I': i_val, 'D': d_val})
        print(f"  {idx:^6} {temp_val:^12.2f} {p_val:^10.4f} {i_val:^10.4f} {d_val:^10.4f}")
    return entries

def write_pid_table(ser, table_num, entries):
    print(f"\n  Writing {len(entries)} entries to PID Table {table_num:02d} ...")
    for idx, row in enumerate(entries):
        send(ser, f"PIDITBL {table_num}:{idx}:TEMP {row['temp']:.4f}")
        send(ser, f"PIDITBL {table_num}:{idx}:PGAIN {row['P']:.6f}")
        send(ser, f"PIDITBL {table_num}:{idx}:IGAIN {row['I']:.6f}")
        send(ser, f"PIDITBL {table_num}:{idx}:DGAIN {row['D']:.6f}")
        print(f"  [OK] Row {idx}: Temp={row['temp']:.2f}K  P={row['P']}  I={row['I']}  D={row['D']}")
    print(f"  Done writing Table {table_num:02d}.")

def verify_pid_table(ser, table_num, expected_entries):
    print(f"\n  Verifying PID Table {table_num:02d} ...")
    actual = read_pid_table(ser, table_num, max_entries=len(expected_entries)+2)
    mismatches = 0
    for idx, (exp, act) in enumerate(zip(expected_entries, actual)):
        t_ok = abs(exp['temp'] - act['temp']) < 0.1
        p_ok = abs(exp['P']    - act['P'])    < 0.001
        i_ok = abs(exp['I']    - act['I'])    < 0.001
        d_ok = abs(exp['D']    - act['D'])    < 0.001
        if not all([t_ok, p_ok, i_ok, d_ok]):
            print(f"  [MISMATCH] Row {idx}: expected T={exp['temp']} P={exp['P']} I={exp['I']} D={exp['D']}")
            print(f"              got     T={act['temp']} P={act['P']} I={act['I']} D={act['D']}")
            mismatches += 1
    if mismatches == 0:
        print(f"  [PASS] All {len(expected_entries)} rows verified correctly in Table {table_num:02d}.")
    else:
        print(f"  [FAIL] {mismatches} mismatch(es) found.")
    return mismatches == 0

def main():
    print("=" * 62)
    print("   CRYOCON 22C - PID TABLE MANAGER")
    print("=" * 62)
    ser = connect()
    print(f"[OK] Connected on {PORT}")
    idn = query(ser, "*IDN?")
    print(f"[OK] Device ID : {idn}")
    print("\n" + "-"*62)
    print("STEP 1: Reading PID Table 01 (factory values, up to 300K)")
    print("-"*62)
    table01 = read_pid_table(ser, table_num=1)
    if not table01:
        print("\n[WARNING] Table 01 appears empty or unreadable.")
        ser.close()
        return
    print(f"\n[OK] Found {len(table01)} entries in Table 01.")
    print("\n" + "-"*62)
    print("STEP 2: Confirm Table 01 values before copying to Table 02")
    print("-"*62)
    answer = input("\n>>> Do the Table 01 values above look correct? [yes/no]: ").strip().lower()
    if answer not in ('yes', 'y'):
        print("[ABORTED] No changes made to Table 02.")
        ser.close()
        return
    print("\n" + "-"*62)
    print("STEP 3: Writing Table 01 values into PID Table 02")
    print("-"*62)
    write_pid_table(ser, table_num=2, entries=table01)
    print("\n" + "-"*62)
    print("STEP 4: Verifying PID Table 02 (read-back)")
    print("-"*62)
    passed = verify_pid_table(ser, table_num=2, expected_entries=table01)
    if passed:
        print("\n[SUCCESS] Table 02 matches Table 01 values.")
        print("          Next: extend Table 02 with 300K-450K entries.")
    else:
        print("\n[WARNING] Mismatch found. Check controller.")
    ser.close()
    print("\n[OK] Disconnected.")

if __name__ == "__main__":
    main()
