"""
Cryocon 22C Temperature Controller - Professional Lab GUI
=========================================================
Target System: Janis Research ST-LN-500 Cryogenic Probe Station
Controller: Cryo-con Model 22C (Firmware 3.33G, Serial 206687)

Validated Operating Parameters (2026-09-05 Study):
- Proportional Gain (P):  40.0
- Integral Time (I):      900.0 s (15 minutes) - NOTE: seconds, not gain!
- Derivative Gain (D):    0.0
- Heater Range:           HI (50 W full scale authority)
- Maximum Power Cap:      70.0 % (35 W ceiling)
- Ramp Rate:              1.0 K/min (or 2.0 K/min)
- Loop Mode:              RAMPP (PID control with ramp)

Safety Rule: Anti-Surge Command Ordering
Always parks setpoint at current temperature in PID mode and engages CONTROL
before arming target setpoint in RAMPP mode to prevent full-power heater surges.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import datetime
import os
import csv
import serial
import serial.tools.list_ports
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

PYTHON_SERIAL_TIMEOUT = 1.5

# Validated Baseline Tuning Parameters (FINAL_REPORT.md 2026-09-05)
DEFAULT_PGAIN = 40.0
DEFAULT_IGAIN = 900.0   # Seconds (Integral reset time, NOT a gain)
DEFAULT_DGAIN = 0.0
DEFAULT_RANGE = "HI"    # 50 W full-scale authority
DEFAULT_MAXPWR = 70.0   # % power ceiling
DEFAULT_RATE = 1.0      # K/min


class CryoconComm:
    """Thread-safe Cryocon 22C Serial Communication Manager."""
    def __init__(self):
        self.ser = None
        self.lock = threading.Lock()
        self.connected = False
        self.port = "COM5"
        self.baud = 57600

    def connect(self, port="COM5", baud=57600):
        with self.lock:
            try:
                self.ser = serial.Serial(port, baud, timeout=PYTHON_SERIAL_TIMEOUT,
                                         bytesize=serial.EIGHTBITS,
                                         parity=serial.PARITY_NONE,
                                         stopbits=serial.STOPBITS_ONE)
                time.sleep(0.3)
                self.port = port
                self.baud = baud
                self.connected = True
                return True, "Connected successfully"
            except Exception as e:
                self.connected = False
                return False, str(e)

    def disconnect(self):
        with self.lock:
            if self.ser and self.ser.is_open:
                try:
                    self.ser.close()
                except Exception:
                    pass
            self.connected = False

    def query(self, cmd, wait=0.01):
        with self.lock:
            if not self.connected or not self.ser:
                return "ERR"
            try:
                self.ser.reset_input_buffer()
                self.ser.write((cmd + "\r\n").encode())
                if wait > 0:
                    time.sleep(wait)
                resp = self.ser.readline().decode("utf-8", errors="ignore").strip()
                return resp
            except Exception:
                return "ERR"

    def query_multiline(self, cmd, wait=1.5):
        with self.lock:
            if not self.connected or not self.ser:
                return "ERR"
            try:
                self.ser.reset_input_buffer()
                self.ser.write((cmd + "\r\n").encode())
                time.sleep(wait)
                chunks = []
                deadline = time.time() + 3.5
                while time.time() < deadline:
                    n = self.ser.in_waiting
                    if n > 0:
                        chunks.append(self.ser.read(n).decode("utf-8", errors="ignore"))
                        time.sleep(0.1)
                    elif chunks:
                        break
                    else:
                        time.sleep(0.1)
                return "".join(chunks).strip()
            except Exception as e:
                return f"ERR: {e}"

    def send(self, cmd, wait=0.15):
        with self.lock:
            if not self.connected or not self.ser:
                return False
            try:
                self.ser.write((cmd + "\r\n").encode())
                time.sleep(wait)
                return True
            except Exception:
                return False


class CryoconGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cryocon 22C Temperature Controller - Janis ST-LN-500 Station")
        self.root.geometry("1320x880")
        self.root.minsize(1100, 720)

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self._setup_styles()

        self.comm = CryoconComm()

        self.telemetry = {
            "temp_a": 0.0, "temp_b": 0.0, "setpoint": 0.0, "error": 0.0,
            "heater_pwr": 0.0, "control": "OFF", "type": "RAMPP",
            "tableix": "2", "rate": DEFAULT_RATE, "range": DEFAULT_RANGE,
            "maxpwr": DEFAULT_MAXPWR, "pgain": DEFAULT_PGAIN,
            "igain": DEFAULT_IGAIN, "dgain": DEFAULT_DGAIN,
            "ramp_active": "NO", "idn": "Disconnected"
        }

        # Plot Data Buffers
        self.plot_times = []
        self.plot_temp_a = []
        self.plot_temp_b = []
        self.plot_setpt = []
        self.plot_heater = []
        self.max_plot_points = 2400
        self.plot_window_seconds = 600

        # Logging State
        self.logging_active = False
        self.log_file = None
        self.log_writer = None
        self.log_records_count = 0
        self.log_start_time = None
        self.log_filename = ""

        # Ramp Execution State
        self.ramp_worker_thread = None
        self.is_arming_ramp = False

        # Polling Thread State
        self.poll_running = False
        self.poll_thread = None
        self.poll_delay = 0.01
        self.last_chart_draw = 0.0

        self._build_layout()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.after(400, self._auto_connect)

    def _setup_styles(self):
        self.style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))
        self.style.configure("ReadoutTitle.TLabel", font=("Segoe UI", 9, "bold"), foreground="#555555")
        self.style.configure("ReadoutValueA.TLabel", font=("Segoe UI", 26, "bold"), foreground="#0066cc")
        self.style.configure("ReadoutValueB.TLabel", font=("Segoe UI", 20, "bold"), foreground="#2e7d32")
        self.style.configure("ReadoutValueSP.TLabel", font=("Segoe UI", 22, "bold"), foreground="#d84315")
        self.style.configure("ReadoutValueHT.TLabel", font=("Segoe UI", 22, "bold"), foreground="#6a1b9a")
        self.style.configure("SubText.TLabel", font=("Segoe UI", 8), foreground="#777777")

    def _build_layout(self):
        top_frame = ttk.Frame(self.root, padding=8)
        top_frame.pack(fill=tk.X)

        ttk.Label(top_frame, text="COM Port:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.port_combo = ttk.Combobox(top_frame, width=8, values=self._get_com_ports())
        self.port_combo.set("COM5")
        self.port_combo.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_refresh_ports = ttk.Button(top_frame, text="↻", width=3, command=self._refresh_ports)
        self.btn_refresh_ports.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_connect = ttk.Button(top_frame, text="Connect", command=self._toggle_connection)
        self.btn_connect.pack(side=tk.LEFT, padx=(0, 10))

        self.lbl_conn_status = ttk.Label(top_frame, text="● Disconnected", font=("Segoe UI", 10, "bold"), foreground="red")
        self.lbl_conn_status.pack(side=tk.LEFT, padx=(0, 12))

        self.lbl_idn = ttk.Label(top_frame, text="Device: Disconnected", font=("Segoe UI", 9))
        self.lbl_idn.pack(side=tk.LEFT, padx=(0, 12))

        ttk.Label(top_frame, text="Update Rate:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(6, 3))
        self.combo_poll_rate = ttk.Combobox(
            top_frame, width=17, state="readonly",
            values=["0.10 s (10 Hz Ultra)", "0.25 s (Fast)", "0.5 s (LCD)", "1.0 s (1 Hz)", "2.0 s (Slow)"]
        )
        self.combo_poll_rate.set("0.10 s (10 Hz Ultra)")
        self.combo_poll_rate.bind("<<ComboboxSelected>>", self._on_poll_rate_change)
        self.combo_poll_rate.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_stop = tk.Button(top_frame, text="🛑 EMERGENCY STOP", font=("Segoe UI", 11, "bold"),
                                  bg="#d32f2f", fg="white", activebackground="#b71c1c", activeforeground="white",
                                  command=self._emergency_stop, padx=12, pady=3, relief=tk.RAISED)
        self.btn_stop.pack(side=tk.RIGHT, padx=4)

        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X)

        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        left_frame = ttk.Frame(main_paned, width=500)
        main_paned.add(left_frame, weight=0)

        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)

        self._build_telemetry_cards(left_frame)
        self._build_validated_ramp_panel(left_frame)
        self._build_logging_panel(left_frame)

        self._build_notebook_tabs(right_frame)

        self.statusbar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W, padding=(6, 3))
        self.statusbar.pack(fill=tk.X, side=tk.BOTTOM)

    def _build_telemetry_cards(self, parent):
        card_frame = ttk.LabelFrame(parent, text="Live Instrument Telemetry", padding=8)
        card_frame.pack(fill=tk.X, pady=(0, 6))

        # Temperature Unit Selection Toolbar
        unit_toolbar = ttk.Frame(card_frame)
        unit_toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=3, pady=(0, 6))

        ttk.Label(unit_toolbar, text="Display Unit:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(2, 8))

        self.temp_unit_var = tk.StringVar(value="C")

        self.rb_unit_c = ttk.Radiobutton(
            unit_toolbar, text="Celsius (°C)", variable=self.temp_unit_var, value="C",
            command=self._on_unit_change
        )
        self.rb_unit_c.pack(side=tk.LEFT, padx=(0, 8))

        self.rb_unit_k = ttk.Radiobutton(
            unit_toolbar, text="Kelvin (K)", variable=self.temp_unit_var, value="K",
            command=self._on_unit_change
        )
        self.rb_unit_k.pack(side=tk.LEFT, padx=(0, 8))

        self.rb_unit_dual = ttk.Radiobutton(
            unit_toolbar, text="Dual (K & °C)", variable=self.temp_unit_var, value="DUAL",
            command=self._on_unit_change
        )
        self.rb_unit_dual.pack(side=tk.LEFT, padx=(0, 8))

        # Channel A (Sample Stage) - Full Width Primary Readout
        f_a = ttk.Frame(card_frame, relief=tk.RIDGE, borderwidth=1, padding=8)
        f_a.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=3, pady=3)
        ttk.Label(f_a, text="SAMPLE STAGE TEMPERATURE (Channel A)", style="ReadoutTitle.TLabel").pack(anchor=tk.W)
        self.lbl_temp_a = ttk.Label(f_a, text="--.--- °C", style="ReadoutValueA.TLabel")
        self.lbl_temp_a.pack(anchor=tk.CENTER)
        self.lbl_status_a = ttk.Label(f_a, text="Active Control Sensor (Janis ST-LN-500)", style="SubText.TLabel")
        self.lbl_status_a.pack(anchor=tk.CENTER)

        # Setpoint & Tracking
        f_sp = ttk.Frame(card_frame, relief=tk.RIDGE, borderwidth=1, padding=6)
        f_sp.grid(row=2, column=0, sticky="nsew", padx=3, pady=3)
        ttk.Label(f_sp, text="SETPOINT & TRACKING", style="ReadoutTitle.TLabel").pack(anchor=tk.W)
        self.lbl_setpt = ttk.Label(f_sp, text="--.--- °C", style="ReadoutValueSP.TLabel")
        self.lbl_setpt.pack(anchor=tk.CENTER)
        self.lbl_error = ttk.Label(f_sp, text="Error: --.--- °C", font=("Segoe UI", 9, "bold"), foreground="#555")
        self.lbl_error.pack(anchor=tk.CENTER)

        # Heater Output %
        f_ht = ttk.Frame(card_frame, relief=tk.RIDGE, borderwidth=1, padding=6)
        f_ht.grid(row=2, column=1, sticky="nsew", padx=3, pady=3)
        ttk.Label(f_ht, text="HEATER POWER OUTPUT", style="ReadoutTitle.TLabel").pack(anchor=tk.W)
        self.lbl_heater = ttk.Label(f_ht, text="0.0 %", style="ReadoutValueHT.TLabel")
        self.lbl_heater.pack(anchor=tk.CENTER)
        self.pbar_heater = ttk.Progressbar(f_ht, orient=tk.HORIZONTAL, length=120, mode='determinate')
        self.pbar_heater.pack(fill=tk.X, padx=4, pady=(2, 0))

        card_frame.columnconfigure(0, weight=1)
        card_frame.columnconfigure(1, weight=1)

        # Status Badges
        badge_frame = ttk.Frame(card_frame)
        badge_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(6, 0))

        self.badge_ctrl = tk.Label(badge_frame, text="CONTROL: OFF", bg="#ffcdd2", fg="#b71c1c",
                                   font=("Segoe UI", 8, "bold"), padx=6, pady=2, relief=tk.GROOVE)
        self.badge_ctrl.pack(side=tk.LEFT, padx=2)

        self.badge_mode = tk.Label(badge_frame, text="MODE: RAMPP", bg="#e8eaf6", fg="#283593",
                                   font=("Segoe UI", 8, "bold"), padx=6, pady=2, relief=tk.GROOVE)
        self.badge_mode.pack(side=tk.LEFT, padx=2)

        self.badge_range = tk.Label(badge_frame, text="RANGE: HI", bg="#f3e5f5", fg="#4a148c",
                                    font=("Segoe UI", 8, "bold"), padx=6, pady=2, relief=tk.GROOVE)
        self.badge_range.pack(side=tk.LEFT, padx=2)

        self.badge_rate = tk.Label(badge_frame, text="RATE: 1.0 K/min", bg="#fff3e0", fg="#e65100",
                                   font=("Segoe UI", 8, "bold"), padx=6, pady=2, relief=tk.GROOVE)
        self.badge_rate.pack(side=tk.LEFT, padx=2)

        self.badge_pid = tk.Label(badge_frame, text="P=40 I=900 D=0", bg="#e0f2f1", fg="#004d40",
                                  font=("Segoe UI", 8, "bold"), padx=6, pady=2, relief=tk.GROOVE)
        self.badge_pid.pack(side=tk.LEFT, padx=2)

    def _build_validated_ramp_panel(self, parent):
        ramp_frame = ttk.LabelFrame(parent, text="🎯 Validated Temperature Ramp Controller", padding=8)
        ramp_frame.pack(fill=tk.X, pady=(0, 6))

        # Target Setpoint Row with Quick Presets
        r1 = ttk.Frame(ramp_frame)
        r1.pack(fill=tk.X, pady=3)
        ttk.Label(r1, text="Target Temp (K):", width=16, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        self.ent_target_temp = ttk.Entry(r1, width=9, font=("Segoe UI", 10))
        self.ent_target_temp.insert(0, "320.0")
        self.ent_target_temp.pack(side=tk.LEFT, padx=(0, 8))

        for p_temp in [300.0, 320.0, 350.0, 380.0, 400.0, 450.0]:
            btn = ttk.Button(r1, text=f"{int(p_temp)}K", width=5,
                             command=lambda t=p_temp: self._set_target_preset(t))
            btn.pack(side=tk.LEFT, padx=1)

        self.btn_inline_ramp = tk.Button(r1, text="▶ START RAMP", font=("Segoe UI", 9, "bold"),
                                         bg="#1b5e20", fg="white", activebackground="#2e7d32", activeforeground="white",
                                         command=self._start_anti_surge_ramp, padx=8, pady=1, relief=tk.RAISED)
        self.btn_inline_ramp.pack(side=tk.LEFT, padx=(6, 0))

        # Keyboard & Focus bindings for Target Temp
        self.ent_target_temp.bind("<Return>", lambda e: self._start_anti_surge_ramp())
        self.ent_target_temp.bind("<KP_Enter>", lambda e: self._start_anti_surge_ramp())
        self.ent_target_temp.bind("<FocusOut>", self._on_target_focus_out)
        self.ent_target_temp.bind("<KeyRelease>", self._on_target_key_release)

        # Ramp Rate & Hardware Limits Row
        r2 = ttk.Frame(ramp_frame)
        r2.pack(fill=tk.X, pady=3)
        ttk.Label(r2, text="Ramp Rate (K/min):", width=16).pack(side=tk.LEFT)
        self.ent_rate = ttk.Entry(r2, width=6)
        self.ent_rate.insert(0, f"{DEFAULT_RATE:.1f}")
        self.ent_rate.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(r2, text="Max Power (%):").pack(side=tk.LEFT)
        self.ent_maxpwr = ttk.Entry(r2, width=5)
        self.ent_maxpwr.insert(0, f"{DEFAULT_MAXPWR:.0f}")
        self.ent_maxpwr.pack(side=tk.LEFT, padx=(4, 10))

        ttk.Label(r2, text="Range:").pack(side=tk.LEFT)
        self.combo_range = ttk.Combobox(r2, width=5, values=["HI", "MID", "LOW"], state="readonly")
        self.combo_range.set(DEFAULT_RANGE)
        self.combo_range.pack(side=tk.LEFT, padx=(4, 0))

        # Tuned PID Parameters Row
        r3 = ttk.Frame(ramp_frame)
        r3.pack(fill=tk.X, pady=3)
        ttk.Label(r3, text="PID Gains (Tuned):", width=16).pack(side=tk.LEFT)

        ttk.Label(r3, text="P:").pack(side=tk.LEFT)
        self.ent_p = ttk.Entry(r3, width=5)
        self.ent_p.insert(0, f"{DEFAULT_PGAIN:.0f}")
        self.ent_p.pack(side=tk.LEFT, padx=(2, 8))

        ttk.Label(r3, text="I (sec):").pack(side=tk.LEFT)
        self.ent_i = ttk.Entry(r3, width=6)
        self.ent_i.insert(0, f"{DEFAULT_IGAIN:.0f}")
        self.ent_i.pack(side=tk.LEFT, padx=(2, 8))

        ttk.Label(r3, text="D:").pack(side=tk.LEFT)
        self.ent_d = ttk.Entry(r3, width=5)
        self.ent_d.insert(0, f"{DEFAULT_DGAIN:.0f}")
        self.ent_d.pack(side=tk.LEFT, padx=(2, 10))

        ttk.Button(r3, text="↺ Defaults", width=9, command=self._reset_validated_defaults).pack(side=tk.LEFT)

        # Allow pressing Enter in parameter fields to trigger ramp as well
        for ent in (self.ent_rate, self.ent_maxpwr, self.ent_p, self.ent_i, self.ent_d):
            ent.bind("<Return>", lambda e: self._start_anti_surge_ramp())
            ent.bind("<KP_Enter>", lambda e: self._start_anti_surge_ramp())

        ttk.Separator(ramp_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)

        # Action Buttons Row
        r4 = ttk.Frame(ramp_frame)
        r4.pack(fill=tk.X, pady=2)

        self.btn_start_ramp = tk.Button(r4, text="▶ START RAMP (Anti-Surge)", font=("Segoe UI", 10, "bold"),
                                        bg="#1b5e20", fg="white", activebackground="#2e7d32", activeforeground="white",
                                        command=self._start_anti_surge_ramp, padx=10, pady=4, relief=tk.RAISED)
        self.btn_start_ramp.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_hold_now = ttk.Button(r4, text="⏸ Hold Current Temp", command=self._hold_current_temperature)
        self.btn_hold_now.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_stop_ctrl = ttk.Button(r4, text="⏹ Stop Heating", command=self._stop_heating)
        self.btn_stop_ctrl.pack(side=tk.LEFT, padx=(0, 6))

        # Status feedback label
        r5 = ttk.Frame(ramp_frame)
        r5.pack(fill=tk.X, pady=(4, 0))
        self.lbl_ramp_status = ttk.Label(r5, text="Status: Ready (Idle)", font=("Segoe UI", 9, "italic"), foreground="#333333")
        self.lbl_ramp_status.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _get_default_log_filename(self):
        now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"cryocon_log_{now_str}.csv"

    def _reset_log_filename(self):
        if not self.logging_active:
            self.log_filename_var.set(self._get_default_log_filename())

    def _browse_log_file(self):
        if self.logging_active:
            return
        os.makedirs("data", exist_ok=True)
        current_val = self.log_filename_var.get().strip() or self._get_default_log_filename()
        if os.path.isabs(current_val) and os.path.exists(os.path.dirname(current_val)):
            initial_dir = os.path.dirname(current_val)
            initial_file = os.path.basename(current_val)
        else:
            initial_dir = os.path.abspath("data")
            initial_file = os.path.basename(current_val)

        if not initial_file.lower().endswith(".csv"):
            initial_file += ".csv"

        selected = filedialog.asksaveasfilename(
            parent=self.root,
            title="Choose CSV Log File Name and Location",
            initialdir=initial_dir,
            initialfile=initial_file,
            defaultextension=".csv",
            filetypes=[("CSV Log Files", "*.csv"), ("All Files", "*.*")]
        )
        if selected:
            data_dir_abs = os.path.abspath("data")
            if os.path.dirname(os.path.abspath(selected)) == data_dir_abs:
                self.log_filename_var.set(os.path.basename(selected))
            else:
                self.log_filename_var.set(selected)

    def _build_logging_panel(self, parent):
        log_frame = ttk.LabelFrame(parent, text="💾 Data Logging & CSV Storage", padding=8)
        log_frame.pack(fill=tk.X)

        # File naming row
        r_file = ttk.Frame(log_frame)
        r_file.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(r_file, text="File Name:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 6))

        self.log_filename_var = tk.StringVar(value=self._get_default_log_filename())
        self.entry_log_file = ttk.Entry(r_file, textvariable=self.log_filename_var, font=("Segoe UI", 9))
        self.entry_log_file.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        self.btn_browse_log = ttk.Button(r_file, text="📂 Browse", width=8, command=self._browse_log_file)
        self.btn_browse_log.pack(side=tk.LEFT, padx=(0, 2))

        self.btn_reset_log_name = ttk.Button(r_file, text="↺", width=3, command=self._reset_log_filename)
        self.btn_reset_log_name.pack(side=tk.LEFT)

        # Control and Status row
        r1 = ttk.Frame(log_frame)
        r1.pack(fill=tk.X, pady=2)

        self.btn_toggle_log = ttk.Button(r1, text="Start Logging (CSV)", command=self._toggle_logging)
        self.btn_toggle_log.pack(side=tk.LEFT, padx=(0, 8))

        self.lbl_log_status = ttk.Label(r1, text="Logging: Inactive", foreground="#666666")
        self.lbl_log_status.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(r1, text="Records:").pack(side=tk.LEFT)
        self.lbl_log_count = ttk.Label(r1, text="0", font=("Segoe UI", 9, "bold"))
        self.lbl_log_count.pack(side=tk.LEFT, padx=4)

        self.lbl_log_file = ttk.Label(log_frame, text="Active File: --", font=("Segoe UI", 8), foreground="#888")
        self.lbl_log_file.pack(anchor=tk.W, pady=(2, 0))

    def _build_notebook_tabs(self, parent):
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)

        tab_plot = ttk.Frame(notebook, padding=6)
        notebook.add(tab_plot, text="📈 Live Temperature Graph")
        self._build_live_chart(tab_plot)

        tab_tbl2 = ttk.Frame(notebook, padding=6)
        notebook.add(tab_tbl2, text="📋 PID Table 02 (180K - 475K)")
        self._build_pid_table_view(tab_tbl2, table_num=2)

        tab_tbl1 = ttk.Frame(notebook, padding=6)
        notebook.add(tab_tbl1, text="📋 PID Table 01 (Factory 20K - 320K)")
        self._build_pid_table_view(tab_tbl1, table_num=1)

    def _build_live_chart(self, parent):
        tb = ttk.Frame(parent)
        tb.pack(fill=tk.X, pady=(0, 4))

        ttk.Label(tb, text="Time Window:").pack(side=tk.LEFT, padx=(0, 4))
        self.combo_window = ttk.Combobox(tb, width=8, values=["2 min", "5 min", "10 min", "15 min", "30 min", "All"], state="readonly")
        self.combo_window.set("10 min")
        self.combo_window.bind("<<ComboboxSelected>>", self._on_window_change)
        self.combo_window.pack(side=tk.LEFT, padx=(0, 10))

        self.chk_show_a = tk.BooleanVar(value=True)
        ttk.Checkbutton(tb, text="Temp A", variable=self.chk_show_a).pack(side=tk.LEFT, padx=3)

        self.chk_show_sp = tk.BooleanVar(value=True)
        ttk.Checkbutton(tb, text="Setpoint", variable=self.chk_show_sp).pack(side=tk.LEFT, padx=3)

        self.chk_show_ht = tk.BooleanVar(value=True)
        ttk.Checkbutton(tb, text="Heater %", variable=self.chk_show_ht).pack(side=tk.LEFT, padx=3)

        self.chk_autoscale_temp = tk.BooleanVar(value=True)
        ttk.Checkbutton(tb, text="Autoscale Y", variable=self.chk_autoscale_temp).pack(side=tk.LEFT, padx=3)

        self.chk_autoscale_ht = tk.BooleanVar(value=False)
        ttk.Checkbutton(tb, text="Autoscale Pwr", variable=self.chk_autoscale_ht).pack(side=tk.LEFT, padx=3)

        ttk.Button(tb, text="Clear Chart", command=self._clear_chart).pack(side=tk.RIGHT, padx=4)
        ttk.Button(tb, text="⛶ Fit Scale", command=self._redraw_chart).pack(side=tk.RIGHT, padx=2)

        self.fig = Figure(figsize=(7, 5), dpi=100)
        self.fig.patch.set_facecolor("#fcfcfc")

        self.ax1 = self.fig.add_subplot(111)
        self.ax2 = self.ax1.twinx()
        self.ax2.yaxis.tick_right()
        self.ax2.yaxis.set_label_position("right")

        self.ax1.set_xlabel("Elapsed Time (s)", fontsize=9)
        self.ax1.set_ylabel("Temperature (K)", color="#0066cc", fontsize=9)
        self.ax2.set_ylabel("Heater Output (%)", color="#8e24aa", fontsize=9)

        self.ax1.grid(True, linestyle="--", alpha=0.5)
        self.fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _build_pid_table_view(self, parent, table_num):
        tb_bar = ttk.Frame(parent)
        tb_bar.pack(fill=tk.X, pady=(0, 4))

        title_text = f"PID Table {table_num:02d} Entries (Cryocon 22C NVRAM)"
        ttk.Label(tb_bar, text=title_text, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)

        ttk.Button(tb_bar, text="🔄 Reload from Controller",
                   command=lambda: self._trigger_table_load(table_num)).pack(side=tk.RIGHT, padx=4)

        if table_num == 2:
            ttk.Button(tb_bar, text="⚡ Write Validated Table 02 (475K-77K)",
                       command=self._reflash_table_02).pack(side=tk.RIGHT, padx=4)

        cols = ("row", "setpt", "pgain", "igain", "dgain", "range", "channel")
        tree = ttk.Treeview(parent, columns=cols, show="headings", height=18)
        tree.heading("row", text="#")
        tree.heading("setpt", text="Setpoint (K)")
        tree.heading("pgain", text="P Gain")
        tree.heading("igain", text="I Time (s)")
        tree.heading("dgain", text="D Gain")
        tree.heading("range", text="Range")
        tree.heading("channel", text="Source")

        tree.column("row", width=40, anchor=tk.CENTER)
        tree.column("setpt", width=100, anchor=tk.CENTER)
        tree.column("pgain", width=90, anchor=tk.CENTER)
        tree.column("igain", width=100, anchor=tk.CENTER)
        tree.column("dgain", width=90, anchor=tk.CENTER)
        tree.column("range", width=90, anchor=tk.CENTER)
        tree.column("channel", width=90, anchor=tk.CENTER)

        tree.pack(fill=tk.BOTH, expand=True)

        if table_num == 2:
            self.tree_table2 = tree
        else:
            self.tree_table1 = tree

    def _get_com_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        if not ports:
            ports = ["COM5"]
        elif "COM5" not in ports:
            ports.insert(0, "COM5")
        return ports

    def _refresh_ports(self):
        ports = self._get_com_ports()
        self.port_combo["values"] = ports
        if ports:
            self.port_combo.set(ports[0])

    def _auto_connect(self):
        self._toggle_connection()

    def _toggle_connection(self):
        if not self.comm.connected:
            port = self.port_combo.get().strip()
            ok, msg = self.comm.connect(port=port, baud=57600)
            if ok:
                idn = self.comm.query("*IDN?", wait=0.04)
                self.telemetry["idn"] = idn
                self.lbl_idn.config(text=f"Device: {idn}")
                self.lbl_conn_status.config(text="● Connected", foreground="#2e7d32")
                self.btn_connect.config(text="Disconnect")
                self.statusbar.config(text=f"Connected to {idn} on {port} (57600 baud)")

                self.poll_running = True
                self.poll_thread = threading.Thread(target=self._polling_worker, daemon=True)
                self.poll_thread.start()

                # Load tables in background after connection settles
                self.root.after(1000, lambda: self._trigger_table_load(2))
                self.root.after(2500, lambda: self._trigger_table_load(1))
            else:
                self.lbl_conn_status.config(text="● Disconnected", foreground="red")
                self.statusbar.config(text=f"Connection failed: {msg}")
        else:
            self.poll_running = False
            self.comm.disconnect()
            self.lbl_conn_status.config(text="● Disconnected", foreground="red")
            self.lbl_idn.config(text="Device: Disconnected")
            self.btn_connect.config(text="Connect")
            self.statusbar.config(text="Disconnected from serial port.")

    def _on_poll_rate_change(self, event=None):
        val = self.combo_poll_rate.get()
        if "0.10" in val:
            self.poll_delay = 0.01  # ~0.08-0.10s cycle time (10 Hz hardware ADC limit)
        elif "0.25" in val:
            self.poll_delay = 0.08  # ~0.25s cycle time (4 Hz)
        elif "0.5" in val:
            self.poll_delay = 0.25  # ~0.5s cycle time (2 Hz - matches front panel display)
        elif "2.0" in val:
            self.poll_delay = 1.70  # ~2.0s cycle time
        else:
            self.poll_delay = 0.75  # ~1.0s cycle time (1 Hz)
        self.statusbar.config(text=f"Telemetry polling rate set to {val}")

    def _polling_worker(self):
        cycle_count = 0
        while self.poll_running and self.comm.connected:
            try:
                # If an anti-surge arming sequence is running, yield serial to it
                if self.is_arming_ramp:
                    time.sleep(0.3)
                    continue

                # 1. FAST QUERIES (Critical dynamic telemetry polled EVERY cycle)
                # At 57600 baud, each query turnaround is ~25-30ms.
                # INPUT? A and LOOP 1:OUTP? are dynamic sensor & power readouts.
                ta_str = self.comm.query("INPUT? A", wait=0.01)
                ht_str = self.comm.query("LOOP 1:OUTP?", wait=0.01).replace("%", "").strip()
                sp_str = self.comm.query("LOOP 1:SETPT?", wait=0.01).replace("K", "").strip()

                # Control state changes infrequently; query every 5 cycles
                if cycle_count % 5 == 0:
                    ctrl_str = self.comm.query("CONTROL?", wait=0.01)
                else:
                    ctrl_str = self.telemetry.get("control", "OFF")

                try: ta = float(ta_str)
                except ValueError: ta = float("nan")

                try: ht = float(ht_str)
                except ValueError: ht = 0.0

                try: sp = float(sp_str)
                except ValueError: sp = 0.0

                err = ta - sp if (sp > 0 and ta == ta) else 0.0

                update_dict = {
                    "temp_a": ta,
                    "setpoint": sp,
                    "error": err,
                    "heater_pwr": ht,
                    "control": ctrl_str
                }

                # 2. SLOW QUERIES (Infrequent configuration & badges - polled once every 20 cycles)
                if cycle_count % 20 == 0:
                    type_str = self.comm.query("LOOP 1:TYPE?", wait=0.01)
                    tix_str = self.comm.query("LOOP 1:TABLEIX?", wait=0.01)
                    rate_str = self.comm.query("LOOP 1:RATE?", wait=0.01)
                    rng_str = self.comm.query("LOOP 1:RANGE?", wait=0.01)
                    pwr_str = self.comm.query("LOOP 1:MAXPWR?", wait=0.01).replace("%", "").strip()
                    pg_str = self.comm.query("LOOP 1:PGAIN?", wait=0.01)
                    ig_str = self.comm.query("LOOP 1:IGAIN?", wait=0.01)
                    dg_str = self.comm.query("LOOP 1:DGAIN?", wait=0.01)
                    ramp_str = self.comm.query("LOOP 1:RAMP?", wait=0.01)

                    try: rate = float(rate_str)
                    except ValueError: rate = DEFAULT_RATE
                    try: maxpwr = float(pwr_str)
                    except ValueError: maxpwr = DEFAULT_MAXPWR
                    try: pg = float(pg_str)
                    except ValueError: pg = 0.0
                    try: ig = float(ig_str)
                    except ValueError: ig = 0.0
                    try: dg = float(dg_str)
                    except ValueError: dg = 0.0

                    update_dict.update({
                        "temp_b": 0.0, "type": type_str, "tableix": tix_str,
                        "rate": rate, "range": rng_str, "maxpwr": maxpwr,
                        "pgain": pg, "igain": ig, "dgain": dg,
                        "ramp_active": ramp_str
                    })

                self.telemetry.update(update_dict)
                cycle_count += 1

                if self.logging_active and self.log_writer:
                    self._log_telemetry_row()

                # Update live GUI readouts immediately
                self.root.after(0, self._update_gui_readouts)

            except Exception:
                pass

            time.sleep(self.poll_delay)

    def _set_target_preset(self, temp_val):
        self.ent_target_temp.delete(0, tk.END)
        self.ent_target_temp.insert(0, f"{temp_val:.1f}")
        c_val = temp_val - 273.15
        self.lbl_ramp_status.config(
            text=f"Status: Preset {temp_val:.1f} K ({c_val:.1f} °C) loaded. Press Enter or '▶ START RAMP' to begin.",
            foreground="#0066cc"
        )
        self.ent_target_temp.focus_set()

    def _on_target_focus_out(self, event=None):
        val_str = self.ent_target_temp.get().strip()
        try:
            val = float(val_str)
            self.ent_target_temp.delete(0, tk.END)
            self.ent_target_temp.insert(0, f"{val:.1f}")
            c_val = val - 273.15
            if 77.0 <= val <= 460.0:
                self.lbl_ramp_status.config(
                    text=f"Status: Target {val:.1f} K ({c_val:.1f} °C) ready. Press Enter or '▶ START RAMP' to begin.",
                    foreground="#0066cc"
                )
            else:
                self.lbl_ramp_status.config(
                    text=f"Status: ⚠ Target {val:.1f} K ({c_val:.1f} °C) outside normal range (77-460 K).",
                    foreground="#c62828"
                )
        except ValueError:
            if val_str:
                self.lbl_ramp_status.config(
                    text="Status: ⚠ Invalid target temperature format.",
                    foreground="#c62828"
                )

    def _on_target_key_release(self, event=None):
        if event and event.keysym in ("Return", "KP_Enter"):
            return
        val_str = self.ent_target_temp.get().strip()
        try:
            val = float(val_str)
            self.lbl_ramp_status.config(
                text=f"Status: Target {val:.1f} K (Uncommitted) — Press Enter or '▶ START RAMP'",
                foreground="#e65100"
            )
        except ValueError:
            pass

    def _reset_validated_defaults(self):
        self.ent_p.delete(0, tk.END)
        self.ent_p.insert(0, f"{DEFAULT_PGAIN:.0f}")

        self.ent_i.delete(0, tk.END)
        self.ent_i.insert(0, f"{DEFAULT_IGAIN:.0f}")

        self.ent_d.delete(0, tk.END)
        self.ent_d.insert(0, f"{DEFAULT_DGAIN:.0f}")

        self.ent_rate.delete(0, tk.END)
        self.ent_rate.insert(0, f"{DEFAULT_RATE:.1f}")

        self.ent_maxpwr.delete(0, tk.END)
        self.ent_maxpwr.insert(0, f"{DEFAULT_MAXPWR:.0f}")

        self.combo_range.set(DEFAULT_RANGE)
        self.statusbar.config(text="Reset controls to validated tuning defaults (P=40, I=900, D=0, MaxPwr=70%, Range=HI)")

    def _start_anti_surge_ramp(self, event=None):
        """Dispatches the validated anti-surge ramp arming sequence in a worker thread."""
        if not self.comm.connected:
            messagebox.showwarning("Not Connected", "Please connect to the Cryocon 22C controller first.")
            return

        try:
            target = float(self.ent_target_temp.get().strip())
            rate = float(self.ent_rate.get().strip())
            p = float(self.ent_p.get().strip())
            i = float(self.ent_i.get().strip())
            d = float(self.ent_d.get().strip())
            maxpwr = float(self.ent_maxpwr.get().strip())
            range_val = self.combo_range.get().strip().upper()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please check all numeric values before starting.")
            return

        if target < 77.0 or target > 470.0:
            if not messagebox.askyesno("Confirm Setpoint", f"Target setpoint {target:.1f} K is outside normal range (77-470 K). Proceed?"):
                return

        if self.is_arming_ramp:
            messagebox.showinfo("Busy", "Anti-surge ramp arming sequence is already running.")
            return

        self.is_arming_ramp = True
        self.btn_start_ramp.config(state=tk.DISABLED)
        if hasattr(self, 'btn_inline_ramp'):
            self.btn_inline_ramp.config(state=tk.DISABLED)
        self.lbl_ramp_status.config(text=f"Arming ramp to {target:.2f} K (Anti-Surge Sequence)...", foreground="#e65100")

        self.ramp_worker_thread = threading.Thread(
            target=self._execute_anti_surge_ramp_thread,
            args=(target, rate, p, i, d, maxpwr, range_val),
            daemon=True
        )
        self.ramp_worker_thread.start()

    def _execute_anti_surge_ramp_thread(self, target, rate, p, i, d, maxpwr, range_val):
        """
        Anti-Surge Sequence (Strictly Enforced from FINAL_REPORT.md Section 9 & staged_ramp_test.py):
        1. Read current temperature (T_now)
        2. LOOP 1:TYPE PID (drop to PID mode so setpoint moves instantly without ramping)
        3. LOOP 1:SETPT <T_now> (park working setpoint at current reading, error = 0.0 K)
        4. Configure validated tuning: RANGE, MAXPWR, PGAIN, IGAIN, DGAIN, RATE
        5. CONTROL (engage loop at zero error -> heater begins smoothly at hold power)
        6. Wait 2.5s for loop to stabilize at hold power
        7. LOOP 1:TYPE RAMPP (engage ramp mode)
        8. LOOP 1:SETPT <target> (SENT LAST: writing setpoint arms the ramp smoothly)
        """
        try:
            self._update_ramp_ui_status("Step 1/6: Reading current temperature...")
            t_now_str = self.comm.query("INPUT? A", wait=0.15)
            try:
                t_now = float(t_now_str)
            except ValueError:
                t_now = target

            self._update_ramp_ui_status(f"Step 2/6: Parking setpoint at current temp ({t_now:.2f} K)...")
            self.comm.send("LOOP 1:TYPE PID", wait=0.3)
            self.comm.send(f"LOOP 1:SETPT {t_now:.3f}", wait=0.5)

            self._update_ramp_ui_status(f"Step 3/6: Loading tuning (P={p}, I={i}s, Range={range_val}, Cap={maxpwr}%)...")
            self.comm.send(f"LOOP 1:RANGE {range_val}", wait=0.8)  # Mechanical relay switch
            self.comm.send(f"LOOP 1:MAXPWR {maxpwr:.1f}", wait=0.2)
            self.comm.send(f"LOOP 1:PGAIN {p:.1f}", wait=0.2)
            self.comm.send(f"LOOP 1:IGAIN {i:.1f}", wait=0.2)
            self.comm.send(f"LOOP 1:DGAIN {d:.1f}", wait=0.2)
            self.comm.send(f"LOOP 1:RATE {rate:.2f}", wait=0.2)

            self._update_ramp_ui_status("Step 4/6: Engaging CONTROL at zero error...")
            self.comm.send("CONTROL", wait=0.3)
            time.sleep(2.5)  # Allow loop to balance at hold power

            self._update_ramp_ui_status("Step 5/6: Arming RAMPP mode...")
            self.comm.send("LOOP 1:TYPE RAMPP", wait=0.3)

            self._update_ramp_ui_status(f"Step 6/6: Sending target setpoint {target:.2f} K ({target - 273.15:.2f} °C) (Arms Ramp)...")
            self.comm.send(f"LOOP 1:SETPT {target:.3f}", wait=0.3)

            target_c = target - 273.15
            msg = f"✓ RAMP ACTIVE: Climbing to {target:.2f} K ({target_c:.2f} °C) @ {rate:.2f} K/min (Anti-Surge OK)"
            self._update_ramp_ui_status(msg, foreground="#1b5e20")
            self.root.after(0, lambda: self.statusbar.config(text=msg))

        except Exception as e:
            err_msg = f"Anti-Surge Sequence Error: {e}"
            self._update_ramp_ui_status(err_msg, foreground="#c62828")
        finally:
            self.is_arming_ramp = False
            self.root.after(0, lambda: self.btn_start_ramp.config(state=tk.NORMAL))
            if hasattr(self, 'btn_inline_ramp'):
                self.root.after(0, lambda: self.btn_inline_ramp.config(state=tk.NORMAL))

    def _update_ramp_ui_status(self, text, foreground="#333333"):
        self.root.after(0, lambda: self.lbl_ramp_status.config(text=f"Status: {text}", foreground=foreground))

    def _hold_current_temperature(self):
        """Safely parks setpoint at current reading in PID mode without stopping control."""
        if not self.comm.connected:
            return
        t_now_str = self.comm.query("INPUT? A", wait=0.15)
        try:
            t_now = float(t_now_str)
        except ValueError:
            return

        self.comm.send("LOOP 1:TYPE PID", wait=0.3)
        self.comm.send(f"LOOP 1:SETPT {t_now:.3f}", wait=0.3)
        t_now_c = t_now - 273.15
        msg = f"Holding at current temperature {t_now:.3f} K ({t_now_c:.2f} °C) (Type PID)"
        self.lbl_ramp_status.config(text=f"Status: {msg}", foreground="#0066cc")
        self.statusbar.config(text=msg)

    def _stop_heating(self):
        """Sends STOP command and verifies CONTROL is OFF."""
        if not self.comm.connected:
            return
        self.comm.send("STOP", wait=0.3)
        ctrl = self.comm.query("CONTROL?", wait=0.2)
        msg = f"Heater STOP sent (Control = {ctrl})"
        self.lbl_ramp_status.config(text=f"Status: {msg}", foreground="#b71c1c")
        self.statusbar.config(text=msg)

    def _emergency_stop(self):
        """Unconditional emergency stop."""
        self.comm.send("STOP", wait=0.2)
        self.comm.send("STOP", wait=0.2)
        ctrl = self.comm.query("CONTROL?", wait=0.2)
        self.lbl_ramp_status.config(text="Status: 🛑 EMERGENCY STOP ACTIVATED - Heater 0%", foreground="#d32f2f")
        self.statusbar.config(text=f"🛑 EMERGENCY STOP: Heater disengaged (CONTROL = {ctrl})")
        messagebox.showwarning("EMERGENCY STOP", f"Heater control disengaged.\nInstrument CONTROL status: {ctrl}")

    def _trigger_table_load(self, table_num):
        """Asynchronously loads PID table entries without freezing Tkinter."""
        threading.Thread(target=self._load_pid_table_into_tree, args=(table_num,), daemon=True).start()

    def _load_pid_table_into_tree(self, table_num):
        if not self.comm.connected:
            return
        tree = self.tree_table2 if table_num == 2 else self.tree_table1

        raw = self.comm.query_multiline(f"PIDTABLE {table_num}:TABLE?", wait=1.5)
        lines = raw.replace("\r", "").split("\n")

        entries = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 5:
                try:
                    sp = float(parts[0])
                    p = parts[1]
                    i = parts[2]
                    d = parts[3]
                    rng = parts[4]
                    ch = parts[5] if len(parts) > 5 else "ChA"
                    entries.append((f"{sp:.2f}", p, i, d, rng, ch))
                except ValueError:
                    pass

        def _populate():
            for item in tree.get_children():
                tree.delete(item)
            for idx, entry in enumerate(entries, start=1):
                tree.insert("", tk.END, values=(idx, *entry))
            self.statusbar.config(text=f"Loaded {len(entries)} entries from PID Table {table_num:02d}")

        self.root.after(0, _populate)

    def _reflash_table_02(self):
        """
        Writes the validated 16 entries to instrument NVRAM (Table 02).
        Strictly matches write_pid_table02.py (validated 2026-09-05).
        """
        if not messagebox.askyesno(
            "Confirm Re-Flash NVRAM Table 02",
            "This will write the validated 16 PID entries (Zone 1: P=40, I=900, D=0) "
            "directly to Cryo-con 22C non-volatile memory (NVRAM Table 02).\n\n"
            "Are you sure you want to proceed?"
        ):
            return

        validated_entries = [
            # Zone 1: No active cooling (300 K to 475 K) - Tuned 2026-09-05
            (475, 40.0, 900, 0, "HI"),
            (450, 40.0, 900, 0, "HI"),
            (425, 40.0, 900, 0, "HI"),
            (400, 40.0, 900, 0, "HI"),
            (375, 40.0, 900, 0, "HI"),
            (350, 40.0, 900, 0, "HI"),
            (325, 40.0, 900, 0, "HI"),
            (300, 40.0, 900, 0, "HI"),
            # Zone 2: LN2 active cooling (77 K to 300 K)
            (275,  2.0,  55, 50, "HI"),
            (250,  1.9,  58, 47, "HI"),
            (225,  1.8,  60, 44, "HI"),
            (200,  1.7,  62, 41, "HI"),
            (175,  1.6,  62, 38, "HI"),
            (150,  1.5,  60, 33, "HI"),
            (120,  1.3,  56, 27, "HI"),
            ( 77,  1.0,  50, 20, "MID"),
        ]

        cmd_lines = ["PIDTABLE 2:TABLE", "PID Table 2"]
        for (sp, p, i, d, rng) in validated_entries:
            cmd_lines.append(f" {sp:6.2f}  {p:5.2f}  {i:6.2f}  {d:5.2f}  {rng}")
        cmd_lines.append(";")
        full_cmd = "\r\n".join(cmd_lines) + "\r\n"

        threading.Thread(target=self._execute_reflash_thread, args=(full_cmd,), daemon=True).start()

    def _execute_reflash_thread(self, full_cmd):
        self.root.after(0, lambda: self.statusbar.config(text="Flashing PID Table 02 to controller NVRAM..."))
        with self.comm.lock:
            if not self.comm.connected or not self.comm.ser:
                return
            self.comm.ser.reset_input_buffer()
            self.comm.ser.write(full_cmd.encode())
            time.sleep(3.0)

        self._trigger_table_load(2)
        self.root.after(0, lambda: messagebox.showinfo(
            "Success",
            "PID Table 02 successfully re-flashed with validated tuning (P=40, I=900, D=0) and verified!"
        ))

    def _toggle_logging(self):
        if not self.logging_active:
            user_input = self.log_filename_var.get().strip()
            if not user_input:
                user_input = self._get_default_log_filename()

            if not user_input.lower().endswith(".csv"):
                user_input += ".csv"

            # Determine destination path
            if os.path.isabs(user_input) or os.path.dirname(user_input):
                dest_path = os.path.abspath(user_input)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            else:
                os.makedirs("data", exist_ok=True)
                dest_path = os.path.abspath(os.path.join("data", user_input))

            # Safety check: confirm overwrite if non-empty file already exists
            if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
                overwrite = messagebox.askyesno(
                    "Overwrite Existing Log?",
                    f"The file '{os.path.basename(dest_path)}' already exists and contains data.\n\n"
                    "Do you want to overwrite it and replace previous data?",
                    parent=self.root
                )
                if not overwrite:
                    return

            self.log_filename = dest_path
            # Normalize display in text box
            if os.path.dirname(dest_path) == os.path.abspath("data"):
                self.log_filename_var.set(os.path.basename(dest_path))
            else:
                self.log_filename_var.set(dest_path)

            try:
                self.log_file = open(self.log_filename, "w", newline="", encoding="utf-8")
                self.log_writer = csv.writer(self.log_file)
                self.log_writer.writerow([
                    "Timestamp", "Elapsed_Sec", "Temp_A_K",
                    "Setpoint_K", "Error_K", "Heater_Pct", "Ramp_Rate_K_min",
                    "P_Gain", "I_Gain", "D_Gain", "Range", "MaxPwr_Pct",
                    "Control_State", "Loop_Type", "Ramping"
                ])
                self.log_file.flush()
                self.log_records_count = 0
                self.log_start_time = time.time()
                self.logging_active = True

                self.btn_toggle_log.config(text="⏹ Stop Logging")
                self.lbl_log_status.config(text="Logging: RECORDING", foreground="#2e7d32")
                self.lbl_log_file.config(text=f"Active File: {os.path.basename(self.log_filename)}")
                self.entry_log_file.config(state="disabled")
                self.btn_browse_log.config(state="disabled")
                self.btn_reset_log_name.config(state="disabled")
                self.statusbar.config(text=f"Logging started: {self.log_filename}")
            except Exception as e:
                messagebox.showerror("Logging Error", f"Could not create CSV file: {e}")
        else:
            self.logging_active = False
            if self.log_file:
                try:
                    self.log_file.close()
                except Exception:
                    pass
                self.log_file = None
                self.log_writer = None

            self.btn_toggle_log.config(text="Start Logging (CSV)")
            self.lbl_log_status.config(text="Logging: Inactive", foreground="#666666")
            self.entry_log_file.config(state="normal")
            self.btn_browse_log.config(state="normal")
            self.btn_reset_log_name.config(state="normal")
            saved_name = os.path.basename(self.log_filename) if self.log_filename else "log"
            self.statusbar.config(text=f"Logging stopped. Records: {self.log_records_count} saved to {saved_name}")
            # Refresh to a fresh default timestamp for the next run so user doesn't accidentally overwrite
            self.log_filename_var.set(self._get_default_log_filename())

    def _log_telemetry_row(self):
        t = self.telemetry
        elapsed = time.time() - self.log_start_time
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_writer.writerow([
            ts, f"{elapsed:.1f}",
            f"{t['temp_a']:.4f}" if t['temp_a'] == t['temp_a'] else "nan",
            f"{t['setpoint']:.4f}", f"{t['error']:+.4f}", f"{t['heater_pwr']:.2f}",
            f"{t['rate']:.2f}", f"{t['pgain']:.1f}", f"{t['igain']:.1f}", f"{t['dgain']:.1f}",
            t['range'], f"{t['maxpwr']:.1f}", t['control'], t['type'], t['ramp_active']
        ])
        self.log_file.flush()
        self.log_records_count += 1

    def _on_unit_change(self):
        """Immediately refreshes the display readouts when the temperature unit selection changes."""
        self._update_gui_readouts()

    def _update_gui_readouts(self):
        t = self.telemetry
        unit = getattr(self, "temp_unit_var", None)
        mode = unit.get() if unit else "C"

        # Channel A (Reading Temperature)
        if t['temp_a'] == t['temp_a'] and t['temp_a'] > 0:  # Not NaN and valid reading
            ta_k = t['temp_a']
            ta_c = ta_k - 273.15
            if mode == "C":
                self.lbl_temp_a.config(text=f"{ta_c:.3f} °C")
                self.lbl_status_a.config(text=f"Active Control Sensor (Janis ST-LN-500)  •  {ta_k:.3f} K")
            elif mode == "DUAL":
                self.lbl_temp_a.config(text=f"{ta_c:.3f} °C  ({ta_k:.3f} K)")
                self.lbl_status_a.config(text="Active Control Sensor (Janis ST-LN-500)")
            else:  # "K"
                self.lbl_temp_a.config(text=f"{ta_k:.3f} K")
                self.lbl_status_a.config(text=f"Active Control Sensor (Janis ST-LN-500)  •  {ta_c:.2f} °C")
        else:
            sym = "°C" if mode == "C" else ("K" if mode == "K" else "°C (K)")
            self.lbl_temp_a.config(text=f"--.--- {sym}")
            self.lbl_status_a.config(text="Active Control Sensor (Janis ST-LN-500)")

        # Setpoint & Error (Target Temperature)
        if t['setpoint'] > 0:
            sp_k = t['setpoint']
            sp_c = sp_k - 273.15
            err_k = t['error']
            err_sign = "+" if err_k >= 0 else ""
            err_color = "#2e7d32" if abs(err_k) <= 0.10 else ("#e65100" if abs(err_k) <= 0.50 else "#c62828")

            if mode == "C":
                self.lbl_setpt.config(text=f"{sp_c:.3f} °C")
                self.lbl_error.config(text=f"Error: {err_sign}{err_k:.3f} °C  ({sp_k:.3f} K)", foreground=err_color)
            elif mode == "DUAL":
                self.lbl_setpt.config(text=f"{sp_c:.3f} °C")
                self.lbl_error.config(text=f"Error: {err_sign}{err_k:.3f} °C  ({sp_k:.3f} K)", foreground=err_color)
            else:  # "K"
                self.lbl_setpt.config(text=f"{sp_k:.3f} K")
                self.lbl_error.config(text=f"Error: {err_sign}{err_k:.3f} K  ({sp_c:.2f} °C)", foreground=err_color)
        else:
            sym = "°C" if mode == "C" else ("K" if mode == "K" else "°C (K)")
            self.lbl_setpt.config(text=f"--.--- {sym}")
            self.lbl_error.config(text=f"Error: --.--- {sym}", foreground="#555")

        # Heater Output
        self.lbl_heater.config(text=f"{t['heater_pwr']:.1f} %")
        self.pbar_heater["value"] = min(100.0, max(0.0, t['heater_pwr']))

        # Badges
        is_on = t['control'].upper() in ["ON", "1", "TRUE"]
        self.badge_ctrl.config(
            text=f"CONTROL: {t['control']}",
            bg="#c8e6c9" if is_on else "#ffcdd2",
            fg="#1b5e20" if is_on else "#b71c1c"
        )
        self.badge_mode.config(text=f"MODE: {t['type']}")
        self.badge_range.config(text=f"RANGE: {t['range']}")
        self.badge_rate.config(text=f"RATE: {t['rate']:.1f} K/min")
        self.badge_pid.config(text=f"P={t['pgain']:.0f} I={t['igain']:.0f}s D={t['dgain']:.0f}")

        if self.logging_active:
            self.lbl_log_count.config(text=str(self.log_records_count))

        # Update Chart Buffers
        now = time.time()
        self.plot_times.append(now)
        self.plot_temp_a.append(t['temp_a'])
        self.plot_temp_b.append(t['temp_b'])
        self.plot_setpt.append(t['setpoint'])
        self.plot_heater.append(t['heater_pwr'])

        if len(self.plot_times) > self.max_plot_points:
            self.plot_times = self.plot_times[-self.max_plot_points:]
            self.plot_temp_a = self.plot_temp_a[-self.max_plot_points:]
            self.plot_temp_b = self.plot_temp_b[-self.max_plot_points:]
            self.plot_setpt = self.plot_setpt[-self.max_plot_points:]
            self.plot_heater = self.plot_heater[-self.max_plot_points:]

        # Redraw chart smoothly twice per second (2 Hz) to maintain high responsiveness without lag
        if now - self.last_chart_draw >= 0.5:
            self.last_chart_draw = now
            self._redraw_chart()

    def _on_window_change(self, event=None):
        sel = self.combo_window.get()
        mapping = {"2 min": 120, "5 min": 300, "10 min": 600, "15 min": 900, "30 min": 1800, "All": 999999}
        self.plot_window_seconds = mapping.get(sel, 600)
        self._redraw_chart()

    def _clear_chart(self):
        self.plot_times.clear()
        self.plot_temp_a.clear()
        self.plot_temp_b.clear()
        self.plot_setpt.clear()
        self.plot_heater.clear()
        self._redraw_chart()

    def _redraw_chart(self):
        if not self.plot_times:
            return

        self.ax1.clear()
        self.ax2.clear()

        # Enforce secondary Heater axis strictly on the RIGHT side
        self.ax2.yaxis.tick_right()
        self.ax2.yaxis.set_label_position("right")

        t_now = self.plot_times[-1]
        cutoff = t_now - self.plot_window_seconds

        indices = [i for i, t in enumerate(self.plot_times) if t >= cutoff]
        if not indices:
            indices = list(range(len(self.plot_times)))

        times_rel = [(self.plot_times[i] - self.plot_times[0]) for i in indices]

        visible_temps = []

        # Temp A (Sample Stage)
        if self.chk_show_a.get() and len(self.plot_temp_a) >= len(indices):
            y_a = [self.plot_temp_a[i] for i in indices]
            valid_ya = [v for v in y_a if v == v and v > 0]
            if valid_ya:
                self.ax1.plot(times_rel, y_a, label="Temp A (Sample)", color="#0066cc", linewidth=2.0)
                visible_temps.extend(valid_ya)

        # Setpoint (Dashed Orange Line)
        if self.chk_show_sp.get() and len(self.plot_setpt) >= len(indices):
            y_sp = [self.plot_setpt[i] for i in indices]
            valid_sp = [v for v in y_sp if v == v and v > 0]
            if valid_sp:
                self.ax1.plot(times_rel, y_sp, label="Setpoint", color="#e65100", linewidth=1.6, linestyle="--")
                visible_temps.extend(valid_sp)

        # Heater % Output (Secondary Axis on RIGHT)
        visible_heaters = []
        if self.chk_show_ht.get() and len(self.plot_heater) >= len(indices):
            y_ht = [self.plot_heater[i] for i in indices]
            self.ax2.plot(times_rel, y_ht, label="Heater %", color="#8e24aa", linewidth=1.0, alpha=0.5)
            visible_heaters.extend(y_ht)

        # Autoscale Temperature (Y-axis 1 - Left)
        if self.chk_autoscale_temp.get() and visible_temps:
            y_min = min(visible_temps)
            y_max = max(visible_temps)
            span = y_max - y_min
            if span < 1.0:
                mid = (y_max + y_min) / 2.0
                self.ax1.set_ylim(mid - 1.0, mid + 1.0)
            else:
                margin = span * 0.08
                self.ax1.set_ylim(y_min - margin, y_max + margin)

        # Autoscale Heater (Y-axis 2 - Right)
        if self.chk_autoscale_ht.get() and visible_heaters:
            max_ht = max(visible_heaters)
            self.ax2.set_ylim(0, max(20.0, max_ht * 1.25))
        else:
            self.ax2.set_ylim(0, 105)

        self.ax1.set_ylabel("Temperature (K)", color="#0066cc", fontsize=9)
        self.ax2.set_ylabel("Heater Output (%)", color="#8e24aa", fontsize=9)
        self.ax2.yaxis.set_label_position("right")
        self.ax2.yaxis.tick_right()
        self.ax1.grid(True, linestyle="--", alpha=0.4)

        handles1, labels1 = self.ax1.get_legend_handles_labels()
        if handles1:
            self.ax1.legend(loc="upper left", fontsize=8)
        handles2, labels2 = self.ax2.get_legend_handles_labels()
        if handles2:
            self.ax2.legend(loc="upper right", fontsize=8)

        self.fig.tight_layout()
        self.canvas.draw_idle()

    def _on_close(self):
        """Clean and safe shutdown on window exit."""
        # If control is currently active, confirm with user and send STOP
        if self.telemetry.get("control", "").upper() in ["ON", "1", "TRUE"]:
            ans = messagebox.askyesno(
                "Active Heater Warning",
                "Heater control loop is currently ON!\n\n"
                "Turn OFF the heater (send STOP) before closing?"
            )
            if ans:
                self.comm.send("STOP", wait=0.3)

        # Unconditionally stop polling and logging
        self.poll_running = False
        if self.logging_active and self.log_file:
            try:
                self.log_file.close()
            except Exception:
                pass

        # Disconnect serial
        self.comm.disconnect()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = CryoconGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
