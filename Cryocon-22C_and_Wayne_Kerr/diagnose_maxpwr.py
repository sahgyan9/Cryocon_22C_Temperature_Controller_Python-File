"""
Cryo-con 22C Heater Power Ceiling Diagnostic
============================================
Determines why `LOOP 1:MAXPWR 100.0` is not taking effect on the physical 22C.

Run this with the GUI CLOSED - it needs exclusive use of the serial port.

Phase 1 (always, heater stays OFF the whole time):
  - sends STOP so the loop is disengaged and the station is in a safe state
  - reports the ceiling the instrument currently holds
  - tries several command spellings and reports which the firmware accepts

Phase 2 (only with --test-with-control-on):
  - repeats the write with CONTROL engaged, to test the hypothesis that the 22C
    silently ignores loop-configuration writes while the loop is running.
    The setpoint is parked at the live temperature first (anti-surge rule), so the
    heater engages at hold power, never at full power. STOP is sent on every exit.

Usage:
    python diagnose_maxpwr.py
    python diagnose_maxpwr.py --test-with-control-on
"""

import argparse
import sys
import time

from cryocon_controller import Cryocon22C

SPELLINGS = ["100.0", "100", "099.9", "99.9", "99"]


def show(cryo, note):
    raw = cryo.query("LOOP 1:MAXPWR?")
    val = cryo.get_max_power(1)
    shown = "unparseable" if val != val else f"{val:.1f}%"
    print(f"    {note:<34} raw={raw!r:<14} parsed={shown}")
    return val


def try_spellings(cryo, phase):
    print(f"\n  --- {phase}: trying each command spelling ---")
    accepted = []
    for sp in SPELLINGS:
        cryo.write(f"LOOP 1:MAXPWR {sp}", wait_time=0.4)
        time.sleep(0.3)
        val = show(cryo, f"after 'LOOP 1:MAXPWR {sp}'")
        if val == val and abs(val - float(sp)) <= 0.15:
            accepted.append((sp, val))
    return accepted


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default="COM5")
    ap.add_argument("--baud", type=int, default=57600)
    ap.add_argument("--test-with-control-on", action="store_true",
                    help="Also test writes with the loop ENGAGED (heater will run at hold power)")
    args = ap.parse_args()

    cryo = Cryocon22C(port=args.port, baud_rate=args.baud, mock=False)
    if not cryo.connect():
        print(f"[FATAL] Could not open {args.port}. Is the GUI still running and holding the port?")
        sys.exit(1)

    try:
        print("=" * 72)
        print(" CRYO-CON 22C HEATER CEILING DIAGNOSTIC")
        print("=" * 72)
        print(f"  IDN            : {cryo.query('*IDN?')}")

        print("\n[PHASE 0] Disengaging the loop so the station is safe during the test.")
        cryo.stop_control()
        print(f"  CONTROL        : {cryo.query('CONTROL?')}")
        print(f"  live T (A)     : {cryo.read_temperature('A'):.3f} K")
        print(f"  heater range   : {cryo.query('LOOP 1:RANGE?')}")
        print(f"  loop type      : {cryo.query('LOOP 1:TYPE?')}")

        print("\n[PHASE 1] Ceiling as the instrument currently holds it (CONTROL = OFF):")
        baseline = show(cryo, "current value")
        if baseline != baseline:
            print("    >>> The 22C does not answer 'LOOP 1:MAXPWR?' at all.")
            print("    >>> The ceiling can only be read and set from the FRONT PANEL.")

        acc_off = try_spellings(cryo, "CONTROL OFF")

        acc_on = []
        if args.test_with_control_on:
            print("\n[PHASE 2] Repeating with the loop ENGAGED (parking setpoint at live T first).")
            live = cryo.read_temperature("A")
            cryo.write("LOOP 1:TYPE PID", wait_time=0.3)
            cryo.write(f"LOOP 1:SETPT {live:.3f}", wait_time=0.5)
            cryo.write("CONTROL", wait_time=0.3)
            time.sleep(2.5)
            print(f"  CONTROL        : {cryo.query('CONTROL?')}   heater={cryo.read_heater_output(1):.1f}%")
            acc_on = try_spellings(cryo, "CONTROL ON")

        print("\n" + "=" * 72)
        print(" VERDICT")
        print("=" * 72)
        if not acc_off and not acc_on:
            if baseline != baseline:
                print("  MAXPWR is not readable over SCPI on this firmware.")
                print("  -> Set the ceiling on the FRONT PANEL and remove the MAXPWR write from")
                print("     arm_safe_ramp(), otherwise every stage may overwrite your setting.")
            else:
                print(f"  Every spelling was rejected; ceiling stayed at {baseline:.1f}%.")
                print("  -> Set it on the FRONT PANEL and stop writing it from software.")
        else:
            if acc_off:
                print(f"  Accepted with CONTROL OFF : {', '.join(s for s, _ in acc_off)}")
            if args.test_with_control_on:
                if acc_on:
                    print(f"  Accepted with CONTROL ON  : {', '.join(s for s, _ in acc_on)}")
                else:
                    print("  REJECTED with CONTROL ON  -> the 22C ignores MAXPWR while the loop")
                    print("     is engaged. arm_safe_ramp() must send STOP before configuring.")
        print()

    finally:
        print("[SAFETY] Disengaging heater...")
        cryo.stop_control()
        cryo.disconnect()


if __name__ == "__main__":
    main()
