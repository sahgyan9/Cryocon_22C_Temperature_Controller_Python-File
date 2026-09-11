"""
Cryocon 22C Temperature Controller - Robust Python Driver & Simulator
=====================================================================
Target System: Janis Research ST-LN-500 Cryogenic Probe Station
Controller: Cryo-con Model 22C (Firmware 3.33G, Serial 206687)

Validated Operating Parameters (2026-09-05 Study):
- Proportional Gain (P):  40.0 (or 25.0)
- Integral Time (I):      900.0 s (15 minutes) - NOTE: seconds, not gain!
- Derivative Gain (D):    0.0
- Heater Range:           HI (50 W full scale authority at 50 Ohm)
- Maximum Power Cap:      100.0 % (50 W ceiling) - was 70% (35 W); see DEFAULT_MAXPWR note
- Ramp Rate:              2.0 K/min (or 1.0 K/min)
- Loop Mode:              RAMPP (PID control with ramp)

Safety Rule: Anti-Surge Command Ordering
Always parks setpoint at current temperature in PID mode and engages CONTROL
before arming target setpoint in RAMPP mode to prevent full-power heater surges.

Author: Lab Automation & Antigravity
Date: 2026-09-08
"""

import math
import re
import threading
import time
from datetime import datetime
from typing import Dict, Optional, Tuple, Union

try:
    import serial
    import serial.tools.list_ports
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False

# Validated Baseline Tuning Parameters
DEFAULT_PGAIN = 70.0
DEFAULT_IGAIN = 900.0   # Seconds (Integral reset time, NOT a gain)
DEFAULT_DGAIN = 0.0
DEFAULT_RANGE = "HI"    # 50 W full-scale authority
DEFAULT_MAXPWR = 100.0  # % power ceiling (50 W at RANGE HI)
# Raised from 70.0 on 2026-09-09. Station heater demand calibrated from three
# live operating points is hold% = 0.4865 %/K x (T - 300.0 K), plus ~14% for a
# 1 K/min ramp. At the old 70% cap the ramp goes power-limited at ~415 K and the
# loop cannot hold above ~444 K, so the 300-470 K run could never have completed.
# 470 K needs ~83% to hold and ~97% to hold-and-ramp: 100% is required, not optional.
DEFAULT_RATE = 1.0      # K/min


class Cryocon22C:
    """
    Thread-safe interface and simulation model for Cryo-con 22C Temperature Controller.
    """

    def __init__(
        self,
        port: str = "COM5",
        baud_rate: int = 57600,
        timeout: float = 2.0,
        mock: bool = False
    ):
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.mock = mock
        self.serial: Optional[Any] = None
        self.connected = False
        self.lock = threading.Lock()

        # Cached instrument state & mock model
        self._temp_a = 297.315
        self._temp_b = float("nan")
        self._setpoint = 297.315
        self._ramp_target = 297.315
        self._control_on = False
        self._loop_type = "RAMPP"
        self._heater_pwr = 0.0
        self._range = DEFAULT_RANGE
        self._maxpwr = DEFAULT_MAXPWR
        self._pgain = DEFAULT_PGAIN
        self._igain = DEFAULT_IGAIN
        self._dgain = DEFAULT_DGAIN
        self._rate = DEFAULT_RATE
        self.is_arming = False
        self.last_arm_verified = False
        self._last_sim_time = time.time()

    def connect(self) -> bool:
        """Establish serial connection or start mock simulation."""
        with self.lock:
            if self.mock:
                self.connected = True
                print(f"[OK] Cryocon 22C initialized in MOCK SIMULATION mode (Ambient: {self._temp_a:.3f} K)")
                return True

            if not HAS_SERIAL:
                print("[WARN] pyserial not installed. Falling back to mock simulation.")
                self.mock = True
                self.connected = True
                return True

            try:
                self.serial = serial.Serial(
                    port=self.port,
                    baudrate=self.baud_rate,
                    timeout=self.timeout,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE
                )
                time.sleep(0.3)
                self.connected = True
                print(f"[OK] Connected to Cryocon 22C on {self.port} @ {self.baud_rate} baud")
                return True
            except Exception as e:
                print(f"[ERROR] Connection to Cryocon 22C on {self.port} failed: {e}")
                self.connected = False
                return False

    def disconnect(self) -> None:
        """Safely close serial port."""
        with self.lock:
            if self.serial and hasattr(self.serial, "is_open") and self.serial.is_open:
                try:
                    self.serial.close()
                except Exception:
                    pass
            self.connected = False
            print("[OK] Disconnected from Cryocon 22C")

    def _send_raw(self, cmd: str, wait_time: float = 0.02) -> str:
        """Low-level command sender with CRLF termination."""
        if not self.connected:
            raise ConnectionError("Not connected to Cryocon 22C")

        if self.mock:
            return self._handle_mock_command(cmd)

        if not self.serial:
            raise ConnectionError("Serial port is None")

        self.serial.reset_input_buffer()
        self.serial.write(f"{cmd}\r\n".encode("utf-8"))
        try:
            self.serial.flush()
        except Exception:
            pass
        if wait_time > 0:
            time.sleep(wait_time)

        resp = self.serial.readline().decode("utf-8", errors="ignore").strip()
        return resp

    def query(self, cmd: str, wait_time: float = 0.02) -> str:
        """Send SCPI query and return response."""
        with self.lock:
            return self._send_raw(cmd, wait_time)

    def write(self, cmd: str, wait_time: float = 0.02) -> None:
        """Send SCPI command without expecting response."""
        with self.lock:
            if self.mock:
                self._handle_mock_command(cmd)
                return
            if self.serial:
                self.serial.write(f"{cmd}\r\n".encode("utf-8"))
                try:
                    self.serial.flush()
                except Exception:
                    pass
                if wait_time > 0:
                    time.sleep(wait_time)

    # -------------------------------------------------------------------------
    # High-Level Controls
    # -------------------------------------------------------------------------

    def read_temperature(self, channel: str = "A") -> float:
        """Read temperature from specified channel in Kelvin."""
        ch = channel.upper()
        res = self.query(f"INPUT? {ch}")
        try:
            val = float(res)
            if ch == "A":
                self._temp_a = val
            return val
        except ValueError:
            return self._temp_a if ch == "A" else float("nan")

    def read_heater_output(self, loop: int = 1) -> float:
        """Get current heater output power percentage (0 - 100%)."""
        res = self.query(f"LOOP {loop}:OUTP?")
        clean = res.replace("%", "").strip()
        try:
            val = float(clean)
            # Physical sanity check: Cryo-con 22C output percentage must be in [0.0, 100.0]
            # Protects against corrupt serial frames or misaligned responses (e.g. 298.66 K from INPUT? A)
            if 0.0 <= val <= 100.0:
                self._heater_pwr = val
                return val
            return self._heater_pwr
        except ValueError:
            return self._heater_pwr

    def get_setpoint(self, loop: int = 1) -> float:
        """Get active setpoint."""
        res = self.query(f"LOOP {loop}:SETPT?")
        clean = res.rstrip("KkCcFf ").strip()
        try:
            val = float(clean)
            self._setpoint = val
            return val
        except ValueError:
            return self._setpoint

    def get_max_power(self, loop: int = 1) -> float:
        """
        Read back the loop's maximum power ceiling in percent.

        Returns NaN if the instrument does not answer or the reply cannot be parsed.
        It deliberately does NOT fall back to the cached value: this reader exists to
        VERIFY a write, and a verifier that quietly returns the value you hoped for
        can never fail. (That defect shipped on 2026-09-09 and hid a rejected
        MAXPWR write for a full run.)
        """
        res = self.query(f"LOOP {loop}:MAXPWR?")
        clean = res.replace("%", "").strip()
        try:
            val = float(clean)
        except ValueError:
            return float("nan")
        if not (0.0 <= val <= 100.0):
            return float("nan")
        self._maxpwr = val
        return val

    def set_max_power_verified(self, value: float, loop: int = 1) -> float:
        """
        Write the power ceiling and confirm the instrument actually took it.

        Tries several command spellings because the 22C rejects some forms outright
        rather than clamping. Returns the ceiling the hardware reports, or NaN if the
        instrument will not report one at all (in which case the caller is told the
        cap is UNVERIFIED rather than being lied to).
        """
        candidates = [f"{value:.1f}", f"{int(round(value))}", "99.9", "99"]
        last = float("nan")
        for cand in candidates:
            self.write(f"LOOP {loop}:MAXPWR {cand}", wait_time=0.3)
            time.sleep(0.2)
            actual = self.get_max_power(loop)
            last = actual
            if actual != actual:                      # NaN -> no usable readback
                print(f"[WARN] Cryocon did not report MAXPWR back after writing '{cand}'.")
                continue
            if abs(actual - float(cand)) <= 0.15:
                if abs(actual - value) > 0.15:
                    print(f"[WARN] Cryocon refused MAXPWR {value:.1f}%; accepted {actual:.1f}%.")
                else:
                    print(f"[OK] Heater power ceiling confirmed at {actual:.1f}%.")
                return actual
            print(f"[WARN] MAXPWR readback mismatch (wrote '{cand}', reads {actual:.1f}%).")

        if last != last:
            print(f"[ERROR] MAXPWR is UNVERIFIED - the 22C will not report it over SCPI. "
                  f"Check the front panel: the ceiling may still be at its old value.")
        else:
            print(f"[ERROR] Could not set MAXPWR. Heater ceiling is {last:.1f}%, NOT {value:.1f}%. "
                  f"Stages above ~415 K will run out of heater authority and stall.")
        return last

    def get_control_status(self) -> bool:
        """Query if temperature control is actively engaged."""
        res = self.query("CONTROL?")
        is_on = res.upper().startswith("ON") or res == "1"
        self._control_on = is_on
        return is_on

    def start_control(self) -> None:
        """Engage control loop."""
        self.write("CONTROL")
        self._control_on = True

    def stop_control(self) -> bool:
        """
        Emergency disengage of control loop (cuts heater power to 0%).
        Retries up to 3 times to guarantee CONTROL is OFF.
        """
        for _ in range(3):
            try:
                self.write("STOP", wait_time=0.3)
                time.sleep(0.2)
                stat = self.query("CONTROL?", wait_time=0.2).upper()
                if stat.startswith("OFF") or stat == "0":
                    self._control_on = False
                    self._heater_pwr = 0.0
                    print("[STOP] Cryocon 22C Control Confirmed OFF")
                    return True
            except Exception as e:
                print(f"[WARN] Error during STOP command: {e}")
            time.sleep(0.2)
        return False

    def arm_safe_ramp(
        self,
        target_temp: float,
        rate: float = DEFAULT_RATE,
        p: float = DEFAULT_PGAIN,
        i: float = DEFAULT_IGAIN,
        d: float = DEFAULT_DGAIN,
        range_val: str = DEFAULT_RANGE,
        maxpwr: float = DEFAULT_MAXPWR
    ) -> float:
        """
        Configures and arms a safe temperature ramp to target_temp.
        
        Strict Anti-Surge Sequence (enforced from cryocon_gui.py and staged_ramp_test.py):
        1. Read current live temperature T_live.
        2. Set LOOP 1:TYPE PID (drop to PID mode so setpoint moves instantly without ramping).
        3. Set LOOP 1:SETPT T_live (park working setpoint at current reading, error = 0.0 K).
        4. Configure validated tuning: RANGE, MAXPWR, PGAIN, IGAIN, DGAIN, RATE with inter-command spacing.
        5. Send CONTROL (engage loop at zero error -> heater begins smoothly at hold power).
        6. Wait 2.5s for loop to balance at hold power.
        7. Send LOOP 1:TYPE RAMPP with 0.3s settling delay.
        8. Send LOOP 1:SETPT target (arms the ramp smoothly).
        """
        self.is_arming = True
        self.last_arm_verified = False
        try:
            live_temp = self.read_temperature("A")
            print(f"[RAMP] Initiating safe ramp: Current={live_temp:.3f} K -> Target={target_temp:.2f} K @ {rate:.1f} K/min")

            # Step 1: Resync working setpoint to current temp in PID mode
            self.write("LOOP 1:TYPE PID", wait_time=0.3)
            time.sleep(0.3)
            self.write(f"LOOP 1:SETPT {live_temp:.3f}", wait_time=0.5)
            time.sleep(0.5)

            # Step 2: Configure loop gains and limits
            self.write(f"LOOP 1:RANGE {range_val}", wait_time=0.8)
            time.sleep(0.5)  # Mechanical relay switch
            self.set_max_power_verified(maxpwr)
            self.write(f"LOOP 1:PGAIN {p:.1f}", wait_time=0.2)
            self.write(f"LOOP 1:IGAIN {i:.1f}", wait_time=0.2)
            self.write(f"LOOP 1:DGAIN {d:.1f}", wait_time=0.2)
            self.write(f"LOOP 1:RATE {rate:.2f}", wait_time=0.2)

            # Step 3: Engage control while setpoint is parked at live reading
            self.write("CONTROL", wait_time=0.3)
            time.sleep(2.5)  # Allow loop to balance at hold power

            # Step 4: Arm the ramp (CRITICAL: 0.4s delay gives 22C microcontroller time to transition to RAMPP before target setpoint is written)
            self.write("LOOP 1:TYPE RAMPP", wait_time=0.4)
            time.sleep(0.4)
            self.write(f"LOOP 1:SETPT {target_temp:.3f}", wait_time=0.4)

            # Step 5: Readback Verification & Retry (guarantees hardware accepted target setpoint)
            verified = False
            for attempt in range(1, 4):
                time.sleep(0.3)
                sp_read = self.get_setpoint(1)
                if abs(sp_read - target_temp) <= 0.15:
                    print(f"[RAMP] Setpoint verified on hardware: {sp_read:.3f} K")
                    verified = True
                    break
                print(f"[WARN] Setpoint verification mismatch (target {target_temp:.2f} K, read {sp_read:.2f} K). Resending (attempt {attempt}/3)...")
                self.write("LOOP 1:TYPE RAMPP", wait_time=0.3)
                time.sleep(0.3)
                self.write(f"LOOP 1:SETPT {target_temp:.3f}", wait_time=0.5)

            if not verified:
                print(f"[WARN] Cryocon setpoint verification could not confirm {target_temp:.2f} K (last read: {sp_read:.2f} K).")

            # Expose the outcome so the orchestrator can react instead of waiting blindly.
            self.last_arm_verified = verified

            self._ramp_target = target_temp
            self._setpoint = target_temp
            self._control_on = True
            return live_temp
        finally:
            self.is_arming = False

    # -------------------------------------------------------------------------
    # Physics Mock Simulation Engine
    # -------------------------------------------------------------------------

    def _handle_mock_command(self, cmd: str) -> str:
        """Simulate Cryocon 22C responses and realistic thermal physics."""
        now = time.time()
        dt = max(0.001, now - self._last_sim_time)
        self._last_sim_time = now

        # Update simulated thermal model: C * dT/dt = P_heater - P_loss
        # C ≈ 520 J/K, P_loss ≈ 0.0754 * (T - 297.3) W
        if self._control_on:
            err = self._ramp_target - self._temp_a
            # Simulate ramp progress
            max_d_temp = (self._rate / 60.0) * dt
            if abs(err) > max_d_temp:
                self._temp_a += math.copysign(max_d_temp, err)
            else:
                self._temp_a = self._ramp_target

            # Simulated heater percentage needed to maintain/climb
            p_loss = max(0.0, 0.0754 * (self._temp_a - 297.3))
            p_ramp = 520.0 * (self._rate / 60.0) if self._temp_a < self._ramp_target else 0.0
            p_total_w = min(35.0, p_loss + p_ramp)
            self._heater_pwr = min(self._maxpwr, (p_total_w / 50.0) * 100.0)
        else:
            # Passive cool down towards 297.3 K
            if self._temp_a > 297.315:
                self._temp_a = max(297.315, self._temp_a - 0.005 * dt)
            self._heater_pwr = 0.0

        c_upper = cmd.strip().upper()
        if c_upper == "*IDN?":
            return "Cryo-con,22C,206687,3.33G"
        if c_upper.startswith("INPUT? A"):
            return f"{self._temp_a:.4f}"
        if c_upper.startswith("INPUT? B"):
            return "......."  # Channel B disconnected fault
        if c_upper.startswith("LOOP 1:OUTP?"):
            return f"{self._heater_pwr:.2f}%"
        if c_upper.startswith("LOOP 1:SETPT?"):
            return f"{self._setpoint:.3f}K"
        if c_upper.startswith("CONTROL?"):
            return "ON" if self._control_on else "OFF"
        if c_upper == "CONTROL":
            self._control_on = True
            return ""
        if c_upper == "STOP":
            self._control_on = False
            self._heater_pwr = 0.0
            return ""
        if c_upper.startswith("LOOP 1:SETPT"):
            parts = cmd.split()
            if len(parts) >= 3:
                try:
                    self._ramp_target = float(parts[2].rstrip("KkCcFf"))
                    self._setpoint = self._ramp_target
                except ValueError:
                    pass
            return ""
        if c_upper.startswith("LOOP 1:MAXPWR?"):
            return f"{self._maxpwr:.1f}"
        if c_upper.startswith("LOOP 1:MAXPWR"):
            parts = cmd.split()
            if len(parts) >= 3:
                try:
                    # Simulate firmware that refuses a full-scale ceiling.
                    self._maxpwr = min(99.9, float(parts[2]))
                except ValueError:
                    pass
            return ""
        if c_upper.startswith("LOOP 1:RATE"):
            parts = cmd.split()
            if len(parts) >= 3:
                try:
                    self._rate = float(parts[2])
                except ValueError:
                    pass
            return ""

        return "OK"
