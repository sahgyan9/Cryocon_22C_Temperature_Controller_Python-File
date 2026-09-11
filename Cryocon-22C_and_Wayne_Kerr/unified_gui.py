"""
Unified Laboratory Desktop GUI
==============================
Wayne Kerr 6510B Precision Impedance Analyzer & Cryo-con 22C Temperature Controller
Automated Temperature-Dependent Dielectric Spectroscopy Suite for PMN-PT Samples.

Pre-populated Default Parameters:
- Ramp Rate: 1.0 K/min
- PID Tuning: P=40, I=900 s, D=0, HI, 70%
- Frequency Sweep: 20 Hz to 10 MHz (200 Logarithmic points)
- AC Bias (Drive Level): 100 mV (0.100 V RMS)
- Measurement Parameters: R (Ohms) & X (Ohms) in Series Equivalent Circuit
- File Naming: <Tempr>_<Bais>_<time_stamp>.dat in Data/

Author: Lab Automation & Antigravity
Date: 2026-09-08
"""

import csv
import datetime
import glob
import math
import os
import queue
import re
import sys
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Nominal decade target frequencies for PMN-PT dielectric analysis
NOMINAL_TARGET_FREQS = [
    (1e3, "1 kHz", "#1f77b4", "o"),
    (1e4, "10 kHz", "#ff7f0e", "o"),
    (1e5, "100 kHz", "#2ca02c", "o"),
    (1e6, "1 MHz", "#d62728", "o"),
    (1e7, "10 MHz", "#9467bd", "o"),
]


import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from cryocon_controller import Cryocon22C
from wayne_kerr_controller import WayneKerr6500B
from unified_experiment_runner import ExperimentOrchestrator


class UnifiedLabGUI:
    """
    Unified laboratory control application.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Wayne Kerr 6510B & Cryo-con 22C — Unified Impedance Spectroscopy (PMN-0.3PT)")
        self.root.geometry("1420x860")
        self.root.minsize(1100, 640)

        # Communication instances
        self.cryocon: Optional[Cryocon22C] = None
        self.wayne_kerr: Optional[WayneKerr6500B] = None
        self.orchestrator: Optional[ExperimentOrchestrator] = None
        self.worker_thread: Optional[threading.Thread] = None

        # Threading queue for UI updates
        self.ui_queue: queue.Queue = queue.Queue()

        # Telemetry & plotting caches
        self.time_history: List[float] = []
        self.temp_history: List[float] = []
        self.sp_history: List[float] = []
        self.heater_history: List[float] = []
        self.sweep_events: List[Tuple[float, float]] = []  # (time, temp)

        # Cryo-con 22C Live Temperature Graph Configuration
        self.chk_show_a = tk.BooleanVar(value=True)
        self.chk_show_sp = tk.BooleanVar(value=True)
        self.chk_show_ht = tk.BooleanVar(value=True)
        self.chk_autoscale_temp = tk.BooleanVar(value=True)
        self.chk_autoscale_ht = tk.BooleanVar(value=False)
        self.plot_window_seconds = 600  # Default: 10 min
        self.max_plot_points = 3600
        self.last_chart_draw = 0.0
        self._last_sweep_thermal_time = 0.0

        self.current_sweep_freqs: List[float] = []
        self.current_sweep_r: List[float] = []
        self.current_sweep_x: List[float] = []
        self.current_sweep_z: List[float] = []
        self.current_sweep_theta: List[float] = []

        self.all_completed_sweeps: List[Dict[str, Any]] = []

        # PMN-PT Dielectric Permittivity State
        self.sample_d_var = tk.DoubleVar(value=0.30)  # Sample thickness d in mm
        self.sample_a_var = tk.DoubleVar(value=6.00)  # Electrode area A in mm^2
        self.permittivity_view_var = tk.StringVar(value="all")  # "all" or "bulk"
        self.permittivity_data: Dict[float, Dict[str, Any]] = {}

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
        self.style.configure("Status.TLabel", font=("Segoe UI", 9, "bold"), foreground="#2563eb")
        self.style.configure("Emergency.TButton", font=("Segoe UI", 10, "bold"), foreground="#ffffff", background="#dc2626")

    def _build_ui(self):
        # Top toolbar: Connections and Emergency Stop
        top_frame = ttk.Frame(self.root, padding="6 6 6 6")
        top_frame.pack(side=tk.TOP, fill=tk.X)

        # Cryocon connection
        ttk.Label(top_frame, text="Cryocon 22C Port:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=3)
        self.cryo_port_var = tk.StringVar(value="COM5")
        ttk.Entry(top_frame, textvariable=self.cryo_port_var, width=7).pack(side=tk.LEFT, padx=2)

        ttk.Label(top_frame, text="Baud:").pack(side=tk.LEFT, padx=2)
        self.cryo_baud_var = tk.StringVar(value="57600")
        ttk.Combobox(top_frame, textvariable=self.cryo_baud_var, values=["57600", "9600", "19200"], width=6, state="readonly").pack(side=tk.LEFT, padx=2)

        # Wayne Kerr connection
        ttk.Label(top_frame, text=" | Wayne Kerr VISA:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=4)
        self.wk_visa_var = tk.StringVar(value="GPIB0::6::INSTR")
        ttk.Entry(top_frame, textvariable=self.wk_visa_var, width=16).pack(side=tk.LEFT, padx=2)

        # Mock simulation toggle
        self.mock_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(top_frame, text="Mock Mode", variable=self.mock_var, command=self._on_mock_toggle).pack(side=tk.LEFT, padx=8)

        # Connect / Disconnect Buttons
        self.btn_connect = tk.Button(top_frame, text="Connect Hardware", font=("Segoe UI", 9, "bold"), bg="#2563eb", fg="#ffffff", relief="groove", command=self.connect_hardware)
        self.btn_connect.pack(side=tk.LEFT, padx=4)

        self.btn_disconnect = tk.Button(top_frame, text="Disconnect", font=("Segoe UI", 9), bg="#e2e8f0", relief="groove", state=tk.DISABLED, command=self.disconnect_hardware)
        self.btn_disconnect.pack(side=tk.LEFT, padx=4)

        self.lbl_conn_status = ttk.Label(top_frame, text="[DISCONNECTED]", foreground="#dc2626", font=("Segoe UI", 9, "bold"))
        self.lbl_conn_status.pack(side=tk.LEFT, padx=8)

        # Prominent Emergency Stop Button on top right
        self.btn_emergency_stop = tk.Button(
            top_frame,
            text="⚠ EMERGENCY STOP",
            font=("Segoe UI", 11, "bold"),
            bg="#dc2626",
            fg="#ffffff",
            activebackground="#b91c1c",
            activeforeground="#ffffff",
            padx=12,
            pady=2,
            relief="raised",
            command=self.emergency_stop
        )
        self.btn_emergency_stop.pack(side=tk.RIGHT, padx=6)

        # Main Layout: Left Control Panel (Scrollable Paned) + Right Plotting Canvas
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        # Left Container Frame holding Canvas & Scrollbar
        left_container = ttk.Frame(main_paned, width=460)
        main_paned.add(left_container, weight=0)

        right_container = ttk.Frame(main_paned, padding="4")
        main_paned.add(right_container, weight=1)

        # Scrollable Canvas for Left Panel
        self.left_canvas = tk.Canvas(left_container, borderwidth=0, highlightthickness=0, width=450)
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

        # Mousewheel scrolling: scrolls left canvas when mouse is anywhere over left_container
        def _on_left_mousewheel(event):
            try:
                x, y = self.root.winfo_pointerxy()
                w = self.root.winfo_containing(x, y)
                while w is not None:
                    if w == left_container or w == self.left_canvas or w == self.left_scrollable:
                        self.left_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                        return
                    w = getattr(w, "master", None)
            except Exception:
                pass

        def _on_linux_scroll_up(event):
            try:
                x, y = self.root.winfo_pointerxy()
                w = self.root.winfo_containing(x, y)
                while w is not None:
                    if w == left_container or w == self.left_canvas or w == self.left_scrollable:
                        self.left_canvas.yview_scroll(-1, "units")
                        return
                    w = getattr(w, "master", None)
            except Exception:
                pass

        def _on_linux_scroll_down(event):
            try:
                x, y = self.root.winfo_pointerxy()
                w = self.root.winfo_containing(x, y)
                while w is not None:
                    if w == left_container or w == self.left_canvas or w == self.left_scrollable:
                        self.left_canvas.yview_scroll(1, "units")
                        return
                    w = getattr(w, "master", None)
            except Exception:
                pass

        self.root.bind_all("<MouseWheel>", _on_left_mousewheel, add="+")
        self.root.bind_all("<Button-4>", _on_linux_scroll_up, add="+")
        self.root.bind_all("<Button-5>", _on_linux_scroll_down, add="+")

        # Build Left Control Sections inside scrollable frame
        self._build_thermal_panel(self.left_scrollable)
        self._build_impedance_panel(self.left_scrollable)
        self._build_sample_panel(self.left_scrollable)
        self._build_execution_panel(self.left_scrollable)

        # Build Right Visualization Section
        self._build_plotting_panel(right_container)

        # Attach dynamic live estimation traces
        self.ramp_rate_var.trace_add("write", self._update_estimated_time)
        self.soak_min_var.trace_add("write", self._update_estimated_time)
        self.target_temps_var.trace_add("write", self._update_estimated_time)
        self.num_pts_var.trace_add("write", self._update_estimated_time)
        self._update_estimated_time()

    def _build_thermal_panel(self, parent):
        grp = ttk.LabelFrame(parent, text=" 1. Temperature Ramp & Soak Control ", padding="6 3 6 3")
        grp.pack(fill=tk.X, pady=2)

        # Preset selection buttons
        preset_frame = ttk.Frame(grp)
        preset_frame.pack(fill=tk.X, pady=1)
        ttk.Label(preset_frame, text="Presets:").pack(side=tk.LEFT, padx=2)
        btn_test = ttk.Button(preset_frame, text="Test: 299, 300 K", command=self._set_preset_test)
        btn_test.pack(side=tk.LEFT, padx=3)
        btn_full = ttk.Button(preset_frame, text="Full: 300 to 470 K (Step 5)", command=self._set_preset_full)
        btn_full.pack(side=tk.LEFT, padx=3)

        # Target temperature list entry
        t_row = ttk.Frame(grp)
        t_row.pack(fill=tk.X, pady=2)
        ttk.Label(t_row, text="Target Temps (K):", width=15).pack(side=tk.LEFT)
        self.target_temps_var = tk.StringVar(value="300, 305, 310, 315, 320, 325, 330, 335, 340, 345, 350, 355, 360, 365, 370, 375, 380, 385, 390, 395, 400, 405, 410, 415, 420, 425, 430, 435, 440, 445, 450, 455, 460, 465, 470")
        ttk.Entry(t_row, textvariable=self.target_temps_var).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Thermal Soak Delay (Thermal Equilibration for PMN-PT)
        soak_row = ttk.Frame(grp)
        soak_row.pack(fill=tk.X, pady=2)
        ttk.Label(soak_row, text="Sample Soak (min):", width=15).pack(side=tk.LEFT)
        self.soak_min_var = tk.DoubleVar(value=5.0)
        ttk.Spinbox(soak_row, textvariable=self.soak_min_var, from_=0.1, to=60.0, increment=0.5, width=6).pack(side=tk.LEFT)
        ttk.Label(soak_row, text=" (PMN-PT thermal soak)", foreground="#475569", font=("Segoe UI", 8, "italic")).pack(side=tk.LEFT, padx=3)

        # Settle Band, Ramp Rate, Max Power, Range
        param_row = ttk.Frame(grp)
        param_row.pack(fill=tk.X, pady=2)
        ttk.Label(param_row, text="Settle Band (±K):").pack(side=tk.LEFT)
        self.settle_band_var = tk.DoubleVar(value=0.10)
        ttk.Spinbox(param_row, textvariable=self.settle_band_var, from_=0.02, to=1.0, increment=0.02, width=5).pack(side=tk.LEFT, padx=2)

        ttk.Label(param_row, text="Rate (K/min):").pack(side=tk.LEFT, padx=(4, 2))
        self.ramp_rate_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(param_row, textvariable=self.ramp_rate_var, from_=0.2, to=5.0, increment=0.5, width=5).pack(side=tk.LEFT, padx=2)

        ttk.Label(param_row, text="Max Pwr (%):").pack(side=tk.LEFT, padx=(4, 2))
        self.max_power_var = tk.DoubleVar(value=100.0)
        ttk.Spinbox(param_row, textvariable=self.max_power_var, from_=1.0, to=100.0, increment=5.0, width=5).pack(side=tk.LEFT, padx=2)

        ttk.Label(param_row, text="Range:").pack(side=tk.LEFT, padx=(4, 2))
        self.heater_range_var = tk.StringVar(value="HI")
        ttk.Combobox(param_row, textvariable=self.heater_range_var, values=["HI", "MID", "LOW"], width=4, state="readonly").pack(side=tk.LEFT, padx=2)

        # Tuned PID Controls Row
        pid_row = ttk.Frame(grp)
        pid_row.pack(fill=tk.X, pady=2)
        ttk.Label(pid_row, text="PID Gains (Tuned):").pack(side=tk.LEFT)

        ttk.Label(pid_row, text="P:").pack(side=tk.LEFT, padx=(6, 1))
        self.p_gain_var = tk.DoubleVar(value=70.0)
        ttk.Spinbox(pid_row, textvariable=self.p_gain_var, from_=0.0, to=500.0, increment=5.0, width=5).pack(side=tk.LEFT, padx=1)

        ttk.Label(pid_row, text="I (s):").pack(side=tk.LEFT, padx=(4, 1))
        self.i_gain_var = tk.DoubleVar(value=900.0)
        ttk.Spinbox(pid_row, textvariable=self.i_gain_var, from_=0.0, to=5000.0, increment=50.0, width=5).pack(side=tk.LEFT, padx=1)

        ttk.Label(pid_row, text="D:").pack(side=tk.LEFT, padx=(4, 1))
        self.d_gain_var = tk.DoubleVar(value=0.0)
        ttk.Spinbox(pid_row, textvariable=self.d_gain_var, from_=0.0, to=100.0, increment=1.0, width=4).pack(side=tk.LEFT, padx=1)

        btn_reset_pid = ttk.Button(pid_row, text="↺ Defaults", width=9, command=self._reset_pid_defaults)
        btn_reset_pid.pack(side=tk.LEFT, padx=(6, 0))

        # Live Estimated Run Time Display Card
        est_frame = ttk.Frame(grp, relief="groove", padding="4 2 4 2")
        est_frame.pack(fill=tk.X, pady=2)

        est_header = ttk.Frame(est_frame)
        est_header.pack(fill=tk.X)
        ttk.Label(est_header, text="⏱ EST. TOTAL RUN TIME:", font=("Segoe UI", 8, "bold"), foreground="#0284c7").pack(side=tk.LEFT)
        self.lbl_est_total = ttk.Label(est_header, text="--", font=("Segoe UI", 9, "bold"), foreground="#0f172a")
        self.lbl_est_total.pack(side=tk.LEFT, padx=6)

        self.lbl_est_details = ttk.Label(
            est_frame,
            text="Ramp: -- | Soak: -- | Sweep: --",
            font=("Segoe UI", 8),
            foreground="#475569"
        )
        self.lbl_est_details.pack(anchor=tk.W, pady=(1, 0))

        # Big Digital Displays for Stage & Setpoint
        digits_frame = ttk.Frame(grp, padding="2")
        digits_frame.pack(fill=tk.X, pady=2)

        d1 = ttk.Frame(digits_frame, relief="sunken", padding="2")
        d1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        ttk.Label(d1, text="STAGE TEMP (T)", font=("Segoe UI", 7, "bold"), foreground="#64748b").pack()
        self.lbl_digit_temp = ttk.Label(d1, text="297.315 K", style="BigDigit.TLabel")
        self.lbl_digit_temp.pack()

        d2 = ttk.Frame(digits_frame, relief="sunken", padding="2")
        d2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        ttk.Label(d2, text="SETPOINT", font=("Segoe UI", 7, "bold"), foreground="#64748b").pack()
        self.lbl_digit_setpt = ttk.Label(d2, text="--.-- K", style="BigDigit.TLabel")
        self.lbl_digit_setpt.pack()

        d3 = ttk.Frame(digits_frame, relief="sunken", padding="2")
        d3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        ttk.Label(d3, text="HEATER (W)", font=("Segoe UI", 7, "bold"), foreground="#64748b").pack()
        self.lbl_digit_heater = ttk.Label(d3, text="0.0 %", style="BigDigit.TLabel")
        self.lbl_digit_heater.pack()

    def _build_impedance_panel(self, parent):
        grp = ttk.LabelFrame(parent, text=" 2. Wayne Kerr 6510B Frequency Sweep ", padding="6 3 6 3")
        grp.pack(fill=tk.X, pady=2)

        # Measurement Function & Drive Level
        r1 = ttk.Frame(grp)
        r1.pack(fill=tk.X, pady=1)
        ttk.Label(r1, text="Function:", width=13).pack(side=tk.LEFT)
        self.func_var = tk.StringVar(value="R - X")
        ttk.Combobox(r1, textvariable=self.func_var, values=["R - X", "Z - θ", "C - D"], width=8, state="readonly").pack(side=tk.LEFT)

        ttk.Label(r1, text="Drive (Bias):", width=11).pack(side=tk.LEFT, padx=4)
        self.bias_mv_var = tk.DoubleVar(value=100.0)
        ttk.Spinbox(r1, textvariable=self.bias_mv_var, from_=10.0, to=1000.0, increment=10.0, width=6).pack(side=tk.LEFT)
        ttk.Label(r1, text="mV RMS").pack(side=tk.LEFT, padx=2)

        # Frequency Span & Points
        r2 = ttk.Frame(grp)
        r2.pack(fill=tk.X, pady=1)
        ttk.Label(r2, text="Frequency Span:", width=13).pack(side=tk.LEFT)
        self.start_f_var = tk.DoubleVar(value=20.0)
        ttk.Entry(r2, textvariable=self.start_f_var, width=6).pack(side=tk.LEFT)
        ttk.Label(r2, text="Hz to").pack(side=tk.LEFT, padx=2)
        self.stop_f_var = tk.DoubleVar(value=10000000.0)
        ttk.Entry(r2, textvariable=self.stop_f_var, width=9).pack(side=tk.LEFT)
        ttk.Label(r2, text="Hz").pack(side=tk.LEFT, padx=2)

        r3 = ttk.Frame(grp)
        r3.pack(fill=tk.X, pady=1)
        ttk.Label(r3, text="Sweep Points:", width=13).pack(side=tk.LEFT)
        self.num_pts_var = tk.IntVar(value=200)
        ttk.Spinbox(r3, textvariable=self.num_pts_var, from_=10, to=1000, increment=10, width=6).pack(side=tk.LEFT)
        ttk.Label(r3, text="Logarithmic Points (SER)").pack(side=tk.LEFT, padx=4)

        # Output file preview
        r4 = ttk.Frame(grp)
        r4.pack(fill=tk.X, pady=1)
        ttk.Label(r4, text="File Pattern:", width=13).pack(side=tk.LEFT)
        self.lbl_file_preview = ttk.Label(r4, text="<Tempr>_<Bais>_<time_stamp>.dat", font=("Segoe UI", 9, "bold"), foreground="#0369a1")
        self.lbl_file_preview.pack(side=tk.LEFT)

        r5 = ttk.Frame(grp)
        r5.pack(fill=tk.X, pady=1)
        ttk.Label(r5, text="Data Folder:", width=13).pack(side=tk.LEFT)
        self.out_dir_var = tk.StringVar(value="Data")
        ttk.Entry(r5, textvariable=self.out_dir_var, width=18).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(r5, text="Browse", width=7, command=self._browse_dir).pack(side=tk.LEFT, padx=4)

    def _build_sample_panel(self, parent):
        grp = ttk.LabelFrame(parent, text=" 3. PMN-0.3PT Sample Geometry & Analysis ", padding="6 3 6 3")
        grp.pack(fill=tk.X, pady=2)

        # Thickness and Area
        r1 = ttk.Frame(grp)
        r1.pack(fill=tk.X, pady=1)
        ttk.Label(r1, text="Thickness d:", width=12).pack(side=tk.LEFT)
        self.sp_d = ttk.Spinbox(r1, textvariable=self.sample_d_var, from_=0.01, to=10.0, increment=0.05, width=6, command=self._on_geometry_change)
        self.sp_d.pack(side=tk.LEFT)
        self.sp_d.bind("<KeyRelease>", lambda e: self._on_geometry_change())
        ttk.Label(r1, text="mm").pack(side=tk.LEFT, padx=2)

        ttk.Label(r1, text="Area A:", width=7).pack(side=tk.LEFT, padx=4)
        self.sp_a = ttk.Spinbox(r1, textvariable=self.sample_a_var, from_=0.1, to=100.0, increment=0.5, width=6, command=self._on_geometry_change)
        self.sp_a.pack(side=tk.LEFT)
        self.sp_a.bind("<KeyRelease>", lambda e: self._on_geometry_change())
        ttk.Label(r1, text="mm²").pack(side=tk.LEFT, padx=2)

        # Vacuum Capacitance Readout C0
        r2 = ttk.Frame(grp)
        r2.pack(fill=tk.X, pady=1)
        ttk.Label(r2, text="Vacuum C₀:", width=12).pack(side=tk.LEFT)
        c0_init = self.calculate_c0()
        self.lbl_c0_val = ttk.Label(r2, text=f"{c0_init * 1e12:.3f} pF", font=("Segoe UI", 9, "bold"), foreground="#0369a1")
        self.lbl_c0_val.pack(side=tk.LEFT)
        ttk.Label(r2, text="(C₀ = ε₀·A/d)", foreground="#64748b", font=("Segoe UI", 8, "italic")).pack(side=tk.LEFT, padx=4)

        # Action buttons
        r3 = ttk.Frame(grp)
        r3.pack(fill=tk.X, pady=2)
        self.btn_load_latest = tk.Button(
            r3,
            text="⚡ Load Latest (Data/)",
            font=("Segoe UI", 8, "bold"),
            bg="#f1f5f9",
            fg="#0f172a",
            relief="groove",
            command=self.load_latest_pmn_03pt_data
        )
        self.btn_load_latest.pack(side=tk.LEFT, padx=2)

        self.btn_load_ref = tk.Button(
            r3,
            text="⚡ Load Reference",
            font=("Segoe UI", 8),
            bg="#f8fafc",
            fg="#0f172a",
            relief="groove",
            command=self.load_pmn_pt_reference
        )
        self.btn_load_ref.pack(side=tk.LEFT, padx=2)

        self.btn_import_sweeps = tk.Button(
            r3,
            text="📂 Import Folder...",
            font=("Segoe UI", 8),
            bg="#f8fafc",
            relief="groove",
            command=self.import_sweep_folder
        )
        self.btn_import_sweeps.pack(side=tk.LEFT, padx=2)

        self.btn_export_perm = tk.Button(
            r3,
            text="💾 Export CSV",
            font=("Segoe UI", 8),
            bg="#f8fafc",
            relief="groove",
            command=self.export_permittivity_csv
        )
        self.btn_export_perm.pack(side=tk.LEFT, padx=2)

    def _build_execution_panel(self, parent):
        grp = ttk.LabelFrame(parent, text=" 4. Automation Execution & Status ", padding="6 3 6 3")
        grp.pack(fill=tk.X, pady=2)

        # Status text & Progress Bar
        self.lbl_status = ttk.Label(grp, text="READY: Configure settings and click Start Experiment.", font=("Segoe UI", 9, "bold"), foreground="#0284c7")
        self.lbl_status.pack(anchor=tk.W, pady=1)

        self.progress_bar = ttk.Progressbar(grp, orient=tk.HORIZONTAL, mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=2)

        self.lbl_soak_status = ttk.Label(grp, text="Soak Timer: 05:00 / 05:00 (Idle)", font=("Segoe UI", 8))
        self.lbl_soak_status.pack(anchor=tk.W, pady=1)

        self.lbl_exec_est = ttk.Label(grp, text="Est. Total Time: --", font=("Segoe UI", 8, "italic"), foreground="#475569")
        self.lbl_exec_est.pack(anchor=tk.W, pady=1)

        # Action Buttons
        btn_box = ttk.Frame(grp)
        btn_box.pack(fill=tk.X, pady=2)

        self.btn_start = tk.Button(
            btn_box,
            text="▶ START EXPERIMENT",
            font=("Segoe UI", 9, "bold"),
            bg="#16a34a",
            fg="#ffffff",
            activebackground="#15803d",
            activeforeground="#ffffff",
            padx=12,
            pady=3,
            command=self.start_experiment
        )
        self.btn_start.pack(side=tk.LEFT, padx=3)

        self.btn_skip_soak = tk.Button(
            btn_box,
            text="⏭ Skip Soak / Sweep Now",
            font=("Segoe UI", 8),
            bg="#f59e0b",
            fg="#000000",
            state=tk.DISABLED,
            command=self.skip_soak
        )
        self.btn_skip_soak.pack(side=tk.LEFT, padx=3)

        self.btn_stop = tk.Button(
            btn_box,
            text="⏹ Abort",
            font=("Segoe UI", 8),
            bg="#e2e8f0",
            state=tk.DISABLED,
            command=self.abort_experiment
        )
        self.btn_stop.pack(side=tk.LEFT, padx=3)

    def _build_plotting_panel(self, parent):
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Live Sweep Curves (R and X vs Frequency)
        tab1 = ttk.Frame(self.notebook)
        self.notebook.add(tab1, text="  Live R & X Spectrum  ")
        self.fig1 = Figure(figsize=(7, 5), dpi=100)
        self.ax1_r = self.fig1.add_subplot(211)
        self.ax1_x = self.fig1.add_subplot(212, sharex=self.ax1_r)
        self.fig1.tight_layout(pad=2.0)
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=tab1)
        self.canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        toolbar1 = NavigationToolbar2Tk(self.canvas1, tab1)
        toolbar1.update()

        # Tab 2: Bode Plot (|Z| & Phase θ)
        tab2 = ttk.Frame(self.notebook)
        self.notebook.add(tab2, text="  Bode Plot (|Z| & θ)  ")
        self.fig2 = Figure(figsize=(7, 5), dpi=100)
        self.ax2_z = self.fig2.add_subplot(211)
        self.ax2_th = self.fig2.add_subplot(212, sharex=self.ax2_z)
        self.fig2.tight_layout(pad=2.0)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=tab2)
        self.canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        toolbar2 = NavigationToolbar2Tk(self.canvas2, tab2)
        toolbar2.update()

        # Tab 3: Live Temperature Graph (Original Cryo-con 22C Dual-Axis Chart & Toolbar)
        tab3 = ttk.Frame(self.notebook)
        self.notebook.add(tab3, text="  📈 Live Temperature Graph  ")

        tb3 = ttk.Frame(tab3, padding="3")
        tb3.pack(fill=tk.X, side=tk.TOP, pady=(0, 2))

        ttk.Label(tb3, text="Time Window:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(2, 4))
        self.combo_window = ttk.Combobox(
            tb3, width=8,
            values=["2 min", "5 min", "10 min", "15 min", "30 min", "All"],
            state="readonly"
        )
        self.combo_window.set("10 min")
        self.combo_window.bind("<<ComboboxSelected>>", self._on_window_change)
        self.combo_window.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Checkbutton(tb3, text="Temp A", variable=self.chk_show_a, command=self._update_thermal_plot).pack(side=tk.LEFT, padx=3)
        ttk.Checkbutton(tb3, text="Setpoint", variable=self.chk_show_sp, command=self._update_thermal_plot).pack(side=tk.LEFT, padx=3)
        ttk.Checkbutton(tb3, text="Heater %", variable=self.chk_show_ht, command=self._update_thermal_plot).pack(side=tk.LEFT, padx=3)
        ttk.Checkbutton(tb3, text="Autoscale Y", variable=self.chk_autoscale_temp, command=self._update_thermal_plot).pack(side=tk.LEFT, padx=3)
        ttk.Checkbutton(tb3, text="Autoscale Pwr", variable=self.chk_autoscale_ht, command=self._update_thermal_plot).pack(side=tk.LEFT, padx=3)

        ttk.Button(tb3, text="Clear Chart", command=self._clear_chart).pack(side=tk.RIGHT, padx=4)
        ttk.Button(tb3, text="⛶ Fit Scale", command=self._update_thermal_plot).pack(side=tk.RIGHT, padx=2)

        self.fig3 = Figure(figsize=(7, 5), dpi=100)
        self.fig3.patch.set_facecolor("#fcfcfc")
        self.ax3_t = self.fig3.add_subplot(111)
        self.ax3_h = self.ax3_t.twinx()
        self.ax3_h.yaxis.tick_right()
        self.ax3_h.yaxis.set_label_position("right")
        self.fig3.tight_layout()
        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=tab3)
        self.canvas3.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        toolbar3 = NavigationToolbar2Tk(self.canvas3, tab3)
        toolbar3.update()

        # Tab 4: Nyquist Plot (-X vs R)
        tab4 = ttk.Frame(self.notebook)
        self.notebook.add(tab4, text="  Nyquist Plot (-X vs R)  ")
        self.fig4 = Figure(figsize=(7, 5), dpi=100)
        self.ax4_ny = self.fig4.add_subplot(111)
        self.fig4.tight_layout(pad=2.5)
        self.canvas4 = FigureCanvasTkAgg(self.fig4, master=tab4)
        self.canvas4.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        toolbar4 = NavigationToolbar2Tk(self.canvas4, tab4)
        toolbar4.update()

        # Tab 5: PMN-0.3PT Dielectric Permittivity vs Temperature
        tab5 = ttk.Frame(self.notebook)
        self.tab5 = tab5
        self.notebook.add(tab5, text="  PMN-0.3PT Permittivity vs T  ")

        # Top control toolbar for Tab 5
        top_bar = ttk.Frame(tab5, padding="4")
        top_bar.pack(fill=tk.X, side=tk.TOP)

        ttk.Label(top_bar, text="View Mode:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=4)
        self.rb_all = ttk.Radiobutton(
            top_bar,
            text="All Frequencies (1 kHz - 10 MHz) [Fig a]",
            value="all",
            variable=self.permittivity_view_var,
            command=self._update_permittivity_plot
        )
        self.rb_all.pack(side=tk.LEFT, padx=6)
        self.rb_bulk = ttk.Radiobutton(
            top_bar,
            text="Bulk Response (1 kHz - 1 MHz) [Fig b]",
            value="bulk",
            variable=self.permittivity_view_var,
            command=self._update_permittivity_plot
        )
        self.rb_bulk.pack(side=tk.LEFT, padx=6)

        self.lbl_dataset_info = ttk.Label(top_bar, text="Dataset: No data loaded", foreground="#64748b", font=("Segoe UI", 8, "italic"))
        self.lbl_dataset_info.pack(side=tk.RIGHT, padx=6)

        # Plot Canvas
        self.fig5 = Figure(figsize=(7, 4.2), dpi=100)
        self.ax5 = self.fig5.add_subplot(111)
        self.fig5.tight_layout(pad=2.0)
        self.canvas5 = FigureCanvasTkAgg(self.fig5, master=tab5)
        self.canvas5.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        toolbar5 = NavigationToolbar2Tk(self.canvas5, tab5)
        toolbar5.update()

        # Summary Metrics Treeview / Table
        summary_frame = ttk.LabelFrame(tab5, text=" Permittivity Summary Metrics (PMN-0.3PT Phase & Curie Transitions) ", padding="4")
        summary_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=4, pady=3)

        cols = ("label", "f_exact", "eps_300", "max_eps", "tm")
        self.tree_summary = ttk.Treeview(summary_frame, columns=cols, show="headings", height=5)
        self.tree_summary.heading("label", text="Frequency Label")
        self.tree_summary.heading("f_exact", text="Exact Frequency (Hz)")
        self.tree_summary.heading("eps_300", text="ε' at 300 K")
        self.tree_summary.heading("max_eps", text="Max ε'")
        self.tree_summary.heading("tm", text="Peak Temp Tm (K)")

        self.tree_summary.column("label", width=190, anchor=tk.W)
        self.tree_summary.column("f_exact", width=140, anchor=tk.CENTER)
        self.tree_summary.column("eps_300", width=120, anchor=tk.CENTER)
        self.tree_summary.column("max_eps", width=120, anchor=tk.CENTER)
        self.tree_summary.column("tm", width=140, anchor=tk.CENTER)
        self.tree_summary.pack(fill=tk.X, expand=True)

        self._init_empty_plots()

    def _init_empty_plots(self):
        # Tab 1
        self.ax1_r.clear()
        self.ax1_r.set_title("Real Resistance R (Ω) vs. Frequency", fontsize=10, fontweight="bold")
        self.ax1_r.set_ylabel("R (Ω)")
        self.ax1_r.set_xscale("log")
        self.ax1_r.set_yscale("log")
        self.ax1_r.grid(True, which="both", linestyle="--", alpha=0.5)

        self.ax1_x.clear()
        self.ax1_x.set_title("Reactance X (Ω) vs. Frequency", fontsize=10, fontweight="bold")
        self.ax1_x.set_xlabel("Frequency (Hz)")
        self.ax1_x.set_ylabel("X (Ω)")
        self.ax1_x.set_xscale("log")
        self.ax1_x.grid(True, which="both", linestyle="--", alpha=0.5)
        self.canvas1.draw_idle()

        # Tab 2
        self.ax2_z.clear()
        self.ax2_z.set_title("Impedance Magnitude |Z| vs. Frequency", fontsize=10, fontweight="bold")
        self.ax2_z.set_ylabel("|Z| (Ω)")
        self.ax2_z.set_xscale("log")
        self.ax2_z.set_yscale("log")
        self.ax2_z.grid(True, which="both", linestyle="--", alpha=0.5)

        self.ax2_th.clear()
        self.ax2_th.set_title("Phase Angle θ (deg) vs. Frequency", fontsize=10, fontweight="bold")
        self.ax2_th.set_xlabel("Frequency (Hz)")
        self.ax2_th.set_ylabel("Phase (deg)")
        self.ax2_th.set_xscale("log")
        self.ax2_th.grid(True, which="both", linestyle="--", alpha=0.5)
        self.canvas2.draw_idle()

        # Tab 3: Cryo-con 22C Live Temperature Graph
        self.ax3_t.clear()
        self.ax3_h.clear()
        self.ax3_t.set_title("Cryo-con 22C — Live Temperature & Heater Profile", fontsize=10, fontweight="bold")
        self.ax3_t.set_xlabel("Elapsed Time (s)", fontsize=9)
        self.ax3_t.set_ylabel("Temperature (K)", color="#0066cc", fontsize=9)
        self.ax3_h.set_ylabel("Heater Output (%)", color="#8e24aa", fontsize=9)
        self.ax3_h.yaxis.set_label_position("right")
        self.ax3_h.yaxis.tick_right()
        self.ax3_h.set_ylim(0, 105)
        self.ax3_t.grid(True, linestyle="--", alpha=0.4)
        self.fig3.tight_layout()
        self.canvas3.draw_idle()

        # Tab 4
        self.ax4_ny.clear()
        self.ax4_ny.set_title("Complex Impedance Plane: -X vs R (Nyquist)", fontsize=10, fontweight="bold")
        self.ax4_ny.set_xlabel("R (Ω)")
        self.ax4_ny.set_ylabel("-X (Ω)")
        self.ax4_ny.grid(True, linestyle="--", alpha=0.5)
        self.canvas4.draw_idle()

        # Tab 5
        self.ax5.clear()
        self.ax5.set_title("Relative Permittivity ε' vs. Temperature T (K) for PMN-PT", fontsize=10, fontweight="bold")
        self.ax5.set_xlabel("Temperature T (K)")
        self.ax5.set_ylabel("Real Relative Permittivity ε'")
        self.ax5.grid(True, which="both", linestyle="--", alpha=0.5)
        self.canvas5.draw_idle()

    # -------------------------------------------------------------------------
    # PMN-PT Dielectric Permittivity Physics & Data Management
    # -------------------------------------------------------------------------

    def calculate_c0(self) -> float:
        """Compute geometric / vacuum capacitance C0 = eps_0 * (A / d) in Farads."""
        d_m = max(1e-6, self.sample_d_var.get() * 1e-3)
        a_m2 = max(1e-9, self.sample_a_var.get() * 1e-6)
        eps_0 = 8.8541878128e-12
        return eps_0 * (a_m2 / d_m)

    @staticmethod
    def calculate_eps_prime(r: float, x: float, f: float, c0: float) -> float:
        """
        Compute Real Relative Permittivity:
            eps' = -X / (omega * C0 * (R^2 + X^2))
        where omega = 2 * pi * f.
        """
        if f <= 0 or c0 <= 0:
            return 0.0
        omega = 2.0 * math.pi * f
        denom = omega * c0 * (r ** 2 + x ** 2)
        if denom == 0:
            return 0.0
        return (-x) / denom

    @staticmethod
    def calculate_eps_double_prime(r: float, x: float, f: float, c0: float) -> float:
        """
        Compute Imaginary Relative Permittivity (Dielectric Loss):
            eps'' = R / (omega * C0 * (R^2 + X^2))
        where omega = 2 * pi * f.
        """
        if f <= 0 or c0 <= 0:
            return 0.0
        omega = 2.0 * math.pi * f
        denom = omega * c0 * (r ** 2 + x ** 2)
        if denom == 0:
            return 0.0
        return r / denom

    @staticmethod
    def calculate_tan_delta(r: float, x: float) -> float:
        """
        Compute Loss Tangent:
            tan(delta) = eps'' / eps' = R / -X
        """
        if x == 0:
            return 0.0
        return r / (-x)

    def _on_geometry_change(self):
        """Update C0 display and recalculate permittivity curves when thickness or area changes."""
        try:
            d_val = self.sample_d_var.get()
            a_val = self.sample_a_var.get()
            if d_val <= 0 or a_val <= 0:
                return
            c0 = self.calculate_c0()
            if hasattr(self, "lbl_c0_val"):
                self.lbl_c0_val.config(text=f"{c0 * 1e12:.3f} pF")
            self._recalculate_permittivity_from_impedance()
        except Exception:
            pass

    def _recalculate_permittivity_from_impedance(self):
        """Recalculate eps_prime, eps_double_prime, and tan_delta for cached impedance points using updated C0."""
        c0 = self.calculate_c0()
        for nom_f, data in self.permittivity_data.items():
            r_list = data.get("r_vals", [])
            x_list = data.get("x_vals", [])
            f_list = data.get("freq_vals", [])
            new_eps = []
            new_eps_dp = []
            new_tan_delta = []
            for r, x, f in zip(r_list, x_list, f_list):
                new_eps.append(self.calculate_eps_prime(r, x, f, c0))
                new_eps_dp.append(self.calculate_eps_double_prime(r, x, f, c0))
                new_tan_delta.append(self.calculate_tan_delta(r, x))
            data["eps_prime"] = new_eps
            data["eps_double_prime"] = new_eps_dp
            data["tan_delta"] = new_tan_delta
        if hasattr(self, "ax5"):
            self._update_permittivity_plot()

    def load_latest_pmn_03pt_data(self):
        """
        Load the latest PMN-0.3PT experimental dataset from the local Data/ folder
        (57 sweeps, 300 K to 412 K in 2 K increments).
        """
        local_data = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")
        if not os.path.exists(local_data):
            local_data = "Data"
        if os.path.exists(local_data):
            self.import_sweep_folder(local_data)
            self.lbl_dataset_info.config(text="Dataset: PMN-0.3PT Latest Measurement (Data/ - 57 sweeps, 300K-412K)")
            self.lbl_status.config(text="Loaded PMN-0.3PT latest measurement dataset (Data/).", foreground="#16a34a")
        else:
            messagebox.showwarning("Data Folder Missing", f"Data folder not found at:\n{local_data}")

    def load_pmn_pt_reference(self):
        """
        Load the 300 K to 460 K reference dataset from C:\\Users\\sahgy\\Downloads\\Impedance_PMN-PT.
        Matches exact values from PMN_PT_Dielectric_Permittivity_Analysis.ipynb.
        """
        ref_dir = r"C:\Users\sahgy\Downloads\Impedance_PMN-PT"
        if not os.path.exists(ref_dir):
            messagebox.showerror("Reference Not Found", f"Reference directory not found:\n{ref_dir}")
            return

        c0 = self.calculate_c0()

        iso_defs = [
            (1e3, "1 kHz (~1.025 kHz)", "1K_Hz.dat", "#1f77b4"),
            (1e4, "10 kHz (~10.19 kHz)", "10K_Hz.dat", "#ff7f0e"),
            (1e5, "100 kHz (~101.2 kHz)", "100K_Hz.dat", "#2ca02c"),
            (1e6, "1 MHz (~1.006 MHz)", "1M_Hz.dat", "#d62728"),
            (1e7, "10 MHz (~10.00 MHz)", "10M_Hz.dat", "#9467bd"),
        ]

        all_exist = all(os.path.exists(os.path.join(ref_dir, f)) for _, _, f, _ in iso_defs)
        if all_exist:
            self.permittivity_data.clear()
            for nom_f, label, fname, color in iso_defs:
                fpath = os.path.join(ref_dir, fname)
                temps, r_vals, x_vals, freqs, eps_primes, eps_double_primes, tan_deltas = [], [], [], [], [], [], []
                with open(fpath, "r", encoding="utf-8") as f:
                    header = f.readline().strip().split("\t")
                    f_idx = header.index("f (Hz)") if "f (Hz)" in header else 0
                    t_idx = header.index("T (K)") if "T (K)" in header else 1
                    r_idx = header.index("R (Ohm)") if "R (Ohm)" in header else 2
                    x_idx = header.index("X (Ohm)") if "X (Ohm)" in header else 3
                    for line in f:
                        parts = line.strip().split("\t")
                        if len(parts) >= 4:
                            f_val = float(parts[f_idx])
                            t_val = float(parts[t_idx])
                            r_val = float(parts[r_idx])
                            x_val = float(parts[x_idx])
                            eps_p = self.calculate_eps_prime(r_val, x_val, f_val, c0)
                            eps_dp = self.calculate_eps_double_prime(r_val, x_val, f_val, c0)
                            tan_d = self.calculate_tan_delta(r_val, x_val)
                            temps.append(t_val)
                            freqs.append(f_val)
                            r_vals.append(r_val)
                            x_vals.append(x_val)
                            eps_primes.append(eps_p)
                            eps_double_primes.append(eps_dp)
                            tan_deltas.append(tan_d)

                exact_f = freqs[0] if freqs else nom_f
                self.permittivity_data[nom_f] = {
                    "label": label,
                    "nom_f": nom_f,
                    "exact_f": exact_f,
                    "color": color,
                    "temps": temps,
                    "freq_vals": freqs,
                    "r_vals": r_vals,
                    "x_vals": x_vals,
                    "eps_prime": eps_primes,
                    "eps_double_prime": eps_double_primes,
                    "tan_delta": tan_deltas,
                }

            self.lbl_dataset_info.config(text=f"Reference: PMN-PT 300K-460K (33 points) from {os.path.basename(ref_dir)}")
            self.notebook.select(self.tab5)
            self._update_permittivity_plot()
            self.lbl_status.config(text="Loaded PMN-PT reference dataset successfully.", foreground="#16a34a")
        else:
            sweep_dir = os.path.join(ref_dir, "frequency_sweeps_100mV")
            if os.path.exists(sweep_dir):
                self.import_sweep_folder(sweep_dir)
            else:
                messagebox.showerror("Error", f"Could not find isofrequency or sweep files in:\n{ref_dir}")

    def import_sweep_folder(self, folder: Optional[str] = None):
        """
        Import a folder of frequency sweep .dat files, extract the 5 nearest isofrequencies,
        and plot the temperature-dependent relative permittivity.
        """
        if not folder:
            folder = filedialog.askdirectory(initialdir=self.out_dir_var.get(), title="Select Sweep Folder")
        if not folder or not os.path.exists(folder):
            return

        c0 = self.calculate_c0()
        pattern = os.path.join(folder, "*.dat")
        raw_files = glob.glob(pattern)
        if not raw_files:
            messagebox.showwarning("No Data Files", f"No .dat sweep files found in:\n{folder}")
            return

        temp_file_map = {}
        temp_pattern = re.compile(r"^(\d+(?:\.\d+)?)K_")
        for p in raw_files:
            bname = os.path.basename(p)
            m = temp_pattern.match(bname)
            if m:
                t_val = float(m.group(1))
                if t_val not in temp_file_map:
                    temp_file_map[t_val] = []
                temp_file_map[t_val].append(p)

        if not temp_file_map:
            for p in raw_files:
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        hdr = f.readline().strip().split("\t")
                        if "T (K)" in hdr:
                            t_col = hdr.index("T (K)")
                            first_line = f.readline().strip().split("\t")
                            t_val = float(first_line[t_col])
                            if t_val not in temp_file_map:
                                temp_file_map[t_val] = []
                            temp_file_map[t_val].append(p)
                except Exception:
                    pass

        if not temp_file_map:
            messagebox.showerror("Unrecognized Data", f"Could not identify temperature sweeps in:\n{folder}")
            return

        sorted_temps = sorted(temp_file_map.keys())
        selected_files = []
        for t in sorted_temps:
            paths = sorted(temp_file_map[t])
            selected_files.append((t, paths[-1]))

        nom_defs = [
            (1e3, "1 kHz", "#1f77b4"),
            (1e4, "10 kHz", "#ff7f0e"),
            (1e5, "100 kHz", "#2ca02c"),
            (1e6, "1 MHz", "#d62728"),
            (1e7, "10 MHz", "#9467bd"),
        ]

        temp_accum = {nom_f: {"temps": [], "freqs": [], "r_vals": [], "x_vals": [], "eps": [], "eps_dp": [], "tan_delta": []} for nom_f, _, _ in nom_defs}
        last_exact_f = {}

        for temp_k, fpath in selected_files:
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    hdr = f.readline().strip().split("\t")
                    f_col = hdr.index("f (Hz)")
                    r_col = hdr.index("R (Ohm)")
                    x_col = hdr.index("X (Ohm)")

                    sweep_rows = []
                    for line in f:
                        parts = line.strip().split("\t")
                        if len(parts) > max(f_col, r_col, x_col):
                            try:
                                sweep_rows.append((
                                    float(parts[f_col]),
                                    float(parts[r_col]),
                                    float(parts[x_col])
                                ))
                            except ValueError:
                                pass

                    if not sweep_rows:
                        continue

                    for nom_f, _, _ in nom_defs:
                        best_row = min(sweep_rows, key=lambda row: abs(row[0] - nom_f))
                        f_act, r_act, x_act = best_row
                        eps_act = self.calculate_eps_prime(r_act, x_act, f_act, c0)
                        eps_dp_act = self.calculate_eps_double_prime(r_act, x_act, f_act, c0)
                        tan_delta_act = self.calculate_tan_delta(r_act, x_act)
                        temp_accum[nom_f]["temps"].append(temp_k)
                        temp_accum[nom_f]["freqs"].append(f_act)
                        temp_accum[nom_f]["r_vals"].append(r_act)
                        temp_accum[nom_f]["x_vals"].append(x_act)
                        temp_accum[nom_f]["eps"].append(eps_act)
                        temp_accum[nom_f]["eps_dp"].append(eps_dp_act)
                        temp_accum[nom_f]["tan_delta"].append(tan_delta_act)
                        last_exact_f[nom_f] = f_act
            except Exception as e:
                print(f"[WARN] Error reading {fpath}: {e}")

        self.permittivity_data.clear()
        for nom_f, base_lbl, color in nom_defs:
            f_exact = last_exact_f.get(nom_f, nom_f)
            if f_exact >= 1e6:
                disp_f = f"{f_exact/1e6:.3f} MHz"
            elif f_exact >= 1e3:
                disp_f = f"{f_exact/1e3:.2f} kHz"
            else:
                disp_f = f"{f_exact:.1f} Hz"
            label = f"{base_lbl} (~{disp_f})"

            self.permittivity_data[nom_f] = {
                "label": label,
                "nom_f": nom_f,
                "exact_f": f_exact,
                "color": color,
                "temps": temp_accum[nom_f]["temps"],
                "freq_vals": temp_accum[nom_f]["freqs"],
                "r_vals": temp_accum[nom_f]["r_vals"],
                "x_vals": temp_accum[nom_f]["x_vals"],
                "eps_prime": temp_accum[nom_f]["eps"],
                "eps_double_prime": temp_accum[nom_f]["eps_dp"],
                "tan_delta": temp_accum[nom_f]["tan_delta"],

            }

        n_pts = len(selected_files)
        self.lbl_dataset_info.config(text=f"Imported: {n_pts} sweeps ({sorted_temps[0]:.0f}K - {sorted_temps[-1]:.0f}K) from {os.path.basename(folder)}")
        self.notebook.select(self.tab5)
        self._update_permittivity_plot()
        self.lbl_status.config(text=f"Imported {n_pts} temperature sweeps from {os.path.basename(folder)}", foreground="#16a34a")

    def _ingest_sweep_points_for_permittivity(self, target_k: float, points: List[Dict[str, Any]]):
        """Extract the 5 target frequencies from a live completed sweep and append to permittivity curves."""
        if not points:
            return

        c0 = self.calculate_c0()
        nom_defs = [
            (1e3, "1 kHz", "#1f77b4"),
            (1e4, "10 kHz", "#ff7f0e"),
            (1e5, "100 kHz", "#2ca02c"),
            (1e6, "1 MHz", "#d62728"),
            (1e7, "10 MHz", "#9467bd"),
        ]

        for nom_f, base_lbl, color in nom_defs:
            if nom_f not in self.permittivity_data:
                self.permittivity_data[nom_f] = {
                    "label": f"{base_lbl}",
                    "nom_f": nom_f,
                    "exact_f": nom_f,
                    "color": color,
                    "temps": [],
                    "freq_vals": [],
                    "r_vals": [],
                    "x_vals": [],
                    "eps_prime": [],
                    "eps_double_prime": [],
                    "tan_delta": [],
                }

        for nom_f, base_lbl, _ in nom_defs:
            best_pt = min(points, key=lambda p: abs(p["freq_hz"] - nom_f))
            f_act = best_pt["freq_hz"]
            r_act = best_pt["r_ohm"]
            x_act = best_pt["x_ohm"]
            eps_act = self.calculate_eps_prime(r_act, x_act, f_act, c0)
            eps_dp_act = self.calculate_eps_double_prime(r_act, x_act, f_act, c0)
            tan_delta_act = self.calculate_tan_delta(r_act, x_act)

            data = self.permittivity_data[nom_f]
            if f_act >= 1e6:
                disp_f = f"{f_act/1e6:.3f} MHz"
            elif f_act >= 1e3:
                disp_f = f"{f_act/1e3:.2f} kHz"
            else:
                disp_f = f"{f_act:.1f} Hz"
            data["label"] = f"{base_lbl} (~{disp_f})"
            data["exact_f"] = f_act

            if target_k in data["temps"]:
                idx = data["temps"].index(target_k)
                data["freq_vals"][idx] = f_act
                data["r_vals"][idx] = r_act
                data["x_vals"][idx] = x_act
                data["eps_prime"][idx] = eps_act
                data["eps_double_prime"][idx] = eps_dp_act
                data["tan_delta"][idx] = tan_delta_act
            else:
                data["temps"].append(target_k)
                data["freq_vals"].append(f_act)
                data["r_vals"].append(r_act)
                data["x_vals"].append(x_act)
                data["eps_prime"].append(eps_act)
                data["eps_double_prime"].append(eps_dp_act)
                data["tan_delta"].append(tan_delta_act)
                zipped = sorted(zip(data["temps"], data["freq_vals"], data["r_vals"], data["x_vals"], data["eps_prime"], data["eps_double_prime"], data["tan_delta"]), key=lambda z: z[0])
                data["temps"] = [z[0] for z in zipped]
                data["freq_vals"] = [z[1] for z in zipped]
                data["r_vals"] = [z[2] for z in zipped]
                data["x_vals"] = [z[3] for z in zipped]
                data["eps_prime"] = [z[4] for z in zipped]
                data["eps_double_prime"] = [z[5] for z in zipped]
                data["tan_delta"] = [z[6] for z in zipped]

        sample_len = len(self.permittivity_data[1e3]["temps"])
        self.lbl_dataset_info.config(text=f"Live Acquisition: {sample_len} temperatures recorded")
        self._update_permittivity_plot()

    def _update_permittivity_plot(self):
        """Redraw Tab 5 plot according to selected view mode and refresh summary metrics."""
        self.ax5.clear()
        view_mode = self.permittivity_view_var.get()

        entries = self.permittivity_data
        if not entries:
            self.ax5.set_title("Relative Permittivity ε' vs. Temperature T (K) for PMN-PT", fontsize=10, fontweight="bold")
            self.ax5.set_xlabel("Temperature T (K)")
            self.ax5.set_ylabel("Real Relative Permittivity ε'")
            self.ax5.grid(True, which="both", linestyle="--", alpha=0.5)
            self.canvas5.draw_idle()
            return

        items = list(entries.items())
        if view_mode == "bulk":
            items = items[:4]

        title_suffix = " (1 kHz - 10 MHz)" if view_mode == "all" else " Bulk Response (1 kHz - 1 MHz)"
        marker_style = "o" if view_mode == "all" else "s"

        for nom_f, data in items:
            t_vals = data["temps"]
            eps_vals = data["eps_prime"]
            if not t_vals or not eps_vals:
                continue
            label = data["label"]
            color = data["color"]
            self.ax5.plot(t_vals, eps_vals, marker=marker_style, markersize=4, linewidth=1.8, color=color, label=label)

        self.ax5.set_title(f"Relative Permittivity ε' vs. T (K) for PMN-0.3PT{title_suffix}", fontsize=11, fontweight="bold")
        self.ax5.set_xlabel("Temperature T (K)", fontsize=9, fontweight="semibold")
        self.ax5.set_ylabel("Real Relative Permittivity ε'", fontsize=9, fontweight="semibold")
        self.ax5.grid(True, which="both", linestyle="--", linewidth=0.6, alpha=0.7)
        self.ax5.legend(fontsize=9, title_fontsize=9.5, frameon=True, loc="upper left")

        all_temps = []
        for _, d in items:
            all_temps.extend(d["temps"])
        if all_temps:
            min_t = min(all_temps)
            max_t = max(all_temps)
            span = max(5.0, max_t - min_t)
            self.ax5.set_xlim(min_t - 0.05 * span, max_t + 0.05 * span)

        self.fig5.tight_layout()
        self.canvas5.draw_idle()
        self._update_summary_table()

    def _update_summary_table(self):
        """Populate the summary treeview table with metrics matching permittivity_summary.csv."""
        for row in self.tree_summary.get_children():
            self.tree_summary.delete(row)

        for nom_f, data in self.permittivity_data.items():
            t_vals = data.get("temps", [])
            eps_vals = data.get("eps_prime", [])
            if not t_vals or not eps_vals:
                continue
            label = data["label"]
            f_exact = data.get("exact_f", nom_f)

            idx_300 = min(range(len(t_vals)), key=lambda i: abs(t_vals[i] - 300.0))
            eps_300_str = f"{eps_vals[idx_300]:.2f}" if abs(t_vals[idx_300] - 300.0) < 5.0 else f"{eps_vals[0]:.2f}"

            max_idx = max(range(len(eps_vals)), key=lambda i: eps_vals[i])
            max_eps_str = f"{eps_vals[max_idx]:.2f}"
            tm_str = f"{t_vals[max_idx]:.1f}"

            self.tree_summary.insert("", tk.END, values=(label, f"{f_exact:.1f}", eps_300_str, max_eps_str, tm_str))

    def export_permittivity_csv(self):
        """Export the compiled T vs eps' matrix and summary table to CSV."""
        if not self.permittivity_data:
            messagebox.showwarning("No Data", "No permittivity data to export.")
            return

        fpath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="permittivity_all_frequencies.csv",
            title="Export Permittivity CSV"
        )
        if not fpath:
            return

        try:
            all_temps = set()
            for _, d in self.permittivity_data.items():
                all_temps.update(d["temps"])
            sorted_t = sorted(all_temps)

            headers = ["T (K)"]
            for _, d in self.permittivity_data.items():
                lbl = d['label']
                headers.extend([f"eps_prime_{lbl}", f"eps_double_prime_{lbl}", f"tan_delta_{lbl}"])

            with open(fpath, "w", newline="", encoding="utf-8") as f_csv:
                writer = csv.writer(f_csv)
                writer.writerow(headers)
                for t in sorted_t:
                    row = [f"{t:.1f}"]
                    for _, d in self.permittivity_data.items():
                        if t in d["temps"]:
                            idx = d["temps"].index(t)
                            row.append(f"{d['eps_prime'][idx]:.6f}")
                            row.append(f"{d['eps_double_prime'][idx]:.6f}" if 'eps_double_prime' in d and len(d['eps_double_prime']) > idx else "")
                            row.append(f"{d['tan_delta'][idx]:.6f}" if 'tan_delta' in d and len(d['tan_delta']) > idx else "")
                        else:
                            row.extend(["", "", ""])
                    writer.writerow(row)
            messagebox.showinfo("Export Successful", f"Exported permittivity data to:\n{fpath}")
            self.lbl_status.config(text=f"Exported: {os.path.basename(fpath)}", foreground="#16a34a")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not export CSV:\n{e}")

    # -------------------------------------------------------------------------
    # Preset Handlers
    # -------------------------------------------------------------------------

    def _set_preset_test(self):
        """Set quick test targets: 299 K, 300 K."""
        self.target_temps_var.set("299, 300")
        self.soak_min_var.set(5.0)
        self.lbl_file_preview.config(text="299K_100mV_<HH-MM-SS>.dat")

    def _set_preset_full(self):
        """Set full production targets: 300 K to 470 K with step 5 K."""
        full_list = [f"{t}" for t in range(300, 475, 5)]
        self.target_temps_var.set(", ".join(full_list))
        self.soak_min_var.set(5.0)
        self.lbl_file_preview.config(text="300K_100mV_<HH-MM-SS>.dat")

    def _reset_pid_defaults(self):
        """Reset PID gains and power authority to validated defaults (P=70, I=900s, D=0, MaxPwr=100%, Range=HI)."""
        self.p_gain_var.set(70.0)
        self.i_gain_var.set(900.0)
        self.d_gain_var.set(0.0)
        self.max_power_var.set(100.0)
        self.heater_range_var.set("HI")
        if hasattr(self, "lbl_status"):
            self.lbl_status.config(
                text="Reset PID & Power to defaults (P=70, I=900s, D=0, MaxPwr=100%, Range=HI)",
                foreground="#0284c7"
            )

    def _browse_dir(self):
        d = filedialog.askdirectory(initialdir=self.out_dir_var.get())
        if d:
            self.out_dir_var.set(d)

    def _on_mock_toggle(self):
        if self.mock_var.get():
            self.lbl_conn_status.config(text="[MOCK SIMULATION MODE]", foreground="#7c3aed")
        else:
            self.lbl_conn_status.config(text="[DISCONNECTED]", foreground="#dc2626")

    def _update_estimated_time(self, *args):
        """
        Calculates and updates the estimated run duration live as Rate,
        Soak Time, Target Temperatures, or Frequency Points change.
        """
        try:
            raw_targets = self.target_temps_var.get()
            targets = []
            for t_str in raw_targets.split(","):
                t_str = t_str.strip()
                if t_str:
                    try:
                        targets.append(float(t_str))
                    except ValueError:
                        pass

            if not targets:
                if hasattr(self, "lbl_est_total"):
                    self.lbl_est_total.config(text="--", foreground="#dc2626")
                    self.lbl_est_details.config(text="No target temperatures specified.")
                if hasattr(self, "lbl_exec_est"):
                    self.lbl_exec_est.config(text="Est. Total Time: --")
                return

            num_stages = len(targets)
            try:
                rate = float(self.ramp_rate_var.get())
            except Exception:
                rate = 1.0
            if rate <= 0.01:
                rate = 1.0

            try:
                soak_min = float(self.soak_min_var.get())
            except Exception:
                soak_min = 5.0
            soak_min = max(0.0, soak_min)

            try:
                num_pts = int(self.num_pts_var.get())
            except Exception:
                num_pts = 200

            # 1. Total Delta T traversed (Kelvin)
            # If stage temp available and not yet running, use delta from current temp to first target
            curr_stage_t = None
            if hasattr(self, "temp_history") and self.temp_history and self.temp_history[-1] > 10.0:
                curr_stage_t = self.temp_history[-1]
            elif hasattr(self, "cryocon") and self.cryocon and hasattr(self.cryocon, "_temp_a") and self.cryocon._temp_a > 10.0:
                curr_stage_t = self.cryocon._temp_a

            initial_delta = abs(targets[0] - curr_stage_t) if curr_stage_t is not None else 0.0
            inter_stage_delta = sum(abs(targets[i] - targets[i - 1]) for i in range(1, num_stages))
            total_delta_k = initial_delta + inter_stage_delta

            # 2. Ramping duration (minutes)
            t_ramp_min = total_delta_k / rate

            # 3. Thermal soak duration (minutes)
            t_soak_min = num_stages * soak_min

            # 4. Sweep acquisition duration (~0.12s per frequency point on Wayne Kerr 6500)
            t_sweep_min = num_stages * (num_pts * 0.12) / 60.0

            # 5. Settle band entry overhead (~20 seconds per stage)
            t_settle_min = num_stages * (20.0 / 60.0)

            total_min = t_ramp_min + t_soak_min + t_sweep_min + t_settle_min

            tot_h = int(total_min // 60)
            tot_m = int(round(total_min % 60))
            if tot_m == 60:
                tot_h += 1
                tot_m = 0

            def fmt_hm(mins: float) -> str:
                m_int = int(round(mins))
                h = m_int // 60
                m = m_int % 60
                if h > 0:
                    return f"{h}h {m:02d}m"
                return f"{m}m"

            ramp_str = fmt_hm(t_ramp_min)
            soak_str = fmt_hm(t_soak_min)
            hw_str = fmt_hm(t_sweep_min + t_settle_min)

            summary_text = f"{tot_h}h {tot_m:02d}m ({total_min:.1f} min)"
            detail_text = (
                f"{num_stages} stages (Δ{total_delta_k:.0f}K) | Ramp: {ramp_str} | Soak: {soak_str} | Sweep+Settle: ~{hw_str}"
            )

            if hasattr(self, "lbl_est_total"):
                self.lbl_est_total.config(text=summary_text, foreground="#0f172a")
                self.lbl_est_details.config(text=detail_text)
            if hasattr(self, "lbl_exec_est"):
                self.lbl_exec_est.config(text=f"Est. Total Time: {summary_text} ({num_stages} stages | Ramp: {ramp_str} | Soak: {soak_str})")
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # Hardware Connection
    # -------------------------------------------------------------------------

    def connect_hardware(self):
        mock = self.mock_var.get()
        port = self.cryo_port_var.get().strip()
        baud = int(self.cryo_baud_var.get())
        visa_res = self.wk_visa_var.get().strip()

        self.lbl_status.config(text="Connecting to instruments...", foreground="#0284c7")
        self.root.update_idletasks()

        self.cryocon = Cryocon22C(port=port, baud_rate=baud, mock=mock)
        c_ok = self.cryocon.connect()

        self.wayne_kerr = WayneKerr6500B(resource_name=visa_res, mock=mock)
        w_ok = self.wayne_kerr.connect()

        if c_ok and w_ok:
            status_txt = "[CONNECTED - MOCK]" if mock else "[CONNECTED - LIVE HARDWARE]"
            color = "#7c3aed" if mock else "#16a34a"
            self.lbl_conn_status.config(text=status_txt, foreground=color)
            self.btn_connect.config(state=tk.DISABLED)
            self.btn_disconnect.config(state=tk.NORMAL)
            self.lbl_status.config(text="Connected to both instruments successfully.", foreground="#16a34a")

            # Start continuous thermal monitor
            self._monitor_active = True
            threading.Thread(target=self._background_telemetry_monitor, daemon=True).start()
        elif c_ok and not w_ok:
            if self.wayne_kerr:
                self.wayne_kerr.disconnect()
                self.wayne_kerr = None
            status_txt = "[CONNECTED - CRYOCON ONLY]" if not mock else "[CONNECTED - MOCK CRYOCON]"
            self.lbl_conn_status.config(text=status_txt, foreground="#d97706")
            self.btn_connect.config(state=tk.DISABLED)
            self.btn_disconnect.config(state=tk.NORMAL)
            self.lbl_status.config(
                text=f"Cryocon 22C connected on {port}. Wayne Kerr offline ({visa_res} not found).",
                foreground="#d97706"
            )
            # Start continuous thermal monitor for Cryocon
            self._monitor_active = True
            threading.Thread(target=self._background_telemetry_monitor, daemon=True).start()
            messagebox.showwarning(
                "Wayne Kerr Offline",
                f"✓ Successfully connected to Cryocon 22C on {port}.\n\n"
                f"⚠ Wayne Kerr on {visa_res} was not found (Offline).\n\n"
                f"Live temperature telemetry and control are now active!\n"
                f"To run impedance sweeps, power on Wayne Kerr and ensure GPIB/VISA is connected."
            )
        elif w_ok and not c_ok:
            if self.cryocon:
                self.cryocon.disconnect()
                self.cryocon = None
            status_txt = "[CONNECTED - WAYNE KERR ONLY]" if not mock else "[CONNECTED - MOCK WAYNE KERR]"
            self.lbl_conn_status.config(text=status_txt, foreground="#d97706")
            self.btn_connect.config(state=tk.DISABLED)
            self.btn_disconnect.config(state=tk.NORMAL)
            self.lbl_status.config(
                text=f"Wayne Kerr connected on {visa_res}. Cryocon offline ({port} not found).",
                foreground="#d97706"
            )
            messagebox.showwarning(
                "Cryocon Offline",
                f"✓ Successfully connected to Wayne Kerr on {visa_res}.\n\n"
                f"⚠ Cryocon 22C on {port} was not found (Offline)."
            )
        else:
            err = []
            if not c_ok:
                err.append(f"Cryocon 22C on {port}")
            if not w_ok:
                err.append(f"Wayne Kerr on {visa_res}")
            messagebox.showerror("Connection Failed", f"Could not connect to:\n" + "\n".join(err) + "\n\nTip: Enable 'Mock Mode' for offline testing.")
            self.disconnect_hardware()

    def disconnect_hardware(self):
        self._monitor_active = False
        self._suspend_background_monitor = False
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
        """Continuously poll temperature and heater in background when idle."""
        while getattr(self, "_monitor_active", False):
            # Check if background telemetry should be suspended (e.g. during experiment or ramp arming)
            if getattr(self, "_suspend_background_monitor", False):
                time.sleep(0.5)
                continue
            if self.orchestrator and getattr(self.orchestrator, "is_running", False):
                time.sleep(0.5)
                continue
            if self.cryocon and getattr(self.cryocon, "is_arming", False):
                time.sleep(0.5)
                continue

            if self.cryocon and self.cryocon.connected:
                try:
                    t_val = self.cryocon.read_temperature("A")
                    h_val = self.cryocon.read_heater_output(1)
                    sp_val = self.cryocon.get_setpoint(1)
                    now = time.time()
                    self.ui_queue.put(("monitor_tick", (now, t_val, sp_val, h_val)))
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
                "Cannot start automated impedance experiment:\n"
                "Wayne Kerr 6510B impedance analyzer is not connected.\n\n"
                "Please power on Wayne Kerr, connect GPIB/VISA, or enable 'Mock Mode'."
            )
            return

        try:
            raw_targets = self.target_temps_var.get().split(",")
            targets = [float(x.strip()) for x in raw_targets if x.strip()]
            if not targets:
                raise ValueError("No valid targets entered.")
        except Exception as e:
            messagebox.showerror("Invalid Targets", f"Please check the target temperature list: {e}")
            return

        soak_min = self.soak_min_var.get()
        settle_band = self.settle_band_var.get()
        rate = self.ramp_rate_var.get()
        max_power = min(100.0, max(1.0, self.max_power_var.get()))
        heater_range = self.heater_range_var.get().strip().upper()
        if heater_range not in ["HI", "MID", "LOW"]:
            heater_range = "HI"
        p_gain = max(0.0, self.p_gain_var.get())
        i_gain = max(0.0, self.i_gain_var.get())
        d_gain = max(0.0, self.d_gain_var.get())
        drive_level = self.bias_mv_var.get() / 1000.0  # mV to V
        num_pts = self.num_pts_var.get()
        start_f = self.start_f_var.get()
        stop_f = self.stop_f_var.get()
        out_dir = self.out_dir_var.get().strip()

        # Update UI buttons
        self.btn_start.config(state=tk.DISABLED)
        self.btn_skip_soak.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.NORMAL)

        # Suspend background telemetry monitor immediately to prevent serial collision with arming sequence
        self._suspend_background_monitor = True

        # Clear active sweep buffers
        self.current_sweep_freqs.clear()
        self.current_sweep_r.clear()
        self.current_sweep_x.clear()
        self.current_sweep_z.clear()
        self.current_sweep_theta.clear()

        # Initialize Orchestrator
        self.orchestrator = ExperimentOrchestrator(
            cryocon=self.cryocon,
            wayne_kerr=self.wayne_kerr,
            targets=targets,
            soak_time_min=soak_min,
            settle_band_k=settle_band,
            ramp_rate=rate,
            drive_level_v=drive_level,
            num_points=num_pts,
            start_f=start_f,
            stop_f=stop_f,
            out_dir=out_dir,
            p_gain=p_gain,
            i_gain=i_gain,
            d_gain=d_gain,
            max_power=max_power,
            heater_range=heater_range,
            on_status_update=lambda s: self.ui_queue.put(("status_update", s)),
            on_point_acquired=lambda pt: self.ui_queue.put(("point_acquired", pt)),
            on_sweep_completed=lambda p, t, pts: self.ui_queue.put(("sweep_completed", (p, t, pts)))
        )

        def _worker():
            try:
                self.orchestrator.run_experiment()
            except Exception as e:
                self.ui_queue.put(("experiment_error", str(e)))
            finally:
                self._suspend_background_monitor = False
                self.ui_queue.put(("experiment_done", None))

        self.worker_thread = threading.Thread(target=_worker, daemon=True)
        self.worker_thread.start()

    def skip_soak(self):
        if self.orchestrator:
            self.orchestrator.request_skip_stage()

    def abort_experiment(self):
        if self.orchestrator:
            self.lbl_status.config(text="ABORTING: Stopping heater and disengaging loop...", foreground="#dc2626")
            self.orchestrator.request_abort()

    def emergency_stop(self):
        """Hard emergency cut: sends STOP directly and immediately."""
        self.lbl_status.config(text="EMERGENCY STOP TRIGGERED: Cutting heater power to 0%!", foreground="#dc2626")
        if self.orchestrator:
            self.orchestrator.request_abort()
        if self.cryocon:
            threading.Thread(target=self.cryocon.stop_control, daemon=True).start()
        messagebox.showwarning("Emergency Stop", "Emergency STOP command dispatched.\nHeater power disengaged (CONTROL = OFF).")

    # -------------------------------------------------------------------------
    # UI Dispatcher & Real-Time Plots
    # -------------------------------------------------------------------------

    def _start_ui_dispatcher(self):
        def _check_queue():
            try:
                while True:
                    msg_type, payload = self.ui_queue.get_nowait()
                    self._handle_ui_message(msg_type, payload)
            except queue.Empty:
                pass
            self.root.after(100, _check_queue)

        self.root.after(100, _check_queue)

    def _on_window_change(self, event=None):
        sel = self.combo_window.get()
        mapping = {"2 min": 120, "5 min": 300, "10 min": 600, "15 min": 900, "30 min": 1800, "All": 999999999}
        self.plot_window_seconds = mapping.get(sel, 600)
        self._update_thermal_plot()

    def _clear_chart(self):
        self.time_history.clear()
        self.temp_history.clear()
        self.sp_history.clear()
        self.heater_history.clear()
        self.ax3_t.clear()
        self.ax3_h.clear()
        self.ax3_t.set_title("Cryo-con 22C — Live Temperature & Heater Profile", fontsize=10, fontweight="bold")
        self.ax3_t.set_xlabel("Elapsed Time (s)", fontsize=9)
        self.ax3_t.set_ylabel("Temperature (K)", color="#0066cc", fontsize=9)
        self.ax3_h.set_ylabel("Heater Output (%)", color="#8e24aa", fontsize=9)
        self.ax3_h.yaxis.set_label_position("right")
        self.ax3_h.yaxis.tick_right()
        self.ax3_h.set_ylim(0, 105)
        self.ax3_t.grid(True, linestyle="--", alpha=0.4)
        self.fig3.tight_layout()
        self.canvas3.draw_idle()

    def _handle_ui_message(self, msg_type: str, payload: Any):
        if msg_type == "monitor_tick":
            t_stamp, t_val, sp_val, h_val = payload
            self.lbl_digit_temp.config(text=f"{t_val:.3f} K")
            if not math.isnan(sp_val):
                self.lbl_digit_setpt.config(text=f"{sp_val:.2f} K")
            self.lbl_digit_heater.config(text=f"{h_val:.1f} %")

            # Update thermal profile history
            self.time_history.append(t_stamp)
            self.temp_history.append(t_val)
            self.sp_history.append(sp_val if not math.isnan(sp_val) else t_val)
            self.heater_history.append(h_val)
            if len(self.time_history) > self.max_plot_points:
                self.time_history.pop(0)
                self.temp_history.pop(0)
                self.sp_history.pop(0)
                self.heater_history.pop(0)

            now = time.time()
            if now - self.last_chart_draw >= 0.5:
                self.last_chart_draw = now
                self._update_thermal_plot()

        elif msg_type == "status_update":
            s = payload
            st_idx = s["stage_idx"] + 1
            tgt = s["target_k"]
            live_sp = s.get("live_setpt_k", tgt)
            cur_t = s["current_temp_k"]
            err = s["error_k"]
            h_pct = min(100.0, max(0.0, s["heater_pct"]))
            phase = s["phase"]
            soak_rem = s["soak_remaining_sec"]
            soak_pct = s["soak_progress_pct"]

            self.lbl_digit_temp.config(text=f"{cur_t:.3f} K")
            self.lbl_digit_setpt.config(text=f"{live_sp:.2f} K")
            self.lbl_digit_heater.config(text=f"{h_pct:.1f} %")

            if phase == "ARMING":
                self.lbl_status.config(text=f"STAGE {st_idx}: ARMING Anti-Surge Ramp towards {tgt:.2f} K...", foreground="#e65100")
                self.lbl_soak_status.config(text="Synchronizing setpoint & arming loop...")
                self.progress_bar["value"] = 0
            elif phase == "RAMPING":
                self.lbl_status.config(text=f"STAGE {st_idx}: RAMPING towards {tgt:.2f} K (Error: {err:+.3f} K)", foreground="#0284c7")
                self.lbl_soak_status.config(text="Waiting to reach setpoint band...")
                self.progress_bar["value"] = 0
            elif phase == "SOAKING":
                m = int(soak_rem // 60)
                sec = int(soak_rem % 60)
                self.lbl_status.config(text=f"STAGE {st_idx}: SAMPLE SOAK (Equilibrating PMN-PT crystal at {cur_t:.3f} K)", foreground="#d97706")
                self.lbl_soak_status.config(text=f"Soak Remaining: {m:02d}:{sec:02d} ({soak_pct:.0f}%)")
                self.progress_bar["value"] = soak_pct
            elif phase == "SWEEPING":
                self.lbl_status.config(text=f"STAGE {st_idx}: SWEEPING 20 Hz - 10 MHz Impedance at {tgt:.2f} K", foreground="#16a34a")
                self.lbl_soak_status.config(text="Impedance Acquisition in progress...")

            if hasattr(self, "lbl_exec_est") and hasattr(self, "orchestrator") and self.orchestrator:
                tot_stages = len(self.orchestrator.targets)
                rem_stages = max(0, tot_stages - st_idx)
                self.lbl_exec_est.config(
                    text=f"Stage {st_idx}/{tot_stages} in progress ({rem_stages} stages remaining after this)"
                )

            now = time.time()
            self.time_history.append(now)
            self.temp_history.append(cur_t)
            self.sp_history.append(live_sp)
            self.heater_history.append(h_pct)
            if len(self.time_history) > self.max_plot_points:
                self.time_history.pop(0)
                self.temp_history.pop(0)
                self.sp_history.pop(0)
                self.heater_history.pop(0)

            if now - self.last_chart_draw >= 0.5:
                self.last_chart_draw = now
                self._update_thermal_plot()

        elif msg_type == "point_acquired":
            pt = payload
            pt_idx = pt["point_idx"]
            total = pt["total_points"]
            f = pt["freq_hz"]
            r = pt["r_ohm"]
            x = pt["x_ohm"]
            z = pt["z_mag_ohm"]
            theta = pt["theta_deg"]
            t_live = pt.get("t_k", float("nan"))

            self.current_sweep_freqs.append(f)
            self.current_sweep_r.append(r)
            self.current_sweep_x.append(x)
            self.current_sweep_z.append(z)
            self.current_sweep_theta.append(theta)

            self.progress_bar["value"] = (pt_idx / total) * 100.0
            self.lbl_soak_status.config(text=f"Point {pt_idx}/{total}: {f:,.1f} Hz | R={r:.2e} Ω | X={x:.2e} Ω")

            if not math.isnan(t_live):
                self.lbl_digit_temp.config(text=f"{t_live:.3f} K")
                now = time.time()
                if now - getattr(self, "_last_sweep_thermal_time", 0) >= 0.5:
                    self._last_sweep_thermal_time = now
                    cur_sp = self.sp_history[-1] if self.sp_history else t_live
                    cur_h = self.heater_history[-1] if self.heater_history else 0.0
                    self.time_history.append(now)
                    self.temp_history.append(t_live)
                    self.sp_history.append(cur_sp)
                    self.heater_history.append(cur_h)
                    if len(self.time_history) > self.max_plot_points:
                        self.time_history.pop(0)
                        self.temp_history.pop(0)
                        self.sp_history.pop(0)
                        self.heater_history.pop(0)
                    if now - self.last_chart_draw >= 0.5:
                        self.last_chart_draw = now
                        self._update_thermal_plot()

            # Update real-time curves point by point
            self._update_sweep_plots()

        elif msg_type == "sweep_completed":
            filepath, target_k, pts = payload
            self.all_completed_sweeps.append({
                "target_k": target_k,
                "filepath": filepath,
                "points": list(pts)
            })
            self.lbl_status.config(text=f"Saved: {os.path.basename(filepath)}", foreground="#16a34a")

            # Dynamically ingest target isofrequencies into PMN-PT permittivity plot
            self._ingest_sweep_points_for_permittivity(target_k, pts)

            # Clear active buffer for next stage
            self.current_sweep_freqs.clear()
            self.current_sweep_r.clear()
            self.current_sweep_x.clear()
            self.current_sweep_z.clear()
            self.current_sweep_theta.clear()

        elif msg_type == "experiment_error":
            err_msg = payload
            messagebox.showerror("Experiment Error", f"Orchestrator error:\n{err_msg}")
            self.lbl_status.config(text=f"ERROR: {err_msg}", foreground="#dc2626")

        elif msg_type == "experiment_done":
            self.btn_start.config(state=tk.NORMAL)
            self.btn_skip_soak.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.DISABLED)
            self.progress_bar["value"] = 100

            # A stalled thermal stage aborts the run on purpose - surface it loudly
            # instead of reporting a clean finish.
            stall = getattr(self.orchestrator, "stall_error", None) if self.orchestrator else None
            if stall:
                self.lbl_status.config(text=f"RUN ABORTED - THERMAL STALL: {stall}", foreground="#dc2626")
                if hasattr(self, "lbl_exec_est"):
                    self.lbl_exec_est.config(text="Run aborted: temperature stage stalled. Heater is OFF.")
                msg_txt = (
                    str(stall)
                    + "\n\nThe Cryo-con heater has been disengaged (CONTROL = OFF)."
                    + "\nCompleted sweeps are safe in the data folder."
                    + "\nRestart the run from the first missing temperature."
                )
                messagebox.showerror("Thermal Stall - Run Aborted", msg_txt)
            else:
                self.lbl_status.config(text="Experiment sequence finished. Heater stopped and safe.", foreground="#16a34a")
                if hasattr(self, "lbl_exec_est"):
                    self.lbl_exec_est.config(text="Experiment Complete! All stages finished successfully.")

    def _update_thermal_plot(self):
        if not self.time_history:
            return

        self.ax3_t.clear()
        self.ax3_h.clear()

        # Enforce secondary Heater axis strictly on the RIGHT side
        self.ax3_h.yaxis.tick_right()
        self.ax3_h.yaxis.set_label_position("right")

        t_now = self.time_history[-1]
        cutoff = t_now - self.plot_window_seconds

        indices = [i for i, t in enumerate(self.time_history) if t >= cutoff]
        if not indices:
            indices = list(range(len(self.time_history)))

        t_base = self.time_history[0]
        times_rel = [(self.time_history[i] - t_base) for i in indices]

        visible_temps = []

        # Temp A (Sample Stage)
        if self.chk_show_a.get() and len(self.temp_history) >= len(indices):
            y_a = [self.temp_history[i] for i in indices]
            valid_ya = [v for v in y_a if v == v and v > 0]
            if valid_ya:
                self.ax3_t.plot(times_rel, y_a, label="Temp A (Sample)", color="#0066cc", linewidth=2.0)
                visible_temps.extend(valid_ya)

        # Setpoint (Dashed Orange Line)
        if self.chk_show_sp.get() and len(self.sp_history) >= len(indices):
            y_sp = [self.sp_history[i] for i in indices]
            valid_sp = [v for v in y_sp if v == v and v > 0]
            if valid_sp:
                self.ax3_t.plot(times_rel, y_sp, label="Setpoint", color="#e65100", linewidth=1.6, linestyle="--")
                visible_temps.extend(valid_sp)

        # Heater % Output (Secondary Axis on RIGHT)
        visible_heaters = []
        if self.chk_show_ht.get() and len(self.heater_history) >= len(indices):
            y_ht = [min(100.0, max(0.0, self.heater_history[i])) for i in indices]
            self.ax3_h.plot(times_rel, y_ht, label="Heater %", color="#8e24aa", linewidth=1.0, alpha=0.6)
            visible_heaters.extend(y_ht)

        # Autoscale Temperature (Y-axis 1 - Left)
        if self.chk_autoscale_temp.get() and visible_temps:
            y_min = min(visible_temps)
            y_max = max(visible_temps)
            span = y_max - y_min
            if span < 1.0:
                mid = (y_max + y_min) / 2.0
                self.ax3_t.set_ylim(mid - 1.0, mid + 1.0)
            else:
                margin = span * 0.08
                self.ax3_t.set_ylim(y_min - margin, y_max + margin)

        # Autoscale Heater (Y-axis 2 - Right)
        if self.chk_autoscale_ht.get() and visible_heaters:
            max_ht = max(visible_heaters)
            self.ax3_h.set_ylim(0, max(20.0, max_ht * 1.25))
        else:
            self.ax3_h.set_ylim(0, 105)

        self.ax3_t.set_title("Cryo-con 22C — Live Temperature & Heater Profile", fontsize=10, fontweight="bold")
        self.ax3_t.set_xlabel("Elapsed Time (s)", fontsize=9)
        self.ax3_t.set_ylabel("Temperature (K)", color="#0066cc", fontsize=9)
        self.ax3_h.set_ylabel("Heater Output (%)", color="#8e24aa", fontsize=9)
        self.ax3_h.yaxis.set_label_position("right")
        self.ax3_h.yaxis.tick_right()
        self.ax3_t.grid(True, linestyle="--", alpha=0.4)

        handles1, labels1 = self.ax3_t.get_legend_handles_labels()
        if handles1:
            self.ax3_t.legend(loc="upper left", fontsize=8)
        handles2, labels2 = self.ax3_h.get_legend_handles_labels()
        if handles2:
            self.ax3_h.legend(loc="upper right", fontsize=8)

        self.fig3.tight_layout()
        self.canvas3.draw_idle()

    def _update_sweep_plots(self):
        if not self.current_sweep_freqs:
            return

        freqs = self.current_sweep_freqs
        r_vals = [abs(v) + 1e-12 for v in self.current_sweep_r]
        x_vals = self.current_sweep_x
        z_vals = [max(1e-12, v) for v in self.current_sweep_z]
        th_vals = self.current_sweep_theta

        # Tab 1: R and X
        self.ax1_r.clear()
        self.ax1_r.set_title("Real Resistance R (Ohm) vs. Frequency", fontsize=10, fontweight="bold")
        self.ax1_r.plot(freqs, r_vals, color="#2563eb", marker=".", markersize=4, label="R (Live)")
        self.ax1_r.set_ylabel("R (Ohm)")
        self.ax1_r.set_xscale("log")
        self.ax1_r.set_yscale("log")
        self.ax1_r.grid(True, which="both", linestyle="--", alpha=0.5)

        self.ax1_x.clear()
        self.ax1_x.set_title("Reactance X (Ohm) vs. Frequency", fontsize=10, fontweight="bold")
        self.ax1_x.plot(freqs, x_vals, color="#dc2626", marker=".", markersize=4, label="X (Live)")
        self.ax1_x.set_xlabel("Frequency (Hz)")
        self.ax1_x.set_ylabel("X (Ohm)")
        self.ax1_x.set_xscale("log")
        self.ax1_x.grid(True, which="both", linestyle="--", alpha=0.5)
        self.canvas1.draw_idle()

        # Tab 2: Bode (|Z| and theta)
        self.ax2_z.clear()
        self.ax2_z.set_title("Impedance Magnitude |Z| vs. Frequency", fontsize=10, fontweight="bold")
        self.ax2_z.plot(freqs, z_vals, color="#7c3aed", marker=".", markersize=4)
        self.ax2_z.set_ylabel("|Z| (Ohm)")
        self.ax2_z.set_xscale("log")
        self.ax2_z.set_yscale("log")
        self.ax2_z.grid(True, which="both", linestyle="--", alpha=0.5)

        self.ax2_th.clear()
        self.ax2_th.set_title("Phase Angle theta (deg) vs. Frequency", fontsize=10, fontweight="bold")
        self.ax2_th.plot(freqs, th_vals, color="#059669", marker=".", markersize=4)
        self.ax2_th.set_xlabel("Frequency (Hz)")
        self.ax2_th.set_ylabel("Phase (deg)")
        self.ax2_th.set_xscale("log")
        self.ax2_th.grid(True, which="both", linestyle="--", alpha=0.5)
        self.canvas2.draw_idle()

        # Tab 4: Nyquist (-X vs R)
        self.ax4_ny.clear()
        neg_x = [-x for x in x_vals]
        self.ax4_ny.set_title("Nyquist Plot: -X vs R", fontsize=10, fontweight="bold")
        self.ax4_ny.plot(r_vals, neg_x, color="#0284c7", marker="o", markersize=3)
        self.ax4_ny.set_xlabel("R (Ω)")
        self.ax4_ny.set_ylabel("-X (Ω)")
        self.ax4_ny.grid(True, linestyle="--", alpha=0.5)
        self.canvas4.draw_idle()


def main():
    root = tk.Tk()
    app = UnifiedLabGUI(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.disconnect_hardware(), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main()
