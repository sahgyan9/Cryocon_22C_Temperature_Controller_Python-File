"""
Wayne Kerr 6510B & Cryo-con 22C — Fixed 10 kHz Continuous Cooling Desktop GUI
==============================================================================
Specialized Automated Dielectric Spectroscopy Suite for PMN-0.3PT Relaxor Samples.

Target Mission:
- Starting Temperature: Current Live Reading (~422 K)
- Controlled Cooling Ramp: Down to 300.0 K at 0.50 K/min
- Validated PID Loop: P=70.0, I=900.0 s, D=0.0, Range HI, MaxPwr 100%
- Wayne Kerr 6510B: Fixed 10 kHz (10,000 Hz), 100 mV RMS AC drive, Series (R-X)
- Real-Time Table: T (K) | f (Fixed) | R (ohm) | X (ohm)
- Live Multi-Tab Plotting:
    1. Table: Live streaming measurements table
    2. Spectrum: R & X vs. Temperature T (K)
    3. Permittivity: ε' & Tan δ vs. Temperature T (K)
    4. Thermal Profile: T, Setpoint & Heater % vs. Time
    5. Impedance & Nyquist: |Z| & θ vs. T, -X vs. R
- Zero Data Corruption: Unbuffered streaming writes with .flush() & os.fsync()
- Failsafe: Emergency Stop & auto heater disconnect on any exit.

Author: Lab Automation & Antigravity
Date: 2026-09-11
"""

import csv
import datetime
import math
import os
import queue
import sys
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from cryocon_controller import Cryocon22C
from wayne_kerr_controller import WayneKerr6500B
from cooling_runner import CoolingOrchestrator, EPSILON_0


class CoolingGUI:
    """
    Desktop GUI for fixed 10 kHz continuous cooling measurements.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Wayne Kerr 6510B & Cryo-con 22C — Continuous Cooling (10 kHz Fixed)")
        self.root.geometry("1440x880")
        self.root.minsize(1100, 650)

        # Hardware and orchestrator handles
        self.cryocon: Optional[Cryocon22C] = None
        self.wayne_kerr: Optional[WayneKerr6500B] = None
        self.orchestrator: Optional[CoolingOrchestrator] = None
        self.worker_thread: Optional[threading.Thread] = None

        # Threading queue for UI updates
        self.ui_queue: queue.Queue = queue.Queue()
        self._alive: bool = True
        self._poll_job: Optional[str] = None

        # Telemetry & Plotting History Buffers
        self.time_history: List[float] = []
        self.temp_history: List[float] = []
        self.sp_history: List[float] = []
        self.heater_history: List[float] = []
        self.r_history: List[float] = []
        self.x_history: List[float] = []
        self.eps_history: List[float] = []
        self.tand_history: List[float] = []
        self.z_history: List[float] = []
        self.theta_history: List[float] = []

        # Table & Plotting Controls
        self.autoscroll_table_var = tk.BooleanVar(value=True)
        self.chk_show_temp = tk.BooleanVar(value=True)
        self.chk_show_sp = tk.BooleanVar(value=True)
        self.chk_show_heater = tk.BooleanVar(value=True)
        self.chk_autoscale_temp = tk.BooleanVar(value=True)
        self.chk_autoscale_heater = tk.BooleanVar(value=False)
        self.thermal_plot_window_s = 600  # Default 10 min
        self.last_chart_draw = 0.0

        # Sample Geometry (PMN-0.3PT)
        self.sample_d_var = tk.DoubleVar(value=0.30)  # 0.30 mm thickness
        self.sample_a_var = tk.DoubleVar(value=6.00)  # 6.00 mm^2 electrode area

        # Experiment Configuration Defaults
        self.fixed_freq_var = tk.DoubleVar(value=10000.0)  # 10 kHz
        self.bias_mv_var = tk.DoubleVar(value=100.0)       # 100 mV RMS
        self.target_temp_var = tk.DoubleVar(value=300.0)   # 300 K
        self.start_temp_var = tk.DoubleVar(value=422.0)    # ~422 K starting temp
        self.cooling_rate_var = tk.DoubleVar(value=0.50)   # 0.5 K/min
        self.sample_interval_var = tk.DoubleVar(value=1.0) # 1.0 sec
        self.p_gain_var = tk.DoubleVar(value=70.0)
        self.i_gain_var = tk.DoubleVar(value=900.0)
        self.d_gain_var = tk.DoubleVar(value=0.0)
        self.max_power_var = tk.DoubleVar(value=100.0)
        self.heater_range_var = tk.StringVar(value="HI")
        # Ensure Data folder is created directly in this subfolder
        default_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")
        os.makedirs(default_data_dir, exist_ok=True)
        self.out_dir_var = tk.StringVar(value=default_data_dir)

        # Window closing failsafe
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)

        self._build_style()
        self._build_ui()
        self._start_ui_dispatcher()

    def _build_style(self):
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass
        self.style.configure(".", font=("Segoe UI", 9))
        self.style.configure("Header.TLabel", font=("Segoe UI", 11, "bold"))
        self.style.configure("SubHeader.TLabel", font=("Segoe UI", 9, "bold"), foreground="#1a365d")
        self.style.configure("BigDigit.TLabel", font=("Consolas", 15, "bold"), foreground="#0f172a")
        self.style.configure("Status.TLabel", font=("Segoe UI", 9, "bold"), foreground="#0284c7")

    def _build_ui(self):
        # ---------------------------------------------------------------------
        # Top Connection & Emergency Toolbar
        # ---------------------------------------------------------------------
        top_bar = ttk.Frame(self.root, padding="6 6 6 6")
        top_bar.pack(side=tk.TOP, fill=tk.X)

        # Cryocon Port & Baud
        ttk.Label(top_bar, text="Cryocon 22C:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=3)
        self.cryo_port_var = tk.StringVar(value="COM5")
        ttk.Entry(top_bar, textvariable=self.cryo_port_var, width=7).pack(side=tk.LEFT, padx=2)

        ttk.Label(top_bar, text="Baud:").pack(side=tk.LEFT, padx=2)
        self.cryo_baud_var = tk.StringVar(value="57600")
        ttk.Combobox(top_bar, textvariable=self.cryo_baud_var, values=["57600", "9600", "19200"], width=6, state="readonly").pack(side=tk.LEFT, padx=2)

        # Wayne Kerr VISA
        ttk.Label(top_bar, text=" | Wayne Kerr VISA:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=4)
        self.wk_visa_var = tk.StringVar(value="GPIB0::6::INSTR")
        ttk.Entry(top_bar, textvariable=self.wk_visa_var, width=16).pack(side=tk.LEFT, padx=2)

        # Mock Mode Checkbox
        self.mock_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(top_bar, text="Mock Mode", variable=self.mock_var).pack(side=tk.LEFT, padx=8)

        # Connect / Disconnect Buttons
        self.btn_connect = tk.Button(
            top_bar, text="Connect Hardware", font=("Segoe UI", 9, "bold"),
            bg="#2563eb", fg="#ffffff", padx=8, pady=2, relief="groove",
            command=self.connect_hardware
        )
        self.btn_connect.pack(side=tk.LEFT, padx=4)

        self.btn_disconnect = tk.Button(
            top_bar, text="Disconnect", font=("Segoe UI", 9),
            bg="#e2e8f0", padx=6, pady=2, relief="groove", state=tk.DISABLED,
            command=self.disconnect_hardware
        )
        self.btn_disconnect.pack(side=tk.LEFT, padx=4)

        self.lbl_conn_status = ttk.Label(top_bar, text="[DISCONNECTED]", foreground="#dc2626", font=("Segoe UI", 9, "bold"))
        self.lbl_conn_status.pack(side=tk.LEFT, padx=8)

        # Prominent Emergency Stop Button
        self.btn_emergency_stop = tk.Button(
            top_bar,
            text="⚠ EMERGENCY STOP",
            font=("Segoe UI", 11, "bold"),
            bg="#dc2626",
            fg="#ffffff",
            activebackground="#b91c1c",
            activeforeground="#ffffff",
            padx=14,
            pady=2,
            relief="raised",
            command=self.emergency_stop
        )
        self.btn_emergency_stop.pack(side=tk.RIGHT, padx=6)

        # ---------------------------------------------------------------------
        # Main Layout: Scrollable Left Panel + Right Plotting Notebook
        # ---------------------------------------------------------------------
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        # Left Container
        left_container = ttk.Frame(main_paned, width=470)
        main_paned.add(left_container, weight=0)

        # Right Container
        right_container = ttk.Frame(main_paned, padding="4")
        main_paned.add(right_container, weight=1)

        # Scrollable Canvas setup for Left Panel
        self.left_canvas = tk.Canvas(left_container, borderwidth=0, highlightthickness=0, width=460)
        self.left_scrollbar = ttk.Scrollbar(left_container, orient="vertical", command=self.left_canvas.yview)
        self.left_scrollable = ttk.Frame(self.left_canvas, padding="2 2 4 2")

        self.canvas_window = self.left_canvas.create_window((0, 0), window=self.left_scrollable, anchor="nw")

        def _on_left_configure(event):
            self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all"))

        def _on_canvas_configure(event):
            self.left_canvas.itemconfig(self.canvas_window, width=event.width)

        self.left_scrollable.bind("<Configure>", _on_left_configure)
        self.left_canvas.bind("<Configure>", _on_canvas_configure)
        self.left_canvas.configure(yscrollcommand=self.left_scrollbar.set)

        self.left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Mousewheel binding for left panel
        def _on_left_mousewheel(event):
            try:
                x, y = self.root.winfo_pointerxy()
                w = self.root.winfo_containing(x, y)
                while w is not None:
                    if w in {left_container, self.left_canvas, self.left_scrollable}:
                        self.left_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                        return
                    w = getattr(w, "master", None)
            except Exception:
                pass

        self.root.bind_all("<MouseWheel>", _on_left_mousewheel, add="+")

        # Build Sub-Panels
        self._build_thermal_panel(self.left_scrollable)
        self._build_wayne_kerr_panel(self.left_scrollable)
        self._build_sample_panel(self.left_scrollable)
        self._build_execution_panel(self.left_scrollable)

        # Build Right Multi-Tab Visualizer
        self._build_visualizer(right_container)

    # -------------------------------------------------------------------------
    # Left Panels
    # -------------------------------------------------------------------------

    def _build_thermal_panel(self, parent):
        grp = ttk.LabelFrame(parent, text=" 1. Temperature Cooling Ramp Control ", padding="6 4 6 4")
        grp.pack(fill=tk.X, pady=2)

        # Big Digital Indicators
        digits_box = ttk.Frame(grp, padding="2")
        digits_box.pack(fill=tk.X, pady=2)

        d1 = ttk.Frame(digits_box, relief="sunken", padding="2")
        d1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        ttk.Label(d1, text="STAGE TEMP (T)", font=("Segoe UI", 7, "bold"), foreground="#64748b").pack()
        self.lbl_digit_temp = ttk.Label(d1, text="--.--- K", style="BigDigit.TLabel")
        self.lbl_digit_temp.pack()

        d2 = ttk.Frame(digits_box, relief="sunken", padding="2")
        d2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        ttk.Label(d2, text="SETPOINT", font=("Segoe UI", 7, "bold"), foreground="#64748b").pack()
        self.lbl_digit_setpt = ttk.Label(d2, text="300.00 K", style="BigDigit.TLabel")
        self.lbl_digit_setpt.pack()

        d3 = ttk.Frame(digits_box, relief="sunken", padding="2")
        d3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        ttk.Label(d3, text="HEATER (W)", font=("Segoe UI", 7, "bold"), foreground="#64748b").pack()
        self.lbl_digit_heater = ttk.Label(d3, text="0.0 %", style="BigDigit.TLabel")
        self.lbl_digit_heater.pack()

        # Ramp Parameters: Target & Rate
        r1 = ttk.Frame(grp)
        r1.pack(fill=tk.X, pady=2)
        ttk.Label(r1, text="Target Temp (K):", width=16).pack(side=tk.LEFT)
        ttk.Entry(r1, textvariable=self.target_temp_var, width=8).pack(side=tk.LEFT)
        ttk.Label(r1, text="K  (Cool to 300.0 K)", foreground="#475569", font=("Segoe UI", 8, "italic")).pack(side=tk.LEFT, padx=4)

        r2 = ttk.Frame(grp)
        r2.pack(fill=tk.X, pady=2)
        ttk.Label(r2, text="Cooling Rate:", width=16).pack(side=tk.LEFT)
        ttk.Spinbox(r2, textvariable=self.cooling_rate_var, from_=0.1, to=2.0, increment=0.1, width=7).pack(side=tk.LEFT)
        ttk.Label(r2, text="K/min  (Default: 0.5 K/min)", foreground="#0369a1", font=("Segoe UI", 8, "bold")).pack(side=tk.LEFT, padx=4)

        # PID Gains Row
        r3 = ttk.Frame(grp)
        r3.pack(fill=tk.X, pady=2)
        ttk.Label(r3, text="PID (Default):", width=12).pack(side=tk.LEFT)

        ttk.Label(r3, text="P:").pack(side=tk.LEFT, padx=(2, 1))
        ttk.Spinbox(r3, textvariable=self.p_gain_var, from_=0.0, to=200.0, increment=5.0, width=5).pack(side=tk.LEFT)

        ttk.Label(r3, text="I (s):").pack(side=tk.LEFT, padx=(4, 1))
        ttk.Spinbox(r3, textvariable=self.i_gain_var, from_=0.0, to=3000.0, increment=50.0, width=5).pack(side=tk.LEFT)

        ttk.Label(r3, text="D:").pack(side=tk.LEFT, padx=(4, 1))
        ttk.Spinbox(r3, textvariable=self.d_gain_var, from_=0.0, to=50.0, increment=1.0, width=4).pack(side=tk.LEFT)

        ttk.Button(r3, text="↺ Defaults", width=8, command=self._reset_pid_defaults).pack(side=tk.LEFT, padx=(4, 0))

        # Heater Authority Row
        r4 = ttk.Frame(grp)
        r4.pack(fill=tk.X, pady=2)
        ttk.Label(r4, text="Heater Authority:", width=16).pack(side=tk.LEFT)
        ttk.Label(r4, text="Range:").pack(side=tk.LEFT, padx=1)
        ttk.Combobox(r4, textvariable=self.heater_range_var, values=["HI", "MID", "LOW"], width=5, state="readonly").pack(side=tk.LEFT, padx=2)
        ttk.Label(r4, text="Max Pwr:").pack(side=tk.LEFT, padx=(4, 1))
        ttk.Spinbox(r4, textvariable=self.max_power_var, from_=1.0, to=100.0, increment=5.0, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Label(r4, text="%").pack(side=tk.LEFT)

        # Duration Estimation Card
        est_card = ttk.Frame(grp, relief="groove", padding="4 3 4 3")
        est_card.pack(fill=tk.X, pady=(4, 1))
        self.lbl_est_summary = ttk.Label(
            est_card,
            text="⏱ Est. Cooling Duration: ~244 min (4h 04m) from 422 K to 300 K @ 0.5 K/min",
            font=("Segoe UI", 8, "bold"),
            foreground="#0369a1"
        )
        self.lbl_est_summary.pack(anchor=tk.W)

    def _build_wayne_kerr_panel(self, parent):
        grp = ttk.LabelFrame(parent, text=" 2. Wayne Kerr 6510B Fixed Frequency (10 kHz) ", padding="6 4 6 4")
        grp.pack(fill=tk.X, pady=2)

        # Fixed Frequency
        r1 = ttk.Frame(grp)
        r1.pack(fill=tk.X, pady=2)
        ttk.Label(r1, text="Fixed Frequency:", width=16).pack(side=tk.LEFT)
        self.entry_freq = ttk.Entry(r1, textvariable=self.fixed_freq_var, width=10, state="readonly")
        self.entry_freq.pack(side=tk.LEFT)
        ttk.Label(r1, text="Hz  (10.0 kHz Fixed)", font=("Segoe UI", 8, "bold"), foreground="#15803d").pack(side=tk.LEFT, padx=4)

        # Function & Circuit Model
        r2 = ttk.Frame(grp)
        r2.pack(fill=tk.X, pady=2)
        ttk.Label(r2, text="Function & Mode:", width=16).pack(side=tk.LEFT)
        ttk.Label(r2, text="R (Ω) & X (Ω)  |  Series (SER)  |  FAST", font=("Segoe UI", 8, "bold"), foreground="#0f172a").pack(side=tk.LEFT)

        # Drive Level & Interval
        r3 = ttk.Frame(grp)
        r3.pack(fill=tk.X, pady=2)
        ttk.Label(r3, text="Drive (AC Bias):", width=16).pack(side=tk.LEFT)
        ttk.Spinbox(r3, textvariable=self.bias_mv_var, from_=10.0, to=1000.0, increment=10.0, width=6).pack(side=tk.LEFT)
        ttk.Label(r3, text="mV RMS").pack(side=tk.LEFT, padx=2)

        ttk.Label(r3, text="Pacing:").pack(side=tk.LEFT, padx=(6, 2))
        ttk.Spinbox(r3, textvariable=self.sample_interval_var, from_=0.2, to=10.0, increment=0.2, width=5).pack(side=tk.LEFT)
        ttk.Label(r3, text="sec").pack(side=tk.LEFT, padx=1)

        # File Saving Directory
        r4 = ttk.Frame(grp)
        r4.pack(fill=tk.X, pady=2)
        ttk.Label(r4, text="Data Directory:", width=16).pack(side=tk.LEFT)
        ttk.Entry(r4, textvariable=self.out_dir_var, width=16).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(r4, text="Browse", width=7, command=self._browse_dir).pack(side=tk.LEFT, padx=4)

    def _build_sample_panel(self, parent):
        grp = ttk.LabelFrame(parent, text=" 3. PMN-0.3PT Sample Geometry & Capacitance ", padding="6 4 6 4")
        grp.pack(fill=tk.X, pady=2)

        r1 = ttk.Frame(grp)
        r1.pack(fill=tk.X, pady=2)
        ttk.Label(r1, text="Thickness d:", width=12).pack(side=tk.LEFT)
        sp_d = ttk.Spinbox(r1, textvariable=self.sample_d_var, from_=0.01, to=10.0, increment=0.05, width=6, command=self._update_c0)
        sp_d.pack(side=tk.LEFT)
        sp_d.bind("<KeyRelease>", lambda e: self._update_c0())
        ttk.Label(r1, text="mm").pack(side=tk.LEFT, padx=2)

        ttk.Label(r1, text="Area A:", width=7).pack(side=tk.LEFT, padx=(6, 2))
        sp_a = ttk.Spinbox(r1, textvariable=self.sample_a_var, from_=0.1, to=100.0, increment=0.5, width=6, command=self._update_c0)
        sp_a.pack(side=tk.LEFT)
        sp_a.bind("<KeyRelease>", lambda e: self._update_c0())
        ttk.Label(r1, text="mm²").pack(side=tk.LEFT, padx=2)

        r2 = ttk.Frame(grp)
        r2.pack(fill=tk.X, pady=2)
        ttk.Label(r2, text="Vacuum C₀:", width=12).pack(side=tk.LEFT)
        c0_init = self._calculate_c0()
        self.lbl_c0 = ttk.Label(r2, text=f"{c0_init * 1e12:.3f} pF", font=("Segoe UI", 9, "bold"), foreground="#0369a1")
        self.lbl_c0.pack(side=tk.LEFT)
        ttk.Label(r2, text="(C₀ = ε₀·A/d for ε' derivation)", foreground="#64748b", font=("Segoe UI", 8, "italic")).pack(side=tk.LEFT, padx=4)

    def _build_execution_panel(self, parent):
        grp = ttk.LabelFrame(parent, text=" 4. Experiment Execution & Progress ", padding="6 4 6 4")
        grp.pack(fill=tk.X, pady=2)

        self.lbl_status = ttk.Label(
            grp,
            text="READY: Connect hardware and press Start to cool to 300 K.",
            font=("Segoe UI", 9, "bold"),
            foreground="#0284c7"
        )
        self.lbl_status.pack(anchor=tk.W, pady=1)

        # Progress bar
        self.progress_bar = ttk.Progressbar(grp, orient=tk.HORIZONTAL, mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=2)

        # Live Progress Readout
        self.lbl_progress_details = ttk.Label(
            grp,
            text="Cooling Progress: 0.0% | Elapsed: 00:00:00 | Remaining: --:--:--",
            font=("Segoe UI", 8)
        )
        self.lbl_progress_details.pack(anchor=tk.W, pady=1)

        self.lbl_points_logged = ttk.Label(
            grp,
            text="Points Logged: 0 | Current File: (none)",
            font=("Segoe UI", 8, "italic"),
            foreground="#475569"
        )
        self.lbl_points_logged.pack(anchor=tk.W, pady=1)

        # Action Buttons
        btn_row = ttk.Frame(grp)
        btn_row.pack(fill=tk.X, pady=4)

        self.btn_start = tk.Button(
            btn_row,
            text="▶ START COOLING EXPERIMENT",
            font=("Segoe UI", 9, "bold"),
            bg="#16a34a",
            fg="#ffffff",
            activebackground="#15803d",
            activeforeground="#ffffff",
            padx=10,
            pady=3,
            command=self.start_experiment
        )
        self.btn_start.pack(side=tk.LEFT, padx=2)

        self.btn_abort = tk.Button(
            btn_row,
            text="⏹ Abort",
            font=("Segoe UI", 9),
            bg="#e2e8f0",
            padx=8,
            pady=3,
            state=tk.DISABLED,
            command=self.abort_experiment
        )
        self.btn_abort.pack(side=tk.LEFT, padx=4)

    # -------------------------------------------------------------------------
    # Right Visualization Tabs
    # -------------------------------------------------------------------------

    def _build_visualizer(self, parent):
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # ---------------------------------------------------------------------
        # Tab 1: Live Data Table (User Requested Exact Format)
        # ---------------------------------------------------------------------
        tab1 = ttk.Frame(self.notebook, padding="4")
        self.notebook.add(tab1, text="  📋 Live Data Table  ")

        # Top toolbar for table
        tb_table = ttk.Frame(tab1)
        tb_table.pack(fill=tk.X, side=tk.TOP, pady=(0, 4))

        self.lbl_table_count = ttk.Label(tb_table, text="Points Logged: 0", font=("Segoe UI", 9, "bold"), foreground="#0369a1")
        self.lbl_table_count.pack(side=tk.LEFT, padx=4)

        ttk.Checkbutton(tb_table, text="Auto-scroll to latest", variable=self.autoscroll_table_var).pack(side=tk.LEFT, padx=12)

        self.lbl_auto_save_badge = ttk.Label(
            tb_table,
            text="● Auto-Saving Live to Data/ (.dat & .csv unbuffered)",
            font=("Segoe UI", 9, "bold"),
            foreground="#16a34a"
        )
        self.lbl_auto_save_badge.pack(side=tk.RIGHT, padx=6)
        ttk.Button(tb_table, text="Clear Table", command=self.clear_table).pack(side=tk.RIGHT, padx=4)

        # Treeview for Table
        # Exact columns requested: T (K) | f (Fixed) | R (ohm) | X (ohm)
        cols = ("t_k", "f_fixed", "r_ohm", "x_ohm", "time_s", "cp_pf", "tan_d", "eps_prime", "heater_pct")
        self.table = ttk.Treeview(tab1, columns=cols, show="headings", height=24)

        self.table.heading("t_k", text="T (K)")
        self.table.heading("f_fixed", text="f (Fixed)")
        self.table.heading("r_ohm", text="R (ohm)")
        self.table.heading("x_ohm", text="X (ohm)")
        self.table.heading("time_s", text="Time (s)")
        self.table.heading("cp_pf", text="Cp (pF)")
        self.table.heading("tan_d", text="Tan δ")
        self.table.heading("eps_prime", text="ε'")
        self.table.heading("heater_pct", text="Heater (%)")

        self.table.column("t_k", width=95, anchor=tk.CENTER)
        self.table.column("f_fixed", width=105, anchor=tk.CENTER)
        self.table.column("r_ohm", width=130, anchor=tk.E)
        self.table.column("x_ohm", width=130, anchor=tk.E)
        self.table.column("time_s", width=85, anchor=tk.CENTER)
        self.table.column("cp_pf", width=100, anchor=tk.E)
        self.table.column("tan_d", width=90, anchor=tk.CENTER)
        self.table.column("eps_prime", width=95, anchor=tk.E)
        self.table.column("heater_pct", width=85, anchor=tk.CENTER)

        table_scroll_y = ttk.Scrollbar(tab1, orient="vertical", command=self.table.yview)
        table_scroll_x = ttk.Scrollbar(tab1, orient="horizontal", command=self.table.xview)
        self.table.configure(yscrollcommand=table_scroll_y.set, xscrollcommand=table_scroll_x.set)

        table_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        table_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.table.pack(fill=tk.BOTH, expand=True)

        # ---------------------------------------------------------------------
        # Tab 2: R & X vs. Temperature T (K)
        # ---------------------------------------------------------------------
        tab2 = ttk.Frame(self.notebook)
        self.notebook.add(tab2, text="  📉 R & X vs. Temp (10 kHz)  ")
        self.fig2 = Figure(figsize=(7, 5), dpi=100)
        self.ax2_r = self.fig2.add_subplot(211)
        self.ax2_x = self.fig2.add_subplot(212, sharex=self.ax2_r)
        self.fig2.tight_layout(pad=2.2)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=tab2)
        self.canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        toolbar2 = NavigationToolbar2Tk(self.canvas2, tab2)
        toolbar2.update()

        # ---------------------------------------------------------------------
        # Tab 3: Permittivity ε' & Tan δ vs. Temperature T (K)
        # ---------------------------------------------------------------------
        tab3 = ttk.Frame(self.notebook)
        self.notebook.add(tab3, text="  ⚡ Permittivity ε' vs. Temp  ")
        self.fig3 = Figure(figsize=(7, 5), dpi=100)
        self.ax3_eps = self.fig3.add_subplot(211)
        self.ax3_tan = self.fig3.add_subplot(212, sharex=self.ax3_eps)
        self.fig3.tight_layout(pad=2.2)
        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=tab3)
        self.canvas3.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        toolbar3 = NavigationToolbar2Tk(self.canvas3, tab3)
        toolbar3.update()

        # ---------------------------------------------------------------------
        # Tab 4: Thermal Profile (T, Setpoint, Heater %) vs. Time
        # ---------------------------------------------------------------------
        tab4 = ttk.Frame(self.notebook)
        self.notebook.add(tab4, text="  📈 Thermal Profile vs. Time  ")

        tb4 = ttk.Frame(tab4, padding="3")
        tb4.pack(fill=tk.X, side=tk.TOP, pady=(0, 2))

        ttk.Label(tb4, text="Window:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(2, 4))
        self.combo_window = ttk.Combobox(
            tb4, width=8,
            values=["5 min", "15 min", "30 min", "1 hour", "All"],
            state="readonly"
        )
        self.combo_window.set("15 min")
        self.combo_window.bind("<<ComboboxSelected>>", self._on_window_change)
        self.combo_window.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Checkbutton(tb4, text="Temp A", variable=self.chk_show_temp, command=self._redraw_thermal_plot).pack(side=tk.LEFT, padx=3)
        ttk.Checkbutton(tb4, text="Setpoint", variable=self.chk_show_sp, command=self._redraw_thermal_plot).pack(side=tk.LEFT, padx=3)
        ttk.Checkbutton(tb4, text="Heater %", variable=self.chk_show_heater, command=self._redraw_thermal_plot).pack(side=tk.LEFT, padx=3)
        ttk.Checkbutton(tb4, text="Autoscale Y", variable=self.chk_autoscale_temp, command=self._redraw_thermal_plot).pack(side=tk.LEFT, padx=3)

        ttk.Button(tb4, text="⛶ Fit Scale", command=self._redraw_thermal_plot).pack(side=tk.RIGHT, padx=4)

        self.fig4 = Figure(figsize=(7, 5), dpi=100)
        self.ax4_t = self.fig4.add_subplot(111)
        self.ax4_h = self.ax4_t.twinx()
        self.ax4_h.yaxis.tick_right()
        self.ax4_h.yaxis.set_label_position("right")
        self.fig4.tight_layout(pad=2.0)
        self.canvas4 = FigureCanvasTkAgg(self.fig4, master=tab4)
        self.canvas4.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        toolbar4 = NavigationToolbar2Tk(self.canvas4, tab4)
        toolbar4.update()

        # ---------------------------------------------------------------------
        # Tab 5: Impedance & Nyquist
        # ---------------------------------------------------------------------
        tab5 = ttk.Frame(self.notebook)
        self.notebook.add(tab5, text="  🔄 Complex Impedance  ")
        self.fig5 = Figure(figsize=(7, 5), dpi=100)
        self.ax5_z = self.fig5.add_subplot(211)
        self.ax5_ny = self.fig5.add_subplot(212)
        self.fig5.tight_layout(pad=2.2)
        self.canvas5 = FigureCanvasTkAgg(self.fig5, master=tab5)
        self.canvas5.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        toolbar5 = NavigationToolbar2Tk(self.canvas5, tab5)
        toolbar5.update()

        # ---------------------------------------------------------------------
        # Tab 6: Real Relative Permittivity ε' vs. Temperature T (K) ONLY
        # ---------------------------------------------------------------------
        tab6 = ttk.Frame(self.notebook)
        self.notebook.add(tab6, text="  ⚡ ε' vs. Temperature  ")

        tb6 = ttk.Frame(tab6, padding="4")
        tb6.pack(fill=tk.X, side=tk.TOP, pady=(0, 2))

        self.lbl_tab6_live = ttk.Label(tb6, text="Live ε': --.-  |  T: --.--- K", font=("Segoe UI", 10, "bold"), foreground="#0369a1")
        self.lbl_tab6_live.pack(side=tk.LEFT, padx=6)

        self.lbl_tab6_peak = ttk.Label(tb6, text="Max Peak ε' (Curie Tm): --.- at --.- K", font=("Segoe UI", 9, "bold"), foreground="#15803d")
        self.lbl_tab6_peak.pack(side=tk.LEFT, padx=12)

        ttk.Button(tb6, text="⛶ Fit Scale", command=self._redraw_tab6_plot).pack(side=tk.RIGHT, padx=4)

        self.fig6 = Figure(figsize=(7.5, 5.2), dpi=100)
        self.ax6_eps = self.fig6.add_subplot(111)
        self.fig6.tight_layout(pad=2.2)
        self.canvas6 = FigureCanvasTkAgg(self.fig6, master=tab6)
        self.canvas6.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        toolbar6 = NavigationToolbar2Tk(self.canvas6, tab6)
        toolbar6.update()

        self._init_empty_plots()
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _init_empty_plots(self):
        # Tab 2
        self.ax2_r.clear()
        self.ax2_r.set_title("Real Resistance R (Ω) vs. Temperature T (K) [10 kHz Fixed]", fontsize=10, fontweight="bold")
        self.ax2_r.set_ylabel("R (Ω)")
        self.ax2_r.grid(True, linestyle="--", alpha=0.5)

        self.ax2_x.clear()
        self.ax2_x.set_title("Reactance X (Ω) vs. Temperature T (K) [10 kHz Fixed]", fontsize=10, fontweight="bold")
        self.ax2_x.set_xlabel("Temperature T (K)")
        self.ax2_x.set_ylabel("X (Ω)")
        self.ax2_x.grid(True, linestyle="--", alpha=0.5)
        self.canvas2.draw_idle()

        # Tab 3
        self.ax3_eps.clear()
        self.ax3_eps.set_title("Real Relative Permittivity ε' vs. Temperature T (K) [10 kHz]", fontsize=10, fontweight="bold")
        self.ax3_eps.set_ylabel("Permittivity ε'")
        self.ax3_eps.grid(True, linestyle="--", alpha=0.5)

        self.ax3_tan.clear()
        self.ax3_tan.set_title("Dielectric Loss Tangent Tan δ vs. Temperature T (K)", fontsize=10, fontweight="bold")
        self.ax3_tan.set_xlabel("Temperature T (K)")
        self.ax3_tan.set_ylabel("Tan δ")
        self.ax3_tan.grid(True, linestyle="--", alpha=0.5)
        self.canvas3.draw_idle()

        # Tab 4
        self.ax4_t.clear()
        self.ax4_h.clear()
        self.ax4_t.set_title("Cryo-con 22C — Continuous Cooling Thermal Profile", fontsize=10, fontweight="bold")
        self.ax4_t.set_xlabel("Elapsed Time (s)")
        self.ax4_t.set_ylabel("Temperature (K)", color="#0066cc")
        self.ax4_h.set_ylabel("Heater Output (%)", color="#8e24aa")
        self.ax4_h.set_ylim(0, 105)
        self.ax4_t.grid(True, linestyle="--", alpha=0.4)
        self.canvas4.draw_idle()

        # Tab 5
        self.ax5_z.clear()
        self.ax5_z.set_title("Impedance Magnitude |Z| vs. Temperature T (K)", fontsize=10, fontweight="bold")
        self.ax5_z.set_ylabel("|Z| (Ω)")
        self.ax5_z.grid(True, linestyle="--", alpha=0.5)

        self.ax5_ny.clear()
        self.ax5_ny.set_title("Cole-Cole Nyquist Plot: -X vs. R (10 kHz)", fontsize=10, fontweight="bold")
        self.ax5_ny.set_xlabel("R (Ω)")
        self.ax5_ny.set_ylabel("-X (Ω)")
        self.ax5_ny.grid(True, linestyle="--", alpha=0.5)
        self.canvas5.draw_idle()

        # Tab 6: Only ε' vs T
        self.ax6_eps.clear()
        self.ax6_eps.set_title("PMN-0.3PT — Real Relative Permittivity ε' vs. Temperature T (K) [10 kHz Fixed]", fontsize=11, fontweight="bold")
        self.ax6_eps.set_xlabel("Temperature T (K)", fontsize=10, fontweight="bold")
        self.ax6_eps.set_ylabel("Real Relative Permittivity ε'", fontsize=10, fontweight="bold")
        self.ax6_eps.grid(True, linestyle="--", alpha=0.5)
        self.canvas6.draw_idle()

    # -------------------------------------------------------------------------
    # Sample Geometry & Capacitance
    # -------------------------------------------------------------------------

    def _calculate_c0(self) -> float:
        d_m = max(1e-6, self.sample_d_var.get() * 1e-3)
        a_m2 = max(1e-8, self.sample_a_var.get() * 1e-6)
        return EPSILON_0 * (a_m2 / d_m)

    def _update_c0(self):
        c0 = self._calculate_c0()
        self.lbl_c0.config(text=f"{c0 * 1e12:.3f} pF")
        if self.orchestrator:
            self.orchestrator.update_sample_geometry(self.sample_d_var.get(), self.sample_a_var.get())

    def _reset_pid_defaults(self):
        self.p_gain_var.set(70.0)
        self.i_gain_var.set(900.0)
        self.d_gain_var.set(0.0)
        self.cooling_rate_var.set(0.50)
        self.max_power_var.set(100.0)
        self.heater_range_var.set("HI")

    def _browse_dir(self):
        folder = filedialog.askdirectory(initialdir=self.out_dir_var.get())
        if folder:
            self.out_dir_var.set(folder)

    def _on_window_change(self, event=None):
        sel = self.combo_window.get()
        mapping = {
            "5 min": 300,
            "15 min": 900,
            "30 min": 1800,
            "1 hour": 3600,
            "All": 999999999
        }
        self.thermal_plot_window_s = mapping.get(sel, 900)
        self._redraw_thermal_plot()

    # -------------------------------------------------------------------------
    # Hardware Connection Management
    # -------------------------------------------------------------------------

    def connect_hardware(self):
        port = self.cryo_port_var.get().strip()
        baud = int(self.cryo_baud_var.get().strip())
        mock = self.mock_var.get()
        visa_res = self.wk_visa_var.get().strip()

        self.lbl_status.config(text="Connecting to hardware instruments...", foreground="#0284c7")
        self.root.update_idletasks()

        self.cryocon = Cryocon22C(port=port, baud_rate=baud, mock=mock)
        c_ok = self.cryocon.connect()

        self.wayne_kerr = WayneKerr6500B(resource_name=visa_res, mock=mock)
        w_ok = self.wayne_kerr.connect()

        if c_ok and w_ok:
            status_txt = "[CONNECTED - MOCK SIMULATION]" if mock else "[CONNECTED - LIVE HARDWARE]"
            color = "#7c3aed" if mock else "#16a34a"
            self.lbl_conn_status.config(text=status_txt, foreground=color)
            self.btn_connect.config(state=tk.DISABLED)
            self.btn_disconnect.config(state=tk.NORMAL)
            self.lbl_status.config(text="Both instruments connected successfully. Ready to start cooling.", foreground="#16a34a")

            # Read initial temperature
            t_init = self.cryocon.read_temperature("A")
            self.lbl_digit_temp.config(text=f"{t_init:.3f} K")
            self.start_temp_var.set(round(t_init, 2))

            # Start idle background telemetry monitor
            self._monitor_active = True
            threading.Thread(target=self._background_telemetry_monitor, daemon=True).start()

        elif c_ok and not w_ok:
            if self.wayne_kerr:
                self.wayne_kerr.disconnect()
                self.wayne_kerr = None
            self.lbl_conn_status.config(text="[CRYOCON ONLY]", foreground="#d97706")
            self.btn_connect.config(state=tk.DISABLED)
            self.btn_disconnect.config(state=tk.NORMAL)
            self.lbl_status.config(text=f"Cryocon 22C connected on {port}. Wayne Kerr offline ({visa_res} not found).", foreground="#d97706")
            messagebox.showwarning("Wayne Kerr Offline", f"Connected to Cryocon 22C on {port}.\nWayne Kerr on {visa_res} was not found.")
            self._monitor_active = True
            threading.Thread(target=self._background_telemetry_monitor, daemon=True).start()
        else:
            err = []
            if not c_ok:
                err.append(f"Cryocon 22C on {port}")
            if not w_ok:
                err.append(f"Wayne Kerr on {visa_res}")
            messagebox.showerror(
                "Connection Failed",
                f"Could not connect to:\n" + "\n".join(err) +
                "\n\nNote: If 'unified_gui.py' is still running, close it first as Windows allows only one process on COM5.\nTip: Enable 'Mock Mode' for offline simulation."
            )
            self.disconnect_hardware()

    def disconnect_hardware(self):
        self._monitor_active = False
        if self.orchestrator and self.orchestrator.is_running:
            self.orchestrator.request_abort()

        if self.cryocon:
            self.cryocon.disconnect()
            self.cryocon = None
        if self.wayne_kerr:
            self.wayne_kerr.disconnect()
            self.wayne_kerr = None

        self.lbl_conn_status.config(text="[DISCONNECTED]", foreground="#dc2626")
        self.btn_connect.config(state=tk.NORMAL)
        self.btn_disconnect.config(state=tk.DISABLED)
        self.lbl_status.config(text="Hardware disconnected.", foreground="#64748b")

    def _background_telemetry_monitor(self):
        """Continuously polls temperature when idle (suspended during active experiment)."""
        while getattr(self, "_monitor_active", False):
            if self.orchestrator and getattr(self.orchestrator, "is_running", False):
                time.sleep(0.5)
                continue
            if self.cryocon and getattr(self.cryocon, "is_arming", False):
                time.sleep(0.5)
                continue

            if self.cryocon and self.cryocon.connected:
                try:
                    t_val = self.cryocon.read_temperature("A")
                    sp_val = self.cryocon.get_setpoint(1)
                    h_val = self.cryocon.read_heater_output(1)
                    now = time.time()
                    self.ui_queue.put(("idle_tick", (now, t_val, sp_val, h_val)))
                except Exception:
                    pass
            time.sleep(1.0)

    # -------------------------------------------------------------------------
    # Experiment Execution
    # -------------------------------------------------------------------------

    def start_experiment(self):
        if not self.cryocon or not self.cryocon.connected:
            messagebox.showwarning("Not Connected", "Please connect hardware or enable 'Mock Mode' first.")
            return

        if not self.wayne_kerr or not self.wayne_kerr.connected:
            messagebox.showwarning(
                "Wayne Kerr Required",
                "Cannot start continuous cooling impedance experiment:\n"
                "Wayne Kerr 6510B impedance analyzer is not connected.\n\n"
                "Please connect GPIB/VISA or enable 'Mock Mode'."
            )
            return

        tgt_temp = self.target_temp_var.get()
        rate = self.cooling_rate_var.get()
        p_gain = self.p_gain_var.get()
        i_gain = self.i_gain_var.get()
        d_gain = self.d_gain_var.get()
        max_power = self.max_power_var.get()
        htr_range = self.heater_range_var.get().strip().upper()
        pacing = self.sample_interval_var.get()
        out_dir = self.out_dir_var.get().strip()

        # Update button states
        self.btn_start.config(state=tk.DISABLED)
        self.btn_abort.config(state=tk.NORMAL)

        # Initialize Orchestrator
        self.orchestrator = CoolingOrchestrator(
            cryocon=self.cryocon,
            wayne_kerr=self.wayne_kerr,
            target_temp=tgt_temp,
            ramp_rate=rate,
            fixed_freq_hz=10000.0,
            drive_level_v=self.bias_mv_var.get() / 1000.0,
            sample_interval_s=pacing,
            sample_thickness_mm=self.sample_d_var.get(),
            sample_area_mm2=self.sample_a_var.get(),
            p_gain=p_gain,
            i_gain=i_gain,
            d_gain=d_gain,
            max_power=max_power,
            heater_range=htr_range,
            out_dir=out_dir,
            file_prefix="Cooling_10kHz",
            on_point_acquired=lambda pt: self.ui_queue.put(("point_acquired", pt)),
            on_status_update=lambda st: self.ui_queue.put(("status_update", st))
        )

        def _worker():
            try:
                self.orchestrator.run()
            except Exception as e:
                self.ui_queue.put(("experiment_error", str(e)))
            finally:
                self.ui_queue.put(("experiment_done", None))

        self.worker_thread = threading.Thread(target=_worker, daemon=True)
        self.worker_thread.start()

    def abort_experiment(self):
        if self.orchestrator and self.orchestrator.is_running:
            self.lbl_status.config(text="ABORTING: Cutting heater power to 0% and stopping...", foreground="#dc2626")
            self.orchestrator.request_abort()

    def emergency_stop(self):
        """Hard emergency cut: sends STOP command immediately."""
        self.lbl_status.config(text="EMERGENCY STOP TRIGGERED: Disengaging heater!", foreground="#dc2626")
        if self.orchestrator:
            self.orchestrator.request_abort()
        if self.cryocon:
            threading.Thread(target=self.cryocon.stop_control, daemon=True).start()
        messagebox.showwarning("Emergency Stop", "Emergency STOP command dispatched.\nHeater power zeroed (CONTROL = OFF).")

    def destroy_cleanly(self):
        """Cleanly cancel all Tk after jobs and disconnect hardware."""
        self._alive = False
        if self._poll_job is not None:
            try:
                self.root.after_cancel(self._poll_job)
            except Exception:
                pass
            self._poll_job = None
        self._monitor_active = False

    def _on_window_close(self):
        if self.orchestrator and self.orchestrator.is_running:
            if not messagebox.askyesno("Exit Confirmation", "Cooling experiment is currently running!\nDo you want to abort and disengage the heater?"):
                return
            self.orchestrator.request_abort()
        self.destroy_cleanly()
        if self.cryocon:
            try:
                self.cryocon.stop_control()
            except Exception:
                pass
            self.cryocon.disconnect()
        if self.wayne_kerr:
            self.wayne_kerr.disconnect()
        self.root.destroy()

    # -------------------------------------------------------------------------
    # UI Dispatcher & Live Plotting Engine
    # -------------------------------------------------------------------------

    def _start_ui_dispatcher(self):
        def _poll_queue():
            if not getattr(self, "_alive", True):
                return
            try:
                while True:
                    msg_type, payload = self.ui_queue.get_nowait()
                    self._handle_ui_message(msg_type, payload)
            except queue.Empty:
                pass
            except Exception:
                pass
            if getattr(self, "_alive", True):
                try:
                    self._poll_job = self.root.after(100, _poll_queue)
                except Exception:
                    pass

        try:
            self._poll_job = self.root.after(100, _poll_queue)
        except Exception:
            pass

    def _handle_ui_message(self, msg_type: str, payload: Any):
        if msg_type == "idle_tick":
            t_stamp, t_val, sp_val, h_val = payload
            self.lbl_digit_temp.config(text=f"{t_val:.3f} K")
            if not math.isnan(sp_val):
                self.lbl_digit_setpt.config(text=f"{sp_val:.2f} K")
            self.lbl_digit_heater.config(text=f"{h_val:.1f} %")

        elif msg_type == "status_update":
            st = payload
            phase = st.get("phase", "IDLE")
            cur_t = st.get("current_temp_k", 0.0)
            tgt_t = st.get("target_temp_k", 300.0)
            sp_t = st.get("setpoint_k", tgt_t)
            htr = st.get("heater_pct", 0.0)
            elapsed_s = st.get("elapsed_s", 0.0)
            rem_s = st.get("remaining_s", 0.0)
            prog_pct = st.get("progress_pct", 0.0)
            pts_cnt = st.get("points_count", 0)
            fpath = st.get("filepath", "")

            self.lbl_digit_temp.config(text=f"{cur_t:.3f} K")
            self.lbl_digit_setpt.config(text=f"{sp_t:.2f} K")
            self.lbl_digit_heater.config(text=f"{htr:.1f} %")

            if phase == "ARMING":
                self.lbl_status.config(text="ARMING: Synchronizing setpoint & arming anti-surge cooling ramp...", foreground="#e65100")
            elif phase == "COOLING":
                self.lbl_status.config(text=f"COOLING: Ramping from {self.start_temp_var.get():.1f} K to {tgt_t:.1f} K @ {self.cooling_rate_var.get():.2f} K/min", foreground="#16a34a")
                self.progress_bar["value"] = prog_pct

                # Format time
                el_h = int(elapsed_s // 3600)
                el_m = int((elapsed_s % 3600) // 60)
                el_s = int(elapsed_s % 60)

                rem_h = int(rem_s // 3600)
                rem_m = int((rem_s % 3600) // 60)
                rem_s_i = int(rem_s % 60)

                self.lbl_progress_details.config(
                    text=f"Cooling Progress: {prog_pct:.1f}% | Elapsed: {el_h:02d}:{el_m:02d}:{el_s:02d} | Remaining: ~{rem_h:02d}:{rem_m:02d}:{rem_s_i:02d}"
                )
                self.lbl_points_logged.config(text=f"Points Logged: {pts_cnt:,} | File: {os.path.basename(fpath)}")

            elif phase == "COMPLETE":
                self.lbl_status.config(text="COOLING EXPERIMENT COMPLETE! Reached 300.0 K.", foreground="#15803d")
                self.progress_bar["value"] = 100.0
            elif phase == "ABORTED":
                self.lbl_status.config(text="EXPERIMENT ABORTED: Heater disengaged (CONTROL = OFF).", foreground="#dc2626")

        elif msg_type == "point_acquired":
            pt = payload
            t_curr = pt["temp_k"]
            f_fix = pt["freq_fixed"]
            r_val = pt["r_ohm"]
            x_val = pt["x_ohm"]
            el_s = pt["elapsed_s"]
            cp_val = pt["cp_farad"]
            tan_d = pt["tan_delta"]
            eps_val = pt["eps_prime"]
            htr_val = pt["heater_pct"]
            sp_val = pt["setpoint_k"]
            z_mag = pt["z_mag_ohm"]
            th_deg = pt["theta_deg"]

            # 1. Insert into Live Table
            # Requested table format: T (K) | f (Fixed) | R (ohm) | X (ohm)
            f_str = f"{f_fix/1000.0:.1f} kHz"
            cp_pf = cp_val * 1e12
            row_id = self.table.insert(
                "",
                tk.END,
                values=(
                    f"{t_curr:.3f}",
                    f_str,
                    f"{r_val:.2e}",
                    f"{x_val:.2e}",
                    f"{el_s:.1f}",
                    f"{cp_pf:.2f}",
                    f"{tan_d:.4f}",
                    f"{eps_val:.1f}",
                    f"{htr_val:.1f}"
                )
            )

            if self.autoscroll_table_var.get():
                self.table.see(row_id)

            self.lbl_table_count.config(text=f"Points Logged: {pt['point_idx']:,}")

            # 2. Append to Plot History Buffers
            now = time.time()
            self.time_history.append(now)
            self.temp_history.append(t_curr)
            self.sp_history.append(sp_val)
            self.heater_history.append(htr_val)
            self.r_history.append(r_val)
            self.x_history.append(x_val)
            self.eps_history.append(eps_val)
            self.tand_history.append(tan_d)
            self.z_history.append(z_mag)
            self.theta_history.append(th_deg)

            # Rate limit redraw to 2 Hz (0.5 s) to maintain GUI fluidity
            if now - self.last_chart_draw >= 0.5:
                self.last_chart_draw = now
                self._redraw_all_plots()

        elif msg_type == "experiment_error":
            err_msg = payload
            messagebox.showerror("Experiment Error", f"Error during continuous cooling experiment:\n{err_msg}")
            self.btn_start.config(state=tk.NORMAL)
            self.btn_abort.config(state=tk.DISABLED)

        elif msg_type == "experiment_done":
            self.btn_start.config(state=tk.NORMAL)
            self.btn_abort.config(state=tk.DISABLED)
            self._redraw_all_plots(force_all=True)

    # -------------------------------------------------------------------------
    # Matplotlib Redraw Engine
    # -------------------------------------------------------------------------

    def _on_tab_changed(self, event=None):
        """Redraw the newly selected tab immediately upon user navigation."""
        self._redraw_active_tab()

    def _redraw_active_tab(self):
        if not self.temp_history:
            return
        try:
            tab_id = self.notebook.select()
            idx = self.notebook.index(tab_id) if tab_id else -1
        except Exception:
            idx = -1

        if idx == 1:
            self._redraw_tab2_plot()
        elif idx == 2:
            self._redraw_tab3_plot()
        elif idx == 3:
            self._redraw_thermal_plot()
        elif idx == 4:
            self._redraw_tab5_plot()
        elif idx == 5:
            self._redraw_tab6_plot()

    def _redraw_all_plots(self, force_all: bool = False):
        """Redraw plots. In continuous mode, redraws only the active tab for maximum UI fluidity."""
        if not self.temp_history:
            return

        if not force_all:
            self._redraw_active_tab()
            return

        self._redraw_tab2_plot()
        self._redraw_tab3_plot()
        self._redraw_thermal_plot()
        self._redraw_tab5_plot()
        self._redraw_tab6_plot()

    def _redraw_tab2_plot(self):
        if not self.temp_history:
            return
        temps = self.temp_history
        rs = self.r_history
        xs = self.x_history

        self.ax2_r.clear()
        self.ax2_r.set_title("Real Resistance R (Ω) vs. Temperature T (K) [10 kHz Fixed]", fontsize=10, fontweight="bold")
        self.ax2_r.plot(temps, rs, color="#1e40af", lw=1.6, label="R (Ω)")
        self.ax2_r.set_ylabel("R (Ω)")
        self.ax2_r.grid(True, linestyle="--", alpha=0.5)
        self.ax2_r.legend(loc="best", fontsize=8)

        self.ax2_x.clear()
        self.ax2_x.set_title("Reactance X (Ω) vs. Temperature T (K) [10 kHz Fixed]", fontsize=10, fontweight="bold")
        self.ax2_x.plot(temps, xs, color="#b91c1c", lw=1.6, label="X (Ω)")
        self.ax2_x.set_xlabel("Temperature T (K)")
        self.ax2_x.set_ylabel("X (Ω)")
        self.ax2_x.grid(True, linestyle="--", alpha=0.5)
        self.ax2_x.legend(loc="best", fontsize=8)
        self.canvas2.draw_idle()

    def _redraw_tab3_plot(self):
        if not self.temp_history:
            return
        temps = self.temp_history
        epss = self.eps_history
        tans = self.tand_history

        self.ax3_eps.clear()
        self.ax3_eps.set_title("Real Relative Permittivity ε' vs. Temperature T (K) [10 kHz]", fontsize=10, fontweight="bold")
        self.ax3_eps.plot(temps, epss, color="#059669", lw=1.8, label="ε' (10 kHz)")
        self.ax3_eps.set_ylabel("Permittivity ε'")
        self.ax3_eps.grid(True, linestyle="--", alpha=0.5)
        self.ax3_eps.legend(loc="best", fontsize=8)

        self.ax3_tan.clear()
        self.ax3_tan.set_title("Dielectric Loss Tangent Tan δ vs. Temperature T (K)", fontsize=10, fontweight="bold")
        self.ax3_tan.plot(temps, tans, color="#d97706", lw=1.6, label="Tan δ")
        self.ax3_tan.set_xlabel("Temperature T (K)")
        self.ax3_tan.set_ylabel("Tan δ")
        self.ax3_tan.grid(True, linestyle="--", alpha=0.5)
        self.ax3_tan.legend(loc="best", fontsize=8)
        self.canvas3.draw_idle()

    def _redraw_tab5_plot(self):
        if not self.temp_history:
            return
        temps = self.temp_history
        rs = self.r_history
        xs = self.x_history

        self.ax5_z.clear()
        self.ax5_z.set_title("Impedance Magnitude |Z| vs. Temperature T (K)", fontsize=10, fontweight="bold")
        self.ax5_z.plot(temps, self.z_history, color="#7c3aed", lw=1.6, label="|Z| (Ω)")
        self.ax5_z.set_ylabel("|Z| (Ω)")
        self.ax5_z.grid(True, linestyle="--", alpha=0.5)
        self.ax5_z.legend(loc="best", fontsize=8)

        self.ax5_ny.clear()
        self.ax5_ny.set_title("Cole-Cole Nyquist Plot: -X vs. R (10 kHz Fixed)", fontsize=10, fontweight="bold")
        neg_xs = [-x for x in xs]
        self.ax5_ny.scatter(rs, neg_xs, c=temps, cmap="coolwarm", s=10, alpha=0.8)
        self.ax5_ny.set_xlabel("R (Ω)")
        self.ax5_ny.set_ylabel("-X (Ω)")
        self.ax5_ny.grid(True, linestyle="--", alpha=0.5)
        self.canvas5.draw_idle()

    def _redraw_tab6_plot(self):
        if not self.temp_history or not self.eps_history:
            return
        temps = self.temp_history
        epss = self.eps_history

        self.ax6_eps.clear()
        self.ax6_eps.set_title("PMN-0.3PT — Real Relative Permittivity ε' vs. Temperature T (K) [10 kHz Fixed]", fontsize=11, fontweight="bold")
        self.ax6_eps.plot(temps, epss, color="#0284c7", lw=2.2, marker="o", markersize=3, label="ε' (10 kHz)")
        self.ax6_eps.set_xlabel("Temperature T (K)", fontsize=10, fontweight="bold")
        self.ax6_eps.set_ylabel("Real Relative Permittivity ε'", fontsize=10, fontweight="bold")
        self.ax6_eps.grid(True, linestyle="--", alpha=0.5)

        # Highlight maximum peak
        max_eps = max(epss)
        max_idx = epss.index(max_eps)
        t_max = temps[max_idx]
        self.ax6_eps.plot(t_max, max_eps, marker="*", markersize=12, color="#dc2626", label=f"Tm Peak: {max_eps:.1f} ({t_max:.1f} K)")
        self.ax6_eps.legend(loc="best", fontsize=9)

        # Update banner readouts
        self.lbl_tab6_live.config(text=f"Live ε': {epss[-1]:.1f}  |  T: {temps[-1]:.3f} K")
        self.lbl_tab6_peak.config(text=f"Max Peak ε' (Curie Tm): {max_eps:.1f} at {t_max:.2f} K")
        self.canvas6.draw_idle()

    def _redraw_thermal_plot(self):
        if not self.time_history:
            return

        now = self.time_history[-1]
        cutoff = now - self.thermal_plot_window_s
        indices = [i for i, t in enumerate(self.time_history) if t >= cutoff]

        if not indices:
            return

        t_rel = [self.time_history[i] - self.time_history[0] for i in indices]
        temps = [self.temp_history[i] for i in indices]
        sps = [self.sp_history[i] for i in indices]
        htrs = [self.heater_history[i] for i in indices]

        self.ax4_t.clear()
        self.ax4_h.clear()

        self.ax4_t.set_title("Cryo-con 22C — Continuous Cooling Thermal Profile", fontsize=10, fontweight="bold")
        self.ax4_t.set_xlabel("Elapsed Time (s)", fontsize=9)
        self.ax4_t.set_ylabel("Temperature (K)", color="#0066cc", fontsize=9)
        self.ax4_h.set_ylabel("Heater Output (%)", color="#8e24aa", fontsize=9)
        self.ax4_h.yaxis.set_label_position("right")
        self.ax4_h.yaxis.tick_right()

        if self.chk_show_temp.get():
            self.ax4_t.plot(t_rel, temps, color="#0066cc", lw=1.8, label="Temp A (K)")
        if self.chk_show_sp.get():
            self.ax4_t.plot(t_rel, sps, color="#e65100", lw=1.4, linestyle="--", label="Setpoint (K)")
        if self.chk_show_heater.get():
            self.ax4_h.plot(t_rel, htrs, color="#8e24aa", lw=1.2, alpha=0.6, label="Heater (%)")

        self.ax4_h.set_ylim(0, 105)
        if self.chk_autoscale_temp.get() and temps:
            min_t = min(min(temps), min(sps) if sps else min(temps)) - 1.0
            max_t = max(max(temps), max(sps) if max(temps) else max(temps)) + 1.0
            self.ax4_t.set_ylim(min_t, max_t)

        self.ax4_t.grid(True, linestyle="--", alpha=0.4)
        self.canvas4.draw_idle()

    # -------------------------------------------------------------------------
    # Table Operations & Export
    # -------------------------------------------------------------------------

    def clear_table(self):
        for item in self.table.get_children():
            self.table.delete(item)
        self.lbl_table_count.config(text="Points Logged: 0")

    def export_table_csv(self):
        if not self.table.get_children():
            messagebox.showinfo("Empty Table", "No data in table to export.")
            return

        fpath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            initialfile=f"PMN-PT_10kHz_Cooling_Table_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        if not fpath:
            return

        with open(fpath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Standard requested header
            writer.writerow(["T (K)", "f (Fixed)", "R (ohm)", "X (ohm)", "Time (s)", "Cp (pF)", "Tan δ", "ε'", "Heater (%)"])
            for row_id in self.table.get_children():
                writer.writerow(self.table.item(row_id)["values"])

        messagebox.showinfo("Export Complete", f"Successfully exported {len(self.table.get_children())} rows to:\n{fpath}")


def main():
    root = tk.Tk()
    app = CoolingGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
