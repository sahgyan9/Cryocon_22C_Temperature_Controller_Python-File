"""
Live Data Tailer & Terminal Monitor
====================================
Monitors active acquisition files in Data/ in real-time.
Because this script reads from disk, it consumes zero VISA or serial resources
and can safely run alongside the GUI or LabVIEW without port contention.

Usage:
    python live_view.py
    python live_view.py Data/300K_100mV_11-56-28.dat
"""

import glob
import math
import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def get_latest_dat_file(data_dir: str = "Data") -> str:
    files = glob.glob(os.path.join(data_dir, "*.dat"))
    if not files:
        return ""
    return max(files, key=os.path.getmtime)


def tail_file(filepath: str):
    print("=" * 96)
    print(f" TAILING LIVE FILE: {filepath}")
    print("=" * 96)

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        # Print header
        header = f.readline()
        print(f"Header: {header.strip()}")
        print("-" * 96)
        print(f"{'Elapsed (s)':^12} | {'Temp (K)':^10} | {'Frequency (Hz)':^15} | {'R (Ohm)':^15} | {'X (Ohm)':^15} | {'|Z| (Ohm)':^12}")
        print("-" * 96)

        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue

            parts = line.strip().split("\t")
            if len(parts) >= 6:
                try:
                    el = float(parts[0])
                    t_k = float(parts[2])
                    freq = float(parts[3])
                    r_val = float(parts[4])
                    x_val = float(parts[5])
                    z_mag = math.sqrt(r_val ** 2 + x_val ** 2)
                    print(f"{el:10.3f}s  | {t_k:8.3f} K | {freq:13.1f} | {r_val:13.2e} | {x_val:13.2e} | {z_mag:10.2e}")
                except ValueError:
                    pass


def main():
    target_file = sys.argv[1] if len(sys.argv) > 1 else ""
    if not target_file:
        print("[INFO] No file specified. Searching for latest active .dat file in Data/...")
        while not target_file:
            target_file = get_latest_dat_file("Data")
            if not target_file:
                time.sleep(1.0)
        print(f"[FOUND] Watching: {target_file}")

    try:
        tail_file(target_file)
    except KeyboardInterrupt:
        print("\n[INFO] Live view terminated.")


if __name__ == "__main__":
    main()
