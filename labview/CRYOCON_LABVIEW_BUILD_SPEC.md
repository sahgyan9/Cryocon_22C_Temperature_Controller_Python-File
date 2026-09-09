# Cryocon 22C ramp-control VI — build spec

Build target: **`CryoCon_RampControl.vi`**, a standalone LabVIEW program that does
what [`staged_ramp_test.py`](../staged_ramp_test.py) does — load the validated
tuning, ramp to a setpoint in the safe command order, monitor, and always send
`STOP` on the way out.

Everything below is grounded in the measured study in
[`FINAL_REPORT.md`](../FINAL_REPORT.md). The settings are from section 8, the
command order from section 9, and the ordering rationale from section 9's
"Why that order, specifically".

---

## 0. Read this first

Two facts drive the whole design.

**The command order is safety-critical.** `CONTROL` must be sent *before* the
target setpoint, and the setpoint must be sent *last*. Get it backwards and the
controller sees the entire temperature error the instant control engages; with
P = 40 a 10 K error demands 400 % power, so the heater pins at its limit. This
was observed on the real instrument — 70 % for 35 seconds, winding the
integrator to 60 % when 7 % was needed.

**`Loop_CONTROL.vi` engages both loops.** Its own front-panel note reads: "Sets
CONTROL mode, which will engage both control loops." Before first use, confirm
Loop 2 is off or harmless, or you will silently arm a second heater.

---

## 1. Driver VIs — verified connector panes

I opened these front panels and read the terminals directly. **Verified:**

| VI | Library | Inputs | Outputs |
|---|---|---|---|
| `CC_Initialize.vi` | `M54U.llb` | `VISA resource name` (default `COM5`) | `VISA resource name out`, `error out` |
| `CC_IO.vi` | `M54U.llb` | `Output Command` (string), `VISA In` | `Input String` (response) |
| `CC_WriteCmd.vi` | `M54U.llb` | `Output Command` (string), `VISA In` | `error out` |
| `CC_Close.vi` | `M54U.llb` | `VISA In` | `error out` |
| `Loop_CONTROL.vi` | `M54.llb` | `VISA In` only | — |
| `Loop_STOP.vi` | `M54.llb` | `VISA In` only | — |
| `Loop_Type.vi` | `M54.llb` | `Loop` (I32), `Loop Type` (enum), `VISA In` | `Return` (string) |
| `Loop_Set_PID.vi` | `M54.llb` | `Loop` (I32), `P`, `I`, `D`, `VISA In` | — |

**Inferred** from the identical pattern (`Loop`, one value, `VISA In`, `Return`)
— confirm each in Context Help as you drop it:

| VI | Sets |
|---|---|
| `Loop_Setpoint.vi` | `LOOP n:SETPT` |
| `Loop_RampRate.vi` | `LOOP n:RATE` |
| `Loop_MaximumPower.vi` | `LOOP n:MAXPWR` |
| `Loop1_Range.vi` | `LOOP 1:RANGE` |
| `Loop_Output_Power.vi` | `LOOP n:OUTP?` (query) |
| `Input_Read_Temp.vi` | `INPUT? A` |

### `Loop_Type.vi` enum — the mapping that matters

| Enum item | SCPI | Use it? |
|---|---|---|
| OFF | `OFF` | — |
| PID | `PID` | yes, transiently, to re-sync the ramp |
| Manual | `MAN` | no |
| Use PID Lookup Table | `TABLE` | **no** |
| **PID control with ramp** | **`RAMPP`** | **yes — this is the run mode** |
| PID lookup table with ramp | `RAMPT` | **no** |

The two lookup-table modes make the controller read gains from PID Table 2
instead of the ones you send. Table 2 has since been corrected (section 8b), but
`RAMPP` does not depend on it at all, so stay in `RAMPP`.

### Anything without a wrapper VI

`Loop1_Range.vi` covers `RANGE`. If any other raw command is needed, use
`CC_WriteCmd.vi` with the literal string — that is exactly what your existing
`All control Connected flat sequence.vi` already does.

---

## 2. Front panel

**Use these names exactly.** The test harness addresses controls by name through
the ActiveX VI Server, so a rename breaks the automated tests.

### Controls

| Name | Type | Default |
|---|---|---|
| `VISA Resource` | VISA resource name | `COM5` |
| `Target Setpoint (K)` | DBL | `300` |
| `Ramp Rate (K/min)` | DBL | `1.0` |
| `P Gain` | DBL | `40` |
| `I Time (s)` | DBL | `900` |
| `D Gain` | DBL | `0` |
| `Max Power (%)` | DBL | `70` |
| `Heater Range` | ring: LOW / MID / HI | `HI` |
| `Log File Path` | path | — |
| `GO TO SETPOINT` | boolean, latch when released | — |
| `STOP CONTROL` | boolean, latch when released | — |
| `EXIT` | boolean, latch when released | — |

Label `I Time (s)` exactly that. It is an **integral time in seconds, not a
gain** — the single unit error that caused the original +4.08 K overshoot.
Section 11 of the report is about this. Do not label it "I Gain".

### Indicators

| Name | Type |
|---|---|
| `Temperature (K)` | DBL |
| `Heater (%)` | DBL |
| `Working Setpoint (K)` | DBL |
| `Ramping?` | boolean LED |
| `Control State` | string (`ON` / `OFF`) |
| `Status` | string |
| `Trend` | waveform chart, 2 plots: temperature and heater % |
| `error out` | error cluster |

Set `Max Power (%)` to a coerced range of 0–70 and `Target Setpoint (K)` to
0–475. The instrument's Over Temperature Disconnect (Channel A, 470 K) is the
real backstop, but it is set by hand on the front panel and, per section 9, is
not remotely readable — so the panel limit is your only software guard.

---

## 3. Block diagram — state machine

A while loop containing a case structure on a `State` enum, with a shift
register carrying state, the VISA session, and the error cluster. Not a flat
sequence: the monitor state has to run repeatedly while remaining responsive to
`STOP CONTROL` and `EXIT`.

```
States: Init -> LoadTuning -> Idle -> ArmRamp -> Monitor -> StopControl -> Shutdown
                                ^                    |
                                +--------------------+
```

Put **200 ms** between every command (`Wait (ms)`). The controller drops
commands sent faster than it can process them.

### Init
1. `CC_Initialize.vi` ← `VISA Resource`. Session to shift register.
2. `CC_IO.vi` with `*IDN?`; show the reply in `Status`.
3. On error → `Shutdown`. Else → `LoadTuning`.

### LoadTuning — section 8 settings, once per session
1. `Loop1_Range.vi` ← `Heater Range`
2. `Loop_MaximumPower.vi` ← Loop 1, `Max Power (%)`
3. `Loop_Set_PID.vi` ← Loop 1, `P Gain`, `I Time (s)`, `D Gain`
4. `Loop_RampRate.vi` ← Loop 1, `Ramp Rate (K/min)`

Then read each back (`LOOP 1:PGAIN?` etc. via `CC_IO.vi`) and compare. If a
read-back disagrees, write it to `Status` and go to `Shutdown` rather than
ramping on unknown gains. → `Idle`.

### Idle
Poll `Input_Read_Temp.vi` and `Loop_Output_Power.vi` once per second, update the
indicators and chart. On `GO TO SETPOINT` → `ArmRamp`. On `EXIT` → `Shutdown`.

### ArmRamp — the safety-critical sequence

**This order is the whole point of the program. Do not reorder it.**

| # | Call | Why |
|---|---|---|
| 1 | `Input_Read_Temp.vi` → `T_now` | where we actually are |
| 2 | `Loop_Type.vi` ← `PID` | leave ramp mode so the next write lands instantly |
| 3 | `Loop_Setpoint.vi` ← `T_now` | park the working setpoint at the present temperature |
| 4 | `Loop_Type.vi` ← `PID control with ramp` | back into `RAMPP` |
| 5 | `Loop_CONTROL.vi` | **control ON — must precede the target** |
| 6 | `Loop_Setpoint.vi` ← `Target Setpoint (K)` | **last — writing this arms the ramp** |

Steps 2–4 re-synchronise the ramp to the current temperature. Without them the
ramp resumes from wherever the previous setpoint left it, which can be far from
where you are. → `Monitor`.

### Monitor
Once per second: `Input_Read_Temp.vi`, `Loop_Output_Power.vi`,
`CC_IO.vi` with `LOOP 1:RAMP?` (`YES`/`NO`) and `LOOP 1:SETPT?`. Update
indicators, chart, and append a row to the log. On `STOP CONTROL` →
`StopControl`. On `EXIT` → `Shutdown`. On error → `Shutdown`.

### StopControl
`Loop_STOP.vi`, confirm with `CONTROL?` via `CC_IO.vi` → `Idle`.

### Shutdown — must run on every exit path
1. `Loop_STOP.vi` — unconditionally, **even when arriving with an error**
2. `CONTROL?` read-back; if not `OFF`, retry `Loop_STOP.vi` once
3. `CC_Close.vi`
4. `Simple Error Handler` → `error out`

Wire `Loop_STOP.vi`'s error input from a **cleared** error wire (use `Clear
Errors`), or an upstream error will make the stop node no-op and leave the
heater running. This is the LabVIEW equivalent of the `try/finally` that
`staged_ramp_test.py` uses to send `STOP` on every exit path.

Also set **File » VI Properties » Execution » "Abort" disabled** so the red
abort button cannot skip `Shutdown`. `EXIT` becomes the only way out.

### Logging
Match the Python CSV so the existing analysis scripts work unchanged. Header
from `data/cryocon_log_*.csv`:

```
Timestamp,Elapsed_Sec,Temp_A_K,Temp_B_K,Setpoint_K,Error_K,Heater_Pct,
Ramp_Rate_K_min,Active_PID_Table,Control_State,P_Gain,I_Gain,D_Gain
```

Open the file once in `Init`, append in `Monitor`, close in `Shutdown`.

---

## 4. Testing without the instrument

`cryocon22c_sim.py` in this folder emulates the 22C over a TCP socket, so you
can build and test with nothing plugged in. Its thermal model was least-squares
fitted to 21,722 samples from the 26 runs in `data/`, and it reproduces the
report's measured power budget to about 1 W.

Start it:

```bash
python labview/cryocon22c_sim.py --speed 60
```

Then set `VISA Resource` to `TCPIP0::127.0.0.1::5025::SOCKET` instead of `COM5`.
`--speed 60` runs one simulated minute per real second, so a 30-minute ramp
takes 30 seconds.

The simulator implements the trap faithfully: a setpoint written while control
is OFF arms no ramp. `test_ordering.py` proves it — wrong order pins the heater
at 70 %, correct order holds it to 22 %.

```bash
python labview/test_ordering.py
```

Then drive the VI itself through both cases:

```bash
python labview/lv_harness.py --vi "D:/Labview/Cryo Con 2/CryoCon_RampControl.vi"
```

The harness talks to LabVIEW over the ActiveX VI Server — already working on
this machine, nothing to install. It sets the front-panel controls by name, runs
the VI, reads the indicators back, and checks the peak heater output against the
same thresholds `test_ordering.py` uses.

---

## 5. Going to the real instrument

1. Reconnect the controller and confirm the port. **COM5 was absent while this
   was written** — only COM3 and COM4 existed. Check NI MAX, and update `VISA
   Resource` if it enumerates differently.
2. Re-enter the Over Temperature Disconnect by hand (Channel A, 470 K) if the
   instrument has been reset. It is not remotely settable.
3. First real run: target **5 K above ambient**, watch that peak heater output
   stays under ~25 %. If it pins at `Max Power (%)`, the ordering is wrong —
   stop and recheck `ArmRamp`.

### Worth testing on hardware

The driver exposes **OTD Enable**, **OTD Source** and **OverT Setpt** VIs under
"Cryostat Protection" in `Icon_Tree.vi`. That contradicts section 9's note that
Over Temperature Disconnect is not remotely settable. These are Model 54 VIs and
the 22C may simply reject the commands — but if they work, the OTD could be set
and verified in software instead of by hand, which closes a real safety gap.
Test with a query first, and only against a harmless value.

---

## 6. Open item inherited from the study

The **77–300 K zone is still untuned**. These settings are validated for
300–475 K with no active cooling. Once LN₂ arrives, that zone needs its own
campaign; do not assume these gains carry over.
