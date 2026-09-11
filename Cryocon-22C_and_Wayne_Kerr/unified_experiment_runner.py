"""
Unified Experiment Runner & Orchestrator
========================================
Coordinates the Cryocon 22C Temperature Controller and Wayne Kerr 6510B
Impedance Analyzer for automated temperature-dependent dielectric spectroscopy.

Core Pipeline for each target temperature:
1. Safe Anti-Surge Ramp: Parks setpoint at live temperature in PID mode, engages
   CONTROL, waits 3s, then switches to RAMPP mode and arms target setpoint.
2. In-Band Stabilization: Monitors until |T_stage - T_target| <= band (default 0.10 K).
3. 5-Minute Sample Thermal Soak: Holds within band for 300 seconds to allow the
   PMN-0.3PT crystal/ceramic sample to thermally equilibrate with the cryostat cold head.
   (Timer automatically resets if temperature drifts outside the band).
4. Automated 200-Point Frequency Sweep: Sweeps 20 Hz to 10 MHz logarithmically
   at 100 mV AC drive level, saving directly to:
   Data/<Tempr>_<Bais>_<time_stamp>.dat (e.g. 300K_100mV_11-56-28.dat).
5. Safe Emergency Shutdown: Guarantees STOP command is sent on any exit path.

Author: Lab Automation & Antigravity
Date: 2026-09-08
"""

import argparse
import csv
import datetime
import math
import os
import sys
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from cryocon_controller import Cryocon22C
from wayne_kerr_controller import WayneKerr6500B


class ExperimentOrchestrator:
    """
    Manages automated execution, progress callbacks, and fail-safe shutdown.
    """

    def __init__(
        self,
        cryocon: Cryocon22C,
        wayne_kerr: WayneKerr6500B,
        targets: List[float],
        soak_time_min: float = 5.0,
        settle_band_k: float = 0.10,
        ramp_rate: float = 1.0,
        drive_level_v: float = 0.100,  # 100 mV
        num_points: int = 200,
        start_f: float = 20.0,
        stop_f: float = 10000000.0,
        out_dir: str = "Data",
        stall_grace_s: float = 600.0,
        p_gain: float = 70.0,
        i_gain: float = 900.0,
        d_gain: float = 0.0,
        max_power: float = 100.0,
        heater_range: str = "HI",
        on_status_update: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_point_acquired: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_sweep_completed: Optional[Callable[[str, float, List[Dict[str, Any]]], None]] = None,
    ):
        self.cryocon = cryocon
        self.wayne_kerr = wayne_kerr
        self.targets = targets
        self.soak_time_sec = soak_time_min * 60.0
        self.settle_band_k = settle_band_k
        self.ramp_rate = ramp_rate
        self.drive_level_v = drive_level_v
        self.num_points = num_points
        self.start_f = start_f
        self.stop_f = stop_f
        self.out_dir = out_dir
        # Extra margin beyond 2x the theoretical ramp time before a stage is
        # declared stalled. Lowered only by the automated test suite.
        self.stall_grace_s = stall_grace_s
        self.p_gain = p_gain
        self.i_gain = i_gain
        self.d_gain = d_gain
        self.max_power = max_power
        self.heater_range = heater_range

        self.on_status_update = on_status_update
        self.on_point_acquired = on_point_acquired
        self.on_sweep_completed = on_sweep_completed

        self.is_running = False
        self.abort_requested = False
        self.skip_stage_requested = False
        self.current_stage_idx = 0
        self.current_phase = "IDLE"  # IDLE, RAMPING, SOAKING, SWEEPING, COMPLETE, ABORTED
        self.stall_error: Optional[str] = None

    def request_abort(self) -> None:
        """Signal thread to stop and disengage heater immediately."""
        self.abort_requested = True
        print("[ORCHESTRATOR] Abort requested by user.")

    def request_skip_stage(self) -> None:
        """Signal thread to immediately proceed to frequency sweep or next stage."""
        self.skip_stage_requested = True
        print("[ORCHESTRATOR] Skip stage / immediate sweep requested.")

    def run_experiment(self) -> bool:
        """
        Execute the full automated measurement sequence across all target temperatures.
        """
        self.is_running = True
        self.abort_requested = False
        self.skip_stage_requested = False
        self.stall_error = None
        os.makedirs(self.out_dir, exist_ok=True)

        print("=" * 80)
        print(" UNIFIED PMN-PT IMPEDANCE SPECTROSCOPY EXPERIMENT")
        print("=" * 80)
        print(f" Targets         : {', '.join(f'{t:g}K' for t in self.targets)}")
        print(f" Ramp Rate       : {self.ramp_rate:.1f} K/min")
        print(f" PID Tuning      : P={self.p_gain:.1f}, I={self.i_gain:.1f}s, D={self.d_gain:.1f}")
        print(f" Power Authority : Max={self.max_power:.0f}%, Range={self.heater_range}")
        print(f" Settle Band     : +/-{self.settle_band_k:.2f} K")
        print(f" Sample Soak     : {self.soak_time_sec / 60.0:.1f} min ({self.soak_time_sec:.0f} s)")
        print(f" Frequency Span  : {self.start_f:,.0f} Hz -> {self.stop_f:,.0f} Hz ({self.num_points} log points)")
        print(f" AC Drive Level  : {self.drive_level_v * 1e3:.0f} mV (0.1 V)")
        print(f" Output Directory: {os.path.abspath(self.out_dir)}")
        print("=" * 80)

        frequencies = WayneKerr6500B.generate_frequency_array(
            start_f=self.start_f,
            stop_f=self.stop_f,
            num_points=self.num_points,
            log_spacing=True
        )

        try:
            # Configure Wayne Kerr once
            self.wayne_kerr.set_function("R", "X")
            self.wayne_kerr.set_equivalent_circuit("SER")
            self.wayne_kerr.set_speed("FAST")
            self.wayne_kerr.set_drive_level(self.drive_level_v, "V")

            for stage_idx, target_k in enumerate(self.targets):
                self.current_stage_idx = stage_idx
                if self.abort_requested:
                    break

                print(f"\n[STAGE {stage_idx + 1}/{len(self.targets)}] Target Setpoint: {target_k:.2f} K")
                
                # -------------------------------------------------------------
                # 1. Arm Safe Anti-Surge Ramp
                # -------------------------------------------------------------
                self.current_phase = "ARMING"
                if self.on_status_update:
                    t_now = self.cryocon.read_temperature("A")
                    self.on_status_update({
                        "stage_idx": stage_idx,
                        "target_k": target_k,
                        "live_setpt_k": t_now,
                        "current_temp_k": t_now,
                        "error_k": 0.0,
                        "heater_pct": 0.0,
                        "phase": "ARMING",
                        "soak_remaining_sec": self.soak_time_sec,
                        "soak_progress_pct": 0.0
                    })

                self.current_phase = "RAMPING"
                live_temp = self.cryocon.arm_safe_ramp(
                    target_temp=target_k,
                    rate=self.ramp_rate,
                    p=self.p_gain,
                    i=self.i_gain,
                    d=self.d_gain,
                    range_val=self.heater_range,
                    maxpwr=self.max_power
                )

                # -------------------------------------------------------------
                # 2. Ramp & Settle Monitoring with 5-Minute Soak Timer
                # -------------------------------------------------------------
                in_band_start: Optional[float] = None
                soak_completed = False
                stage_t0 = time.time()
                last_reassert_t = 0.0
                rearm_count = 0

                # Bounded-time guarantee: how long this stage may spend trying to
                # reach the band before we assume the hardware ramp is dead.
                # 2x the theoretical ramp time plus a 10-minute grace margin.
                theo_ramp_s = abs(target_k - live_temp) / max(self.ramp_rate, 0.01) * 60.0
                band_deadline_s = theo_ramp_s * 2.0 + self.stall_grace_s

                if not getattr(self.cryocon, "last_arm_verified", True):
                    print(f"  [WARN] Ramp arm to {target_k:.2f} K was NOT confirmed by hardware. "
                          f"Watchdog will re-arm if the stage stalls.")

                while not soak_completed and not self.abort_requested:
                    if self.skip_stage_requested:
                        print("[ORCHESTRATOR] Skipping soak, starting sweep immediately.")
                        self.skip_stage_requested = False
                        break

                    # Update mock simulation temperature if running in mock mode
                    if hasattr(self.wayne_kerr, "sim_sample_temp"):
                        self.wayne_kerr.sim_sample_temp = self.cryocon._temp_a

                    curr_temp = self.cryocon.read_temperature("A")
                    heater_pct = self.cryocon.read_heater_output(1)
                    live_sp = self.cryocon.get_setpoint(1)
                    err = curr_temp - target_k

                    # ---------------------------------------------------------
                    # Self-Healing Setpoint Watchdog (Level 1)
                    # If the hardware setpoint does not match the target while
                    # ramping, re-assert it. Gated on wall-clock elapsed time, NOT
                    # on int(elapsed) % 15: the poll period is ~1.3-1.5 s (1 s sleep
                    # plus three serial round trips), so integer seconds are skipped
                    # and a modulo gate can miss every multiple for minutes at a time.
                    # ---------------------------------------------------------
                    stage_elapsed = time.time() - stage_t0
                    now_t = time.time()
                    if abs(live_sp - target_k) > 0.2 and abs(err) > self.settle_band_k:
                        if stage_elapsed > 10.0 and (now_t - last_reassert_t) >= 15.0:
                            last_reassert_t = now_t
                            print(f"  [WATCHDOG] Hardware setpoint mismatch detected (SP={live_sp:.2f} K != Target={target_k:.2f} K). Re-asserting target...")
                            self.cryocon.write("LOOP 1:TYPE RAMPP", wait_time=0.3)
                            self.cryocon.write(f"LOOP 1:SETPT {target_k:.3f}", wait_time=0.4)

                    # ---------------------------------------------------------
                    # Stage Stall Watchdog (Level 2) - bounded-time guarantee
                    # Level 1 only fires when SETPT? disagrees with the target. If the
                    # setpoint reads correctly but the temperature never moves (dead
                    # ramp engine, heater range dropped, control silently off), nothing
                    # above catches it. Without this the stage waits forever with the
                    # heater energised - the exact failure that lost the 2026-09-08
                    # overnight run at 330 K.
                    # ---------------------------------------------------------
                    if in_band_start is None and stage_elapsed > band_deadline_s:
                        if rearm_count < 2:
                            rearm_count += 1
                            print(f"  [STALL] Stage {stage_idx + 1} has not reached {target_k:.2f} K "
                                  f"after {stage_elapsed / 60.0:.1f} min (T={curr_temp:.3f} K, "
                                  f"SP={live_sp:.2f} K, heater={heater_pct:.1f}%). "
                                  f"Performing full ramp re-arm {rearm_count}/2...")
                            live_temp = self.cryocon.arm_safe_ramp(
                                target_temp=target_k,
                                rate=self.ramp_rate,
                                p=self.p_gain,
                                i=self.i_gain,
                                d=self.d_gain,
                                range_val=self.heater_range,
                                maxpwr=self.max_power
                            )
                            stage_t0 = time.time()
                            last_reassert_t = 0.0
                            theo_ramp_s = abs(target_k - live_temp) / max(self.ramp_rate, 0.01) * 60.0
                            band_deadline_s = theo_ramp_s * 2.0 + self.stall_grace_s
                            continue
                        else:
                            print(f"[FATAL] Stage {stage_idx + 1} stalled at {curr_temp:.3f} K and could not be "
                                  f"recovered after 2 re-arm attempts. Aborting run and disengaging heater "
                                  f"so the cryostat is left in a safe state.")
                            self.stall_error = (
                                f"Stage {stage_idx + 1} ({target_k:.2f} K) stalled: temperature held at "
                                f"{curr_temp:.3f} K with setpoint {live_sp:.2f} K. Run aborted safely."
                            )
                            self.abort_requested = True
                            break

                    # Settle & Soak Detection
                    if abs(err) <= self.settle_band_k:
                        if in_band_start is None:
                            in_band_start = time.time()
                            print(f"  >>> Entered +/-{self.settle_band_k:.2f} K band at {curr_temp:.3f} K. Starting 5-minute soak timer...")
                        
                        soak_elapsed = time.time() - in_band_start
                        remaining_soak = max(0.0, self.soak_time_sec - soak_elapsed)
                        self.current_phase = "SOAKING"

                        if soak_elapsed >= self.soak_time_sec:
                            soak_completed = True
                            print(f"[STAGE {stage_idx + 1}] Sample thermal soak COMPLETE at {curr_temp:.3f} K! (5.0 min held).")
                    else:
                        if in_band_start is not None:
                            print(f"  >>> Exited +/-{self.settle_band_k:.2f} K band ({curr_temp:.3f} K, err={err:+.3f} K). Resetting soak timer.")
                        in_band_start = None
                        self.current_phase = "RAMPING"
                        remaining_soak = self.soak_time_sec

                    # Dispatch status update
                    status_dict = {
                        "stage_idx": stage_idx,
                        "target_k": target_k,
                        "live_setpt_k": live_sp if (live_sp == live_sp and live_sp > 0) else target_k,
                        "current_temp_k": curr_temp,
                        "error_k": err,
                        "heater_pct": heater_pct,
                        "phase": self.current_phase,
                        "soak_remaining_sec": remaining_soak if in_band_start else self.soak_time_sec,
                        "soak_progress_pct": (1.0 - (remaining_soak / self.soak_time_sec)) * 100.0 if in_band_start else 0.0
                    }
                    if self.on_status_update:
                        self.on_status_update(status_dict)

                    time.sleep(1.0)

                if self.abort_requested:
                    break

                # -------------------------------------------------------------
                # 3. Frequency Sweep Acquisition
                # -------------------------------------------------------------
                self.current_phase = "SWEEPING"
                timestamp_str = datetime.datetime.now().strftime("%H-%M-%S")
                # Format: <Tempr>_<Bais>_<time_stamp>.dat e.g. 300K_100mV_11-56-28.dat
                bias_mv = int(round(self.drive_level_v * 1000.0))
                temp_label = f"{int(round(target_k))}K" if abs(target_k - round(target_k)) < 0.01 else f"{target_k:.1f}K"
                filename = f"{temp_label}_{bias_mv}mV_{timestamp_str}.dat"
                filepath = os.path.join(self.out_dir, filename)

                print(f"\n[SWEEP] Running {self.num_points}-point RX sweep at {target_k:.2f} K -> {filepath}")

                sweep_data_points: List[Dict[str, Any]] = []
                t_sweep_start = time.time()

                with open(filepath, "w", encoding="utf-8") as f_out:
                    # Write standard laboratory header: Time (s)\tLight (A)\tT (K)\tf (Hz)\tR (Ohm)\tX (Ohm)
                    f_out.write("Time (s)\tLight (A)\tT (K)\tf (Hz)\tR (Ohm)\tX (Ohm)\n")
                    f_out.flush()

                    for pt_idx, freq in enumerate(frequencies):
                        if self.abort_requested:
                            print("[SWEEP] Abort requested during sweep.")
                            break

                        # Set frequency and trigger
                        self.wayne_kerr.set_frequency(freq)
                        time.sleep(0.02)  # brief hardware settling delay
                        r_val, x_val = self.wayne_kerr.trigger_measurement()
                        t_live = self.cryocon.read_temperature("A")
                        elapsed_s = time.time() - t_sweep_start

                        # Derive parameters
                        z_mag = math.sqrt(r_val ** 2 + x_val ** 2)
                        theta_deg = math.degrees(math.atan2(x_val, r_val))

                        # Write tab-delimited record: Time (s)\tLight (A)\tT (K)\tf (Hz)\tR (Ohm)\tX (Ohm)
                        row_line = f"{elapsed_s:.3f}\t0.000\t{t_live:.3f}\t{freq:.3f}\t{r_val:.3f}\t{x_val:.3f}\n"
                        f_out.write(row_line)
                        f_out.flush()

                        pt_dict = {
                            "point_idx": pt_idx + 1,
                            "total_points": self.num_points,
                            "elapsed_s": elapsed_s,
                            "temp_k": t_live,
                            "freq_hz": freq,
                            "r_ohm": r_val,
                            "x_ohm": x_val,
                            "z_mag_ohm": z_mag,
                            "theta_deg": theta_deg,
                            "target_k": target_k
                        }
                        sweep_data_points.append(pt_dict)

                        if self.on_point_acquired:
                            self.on_point_acquired(pt_dict)

                        if (pt_idx + 1) % 25 == 0 or pt_idx == self.num_points - 1:
                            print(f"  Point {pt_idx+1:>3}/{self.num_points}: f={freq:10.1f} Hz | R={r_val:11.2e} Ohm | X={x_val:11.2e} Ohm | T={t_live:.3f} K")

                sweep_duration = time.time() - t_sweep_start
                print(f"[SAVED] Stage {stage_idx + 1} sweep completed in {sweep_duration:.1f} s -> {filepath}\n")

                if self.on_sweep_completed:
                    self.on_sweep_completed(filepath, target_k, sweep_data_points)

            self.current_phase = "COMPLETE" if not self.abort_requested else "ABORTED"

        except Exception as e:
            print(f"[FATAL] Exception in experiment loop: {e}")
            self.current_phase = "ERROR"
            raise e

        finally:
            self.is_running = False
            # Failsafe: ALWAYS stop Cryocon heating upon exit
            print("\n[SAFETY] Disengaging Cryo-con 22C heater (STOP)...")
            self.cryocon.stop_control()
            print("[SAFETY] Failsafe shutdown complete. System safe and idle.\n")

        return not self.abort_requested


# -----------------------------------------------------------------------------
# Standalone CLI Entrypoint
# -----------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(description="Automated PMN-PT Temperature & Impedance Sweep")
    parser.add_argument("--targets", type=str, default="299,300",
                        help="Comma-separated target temperatures in K (default: '299,300')")
    parser.add_argument("--start", type=float, default=300.0, help="Start temp in K if range mode")
    parser.add_argument("--stop", type=float, default=470.0, help="Stop temp in K if range mode")
    parser.add_argument("--step", type=float, default=5.0, help="Step temp in K if range mode")
    parser.add_argument("--use-range", action="store_true", help="Use start/stop/step instead of --targets")
    parser.add_argument("--soak-min", type=float, default=5.0, help="PMN-PT soak delay in minutes (default 5.0)")
    parser.add_argument("--band", type=float, default=0.10, help="Settle tolerance band in K (default 0.10)")
    parser.add_argument("--rate", type=float, default=1.0, help="Ramp rate in K/min (default 1.0)")
    parser.add_argument("--level", type=float, default=0.100, help="AC drive level in V (default 0.100 V = 100 mV)")
    parser.add_argument("--points", type=int, default=200, help="Number of frequency sweep points (default 200)")
    parser.add_argument("--start-f", type=float, default=20.0, help="Start frequency in Hz (min 20 Hz)")
    parser.add_argument("--stop-f", type=float, default=10000000.0, help="Stop frequency in Hz (max 10 MHz)")
    parser.add_argument("--port", type=str, default="COM5", help="Cryocon serial port (default: COM5)")
    parser.add_argument("--baud", type=int, default=57600, help="Cryocon baud rate (default: 57600)")
    parser.add_argument("--visa", type=str, default="GPIB0::6::INSTR", help="Wayne Kerr VISA resource")
    parser.add_argument("--mock", action="store_true", help="Run in mock simulation mode without instruments")
    parser.add_argument("--out-dir", type=str, default="Data", help="Output directory for .dat files")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.use_range:
        t = args.start
        targets = []
        while t <= args.stop + 1e-5:
            targets.append(round(t, 2))
            t += args.step
    else:
        targets = [float(x.strip()) for x in args.targets.split(",") if x.strip()]

    print(f"Connecting instruments (Mock Mode: {args.mock})...")
    cryo = Cryocon22C(port=args.port, baud_rate=args.baud, mock=args.mock)
    if not cryo.connect():
        print(f"[FATAL] Failed to connect to Cryocon on {args.port}. Aborting.")
        sys.exit(1)

    wk = WayneKerr6500B(resource_name=args.visa, mock=args.mock)
    if not wk.connect():
        print(f"[FATAL] Failed to connect to Wayne Kerr on {args.visa}. Aborting.")
        cryo.disconnect()
        sys.exit(1)

    orchestrator = ExperimentOrchestrator(
        cryocon=cryo,
        wayne_kerr=wk,
        targets=targets,
        soak_time_min=args.soak_min,
        settle_band_k=args.band,
        ramp_rate=args.rate,
        drive_level_v=args.level,
        num_points=args.points,
        start_f=args.start_f,
        stop_f=args.stop_f,
        out_dir=args.out_dir
    )

    try:
        success = orchestrator.run_experiment()
        print(f"Experiment finished with status: {'SUCCESS' if success else 'ABORTED'}")
    except KeyboardInterrupt:
        print("\n[USER INTERRUPT] Aborting experiment...")
        orchestrator.request_abort()
    finally:
        cryo.disconnect()
        wk.disconnect()


if __name__ == "__main__":
    main()
