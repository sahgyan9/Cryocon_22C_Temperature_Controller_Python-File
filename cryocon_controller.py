"""
Cryocon 22C Temperature Controller - Python Control Module
===========================================================
This module provides a class-based interface to communicate with
the Cryocon 22C temperature controller.

Author: Lab Automation
Date: 2026-02-01
"""

import serial
import time
from datetime import datetime
from typing import Optional, Tuple, Dict, Any


class Cryocon22C:
    """
    Class to interface with Cryocon 22C Temperature Controller.
    
    The Cryocon 22C is a dual-channel temperature controller commonly used
    in cryogenic applications. It supports various sensor types (diodes, RTDs)
    and has two control loops for PID temperature control.
    
    Usage:
        controller = Cryocon22C("COM20")
        controller.connect()
        temp = controller.read_temperature("A")
        controller.disconnect()
    """
    
    def __init__(self, port: str = "COM5", baud_rate: int = 57600, timeout: float = 2.0):
        """
        Initialize the Cryocon 22C controller interface.
        
        Args:
            port: Serial port (e.g., "COM5" or "COM20" on Windows, "/dev/ttyUSB0" on Linux)
            baud_rate: Communication baud rate (default 57600 for upgraded hardware rate; previously 9600)
            timeout: Serial communication timeout in seconds
        """
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.serial: Optional[serial.Serial] = None
        self.connected = False
        
    def connect(self) -> bool:
        """
        Establish connection to the Cryocon controller.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            time.sleep(0.3)  # Wait for connection to stabilize
            self.connected = True
            print(f"[OK] Connected to Cryocon 22C on {self.port} @ {self.baud_rate} baud")
            return True
        except serial.SerialException as e:
            print(f"[ERROR] Connection failed: {e}")
            self.connected = False
            return False
    
    def disconnect(self) -> None:
        """Close the serial connection."""
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.connected = False
            print("[OK] Disconnected from Cryocon 22C")
    
    def _send_command(self, command: str, wait_time: float = 0.01) -> str:
        """
        Send a command and receive response.
        
        Args:
            command: SCPI command to send
            wait_time: Small pause before reading if needed (0.01s at 57600 baud)
            
        Returns:
            Response string from the controller
        """
        if not self.connected or not self.serial:
            raise ConnectionError("Not connected to controller")
        
        # Clear any pending data
        self.serial.reset_input_buffer()
        
        # Send command with termination
        self.serial.write(f'{command}\r\n'.encode())
        if wait_time > 0:
            time.sleep(wait_time)
        
        # Read line response terminated by CRLF
        response = self.serial.readline().decode('utf-8', errors='ignore').strip()
        return response
    
    # ==================== IDENTIFICATION ====================
    
    def get_identity(self) -> str:
        """Get device identification string."""
        return self._send_command("*IDN?")
    
    def get_firmware_version(self) -> str:
        """Get firmware revision."""
        return self._send_command("SYSTEM:FWREV?")
    
    # ==================== TEMPERATURE READING ====================
    
    def read_temperature(self, channel: str = "A") -> float:
        """
        Read temperature from specified channel.
        
        Args:
            channel: "A" or "B"
            
        Returns:
            Temperature value in current units (K, C, or F)
        """
        channel = channel.upper()
        if channel not in ["A", "B"]:
            raise ValueError("Channel must be 'A' or 'B'")
        
        response = self._send_command(f"INPUT? {channel}")
        try:
            return float(response)
        except ValueError:
            print(f"Warning: Could not parse temperature: {response}")
            return float('nan')
    
    def read_both_temperatures(self) -> Tuple[float, float]:
        """
        Read temperature from both channels.
        
        Returns:
            Tuple of (Channel A temp, Channel B temp)
        """
        temp_a = self.read_temperature("A")
        temp_b = self.read_temperature("B")
        return temp_a, temp_b
    
    def get_temperature_units(self, channel: str = "A") -> str:
        """Get the temperature units for a channel (K, C, or F)."""
        return self._send_command(f"INPUT {channel}:UNITS?")
    
    def set_temperature_units(self, channel: str, units: str) -> None:
        """
        Set temperature units for a channel.
        
        Args:
            channel: "A" or "B"
            units: "K" (Kelvin), "C" (Celsius), or "F" (Fahrenheit)
        """
        units = units.upper()
        if units not in ["K", "C", "F"]:
            raise ValueError("Units must be 'K', 'C', or 'F'")
        self._send_command(f"INPUT {channel}:UNITS {units}")
    
    def get_sensor_type(self, channel: str = "A") -> str:
        """Get the sensor type for a channel."""
        return self._send_command(f"INPUT {channel}:SENTYPE?")
    
    def get_sensor_name(self, channel: str = "A") -> str:
        """Get the sensor name for a channel."""
        return self._send_command(f"INPUT {channel}:NAME?")
    
    # ==================== PID CONTROL ====================
    
    def get_setpoint(self, loop: int = 1) -> float:
        """
        Get the current setpoint for a control loop.
        
        Args:
            loop: 1 or 2
            
        Returns:
            Setpoint temperature
        """
        response = self._send_command(f"LOOP {loop}:SETPT?")
        clean_resp = response.rstrip('KkCcFf ').strip()
        try:
            return float(clean_resp)
        except ValueError:
            return float('nan')
    
    def set_setpoint(self, temperature: float, loop: int = 1) -> None:
        """
        Set the temperature setpoint for a control loop.
        
        Args:
            temperature: Target temperature in current units
            loop: 1 or 2
        """
        self._send_command(f"LOOP {loop}:SETPT {temperature}")
        print(f"[OK] Setpoint set to {temperature} on Loop {loop}")
    
    def get_pid_parameters(self, loop: int = 1) -> Dict[str, float]:
        """
        Get PID parameters for a control loop.
        
        Returns:
            Dictionary with 'P', 'I', 'D' gains
        """
        p_gain = self._send_command(f"LOOP {loop}:PGAIN?")
        i_gain = self._send_command(f"LOOP {loop}:IGAIN?")
        d_gain = self._send_command(f"LOOP {loop}:DGAIN?")
        
        return {
            'P': float(p_gain) if p_gain.replace('.','').replace('-','').isdigit() else 0,
            'I': float(i_gain) if i_gain.replace('.','').replace('-','').isdigit() else 0,
            'D': float(d_gain) if d_gain.replace('.','').replace('-','').isdigit() else 0
        }
    
    def set_pid_parameters(self, p: float, i: float, d: float, loop: int = 1) -> None:
        """
        Set PID parameters for a control loop.
        
        Args:
            p: Proportional gain
            i: Integral gain
            d: Derivative gain
            loop: 1 or 2
        """
        self._send_command(f"LOOP {loop}:PGAIN {p}")
        self._send_command(f"LOOP {loop}:IGAIN {i}")
        self._send_command(f"LOOP {loop}:DGAIN {d}")
        print(f"[OK] PID set to P={p}, I={i}, D={d} on Loop {loop}")
    
    def get_control_source(self, loop: int = 1) -> str:
        """Get which input channel is the source for a control loop."""
        return self._send_command(f"LOOP {loop}:SOURCE?")
    
    def set_control_source(self, channel: str, loop: int = 1) -> None:
        """
        Set which input channel is the source for a control loop.
        
        Args:
            channel: "A" or "B"
            loop: 1 or 2
        """
        self._send_command(f"LOOP {loop}:SOURCE CH{channel}")
    
    def get_control_type(self, loop: int = 1) -> str:
        """Get the control type for a loop (PID, MAN, TABLE, etc.)."""
        return self._send_command(f"LOOP {loop}:TYPE?")
    
    def set_control_type(self, control_type: str, loop: int = 1) -> None:
        """
        Set the control type for a loop.
        
        Args:
            control_type: "PID", "MAN", "TABLE", "RAMPP"
            loop: 1 or 2
        """
        self._send_command(f"LOOP {loop}:TYPE {control_type}")
    
    def get_heater_range(self, loop: int = 1) -> str:
        """Get the heater range setting."""
        return self._send_command(f"LOOP {loop}:RANGE?")
    
    def set_heater_range(self, range_setting: str, loop: int = 1) -> None:
        """
        Set the heater range.
        
        Args:
            range_setting: "HI", "MID", "LOW", or specific value
            loop: 1 or 2
        """
        self._send_command(f"LOOP {loop}:RANGE {range_setting}")
    
    def get_heater_output(self, loop: int = 1) -> float:
        """
        Get current heater output power percentage.
        
        Returns:
            Heater power as percentage (0-100)
        """
        response = self._send_command(f"LOOP {loop}:OUTP?")
        clean_resp = response.rstrip('% ').strip()
        try:
            return float(clean_resp)
        except ValueError:
            return 0.0
    
    def get_max_power(self, loop: int = 1) -> float:
        """Get maximum heater power setting (percentage 0-100%)."""
        response = self._send_command(f"LOOP {loop}:MAXPWR?")
        clean_resp = response.rstrip('% ').strip()
        try:
            return float(clean_resp)
        except ValueError:
            return 0.0
    
    def set_max_power(self, max_power: float, loop: int = 1) -> None:
        """Set maximum heater power (0-100%)."""
        self._send_command(f"LOOP {loop}:MAXPWR {max_power}")
        print(f"[OK] Max power set to {max_power}% on Loop {loop}")

    def get_ramp_rate(self, loop: int = 1) -> float:
        """Get ramp rate in K/min."""
        response = self._send_command(f"LOOP {loop}:RATE?")
        try:
            return float(response)
        except ValueError:
            return 0.0

    def set_ramp_rate(self, rate: float, loop: int = 1) -> None:
        """Set ramp rate in K/min."""
        self._send_command(f"LOOP {loop}:RATE {rate}")
        print(f"[OK] Ramp rate set to {rate} K/min on Loop {loop}")

    def start_ramp_anti_surge(self, target: float, rate: float = 1.0,
                              p: float = 40.0, i: float = 900.0, d: float = 0.0,
                              range_val: str = "HI", maxpwr: float = 70.0,
                              loop: int = 1) -> float:
        """
        Safely arm and start a temperature ramp to target with zero surge current.
        Enforces the validated anti-surge command sequence from the 2026-09-05 study.
        """
        live = self.read_temperature("A")
        if live != live:  # NaN check
            live = target

        # 1. Park working setpoint at current temperature in PID mode
        self.set_control_type("PID", loop=loop)
        time.sleep(0.3)
        self.set_setpoint(live, loop=loop)
        time.sleep(0.5)

        # 2. Configure validated hardware limits and PID gains
        self.set_heater_range(range_val, loop=loop)
        time.sleep(0.8)  # range change throws a mechanical relay
        self.set_max_power(maxpwr, loop=loop)
        self.set_pid_parameters(p, i, d, loop=loop)
        self.set_ramp_rate(rate, loop=loop)

        # 3. Engage control BEFORE target setpoint so loop starts from hold power
        self.enable_control()
        time.sleep(2.0)

        # 4. Switch to RAMPP mode and arm ramp with target setpoint
        self.set_control_type("RAMPP", loop=loop)
        time.sleep(0.2)
        self.set_setpoint(target, loop=loop)
        print(f"[OK] Anti-surge ramp armed to {target} K at {rate} K/min (P={p}, I={i}, D={d})")
        return live
    
    # ==================== CONTROL ENABLE/DISABLE ====================
    
    def enable_control(self) -> None:
        """Enable the control loops (start PID control)."""
        self._send_command("CONTROL")
        print("[OK] Control ENABLED")
    
    def disable_control(self) -> None:
        """Disable the control loops (stop PID control)."""
        self._send_command("STOP")
        print("[OK] Control DISABLED (STOP)")
    
    def is_control_enabled(self) -> bool:
        """Check if control is enabled."""
        response = self._send_command("CONTROL?")
        return response.upper() in ["ON", "1", "TRUE"]
    
    # ==================== SYSTEM FUNCTIONS ====================
    
    def get_system_name(self) -> str:
        """Get the system name."""
        return self._send_command("SYSTEM:NAME?")
    
    def beep(self) -> None:
        """Make the controller beep."""
        self._send_command("SYSTEM:BEEP")
    
    # ==================== UTILITY METHODS ====================
    
    def get_full_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of the controller.
        
        Returns:
            Dictionary with all relevant status information
        """
        status = {
            'identity': self.get_identity(),
            'firmware': self.get_firmware_version(),
            'channel_a': {
                'temperature': self.read_temperature('A'),
                'units': self.get_temperature_units('A'),
                'sensor_type': self.get_sensor_type('A'),
            },
            'channel_b': {
                'temperature': self.read_temperature('B'),
                'units': self.get_temperature_units('B'),
                'sensor_type': self.get_sensor_type('B'),
            },
            'loop_1': {
                'setpoint': self.get_setpoint(1),
                'pid': self.get_pid_parameters(1),
                'source': self.get_control_source(1),
                'type': self.get_control_type(1),
                'heater_output': self.get_heater_output(1),
            },
            'control_enabled': self.is_control_enabled(),
        }
        return status
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


# ==================== TEST FUNCTIONS ====================

def test_basic_connection():
    """Test basic connection and identification."""
    print("\n" + "="*60)
    print("TEST 1: Basic Connection")
    print("="*60)
    
    with Cryocon22C("COM5") as controller:
        print(f"\nDevice ID: {controller.get_identity()}")
        print(f"Firmware: {controller.get_firmware_version()}")


def test_temperature_reading():
    """Test temperature reading from both channels."""
    print("\n" + "="*60)
    print("TEST 2: Temperature Reading")
    print("="*60)
    
    with Cryocon22C("COM5") as controller:
        temp_a, temp_b = controller.read_both_temperatures()
        units_a = controller.get_temperature_units('A')
        units_b = controller.get_temperature_units('B')
        
        print(f"\nChannel A: {temp_a} {units_a}")
        print(f"Channel B: {temp_b} {units_b}")
        
        print(f"\nSensor A Type: {controller.get_sensor_type('A')}")
        print(f"Sensor B Type: {controller.get_sensor_type('B')}")


def test_pid_settings():
    """Test reading PID settings."""
    print("\n" + "="*60)
    print("TEST 3: PID Control Settings")
    print("="*60)
    
    with Cryocon22C("COM5") as controller:
        print("\n--- Loop 1 ---")
        print(f"Setpoint: {controller.get_setpoint(1)}")
        print(f"PID Parameters: {controller.get_pid_parameters(1)}")
        print(f"Control Source: {controller.get_control_source(1)}")
        print(f"Control Type: {controller.get_control_type(1)}")
        print(f"Heater Range: {controller.get_heater_range(1)}")
        print(f"Heater Output: {controller.get_heater_output(1)}%")
        print(f"Max Power: {controller.get_max_power(1)}%")
        
        print("\n--- Loop 2 ---")
        print(f"Setpoint: {controller.get_setpoint(2)}")
        print(f"Control Source: {controller.get_control_source(2)}")
        print(f"Control Type: {controller.get_control_type(2)}")
        
        print(f"\nControl Enabled: {controller.is_control_enabled()}")


def test_full_status():
    """Get complete status dump."""
    print("\n" + "="*60)
    print("TEST 4: Full Status")
    print("="*60)
    
    with Cryocon22C("COM5") as controller:
        import json
        status = controller.get_full_status()
        print(json.dumps(status, indent=2, default=str))


if __name__ == "__main__":
    print("=" * 60)
    print("     CRYOCON 22C TEMPERATURE CONTROLLER - PYTHON TEST")
    print("=" * 60)
    
    # Run all tests
    test_basic_connection()
    test_temperature_reading()
    test_pid_settings()
    test_full_status()
    
    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60)
