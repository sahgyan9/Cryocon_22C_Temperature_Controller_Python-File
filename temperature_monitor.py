"""
Cryocon 22C - Continuous Temperature Monitor with Live Plot
============================================================
Features:
- Real-time temperature display
- Live plotting with matplotlib
- Data logging to CSV file
- Configurable sampling interval

Press Ctrl+C to stop monitoring
"""

import serial
import time
import csv
from datetime import datetime
import os

# Try to import matplotlib for plotting
try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from matplotlib.dates import DateFormatter
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    print("Note: matplotlib not installed. Install with: pip install matplotlib")
    print("Running in text-only mode.\n")


class CryoconMonitor:
    def __init__(self, port="COM5", baud_rate=9600):
        self.port = port
        self.baud_rate = baud_rate
        self.serial = None
        self.running = False
        
        # Data storage
        self.timestamps = []
        self.temperatures_a = []
        self.temperatures_b = []
        
        # Settings
        self.sampling_interval = 1.0  # seconds
        self.save_to_file = False
        self.filename = None
        self.csv_writer = None
        self.csv_file = None
        
    def connect(self):
        """Connect to the Cryocon controller."""
        try:
            self.serial = serial.Serial(
                self.port, self.baud_rate, timeout=2
            )
            time.sleep(0.5)
            print(f"[OK] Connected to Cryocon 22C on {self.port}")
            
            # Get device identity
            identity = self._query("*IDN?")
            print(f"  Device: {identity}")
            return True
        except serial.SerialException as e:
            print(f"[ERROR] Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the controller."""
        if self.serial and self.serial.is_open:
            self.serial.close()
            print("[OK] Disconnected")
        if self.csv_file:
            self.csv_file.close()
            print(f"[OK] Data saved to {self.filename}")
    
    def _query(self, cmd):
        """Send command and get response."""
        self.serial.reset_input_buffer()
        self.serial.write(f'{cmd}\r\n'.encode())
        time.sleep(0.05)
        return self.serial.readline().decode('utf-8', errors='ignore').strip()
    
    def read_temperature(self, channel="A"):
        """Read temperature from a channel."""
        response = self._query(f"INPUT? {channel}")
        try:
            return float(response)
        except ValueError:
            return float('nan')
    
    def setup_data_logging(self, filename=None):
        """Setup CSV file for data logging."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cryocon_data_{timestamp}.csv"
        
        self.filename = filename
        self.csv_file = open(filename, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(['Timestamp', 'Elapsed_Seconds', 'Temperature_A_K', 'Temperature_B_K'])
        self.save_to_file = True
        print(f"[OK] Data logging enabled: {filename}")
    
    def monitor_text_mode(self, duration=None, interval=1.0):
        """
        Monitor temperatures in text mode (no plotting).
        
        Args:
            duration: Total monitoring time in seconds (None = indefinite)
            interval: Sampling interval in seconds
        """
        self.sampling_interval = interval
        self.running = True
        start_time = time.time()
        reading_count = 0
        
        print("\n" + "="*60)
        print("TEMPERATURE MONITORING (Press Ctrl+C to stop)")
        print("="*60)
        print(f"{'Time':^12} {'Elapsed':^10} {'Ch A (K)':^12} {'Ch B (K)':^12}")
        print("-"*60)
        
        try:
            while self.running:
                current_time = datetime.now()
                elapsed = time.time() - start_time
                
                # Read temperatures
                temp_a = self.read_temperature("A")
                temp_b = self.read_temperature("B")
                
                # Store data
                self.timestamps.append(current_time)
                self.temperatures_a.append(temp_a)
                self.temperatures_b.append(temp_b)
                
                # Display
                time_str = current_time.strftime("%H:%M:%S")
                temp_b_str = f"{temp_b:.2f}" if not (temp_b != temp_b) else "N/C"  # NaN check
                print(f"{time_str:^12} {elapsed:^10.1f} {temp_a:^12.2f} {temp_b_str:^12}")
                
                # Save to file
                if self.save_to_file and self.csv_writer:
                    self.csv_writer.writerow([
                        current_time.isoformat(),
                        f"{elapsed:.2f}",
                        f"{temp_a:.6f}",
                        f"{temp_b:.6f}" if not (temp_b != temp_b) else ""
                    ])
                    self.csv_file.flush()  # Ensure data is written
                
                reading_count += 1
                
                # Check duration
                if duration and elapsed >= duration:
                    print(f"\n[OK] Monitoring complete ({duration}s)")
                    break
                
                time.sleep(self.sampling_interval)
                
        except KeyboardInterrupt:
            print(f"\n\n[OK] Monitoring stopped by user")
        
        print(f"Total readings: {reading_count}")
        return self.timestamps, self.temperatures_a, self.temperatures_b
    
    def monitor_with_plot(self, duration=None, interval=1.0, max_points=500):
        """
        Monitor temperatures with live matplotlib plot.
        
        Args:
            duration: Total monitoring time in seconds (None = indefinite)
            interval: Sampling interval in seconds
            max_points: Maximum number of points to display
        """
        if not PLOTTING_AVAILABLE:
            print("Matplotlib not available. Using text mode.")
            return self.monitor_text_mode(duration, interval)
        
        self.sampling_interval = interval
        self.running = True
        start_time = time.time()
        
        # Setup the plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        fig.suptitle('Cryocon 22C Temperature Monitor', fontsize=14, fontweight='bold')
        
        # Channel A plot
        line_a, = ax1.plot([], [], 'b-', linewidth=2, label='Channel A')
        ax1.set_ylabel('Temperature (K)', fontsize=12)
        ax1.set_xlabel('Time', fontsize=10)
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)
        ax1.set_title('Channel A Temperature')
        
        # Temperature vs Time elapsed plot
        line_elapsed, = ax2.plot([], [], 'r-', linewidth=2, label='Channel A')
        ax2.set_ylabel('Temperature (K)', fontsize=12)
        ax2.set_xlabel('Elapsed Time (seconds)', fontsize=10)
        ax2.legend(loc='upper right')
        ax2.grid(True, alpha=0.3)
        ax2.set_title('Temperature vs Elapsed Time')
        
        # Text annotations for current values
        temp_text = ax1.text(0.02, 0.95, '', transform=ax1.transAxes, 
                             fontsize=12, verticalalignment='top',
                             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        elapsed_times = []
        
        def update(frame):
            if not self.running:
                return line_a, line_elapsed, temp_text
            
            current_time = datetime.now()
            elapsed = time.time() - start_time
            
            # Read temperature
            temp_a = self.read_temperature("A")
            
            # Store data
            self.timestamps.append(current_time)
            self.temperatures_a.append(temp_a)
            elapsed_times.append(elapsed)
            
            # Limit data points
            if len(self.timestamps) > max_points:
                self.timestamps.pop(0)
                self.temperatures_a.pop(0)
                elapsed_times.pop(0)
            
            # Update plots
            if len(self.timestamps) > 1:
                line_a.set_data(self.timestamps, self.temperatures_a)
                ax1.relim()
                ax1.autoscale_view()
                ax1.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
                fig.autofmt_xdate()
                
                line_elapsed.set_data(elapsed_times, self.temperatures_a)
                ax2.relim()
                ax2.autoscale_view()
            
            # Update text
            temp_text.set_text(f'Current: {temp_a:.3f} K\nElapsed: {elapsed:.1f} s')
            
            # Save to file
            if self.save_to_file and self.csv_writer:
                self.csv_writer.writerow([
                    current_time.isoformat(),
                    f"{elapsed:.2f}",
                    f"{temp_a:.6f}",
                    ""
                ])
                self.csv_file.flush()
            
            # Check duration
            if duration and elapsed >= duration:
                self.running = False
                plt.close(fig)
            
            return line_a, line_elapsed, temp_text
        
        ani = animation.FuncAnimation(
            fig, update, 
            interval=int(self.sampling_interval * 1000),
            blit=False,
            cache_frame_data=False
        )
        
        plt.show()
        
        return self.timestamps, self.temperatures_a, self.temperatures_b


def main():
    """Main function to run the temperature monitor."""
    print("=" * 60)
    print("      CRYOCON 22C CONTINUOUS TEMPERATURE MONITOR")
    print("=" * 60)
    
    # Configuration
    PORT = "COM5"
    SAMPLING_INTERVAL = 1.0  # seconds
    SAVE_DATA = True
    USE_PLOT = PLOTTING_AVAILABLE  # Use plotting if available
    
    # Create monitor
    monitor = CryoconMonitor(PORT)
    
    if not monitor.connect():
        return
    
    try:
        # Setup data logging
        if SAVE_DATA:
            monitor.setup_data_logging()
        
        # Start monitoring
        if USE_PLOT:
            print("\nStarting live plot... Close the plot window to stop.")
            monitor.monitor_with_plot(interval=SAMPLING_INTERVAL)
        else:
            print("\nStarting text-mode monitoring...")
            monitor.monitor_text_mode(interval=SAMPLING_INTERVAL)
            
    finally:
        monitor.disconnect()


if __name__ == "__main__":
    main()
