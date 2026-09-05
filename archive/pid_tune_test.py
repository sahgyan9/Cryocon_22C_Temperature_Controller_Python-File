"""
Cryocon 22C - Single-Rate PID Tuning Test
==========================================
Purpose-built for iterating on PID gains directly (P/I/D applied manually,
NOT via PID Table lookup) using ONE flat ramp rate the whole way -- no
two-speed software trick -- so results transfer directly to a LabVIEW-driven
workflow later.

Puts Loop 1 into RampP (ramp using the PID gains you pass in, not Table
lookup), sets rate/range/setpoint, enables control, then logs and prints
temperature/heater/error every second until settled+held or a safety
timeout is hit.

Includes a software over-temperature abort: if the reading ever exceeds
setpoint by more than --maxover (default 15K), control is stopped
immediately (LOOP 1:STOP + CONTROL off is not enough alone -- also cuts to
Range OFF... actually just disables control loop, which drives heater to 0).

Usage:
  python pid_tune_test.py --target 315 --rate 2.0 --p 2.02 --i 30.4 --d 70 --range HI --hold 3 --maxrun 10
"""
import serial
import time
import datetime
import csv
import argparse
import sys

PORT = "COM5"
BAUD = 9600


def query(ser, cmd, wait=0.2, retries=6):
    for attempt in range(retries):
        ser.reset_input_buffer()
        ser.write((cmd + "\r\n").encode())
        time.sleep(wait)
        resp = ser.readline().decode("utf-8", errors="ignore").strip()
        if resp:
            return resp
        time.sleep(0.3)
    return ""


def send(ser, cmd, wait=0.2):
    ser.write((cmd + "\r\n").encode())
    time.sleep(wait)


def run(target_k, rate, p, i, d, range_val, hold_minutes, max_run_minutes, max_over, maxpwr=None):
    print("=" * 72)
    print("  CRYOCON 22C - SINGLE-RATE PID TUNING TEST (RampP, no software ramp trick)")
    print("=" * 72)
    print(f"  Target Setpoint : {target_k:.2f} K")
    print(f"  Flat Ramp Rate  : {rate:.2f} K/min (constant, whole approach)")
    print(f"  PID Gains       : P={p}  I={i}  D={d}")
    print(f"  Heater Range    : {range_val}")
    print(f"  Max Power       : {maxpwr if maxpwr is not None else '(unchanged)'}%")
    print(f"  Hold after settle: {hold_minutes} min | Safety timeout: {max_run_minutes} min")
    print(f"  Software over-temp abort: setpoint + {max_over} K")
    print("=" * 72)

    try:
        ser = serial.Serial(PORT, BAUD, timeout=2)
        time.sleep(0.5)
    except Exception as e:
        print(f"[ERROR] Could not open {PORT}: {e}")
        return

    idn = query(ser, "*IDN?")
    print(f"[OK] Connected: {idn}")

    # Resync: the controller's internal ramp target resumes from wherever the
    # PREVIOUS setpoint left it, not from the live reading. If the last
    # setpoint is stale (e.g. left over from an earlier test), a new target
    # ramps from that stale point instead of "now", silently lengthening the
    # ramp and giving the I term extra time to wind up (see
    # OVERSHOOT_TUNING_LOG.md, attempt 2). Fix: park the setpoint at the
    # current live reading first so the real ramp starts from "now".
    live_temp = float(query(ser, "INPUT? A"))
    print(f"[INFO] Resyncing setpoint to live temp {live_temp:.3f} K before starting ramp...")
    # The resync MUST be done outside ramp mode. Writing SETPT while TYPE is
    # already RAMPP does not jump the working setpoint -- it starts a ramp
    # toward it at --rate, so the loop keeps controlling to the OLD setpoint
    # for minutes (observed 2026-09-04: heater sat at 0% for ~90s because the
    # working setpoint was still down at the previous target, well below the
    # live reading). Dropping to plain PID mode makes the setpoint write
    # instantaneous; per the manual (Temperature Ramping, "the controller may
    # be regulating in any available control mode... changed to a ramping mode
    # without exiting the control loop. This will not result in a 'glitch' in
    # heater output power"), switching modes mid-control is safe.
    send(ser, "LOOP 1:TYPE PID")
    time.sleep(0.5)
    send(ser, f"LOOP 1:SETPT {live_temp}")
    time.sleep(1.5)

    # Configure Loop 1 for direct-PID ramp mode (bypasses Table interpolation)
    send(ser, f"LOOP 1:RANGE {range_val}")
    time.sleep(1.0)  # range changes switch a physical relay; give it extra settle time
    if maxpwr is not None:
        send(ser, f"LOOP 1:MAXPWR {maxpwr}")
    send(ser, f"LOOP 1:PGAIN {p}")
    send(ser, f"LOOP 1:IGAIN {i}")
    send(ser, f"LOOP 1:DGAIN {d}")
    send(ser, f"LOOP 1:RATE {rate}")
    send(ser, "LOOP 1:TYPE RAMPP")
    send(ser, f"LOOP 1:SETPT {target_k}")
    send(ser, "CONTROL")

    start_temp = float(query(ser, "INPUT? A"))
    print(f"[INFO] Starting Temp A: {start_temp:.3f} K -> Target {target_k:.2f} K "
          f"(delta {target_k - start_temp:+.2f} K)")

    now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"cryocon_log_{now_str}_pidtune.csv"
    f_log = open(csv_file, "w", newline="", encoding="utf-8")
    writer = csv.writer(f_log)
    writer.writerow([
        "Timestamp", "Elapsed_Sec", "Temp_A_K", "Setpoint_K", "Error_K",
        "Ramp_SP_K", "Track_Err_K",
        "Heater_Pct", "Ramp_Rate_K_min", "P_Gain", "I_Gain", "D_Gain", "Range", "MaxPwr_Pct", "Stage"
    ])
    f_log.flush()
    print(f"[OK] Data logging active: {csv_file}\n")

    print(f"{'Time':^10} {'Elapsed':^8} {'Temp A (K)':^12} {'Error':^10} {'RampSP':^10} {'TrkErr':^9} {'Heater%':^9} {'Stage':^12}")
    print("-" * 86)

    start_time = time.time()
    stage = "RAMPING"
    reach_time = None
    peak_error = 0.0
    aborted = False

    try:
        while True:
            elapsed = time.time() - start_time
            ts = datetime.datetime.now().strftime("%H:%M:%S")

            ta_str = query(ser, "INPUT? A")
            ht_str = query(ser, "LOOP 1:OUTP?").replace("%", "").strip()
            try:
                ta = float(ta_str)
            except ValueError:
                ta = float("nan")
            try:
                ht = float(ht_str)
            except ValueError:
                ht = 0.0

            if target_k >= start_temp:
                ramp_sp = min(start_temp + rate * elapsed / 60.0, target_k)
            else:
                ramp_sp = max(start_temp - rate * elapsed / 60.0, target_k)
            track_err = ramp_sp - ta   # what the PID is actually reacting to

            err = ta - target_k
            if abs(err) > abs(peak_error):
                peak_error = err

            # Safety: abort if wildly over target
            if err > max_over:
                print(f"\n[SAFETY ABORT] Temp {ta:.2f}K exceeds setpoint+{max_over}K! Stopping control.")
                send(ser, "STOP")
                aborted = True
                stage = "ABORTED"

            if stage in ("RAMPING", "SETTLED") and abs(err) < 0.2:
                if stage == "RAMPING":
                    print(f"\n>>> [SETTLED] |Error| < 0.2K reached at {ta:.3f}K (peak error during approach: {peak_error:+.3f}K) <<<\n")
                stage = "SETTLED"
                if reach_time is None:
                    reach_time = time.time()
            elif stage == "SETTLED" and abs(err) >= 0.2:
                # Left the band again -- this is NOT a real settle, reset the hold clock
                print(f"\n>>> [REBOUND] Left 0.2K band again at {ta:.3f}K (err {err:+.3f}K) -- resetting hold timer <<<\n")
                stage = "RAMPING"
                reach_time = None

            if stage == "SETTLED" and reach_time:
                held = time.time() - reach_time
                if held >= hold_minutes * 60:
                    print(f"\n[SUCCESS] Held within 0.2K continuously for {hold_minutes} minutes.")
                    break

            if elapsed >= max_run_minutes * 60:
                print(f"\n[TIMEOUT] Safety max runtime ({max_run_minutes} min) reached, stopping test.")
                break

            if aborted:
                break

            print(f"{ts:^10} {elapsed:^8.1f} {ta:^12.3f} {err:^+10.3f} {ramp_sp:^10.3f} {track_err:^+9.3f} {ht:^9.1f} {stage:^12}")

            writer.writerow([
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                f"{elapsed:.1f}", f"{ta:.4f}", f"{target_k:.2f}", f"{err:+.4f}",
                f"{ramp_sp:.4f}", f"{track_err:+.4f}",
                f"{ht:.2f}", f"{rate:.2f}", p, i, d, range_val, maxpwr, stage
            ])
            f_log.flush()

            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\n\n[ABORT] Stopped by user (Ctrl+C).")
    finally:
        f_log.close()
        final_temp = query(ser, "INPUT? A")
        final_heater = query(ser, "LOOP 1:OUTP?")
        ser.close()
        print(f"\n[SUMMARY] Peak error during test: {peak_error:+.3f} K")
        print(f"[SUMMARY] Final temp: {final_temp} K | Final heater: {final_heater}%")
        print(f"[OK] Data saved to {csv_file}")
        print("[OK] Disconnected.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cryocon 22C single-rate PID tuning test (RampP mode)")
    parser.add_argument("--target", type=float, required=True, help="Target setpoint (K)")
    parser.add_argument("--rate", type=float, default=2.0, help="Flat ramp rate (K/min), constant whole approach")
    parser.add_argument("--p", type=float, required=True, help="P gain")
    parser.add_argument("--i", type=float, required=True, help="I gain")
    parser.add_argument("--d", type=float, required=True, help="D gain")
    parser.add_argument("--range", type=str, default="HI", help="Heater range: HI, MID, LOW")
    parser.add_argument("--hold", type=float, default=3.0, help="Minutes to hold within 0.2K before declaring success")
    parser.add_argument("--maxrun", type=float, default=10.0, help="Safety timeout in minutes")
    parser.add_argument("--maxover", type=float, default=15.0, help="Software abort if temp exceeds setpoint by this many K")
    parser.add_argument("--maxpwr", type=float, default=None, help="LOOP 1:MAXPWR percent (15-100) to set before starting; omit to leave unchanged")

    args = parser.parse_args()
    run(target_k=args.target, rate=args.rate, p=args.p, i=args.i, d=args.d,
        range_val=args.range, hold_minutes=args.hold, max_run_minutes=args.maxrun,
        max_over=args.maxover, maxpwr=args.maxpwr)
