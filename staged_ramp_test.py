"""
Cryocon 22C - staged ramp campaign (unattended)
==============================================
Walks a list of setpoints with ONE fixed gain set and ONE flat ramp rate, so the
only variable between stages is the setpoint delta. Purpose: confirm the tuned
gains (P=25 I=900 D=0) hold as the hop size grows 7 -> 10 -> 5 -> 15 -> 15 -> 30 K
on the way to the 450 K target.

Differences from pid_tune_test.py, all of which matter for running overnight:

  * Safety: STOP is sent on ANY exit path -- exception, Ctrl+C, abort, or
    absolute-limit trip. pid_tune_test.py leaves the heater running if the
    process dies, which is fine attended and not fine at 3am.
  * Absolute ceiling (--maxtemp) independent of the per-stage overshoot abort.
  * Correct setpoint resync (drops to TYPE PID so the setpoint jumps instead of
    ramping -- see OVERSHOOT_TUNING_LOG.md section 8).
  * Settle detection resets if the band is left again (the bug fixed earlier).
  * After the final stage it keeps holding and watchdogging rather than exiting,
    so the station is never left controlling unwatched.

Usage:
  python staged_ramp_test.py --targets 375,385,390,405,420,450 \
      --rate 1.0 --p 25 --i 900 --d 0 --range HI --maxpwr 70
"""
import serial
import time
import datetime
import csv
import argparse
import os
import sys

PORT = "COM5"
BAUD = 57600


def query(ser, cmd, wait=0.2, retries=6):
    for _ in range(retries):
        try:
            ser.reset_input_buffer()
            ser.write((cmd + "\r\n").encode())
            time.sleep(wait)
            resp = ser.readline().decode("utf-8", errors="ignore").strip()
            if resp:
                return resp
        except Exception as e:
            print(f"[WARN] serial error on '{cmd}': {e}")
        time.sleep(0.3)
    return ""


def send(ser, cmd, wait=0.2):
    ser.write((cmd + "\r\n").encode())
    time.sleep(wait)


def read_temp(ser, last):
    """Never raise -- a bad read must not kill an overnight run."""
    try:
        return float(query(ser, "INPUT? A"))
    except ValueError:
        return last


def read_heater(ser):
    try:
        return float(query(ser, "LOOP 1:OUTP?").replace("%", "").strip())
    except ValueError:
        return float("nan")


def emergency_stop(ser, why):
    """Best-effort: cut control on every exit path."""
    print(f"\n[STOP] {why} -- disengaging control loop.")
    for _ in range(3):
        try:
            send(ser, "STOP", wait=0.4)
            time.sleep(0.3)
            if query(ser, "CONTROL?").upper().startswith("OFF"):
                print("[STOP] Confirmed CONTROL = OFF.")
                return True
        except Exception as e:
            print(f"[STOP] retry after error: {e}")
    print("[STOP] WARNING: could not confirm CONTROL=OFF -- CHECK THE INSTRUMENT.")
    return False


def configure_stage(ser, target, rate, p, i, d, range_val, maxpwr):
    """Resync the working setpoint to 'now', then arm the ramp to target."""
    live = read_temp(ser, target)
    # Resync MUST happen outside ramp mode or it ramps instead of jumping.
    send(ser, "LOOP 1:TYPE PID")
    time.sleep(0.5)
    send(ser, f"LOOP 1:SETPT {live}")
    time.sleep(1.5)

    send(ser, f"LOOP 1:RANGE {range_val}")
    time.sleep(1.0)                      # range change throws a physical relay
    send(ser, f"LOOP 1:MAXPWR {maxpwr}")
    send(ser, f"LOOP 1:PGAIN {p}")
    send(ser, f"LOOP 1:IGAIN {i}")
    send(ser, f"LOOP 1:DGAIN {d}")
    send(ser, f"LOOP 1:RATE {rate}")

    # Engage control BEFORE arming the ramp, while the setpoint is still parked
    # at the live reading. If CONTROL is off when the target setpoint is
    # written, no ramp is armed (the ramp state machine only runs while
    # controlling), so switching CONTROL on afterwards makes the loop see the
    # FULL setpoint error at once -- P=25 on a 10 K error demands 250% and the
    # heater slams to the MAXPWR cap for tens of seconds, winding the
    # integrator up exactly like the saturation failure this whole project
    # exists to avoid. Observed 2026-09-05: heater pinned at 70% from a cold
    # CONTROL=OFF start. Engaging control at zero error first means the loop
    # starts from ~hold power, and only then does the setpoint write arm a
    # clean ramp.
    send(ser, "CONTROL")
    time.sleep(3.0)                      # let the loop settle at hold power
    send(ser, "LOOP 1:TYPE RAMPP")       # setpoint change below arms the ramp
    send(ser, f"LOOP 1:SETPT {target}")
    return live


def run(targets, rate, p, i, d, range_val, maxpwr, band, hold_min,
        stage_pad_min, max_over, max_temp, hold_hours):

    print("=" * 78)
    print("  CRYOCON 22C - STAGED RAMP CAMPAIGN (unattended)")
    print("=" * 78)
    print(f"  Stages          : {' -> '.join(str(t) for t in targets)} K")
    print(f"  Gains           : P={p}  I={i} s  D={d}   Range={range_val}  MaxPwr={maxpwr}%")
    print(f"  Flat ramp rate  : {rate} K/min (same for every stage)")
    print(f"  Settle          : |err| <= {band} K held {hold_min} min")
    print(f"  Aborts          : setpoint+{max_over} K, or absolute {max_temp} K")
    print(f"  Final hold      : {hold_hours} h watchdog at {targets[-1]} K")
    print("=" * 78)

    ser = None
    try:
        ser = serial.Serial(PORT, BAUD, timeout=2)
        time.sleep(0.5)
    except Exception as e:
        print(f"[ERROR] Could not open {PORT}: {e}")
        return

    now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("data", exist_ok=True)
    csv_file = os.path.join("data", f"cryocon_log_{now_str}_staged.csv")
    f_log = open(csv_file, "w", newline="", encoding="utf-8")
    writer = csv.writer(f_log)
    writer.writerow(["Timestamp", "Elapsed_Sec", "Stage_Idx", "Stage_Target_K",
                     "Temp_A_K", "Error_K", "Ramp_SP_K", "Track_Err_K",
                     "Heater_Pct", "Ramp_Rate_K_min", "P_Gain", "I_Gain",
                     "D_Gain", "Range", "MaxPwr_Pct", "Phase"])
    f_log.flush()

    print(f"[OK] Connected: {query(ser, '*IDN?')}")
    print(f"[OK] Logging to {csv_file}\n")

    t0 = time.time()
    results = []
    last_temp = read_temp(ser, 300.0)

    try:
        for idx, target in enumerate(targets):
            start_temp = configure_stage(ser, target, rate, p, i, d, range_val, maxpwr)
            delta = target - start_temp
            budget = abs(delta) / max(rate, 1e-6) + stage_pad_min      # minutes
            print("-" * 78)
            print(f"[STAGE {idx+1}/{len(targets)}] {start_temp:.3f} K -> {target:.2f} K "
                  f"(delta {delta:+.2f} K)  budget {budget:.0f} min")
            print("-" * 78)

            s_start = time.time()
            peak_err = -1e9
            in_band_since = None
            settled = False

            while True:
                elapsed_total = time.time() - t0
                s_elapsed = time.time() - s_start

                last_temp = ta = read_temp(ser, last_temp)
                ht = read_heater(ser)
                err = ta - target
                peak_err = max(peak_err, err)

                ramp_sp = (min(start_temp + rate * s_elapsed / 60.0, target)
                           if target >= start_temp
                           else max(start_temp - rate * s_elapsed / 60.0, target))

                # ---- safety ----
                if ta > max_temp:
                    emergency_stop(ser, f"ABSOLUTE LIMIT: {ta:.2f} K > {max_temp} K")
                    return
                if err > max_over:
                    emergency_stop(ser, f"OVERSHOOT ABORT: {ta:.2f} K is {err:+.2f} K past setpoint")
                    return

                # ---- settle detection (resets if the band is left) ----
                if abs(err) <= band:
                    if in_band_since is None:
                        in_band_since = time.time()
                        print(f"  >>> entered +/-{band} K band at {ta:.3f} K "
                              f"(peak so far {peak_err:+.3f} K)")
                    elif time.time() - in_band_since >= hold_min * 60:
                        settled = True
                else:
                    if in_band_since is not None:
                        print(f"  >>> LEFT the band at {ta:.3f} K ({err:+.3f} K) -- hold timer reset")
                    in_band_since = None

                phase = "SETTLED" if settled else ("HOLDING" if in_band_since else "RAMPING")
                writer.writerow([
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    f"{elapsed_total:.1f}", idx + 1, f"{target:.2f}",
                    f"{ta:.4f}", f"{err:+.4f}", f"{ramp_sp:.4f}", f"{ramp_sp - ta:+.4f}",
                    f"{ht:.2f}", f"{rate:.2f}", p, i, d, range_val, maxpwr, phase])
                f_log.flush()

                if int(s_elapsed) % 30 < 1:
                    print(f"  t={s_elapsed:7.0f}s  T={ta:8.3f}  err={err:+7.3f}  "
                          f"heat={ht:5.1f}%  {phase}")

                if settled:
                    print(f"[STAGE {idx+1}] SETTLED at {ta:.4f} K  err {err:+.4f} K  "
                          f"| PEAK OVERSHOOT {peak_err:+.4f} K  | {s_elapsed/60:.1f} min")
                    results.append((target, delta, peak_err, err, s_elapsed / 60.0, "settled"))
                    break

                if s_elapsed > budget * 60:
                    print(f"[STAGE {idx+1}] TIMEOUT after {budget:.0f} min at {ta:.4f} K "
                          f"(err {err:+.4f} K, peak {peak_err:+.4f} K) -- moving on")
                    results.append((target, delta, peak_err, err, s_elapsed / 60.0, "timeout"))
                    break

                time.sleep(1.0)

        # ---------- summary ----------
        print("\n" + "=" * 78)
        print("  CAMPAIGN SUMMARY")
        print("=" * 78)
        print(f"  {'target':>8} {'delta':>8} {'peak over':>11} {'final err':>11} {'min':>7}  outcome")
        for tg, dl, pk, fe, mn, oc in results:
            print(f"  {tg:>8.1f} {dl:>+8.2f} {pk:>+11.3f} {fe:>+11.3f} {mn:>7.1f}  {oc}")
        print("=" * 78)

        # ---------- final watchdog hold ----------
        final = targets[-1]
        print(f"\n[HOLD] Holding {final} K with watchdog for up to {hold_hours} h.")
        print("[HOLD] Control stays ON so the station is at temperature when you return.")
        print("[HOLD] Stop this script before connecting LabVIEW (it owns COM5).\n")
        h_start = time.time()
        while time.time() - h_start < hold_hours * 3600:
            last_temp = ta = read_temp(ser, last_temp)
            ht = read_heater(ser)
            err = ta - final
            if ta > max_temp:
                emergency_stop(ser, f"ABSOLUTE LIMIT during hold: {ta:.2f} K")
                return
            if err > max_over:
                emergency_stop(ser, f"DRIFT during hold: {err:+.2f} K past setpoint")
                return
            writer.writerow([
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                f"{time.time()-t0:.1f}", len(targets), f"{final:.2f}",
                f"{ta:.4f}", f"{err:+.4f}", f"{final:.4f}", f"{final-ta:+.4f}",
                f"{ht:.2f}", f"{rate:.2f}", p, i, d, range_val, maxpwr, "HOLD"])
            f_log.flush()
            if int(time.time() - h_start) % 300 < 2:
                print(f"  [hold] {ta:.4f} K  err {err:+.4f}  heat {ht:.1f}%  "
                      f"({(time.time()-h_start)/3600:.1f} h)")
            time.sleep(2.0)

        print("[HOLD] Watchdog window elapsed.")
        emergency_stop(ser, "End of scheduled hold window")

    except KeyboardInterrupt:
        emergency_stop(ser, "Interrupted by user (Ctrl+C)")
    except Exception as e:
        import traceback
        traceback.print_exc()
        emergency_stop(ser, f"Unhandled exception: {e}")
    finally:
        try:
            f_log.close()
        except Exception:
            pass
        try:
            print(f"[FINAL] Temp A = {query(ser, 'INPUT? A')} K | "
                  f"heater = {query(ser, 'LOOP 1:OUTP?')}% | "
                  f"control = {query(ser, 'CONTROL?')}")
            ser.close()
        except Exception:
            pass
        print(f"[OK] Data saved to {csv_file}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Cryocon 22C staged ramp campaign")
    ap.add_argument("--targets", type=str, required=True,
                    help="Comma-separated setpoints in K, e.g. 375,385,390,405,420,450")
    ap.add_argument("--rate", type=float, default=1.0)
    ap.add_argument("--p", type=float, default=25.0)
    ap.add_argument("--i", type=float, default=900.0)
    ap.add_argument("--d", type=float, default=0.0)
    ap.add_argument("--range", dest="range_val", type=str, default="HI")
    ap.add_argument("--maxpwr", type=float, default=70.0)
    ap.add_argument("--band", type=float, default=0.10,
                    help="Settle band in K (default 0.10)")
    ap.add_argument("--hold", type=float, default=3.0,
                    help="Minutes inside the band before a stage counts as settled")
    ap.add_argument("--stagepad", type=float, default=25.0,
                    help="Minutes allowed beyond the ideal ramp time before timing out a stage")
    ap.add_argument("--maxover", type=float, default=3.0,
                    help="Abort if temperature exceeds the stage setpoint by this many K")
    ap.add_argument("--maxtemp", type=float, default=470.0,
                    help="Absolute ceiling; abort immediately above this")
    ap.add_argument("--holdhours", type=float, default=8.0,
                    help="Hours to hold the final setpoint under watchdog")
    a = ap.parse_args()

    tg = [float(x) for x in a.targets.split(",") if x.strip()]
    run(tg, a.rate, a.p, a.i, a.d, a.range_val, a.maxpwr, a.band, a.hold,
        a.stagepad, a.maxover, a.maxtemp, a.holdhours)
