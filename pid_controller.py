"""
Cryocon 22C - PID Temperature Controller
=========================================
This script demonstrates how to use PID control to:
1. Set a target temperature
2. Enable/disable control
3. Monitor the approach to setpoint

For cooling to 77K with liquid nitrogen:
- The LN2 provides cooling
- The heater provides controlled warming to stabilize at setpoint
- PID adjusts heater power to maintain temperature

IMPORTANT PID CONCEPTS:
-----------------------
P (Proportional): Reacts to current error
   - Higher P = faster response, but may overshoot
   - Too high = oscillation

I (Integral): Eliminates steady-state error
   - Accumulates error over time
   - Too high = slow response, windup issues

D (Derivative): Dampens oscillations
   - Reacts to rate of change
   - Too high = noise sensitivity

Typical starting values for Cryocon:
- P: 50-100
- I: 10-50
- D: 0-10

Press Ctrl+C to stop
"""

import serial
import time
from datetime import datetime
import csv


class CryoconPIDController:
    def __init__(self, port="COM5", baud_rate=9600):
        self.port = port
        self.baud_rate = baud_rate
        self.serial = None
        
    def connect(self):
        """Connect to the controller."""
        try:
            self.serial = serial.Serial(self.port, self.baud_rate, timeout=2)
            time.sleep(0.5)
            identity = self._query("*IDN?")
            print(f"[OK] Connected: {identity}")
            return True
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the controller."""
        if self.serial and self.serial.is_open:
            self.serial.close()
            print("[OK] Disconnected")
    
    def _query(self, cmd):
        """Send command and get response."""
        self.serial.reset_input_buffer()
        self.serial.write(f'{cmd}\r\n'.encode())
        time.sleep(0.05)
        return self.serial.readline().decode('utf-8', errors='ignore').strip()
    
    def _send(self, cmd):
        """Send command without expecting response."""
        self.serial.write(f'{cmd}\r\n'.encode())
        time.sleep(0.1)
    
    # ============ Temperature Reading ============
    
    def read_temperature(self, channel="A"):
        """Read temperature from a channel."""
        response = self._query(f"INPUT? {channel}")
        try:
            return float(response)
        except ValueError:
            return float('nan')
    
    # ============ PID Control ============
    
    def get_setpoint(self, loop=1):
        """Get current setpoint."""
        response = self._query(f"LOOP {loop}:SETPT?")
        try:
            return float(response.replace('K', '').strip())
        except ValueError:
            return 0.0
    
    def set_setpoint(self, temperature, loop=1):
        """Set target temperature."""
        self._send(f"LOOP {loop}:SETPT {temperature}")
        print(f"[OK] Setpoint set to {temperature} K")
    
    def get_pid(self, loop=1):
        """Get PID parameters."""
        p = float(self._query(f"LOOP {loop}:PGAIN?"))
        i = float(self._query(f"LOOP {loop}:IGAIN?"))
        d = float(self._query(f"LOOP {loop}:DGAIN?"))
        return {'P': p, 'I': i, 'D': d}
    
    def set_pid(self, p, i, d, loop=1):
        """Set PID parameters."""
        self._send(f"LOOP {loop}:PGAIN {p}")
        self._send(f"LOOP {loop}:IGAIN {i}")
        self._send(f"LOOP {loop}:DGAIN {d}")
        print(f"[OK] PID set to P={p}, I={i}, D={d}")
    
    def get_heater_output(self, loop=1):
        """Get current heater output percentage."""
        response = self._query(f"LOOP {loop}:OUTP?")
        try:
            return float(response)
        except ValueError:
            return 0.0
    
    def set_heater_range(self, range_val, loop=1):
        """
        Set heater range.
        For Model 22C: HI, MID, LOW
        """
        self._send(f"LOOP {loop}:RANGE {range_val}")
        print(f"[OK] Heater range set to {range_val}")
    
    def get_heater_range(self, loop=1):
        """Get current heater range."""
        return self._query(f"LOOP {loop}:RANGE?")
    
    def set_max_power(self, max_pct, loop=1):
        """Set maximum heater power (0-100%)."""
        self._send(f"LOOP {loop}:PMAX {max_pct}")
        print(f"[OK] Max power set to {max_pct}%")
    
    def enable_control(self):
        """Enable PID control."""
        self._send("CONTROL")
        print("[OK] Control ENABLED")
    
    def disable_control(self):
        """Disable PID control (stop heater)."""
        self._send("STOP")
        print("[OK] Control DISABLED")
    
    def is_control_enabled(self):
        """Check if control is enabled."""
        response = self._query("CONTROL?")
        return response.upper() in ["ON", "1", "TRUE"]
    
    def get_status(self):
        """Get comprehensive status."""
        temp_a = self.read_temperature("A")
        setpoint = self.get_setpoint()
        heater = self.get_heater_output()
        control = self.is_control_enabled()
        pid = self.get_pid()
        
        return {
            'temperature': temp_a,
            'setpoint': setpoint,
            'error': temp_a - setpoint,
            'heater_output': heater,
            'control_enabled': control,
            'pid': pid
        }
    
    def print_status(self):
        """Print formatted status."""
        status = self.get_status()
        print(f"\n{'='*50}")
        print(f"Temperature:    {status['temperature']:.3f} K")
        print(f"Setpoint:       {status['setpoint']:.3f} K")
        print(f"Error:          {status['error']:+.3f} K")
        print(f"Heater Output:  {status['heater_output']:.1f}%")
        print(f"Control:        {'ON' if status['control_enabled'] else 'OFF'}")
        print(f"PID:            P={status['pid']['P']}, I={status['pid']['I']}, D={status['pid']['D']}")
        print(f"{'='*50}")


def demo_pid_monitoring():
    """
    Demonstrate PID control monitoring.
    Shows how temperature approaches setpoint.
    """
    controller = CryoconPIDController("COM5")
    
    if not controller.connect():
        return
    
    try:
        print("\n" + "="*60)
        print("CURRENT CONTROLLER STATUS")
        print("="*60)
        controller.print_status()
        
        print("\n" + "="*60)
        print("MONITORING TEMPERATURE (Press Ctrl+C to stop)")
        print("="*60)
        
        # Setup data logging
        filename = f"pid_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Elapsed_s', 'Temperature_K', 'Setpoint_K', 'Error_K', 'Heater_%', 'Control'])
            
            start_time = time.time()
            
            print(f"\n{'Time':^10} {'Elapsed':^8} {'Temp (K)':^12} {'Setpoint':^10} {'Error':^10} {'Heater%':^8} {'Ctrl':^5}")
            print("-"*70)
            
            while True:
                current_time = datetime.now()
                elapsed = time.time() - start_time
                
                status = controller.get_status()
                
                ctrl_str = "ON" if status['control_enabled'] else "OFF"
                print(f"{current_time.strftime('%H:%M:%S'):^10} "
                      f"{elapsed:^8.1f} "
                      f"{status['temperature']:^12.3f} "
                      f"{status['setpoint']:^10.1f} "
                      f"{status['error']:^+10.3f} "
                      f"{status['heater_output']:^8.1f} "
                      f"{ctrl_str:^5}")
                
                writer.writerow([
                    current_time.isoformat(),
                    f"{elapsed:.2f}",
                    f"{status['temperature']:.6f}",
                    f"{status['setpoint']:.2f}",
                    f"{status['error']:.6f}",
                    f"{status['heater_output']:.2f}",
                    ctrl_str
                ])
                f.flush()
                
                time.sleep(1.0)
                
    except KeyboardInterrupt:
        print(f"\n\n[OK] Monitoring stopped")
        print(f"[OK] Data saved to {filename}")
    finally:
        controller.disconnect()


def interactive_pid_control():
    """
    Interactive PID control interface.
    Allows user to set parameters and control heating.
    """
    controller = CryoconPIDController("COM5")
    
    if not controller.connect():
        return
    
    try:
        print("\n" + "="*60)
        print("INTERACTIVE PID CONTROL")
        print("="*60)
        controller.print_status()
        
        while True:
            print("\n--- MENU ---")
            print("1. Read temperature")
            print("2. Set setpoint")
            print("3. Set PID parameters")
            print("4. Enable control")
            print("5. Disable control (STOP)")
            print("6. Set heater range")
            print("7. Set max power")
            print("8. Show full status")
            print("9. Start monitoring")
            print("0. Exit")
            
            choice = input("\nChoice: ").strip()
            
            if choice == '1':
                temp = controller.read_temperature("A")
                print(f"\nTemperature: {temp:.3f} K")
                
            elif choice == '2':
                try:
                    sp = float(input("Enter setpoint (K): "))
                    controller.set_setpoint(sp)
                except ValueError:
                    print("Invalid input")
                    
            elif choice == '3':
                try:
                    p = float(input("P gain: "))
                    i = float(input("I gain: "))
                    d = float(input("D gain: "))
                    controller.set_pid(p, i, d)
                except ValueError:
                    print("Invalid input")
                    
            elif choice == '4':
                controller.enable_control()
                
            elif choice == '5':
                controller.disable_control()
                
            elif choice == '6':
                print("Options: HI, MID, LOW")
                range_val = input("Heater range: ").strip().upper()
                controller.set_heater_range(range_val)
                
            elif choice == '7':
                try:
                    pmax = float(input("Max power (%): "))
                    controller.set_max_power(pmax)
                except ValueError:
                    print("Invalid input")
                    
            elif choice == '8':
                controller.print_status()
                
            elif choice == '9':
                demo_pid_monitoring()
                break
                
            elif choice == '0':
                break
                
            else:
                print("Invalid choice")
                
    finally:
        controller.disconnect()


if __name__ == "__main__":
    print("=" * 60)
    print("       CRYOCON 22C PID TEMPERATURE CONTROLLER")
    print("=" * 60)
    print("\nSelect mode:")
    print("1. Monitoring only")
    print("2. Interactive control")
    
    mode = input("\nChoice [1/2]: ").strip()
    
    if mode == '2':
        interactive_pid_control()
    else:
        demo_pid_monitoring()
