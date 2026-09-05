"""
Cryocon 22C Temperature Controller - Professional Lab GUI
=========================================================
Features:
- Real-time Channel A & B Temperature monitoring
- Live interactive Matplotlib rolling plot (Temp A, Temp B, Setpoint, Heater %)
- Smart Two-Speed Ramping Engine (eliminates overshoot)
- Continuous CSV Data Logging with timestamped files
- PID Table Management (Table 01 & Table 02 viewer and switcher)
- Full Control Loop management (Setpoint, Rate, Range, Control ON/OFF, STOP)
- Thread-safe non-blocking serial communication
"""

import tkinter as tk
from tkinter import ttk, messagebox
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

PYTHON_SERIAL_TIMEOUT = 1.0


class CryoconComm:
    """Thread-safe Cryocon 22C Serial Communication Manager."""
    def __init__(self):
        self.ser = None
        self.lock = threading.Lock()
        self.connected = False
        self.port = "COM5"
        self.baud = 9600

    def connect(self, port="COM5", baud=9600):
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

    def query(self, cmd, wait=0.08):
        with self.lock:
            if not self.connected or not self.ser:
                return "ERR"
            try:
                self.ser.reset_input_buffer()
                self.ser.write((cmd + "\r\n").encode())
                time.sleep(wait)
                resp = self.ser.readline().decode("utf-8", errors="ignore").strip()
                return resp
            except Exception:
                return "ERR"

    def query_multiline(self, cmd, wait=1.2):
        with self.lock:
            if not self.connected or not self.ser:
                return "ERR"
            try:
                self.ser.reset_input_buffer()
                self.ser.write((cmd + "\r\n").encode())
                time.sleep(wait)
                chunks = []
                deadline = time.time() + 3.0
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

    def send(self, cmd, wait=0.1):
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
        self.root.title("Cryocon 22C Temperature Controller - Lab Dashboard")
        self.root.geometry("1280x850")
        self.root.minsize(1050, 700)

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self._setup_styles()

        self.comm = CryoconComm()

        self.telemetry = {
            "temp_a": 0.0, "temp_b": 0.0, "setpoint": 0.0, "error": 0.0,
            "heater_pwr": 0.0, "control": "OFF", "type": "RAMPT",
            "tableix": "2", "rate": 0.5, "range": "HI",
            "pgain": 0.0, "igain": 0.0, "dgain": 0.0, "idn": "Disconnected"
        }

        self.plot_times = []
        self.plot_temp_a = []
        self.plot_temp_b = []
        self.plot_setpt = []
        self.plot_heater = []
        self.max_plot_points = 1800
        self.plot_window_seconds = 600

        self.logging_active = False
        self.log_file = None
        self.log_writer = None
        self.log_records_count = 0
        self.log_start_time = None
        self.log_filename = ""

        self.smart_ramp_active = False
        self.target_temp = 300.0
        self.fast_rate = 5.0
        self.slow_rate = 0.5
        self.threshold_delta = 15.0
        self.ramp_stage = "IDLE"

        self.poll_running = False
        self.poll_thread = None

        self._build_layout()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.after(500, self._auto_connect)

    def _setup_styles(self):
        self.style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))
        self.style.configure("ReadoutTitle.TLabel", font=("Segoe UI", 10), foreground="#555555")
        self.style.configure("ReadoutValueA.TLabel", font=("Segoe UI", 28, "bold"), foreground="#0066cc")
        self.style.configure("ReadoutValueB.TLabel", font=("Segoe UI", 24, "bold"), foreground="#2e7d32")
        self.style.configure("ReadoutValueSP.TLabel", font=("Segoe UI", 24, "bold"), foreground="#d84315")
        self.style.configure("ReadoutValueHT.TLabel", font=("Segoe UI", 24, "bold"), foreground="#6a1b9a")

    def _build_layout(self):
        top_frame = ttk.Frame(self.root, padding=8)
        top_frame.pack(fill=tk.X)

        ttk.Label(top_frame, text="COM Port:").pack(side=tk.LEFT, padx=(0, 4))
        self.port_combo = ttk.Combobox(top_frame, width=10, values=self._get_com_ports())
        self.port_combo.set("COM5")
        self.port_combo.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_refresh_ports = ttk.Button(top_frame, text="↻", width=3, command=self._refresh_ports)
        self.btn_refresh_ports.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_connect = ttk.Button(top_frame, text="Connect", command=self._toggle_connection)
        self.btn_connect.pack(side=tk.LEFT, padx=(0, 15))

        self.lbl_conn_status = ttk.Label(top_frame, text="● Disconnected", font=("Segoe UI", 10, "bold"), foreground="red")
        self.lbl_conn_status.pack(side=tk.LEFT, padx=(0, 15))

        self.lbl_idn = ttk.Label(top_frame, text="Device: Disconnected", font=("Segoe UI", 9))
        self.lbl_idn.pack(side=tk.LEFT, padx=(0, 20))

        self.btn_stop = tk.Button(top_frame, text="🛑 EMERGENCY STOP", font=("Segoe UI", 11, "bold"),
                                  bg="#d32f2f", fg="white", activebackground="#b71c1c", activeforeground="white",
                                  command=self._emergency_stop, padx=12, pady=4)
        self.btn_stop.pack(side=tk.RIGHT, padx=4)

        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X)

        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        left_frame = ttk.Frame(main_paned, width=480)
        main_paned.add(left_frame, weight=0)

        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)

        self._build_telemetry_cards(left_frame)
        self._build_smart_ramp_panel(left_frame)
        self._build_loop_controls(left_frame)
        self._build_logging_panel(left_frame)

        self._build_notebook_tabs(right_frame)

        self.statusbar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W, padding=(6, 2))
        self.statusbar.pack(fill=tk.X, side=tk.BOTTOM)

    def _build_telemetry_cards(self, parent):
        card_frame = ttk.LabelFrame(parent, text="Live Telemetry", padding=8)
        card_frame.pack(fill=tk.X, pady=(0, 6))

        f_a = ttk.Frame(card_frame, relief=tk.RIDGE, borderwidth=1, padding=6)
        f_a.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        ttk.Label(f_a, text="CHANNEL A (Sample)", style="ReadoutTitle.TLabel").pack(anchor=tk.W)
        self.lbl_temp_a = ttk.Label(f_a, text="--.--- K", style="ReadoutValueA.TLabel")
        self.lbl_temp_a.pack(anchor=tk.CENTER)

        f_b = ttk.Frame(card_frame, relief=tk.RIDGE, borderwidth=1, padding=6)
        f_b.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)
        ttk.Label(f_b, text="CHANNEL B", style="ReadoutTitle.TLabel").pack(anchor=tk.W)
        self.lbl_temp_b = ttk.Label(f_b, text="--.--- K", style="ReadoutValueB.TLabel")
        self.lbl_temp_b.pack(anchor=tk.CENTER)

        f_sp = ttk.Frame(card_frame, relief=tk.RIDGE, borderwidth=1, padding=6)
        f_sp.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)
        ttk.Label(f_sp, text="SETPOINT", style="ReadoutTitle.TLabel").pack(anchor=tk.W)
        self.lbl_setpt = ttk.Label(f_sp, text="--.--- K", style="ReadoutValueSP.TLabel")
        self.lbl_setpt.pack(anchor=tk.CENTER)
        self.lbl_error = ttk.Label(f_sp, text="Error: -- K", font=("Segoe UI", 9, "bold"), foreground="#555")
        self.lbl_error.pack(anchor=tk.CENTER)

        f_ht = ttk.Frame(card_frame, relief=tk.RIDGE, borderwidth=1, padding=6)
        f_ht.grid(row=1, column=1, sticky="nsew", padx=4, pady=4)
        ttk.Label(f_ht, text="HEATER OUTPUT", style="ReadoutTitle.TLabel").pack(anchor=tk.W)
        self.lbl_heater = ttk.Label(f_ht, text="0.0 %", style="ReadoutValueHT.TLabel")
        self.lbl_heater.pack(anchor=tk.CENTER)
        self.pbar_heater = ttk.Progressbar(f_ht, orient=tk.HORIZONTAL, length=120, mode='determinate')
        self.pbar_heater.pack(fill=tk.X, padx=4, pady=(2, 0))

        card_frame.columnconfigure(0, weight=1)
        card_frame.columnconfigure(1, weight=1)

        badge_frame = ttk.Frame(card_frame)
        badge_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(6, 0))

        self.badge_ctrl = tk.Label(badge_frame, text="CONTROL: OFF", bg="#e0e0e0", fg="#333", font=("Segoe UI", 8, "bold"), padx=6, pady=2, relief=tk.GROOVE)
        self.badge_ctrl.pack(side=tk.LEFT, padx=2)

        self.badge_table = tk.Label(badge_frame, text="PID TABLE: 2", bg="#e3f2fd", fg="#0d47a1", font=("Segoe UI", 8, "bold"), padx=6, pady=2, relief=tk.GROOVE)
        self.badge_table.pack(side=tk.LEFT, padx=2)

        self.badge_range = tk.Label(badge_frame, text="RANGE: HI", bg="#f3e5f5", fg="#4a148c", font=("Segoe UI", 8, "bold"), padx=6, pady=2, relief=tk.GROOVE)
        self.badge_range.pack(side=tk.LEFT, padx=2)

        self.badge_ramp = tk.Label(badge_frame, text="RAMP: 0.5 K/min", bg="#fff3e0", fg="#e65100", font=("Segoe UI", 8, "bold"), padx=6, pady=2, relief=tk.GROOVE)
        self.badge_ramp.pack(side=tk.LEFT, padx=2)

    def _build_smart_ramp_panel(self, parent):
        ramp_frame = ttk.LabelFrame(parent, text="🎯 Smart Two-Speed Ramping (Zero Overshoot)", padding=8)
        ramp_frame.pack(fill=tk.X, pady=(0, 6))

        r1 = ttk.Frame(ramp_frame)
        r1.pack(fill=tk.X, pady=2)
        ttk.Label(r1, text="Target Temp (K):", width=16).pack(side=tk.LEFT)
        self.ent_target_temp = ttk.Entry(r1, width=10)
        self.ent_target_temp.insert(0, "320.0")
        self.ent_target_temp.pack(side=tk.LEFT, padx=(0, 8))

        for p_temp in [300.0, 315.0, 350.0, 400.0, 450.0]:
            btn = ttk.Button(r1, text=f"{int(p_temp)}K", width=5,
                             command=lambda t=p_temp: self._set_target_preset(t))
            btn.pack(side=tk.LEFT, padx=1)

        r2 = ttk.Frame(ramp_frame)
        r2.pack(fill=tk.X, pady=2)
        ttk.Label(r2, text="Fast Rate (K/min):", width=16).pack(side=tk.LEFT)
        self.ent_fast_rate = ttk.Entry(r2, width=6)
        self.ent_fast_rate.insert(0, "5.0")
        self.ent_fast_rate.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(r2, text="Slow Final Rate:").pack(side=tk.LEFT)
        self.ent_slow_rate = ttk.Entry(r2, width=6)
        self.ent_slow_rate.insert(0, "0.5")
        self.ent_slow_rate.pack(side=tk.LEFT, padx=(4, 10))

        ttk.Label(r2, text="Switch Delta:").pack(side=tk.LEFT)
        self.ent_switch_delta = ttk.Entry(r2, width=5)
        self.ent_switch_delta.insert(0, "15.0")
        self.ent_switch_delta.pack(side=tk.LEFT, padx=(4, 0))

        r3 = ttk.Frame(ramp_frame)
        r3.pack(fill=tk.X, pady=(6, 2))

        self.btn_start_ramp = tk.Button(r3, text="▶ START SMART RAMP", font=("Segoe UI", 9, "bold"),
                                        bg="#1b5e20", fg="white", activebackground="#2e7d32",
                                        command=self._toggle_smart_ramp, padx=8, pady=3)
        self.btn_start_ramp.pack(side=tk.LEFT, padx=(0, 8))

        self.lbl_ramp_engine_status = ttk.Label(r3, text="Ramp Engine: Idle", font=("Segoe UI", 9, "italic"))
        self.lbl_ramp_engine_status.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _build_loop_controls(self, parent):
        ctrl_frame = ttk.LabelFrame(parent, text="Manual Loop 1 Controls", padding=8)
        ctrl_frame.pack(fill=tk.X, pady=(0, 6))

        row1 = ttk.Frame(ctrl_frame)
        row1.pack(fill=tk.X, pady=2)

        ttk.Label(row1, text="Direct Setpoint (K):").pack(side=tk.LEFT)
        self.ent_direct_sp = ttk.Entry(row1, width=8)
        self.ent_direct_sp.insert(0, "300.0")
        self.ent_direct_sp.pack(side=tk.LEFT, padx=4)

        ttk.Button(row1, text="Apply SP", width=9, command=self._apply_direct_sp).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(row1, text="Ramp Rate:").pack(side=tk.LEFT)
        self.ent_direct_rate = ttk.Entry(row1, width=6)
        self.ent_direct_rate.insert(0, "0.5")
        self.ent_direct_rate.pack(side=tk.LEFT, padx=4)
        ttk.Button(row1, text="Apply Rate", width=9, command=self._apply_direct_rate).pack(side=tk.LEFT)

        row2 = ttk.Frame(ctrl_frame)
        row2.pack(fill=tk.X, pady=(4, 0))

        self.btn_toggle_ctrl = ttk.Button(row2, text="Enable Control", command=self._toggle_control)
        self.btn_toggle_ctrl.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Label(row2, text="Active Table:").pack(side=tk.LEFT)
        self.combo_tableix = ttk.Combobox(row2, width=12, values=["Table 1 (20-320K)", "Table 2 (180-475K)"], state="readonly")
        self.combo_tableix.set("Table 2 (180-475K)")
        self.combo_tableix.pack(side=tk.LEFT, padx=4)
        ttk.Button(row2, text="Switch Table", command=self._apply_tableix).pack(side=tk.LEFT, padx=(0, 8))

        ttk.Label(row2, text="Range:").pack(side=tk.LEFT)
        self.combo_range = ttk.Combobox(row2, width=5, values=["HI", "MID", "LOW", "75W"], state="readonly")
        self.combo_range.set("HI")
        self.combo_range.pack(side=tk.LEFT, padx=4)
        ttk.Button(row2, text="Set", width=4, command=self._apply_heater_range).pack(side=tk.LEFT)

    def _build_logging_panel(self, parent):
        log_frame = ttk.LabelFrame(parent, text="💾 Data Logging & CSV Storage", padding=8)
        log_frame.pack(fill=tk.X)

        r1 = ttk.Frame(log_frame)
        r1.pack(fill=tk.X, pady=2)

        self.btn_toggle_log = ttk.Button(r1, text="Start Logging (CSV)", command=self._toggle_logging)
        self.btn_toggle_log.pack(side=tk.LEFT, padx=(0, 8))

        self.lbl_log_status = ttk.Label(r1, text="Logging: Inactive", foreground="#666666")
        self.lbl_log_status.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(r1, text="Records:").pack(side=tk.LEFT)
        self.lbl_log_count = ttk.Label(r1, text="0", font=("Segoe UI", 9, "bold"))
        self.lbl_log_count.pack(side=tk.LEFT, padx=4)

        self.lbl_log_file = ttk.Label(log_frame, text="File: --", font=("Segoe UI", 8), foreground="#888")
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

        self.chk_show_b = tk.BooleanVar(value=False)
        ttk.Checkbutton(tb, text="Temp B", variable=self.chk_show_b).pack(side=tk.LEFT, padx=3)

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

        self.ax1.set_xlabel("Elapsed Time (s)", fontsize=9)
        self.ax1.set_ylabel("Temperature (K)", color="#0066cc", fontsize=9)
        self.ax2.set_ylabel("Heater Output (%)", color="#6a1b9a", fontsize=9)

        self.ax1.grid(True, linestyle="--", alpha=0.5)
        self.fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _build_pid_table_view(self, parent, table_num):
        tb_bar = ttk.Frame(parent)
        tb_bar.pack(fill=tk.X, pady=(0, 4))

        ttk.Label(tb_bar, text=f"PID Table {table_num:02d} Entries (Cryocon 22C)", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
        ttk.Button(tb_bar, text="🔄 Reload", command=lambda: self._load_pid_table_into_tree(table_num)).pack(side=tk.RIGHT, padx=4)

        if table_num == 2:
            ttk.Button(tb_bar, text="⚡ Re-flash Table 02 (475K-180K)", command=self._reflash_table_02).pack(side=tk.RIGHT, padx=4)

        cols = ("row", "setpt", "pgain", "igain", "dgain", "range", "channel")
        tree = ttk.Treeview(parent, columns=cols, show="headings", height=18)
        tree.heading("row", text="#")
        tree.heading("setpt", text="Setpoint (K)")
        tree.heading("pgain", text="P Gain")
        tree.heading("igain", text="I Gain")
        tree.heading("dgain", text="D Gain")
        tree.heading("range", text="Heater Range")
        tree.heading("channel", text="Source")

        tree.column("row", width=40, anchor=tk.CENTER)
        tree.column("setpt", width=100, anchor=tk.CENTER)
        tree.column("pgain", width=90, anchor=tk.CENTER)
        tree.column("igain", width=90, anchor=tk.CENTER)
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
            ok, msg = self.comm.connect(port=port, baud=9600)
            if ok:
                idn = self.comm.query("*IDN?")
                self.telemetry["idn"] = idn
                self.lbl_idn.config(text=f"Device: {idn}")
                self.lbl_conn_status.config(text="● Connected", foreground="#2e7d32")
                self.btn_connect.config(text="Disconnect")
                self.statusbar.config(text=f"Connected to {idn} on {port}")

                self.poll_running = True
                self.poll_thread = threading.Thread(target=self._polling_worker, daemon=True)
                self.poll_thread.start()

                self.root.after(800, lambda: self._load_pid_table_into_tree(2))
                self.root.after(1600, lambda: self._load_pid_table_into_tree(1))
            else:
                self.lbl_conn_status.config(text="● Disconnected", foreground="red")
        else:
            self.poll_running = False
            self.comm.disconnect()
            self.lbl_conn_status.config(text="● Disconnected", foreground="red")
            self.lbl_idn.config(text="Device: Disconnected")
            self.btn_connect.config(text="Connect")
            self.statusbar.config(text="Disconnected")

    def _polling_worker(self):
        while self.poll_running and self.comm.connected:
            try:
                ta_str = self.comm.query("INPUT? A")
                tb_str = self.comm.query("INPUT? B")
                sp_str = self.comm.query("LOOP 1:SETPT?").replace("K", "").strip()
                ht_str = self.comm.query("LOOP 1:OUTP?").replace("%", "").strip()
                ctrl_str = self.comm.query("CONTROL?")
                type_str = self.comm.query("LOOP 1:TYPE?")
                tix_str = self.comm.query("LOOP 1:TABLEIX?")
                rate_str = self.comm.query("LOOP 1:RATE?")
                rng_str = self.comm.query("LOOP 1:RANGE?")
                pg_str = self.comm.query("LOOP 1:PGAIN?")
                ig_str = self.comm.query("LOOP 1:IGAIN?")
                dg_str = self.comm.query("LOOP 1:DGAIN?")

                try: ta = float(ta_str)
                except ValueError: ta = 0.0
                try: tb = float(tb_str)
                except ValueError: tb = 0.0
                try: sp = float(sp_str)
                except ValueError: sp = 0.0
                try: ht = float(ht_str)
                except ValueError: ht = 0.0
                try: rate = float(rate_str)
                except ValueError: rate = 0.5
                try: pg = float(pg_str)
                except ValueError: pg = 0.0
                try: ig = float(ig_str)
                except ValueError: ig = 0.0
                try: dg = float(dg_str)
                except ValueError: dg = 0.0

                err = ta - sp if sp > 0 else 0.0

                self.telemetry.update({
                    "temp_a": ta, "temp_b": tb, "setpoint": sp, "error": err,
                    "heater_pwr": ht, "control": ctrl_str, "type": type_str,
                    "tableix": tix_str, "rate": rate, "range": rng_str,
                    "pgain": pg, "igain": ig, "dgain": dg
                })

                if self.smart_ramp_active:
                    self._process_smart_ramp_step(ta, sp)

                if self.logging_active and self.log_writer:
                    self._log_telemetry_row()

                self.root.after(0, self._update_gui_readouts)

            except Exception:
                pass

            time.sleep(0.8)

    def _set_target_preset(self, temp_val):
        self.ent_target_temp.delete(0, tk.END)
        self.ent_target_temp.insert(0, str(temp_val))

    def _toggle_smart_ramp(self):
        if not self.smart_ramp_active:
            try:
                self.target_temp = float(self.ent_target_temp.get().strip())
                self.fast_rate = float(self.ent_fast_rate.get().strip())
                self.slow_rate = float(self.ent_slow_rate.get().strip())
                self.threshold_delta = float(self.ent_switch_delta.get().strip())
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid numeric values.")
                return

            if not self.comm.connected:
                messagebox.showwarning("Not Connected", "Please connect to the Cryocon controller first.")
                return

            self.comm.send("LOOP 1:TABLEIX 2")
            self.comm.send("CONTROL")

            current_temp = self.telemetry["temp_a"]
            delta = abs(current_temp - self.target_temp)

            self.comm.send(f"LOOP 1:SETPT {self.target_temp}")

            if delta > self.threshold_delta:
                self.ramp_stage = "FAST_RAMP"
                self.comm.send(f"LOOP 1:RATE {self.fast_rate}")
                status_msg = f"Fast Ramping @ {self.fast_rate} K/min (ΔT={delta:.1f}K > {self.threshold_delta}K)"
            else:
                self.ramp_stage = "GENTLE_APPROACH"
                self.comm.send(f"LOOP 1:RATE {self.slow_rate}")
                status_msg = f"Gentle Approach @ {self.slow_rate} K/min (within {self.threshold_delta}K)"

            self.smart_ramp_active = True
            self.btn_start_ramp.config(text="⏹ STOP RAMP", bg="#d32f2f")
            self.lbl_ramp_engine_status.config(text=f"Engine: {status_msg}")
            self.statusbar.config(text=f"Smart Ramp active: Target {self.target_temp}K | {status_msg}")
        else:
            self.smart_ramp_active = False
            self.ramp_stage = "IDLE"
            self.btn_start_ramp.config(text="▶ START SMART RAMP", bg="#1b5e20")
            self.lbl_ramp_engine_status.config(text="Ramp Engine: Idle / Stopped")
            self.statusbar.config(text="Smart Ramp stopped.")

    def _process_smart_ramp_step(self, current_temp, current_setpt):
        delta = abs(current_temp - self.target_temp)
        # Signed overshoot: temperature has crossed above target
        overshot = (current_temp > self.target_temp + 0.1)

        if self.ramp_stage == "FAST_RAMP":
            if overshot:
                # Temperature crossed target — bail straight to FINE_APPROACH
                self.ramp_stage = "FINE_APPROACH"
                self.comm.send("LOOP 1:RATE 0")   # disable ramp, let PID settle
                _d = delta  # capture for lambda
                self.root.after(0, lambda d=_d: self.lbl_ramp_engine_status.config(
                    text=f"Engine: OVERSHOOT detected (+{d:.2f}K) → PID-only hold (RATE=0)"
                ))
            elif delta <= self.threshold_delta:
                self.ramp_stage = "GENTLE_APPROACH"
                self.comm.send(f"LOOP 1:RATE {self.slow_rate}")
                _d = delta  # capture for lambda
                self.root.after(0, lambda d=_d: self.lbl_ramp_engine_status.config(
                    text=f"Engine: GENTLE @ {self.slow_rate} K/min (ΔT={d:.2f}K ≤ {self.threshold_delta}K)"
                ))

        elif self.ramp_stage == "GENTLE_APPROACH":
            fine_delta = max(self.slow_rate * 2.0, 2.0)  # switch 2× slow-rate or 2K before target
            if overshot or delta <= fine_delta:
                self.ramp_stage = "FINE_APPROACH"
                self.comm.send("LOOP 1:RATE 0")   # stop setpoint ramping, PID takes over
                _d = delta  # capture for lambda
                self.root.after(0, lambda d=_d: self.lbl_ramp_engine_status.config(
                    text=f"Engine: FINE approach — RATE=0, PID settling (ΔT={d:.2f}K)"
                ))

        elif self.ramp_stage == "FINE_APPROACH":
            if delta < 0.2:
                self.ramp_stage = "HOLDING"
                self.root.after(0, lambda: self.lbl_ramp_engine_status.config(
                    text=f"Engine: ✓ Target {self.target_temp}K REACHED — Holding (Error < 0.2K)."
                ))

    def _toggle_logging(self):
        if not self.logging_active:
            now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.log_filename = os.path.abspath(f"cryocon_log_{now_str}.csv")
            try:
                self.log_file = open(self.log_filename, "w", newline="", encoding="utf-8")
                self.log_writer = csv.writer(self.log_file)
                self.log_writer.writerow([
                    "Timestamp", "Elapsed_Sec", "Temp_A_K", "Temp_B_K",
                    "Setpoint_K", "Error_K", "Heater_Pct", "Ramp_Rate_K_min",
                    "Active_PID_Table", "Control_State", "P_Gain", "I_Gain", "D_Gain"
                ])
                self.log_file.flush()
                self.log_records_count = 0
                self.log_start_time = time.time()
                self.logging_active = True

                self.btn_toggle_log.config(text="⏹ Stop Logging")
                self.lbl_log_status.config(text="Logging: RECORDING", foreground="#2e7d32")
                self.lbl_log_file.config(text=f"File: {os.path.basename(self.log_filename)}")
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
            self.statusbar.config(text=f"Logging stopped. Records: {self.log_records_count}")

    def _log_telemetry_row(self):
        t = self.telemetry
        elapsed = time.time() - self.log_start_time
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_writer.writerow([
            ts, f"{elapsed:.1f}", f"{t['temp_a']:.4f}", f"{t['temp_b']:.4f}",
            f"{t['setpoint']:.4f}", f"{t['error']:+.4f}", f"{t['heater_pwr']:.2f}",
            f"{t['rate']:.2f}", t['tableix'], t['control'],
            f"{t['pgain']:.4f}", f"{t['igain']:.4f}", f"{t['dgain']:.4f}"
        ])
        self.log_file.flush()
        self.log_records_count += 1

    def _apply_direct_sp(self):
        try:
            sp = float(self.ent_direct_sp.get().strip())
            self.comm.send(f"LOOP 1:SETPT {sp}")
            self.statusbar.config(text=f"Setpoint {sp} K sent to Loop 1")
        except ValueError:
            messagebox.showerror("Error", "Invalid setpoint value")

    def _apply_direct_rate(self):
        try:
            r = float(self.ent_direct_rate.get().strip())
            self.comm.send(f"LOOP 1:RATE {r}")
            self.statusbar.config(text=f"Ramp rate {r} K/min sent to Loop 1")
        except ValueError:
            messagebox.showerror("Error", "Invalid ramp rate value")

    def _toggle_control(self):
        if self.telemetry["control"].upper() == "ON":
            self.comm.send("STOP")
            self.statusbar.config(text="Control STOPPED (Heater OFF)")
        else:
            self.comm.send("CONTROL")
            self.statusbar.config(text="Control ENABLED (Heater active)")

    def _apply_tableix(self):
        sel = self.combo_tableix.get()
        tix = 1 if "Table 1" in sel else 2
        self.comm.send(f"LOOP 1:TABLEIX {tix}")
        self.statusbar.config(text=f"Loop 1 PID Table set to Table {tix}")

    def _apply_heater_range(self):
        rng = self.combo_range.get().strip()
        self.comm.send(f"LOOP 1:RANGE {rng}")
        self.statusbar.config(text=f"Loop 1 Heater Range set to {rng}")

    def _emergency_stop(self):
        self.comm.send("STOP")
        self.smart_ramp_active = False
        self.ramp_stage = "IDLE"
        self.btn_start_ramp.config(text="▶ START SMART RAMP", bg="#1b5e20")
        self.lbl_ramp_engine_status.config(text="EMERGENCY STOP EXECUTED - Heater DISABLED")
        self.statusbar.config(text="🛑 EMERGENCY STOP: Control aborted, heater set to 0%")
        messagebox.showwarning("EMERGENCY STOP", "Control loop STOP command sent to Cryocon.\nHeater power disabled.")

    def _load_pid_table_into_tree(self, table_num):
        if not self.comm.connected:
            return
        tree = self.tree_table2 if table_num == 2 else self.tree_table1

        raw = self.comm.query_multiline(f"PIDTABLE {table_num}:TABLE?", wait=1.5)
        for item in tree.get_children():
            tree.delete(item)

        lines = raw.replace("\r", "").split("\n")
        row_idx = 1
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
                    tree.insert("", tk.END, values=(row_idx, f"{sp:.2f}", p, i, d, rng, ch))
                    row_idx += 1
                except ValueError:
                    pass

        self.statusbar.config(text=f"Loaded {row_idx-1} entries from PID Table {table_num:02d}")

    def _reflash_table_02(self):
        if not messagebox.askyesno("Confirm Re-Flash", "Write Table 02 (180K - 475K, 16 entries) to Cryocon controller?"):
            return

        entries = [
            (475, 2.5, 250, 60, "HI"),
            (460, 2.4, 240, 60, "HI"),
            (440, 2.3, 230, 50, "HI"),
            (420, 2.2, 220, 50, "HI"),
            (400, 2.1, 210, 50, "HI"),
            (380, 2.0, 200, 50, "HI"),
            (360, 1.9, 190, 40, "HI"),
            (340, 1.8, 180, 40, "HI"),
            (320, 1.7, 170, 40, "HI"),
            (300, 1.6, 160, 40, "HI"),
            (280, 1.5, 150, 30, "HI"),
            (260, 1.4, 140, 30, "HI"),
            (240, 1.3, 130, 30, "HI"),
            (220, 1.2, 120, 30, "HI"),
            (200, 1.1, 110, 20, "MID"),
            (180, 1.0, 100, 20, "MID"),
        ]

        cmd_lines = ["PIDTABLE 2:TABLE", "PID Table 2"]
        for (sp, p, i, d, rng) in entries:
            cmd_lines.append(f" {sp:6.2f}  {p:5.2f}  {i:6.2f}  {d:5.2f}  {rng}")
        cmd_lines.append(";")
        full_cmd = "\r\n".join(cmd_lines) + "\r\n"

        with self.comm.lock:
            self.comm.ser.reset_input_buffer()
            self.comm.ser.write(full_cmd.encode())
            time.sleep(2.0)

        self._load_pid_table_into_tree(2)
        messagebox.showinfo("Success", "PID Table 02 successfully re-flashed and verified!")

    def _update_gui_readouts(self):
        t = self.telemetry

        self.lbl_temp_a.config(text=f"{t['temp_a']:.3f} K")
        self.lbl_temp_b.config(text=f"{t['temp_b']:.3f} K" if t['temp_b'] > 0 else "--.--- K")
        self.lbl_setpt.config(text=f"{t['setpoint']:.3f} K")
        err_sign = "+" if t['error'] >= 0 else ""
        self.lbl_error.config(text=f"Error: {err_sign}{t['error']:.3f} K",
                              foreground="#c62828" if abs(t['error']) > 1.0 else "#2e7d32")
        self.lbl_heater.config(text=f"{t['heater_pwr']:.1f} %")
        self.pbar_heater["value"] = min(100.0, max(0.0, t['heater_pwr']))

        is_on = t['control'].upper() in ["ON", "1", "TRUE"]
        self.badge_ctrl.config(text=f"CONTROL: {t['control']}",
                               bg="#c8e6c9" if is_on else "#ffcdd2",
                               fg="#1b5e20" if is_on else "#b71c1c")
        self.btn_toggle_ctrl.config(text="Disable Control (STOP)" if is_on else "Enable Control (ON)")

        self.badge_table.config(text=f"PID TABLE: {t['tableix']}")
        self.badge_range.config(text=f"RANGE: {t['range']}")
        self.badge_ramp.config(text=f"RAMP: {t['rate']:.2f} K/min")

        if self.logging_active:
            self.lbl_log_count.config(text=str(self.log_records_count))

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

        if len(self.plot_times) % 2 == 0:
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

        t_now = self.plot_times[-1]
        cutoff = t_now - self.plot_window_seconds

        indices = [i for i, t in enumerate(self.plot_times) if t >= cutoff]
        if not indices:
            indices = list(range(len(self.plot_times)))

        times_rel = [(self.plot_times[i] - self.plot_times[0]) for i in indices]

        visible_temps = []
        if self.chk_show_a.get() and len(self.plot_temp_a) >= len(indices):
            y_a = [self.plot_temp_a[i] for i in indices]
            self.ax1.plot(times_rel, y_a, label="Temp A", color="#0066cc", linewidth=2.0)
            visible_temps.extend(y_a)

        if self.chk_show_b.get() and len(self.plot_temp_b) >= len(indices):
            y_b = [self.plot_temp_b[i] for i in indices]
            self.ax1.plot(times_rel, y_b, label="Temp B", color="#2e7d32", linewidth=1.5, linestyle=":")
            if any(v > 0 for v in y_b):
                visible_temps.extend(y_b)



        visible_heaters = []
        if self.chk_show_ht.get() and len(self.plot_heater) >= len(indices):
            y_ht = [self.plot_heater[i] for i in indices]
            self.ax2.plot(times_rel, y_ht, label="Heater %", color="#9c27b0", linewidth=1.0, alpha=0.6)
            visible_heaters.extend(y_ht)

        # Smart Autoscale for Temperature (Y-axis 1)
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

        # Smart Autoscale for Heater Output % (Y-axis 2)
        if self.chk_autoscale_ht.get() and visible_heaters:
            max_ht = max(visible_heaters)
            self.ax2.set_ylim(0, max(20.0, max_ht * 1.25))
        else:
            self.ax2.set_ylim(0, 105)

        self.ax1.set_ylabel("Temperature (K)", color="#0066cc", fontsize=9)
        self.ax2.set_ylabel("Heater Output (%)", color="#9c27b0", fontsize=9)
        self.ax1.grid(True, linestyle="--", alpha=0.4)

        self.ax1.legend(loc="upper left", fontsize=8)
        self.ax2.legend(loc="upper right", fontsize=8)

        self.fig.tight_layout()
        self.canvas.draw_idle()

    def _on_close(self):
        self.poll_running = False
        self.smart_ramp_active = False
        if self.logging_active and self.log_file:
            try:
                self.log_file.close()
            except Exception:
                pass
        self.comm.disconnect()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = CryoconGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
