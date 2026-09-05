"""
Live view of a running Cryocon test.

Reads the newest cryocon_log_*.csv and redraws every second. It does NOT open
COM5, so it is safe to run in a second terminal while a test owns the port
(only one process can hold the serial port -- that is why monitor_only.py
cannot be used at the same time as a test).

Usage:
    python live_view.py              # follow the newest log automatically
    python live_view.py somefile.csv # follow a specific log
"""
import csv
import glob
import os
import sys
import time

BAR_W = 44


def newest_log():
    files = glob.glob(os.path.join("data", "cryocon_log_*.csv"))
    files += glob.glob("cryocon_log_*.csv")   # fallback if run from data/
    return max(files, key=os.path.getmtime) if files else None


def read_rows(path):
    try:
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except Exception:
        return []


def band_bar(err, band=0.1, half_span=0.6):
    """ASCII bar: where the error sits relative to the +/-band tolerance."""
    slot = lambda v: max(0, min(BAR_W - 1,
                                int((v + half_span) / (2 * half_span) * BAR_W)))
    cells = ["-"] * BAR_W
    for edge in (-band, band):
        cells[slot(edge)] = "|"
    cells[slot(0.0)] = "+"
    cells[slot(err)] = "#"
    return "".join(cells)


def main():
    target_file = sys.argv[1] if len(sys.argv) > 1 else None
    print("live view -- Ctrl+C to exit (this does not affect the running test)\n")
    last_n = -1
    try:
        while True:
            path = target_file or newest_log()
            if not path:
                print("waiting for a log file...", end="\r")
                time.sleep(1.0)
                continue

            rows = read_rows(path)
            if not rows:
                time.sleep(1.0)
                continue

            r = rows[-1]
            g = lambda k, d="-": r.get(k, d)
            tgt = float(g("Stage_Target_K") or g("Setpoint_K") or 0)
            temp = float(g("Temp_A_K", "nan"))
            err = float(g("Error_K", "nan"))
            heat = float(g("Heater_Pct", "nan"))
            elapsed = float(g("Elapsed_Sec", "0"))

            errs = [float(x["Error_K"]) for x in rows if x.get("Error_K")]
            peak = max(errs) if errs else float("nan")

            # rate of change over the last ~30 samples
            drift = float("nan")
            if len(rows) > 30:
                a, b = rows[-30], rows[-1]
                dt = float(b["Elapsed_Sec"]) - float(a["Elapsed_Sec"])
                if dt > 0:
                    drift = (float(b["Temp_A_K"]) - float(a["Temp_A_K"])) / dt * 60

            inband = abs(err) <= 0.1
            os.system("cls" if os.name == "nt" else "clear")
            print(f"  file    : {path}")
            print(f"  gains   : P={g('P_Gain')}  I={g('I_Gain')} s  D={g('D_Gain')}"
                  f"   rate={g('Ramp_Rate_K_min')} K/min  cap={g('MaxPwr_Pct')}%")
            print(f"  stage   : {g('Stage_Idx','-')}   phase: {g('Phase') or g('Stage')}"
                  f"   elapsed: {elapsed/60:6.1f} min")
            print()
            print(f"  TARGET  : {tgt:10.3f} K")
            print(f"  TEMP    : {temp:10.4f} K")
            print(f"  ERROR   : {err:+10.4f} K   {'<<< INSIDE +/-0.1 K' if inband else ''}")
            print(f"  drift   : {drift:+10.4f} K/min")
            print(f"  heater  : {heat:10.2f} %")
            print(f"  peak err: {peak:+10.4f} K   (worst so far this run)")
            print()
            print(f"  -0.6{' ' * (BAR_W - 8)}+0.6")
            print(f"  {band_bar(err)}")
            print(f"  '|' = +/-0.1 K tolerance   '+' = setpoint   '#' = now")
            if len(rows) != last_n:
                last_n = len(rows)
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nlive view closed (the test keeps running).")


if __name__ == "__main__":
    main()
