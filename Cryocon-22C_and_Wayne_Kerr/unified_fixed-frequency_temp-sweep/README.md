# Fixed 10 kHz Continuous Temperature Sweep & Cooling Spectroscopy Suite
## Wayne Kerr 6510B Precision Impedance Analyzer & Cryo-con 22C Temperature Controller

**Subfolder:** `unified_fixed-frequency_temp-sweep`  
**Sample Target:** PMN-0.3PT ($0.70\text{Pb}(\text{Mg}_{1/3}\text{Nb}_{2/3})\text{O}_3 - 0.30\text{PbTiO}_3$) Relaxor Ferroelectric  
**Date Created:** 2026-09-11  

---

## 1. Objective & Operational Profile
This suite is designed for continuous, high-thermal-resolution dielectric and impedance spectroscopy at a **fixed frequency of 10.0 kHz (10,000 Hz)** during controlled cooling:
- **Starting Temperature:** Current sample temperature (~422 K)
- **Target Temperature:** 300.0 K
- **Cooling Rate:** 0.50 K/min (linear controlled ramp)
- **Estimated Run Time:** $\approx 244\text{ minutes}$ (~4 hours 4 minutes)
- **Impedance Mode:** Wayne Kerr 6510B measuring $R\ (\Omega)$ and $X\ (\Omega)$ in Series equivalent circuit (`SER`) at 100 mV RMS AC excitation.
- **Continuous Logging Schema:**
  - Table: `T (K) | f (Fixed) | R (ohm) | X (ohm)` (plus Time, $C_p$, $\tan\delta$, $\varepsilon'$)
  - Disk File: `Data/Cooling_10kHz_<T_start>K_to_<T_target>K_10kHz_100mV_<timestamp>.dat`

---

## 2. File Organization
```
Cryocon-22C_and_Wayne_Kerr/unified_fixed-frequency_temp-sweep/
├── cooling_gui.py            # Primary Desktop GUI with live table and multi-tab plots
├── cooling_runner.py         # Headless orchestrator and streaming data engine
├── cryocon_controller.py     # Cryo-con 22C serial driver (COM5, 57600 baud)
├── wayne_kerr_controller.py  # Wayne Kerr 6510B VISA driver (GPIB0::6::INSTR)
├── run_gui.bat               # One-click Windows batch launcher
├── verify_cooling_gui.py     # Automated mock verification suite
└── README.md                 # This operational reference
```

---

## 3. How to Launch & Run

### Step 1: Release Hardware from Unified GUI
If `unified_gui.py` is currently running, close it or click **Disconnect Hardware**. Windows only allows one process to hold serial port `COM5`.

### Step 2: Start the Cooling GUI
Double-click `run_gui.bat` or run:
```cmd
python cooling_gui.py
```

### Step 3: Connect Hardware
1. Confirm Cryocon Port is `COM5` (Baud `57600`) and Wayne Kerr VISA is `GPIB0::6::INSTR`.
2. Click **Connect Hardware**.
3. Live temperature will display in the `STAGE TEMP (T)` digital readout (confirming ~422 K).

### Step 4: Verify Parameters
- **Target Temp**: `300.0 K`
- **Cooling Rate**: `0.50 K/min`
- **PID Defaults**: `P=70.0`, `I=900.0 s`, `D=0.0`
- **Heater Authority**: Range `HI`, Max Power `100.0%`
- **Fixed Frequency**: `10,000.0 Hz`
- **Drive Level**: `100.0 mV RMS`

### Step 5: Start Experiment
Click **▶ START COOLING EXPERIMENT**.
- The Cryo-con 22C will safely park the working setpoint at the current temperature in `PID` mode, engage `CONTROL`, switch to `RAMPP` mode, and set the target setpoint to `300.0 K`.
- The live table on Tab 1 will populate row-by-row with `T (K) | f (Fixed) | R (ohm) | X (ohm)`.
- Plots on Tabs 2–5 will update live with unbuffered disk logging to `Data/`.

---

## 4. Emergency & Safety Controls
- **Emergency Stop Button**: Clicking the red `⚠ EMERGENCY STOP` button instantly dispatches `STOP` to the Cryo-con 22C, cutting heater power to 0%.
- **Exit Failsafe**: Closing the window or clicking **Abort** guarantees `STOP` is sent to disengage active heating.
