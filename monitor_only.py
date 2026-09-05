"""
Read-only monitor/logger. Sends NO configuration commands -- just watches
whatever ramp/PID/setpoint is already active on the controller and logs it.
Use this to pick up monitoring on a run that's already in progress (e.g.
after a controller-side config script already set things up).

Usage:
  python monitor_only.py --target 315 --hold 3 --maxrun 9 --maxover 15 --tag pidtune
"""
import serial
import time
import datetime
import csv
import argparse

PORT = "COM5"
BAUD = 9600


def query_retry(ser, cmd, wait=0.2, retries=3):
    for attempt in range(retries):
        ser.reset_input_buffer()
        ser.write((cmd + "\r\n").encode())
        time.sleep(wait)
        resp = ser.readline().decode("utf-8", errors="ignore").strip()
        if resp:
            return resp
        time.sleep(0.2)
    return ""


def run(target_k, hold_minutes, max_run_minutes, max_over, tag):
    try:
        ser = serial.Serial(PORT, BAUD, timeout=2)
        time.sleep(0.5)
    except Exception as e:
        print(f"[ERROR] Could not open {PORT}: {e}")
        return

    idn = query_retry(ser, "*IDN?")
    print(f"[OK] Connected: {idn}")
    print(f"[INFO] Monitoring only -- no config commands sent.")
    print(f"[INFO] Watching for Target={target_k}K, hold={hold_minutes}min, "
          f"timeout={max_run_minutes}min, abort at +{max_over}K over target\n")

    p = query_retry(ser, "LOOP 1:PGAIN?")
    i = query_retry(ser, "LOOP 1:IGAIN?")
    d = query_retry(ser, "LOOP 1:DGAIN?")
    rng = query_retry(ser, "LOOP 1:RANGE?")
    rate = query_retry(ser, "LOOP 1:RATE?")
    ltype = query_retry(ser, "LOOP 1:TYPE?")
    print(f"[INFO] Live config: Type={ltype} Rate={rate} Range={rng} P={p} I={i} D={d}\n")

    now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"cryocon_log_{now_str}_{tag}.csv"
    f_log = open(csv_file, "w", newline="", encoding="utf-8")
    writer = csv.writer(f_log)
    writer.writerow([
        "Timestamp", "Elapsed_Sec", "Temp_A_K", "Setpoint_K", "Error_K",
        "Heater_Pct", "Rate", "P_Gain", "I_Gain", "D_Gain", "Range", "Type", "Stage"
    ])
    f_log.flush()
    print(f"[OK] Data logging active: {csv_file}\n")

    print(f"{'Time':^10} {'Elapsed':^8} {'Temp A (K)':^12} {'Error':^10} {'Heater%':^9} {'Stage':^12}")
    print("-" * 66)

    start_time = time.time()
    stage = "RAMPING"
    reach_time = None
    peak_error = 0.0
    aborted = False

    try:
        while True:
            elapsed = time.time() - start_time
            ts = datetime.datetime.now().strftime("%H:%M:%S")

            ta_str = query_retry(ser, "INPUT? A")
            ht_str = query_retry(ser, "LOOP 1:OUTP?").replace("%", "").strip()
            try:
                ta = float(ta_str)
            except ValueError:
                time.sleep(1.0)
                continue
            try:
                ht = float(ht_str)
            except ValueError:
                ht = 0.0

            err = ta - target_k
            if abs(err) > abs(peak_error):
                peak_error = err

            if err > max_over:
                print(f"\n[SAFETY ABORT] Temp {ta:.2f}K exceeds setpoint+{max_over}K! Stopping control.")
                query_retry(ser, "STOP")
                aborted = True
                stage = "ABORTED"

            if stage in ("RAMPING", "SETTLED") and abs(err) < 0.2:
                if stage == "RAMPING":
                    print(f"\n>>> [SETTLED] |Error| < 0.2K reached at {ta:.3f}K "
                          f"(peak error during approach: {peak_error:+.3f}K) <<<\n")
                stage = "SETTLED"
                if reach_time is None:
                    reach_time = time.time()
            elif stage == "SETTLED" and abs(err) >= 0.2:
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

            print(f"{ts:^10} {elapsed:^8.1f} {ta:^12.3f} {err:^+10.3f} {ht:^9.1f} {stage:^12}")

            writer.writerow([
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                f"{elapsed:.1f}", f"{ta:.4f}", f"{target_k:.2f}", f"{err:+.4f}",
                f"{ht:.2f}", rate, p, i, d, rng, ltype, stage
            ])
            f_log.flush()

            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\n\n[ABORT] Stopped by user (Ctrl+C).")
    finally:
        f_log.close()
        final_temp = query_retry(ser, "INPUT? A")
        final_heater = query_retry(ser, "LOOP 1:OUTP?")
        ser.close()
        print(f"\n[SUMMARY] Peak error during monitored window: {peak_error:+.3f} K")
        print(f"[SUMMARY] Final temp: {final_temp} K | Final heater: {final_heater}%")
        print(f"[OK] Data saved to {csv_file}")
        print("[OK] Disconnected.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read-only Cryocon 22C monitor/logger")
    parser.add_argument("--target", type=float, required=True)
    parser.add_argument("--hold", type=float, default=3.0)
    parser.add_argument("--maxrun", type=float, default=10.0)
    parser.add_argument("--maxover", type=float, default=15.0)
    parser.add_argument("--tag", type=str, default="monitor")

    args = parser.parse_args()
    run(target_k=args.target, hold_minutes=args.hold, max_run_minutes=args.maxrun,
        max_over=args.maxover, tag=args.tag)
