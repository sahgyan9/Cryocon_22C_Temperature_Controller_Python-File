"""
Wayne Kerr 6500B / 6510B Precision Impedance Analyzer - Python Driver & Simulator
==================================================================================
Hardware Interface:
- Default GPIB: GPIB0::6::INSTR
- Secondary LAN: TCPIP0::192.168.10.250::5025::SOCKET
- Line Termination: '\\n' (0x0A) with EOI
- Hardware Frequency Limits: 20 Hz to 10 MHz (6510B model)
- AC Drive Level: 100 mV (0.1 V RMS) default
- Measurement Functions: R (Resistance, Ohm) & X (Reactance, Ohm)

Physics Simulation:
High-fidelity Cole-Cole relaxor model simulating PMN-PT dielectric response
as a function of frequency and temperature.

Author: Lab Automation & Antigravity
Date: 2026-09-08
"""

import math
import random
import re
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import pyvisa
    HAS_PYVISA = True
except ImportError:
    HAS_PYVISA = False

VALID_FUNCTIONS = {"L", "C", "Q", "D", "R", "X", "Z", "Y", "THETA", "B", "G"}
VALID_SPEEDS = {"MAX", "MAXIMUM", "FAST", "MED", "MEDIUM", "SLOW"}
VALID_EQU_CCT = {"SER", "PAR"}

FUNCTION_INDEX_MAP = {
    0: "L", 1: "C", 2: "R", 3: "Z", 4: "Y",
    5: "X", 6: "G", 7: "B", 8: "Q", 9: "D", 10: "THETA"
}


class WayneKerr6500B:
    """
    Thread-safe controller and physics simulator for Wayne Kerr 6510B Impedance Analyzer.
    """

    def __init__(
        self,
        resource_name: str = "GPIB0::6::INSTR",
        timeout: float = 5.0,
        mock: bool = False
    ):
        self.resource_name = resource_name
        self.timeout = timeout
        self.mock = mock
        self.rm: Optional[Any] = None
        self.instrument: Optional[Any] = None
        self.connected = False
        self.lock = threading.Lock()

        # Cached state
        self._term1 = "R"
        self._term2 = "X"
        self._freq_hz = 1000.0
        self._level = 0.100  # 100 mV default
        self._drive_type = "V"
        self._equ_cct = "SER"
        self._speed = "FAST"
        self._range = "AUTO"
        self.options = "0"
        self.has_bias_option = False

        # Mock simulation state for PMN-PT dielectric sample
        self.sim_sample_temp = 298.0

    def connect(self) -> bool:
        """Connect to instrument via VISA or initialize mock mode."""
        with self.lock:
            if self.mock:
                self.connected = True
                self.options = "0"
                print("[OK] Initialized Wayne Kerr 6510B in MOCK SIMULATION mode")
                return True

            if not HAS_PYVISA:
                print("[WARN] PyVISA not installed. Falling back to mock simulation.")
                self.mock = True
                self.connected = True
                return True

            try:
                self.rm = pyvisa.ResourceManager()
                self.instrument = self.rm.open_resource(
                    self.resource_name,
                    timeout=int(self.timeout * 1000)
                )
                self.instrument.read_termination = '\n'
                self.instrument.write_termination = '\n'

                idn = self.instrument.query("*IDN?").strip()
                try:
                    self.options = self.instrument.query("*OPT?").strip()
                    self.has_bias_option = ("/D1" in self.options or "D1" in self.options)
                except Exception:
                    self.options = "0"
                    self.has_bias_option = False

                self.connected = True
                print(f"[OK] Connected to Wayne Kerr on {self.resource_name}: {idn} (Options: {self.options})")
                return True
            except Exception as e:
                print(f"[ERROR] Connection to Wayne Kerr on {self.resource_name} failed: {e}")
                self.connected = False
                return False

    def disconnect(self) -> None:
        """Safely disconnect instrument."""
        with self.lock:
            if self.instrument is not None:
                try:
                    self.instrument.close()
                except Exception:
                    pass
                self.instrument = None
            if self.rm is not None:
                try:
                    self.rm.close()
                except Exception:
                    pass
                self.rm = None
            self.connected = False
            print("[OK] Disconnected from Wayne Kerr 6510B")

    def write(self, command: str) -> None:
        """Send SCPI command."""
        with self.lock:
            if not self.connected:
                raise ConnectionError("Not connected to Wayne Kerr")
            if self.mock:
                return
            self.instrument.write(command)

    def query(self, command: str) -> str:
        """Send SCPI query and return response."""
        with self.lock:
            if not self.connected:
                raise ConnectionError("Not connected to Wayne Kerr")
            if self.mock:
                return self._handle_mock_query(command)
            return self.instrument.query(command).strip()

    # -------------------------------------------------------------------------
    # Instrument Setup Methods
    # -------------------------------------------------------------------------

    def set_function(self, term1: str = "R", term2: str = "X") -> None:
        """Set measurement parameters (default R-X)."""
        def _map_term(t: str) -> Tuple[str, str]:
            clean = t.strip().upper()
            if clean in {"THETA", "θ", "ANGLE", "PHASE"}:
                return "THETA", "ANGLE"
            return clean, clean

        t1, c1 = _map_term(term1)
        t2, c2 = _map_term(term2)
        self.write(f":METER:FUNC:1 {c1};2 {c2}")
        self._term1 = t1
        self._term2 = t2

    def set_frequency(self, freq_hz: float) -> float:
        """
        Set measurement frequency in Hz.
        Clamps to hardware limits: min 20 Hz, max 9,999,999.0 Hz (~10 MHz).
        """
        f_clamped = max(20.0, min(float(freq_hz), 9999999.0))
        self.write(f":METER:FREQ {f_clamped:.2f}")
        self._freq_hz = f_clamped
        return f_clamped

    def set_drive_level(self, level_v: float = 0.100, drive_type: str = "V") -> None:
        """Set AC drive level (default 100 mV = 0.1 V)."""
        dt = drive_type.upper()
        self.write(f":METER:LEVEL {level_v:.4e}{dt}")
        self._level = level_v
        self._drive_type = dt

    def set_equivalent_circuit(self, cct: str = "SER") -> None:
        """Set equivalent circuit model ('SER' or 'PAR')."""
        mode = cct.upper()
        self.write(f":METER:EQU-CCT {mode}")
        self._equ_cct = mode

    def set_speed(self, speed: str = "FAST") -> None:
        """Set measurement speed ('MAX', 'FAST', 'MED', 'SLOW')."""
        spd = speed.upper()
        cmd = "MAXIMUM" if spd.startswith("MAX") else ("MEDIUM" if spd.startswith("MED") else spd)
        self.write(f":METER:SPEED {cmd}")
        self._speed = spd

    def trigger_measurement(self) -> Tuple[float, float]:
        """
        Trigger single measurement and return primary & secondary terms.
        Default R-X mode returns (R in Ohms, X in Ohms).
        """
        resp = self.query(":METER:TRIG")
        parts = resp.replace(";", ",").split(",")
        if len(parts) >= 2:
            try:
                v1 = float(parts[0].strip())
                v2 = float(parts[1].strip())
                return v1, v2
            except ValueError as e:
                raise RuntimeError(f"Parse error for measurement '{resp}': {e}")
        raise RuntimeError(f"Unexpected response: '{resp}'")

    # -------------------------------------------------------------------------
    # Frequency Sweep Generator
    # -------------------------------------------------------------------------

    @staticmethod
    def generate_frequency_array(
        start_f: float = 20.0,
        stop_f: float = 10000000.0,
        num_points: int = 200,
        log_spacing: bool = True
    ) -> List[float]:
        """Generate frequency list clamped to valid Wayne Kerr 6510B bounds."""
        s_f = max(20.0, float(start_f))
        e_f = min(9999999.0, float(stop_f))
        if log_spacing:
            log_start = math.log10(s_f)
            log_stop = math.log10(e_f)
            step = (log_stop - log_start) / max(1, num_points - 1)
            freqs = [10 ** (log_start + i * step) for i in range(num_points)]
        else:
            step = (e_f - s_f) / max(1, num_points - 1)
            freqs = [s_f + i * step for i in range(num_points)]
        # Ensure exact end frequency is clamped
        freqs[-1] = min(freqs[-1], 9999999.0)
        return freqs

    # -------------------------------------------------------------------------
    # Physics Simulation (PMN-PT Dielectric Relaxor Model)
    # -------------------------------------------------------------------------

    def _handle_mock_query(self, cmd: str) -> str:
        c_upper = cmd.strip().upper()
        if c_upper == "*IDN?":
            return "WAYNE KERR, 6510B,0,  4.280"
        if c_upper == "*OPT?":
            return "0"
        if c_upper.startswith(":METER:FREQ?"):
            return f"{self._freq_hz:.4e}"
        if c_upper.startswith(":METER:LEVEL?"):
            return f"{self._level:.6e}"
        if c_upper.startswith(":METER:FUNC:1?"):
            return "2"  # R
        if c_upper.startswith(":METER:FUNC:2?"):
            return "5"  # X
        if c_upper == ":METER:TRIG":
            # High fidelity PMN-PT dielectric model
            # Dielectric permittivity peaks near Curie temperature ~410 - 430 K
            t = getattr(self, "sim_sample_temp", 298.0)
            f = max(20.0, self._freq_hz)
            omega = 2.0 * math.pi * f

            # Relaxor dielectric peak behavior
            t_curie = 415.0  # PMN-PT peak temperature in Kelvin
            t_diff = abs(t - t_curie)
            eps_peak = 18000.0 / (1.0 + (t_diff / 35.0) ** 2)
            c_base = max(200e-12, eps_peak * 8.854e-12 * 1e-4 / 1e-3)  # Sample geometry: ~0.5 nF to 5 nF

            # Relaxor dispersion: capacitance decreases slightly with higher frequency
            c_sample = c_base * (1.0 - 0.04 * math.log10(f / 1e3 + 1.0))

            # Loss tangent tan(delta) has relaxation peak around 100 kHz - 1 MHz
            tan_delta = 0.02 + 0.05 / (1.0 + (math.log10(f / 2e5)) ** 2)
            r_series = 15.0 + (tan_delta / (omega * c_sample)) * 0.05
            x_series = -1.0 / (omega * c_sample) + omega * 1.5e-7  # Including small fixture lead inductance

            # Add subtle realistic instrument noise (0.1%)
            noise_r = 1.0 + random.gauss(0, 0.002)
            noise_x = 1.0 + random.gauss(0, 0.002)
            return f"{r_series * noise_r:.4f}, {x_series * noise_x:.4f}"

        return "0.0, 0.0"
