"""
Cryocon 22C simulator - lets the LabVIEW VI be developed and tested with no
instrument attached, and no risk to the cryostat.

It speaks the same SCPI subset as the real controller over a TCP socket, so
LabVIEW reaches it through an ordinary NI-VISA resource:

    TCPIP0::127.0.0.1::5025::SOCKET

The thermal plant is not invented. C and k(T) were least-squares fitted to
21,722 samples across the 26 logged runs in ../data, and the fit reproduces the
measured power budget in FINAL_REPORT.md section 7 to within about 1 W:

    hold power   350 K   3.7 W (report 3.0)
                 400 K   6.9 W (report 6.8)
                 450 K   9.8 W (report 10.6)

The point of the simulator is the *ordering rule*. It reproduces the failure
mode described in section 9: a setpoint written while control is OFF does not
arm a ramp, so switching control on afterwards presents the whole error at once
and the heater slams to its limit. Send the commands in the right order and the
ramp is smooth. That makes the ordering rule an automated regression test
instead of something you have to remember.

Usage
-----
    python labview/cryocon22c_sim.py                  # listen on 5025
    python labview/cryocon22c_sim.py --port 5030
    python labview/cryocon22c_sim.py --log cmds.txt   # record command order

Every command received is timestamped and written to the command log, which is
what lv_harness.py inspects to assert the sequence was correct.
"""

from __future__ import annotations

import argparse
import socketserver
import sys
import threading
import time
from dataclasses import dataclass, field

# ---------------------------------------------------------------- plant model

T_AMBIENT = 295.0        # K, room temperature the stage decays back to
C_THERMAL = 491.4        # J/K,    fitted from data/
K0 = 0.07010             # W/K,    fitted
K1 = -4.453e-05          # W/K^2,  fitted
RANGE_WATTS = {"HI": 50.0, "MID": 5.0, "LOW": 0.5}
SENSOR_TAU = 25.0        # s, heater-block to sensor lag; gives the plant the
                         # phase shift that makes bad tuning actually overshoot


def heat_loss(temp):
    """Steady-state power needed to hold `temp`, in watts."""
    d = temp - T_AMBIENT
    if d <= 0:
        return 0.0
    return (K0 + K1 * d) * d


# ------------------------------------------------------------ instrument state

@dataclass
class LoopState:
    setpoint: float = 0.0        # target the user asked for
    working_sp: float = 0.0      # where the ramp generator currently is
    pgain: float = 40.0          # percent per kelvin
    igain: float = 900.0         # INTEGRAL TIME IN SECONDS, not a gain
    dgain: float = 0.0
    rate: float = 1.0            # K/min
    maxpwr: float = 70.0         # percent
    range_: str = "HI"
    type_: str = "RAMPP"
    source: str = "CHA"
    output: float = 0.0          # percent of full scale
    integrator: float = 0.0
    ramping: bool = False


@dataclass
class Instrument:
    control: bool = False
    loop: LoopState = field(default_factory=LoopState)
    t_block: float = T_AMBIENT   # heater block, what the PID actually drives
    t_sensor: float = T_AMBIENT  # what INPUT? A reports, lags the block
    t_b: float = 0.0
    lock: threading.Lock = field(default_factory=threading.Lock)

    # ------------------------------------------------------------- simulation
    def step(self, dt):
        lp = self.loop

        if self.control:
            # Ramp generator. RAMPP walks the working setpoint toward the
            # target at RATE K/min. This only happens while control is on,
            # which is the whole reason CONTROL must precede the setpoint.
            if lp.type_ in ("RAMPP", "RAMPT"):
                step_k = lp.rate * dt / 60.0
                gap = lp.setpoint - lp.working_sp
                if abs(gap) <= step_k:
                    lp.working_sp = lp.setpoint
                    lp.ramping = False
                else:
                    lp.working_sp += step_k if gap > 0 else -step_k
                    lp.ramping = True
            else:
                lp.working_sp = lp.setpoint
                lp.ramping = False

            err = lp.working_sp - self.t_sensor

            # P is percent of full scale per kelvin; I is an integral TIME, so
            # the integral term is (P / Ti) * integral(err dt).
            if lp.igain > 0:
                lp.integrator += err * dt
            out = lp.pgain * err
            if lp.igain > 0:
                out += (lp.pgain / lp.igain) * lp.integrator

            # Clamp, and stop winding the integrator up once clamped.
            limit = lp.maxpwr
            if out > limit:
                out = limit
                if lp.igain > 0 and err > 0:
                    lp.integrator -= err * dt
            elif out < 0.0:
                out = 0.0
                if lp.igain > 0 and err < 0:
                    lp.integrator -= err * dt
            lp.output = out
        else:
            lp.output = 0.0
            lp.integrator = 0.0
            lp.ramping = False

        # Plant: heated block loses heat to ambient, sensor follows the block.
        p_in = RANGE_WATTS.get(lp.range_, 50.0) * lp.output / 100.0
        self.t_block += (p_in - heat_loss(self.t_block)) / C_THERMAL * dt
        if self.t_block < T_AMBIENT:
            self.t_block = T_AMBIENT
        self.t_sensor += (self.t_block - self.t_sensor) * (dt / SENSOR_TAU)

    # ------------------------------------------------------------- SCPI layer
    def handle(self, raw):
        """Return a response string, or None for commands that do not reply."""
        cmd = raw.strip()
        if not cmd:
            return None
        up = cmd.upper()
        lp = self.loop

        if up == "*IDN?":
            return "Cryocon,22C,SIMULATOR,1.0"
        if up.startswith("SYSTEM:FWREV"):
            return "1.00S"
        if up == "CONTROL":
            # Arming control does NOT resynchronise the ramp. If a setpoint was
            # written while control was off, working_sp already equals it and
            # the loop now sees the entire error at once.
            self.control = True
            return None
        if up == "STOP":
            self.control = False
            return None
        if up == "CONTROL?":
            return "ON" if self.control else "OFF"

        if up.startswith("INPUT?"):
            ch = up.split("?", 1)[1].strip().strip(";").upper() or "A"
            return "%.4f" % (self.t_sensor if ch.startswith("A") else self.t_b)
        if up.startswith("INPUT ") and ":UNITS" in up:
            return "K" if up.endswith("?") else None

        if up.startswith("LOOP "):
            body = cmd[5:].strip()
            _, _, rest = body.partition(":")
            key, _, val = rest.partition(" ")
            key = key.strip().upper()
            val = val.strip()
            query = key.endswith("?")
            key = key.rstrip("?")

            simple = {
                "PGAIN": "pgain", "IGAIN": "igain", "DGAIN": "dgain",
                "RATE": "rate", "MAXPWR": "maxpwr",
            }
            if key in simple:
                attr = simple[key]
                if query:
                    return "%.6f" % getattr(lp, attr)
                setattr(lp, attr, float(val))
                return None
            if key == "SETPT":
                if query:
                    return "%.4f" % lp.setpoint
                lp.setpoint = float(val)
                if not self.control:
                    # No ramp is armed while control is off -- this is the trap.
                    lp.working_sp = lp.setpoint
                elif lp.type_ not in ("RAMPP", "RAMPT"):
                    lp.working_sp = lp.setpoint
                return None
            if key == "TYPE":
                if query:
                    return lp.type_
                lp.type_ = val.upper()
                if lp.type_ not in ("RAMPP", "RAMPT"):
                    lp.working_sp = lp.setpoint
                return None
            if key == "RANGE":
                if query:
                    return lp.range_
                lp.range_ = val.upper()
                return None
            if key == "SOURCE":
                if query:
                    return lp.source
                lp.source = val.upper()
                return None
            if key in ("OUTP", "HTRR", "HTRREAD"):
                # OUTP? is what the validated Python study logged. HTRR? is what
                # Loop_Output_Power.vi in the M54 driver actually sends. The 22C
                # manual documents HTRREAD? as "percent of full scale" but then
                # contradicts itself on whether power is linear in that percent
                # or its square. Both are answered identically here; confirm on
                # hardware which one the instrument really returns.
                return "%.2f" % lp.output
            if key == "RAMP":
                return "YES" if lp.ramping else "NO"
            if key == "TABLEIX":
                return "2"
            return "" if query else None

        return "" if up.endswith("?") else None


# ------------------------------------------------------------------ networking

class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        inst = self.server.instrument
        buf = b""
        while True:
            try:
                chunk = self.request.recv(4096)
            except OSError:
                return
            if not chunk:
                return
            buf += chunk
            while b"\n" in buf or b"\r" in buf:
                idx = min(i for i in (buf.find(b"\n"), buf.find(b"\r")) if i >= 0)
                line, buf = buf[:idx], buf[idx + 1:].lstrip(b"\r\n")
                text = line.decode("ascii", "ignore").strip()
                if not text:
                    continue
                for part in text.split(";"):
                    part = part.strip()
                    if not part:
                        continue
                    with inst.lock:
                        reply = inst.handle(part)
                    self.server.record(part)
                    if reply is not None:
                        self.request.sendall(reply.encode() + b"\r\n")


class SimServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, addr, instrument, logpath):
        socketserver.ThreadingTCPServer.__init__(self, addr, Handler)
        self.instrument = instrument
        self.logpath = logpath
        self.t0 = time.time()
        self._loglock = threading.Lock()
        if logpath:
            with open(logpath, "w", encoding="utf-8") as fh:
                fh.write("elapsed_s\tcommand\ttemp_K\theater_pct\tcontrol\n")

    def record(self, cmd):
        inst = self.instrument
        line = "%8.2f\t%s\t%.3f\t%.2f\t%s" % (
            time.time() - self.t0, cmd, inst.t_sensor, inst.loop.output,
            "ON" if inst.control else "OFF")
        print(line, flush=True)
        if self.logpath:
            with self._loglock:
                with open(self.logpath, "a", encoding="utf-8") as fh:
                    fh.write(line + "\n")


def run_plant(inst, stop, dt=0.1):
    while not stop.is_set():
        with inst.lock:
            inst.step(dt)
        time.sleep(0.1)


def main():
    ap = argparse.ArgumentParser(description="Cryocon 22C simulator")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=5025)
    ap.add_argument("--log", default=None, help="write the command log here")
    ap.add_argument("--start-temp", type=float, default=T_AMBIENT)
    ap.add_argument("--speed", type=float, default=1.0,
                    help="time acceleration; 10 makes a 30 min ramp take 3 min")
    args = ap.parse_args()

    inst = Instrument(t_block=args.start_temp, t_sensor=args.start_temp)
    stop = threading.Event()
    threading.Thread(target=run_plant, args=(inst, stop, 0.1 * args.speed),
                     daemon=True).start()

    server = SimServer((args.host, args.port), inst, args.log)
    print("Cryocon 22C simulator listening on %s:%d" % (args.host, args.port))
    print("VISA resource: TCPIP0::%s::%d::SOCKET" % (args.host, args.port))
    print("start %.1f K, speed x%g" % (args.start_temp, args.speed))
    print("-" * 72)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopping")
    finally:
        stop.set()
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
