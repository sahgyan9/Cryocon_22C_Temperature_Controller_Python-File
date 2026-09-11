# Wayne Kerr 6510B & Cryo-con 22C — Unified Impedance Spectroscopy Suite

Automated temperature-dependent dielectric spectroscopy suite unifying the **Cryo-con 22C Temperature Controller** (`COM5`) and the **Wayne Kerr 6510B Precision Impedance Analyzer** (`GPIB0::6::INSTR`) for **PMN-0.3PT** ($0.70\text{Pb}(\text{Mg}_{1/3}\text{Nb}_{2/3})\text{O}_3 - 0.30\text{PbTiO}_3$) crystal characterization from 300 K to 470 K (with quick-test support at 299 K & 300 K).

---

## 🧪 Sample Under Test: PMN-0.3PT (0.70PMN-0.30PT)

- **Material:** $0.70\text{Pb}(\text{Mg}_{1/3}\text{Nb}_{2/3})\text{O}_3 - 0.30\text{PbTiO}_3$ ($x = 0.30$), a relaxor-based ferroelectric on the rhombohedral side of the Morphotropic Phase Boundary (MPB).
- **Latest Measurement Location:** [`Cryocon-22C_and_Wayne_Kerr/Data/`](Data/)
  - **Recorded Sweeps:** 57 full-spectrum impedance files from **300.0 K to 412.0 K** in 2.0 K steps (`300K_100mV_*.dat` to `412K_100mV_*.dat`).
  - **Sweep Parameters:** 200 logarithmic frequency points from **20 Hz to 10 MHz**, 100 mV AC excitation RMS.
- **Sample Geometry & Vacuum Capacitance:**
  - Standard pre-populated defaults: Thickness $d = 0.30\text{ mm}$ ($300\text{ }\mu\text{m}$), Electrode Area $A = 6.00\text{ mm}^2$.
  - Vacuum Capacitance: $C_0 = \varepsilon_0 \frac{A}{d} \approx 0.17708\text{ pF}$.
- **Key Phase Transitions & Literature Signatures:**
  - **Rhombohedral-to-Tetragonal Transition ($T_{R-T}$):** $\approx 370 - 374\text{ K}$ ($97 - 101^\circ\text{C}$). Manifests as a distinct inflection/kink anomaly on the permittivity curve.
  - **Dielectric Maximum ($T_m$ / Curie Region):** $\approx 410 - 440\text{ K}$ ($137 - 167^\circ\text{C}$).

---

## 📌 Reference Codebases & Architecture Lineage

This workspace unifies and coordinates the code, drivers, and lessons learned from two upstream laboratory repositories:

1. **Wayne Kerr Impedance Analyzer Suite:**
   - **Path:** `C:\Users\sahgy\Downloads\Wayne_kerr_2500B`
   - **Extracted Components & Reference:**
     - Core VISA driver for the Wayne Kerr 6510B (`wayne_kerr_controller.py`).
     - Automated headless GUI simulation test pattern (`verify_simplified_gui.py`).
     - Zero-locking live file tailing logic (`live_view.py`).
     - Standard laboratory tab-delimited acquisition schema: `Time (s)\tLight (A)\tT (K)\tf (Hz)\tR (Ohm)\tX (Ohm)`.
     - Hardware frequency limits (20 Hz minimum, 10 MHz maximum).

2. **Cryo-con 22C Temperature Controller Suite:**
   - **Path:** `C:\Users\sahgy\Downloads\Cryocon_22C_Temperature_Controller_Python-File`
   - **Extracted Components & Reference:**
     - Core RS-232 serial driver for Cryo-con 22C (`cryocon_controller.py` on `COM5` @ 57,600 baud).
     - Validated anti-windup PID tuning parameters: `P=40.0, I=900.0 s, D=0.0, Range=HI, MaxPwr=70%`.
     - Critical anti-surge arming sequence: park at live temperature in PID mode, engage `CONTROL`, then switch to `RAMPP` and send setpoint last.
     - Unattended staged ramp state machine and settle detection (`staged_ramp_test.py`).
     - Overshoot technical reports and physical plant parameters (`FINAL_REPORT.html`, `OVERSHOOT_TUNING_LOG.md`).

3. **Unified Production Workspace:**
   - **Path:** `C:\Users\sahgy\Downloads\Cryocon-22C_and_Wayne_Kerr`
   - **Integrated Capability:** Desktop GUI ([`unified_gui.py`](unified_gui.py)), headless orchestrator ([`unified_experiment_runner.py`](unified_experiment_runner.py)), automated verification suite ([`verify_unified_gui.py`](verify_unified_gui.py)), and 5-minute PMN-0.3PT crystal thermal soak watchdog.

4. **PMN-0.3PT Dielectric Permittivity Suite:**
   - **Path:** `C:\Users\sahgy\Downloads\Impedance_PMN-PT`
   - **Extracted Physics & Characterization:**
     - Real relative permittivity: $\varepsilon'(T) = \frac{-X}{\omega C_0 (R^2 + X^2)}$ where $C_0 = \varepsilon_0 \frac{A}{d} \approx 0.177\text{ pF}$ ($d=0.30\text{ mm}, A=6.00\text{ mm}^2$).
     - Dual-mode interactive visualization matching `PMN_PT_Dielectric_Permittivity_Analysis.ipynb`:
       - **Figure (a)**: All Frequencies (1 kHz to 10 MHz)
       - **Figure (b)**: Bulk Dielectric Response (1 kHz to 1 MHz)
     - Dynamic nearest-frequency decade approximation: automatically extracts optimal points from 200-pt (`Wayne_kerr_2500B` and `Data/`) and 201-pt (`Impedance_PMN-PT`) sweeps.
     - Curie transition summary metrics ($T_m$ peak temperature, max $\varepsilon'$, $\varepsilon'$ at 300 K) matching `permittivity_summary.csv`.
     - 1-click PMN-0.3PT reference loader and live multi-stage sweep accumulation.

---

## Key Features & Pre-Populated Defaults

| Parameter | Pre-Populated Default Value | Description |
|---|---|---|
| **Cryocon Port** | `COM5` (57,600 baud, 8N1) | Upgraded high-speed communication |
| **Wayne Kerr VISA** | `GPIB0::6::INSTR` | Primary IEEE-488.2 interface |
| **Target Temperatures** | `300 to 470 K` (Step: 5 K) | Or quick-test preset: `299, 300 K` |
| **Sample Thermal Soak** | **5.0 minutes** (300 seconds) | Holds within $\pm 0.10$ K for PMN-PT thermal equilibrium |
| **Settle Band** | `±0.10 K` | Settle detection tolerance window |
| **Ramp Rate** | `1.0 K/min` | Clean linear ramp with zero overshoot |
| **PID Tuning** | `P=40, I=900 s, D=0, HI, 70%` | Validated anti-windup parameters |
| **Frequency Span** | **20 Hz to 10 MHz** | 200 logarithmic points (hardware limits) |
| **AC Drive (Bias)** | **100 mV RMS** (`0.100 V`) | AC excitation amplitude |
| **Measurement Mode** | **R - X** (Series Circuit) | Real Resistance and Reactance |
| **Live Duration Estimate** | **Dynamic (Tkinter trace)** | Updates live as Rate (K/min), Soak (min), or targets change |
| **Scrollable Viewport** | **tk.Canvas + Scrollbar** | Full mousewheel & scrollbar support; all 4 panels fit on any screen/DPI |
| **File Naming** | `<Tempr>_<Bais>_<time_stamp>.dat` | e.g. `300K_100mV_11-56-28.dat` in `Data/` |

---

## Quick Start Guide

### Option 1: Laboratory Desktop GUI (Recommended)
Double-click `run_gui.bat` or run from terminal:
```bash
python unified_gui.py
```
1. Click **Connect Hardware** (or check **Mock Mode** for offline testing).
2. Use **Presets**:
   - Click `Test: 299, 300 K` for the immediate test run.
   - Or click `Full: 300 to 470 K (Step 5)` for the complete run.
3. Click **▶ START EXPERIMENT**.
4. The system will automatically:
   - Ramp to the first setpoint (e.g. 299 K).
   - Enter the $\pm 0.10$ K band and start the **5-minute sample soak timer**.
   - Stream the 200-point logarithmic RX sweep to `Data/299K_100mV_<timestamp>.dat`.
   - Update the real-time plots point-by-point.
   - Advance to the next temperature (e.g. 300 K) and repeat until complete.
5. **Live Temperature Graph (Original Cryo-con 22C Visualizer):**
   - Switch to the **📈 Live Temperature Graph** tab (Tab 3) for real-time thermal tracking.
   - **Dual-Axis Display:** Stage Temperature (solid blue `#0066cc`) and Setpoint (dashed orange `#e65100`) on the primary left Y-axis in Kelvin; Heater Output Power % (purple `#8e24aa`) on the secondary right Y-axis via `twinx`.
   - **Interactive Toolbar:** Filter history using the **Time Window** selector (`2 min`, `5 min`, `10 min`, `15 min`, `30 min`, `All`), toggle individual traces via checkbuttons (`Temp A`, `Setpoint`, `Heater %`), toggle `Autoscale Y` and `Autoscale Pwr`, and click `Clear Chart` or `⛶ Fit Scale`.
   - Continuously updates during background idle monitoring and across all experiment stages (`RAMPING`, `SOAKING`, `SWEEPING`).
6. **PMN-0.3PT Dielectric Permittivity Analysis:**
   - Switch to the **PMN-0.3PT Permittivity vs T** tab (Tab 5) to observe Real Relative Permittivity $\varepsilon'$ across 1 kHz, 10 kHz, 100 kHz, 1 MHz, and 10 MHz.
   - Click **⚡ Load Latest (Data/)** or **⚡ Load Reference** to inspect permittivity curves (including the latest 57-point dataset from 300 K to 412 K).
   - Toggle between **All Frequencies (1 kHz - 10 MHz)** [Fig a] and **Bulk Response (1 kHz - 1 MHz)** [Fig b].
   - Adjust sample thickness $d$ or electrode area $A$ in Section 3 to see live recalculated permittivity curves and $C_0$.
   - Inspect the Curie and phase transition summary table ($T_m$, $T_{R-T}$, max $\varepsilon'$, $\varepsilon'$ at 300 K) and export publication-ready data via **💾 Export CSV**.
7. **⏱ Live Estimated Experiment Duration Engine:**
   - Located in Section 1 (**Temperature Ramp & Soak Control**), the live status badge dynamically recalculates and displays the exact total estimated run time and phase breakdown:
     $$T_{\text{total}} = \frac{\Delta T_{\text{total}}}{\text{Rate}} + (N \times t_{\text{soak}}) + N \times \left( \frac{N_{\text{pts}} \times 0.12\text{ s} + 20\text{ s}}{60} \right)$$
   - Re-evaluates instantly via Tkinter observers whenever **Rate (K/min)**, **Sample Soak (min)**, or **Target Temps (K)** are adjusted, or when preset buttons (**Full: 300 to 470 K** or **Test: 299, 300 K**) are clicked.
   - For the standard Full sequence (300 K to 470 K, 35 stages):
     - **Rate 1.0 K/min, Soak 5.0 min:** `6h 11m (370.7 min)`
     - **Rate 2.0 K/min, Soak 5.0 min:** `4h 46m (285.7 min)`
     - **Rate 2.0 K/min, Soak 2.0 min:** `3h 01m (180.7 min)`
   - Section 4 (**Automation Execution & Status**) tracks stage progress live (e.g. `Stage 12/35 in progress (23 stages remaining)`).
8. **Responsive Scrollable Left Control Panel:**
   - The 4 control sections (Temperature Ramp, Frequency Sweep, Sample Geometry, and Automation Execution) are housed in a scrollable canvas with vertical scrollbar and full mousewheel support.
   - Compacted vertical padding ensures all 4 sections are immediately visible without scrolling on standard displays, while smooth scrolling guarantees complete accessibility on smaller monitors or with high-DPI scaling (125%/150%).
9. In case of emergency, click the red **⚠ EMERGENCY STOP** button.

---

### Option 2: Automated Command-Line Runner (Headless)

```bash
# Immediate test run on hardware: 299 K and 300 K with 5-minute soak
python unified_experiment_runner.py --targets 299,300 --soak-min 5.0 --rate 2.0 --level 0.1 --points 200

# Full automated production run: 300 K to 470 K in 5 K steps
python unified_experiment_runner.py --use-range --start 300 --stop 470 --step 5 --soak-min 5.0 --rate 2.0 --level 0.1 --points 200

# Offline dry-run in mock simulation mode:
python unified_experiment_runner.py --mock --targets 299,300 --soak-min 0.05 --points 20
```

---

### Option 3: Live File Tailer (Zero-Locking Terminal Monitor)
Run in a secondary terminal to watch active sweeps without occupying COM5 or GPIB:
```bash
python live_view.py
```

---

## Output Data Format

Data files are saved in `Data/` using tab-delimited columns matching laboratory standards:

```tsv
Time (s)	Light (A)	T (K)	f (Hz)	R (Ohm)	X (Ohm)
0.021	0.000	298.000	20.000	6990.516	-6059945.457
0.042	0.000	298.000	39.900	3596.501	-3048589.277
...
```

---

## Directory Structure

```
c:\Users\sahgy\Downloads\Cryocon-22C_and_Wayne_Kerr/
│
├── unified_gui.py                 # Interactive Tkinter Desktop GUI
├── unified_experiment_runner.py   # CLI / headless experiment orchestrator
├── cryocon_controller.py          # Cryo-con 22C serial driver (57.6k baud)
├── wayne_kerr_controller.py       # Wayne Kerr 6510B GPIB driver
├── live_view.py                   # Live file tailer (zero COM/VISA contention)
├── run_gui.bat                    # One-click Windows GUI launcher
├── requirements.txt               # Dependencies
├── LEARNING_LOG.md                # Complete 0-to-1 operational history & physics
├── README.md                      # This file
└── Data/                          # Acquired .dat files
```

---

## Safety & Troubleshooting

- **Emergency Disengage:** The software sends `STOP` to Cryo-con on every exit path (normal exit, exception, Ctrl+C, or Emergency Stop button).
- **Single Process Ownership:** Only one program can access `COM5` at a time. If the GUI is connected, do not run CLI scripts until Disconnect is clicked.
- **Hardware Minimum Frequency:** Wayne Kerr 6510B clamps frequencies below 20 Hz to 20.0 Hz.
- **Comprehensive Technical Reference:** Read `LEARNING_LOG.md` for full engineering context, anti-surge sequence details, and PMN-PT physics.
