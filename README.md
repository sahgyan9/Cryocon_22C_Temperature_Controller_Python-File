# Cryocon 22C — Janis ST-LN-500 Probe Station Control

Temperature control for a Janis Research ST-LN-500_1-4CX LN₂ cryogenic probe
station via a Cryo-con 22C controller on COM5.

**Start here: [`FINAL_REPORT.html`](FINAL_REPORT.html)** — the overshoot study,
the settings that fixed it, and the LabVIEW SCPI sequence. Open it in a browser;
it is self-contained and prints cleanly.

## Current tuning (validated 2026-09-05)

```
LOOP 1:PGAIN   40        proportional gain
LOOP 1:IGAIN   900       integral time, SECONDS (not a gain)
LOOP 1:DGAIN   0         derivative off
LOOP 1:RANGE   HI        50 W full scale
LOOP 1:MAXPWR  70        percent
LOOP 1:RATE    1.0       K/min (2.0 works equally well and is twice as fast)
LOOP 1:TYPE    RAMPP
```

Peak overshoot **+0.22 K**, down from +4.08 K. PID Table 2 in the instrument's
memory now carries these Zone 1 values as well, so `RAMPT`/`TABLE` mode is safe
above 300 K.

## Ordering rule that matters

Send `CONTROL` **before** the target setpoint, and send the setpoint **last** —
writing the setpoint is what arms the ramp. Setting a target while control is OFF
makes the heater slam to its power limit the moment control is switched on.

## Serial Interface & Communication Speed

- **Port:** `COM5` (or assigned USB-serial COM port)
- **Baud Rate:** `57,600` (8 Data Bits, 1 Stop Bit, No Parity, `\r\n` Line Termination)
- **Hardware Upgrade Note:** Upgraded from the factory 9,600 baud to **57,600 baud** on the instrument front panel (`System -> Remote -> RS-232 Rate: 57600`).
- **Telemetry Throughput & ADC Limits:**
  - The Cryo-con 22C has a fixed 24-bit delta-sigma ADC running at **10 Hz (100 ms)**.
  - At 57,600 baud, single SCPI query roundtrips take ~25–30 ms (down from ~120 ms at 9600).
  - The Python GUI (`cryocon_gui.py`) features an **Ultra (0.10 s / 10 Hz)** polling option that streams stage temperature, heater output, and setpoints at the full hardware ADC limit with zero lag.

## Layout

| Path | Contents |
|---|---|
| `FINAL_REPORT.html` / `.md` | The report |
| `OVERSHOOT_TUNING_LOG.md` | Full technical log — every attempt, superseded theories, safety config |
| `data/` | 26 measured runs + the PID table backup taken before overwriting |
| `figures/` | Report figures (regenerate with `make_final_figures.py`) |
| `docs/` | Cryocon manual, project objective, dev notes |
| `labview/` | LabVIEW port — build spec, 22C simulator, ActiveX test harness |
| `archive/` | Superseded scripts and the earlier report's generators |
| `data_backup_20260904/` | Independent backup taken mid-study |
| `Cryocon-22C_and_Wayne_Kerr/` | Unified suite: Wayne Kerr 6510B Impedance Analyzer + Cryo-con 22C |

## Integrated Suite: Wayne Kerr 6510B & Cryo-con 22C (PMN-0.3PT Characterization)

The folder [`Cryocon-22C_and_Wayne_Kerr/`](Cryocon-22C_and_Wayne_Kerr/) contains the unified impedance spectroscopy software used for characterizing **PMN-0.3PT** ($0.70\text{Pb}(\text{Mg}_{1/3}\text{Nb}_{2/3})\text{O}_3 - 0.30\text{PbTiO}_3$):
- **`unified_gui.py`**: Unified GUI orchestrating simultaneous temperature ramps and multi-frequency dielectric impedance sweeps with live $\varepsilon'(T)$ visualization.
- **Latest Data**: Subfolder [`Cryocon-22C_and_Wayne_Kerr/Data/`](Cryocon-22C_and_Wayne_Kerr/Data/) contains the latest 57-point dataset (300 K to 412 K) for PMN-0.3PT.
- **Launcher**: Run `Cryocon-22C_and_Wayne_Kerr\run_gui.bat` or `python Cryocon-22C_and_Wayne_Kerr/unified_gui.py`.
- **Documentation**: See [`Cryocon-22C_and_Wayne_Kerr/README.md`](Cryocon-22C_and_Wayne_Kerr/README.md) and [`LEARNING_LOG.md`](Cryocon-22C_and_Wayne_Kerr/LEARNING_LOG.md) for full physical and operational details.

## Scripts

| Script | Purpose |
|---|---|
| `staged_ramp_test.py` | Ramp runner for tests. **Sends `STOP` on every exit path** — use this for anything unattended. |
| `live_view.py` | Live temperature/heater display. Tails the log file, so it does not occupy COM5 while a test runs. |
| `write_pid_table02.py` | Writes PID Table 2 to instrument NVRAM. Backs nothing up itself — take a copy first. |
| `make_final_figures.py` | Regenerates every report figure from `data/`. |
| `read_full_table.py` | Dumps the PID tables currently in the instrument. |
| `monitor_only.py` | Read-only monitor. |
| `cryocon_gui.py` | GUI (`run_gui.bat`). |

Only one process can hold COM5. Close the GUI and stop any running test before
starting another.

## Open items

- **77–300 K zone is untuned.** Its table values are likely wrong for the same
  units reason as Zone 1, but LN₂ changes the dynamics and there is no data yet.
  LN₂ is on order — retune once it arrives.
- **Over Temperature Disconnect** (Channel A, 470 K) is set by hand on the front
  panel and is **not** remotely settable or readable. Re-enter it manually if the
  instrument is ever reset. (Updated from 460 K).
