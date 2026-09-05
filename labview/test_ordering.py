"""
Regression test for the command-ordering rule in FINAL_REPORT.md section 9.

Runs the same 10 K step against the simulator twice: once with the setpoint
written before CONTROL (the trap), once in the validated order. The wrong order
must slam the heater to MAXPWR; the right order must not.

This is the reference behaviour the LabVIEW VI has to reproduce. lv_harness.py
drives the VI through the same two cases and compares against these thresholds.

    python labview/test_ordering.py
"""

import socket
import sys
import threading
import time

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])

from cryocon22c_sim import Instrument, SimServer  # noqa: E402

HOST = "127.0.0.1"
SPEED = 60.0          # 60x: one simulated minute per real second
SETTLE = 2.0          # real seconds to watch after the step


class Link:
    """Minimal SCPI client, same framing the M54 driver uses (CR+LF)."""

    def __init__(self, host, port):
        self.s = socket.create_connection((host, port), timeout=5)

    def write(self, cmd):
        self.s.sendall(cmd.encode() + b"\r\n")
        time.sleep(0.02)

    def query(self, cmd):
        self.s.sendall(cmd.encode() + b"\r\n")
        buf = b""
        while not buf.endswith(b"\r\n"):
            buf += self.s.recv(256)
        return buf.decode().strip()

    def close(self):
        self.s.close()


def load_tuning(link):
    """Section 9 step 1 - the validated tuning."""
    for cmd in ("LOOP 1:RANGE HI", "LOOP 1:MAXPWR 70", "LOOP 1:PGAIN 40",
                "LOOP 1:IGAIN 900", "LOOP 1:DGAIN 0", "LOOP 1:RATE 1.0"):
        link.write(cmd)


def watch(link, seconds):
    """Poll temperature and heater, return the peak heater percentage."""
    peak_heat = 0.0
    peak_temp = 0.0
    t_end = time.time() + seconds
    while time.time() < t_end:
        h = float(link.query("LOOP 1:OUTP?"))
        t = float(link.query("INPUT? A"))
        peak_heat = max(peak_heat, h)
        peak_temp = max(peak_temp, t)
        time.sleep(0.05)
    return peak_heat, peak_temp


def run_case(port, wrong_order):
    inst = Instrument(t_block=300.0, t_sensor=300.0)
    stop = threading.Event()

    def plant():
        while not stop.is_set():
            with inst.lock:
                inst.step(0.1 * SPEED)
            time.sleep(0.1)

    threading.Thread(target=plant, daemon=True).start()
    server = SimServer((HOST, port), inst, None)
    server.record = lambda cmd: None          # quiet during the test
    threading.Thread(target=server.serve_forever, daemon=True).start()

    try:
        link = Link(HOST, port)
        link.write("STOP")
        load_tuning(link)
        target = 310.0

        if wrong_order:
            # The trap: target written while control is OFF, so no ramp arms.
            link.write("LOOP 1:TYPE RAMPP")
            link.write("LOOP 1:SETPT %.3f" % target)
            link.write("CONTROL")
        else:
            # Section 9 step 2, in order.
            t_now = float(link.query("INPUT? A"))
            link.write("LOOP 1:TYPE PID")
            link.write("LOOP 1:SETPT %.3f" % t_now)
            link.write("LOOP 1:TYPE RAMPP")
            link.write("CONTROL")
            link.write("LOOP 1:SETPT %.3f" % target)

        peak_heat, peak_temp = watch(link, SETTLE)
        link.write("STOP")
        link.close()
        return peak_heat, peak_temp
    finally:
        stop.set()
        server.shutdown()
        server.server_close()


def main():
    print("Ordering regression test - 300 K -> 310 K, RAMPP at 1 K/min")
    print("-" * 62)

    bad_heat, _ = run_case(5099, wrong_order=True)
    print("setpoint before CONTROL   peak heater %5.1f %%" % bad_heat)

    good_heat, _ = run_case(5098, wrong_order=False)
    print("CONTROL before setpoint   peak heater %5.1f %%" % good_heat)
    print("-" * 62)

    failures = []
    if bad_heat < 60.0:
        failures.append("wrong order did not produce the expected power surge "
                        "(got %.1f %%, expected >= 60 %%)" % bad_heat)
    if good_heat > 25.0:
        failures.append("correct order still surged (got %.1f %%, "
                        "expected <= 25 %%)" % good_heat)

    if failures:
        for f in failures:
            print("FAIL: " + f)
        return 1
    print("PASS  the simulator reproduces the ordering rule:")
    print("      wrong order pins the heater at the %.0f %% limit," % bad_heat)
    print("      correct order holds it to %.1f %%." % good_heat)
    return 0


if __name__ == "__main__":
    sys.exit(main())
