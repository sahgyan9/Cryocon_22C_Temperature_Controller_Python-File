"""
Continuous Cooling Experiment Orchestrator
===========================================
Wayne Kerr 6510B Precision Impedance Analyzer & Cryo-con 22C Temperature Controller.

Core Pipeline:
1. Locks Wayne Kerr 6510B to Fixed 10 kHz (10,000 Hz) in R-X Series mode.
2. Reads current live stage temperature T_start (e.g. ~422 K).
3. Executes safe anti-surge sequence on Cryo-con 22C:
   - Parks working setpoint at T_start in PID mode.
   - Enforces validated PID gains (default P=70.0, I=900.0 s, D=0.0) and Range HI / MaxPwr 100%.
   - Sets cooling ramp rate (0.50 K/min).
   - Engages CONTROL at zero error.
   - Switches to RAMPP mode and arms target setpoint (300.0 K).
   - Verifies hardware setpoint readback.
4. Continuously streams synchronized measurements:
   - Live stage temperature T (K) from Cryo-con 22C (Channel A).
   - Real Resistance R (Ohm) & Reactance X (Ohm) from Wayne Kerr at fixed 10 kHz.
   - Real-time unbuffered disk writing (.flush() + os.fsync()) ensuring zero data loss.
   - Dispatches live telemetry to GUI table and multi-tab plots.
5. Failsafe: Guarantees STOP is sent to disengage heater on exit, abort, or error.

Author: Lab Automation & Antigravity
Date: 2026-09-11
"""

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

# Vacuum permittivity constant
EPSILON_0 = 8.8541878128e-12


class CoolingOrchestrator:
    """
    Manages continuous cooling ramp and fixed-frequency 10 kHz impedance acquisition.
    """

    def __init__(
        self,
        cryocon: Cryocon22C,
        wayne_kerr: WayneKerr6500B,
        target_temp: float = 300.0,
        ramp_rate: float = 0.50,            # 0.5 K/min cooling rate
        fixed_freq_hz: float = 10000.0,     # Fixed 10 kHz
        drive_level_v: float = 0.100,       # 100 mV RMS
        sample_interval_s: float = 1.0,     # Measurement pacing in seconds
        sample_thickness_mm: float = 0.30,  # Sample thickness d in mm
        sample_area_mm2: float = 6.00,      # Sample electrode area A in mm^2
        p_gain: float = 70.0,
        i_gain: float = 900.0,
        d_gain: float = 0.0,
        max_power: float = 100.0,
        heater_range: str = "HI",
        out_dir: str = "Data",
        file_prefix: str = "Cooling_10kHz",
        on_point_acquired: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_status_update: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        self.cryocon = cryocon
        self.wayne_kerr = wayne_kerr
        self.target_temp = float(target_temp)
        self.ramp_rate = float(ramp_rate)
        self.fixed_freq_hz = float(fixed_freq_hz)
        self.drive_level_v = float(drive_level_v)
        self.sample_interval_s = max(0.2, float(sample_interval_s))
        self.sample_d_mm = float(sample_thickness_mm)
        self.sample_a_mm2 = float(sample_area_mm2)
        self.p_gain = float(p_gain)
        self.i_gain = float(i_gain)
        self.d_gain = float(d_gain)
        self.max_power = float(max_power)
        self.heater_range = heater_range
        self.out_dir = out_dir
        self.file_prefix = file_prefix

        # Callbacks
        self.on_point_acquired = on_point_acquired
        self.on_status_update = on_status_update

        # Runtime State
        self.is_running = False
        self.abort_requested = False
        self.current_filepath: Optional[str] = None
        self.current_csvpath: Optional[str] = None
        self.start_temp: float = 422.0
        self.t_start_epoch: float = 0.0
        self.points_count: int = 0
        self.c0: float = self.compute_c0()

    def compute_c0(self) -> float:
        """Compute geometric vacuum capacitance C0 = eps_0 * (A / d)."""
        d_m = max(1e-6, self.sample_d_mm * 1e-3)
        a_m2 = max(1e-8, self.sample_a_mm2 * 1e-6)
        return EPSILON_0 * (a_m2 / d_m)

    def update_sample_geometry(self, thickness_mm: float, area_mm2: float) -> float:
        """Update sample geometry parameters and recompute C0."""
        self.sample_d_mm = max(0.01, thickness_mm)
        self.sample_a_mm2 = max(0.1, area_mm2)
        self.c0 = self.compute_c0()
        return self.c0

    def request_abort(self) -> None:
        """Signal acquisition loop to cleanly terminate and zero heater."""
        self.abort_requested = True
        print("[ORCHESTRATOR] Abort requested. Initiating safe halt...")

    def run(self) -> bool:
        """
        Execute continuous cooling experiment from current temperature down to 300.0 K.
        Returns True on clean completion or False on abort.
        """
        self.is_running = True
        self.abort_requested = False
        self.points_count = 0
        os.makedirs(self.out_dir, exist_ok=True)

        print("=" * 80)
        print(" CONTINUOUS COOLING IMPEDANCE SPECTROSCOPY EXPERIMENT (10 kHz)")
        print("=" * 80)

        # ---------------------------------------------------------------------
        # 1. Hardware Configuration: Wayne Kerr 6510B Fixed 10 kHz
        # ---------------------------------------------------------------------
        print(f"[SETUP] Configuring Wayne Kerr 6510B:")
        print(f"  Fixed Frequency : {self.fixed_freq_hz:,.1f} Hz (10 kHz)")
        print(f"  Function        : Real R & Reactance X (:METER:FUNC:1 R;2 X)")
        print(f"  Drive Level     : {self.drive_level_v * 1000.0:.1f} mV RMS")
        print(f"  Equivalent Cct  : SER (Series)")
        print(f"  Speed           : FAST")

        self.wayne_kerr.set_function("R", "X")
        self.wayne_kerr.set_frequency(self.fixed_freq_hz)
        self.wayne_kerr.set_drive_level(self.drive_level_v, "V")
        self.wayne_kerr.set_equivalent_circuit("SER")
        self.wayne_kerr.set_speed("FAST")

        # ---------------------------------------------------------------------
        # 2. Read Starting Temperature & Prepare Output Files (.dat and .csv)
        # ---------------------------------------------------------------------
        t_live = self.cryocon.read_temperature("A")
        self.start_temp = t_live
        bias_mv = int(round(self.drive_level_v * 1000.0))
        freq_label = "10kHz"
        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{self.file_prefix}_{int(round(self.start_temp))}K_to_{int(round(self.target_temp))}K_{freq_label}_{bias_mv}mV_{timestamp_str}"
        self.current_filepath = os.path.join(self.out_dir, base_filename + ".dat")
        self.current_csvpath = os.path.join(self.out_dir, base_filename + ".csv")

        delta_t = abs(self.start_temp - self.target_temp)
        est_total_min = delta_t / max(0.01, self.ramp_rate)
        est_hours = int(est_total_min // 60)
        est_mins = int(est_total_min % 60)

        print(f"[START] Current Stage Temp: {self.start_temp:.3f} K")
        print(f"[START] Target Temp       : {self.target_temp:.2f} K")
        print(f"[START] Cooling Rate      : {self.ramp_rate:.2f} K/min")
        print(f"[START] Est. Duration     : {est_hours}h {est_mins}m ({est_total_min:.1f} min)")
        print(f"[START] Auto-Saving DAT   : {os.path.abspath(self.current_filepath)}")
        print(f"[START] Auto-Saving CSV   : {os.path.abspath(self.current_csvpath)}")
        print("=" * 80)

        # ---------------------------------------------------------------------
        # 3. Arm Safe Anti-Surge Cooling Ramp on Cryo-con 22C
        # ---------------------------------------------------------------------
        print("[RAMP] Arming safe cooling ramp sequence...")
        if self.on_status_update:
            self.on_status_update({
                "phase": "ARMING",
                "current_temp_k": t_live,
                "target_temp_k": self.target_temp,
                "start_temp_k": self.start_temp,
                "ramp_rate": self.ramp_rate,
                "heater_pct": 0.0,
                "elapsed_s": 0.0,
                "points_count": 0,
                "filepath": self.current_filepath
            })

        self.cryocon.arm_safe_ramp(
            target_temp=self.target_temp,
            rate=self.ramp_rate,
            p=self.p_gain,
            i=self.i_gain,
            d=self.d_gain,
            range_val=self.heater_range,
            maxpwr=self.max_power
        )

        self.t_start_epoch = time.time()
        omega = 2.0 * math.pi * self.fixed_freq_hz

        # ---------------------------------------------------------------------
        # 4. Continuous Acquisition Loop with Zero-Corruption Unbuffered Writes
        # ---------------------------------------------------------------------
        try:
            with open(self.current_filepath, "w", encoding="utf-8") as f_out, \
                 open(self.current_csvpath, "w", encoding="utf-8") as f_csv:
                # Write standard laboratory header for .dat
                header_line = (
                    "Time (s)\tLight (A)\tT (K)\tf (Hz)\tR (Ohm)\tX (Ohm)\t"
                    "Cp (F)\tTanD\tEps_Prime\tHeater (%)\tSetpoint (K)\n"
                )
                f_out.write(header_line)
                f_out.flush()

                # Write CSV header with requested table schema
                header_csv = (
                    "T (K),f (Fixed),R (ohm),X (ohm),Time (s),Cp (pF),Tan_Delta,Eps_Prime,Heater (%),Setpoint (K)\n"
                )
                f_csv.write(header_csv)
                f_csv.flush()
                try:
                    os.fsync(f_out.fileno())
                    os.fsync(f_csv.fileno())
                except Exception:
                    pass

                print(f"[STREAM] Recording started. Continuous 10 kHz R-X data streaming to DAT & CSV...")

                while not self.abort_requested:
                    loop_start = time.time()
                    elapsed_s = loop_start - self.t_start_epoch

                    # Sync mock temperature if in simulation
                    if hasattr(self.wayne_kerr, "sim_sample_temp") and hasattr(self.cryocon, "_temp_a"):
                        self.wayne_kerr.sim_sample_temp = self.cryocon._temp_a

                    # 1. Query live temperature from Cryo-con 22C
                    t_curr = self.cryocon.read_temperature("A")
                    sp_curr = self.cryocon.get_setpoint(1)
                    htr_curr = self.cryocon.read_heater_output(1)

                    # 2. Trigger Wayne Kerr 6510B at fixed 10 kHz
                    try:
                        r_val, x_val = self.wayne_kerr.trigger_measurement()
                    except Exception as e:
                        print(f"  [WARN] Measurement query retry: {e}")
                        time.sleep(0.1)
                        try:
                            r_val, x_val = self.wayne_kerr.trigger_measurement()
                        except Exception as e2:
                            print(f"  [ERROR] Second measurement failed: {e2}")
                            time.sleep(0.5)
                            continue

                    # 3. Calculate derived quantities with zero-division safety
                    z_mag = math.sqrt(r_val ** 2 + x_val ** 2)
                    theta_deg = math.degrees(math.atan2(x_val, r_val))

                    denom = (r_val ** 2 + x_val ** 2)
                    if denom > 1e-18 and abs(omega) > 1e-6:
                        cp_val = -x_val / (omega * denom)
                    else:
                        cp_val = 0.0

                    abs_x = abs(x_val)
                    tan_delta = (r_val / abs_x) if abs_x > 1e-12 else 0.0

                    c0_active = self.c0 if self.c0 > 1e-18 else self.compute_c0()
                    eps_prime = (cp_val / c0_active) if c0_active > 1e-18 else 0.0

                    # 4. Stream to disk immediately (Strict Data Integrity)
                    row_str = (
                        f"{elapsed_s:.3f}\t0.000\t{t_curr:.4f}\t{self.fixed_freq_hz:.2f}\t"
                        f"{r_val:.6e}\t{x_val:.6e}\t{cp_val:.6e}\t{tan_delta:.6e}\t"
                        f"{eps_prime:.4f}\t{htr_curr:.2f}\t{sp_curr:.3f}\n"
                    )
                    f_out.write(row_str)
                    f_out.flush()

                    row_csv = (
                        f"{t_curr:.4f},{self.fixed_freq_hz:.2f},{r_val:.6e},{x_val:.6e},"
                        f"{elapsed_s:.3f},{cp_val * 1e12:.3f},{tan_delta:.6e},{eps_prime:.4f},"
                        f"{htr_curr:.2f},{sp_curr:.3f}\n"
                    )
                    f_csv.write(row_csv)
                    f_csv.flush()
                    try:
                        os.fsync(f_out.fileno())
                        os.fsync(f_csv.fileno())
                    except Exception:
                        pass

                    self.points_count += 1

                    # 5. Package dictionary for UI callbacks
                    point_data = {
                        "point_idx": self.points_count,
                        "elapsed_s": elapsed_s,
                        "temp_k": t_curr,
                        "freq_fixed": self.fixed_freq_hz,
                        "r_ohm": r_val,
                        "x_ohm": x_val,
                        "z_mag_ohm": z_mag,
                        "theta_deg": theta_deg,
                        "cp_farad": cp_val,
                        "tan_delta": tan_delta,
                        "eps_prime": eps_prime,
                        "heater_pct": htr_curr,
                        "setpoint_k": sp_curr,
                        "target_k": self.target_temp
                    }

                    if self.on_point_acquired:
                        self.on_point_acquired(point_data)

                    # Compute progress towards 300.0 K
                    total_span = abs(self.start_temp - self.target_temp)
                    progress_deg = max(0.0, self.start_temp - t_curr)
                    progress_pct = min(100.0, max(0.0, (progress_deg / max(0.01, total_span)) * 100.0))
                    rem_deg = max(0.0, t_curr - self.target_temp)
                    rem_sec = (rem_deg / max(0.01, self.ramp_rate)) * 60.0

                    if self.on_status_update:
                        self.on_status_update({
                            "phase": "COOLING",
                            "current_temp_k": t_curr,
                            "target_temp_k": self.target_temp,
                            "start_temp_k": self.start_temp,
                            "setpoint_k": sp_curr,
                            "heater_pct": htr_curr,
                            "elapsed_s": elapsed_s,
                            "remaining_s": rem_sec,
                            "progress_pct": progress_pct,
                            "points_count": self.points_count,
                            "filepath": self.current_filepath,
                            "csvpath": self.current_csvpath
                        })

                    # Console heartbeat every 15 points
                    if self.points_count % 15 == 0 or self.points_count == 1:
                        print(
                            f"  Pt {self.points_count:>5} | T={t_curr:7.3f} K (SP={sp_curr:6.2f} K) | "
                            f"R={r_val:10.2e} Ω | X={x_val:10.2e} Ω | ε'={eps_prime:7.1f} | "
                            f"Htr={htr_curr:5.1f}% | Prog={progress_pct:4.1f}%"
                        )

                    # Target reached check
                    if t_curr <= self.target_temp + 0.05 and sp_curr <= self.target_temp + 0.05:
                        print(f"\n[TARGET REACHED] Temperature has reached {self.target_temp:.2f} K!")
                        break

                    # Precise interval pacing
                    spent = time.time() - loop_start
                    sleep_needed = max(0.05, self.sample_interval_s - spent)
                    time.sleep(sleep_needed)

        except Exception as e:
            print(f"[FATAL] Exception in cooling acquisition loop: {e}")
            raise e

        finally:
            self.is_running = False
            total_duration = time.time() - self.t_start_epoch if self.t_start_epoch > 0 else 0.0
            print("\n" + "=" * 80)
            print(f" EXPERIMENT FINISHED: {self.points_count} points logged across {total_duration / 60.0:.1f} minutes")
            print(f" Data saved to: {os.path.abspath(self.current_filepath)}")
            print(f" CSV saved to : {os.path.abspath(self.current_csvpath)}")
            print(" Disengaging Cryo-con 22C heater (Failsafe STOP)...")
            self.cryocon.stop_control()
            print("=" * 80)

            if self.on_status_update:
                self.on_status_update({
                    "phase": "COMPLETE" if not self.abort_requested else "ABORTED",
                    "current_temp_k": getattr(self.cryocon, "_temp_a", 300.0),
                    "target_temp_k": self.target_temp,
                    "elapsed_s": total_duration,
                    "points_count": self.points_count,
                    "filepath": self.current_filepath,
                    "csvpath": self.current_csvpath
                })

        return not self.abort_requested
