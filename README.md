# Cryocon 22C Temperature Controller — Python & GUI Suite

A complete Python automation suite and graphical user interface (GUI) designed for the **Cryocon Model 22C Cryogenic Temperature Controller**.

## 📦 Prerequisites & Installation

Clone the repository and install the required Python packages:

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
pip install -r requirements.txt
```

*Required packages:*
- `pyserial` (>= 3.5) — For RS-232 / USB communication with Cryocon 22C
- `matplotlib` (>= 3.5.0) — For live real-time rolling telemetry graphs
- `tkinter` — Built into standard Python distributions on Windows

---

## 🚀 Quick Start

### Option 1: 1-Click Desktop GUI Launcher (Recommended)
Double-click [`run_gui.bat`](run_gui.bat) or run from PowerShell:
```powershell
& "C:\Users\SRMAP\anaconda3\python.exe" cryocon_gui.py
```

### Option 2: Automated Two-Speed Ramping via Command Line
```powershell
& "C:\Users\SRMAP\anaconda3\python.exe" smart_ramp_cli.py --target 350.0 --fast 5.0 --slow 0.5 --delta 15.0 --table 2 --hold 10
```

---

## 🖥️ Graphical User Interface (`cryocon_gui.py`)

The dashboard provides real-time telemetry, automated ramping, interactive graphing, data logging, and PID table management.

### Key GUI Features:
1. **Live Telemetry Cards**:
   * **Channel A (Sample)**: Main sample temperature readout with high decimal precision.
   * **Channel B**: Secondary channel temperature readout.
   * **Setpoint & Error**: Real-time target setpoint and deviation ($T_{sample} - T_{setpoint}$).
   * **Heater Output (%)**: Percentage power applied with live visual progress bar.
   * **Status Badges**: Real-time indicators for `CONTROL` state (`ON`/`OFF`), `PID TABLE` in use (`1` or `2`), `RANGE` (`HI`/`MID`/`LOW`), and `RAMP RATE`.

2. **🎯 Smart Two-Speed Ramping Engine (Zero Overshoot)**:
   * Enter target setpoint (or click quick presets: `300K`, `315K`, `350K`, `400K`, `450K`).
   * Automatically executes a fast approach when far from target, and automatically downshifts to a gentle rate ($0.5\text{ K/min}$) when within the configurable delta threshold ($15\text{ K}$) to **prevent temperature overshoot**.
   * Automatically detects stabilization ($|Error| < 0.2\text{ K}$) and maintains steady hold.

3. **📈 Real-Time Rolling Matplotlib Graph**:
   * Displays live **Temp A**, **Temp B**, and **Heater Power Output %**.
   * **Selectable Time Windows**: `2 min`, `5 min`, `10 min`, `15 min`, `30 min`, or `All`.
   * **Smart Auto-Scaling**: Dynamic Y-axis auto-zoom with span margin protection, toggleable heater power scaling, and 1-click `Fit Scale` button.

4. **📋 PID Table Viewer & Manager**:
   * Tabular inspection of **PID Table 01** ($20\text{K} \to 320\text{K}$) and **PID Table 02** ($180\text{K} \to 475\text{K}$).
   * 1-Click button to switch active table between Table 1 and Table 2.
   * 1-Click button to re-flash / verify Table 02 directly to controller non-volatile memory.

5. **💾 Continuous CSV Data Logging**:
   * One-click recording to timestamped CSV files (`cryocon_log_YYYYMMDD_HHMMSS.csv`).
   * Records every second with live record counter and file path status.

6. **🛑 Safety Emergency Stop**:
   * Dedicated red **EMERGENCY STOP** button to immediately disengage heater power ($0\%$) and abort all ramping operations.

---

## 🎯 How Smart Two-Speed Ramping Eliminates Overshoot

High thermal mass cryogenic systems often overshoot their setpoints when ramping aggressively because heat added by the heater continues to soak into the sample after the setpoint is reached.

```
Temperature (K)
     ^
     |                                    [HOLD STAGE]
T_sp + - - - - - - - - - - - - - - - - - -============= (Target reached with zero overshoot)
     |                             ..''''
     |                     ..''''  <-- [GENTLE STAGE: 0.5 K/min within 15K delta]
T_sw + - - - - - - ..''''              PID has time to brake heater output smoothly
     |         ..''
     |     ..''  <-- [FAST STAGE: 5.0 K/min]
     |  .''          Rapidly brings temperature close to target
 T_0 +''
     +----------------------------------------------------> Time
```

1. **Fast Stage**: Ramps at high speed (e.g. $5.0\text{ K/min}$) while $|T - T_{target}| > 15\text{ K}$.
2. **Gentle Stage**: When within $15\text{ K}$, automatically transitions to $0.5\text{ K/min}$. Because $0.5\text{ K/min}$ is slower than the cryostat's natural dissipation rate, the PID controller can gently reduce heater power *before* crossing the target.
3. **Hold Stage**: Automatically locks onto setpoint with error $< 0.2\text{ K}$.

---

## 📊 PID Tables Reference

The Cryocon 22C supports user PID tables with up to 16 entries each.

### PID Table 02: High-Temperature Extension ($180\text{K} \to 475\text{K}$)
Stored in controller slot `TABLE 2`:

| Row | Setpoint (K) | P Gain | I Gain | D Gain | Heater Range | Source |
|:---:|:------------:|:------:|:------:|:------:|:------------:|:------:|
| 1 | **475.00** | 2.50 | 250.00 | 60.00 | HI | Default |
| 2 | **460.00** | 2.40 | 240.00 | 60.00 | HI | Default |
| 3 | **440.00** | 2.30 | 230.00 | 50.00 | HI | Default |
| 4 | **420.00** | 2.20 | 220.00 | 50.00 | HI | Default |
| 5 | **400.00** | 2.10 | 210.00 | 50.00 | HI | Default |
| 6 | **380.00** | 2.00 | 200.00 | 50.00 | HI | Default |
| 7 | **360.00** | 1.90 | 190.00 | 40.00 | HI | Default |
| 8 | **340.00** | 1.80 | 180.00 | 40.00 | HI | Default |
| 9 | **320.00** | 1.70 | 170.00 | 40.00 | HI | Default |
| 10 | **300.00** | 1.60 | 160.00 | 40.00 | HI | Default |
| 11 | **280.00** | 1.50 | 150.00 | 30.00 | HI | Default |
| 12 | **260.00** | 1.40 | 140.00 | 30.00 | HI | Default |
| 13 | **240.00** | 1.30 | 130.00 | 30.00 | HI | Default |
| 14 | **220.00** | 1.20 | 120.00 | 30.00 | HI | Default |
| 15 | **200.00** | 1.10 | 110.00 | 20.00 | MID | Default |
| 16 | **180.00** | 1.00 | 100.00 | 20.00 | MID | Default |

### PID Table 01: Factory Low-Temperature ($20\text{K} \to 320\text{K}$)
Stored in controller slot `TABLE 1`:

| Row | Setpoint (K) | P Gain | I Gain | D Gain | Heater Range | Source |
|:---:|:------------:|:------:|:------:|:------:|:------------:|:------:|
| 1 | **320.00** | 1.60 | 160.00 | 40.00 | HI | ChA |
| 2 | **300.00** | 1.60 | 160.00 | 40.00 | HI | ChA |
| 3 | **280.00** | 1.50 | 150.00 | 30.00 | HI | ChA |
| 4 | **260.00** | 1.40 | 140.00 | 30.00 | LOW | Default |
| 5 | **240.00** | 1.30 | 130.00 | 30.00 | LOW | Default |
| 6 | **220.00** | 1.20 | 120.00 | 30.00 | LOW | Default |
| 7 | **200.00** | 1.10 | 110.00 | 20.00 | LOW | Default |
| 8 | **180.00** | 1.00 | 100.00 | 20.00 | HI | Default |
| 9 | **160.00** | 0.90 | 90.00 | 20.00 | HI | Default |
| 10 | **140.00** | 0.80 | 80.00 | 20.00 | HI | Default |
| 11 | **120.00** | 0.70 | 70.00 | 10.00 | HI | Default |
| 12 | **100.00** | 0.60 | 60.00 | 10.00 | HI | Default |
| 13 | **80.00** | 0.50 | 50.00 | 10.00 | HI | Default |
| 14 | **60.00** | 0.40 | 40.00 | 10.00 | MID | Default |
| 15 | **40.00** | 0.30 | 30.00 | 0.00 | MID | Default |
| 16 | **20.00** | 0.20 | 20.00 | 0.00 | MID | Default |

---

## 📁 Repository Structure

```
├── run_gui.bat                 # 1-Click Desktop Launcher
├── cryocon_gui.py              # Main Interactive Lab GUI Application
├── smart_ramp_cli.py           # Headless Automated Two-Speed Ramping CLI Tool
├── cryocon_controller.py       # Object-Oriented Python Driver Class for Cryocon 22C
├── write_pid_table02.py        # Dedicated script to program & verify PID Table 02
├── read_full_table.py          # Utility script to inspect table contents
├── pid_controller.py           # Interactive PID console utility
├── quick_test.py               # 10-second rapid sensor read test
├── read_temperature.py         # Simple continuous temperature reader
├── README.md                   # This comprehensive manual
└── Cryocon_32_Temperature_Controller.pdf # Cryocon SCPI Reference Manual
```

---

## 📊 CSV Data Logging Format

Data files are automatically generated with standard laboratory columns:

| Column | Description | Example |
|---|---|---|
| `Timestamp` | Date and Time | `2026-08-24 16:45:10` |
| `Elapsed_Sec` | Time since logging started | `210.5` |
| `Temp_A_K` | Sample temperature | `310.0042` |
| `Temp_B_K` | Secondary channel | `0.0000` |
| `Setpoint_K` | Active target setpoint | `310.0000` |
| `Error_K` | Difference ($T_A - T_{sp}$) | `+0.0042` |
| `Heater_Pct` | Heater output power % | `8.45` |
| `Ramp_Rate_K_min` | Active ramp rate | `0.50` |
| `Active_PID_Table` | PID table in use (1 or 2) | `2` |
| `Control_State` | `ON` or `OFF` | `ON` |
| `P_Gain` / `I_Gain` / `D_Gain` | Active PID coefficients | `1.60 / 160.0 / 40.0` |

---

## 🔧 Essential Hardware & SCPI Guidelines

### 1. Serial Port Connection Parameters
* **Port**: `COM5` (FTDI USB Serial)
* **Baud Rate**: `9600`
* **Data Bits**: `8`
* **Parity**: `None`
* **Stop Bits**: `1`
* **Line Termination**: `\r\n` (CRLF)

### 2. Heater Range Selection Best Practices
* **For $T < 340\text{ K}$**: Use **`RANGE: MID`** or **`RANGE: LOW`**.
  * `MID` (5W max) / `LOW` (0.5W max) gives sub-milliwatt power resolution for tight $\pm 0.05\text{ K}$ stability near ambient temperatures.
* **For $T > 340\text{ K}$**: Use **`RANGE: HI`** (50W/75W max).
  * High power is needed to overcome significant radiative heat losses above 340 K.

### 3. Resolving COM Port Access Errors
If you see `PermissionError(13, 'Access is denied')`:
* Ensure **LabVIEW** or any other serial monitor (PuTTY, HTerm) holding COM5 is closed or its VISA session is stopped.
