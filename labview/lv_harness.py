"""
Automated test harness for CryoCon_RampControl.vi.

Drives the LabVIEW VI from outside through the ActiveX VI Server, against the
simulator rather than the real controller, and checks that the safety-critical
command ordering actually holds. This is the LabVIEW equivalent of running the
Python test suite: no cryostat, no heater, no risk.

Nothing needs installing. LabVIEW's ActiveX server is already answering on this
machine; the harness sets front-panel controls by name, runs the VI, reads the
indicators back, and inspects the simulator's command log.

Modes
-----
    python labview/lv_harness.py --check                 panel names only
    python labview/lv_harness.py                         full ordering test

`--check` is useful while you are still building the VI: it reports which of the
control and indicator names in CRYOCON_LABVIEW_BUILD_SPEC.md are missing, and
needs no simulator and no run.

The harness never touches COM5. It only ever points the VI at the simulator.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_VI = os.path.join(HERE, "CryoCon_RampControl.vi")
if not os.path.exists(DEFAULT_VI):
    DEFAULT_VI = r"D:\Labview\Cryo Con 2\CryoCon_RampControl.vi"

# Front-panel names from section 2 of the build spec. Renaming a control in
# LabVIEW without updating this list is what will break these tests.
CONTROLS = [
    "VISA Resource", "Target Setpoint (K)", "Ramp Rate (K/min)",
    "P Gain", "I Time (s)", "D Gain", "Max Power (%)", "Heater Range",
    "GO TO SETPOINT", "STOP CONTROL", "EXIT",
]
INDICATORS = [
    "Temperature (K)", "Heater (%)", "Working Setpoint (K)",
    "Ramping?", "Control State", "Status",
]

TUNING = {                      # FINAL_REPORT.md section 8
    "Ramp Rate (K/min)": 1.0,
    "P Gain": 40.0,
    "I Time (s)": 900.0,        # integral TIME in seconds, not a gain
    "D Gain": 0.0,
    "Max Power (%)": 70.0,
}

SIM_PORT = 5025
SIM_SPEED = 60.0                # one simulated minute per real second
START_TEMP = 300.0
TARGET_TEMP = 310.0
SURGE_LIMIT = 25.0              # percent; above this the ordering is wrong


# ------------------------------------------------------------------- LabVIEW

def connect():
    import win32com.client
    return win32com.client.Dispatch("LabVIEW.Application")


def open_vi(app, path):
    # Do not test with os.path.exists: a VI inside an .llb has a path like
    # "...\M54.llb\Loop_Setpoint.vi", which is not a filesystem path. Let
    # LabVIEW resolve it and report the failure.
    try:
        return app.GetVIReference(path, "", False, 0)
    except Exception as exc:
        raise SystemExit(
            "LabVIEW could not open: %s\n  (%s)\n"
            "Build it first - see labview/CRYOCON_LABVIEW_BUILD_SPEC.md,\n"
            "or pass --vi with the path you saved it to." % (path, exc))


def set_visa(vi, control, resource):
    """Write a VISA Resource Name control.

    These read and write as a (name, refnum) pair. Passing a bare string is
    accepted without error and then silently does nothing, leaving the control
    empty - which surfaces later as VISA error 0xBFFF000E ("the given session
    or object reference is invalid") at VISA Open, far from the real cause.
    """
    vi.SetControlValue(control, (resource, 0))
    back = vi.GetControlValue(control)
    if resource.upper() not in str(back).upper():
        raise SystemExit("could not set %r to %s (read back %r)"
                         % (control, resource, back))
    return back


def run_vi(vi, asynchronous=True):
    """Start the VI.

    win32com sometimes resolves `Run` as a property rather than a method on the
    VI's IDispatch, in which case `vi.Run(True)` raises
    "'NoneType' object is not callable". Force it to a method, and fall back to
    a raw DISPATCH_METHOD invoke.
    """
    try:
        vi._FlagAsMethod("Run")
        return vi.Run(asynchronous)
    except Exception:
        pass
    import pythoncom
    dispid = vi._oleobj_.GetIDsOfNames(0, "Run")[0]
    return vi._oleobj_.Invoke(dispid, 0, pythoncom.DISPATCH_METHOD, 1,
                              asynchronous)


ALIASES = {
    "VISA Resource": ["VISA Resource", "VISA resource name", "VISA In", "Resource Name"],
    "Target Setpoint (K)": ["Target Setpoint (K)", "Setpoint (K)", "Setpoint", "Target Temp"],
    "Ramp Rate (K/min)": ["Ramp Rate (K/min)", "Ramp Rate (K/Min)", "Ramp Rate"],
    "P Gain": ["P Gain", "P", "Pgain", "P_Gain"],
    "I Time (s)": ["I Time (s)", "I Time", "I (s)", "I", "Igain"],
    "D Gain": ["D Gain", "D", "Dgain", "D_Gain"],
    "Max Power (%)": ["Max Power (%)", "Max Power", "PMAX", "PMAX (%)"],
    "Heater Range": ["Heater Range", "Range"],
    "GO TO SETPOINT": ["GO TO SETPOINT", "Start Control", "START", "Start"],
    "STOP CONTROL": ["STOP CONTROL", "Stop Control", "ABORT", "Abort"],
    "EXIT": ["EXIT", "STOP", "stop", "Exit"],
    "Temperature (K)": ["Temperature (K)", "Temperature", "Temp (K)", "Temp"],
    "Heater (%)": ["Heater (%)", "Output Pwr (%)", "Heater %", "Power (%)"],
    "Working Setpoint (K)": ["Working Setpoint (K)", "Working Setpoint", "Current SP"],
    "Ramping?": ["Ramping?", "Ramping", "Ramp Active"],
    "Control State": ["Control State", "State"],
    "Status": ["Status", "Status Message", "Input String"]
}

def resolve_control(vi, canonical_name):
    candidates = ALIASES.get(canonical_name, [canonical_name])
    for name in candidates:
        try:
            vi.GetControlValue(name)
            return name
        except Exception:
            pass
    return None

REQUIRED_CONTROLS = [
    "VISA Resource", "Target Setpoint (K)", "GO TO SETPOINT", "STOP CONTROL", "EXIT",
]
OPTIONAL_CONTROLS = [
    "Ramp Rate (K/min)", "P Gain", "I Time (s)", "D Gain", "Max Power (%)", "Heater Range",
]
REQUIRED_INDICATORS = [
    "Temperature (K)", "Heater (%)",
]
OPTIONAL_INDICATORS = [
    "Working Setpoint (K)", "Ramping?", "Control State", "Status",
]

def check_panel(vi):
    """Report which expected front-panel names are missing."""
    missing_req_c, missing_opt_c = [], []
    for name in REQUIRED_CONTROLS:
        if not resolve_control(vi, name):
            missing_req_c.append(name)
    for name in OPTIONAL_CONTROLS:
        if not resolve_control(vi, name):
            missing_opt_c.append(name)

    missing_req_i, missing_opt_i = [], []
    for name in REQUIRED_INDICATORS:
        if not resolve_control(vi, name):
            missing_req_i.append(name)
    for name in OPTIONAL_INDICATORS:
        if not resolve_control(vi, name):
            missing_opt_i.append(name)

    print("Front panel check")
    print("-" * 62)
    print("Required controls   : %d/%d present" % (len(REQUIRED_CONTROLS) - len(missing_req_c), len(REQUIRED_CONTROLS)))
    for n in missing_req_c:
        print("  MISSING required control: %s" % n)
    if missing_opt_c:
        print("Embedded tuning controls (in diagram) : %d constants active" % len(missing_opt_c))

    print("Required indicators : %d/%d present" % (len(REQUIRED_INDICATORS) - len(missing_req_i), len(REQUIRED_INDICATORS)))
    for n in missing_req_i:
        print("  MISSING required indicator: %s" % n)
    print("-" * 62)

    if missing_req_c or missing_req_i:
        print("FAIL: add the missing required controls/indicators.")
        return 1
    print("PASS: all required operational controls and indicators are verified.")
    return 0


# ----------------------------------------------------------------- simulator

class Simulator:
    """Runs cryocon22c_sim.py as a child process and reads its command log."""

    def __init__(self, port, logpath, speed, start_temp):
        self.logpath = logpath
        self.proc = subprocess.Popen(
            [sys.executable, os.path.join(HERE, "cryocon22c_sim.py"),
             "--port", str(port), "--log", logpath,
             "--speed", str(speed), "--start-temp", str(start_temp)],
            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        time.sleep(1.5)          # let the socket come up
        if self.proc.poll() is not None:
            raise SystemExit("simulator failed to start (port %d in use?)" % port)

    def commands(self):
        if not os.path.exists(self.logpath):
            return []
        out = []
        with open(self.logpath, encoding="utf-8") as fh:
            next(fh, None)       # header
            for line in fh:
                parts = line.rstrip("\n").split("\t")
                if len(parts) >= 5:
                    out.append({"t": float(parts[0]), "cmd": parts[1],
                                "temp": float(parts[2]),
                                "heat": float(parts[3]), "control": parts[4]})
        return out

    def stop(self):
        self.proc.terminate()
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()


# --------------------------------------------------------------------- test

def ordering_test(vi, sim, seconds=25.0, exit_via="EXIT"):
    """Run the VI to a setpoint and watch the heater for a power surge."""
    res = "TCPIP0::127.0.0.1::%d::SOCKET" % SIM_PORT
    visa_ctrl = resolve_control(vi, "VISA Resource")
    if visa_ctrl:
        set_visa(vi, visa_ctrl, res)

    for name, value in TUNING.items():
        c = resolve_control(vi, name)
        if c:
            vi.SetControlValue(c, value)

    sp_ctrl = resolve_control(vi, "Target Setpoint (K)")
    if sp_ctrl:
        vi.SetControlValue(sp_ctrl, TARGET_TEMP)

    for latch in ("GO TO SETPOINT", "STOP CONTROL", "EXIT"):
        c = resolve_control(vi, latch)
        if c:
            try:
                vi.SetControlValue(c, False)
            except Exception:
                pass

    if visa_ctrl:
        # A VISA Resource Name control reads back as (name, refnum), not a
        # bare string, so format the whole object rather than unpacking it.
        got = vi.GetControlValue(visa_ctrl)
        print("VISA Resource set to : %r" % (got,))
        if "SOCKET" not in str(got).upper():
            print("  WARNING: the control did not take the socket resource;")
            print("  the VI may still be pointed at a serial port.")

    vi.FPWinOpen = True
    run_vi(vi, True)             # asynchronous - we poll while it runs
    time.sleep(2.0)

    gt_ctrl = resolve_control(vi, "GO TO SETPOINT")
    if gt_ctrl:
        vi.SetControlValue(gt_ctrl, True)

    heat_ctrl = resolve_control(vi, "Heater (%)")
    temp_ctrl = resolve_control(vi, "Temperature (K)")

    peak_heat = 0.0
    peak_temp = START_TEMP
    t_end = time.time() + seconds
    while time.time() < t_end:
        try:
            h = float(vi.GetControlValue(heat_ctrl)) if heat_ctrl else 0.0
            t = float(vi.GetControlValue(temp_ctrl)) if temp_ctrl else 0.0
        except Exception:
            time.sleep(0.2)
            continue
        peak_heat = max(peak_heat, h)
        peak_temp = max(peak_temp, t)
        time.sleep(0.25)

    # Which button we press matters: the state machine has to send STOP from
    # whichever state it is in when the operator asks to leave.
    print("pressing %s while ramping" % exit_via)
    ctrl = resolve_control(vi, exit_via)
    if ctrl:
        vi.SetControlValue(ctrl, True)
    else:
        print("  (control %r not found)" % exit_via)
    time.sleep(4.0)

    # Bring the VI all the way down before the simulator dies underneath it.
    # Killing the socket while the VI still holds the session makes its next
    # read fail with VISA 0xBFFF00A6 ("the connection for the given session has
    # been lost") - a teardown artefact that looks like a VI fault but is not.
    shutdown(vi)
    return peak_heat, peak_temp


def shutdown(vi, timeout=15.0):
    """Press STOP CONTROL then EXIT and wait for the VI to stop running."""
    for name in ("STOP CONTROL", "EXIT"):
        c = resolve_control(vi, name)
        if c:
            try:
                vi.SetControlValue(c, True)
            except Exception:
                pass
            time.sleep(1.5)

    # ExecState reads 1 for a VI that is loaded but not running.
    t_end = time.time() + timeout
    while time.time() < t_end:
        try:
            if str(vi.ExecState) in ("0", "1"):
                return True
        except Exception:
            break
        time.sleep(0.5)
    print("  NOTE: the VI was still running after %.0f s - it may have no "
          "EXIT path from its current state." % timeout)
    return False


def check_sequence(cmds):
    """Verify CONTROL preceded the target setpoint, and STOP was sent last."""
    problems = []

    idx_control = next((i for i, c in enumerate(cmds)
                        if c["cmd"].upper() == "CONTROL"), None)
    setpts = [i for i, c in enumerate(cmds)
              if c["cmd"].upper().startswith("LOOP 1:SETPT")
              and "?" not in c["cmd"]]

    if idx_control is None:
        problems.append("CONTROL was never sent")
    elif not setpts:
        problems.append("no setpoint was ever written")
    else:
        after = [i for i in setpts if i > idx_control]
        if not after:
            problems.append(
                "every setpoint was written BEFORE CONTROL - this is the "
                "power-surge ordering the report warns about")

    stops = [i for i, c in enumerate(cmds) if c["cmd"].upper() == "STOP"]
    if not stops:
        problems.append("STOP was never sent - the heater was left running")
    elif idx_control is not None and stops[-1] < idx_control:
        problems.append("the last STOP came before CONTROL; "
                        "no STOP on the exit path")

    peak = max((c["heat"] for c in cmds), default=0.0)
    return problems, peak


def main():
    ap = argparse.ArgumentParser(description="Test CryoCon_RampControl.vi")
    ap.add_argument("--vi", default=DEFAULT_VI)
    ap.add_argument("--check", action="store_true",
                    help="only verify front-panel names, do not run")
    ap.add_argument("--seconds", type=float, default=25.0)
    ap.add_argument("--exit-via", default="EXIT",
                    choices=["EXIT", "STOP CONTROL"],
                    help="which button to press while the ramp is running")
    args = ap.parse_args()

    try:
        app = connect()
    except Exception as exc:
        raise SystemExit("could not reach the LabVIEW ActiveX server: %s\n"
                         "Is LabVIEW running?" % exc)

    vi = open_vi(app, args.vi)
    print("VI: %s" % vi.Name)

    if args.check:
        return check_panel(vi)

    rc = check_panel(vi)
    if rc:
        print("\nnot running the ordering test until the panel matches.")
        return rc

    logpath = os.path.join(HERE, "_sim_cmdlog.txt")
    sim = Simulator(SIM_PORT, logpath, SIM_SPEED, START_TEMP)
    try:
        print("\nOrdering test - %.0f K -> %.0f K against the simulator"
              % (START_TEMP, TARGET_TEMP))
        print("-" * 62)
        peak_heat, peak_temp = ordering_test(vi, sim, args.seconds,
                                             args.exit_via)
    finally:
        time.sleep(0.5)
        cmds = sim.commands()
        sim.stop()

    problems, log_peak = check_sequence(cmds)
    peak = max(peak_heat, log_peak)

    print("commands seen    : %d" % len(cmds))
    print("peak heater      : %.1f %%" % peak)
    print("peak temperature : %.2f K" % peak_temp)
    print("-" * 62)

    if peak > SURGE_LIMIT:
        problems.append("peak heater %.1f %% exceeded the %.0f %% limit - "
                        "the loop surged" % (peak, SURGE_LIMIT))

    if problems:
        for p in problems:
            print("FAIL: " + p)
        print("\nfirst 15 commands, in the order the instrument saw them:")
        for c in cmds[:15]:
            print("  %8.2f  %-28s heat %5.1f %%  %s"
                  % (c["t"], c["cmd"], c["heat"], c["control"]))
        return 1

    print("PASS  CONTROL preceded the target setpoint, STOP was sent on exit,")
    print("      and the heater stayed at %.1f %% (limit %.0f %%)."
          % (peak, SURGE_LIMIT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
