# Handoff prompt for Antigravity

Copy everything below the line into Antigravity as your opening message.

---

You are picking up a lab instrumentation project mid-stream. Work in
`C:\Users\sahgy\Downloads\Cryocon_22C_Temperature_Controller_Python-File`.

## Background

We control a **Janis ST-LN-500_1-4CX** LN2 cryogenic probe station with a
**Cryo-con 22C** temperature controller (serial 206687, firmware 3.33G) over
**COM5, 9600 baud, 8N1, `\r\n`** line endings. The eventual production driver is
LabVIEW, which can only set a single setpoint, a single ramp rate, and PID gains
— so any fix must live in the controller's own settings, not in a Python script
that babysits the ramp.

The goal is to reach a target temperature (ultimately 450 K) and **settle there
without overshooting**, because above 300 K this station has **no active
cooling** — if it overshoots, the only way back down is passive cooling at about
0.25 K/min, which strands the experiment for a long time.

**The overshoot problem has already been solved.** Do not re-open it. Overshoot
went from +2.3 K to 0.00 K. Read `OVERSHOOT_TUNING_LOG.md` in full before
touching anything — especially the section "ROOT CAUSE ANALYSIS AND FIX", and
section 9 "SUPERSEDED", which lists theories the data disproved. Several earlier
sessions lost hours re-deriving or re-testing those. Do not repeat them.

## The five facts that matter (already proven, do not re-litigate)

1. **`IGAIN` is integral time in SECONDS**, not a gain (manual line 5440).
   Lower I = faster, more windup-prone integrator. Earlier sessions kept
   lowering it (160 → 30.4 → 18) believing they were reducing windup; they were
   making it worse. Correct value is **900**.
2. **There is no "heat soak."** After the heater truly reaches 0%, temperature
   rises only a further 0.001–0.046 K. The README's "two-speed ramp" rationale
   is based on a mechanism that does not exist here.
3. **Overshoot was integral windup during actuator saturation.** Overshoot area
   equals windup area. That one sentence explains every run in the log.
4. **Working gains: `P=25  I=900  D=0`, Range HI, MAXPWR 50–70, rate 1.0 K/min,
   `LOOP 1:TYPE RAMPP`.** Verified twice on hardware with zero overshoot
   (352 K and 357 K runs).
5. **Identified plant model** (use these, don't re-derive):
   heat capacity **C ≈ 520 J/K**; dead time **θ ≈ 20 s**;
   heat loss **≈ 0.0754·(T−297) − 0.98 W**; HI range full scale = 50 W at 50 Ω.
   P-only stability limit is P ≈ 82, so P=25 sits at ~62° phase margin.
   **Never set P above ~50.**

## Current hardware state (as of the handoff)

- Temperature **375.25 K**, cooling passively.
- **`CONTROL` is OFF and heater output is 0%** — verified. The station is safe
  and idle.
- Gains left on the controller: P=25, I=900, D=0, Range HI, MAXPWR 70,
  setpoint 375, TYPE RAMPP.
- **Over Temperature Disconnect is ENABLED, source Channel A, trip 460 K.** It
  was set by hand on the front panel. It is NOT remotely settable (every SCPI
  variant returns `NAK`) — you cannot read it back, set it, or restore it. If it
  is ever lost it must be re-entered manually via the **Sys** key.
- Channel B reads a sensor fault (`.......`). Only Channel A is usable.

## TASK A — Build the report (do this first; needs no hardware)

Produce a report **in simple, plain English aimed at a physicist who is not a
control-systems engineer**. No jargon without explaining it. Explain *why*
things happened, not just what the numbers are.

Write it to **`TUNING_REPORT.md`** with embedded PNG figures, and also produce a
single self-contained **`TUNING_REPORT.html`** version.

There are **16 CSV logs** named `cryocon_log_*.csv`. Every one is real measured
data — do not fabricate, interpolate, or "clean" any of it. A backup copy is in
`data_backup_20260904/`; if you ever doubt a file, compare against that. Never
overwrite or delete a CSV.

Two CSV schemas exist — handle both:
- Older: `Timestamp, Elapsed_Sec, Temp_A_K, Setpoint_K, Error_K, Heater_Pct, Ramp_Rate_K_min, P_Gain, I_Gain, D_Gain, Range, MaxPwr_Pct, Stage`
- Newer adds `Ramp_SP_K, Track_Err_K` after `Error_K`
- The staged log (`*_staged.csv`) instead has `Stage_Idx, Stage_Target_K, ..., Phase`
- The oldest file (`164857`) lacks `Range` and `MaxPwr_Pct` entirely — use
  `dict.get()` with defaults, do not assume columns exist.

### Figures to produce

1. **Before/after overshoot.** Temperature minus setpoint vs. time, all runs on
   one axis, old gains dashed/warm colours, new gains solid/cool. Shade the
   ±0.2 K target band. `make_overshoot_figure.py` already does this — extend it
   rather than starting over.
2. **Heater output vs. time** for the same runs. This is where the mechanism is
   visible: the old gains hold ~29% power *while already above setpoint*; the
   new ones taper to the hold value before arrival. Call that out in the caption.
3. **Peak overshoot by configuration** — a horizontal bar chart, one bar per
   run, labelled with its P/I/D/cap. Makes the +4.08 → 0.00 K story obvious.
4. **The "coast" evidence** — for each old run, a small chart comparing total
   overshoot against how far temperature rose *after* the heater hit 0%. This is
   the proof that "heat soak" was not the cause. The second number is ~0.01 K
   in every case.
5. **Heat loss vs. temperature**, derived from the passive-decay tails of every
   log, with the fitted line and the extrapolation to 450 K. Annotate that
   holding 450 K needs ~21% of HI and a 1 K/min ramp there needs ~39% — which is
   why the old MAXPWR=30% cap could never have worked at the target.
6. **Overshoot vs. setpoint jump size**, if/when staged data exists (Task B).

Every figure needs a one-sentence plain-English caption saying what to look at.

### Numbers the report must contain

A results table of every run: setpoint, P, I, D, MAXPWR, ramp rate, peak
overshoot, final error. Compute these from the CSVs, do not copy them from prose.
Key results to verify independently: old gains gave +4.08 K (327 K run), +2.30 K
(340 K), +2.06 K (345 K); new gains gave −0.140 K peak (352 K, P=40 I=0) and
−0.036 K peak (357 K, P=25 I=900) — negative peak meaning it *never crossed the
setpoint at all*.

**Caveat you must state explicitly:** the staged run `224006_staged.csv` shows
+0.288 K on its first stage (375 K). That number is **contaminated** and must not
be presented as a clean result. It inherited a pre-loaded integrator because the
preceding 450 K ramp was killed mid-flight, so the controller began that stage
already commanding ~24% power when only ~10% was needed to hold 375 K. Say so
plainly in the report.

## TASK B — Finish the staged campaign (hardware; only when someone is present)

**Ask the user for explicit go-ahead before energising the heater.** Do not start
a hardware run on your own initiative.

The plan is to confirm the gains hold as the setpoint jump grows, walking
**375 → 385 → 390 → 405 → 420 → 450 K** with one fixed gain set and one flat
ramp rate, so jump size is the only variable. Use the existing script:

```bash
python staged_ramp_test.py --targets 385,390,405,420,450 --rate 1.0 --p 25 --i 900 --d 0 --range HI --maxpwr 70 --band 0.10 --hold 3 --stagepad 25 --maxover 3 --maxtemp 460 --holdhours 0.5
```

Adjust the first target to whatever the station has cooled to. Expect roughly
+0.3 to +0.6 K on the 30 K jump to 450 K, converging to near-zero error
afterwards; the model predicts overshoot grows with jump size but stays under
1 K. Anything much larger means something is unmodelled — stop and investigate
rather than continuing to climb.

**`staged_ramp_test.py` is the only script safe for unattended use.** It sends
`STOP` on every exit path. **`pid_tune_test.py` does NOT** — if that process is
killed mid-ramp the controller keeps heating to its last setpoint. This actually
happened during the previous session.

## Hard rules — these have each cost a previous session real time

- **Check `Cryocon_32_manual.md` before assuming a command doesn't exist or
  guessing syntax.** A `PMAX?` vs `MAXPWR?` mixup burned an entire session.
  The manual is for the Model 32; the 22C is a simpler sibling, so verify with a
  live `?` query.
- **Only one process can hold COM5.** Everything else gets
  `PermissionError(13)`. Close the GUI and stop any running script first. After
  killing a process, wait and retry the port with a loop — Windows takes a few
  seconds to release it.
- **Use plain `python`** (3.14.3, has pyserial + matplotlib). `DEV_NOTES.md`
  tells you to use an Anaconda path — **that is wrong on this machine**, the
  path does not exist.
- **Setting a new setpoint does NOT start the ramp from the current
  temperature.** It resumes from wherever the internal working setpoint was left.
  To resync you must first send `LOOP 1:TYPE PID` (which makes the setpoint jump
  instantly), then set the setpoint, then switch back to `RAMPP`. Writing the
  setpoint while still in RAMPP mode makes the *resync itself* ramp slowly —
  this bug left the heater at 0% for the first 90 s of a run.
- **In `RAMPT`/`Table` mode the controller ignores `PGAIN`/`IGAIN`/`DGAIN`** and
  looks gains up from PID Table 02 instead. Writing gains in that mode silently
  does nothing. All validated results used `RAMPP`.
- **PID Table 02 in the instrument's NVRAM still holds the BAD tuning**
  (P≈2, I=30–45, D=52–70 in the 300–475 K zone). It has not been rewritten.
  Do not switch to Table/RAMPT mode expecting good behaviour.
- **Never set MAXPWR to 30%** — it cannot sustain a 1 K/min ramp at 450 K and
  causes the saturation that drives windup. 50–70 is right.
- **Never use MID or LOW heater range above ~330 K.** MID (5 W full scale) was
  tested and could not track at all; LOW is 0.5 W.
- Append every hardware attempt to the Attempt Log in `OVERSHOOT_TUNING_LOG.md`
  with actual measured data, not a plan.

## Also worth fixing (lower priority)

- `README.md` explains overshoot via heat "soaking into the sample", which the
  data disproves, and its PID Table listing is stale. Correct both.
- `write_pid_table02.py` contains the comment *"I = 30–45 → ~5× lower than
  original. Prevents integrator windup"* — that reasoning is backwards. If the
  table is ever rewritten for a LabVIEW/Table-mode deployment, the 300–475 K
  zone should use P=25, I=900, D=0. Leave the 77–300 K zone alone; there is no
  data at cryogenic temperatures and LN2 cooling changes the dynamics.
- The LabVIEW VI has no control for `LOOP 1:TYPE` or `LOOP 1:MAXPWR`, and its
  panel defaults are P=1.00, I=5.00, D=0.00 — close to factory defaults and much
  worse than the tuned values. Its "Set Resistor Value" button is wired to a
  Range dropdown, so confirm it sends `LOOP 1:RANGE` and not `LOOP 1:LOAD`
  (load must stay 50 Ω or all power readings become wrong).

## Key files

| File | What it is |
|---|---|
| `OVERSHOOT_TUNING_LOG.md` | **Read first.** Full diagnosis, all attempts, superseded theories, safety config |
| `cryocon_log_*.csv` | 16 measured runs — the raw data for the report |
| `data_backup_20260904/` | Backup copy of every log, doc and script |
| `staged_ramp_test.py` | Safe unattended staged-ramp runner (sends STOP on all exits) |
| `pid_tune_test.py` | Single-setpoint tuning harness (NOT safe unattended) |
| `make_overshoot_figure.py` | Existing before/after plot; extend for the report |
| `Cryocon_32_manual.md` | SCPI reference (Model 32; 22C is a simpler sibling) |
| `role_Context_and_objective.md` | The LabVIEW deployment target |

Start with Task A. Ask before running hardware.
