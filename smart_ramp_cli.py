"""
Cryocon 22C - Automated Two-Speed Smart Ramping CLI Tool
========================================================
Runs an automated temperature ramp to any target setpoint
with adaptive two-speed ramping to eliminate overshoot:
  - Fast Stage: Ramps at fast rate (e.g. 5.0 K/min) while delta > 15K
  - Gentle Stage: Automatically slows down to 0.5 K/min within 15K of target
  - Holding Stage: Maintains target temperature once settled
  - Continuous CSV Data Logging

Usage:
  python smart_ramp_cli.py --target 350 --fast 5.0 --slow 0.5 --table 2
"""

import serial
import time
import datetime
import os
import csv
import argparse
import sys

PORT = "COM5"
BAUD = 9600

def query(ser, cmd, wait=0.1):
    ser.reset_input_buffer()
    ser.write((cmd + "\r\n").encode())
    time.sleep(wait)
    return ser.readline().decode("utf-8", errors="ignore").strip()

def send(ser, cmd, wait=0.15):
    ser.write((cmd + "\r\n").encode())
    time.sleep(wait)

def run_smart_ramp(target_k, fast_rate=5.0, slow_rate=0.5, switch_delta=15.0, table_num=2, hold_minutes=10):
    print("=" * 70)
    print("  CRYOCON 22C - AUTOMATED SMART TWO-SPEED RAMP ENGINE")
    print("=" * 70)
    print(f"  Target Setpoint : {target_k:.2f} K")
    print(f"  Fast Ramp Rate  : {fast_rate:.2f} K/min (when ΔT > {switch_delta:.1f} K)")
    print(f"  Slow Final Rate : {slow_rate:.2f} K/min (when ΔT ≤ {switch_delta:.1f} K)")
    print(f"  Active PID Table: Table {table_num:02d}")
    print(f"  Hold Duration   : {hold_minutes} minutes after reaching target")
    print("=" * 70)

    try:
        ser = serial.Serial(PORT, BAUD, timeout=2)
        time.sleep(0.5)
    except Exception as e:
        print(f"[ERROR] Could not open {PORT}: {e}")
        return

    idn = query(ser, "*IDN?")
    print(f"[OK] Connected: {idn}")

    # Set PID Table and Enable Control
    send(ser, f"LOOP 1:TABLEIX {table_num}")
    send(ser, f"LOOP 1:SETPT {target_k}")
    send(ser, "CONTROL")

    start_temp = float(query(ser, "INPUT? A"))
    delta = abs(start_temp - target_k)
    print(f"[INFO] Initial Temp A: {start_temp:.3f} K (ΔT = {delta:.2f} K)")

    # Prepare CSV Log
    now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"smart_ramp_log_{now_str}.csv"
    f_log = open(csv_file, "w", newline="", encoding="utf-8")
    writer = csv.writer(f_log)
    writer.writerow([
        "Timestamp", "Elapsed_Sec", "Temp_A_K", "Temp_B_K",
        "Setpoint_K", "Error_K", "Heater_Pct", "Ramp_Rate",
        "PID_Table", "Stage"
    ])
    f_log.flush()
    print(f"[OK] Data logging active: {csv_file}\n")

    # Initial rate selection
    if delta > switch_delta:
        stage = "FAST_RAMP"
        send(ser, f"LOOP 1:RATE {fast_rate}")
        print(f"[*] Stage 1: Fast Ramping @ {fast_rate} K/min...")
    else:
        stage = "GENTLE_APPROACH"
        send(ser, f"LOOP 1:RATE {slow_rate}")
        print(f"[*] Stage 2: Gentle Approach @ {slow_rate} K/min...")

    print(f"\n{'Time':^10} {'Elapsed':^8} {'Temp A (K)':^14} {'Setpoint':^10} {'Error':^10} {'Heater%':^9} {'Stage':^16}")
    print("-" * 82)

    start_time = time.time()
    reach_target_time = None

    try:
        while True:
            t_now = time.time()
            elapsed = t_now - start_time
            ts = datetime.datetime.now().strftime("%H:%M:%S")

            ta_str = query(ser, "INPUT? A")
            tb_str = query(ser, "INPUT? B")
            ht_str = query(ser, "LOOP 1:OUTP?").replace("%", "").strip()

            try: ta = float(ta_str)
            except ValueError: ta = 0.0
            try: tb = float(tb_str)
            except ValueError: tb = 0.0
            try: ht = float(ht_str)
            except ValueError: ht = 0.0

            err = ta - target_k
            cur_delta = abs(err)

            # State Transitions
            if stage == "FAST_RAMP" and cur_delta <= switch_delta:
                stage = "GENTLE_APPROACH"
                send(ser, f"LOOP 1:RATE {slow_rate}")
                print(f"\n>>> [SWITCH] Within {switch_delta}K of target! Switching to GENTLE rate @ {slow_rate} K/min <<<\n")

            elif stage == "GENTLE_APPROACH" and cur_delta < 0.2:
                stage = "HOLDING"
                reach_target_time = time.time()
                print(f"\n>>> [TARGET REACHED] Stabilized at {target_k}K (Error < 0.2K). Holding for {hold_minutes} min <<<\n")

            # Check hold completion
            if stage == "HOLDING" and reach_target_time:
                held_sec = time.time() - reach_target_time
                if held_sec >= (hold_minutes * 60):
                    print(f"\n[SUCCESS] Hold duration of {hold_minutes} minutes complete!")
                    break

            print(f"{ts:^10} {elapsed:^8.1f} {ta:^14.3f} {target_k:^10.2f} {err:^+10.3f} {ht:^9.1f} {stage:^16}")

            # CSV Log
            rate_now = fast_rate if stage == "FAST_RAMP" else slow_rate
            writer.writerow([
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                f"{elapsed:.1f}", f"{ta:.4f}", f"{tb:.4f}",
                f"{target_k:.2f}", f"{err:+.4f}", f"{ht:.2f}",
                f"{rate_now:.2f}", table_num, stage
            ])
            f_log.flush()

            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\n\n[ABORT] Ramping stopped by user (Ctrl+C).")
    finally:
        f_log.close()
        ser.close()
        print(f"\n[OK] Data saved to {csv_file}")
        print("[OK] Disconnected.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cryocon 22C Smart Two-Speed Ramping Automation")
    parser.add_argument("--target", type=float, default=320.0, help="Target Temperature in Kelvin")
    parser.add_argument("--fast", type=float, default=5.0, help="Fast Ramp Rate (K/min)")
    parser.add_argument("--slow", type=float, default=0.5, help="Slow Final Approach Rate (K/min)")
    parser.add_argument("--delta", type=float, default=15.0, help="Switch Delta (K) to switch to slow rate")
    parser.add_argument("--table", type=int, default=2, help="PID Table number (1 or 2)")
    parser.add_argument("--hold", type=int, default=10, help="Hold duration in minutes")

    args = parser.parse_args()
    run_smart_ramp(target_k=args.target, fast_rate=args.fast, slow_rate=args.slow,
                   switch_delta=args.delta, table_num=args.table, hold_minutes=args.hold)
