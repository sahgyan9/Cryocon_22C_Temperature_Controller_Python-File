# Temperature Overshoot Diagnosis & Tuning Log

Living document for the effort to reach 450 K on the Janis probe station without
overshoot, so measurements can start exactly at the target setpoint. Every AI
agent that works on this problem should read this file first, and append a new
entry to the **Attempt Log** at the bottom before finishing a session.

**Before guessing at SCPI command syntax, valid ranges, or controller behavior,
check `Cryocon_32_manual.md` first** (and cross-reference with live `?` queries
where the 22C might differ from the Model 32 it documents). The `PMAX?` vs
`MAXPWR?` mixup earlier in this log cost a whole session of "unresolved" status
on something the manual answered directly once someone actually reread it —
don't assume a command doesn't exist or guess its syntax when the manual is
sitting right there.

> ### READ THIS FIRST - root cause was found on 2026-09-04 (evening session)
> Overshoot is **solved**: +2.3 K -> **0.00 K** on a 5 K hop, verified twice on
> hardware. The cause was the PID gains, and every earlier session in this file
> was tuning them **in the wrong direction**. Two specific corrections:
>
> 1. **`IGAIN` is integral time in SECONDS** (manual line 5440), not a "gain".
>    *Lower* I = *faster*, *more* windup-prone integrator. Sessions above went
>    160 -> 30.4 -> 18 believing they were reducing windup; they were multiplying
>    it. Thermal loops want 60-300 s or more.
> 2. **There is no "heat soak" / stored-energy lag.** Measured directly: after
>    the heater actually reaches 0%, temperature rises a further
>    **0.001-0.046 K**. The overshoot is entirely "heater is still on at ~29%
>    while already above setpoint", not heat arriving late.
>
> **Working gains: `P=25  I=900  D=0`, Range HI, MAXPWR 50-70.**
> Sections marked *SUPERSEDED* at the bottom of this file record theories that
> the data disproved - they are kept for history, do not act on them.

## Equipment

- **Probe station:** Janis Research Company, Model **ST-LN-500_1-4CX** (LN2 cryogenic probe station)
- **Controller:** Cryo-con 22C, serial 206687, firmware 3.33G (confirmed via `*IDN?` on 2026-09-04)
- **Connection:** COM5, 9600 baud, 8N1, `\r\n` termination
- **Python:** default `python` on this machine (3.14.3) has `pyserial` 3.5 and `matplotlib` installed and works fine — the old `DEV_NOTES.md` instruction to use `C:\Users\SRMAP\anaconda3\python.exe` does not apply on this machine (that path doesn't exist here); this appears to be a different PC than where DEV_NOTES.md was written.

## Original Request (2026-09-04)

> we are in lab. We are using this product and want to reach the temperature target of 450 degree. Our goal is to take measurement once the set temperature is reached. But right now I am setting the temperature but its overshooting (you can see from the recent log of csv file where the set point was 305 but it reached to 308 before the heater turned off). This is giving us pain of not being able to control temperature at our desired point to do the measurement. I want you to diagnize, see different possiblity, run the equipment store the value and check if its working or not till you meet the goal.
>
> I also want the prompt to be save in md file so that ai agents has reference to how things have moved on with the prompt and AI agents solutions both documented

## Evidence Examined

1. **`cryocon_log_20260904_164857.csv`** (173 rows, run starting 16:48:58) — ramp from 297.27 K to setpoint 305 K.
2. **Live read-only status query** (2026-09-04, right after reading the CSV) — confirmed the device was still sitting in the overshot state from that exact log:
   ```
   IDN: Cryo-con,22C,206687,3.33G
   Temp A: 307.343600      Setpoint: 305.000000K      Control: ON
   Heater Output: 0.000000  Heater Range: HI           Ramp Rate: 2.000000
   Active Table: 2          P: 2.02   I: 30.4   D: 52.6
   Max Power query -> "NAK" (LOOP 1:PMAX? not accepted by this firmware/loop — needs correct syntax, unresolved)
   Loop 1 Type: RAMPT
   ```
3. **`Cryocon_32_manual.md`** (SCPI reference; Model 32, closest available manual — 22C shares the SCPI command set but is an older/simpler model, so not everything in it is guaranteed to apply, e.g. `AUTOTUNE` support on the 22C is unconfirmed).

## Diagnosis

### Root cause 1 — No active cooling above 300 K (Zone 1)
Per `DEV_NOTES.md`, Zone 1 (300–475 K) has no LN2 cooling — only the heater. Once
temperature overshoots the setpoint, the **only** path back down is passive
radiative/conductive loss to ambient. The CSV tail (elapsed 271 s → 333 s) shows
the temperature falling only ~0.13 K per 60 s once the heater is at 0%. **Overshoot
above 300 K is effectively permanent on any useful timescale** — it does not
self-correct. This is the single biggest risk for a 450 K target: any overshoot up
there will strand the experiment far from setpoint for a long time.

### Root cause 2 — Flat-rate ramp with no gentle final approach was actually used
`Ramp_Rate_K_min` in the CSV is constant at 2.00 for the *entire* approach, and the
live query confirms `LOOP 1:TYPE = RAMPT` (firmware ramp-to-setpoint at one fixed
rate). The README's "Smart Two-Speed Ramp" (fast far away, 0.5 K/min within 15 K of
target) is a **software feature** implemented in `smart_ramp_cli.py` / the GUI's
ramp button — the Cryocon firmware's native RAMPT mode does not do this on its own.
This run held 2 K/min the whole way, so heater output was still ~49% at only 0.6 K
from setpoint. Heater didn't reach 0% until 305.76 K (elapsed 168 s); stored heat in
the probe station's metal stage kept soaking in afterward, carrying the sample up to
a peak of 308.28 K — a **+3.28 K overshoot**, ~46% of the way from setpoint to the
15 K "switch delta" band.

**Conclusion: the "zero overshoot" ramp engine described in the README exists in
code but was not the thing actually driving this run.** Whatever set the 305 K
point (GUI direct entry, or a script bypassing the two-speed logic) just changed
`LOOP 1:SETPT` with the ramp rate already parked at 2.0 K/min.

### Root cause 3 — README.md's PID Table 02 values are stale
Live query at 305 K: P=2.02, I=30.4, D=52.6. README.md's documented Table 02 claims
I≈160 at 300 K — off by ~5x. The live values instead match `DEV_NOTES.md`'s "last
written 2026-08-24" note (Zone 1: I=30–45, D=52–70). **README.md was not updated
after the table was last reprogrammed.** Any agent tuning PID off the README table
would be tuning against numbers that no longer exist on the hardware.

### Root cause 4 — Heater Range is HI at 305 K
README's own guidance recommends MID/LOW below 340 K for finer heater power
resolution and tighter (±0.05 K) stability; HI is currently active at 305 K, which
is coarser and plausibly contributes to the overshoot burst.

### Open / unresolved
- `LOOP 1:PMAX?` returned `NAK` — either wrong command syntax for the 22C, or the
  22C doesn't expose a power-limit query the way the Model 32 manual describes.
  Needs the correct 22C command (check with `*IDN?`-scoped docs or trial commands)
  before max-power capping can be used as a mitigation.
- Whether the 22C firmware supports `AUTOTUNE:*` commands at all is unconfirmed —
  the manual in this repo is for the Model 32, a related but different product.

## Proposed Fix Plan (staged, most reversible first)

1. **Always drive setpoint changes through the two-speed software ramp**
   (`smart_ramp_cli.py` or the GUI's Smart Ramp), never a raw `LOOP 1:SETPT` with a
   fast rate already configured. This is the fix already built for this exact
   problem — it just wasn't what generated the log in question.
2. **Slow the final-approach rate further** — try `--slow 0.2` (or lower) instead
   of the default 0.5 K/min, since with zero active cooling above 300 K the PID
   loop needs more lead time to bring heater output to 0% *before* crossing
   setpoint, not just as it crosses.
3. **Switch to MID range below 340 K** for finer power resolution near setpoint,
   matching the README's own guidance (currently not followed).
4. **Verify Table 02 in the field vs. documentation**, and update README.md's
   table once confirmed, so it stays a trustworthy reference.
5. **Approach 450 K in verified stages**, not one long ramp: prove near-zero
   overshoot at an intermediate setpoint first, then repeat at progressively
   higher setpoints, logging each attempt below, before committing to 450 K
   unattended.
6. Only if 1–4 are insufficient: investigate `AUTOTUNE` (if supported) or manual
   D/I retuning of Table 02's zone rows — deferred because these apply heater
   power directly and should only be done deliberately, ideally with an Over
   Temperature Disconnect configured first for safety.

## Clarification from user (2026-09-04, after diagnosis was presented)

> The goal is the reach the desired set point just by ramping and not two speed
> ramp because that will not be feasible with labview later. I think we can
> iterate to adjust the value of PID to make it work. I have see the heating
> solider where I just rotate the knob and it reached the exact temperature and
> holds it. I wish it is also implemented here

This rules out the software two-speed ramp (`smart_ramp_cli.py`) as the
long-term fix, since the real deployment target is LabVIEW driving the
controller directly (see `role_Context_and_objective.md`), which will only set
a single setpoint + single ramp rate + PID gains — not run an external Python
script that dynamically rewrites the rate mid-ramp. **The fix has to live in
the PID gains / control mode on the controller itself**, so that a plain single
flat-rate ramp settles cleanly on its own, the way a well-tuned soldering-iron
controller does.

**Also confirmed by user mid-session:** the equipment is a **Janis Research
Company probe station, Model ST-LN-500_1-4CX**, LN2-cooled — consistent with
DEV_NOTES.md's "no active cooling above 300 K" (LN2 only cools the low end of
the range).

### Tuning approach going forward
`LOOP 1:TYPE RAMPT` (the firmware's default) uses **Table 02's interpolated**
PID values, which can't be freely overridden per-test since the table
recalculates them by setpoint. To iterate on raw P/I/D directly, tests below
use `LOOP 1:TYPE RAMPP` — "ramp using the loop's *current* PID gains, not a
table lookup" (see manual §LOOP:TYPE and §Temperature Ramping) — so gains set
via `LOOP 1:PGAIN/IGAIN/DGAIN` take effect directly. Once a good zone-1 gain
set is found, it should be written back into Table 02 (`write_pid_table02.py`)
so the eventual LabVIEW/Table-mode deployment inherits it.

## Attempt Log

| Date | Setpoint | Rate/Range/Table used | Peak overshoot | Time to settle | Notes |
|------|----------|------------------------|-----------------|-----------------|-------|
| 2026-09-04 | 305 K | RAMPT firmware, flat 2.0 K/min, Range HI, Table 2 (P=2.02 I=30.4 D=52.6) | +3.28 K (308.28 K) | Not settled — still +2.5 K after 5+ min at heater 0% | Baseline run analyzed above. Confirmed live: device still stuck at 307.34 K. |
| 2026-09-04 | 315 K | RAMPP (manual gains), flat 2.0 K/min, Range HI, P=2.02 I=30.4 **D=70** (raised from 52.6, I left unchanged) | **+4.6 K or more** (peaked ≥319.6 K; forced STOP mid-decay as a safety cap since it was climbing well past the 305 K baseline's overshoot with no active cooling to recover it) | Not settled — was still actively falling in heater% (21.5%→2.5%) when stopped, hadn't reached 0.2K band | **Worse than baseline.** Raising D alone, without lowering I, backfired. Root-cause hypothesis: `LOOP 1:SETPT` had last been 305 K (settled) before this test; switching to a new target does *not* start the internal ramp from the live reading — it resumes the internal moving-setpoint ramp from wherever it last was (305 K), which was already *below* the actual live temperature (306.7 K) at the time. That made the effective ramp run roughly 2x longer than the 305 K baseline (~355s vs ~152s) before the moving target caught up to/passed the real target, giving the (unchanged) I=30.4 term roughly 2x longer to accumulate integral windup — which is the exact failure mode `write_pid_table02.py`'s own comments warn about ("I=30-45, 5x lower than original, prevents integrator windup during 2K/min ramps"). **Lesson: before commanding a new setpoint for a clean test, must confirm the previous setpoint has fully settled AND resync/verify the internal ramp state — otherwise elapsed-time-based comparisons between runs are not apples-to-apples**, and this also matters for the eventual LabVIEW workflow (don't fire a new setpoint while the prior one hasn't settled). |
| 2026-09-04 | 327 K | RAMPP (manual gains) with setpoint-resync fix applied, flat 2.0 K/min, Range HI, P=2.0 **I=18** D=55 | **+4.08 K** (peaked 331.08 K) | Test script falsely reported "SUCCESS" — see bug note below | **Still overshoots by a similar magnitude even with I cut nearly in half.** Lowering I alone did not fix it. **New, more important finding: heater output pinned at a flat 50.0% for ~145 continuous seconds (t=39s→184s)** — a suspiciously exact, sustained ceiling. This looks like actuator **saturation** (PID demanding more than the loop could/would deliver) rather than a gain-tuning problem: a lot of heat was forced into the probe station's thermal mass while pinned near max, and that stored heat kept arriving at the sensor well after crossing setpoint, which plausibly explains the overshoot better than P/I/D values do. **Also found a bug in `pid_tune_test.py`/`monitor_only.py`**: once the loop first touched the ±0.2K settle band, the script started its hold-timer and never checked whether the temperature left the band again — so it declared "SUCCESS" after 3 minutes even though the real trace blew through the band up to +4.08K during that window. **Fixed** (now resets the hold timer if the error leaves the band again). This means test 1's "not settled" call was accurate, but any future run needs to be re-checked against this same bug pattern if the log wasn't from a post-fix script. |
| 2026-09-04 | 335 K | RAMPP, flat 2.0 K/min, **Range MID**, P=2.0 I=18 D=55 | N/A — could not track the ramp at all | Not settled; timed out at 8 min still -3.3K away, heater **pinned at 100% for ~350 continuous seconds** | **MID range is a dead end at this temperature.** It saturated at 100% and stayed there almost the entire test, yet temperature crept up far slower than the commanded 2 K/min — the probe station's radiative/conductive losses at 330K+ exceed MID's max wattage. README's "<340K use MID" guidance doesn't hold for this LN2-cooled Janis station (its cold shielding/chamber walls create bigger heat loss than a typical isolated setup). Stopped manually (safe — no runaway risk since power is capped low, just wasted time). |

### Key discovery: an existing 50% power-limit cap explains the HI-range saturation
Reading the manual again (prompted by the user) surfaced the correct SCPI command:
`LOOP 1:MAXPWR` — NOT `PMAX`, which is why earlier `PMAX?` queries returned `NAK`
(wrong mnemonic, not an unsupported feature). Querying it live:
```
LOOP 1:LOAD?    -> 50      (50-ohm heater load)
LOOP 1:MAXPWR?  -> 50.0    (an existing 50% power limit is already configured)
```
Per the manual's Table 25 (Loop 1 Heater Output Ranges, 50Ω load): HI=50W, MID=5.0W,
LOW=0.5W full scale. With MAXPWR=50%, **HI range's real ceiling here is 25W** — that
is exactly why heater output pinned at a flat "50.0%" for ~145s in the 315K/327K
tests: it wasn't the PID settling on 50%, it was hitting this hard limit. This
reframes the whole picture: **HI (capped at 25W) overshoots from too much stored
energy; MID (5W) can't keep up at all.** The real fix is almost certainly to stay
on HI and use `LOOP 1:MAXPWR` as a fine, continuous knob (valid range 15–100% per
the manual) between those two extremes, combined with a slower flat ramp rate so
less energy needs to be delivered per unit time before the D-term can start
throttling back. This MAXPWR=50 value looks like it may have been set deliberately
(possibly as an equipment-protection limit) — do not raise it without confirming
that's safe to change; lowering it (e.g. to 30%) to test between HI-uncapped and
MID is the safer direction to explore.

| 2026-09-04 | 340 K | RAMPP, **rate 1.0 K/min** (halved), Range HI, **MAXPWR 30%** (~15W, lowered from 50%), P=2.0 I=18 D=55 | **+2.23 K** (peaked 342.23 K, 167s after crossing setpoint) | Not settled — briefly touched ±0.2K band at 390-407s then rebounded, still +1.54K high at 12-min timeout | **User authorized freely adjusting MAXPWR going forward** (no longer waiting on confirmation it's a deliberate safety limit). Added `--maxpwr` option to `pid_tune_test.py` to make this a controllable test variable. **Result: overshoot roughly halved vs. the closest comparable uncapped-HI run (327K test, +4.08K)** by combining a lower power cap with a slower rate — real progress, but same fundamental shape of failure. Heater stayed pinned at the 30% cap continuously from ramp start through crossing setpoint (398.7s), only starting to taper *after* crossing, taking ~185s post-crossing to reach 0%. That post-crossing lag (not the ramp itself) is what drives the overshoot: stored heat delivered while pinned at cap keeps arriving at the sensor well after the heater backs off. **Conclusion: the D-term isn't causing the heater to anticipate and taper power *before* the setpoint is reached, only after** — next test should raise D further and/or lower P so heater output starts easing off earlier in the approach, before the crossing, rather than staying saturated at the cap right up to it. |

## MAXPWR is now a free tuning variable

Confirmed with the user (2026-09-04): the existing `LOOP 1:MAXPWR=50` value was
**not** a known deliberate safety limit — it was just whatever was last set. The
user gave explicit authorization to adjust it freely during tuning. It should
still be treated as a real actuator-power knob worth documenting per-test (as
above), not reset carelessly, but no further confirmation is needed before
changing it.

**Before assuming a command doesn't exist, doesn't apply, or behaves a certain
way — check `Cryocon_32_manual.md` first.** Confirmed this run: manual states
"For Loop #1, the Power Limit is applied to the HI range only. For lower power
levels on this loop, select either the MID or LOW range" — i.e. MAXPWR is a
no-op on MID/LOW, only meaningful on HI. This matches what the Attempt Log
already found empirically but is worth having as a manual citation for future
agents instead of re-deriving it from scratch.

| 2026-09-04 | 340 K (partial, superseded) | RAMPP, rate 1.0 K/min, Range HI, MAXPWR 30%, **P=2.0 I=18 D=80** (D raised from 55) | **+0.54 K only** (peak error at t=0, essentially just ramp-start noise — real approach overshoot was near-zero) | Settled by 71.6s, held cleanly, but test was manually stopped early (before the 3-min hold timer completed) to move on to the 345K test at user's request | **Big improvement from raising D 55→80.** This run started from a small delta (device was already near 340K from the prior test), so it's not a fully clean apples-to-apples data point, but the near-instant settle with minimal overshoot at these gains is why the same gains were carried into the 345K test below. |
| 2026-09-04 | 345 K | RAMPP, rate 1.0 K/min, Range HI, MAXPWR 30%, P=2.0 I=18 D=80 (same gains as 340K partial run above), **full ~5.1K climb from 339.9K** | **+1.96 K** (peaked 346.96K at t=527.8s, ~177s after first touching the settle band) | Touched ±0.2K band once at 350.9s but **overshot straight through it while still climbing** (heater was still at 27% at the moment of crossing) → rebounded to +1.96K peak → heater decayed 27%→0% over the next ~200s → temp then decayed passively (no active cooling) for another ~500s → finally back under 0.2K at 887.1s, but timeout (15 min) hit at 899.8s after only ~12.7s of continuous hold, short of the 180s required | **FAIL (timeout, not a clean settle) but instructive.** Confirms the windup lesson: identical gains gave near-zero overshoot on a short ~0K delta (340K partial run) but +1.96K on this run's full ~5.1K climb — **overshoot magnitude scales with how far the internal ramp actually has to travel, not just the gains.** Also newly confirmed: heater was still at 27% *at the exact moment* Temp A first crossed into the settle band (350.9s) — the D-term still isn't tapering power early enough before crossing, it's reacting to the crossing itself. **Live re-check ~10 min after test end (device left running, Control ON): Temp A settled naturally to 344.98K, error -0.02K, heater 0.2%** — so it does eventually converge almost exactly on setpoint, just far slower (via passive radiative decay of the overshoot) than the 3-minute hold window this test enforces. |

| 2026-09-04 | 330 K | RAMPP, rate 1.0 K/min, Range HI, MAXPWR 30%, P=2.0 I=18 D=80 (same gains again), climb from 325.8K | **+2.41 K** (peaked 332.41K at t=370.5s) | Interrupted before settling — stopped early at user's request to move directly to a 335K test rather than wait out the passive decay tail | Same pattern as the 345K run: touched the ±0.2K band once at 196.5s while still climbing, blew through it, then started a slow passive decay (heater 0% for the rest of the observed window, still +2.0K high when stopped ~510s in). **Manual research finding (Cryocon_32_manual.md ~line 2135):** the Model 32's enhanced PID explicitly names "Integrator wind up compensation" as a feature for exactly this scenario ("especially true in cryogenic environments where process time constants can be very long") — confirms this is a known, named failure mode, not something unique to this setup. Also found the manual's own Ziegler-Nichols tuning appendix (Appendix D) recommends **D=0** for cryogenic/noisy systems, which is the opposite direction of what's been tried (raising D 55->80 helped on short hops). Unconfirmed whether the 22C's PID implementation includes the same anti-windup compensation the Model 32 manual describes — the 22C is a simpler/older sibling model. |
| 2026-09-04 | 335 K | RAMPP, rate 1.0 K/min, Range HI, MAXPWR 30%, P=2.0 I=18 D=80, **started immediately after stopping the still-decaying 330K run (~332K, +2K error) rather than waiting for full settle** | **+2.33 K** (peaked 337.33K at t=558.7s) | **FAIL (timeout).** Briefly touched the settle band once, 384.6-398.7s (~14s), then rebounded and **never re-entered the band again** for the rest of the 15-min run — ended at +1.13K, still RAMPING, at the 899.8s timeout | Testing whether starting a new setpoint before the prior run's I-term (not just its ramp target, which the resync fix already handles) has unwound made things worse. **Result is somewhat worse than the two prior comparable runs** (345K: recovered to +0.13K by timeout; 330K partial: was still improving when stopped) — this run ended further from settled than either. Suggestive that starting before the previous overshoot has fully bled off may compound the windup, but **this is one data point and the peak magnitude (+2.33K) is not dramatically different from 330K's own +2.41K peak** — not conclusive on its own. Live re-check after test end: Temp A 336.06K, error +1.06K, heater 0%, Control ON, still decaying passively — safe, unresolved. **Recommendation: for the next test, let the device fully settle/decay before starting a new setpoint, to get a clean data point and properly isolate this variable** rather than continuing to chain tests back-to-back. |

## Literature & manual research findings (2026-09-04)

While the 330K/345K decay tails were running, did a deliberate research pass
(manual + external literature) instead of just waiting idle. Findings:

1. **The Model 32 manual names our exact failure mode by name.**
   `Cryocon_32_manual.md` (~line 2135), under "Enhancements" to the PID
   algorithm: *"Integrator wind up compensation. While slewing to a new
   setpoint, the integrator in the PID loop can build up to a very large
   value. If no compensation is applied, overshoot and time to stability at
   the new setpoint can be delayed for an extremely long time. This is
   especially true in cryogenic environments where process time constants can
   be very long."* This is precisely the shape of every overshoot seen in
   this log: heater pins at/near its cap, temperature sails through the
   setpoint, heater backs off only after crossing, and a long passive tail
   follows. **Not yet confirmed** whether the 22C (an older/simpler sibling
   of the Model 32 this manual documents) actually implements this
   compensation in firmware — worth testing empirically (e.g. does overshoot
   scale sub-linearly with ramp distance the way compensated systems should,
   or linearly the way an uncompensated integrator would?).

2. **The same manual section also mentions a "user-settable damping factor...
   to minimize overshoot"** as a separate PID enhancement, but no distinct
   `LOOP:DAMP`-style SCPI command was found anywhere in the remote command
   reference. Either it isn't exposed remotely (front-panel only), it's a
   different name for something we're already setting (e.g. D-gain itself),
   or it doesn't exist on the 22C. **Unconfirmed — do not assume a `DAMP`
   command exists without testing it live first** (`LOOP 1:DAMP?` or similar)
   per this file's own "check the manual, don't assume" rule above.

3. **The manual's own Ziegler-Nichols tuning appendix (Appendix D) recommends
   D=0 for cryogenic/noisy systems** — "In systems where there is high
   thermal noise, including cryocoolers, a Dgain value of zero is often
   used." This directly contradicts the direction explored so far (raising D
   55->80 helped considerably on short hops). Formal Z-N procedure per the
   manual: set P=0.1, I=0, D=0, engage control, raise P until sustained
   oscillation, record that gain as Kc and the oscillation period as Tc, then
   set **P=0.6*Kc, I=0.5*Tc, D=0.85*Tc** (or D=0 if noisy). This hasn't been
   attempted — it requires deliberately inducing oscillation, which needs an
   Over Temperature Disconnect configured first per the manual's own caution.
   Not yet done in this log.

4. **External literature on PID anti-windup** (general control theory, not
   Cryocon-specific) confirms the mechanism: windup specifically requires
   actuator saturation (the heater pinned at a hard cap, e.g. our MAXPWR=30%
   ceiling) — while saturated, the integral term keeps accumulating error it
   can't yet act on. Standard remedies are integral clamping (pause
   accumulation while saturated) or back-calculation (unwind the accumulator
   using the saturation error) — both are firmware-internal techniques we
   can't add to this controller directly. The practical equivalent available
   to us: keep I small enough that little winds up in the first place, and/or
   avoid pinning the heater at its cap for extended periods (e.g. give it
   more headroom via a higher MAXPWR + slower rate, rather than a lower
   MAXPWR that saturates just as hard against a smaller ceiling). Sources:
   [Fixing PID Integral Windup in Temperature Control Applications](https://industrialmonitordirect.com/blogs/knowledgebase/pid-integral-windup-fix-for-slow-temperature-control-systems),
   [Anti-Windup in PID Control: Review, Analysis, and New Tuning Directions (arXiv)](https://arxiv.org/html/2606.01959v1),
   [PID Anti-windup Techniques](https://info.erdosmiller.com/blog/pid-anti-windup-techniques).

| 2026-09-04 | 340 K | RAMPP, rate 1.0 K/min, Range HI, MAXPWR 30%, P=2.0 I=18 D=80, **started from a fully settled, clean 334.89K baseline** (unlike the previous back-to-back 335K run) | **+2.30 K** (peaked 342.30K at t=520.9s) | **FAIL (timeout).** Touched settle band once at 342.5s (12 rows, brief), rebounded, then passive decay — ended at +0.82K, still RAMPING, at the 899.8s timeout, never re-settled | **Key clarifying result: a clean settled start gives essentially the same overshoot (+2.30K) as the previous back-to-back/unsettled-start run (+2.33K at 335K).** This weakens the "starting before settle compounds windup" hypothesis from the 335K entry above — the overshoot magnitude for a ~5K climb with these gains is consistently landing around +2.0-2.4K regardless of whether the prior run had fully settled first. **Conclusion: with the current P=2.0 I=18 D=80 / MAXPWR 30% / rate 1.0 gains, ~5K climbs reliably produce ~2-2.4K overshoot; this is the current performance ceiling for these gains, not a fluke of test sequencing.** Next tuning attempt should change the gains themselves (D=0 per manual's cryo guidance, or a proper Ziegler-Nichols pass) rather than just varying test sequencing/hop size, since hop-size and sequencing have now both been checked and aren't the dominant variable — the gains are. |

## SESSION HANDOFF NOTE (2026-09-04, ~21:37)

**Handing this task to another AI agent/session. Read this whole file before
touching the hardware.**

**Live state at handoff:** A background test (`pid_tune_test.py --target 340
--rate 1.0 --p 2.0 --i 18 --d 80 --range HI --maxpwr 30 --hold 3 --maxrun 15
--maxover 8`) is **still actively running** and holds the COM5 serial port —
attempting to open COM5 from another process will fail with a permission
error until this process exits (either it times out at 15 min run time, or
someone stops it). It is safely decaying from a +2.30K peak overshoot back
toward 340K; no danger, just let it finish or stop it before starting
anything new that needs the port. Log file:
`cryocon_log_20260904_212740_pidtune.csv`.

**Where things stand:** Best gains found so far are **P=2.0 I=18 D=80,
Range=HI, MAXPWR=30%, rate=1.0 K/min** (`pid_tune_test.py`'s `--maxpwr`
flag). These reliably produce near-zero overshoot on very short hops but
**~2.0-2.4K overshoot on ~5K climbs**, confirmed consistent across multiple
runs regardless of whether the prior setpoint had fully settled first (see
340K entry directly above this note) — so the remaining overshoot is a real
property of these gains on longer climbs, not test-sequencing noise.

**Recommended next steps (see "Literature & manual research findings" and
"Next test ideas" sections above for full detail):**
1. Try **D=0**, per the controller manual's own Ziegler-Nichols guidance for
   cryogenic/noisy systems (this is the opposite of the D=55->80 direction
   tried so far, and hasn't been tested).
2. Consider running the manual's formal **Ziegler-Nichols tuning procedure**
   (Appendix D of `Cryocon_32_manual.md`) instead of continued ad hoc
   trial-and-error — set an Over Temperature Disconnect first, since it
   deliberately induces oscillation.
3. Query `LOOP 1:DAMP?` (read-only) once to check whether the manual's
   "user-settable damping factor" feature is exposed on this 22C at all —
   unconfirmed either way.
4. Eventually test a genuinely long ramp from near 300K (not just chained
   ~5K hops) with whatever gains look best, since that's the real 450K
   use-case shape.

**Standing rules for this file (see top of file and inline notes):**
check `Cryocon_32_manual.md` before assuming a command doesn't exist or
guessing its syntax; append every attempt to the Attempt Log with actual
data, not just a plan; the user has authorized freely adjusting `MAXPWR` and
other gains during tuning (no longer a pause-and-confirm item).

## Next test ideas (not yet run)
- Since overshoot scales with ramp distance, test **the same P=2.0 I=18 D=80 gains on a genuinely long ramp from a cold start (e.g. 300K -> 345K or higher)** rather than continuing to chain short hops between tests — that's the real-world 450K use case and the current short-hop testing pattern is under-representing real overshoot.
- Consider **lowering I further** (it hasn't been retested since I=18 at 327K/HI-uncapped) now that D=80 + MAXPWR 30% + rate 1.0 are already damping much better — less integral windup on longer ramps may close most of the remaining gap.
- Consider extending `--hold` past 3 min or loosening the settle band tolerance for the *test script's* success criterion — the controller itself is clearly capable of landing within 0.02-0.05K of setpoint eventually (confirmed via the live re-check above), the test script's pass/fail is a diagnostic convenience, not the real target.
- **Try the manual's own Ziegler-Nichols procedure** (item 3 above) to get a principled starting point instead of continuing to hand-tune by trial and error — set an Over Temperature Disconnect first since it deliberately induces oscillation.
- **Try D=0** per the manual's cryogenic-systems guidance (item 3 above) as a direct contrast to the D=55->80 direction tried so far — current results don't yet distinguish whether D is helping or whether MAXPWR+rate are doing all the work.
- Query `LOOP 1:DAMP?` (or equivalent) once, read-only, to settle whether the manual's "damping factor" enhancement (item 2 above) is exposed on this 22C at all, before assuming it isn't.


---

# ROOT CAUSE ANALYSIS AND FIX (2026-09-04 evening session)

Everything below is derived from the CSVs already in this repo plus three new
hardware runs. Where a number is quoted it came from measurement, not theory.

## 1. The "stored heat / thermal soak" theory is wrong - measured, not argued

`README.md` and the early entries in this file both explain overshoot as heat
continuing to "soak into the sample after the setpoint is reached". That is
testable: find the first moment the heater output actually reads 0%, and see how
much further the temperature climbs.

| Run | Setpoint | Total overshoot | **Climb after heater hit 0%** |
|---|---|---|---|
| `172651` | 327 K | +4.08 K | **+0.009 K** |
| `175131` | 340 K | +2.23 K | **+0.014 K** |
| `181410` | 345 K | +1.96 K | **+0.046 K** |
| `201855` | 330 K | +2.41 K | **+0.001 K** |
| `212740` | 340 K | +2.30 K | **+0.007 K** |

The station has **essentially no heater-to-sensor thermal lag** (identified dead
time is about 20 s, see section 4). Temperature stops climbing the moment power
stops. So the overshoot was never stored energy - in every run **the heater was
still delivering 27-29% power while the sample was already above setpoint**, for
a strikingly repeatable ~166-170 s each time. That repeatable duration is the
signature of an integrator unwinding, not of a thermal time constant.

## 2. `IGAIN` is integral time in SECONDS

`Cryocon_32_manual.md` line 5440: *"This is a numeric field with units of
seconds. Allowed values are 0 (off) through 1000 seconds."* Line 7014 confirms
it: *"The Integral, or I term is in units of Seconds."* Factory defaults are
**P=0.1, I=5.0, D=0** (line 7028).

So a **smaller** `IGAIN` is a **faster** integrator. Every session in this file
lowered it to fight windup, which made windup worse:

- `README.md` documented I around 160 at 300 K (the original table).
- `write_pid_table02.py` rewrote Zone 1 to I = 30-45, with the comment
  *"~5x lower than original (165-250). Prevents integrator windup"* - this
  reasoning is **inverted**. Per `DEV_NOTES.md` that table was written
  2026-08-24, which is a plausible origin for the regression.
- Tests in this log then went further, to I = 18.

External literature puts integral time for thermal processes at **60-300 s**
([ISA, Loop tuning basics: integrating processes](https://www.isa.org/intech-home/2016/march-april/departments/loop-tuning-basics-integrating-processes),
[Fundamentals of lambda tuning](https://www.controleng.com/fundamentals-of-lambda-tuning/)),
and notes that an integrating process **oscillates when integral action is too
fast**. I=18 s was roughly an order of magnitude too fast.

## 3. Identified the controller's actual equation

Fitted against run `212740` (P=2, I=18, D=80, cap 30%) and reproduces the logged
heater trace to **about 4%**:

```
heater% = Pgain * ( e + (1/Igain)*integral(e dt) + Dgain*de/dt )
```

where `e` = (moving ramp setpoint - Temp A) in K, and heater% is percent of the
**range** full scale (HI = 50 W at the measured 50 ohm load).

Worked check at t=84 s of that run: e=1.391, integral(e dt)=61.7 K.s,
de/dt=0.0124 K/s -> P term 2.78% + I term 6.86% + D term 1.99% = **11.6%**
versus **11.2% logged**.

## 4. Identified the plant

From the heater step and the passive-decay tails of all logs:

- **Heat capacity C is about 520 J/K**
- **Dead time is about 20 s** (clean least-squares minimum)
- **Heat loss is about 0.0754*(T-297) - 0.98 W**
- Open-loop time constant C/k is about 3 hours, so over our timescales this is
  effectively an **integrating process** - exactly the class the literature
  above warns must not be given fast integral action.

**Consequence for the 450 K goal:** holding 450 K needs about 21% of HI, and a
1 K/min ramp there needs about **39%**. The MAXPWR = 30% cap that earlier
sessions adopted **cannot physically sustain the ramp at the target
temperature** - it would saturate permanently and wind up without limit.
MAXPWR must be at least about 50%.

## 5. The mechanism, quantified

In run `212740`, at the moment the moving ramp setpoint arrived at 340 K the
loop was **demanding about 50% power but clipped at the 30% cap**, while the
power actually needed to hold 340 K was about 4%. There is no anti-windup in
this firmware path, so the integrator kept accumulating while clipped. That
stored integral (about 446 K.s) can only be paid back by an equal *area* of
negative error - which is precisely the observed +2.3 K over ~170 s overshoot.

**Overshoot area = windup area.** That single sentence explains every run in
this file, including why overshoot scaled with ramp distance and why it was
insensitive to D.

## 6. Hardware results

| Date | Setpoint | Gains / config | Peak overshoot | Outcome |
|------|----------|----------------|----------------|---------|
| 2026-09-04 | 345 K | RAMPP, 1.0 K/min, HI, cap 30, **P=2 I=18 D=0** | **+2.06 K** | Baseline re-run with D removed. Essentially identical to the D=80 run (+2.30 K), so **D was never the variable**. Stopped early once the crossing behaviour was unambiguous (heater still at 22.5% while 1.3 K *above* setpoint). |
| 2026-09-04 | 352 K | RAMPP, 1.0 K/min, HI, cap 50, **P=40 I=0 D=0** (P-only) | **0.00 K** (peak error -0.140 K) | **SUCCESS.** Monotonic approach, never crossed setpoint. Heater tapered 20.7% and parked at 6.1%. Settled at -0.153 K, exactly the predicted P-only droop (hold power 6.1% / P 40 = 0.153 K) - model accurate to 1%. Also confirmed `heater% = 40 * error` live on the device. |
| 2026-09-04 | 357 K | RAMPP, 1.0 K/min, HI, cap 50, **P=25 I=900 D=0** | **0.00 K** (peak error -0.036 K) | **SUCCESS - this is the recommended gain set.** Never crossed setpoint. Settled -0.046 K and kept converging; a live check about 5 min later read **356.9836 K, error -0.016 K**, heater 6.78%. Zero overshoot *and* essentially zero steady-state error. |

See `overshoot_before_after.png`, generated by `make_overshoot_figure.py`.

## 7. Recommended settings

```
LOOP 1:PGAIN  25
LOOP 1:IGAIN  900        # integral time, SECONDS (max 1000)
LOOP 1:DGAIN  0          # manual also recommends D=0 for cryogenic systems
LOOP 1:RANGE  HI
LOOP 1:MAXPWR 50         # raise toward 70 above ~400 K; NEVER 30 (cannot sustain the ramp)
LOOP 1:RATE   1.0
```

This is a single flat ramp rate with fixed gains - no software two-speed trick -
so it transfers directly to the LabVIEW deployment described in
`role_Context_and_objective.md`.

**Why these numbers, so they can be re-derived rather than trusted:** with an
integrating plant and 20 s dead time, P-only goes unstable at P around 82, so
P=25 sits at about 62 degrees phase margin (P=40 gives about 46 degrees, also
fine; P of 60 or more is marginal - do not go there). Igain is then chosen long
enough that little winds up during the approach. A simulator built on the
identified model reproduces all five runs above and was used to pick the pair;
D=40-80 makes it *worse* in both simulation and hardware.

## 8. Bug fixed in `pid_tune_test.py`

The "resync" that parks the setpoint at the live reading before starting a ramp
was being issued **while the loop was still in RAMPP mode**, so the resync
itself ramped at `--rate` instead of jumping. The controller therefore kept
controlling to the *previous* setpoint for a long time - observed live on
2026-09-04: **the heater sat at 0% for the first ~90 s** of a run because the
working setpoint was still down at the old target, below the live reading.
Fixed by dropping to `LOOP 1:TYPE PID` for the resync (instantaneous) before
switching to RAMPP. Verified: the heater now engages within about 50 s.

Also added `Ramp_SP_K` / `Track_Err_K` columns so the moving setpoint and the
tracking error the PID actually sees are logged directly, instead of having to
be reconstructed from the CSV afterwards.

## 9. SUPERSEDED - do not act on these

- **"Stored heat keeps soaking in after the setpoint"** (this file's Root cause 1
  and `README.md`'s "How Smart Two-Speed Ramping Eliminates Overshoot").
  Disproved by the coast-after-zero-power measurements in section 1.
- **"Lower I to reduce windup"** (`write_pid_table02.py` Zone 1 comment, and the
  I: 30.4 -> 18 tests). Backwards - see section 2.
- **"Raise D to damp the approach"** (the D 55 -> 80 direction). D=0, D=55 and
  D=80 all give about +2 K with the old P and I; both clean runs used **D=0**.
- **"MAXPWR 30% helps"** - it halved overshoot only because the ramp rate was
  halved in the same test. A low cap *causes* the saturation that drives windup,
  and 30% cannot sustain a 1 K/min ramp at 450 K at all (section 4).
- **`README.md`'s PID Table 02 listing** is stale, and the table currently on the
  hardware (P about 2, I=30-45, D=52-70 in Zone 1) is the *bad* tuning. It should
  be rewritten with the section 7 values before any Table/RAMPT-mode deployment.

## 10. Safety configuration

### Over Temperature Disconnect - CONFIGURED 2026-09-04

**Status: ENABLED, source Channel A, trip point 460 K.** Set manually on the
front panel by the user before the first unattended overnight run.

**It is NOT remotely settable.** Probed live on this 22C: `SYSTEM:OTD?`,
`SYSTEM:OTDENAB?`, `SYSTEM:OTDSRC?`, `SYSTEM:OTDSETPT?`, `SYSTEM:OTEMP?` and
`OTD?` **all return `NAK`**. It is front-panel only (**Sys** key). Do not waste
time looking for a SCPI command - there isn't one on this firmware, and no
script can set, verify, or restore it. If the instrument is ever factory-reset
or the setting is changed, **it must be re-entered by hand** (factory default is
Off, manual line 326).

Channel A is the only usable source: **Channel B currently reads a sensor fault**
(`INPUT? B` returns `.......`), so it cannot be selected as the OTD input.

Why this matters: the OTD is the *only* hardware-level protection. It opens a
mechanical relay, so it protects the load even if the fault is in the
controller's own output circuitry (manual line 1384). Every other guard in this
project is software and dies with the Python process.

### Layered protection now in place (outermost last)

| Layer | Trip point | Mechanism | Survives script crash? |
|---|---|---|---|
| Per-stage overshoot abort | setpoint + 3 K | `staged_ramp_test.py` sends `STOP` | No |
| Absolute software ceiling | 460 K | `staged_ramp_test.py --maxtemp` | No |
| **Over Temperature Disconnect** | **460 K** | **hardware relay, Channel A** | **Yes** |

Note the ordering is correct by design: for every stage the per-stage abort
(setpoint + 3 K) trips well below 460 K, so the software always acts first and
shuts down gracefully; the OTD only fires as a genuine last resort. With a final
target of 450 K and measured overshoot well under 1 K, the 460 K trip leaves
about 10 K of margin and should never nuisance-trip.

`pid_tune_test.py` does **not** send `STOP` on exit - if that process is killed
mid-ramp the controller keeps heating to its last setpoint. Observed directly on
2026-09-04 when the 450 K run was stopped: the station kept climbing until the
setpoint was manually parked at the live reading. `staged_ramp_test.py` was
written to fix this and sends `STOP` on every exit path (exception, Ctrl+C,
abort, limit trip). **Prefer `staged_ramp_test.py` for anything unattended.**

## 11. Open items

- Rewrite PID Table 02 Zone 1 with the section 7 gains for RAMPT/Table-mode
  deployment. Not yet done - all validated runs so far used RAMPP with direct
  gains, so the bad table values are still in NVRAM.
- Zone 2 (77-300 K, LN2 cooling) has **not** been re-examined. Its I = 50-65 s
  values are also very fast for a thermal loop and are likely wrong for the same
  reason as Zone 1, but there is no data at cryogenic temperatures in this log -
  do not change them without testing.
- The LabVIEW VI has no control for `LOOP 1:TYPE` or `LOOP 1:MAXPWR`. Both
  matter: in `RAMPT`/`Table` mode the loop **ignores** `PGAIN`/`IGAIN`/`DGAIN`
  and uses the table instead, so writing gains from the VI can silently do
  nothing; and MAXPWR = 30% cannot sustain a 1 K/min ramp at 450 K (section 4).

## 12. Overnight Staged Campaign & Full Report Generation (2026-09-04 / 2026-09-05 overnight)

- **Generated Full Tuning Report & Figures:** Created publication-grade report in `TUNING_REPORT.md` and a single self-contained `TUNING_REPORT.html` with embedded base64 figures (Figures 1 through 6) derived directly from all historical CSV logs.
- **Repository Documentation Refinement:**
  - Updated `README.md` to remove the disproven "stored heat soak" hypothesis and replace it with the true physical explanation (integral windup during actuator saturation, `IGAIN` in seconds). Updated PID Table 02 listing and high-temperature power limit guidance.
  - Updated `write_pid_table02.py` Zone 1 table definitions and comments with the validated zero-overshoot gains (`P=25.0, I=900, D=0, Range HI`).
- **Completed Staged Ramp Campaign (`cryocon_log_20260904_225640_staged.csv`):**
  - Walked stages 375 -> 385 -> 390 -> 405 -> 420 -> 450 K with `P=25, I=900 s, D=0, Range HI, MAXPWR 70%, rate 1.0 K/min`.
  - **Stage 1 (375.0 K, hop +2.76 K):** Peak over -0.082 K (zero overshoot), settled cleanly.
  - **Stage 2 (385.0 K, hop +10.08 K):** Peak over +0.165 K, settled at 385.085 K.
  - **Stage 3 (390.0 K, hop +4.91 K):** Peak over +0.158 K, settled at 390.087 K.
  - **Stage 4 (405.0 K, hop +14.91 K):** Peak over +0.284 K, smooth approach.
  - **Stage 5 (420.0 K, hop +14.89 K):** Peak over +0.288 K, smooth approach.
  - **Stage 6 (450.0 K, hop +29.89 K):** Peak over +0.361 K! Held 450 K under watchdog for 30 minutes at 20.85% equilibrium power (flawlessly matching physical heat loss model prediction of 21.1%).
  - **Final Safe Shutdown:** Watchdog window completed cleanly at 02:58; sent `STOP`, verified `CONTROL = OFF`, heater at `0.0%`, COM5 released. Instrument safe and idle.



---

# SESSION 3 (2026-09-05) - startup bug, and the Ti trade-off

## 12. BUG: writing the setpoint while CONTROL is OFF causes a full-power slam

**Symptom.** Starting a ramp from a cold `CONTROL=OFF` state, the heater pinned
at the MAXPWR cap (70%) for about 35 seconds, with a tracking error of only
+0.16 K. Logged live 2026-09-05 06:47 in
`cryocon_log_20260905_064730_staged.csv`.

**Cause.** `configure_stage()` wrote the *target* setpoint before sending
`CONTROL`. **The ramp state machine only runs while the loop is controlling**,
so with control off the setpoint write arms nothing - it just parks the target.
When `CONTROL` was then sent, the loop saw the FULL setpoint error at once
(10 K), and P=25 x 10 K demands 250% output, which clips to the cap. In ~35 s
at 60-70% the integrator wound up to about 60% when holding 353 K needs ~7%.

That is the exact saturation-windup failure this whole project exists to
eliminate, reintroduced through the startup sequence. It never appeared in the
earlier runs because those all began with `CONTROL` already ON, so the setpoint
write armed the ramp correctly. It only surfaced once a session started from a
fully stopped instrument.

**Fix** (in `staged_ramp_test.py`, `configure_stage`): engage `CONTROL` *first*,
while the setpoint is still parked at the live reading, wait ~3 s for the loop
to settle at hold power, and only then switch to `RAMPP` and write the target.
Verified: heater now starts at 1.5% instead of 70%.

**This applies directly to the LabVIEW VI.** Its front panel has the same
hazard - pressing **Set Temperature** before **Start Control** reproduces this
slam. Correct order is:

> **Start Control** -> Set Range -> Set Ramp Rate -> Set PID -> **Set Temperature last**

Setting the setpoint is what arms the ramp, so it must come last, and control
must already be engaged when it happens.

## 13. Ti trade-off measured: I=400 is WORSE than I=900 on overshoot

Motivation: with I=900 the residual error decays to zero with a time constant of
about **21 minutes** (measured in the 450 K stage: +0.164 -> +0.099 -> +0.062 ->
+0.041 over successive 10-minute windows, a constant ratio of ~0.62). The
hypothesis was that shortening Ti would settle faster without reintroducing
overshoot, since the loop was no longer saturating (peak heater ~36% against a
70% cap in the 450 K run).

**Result: the hypothesis was wrong on the axis that matters.**

| Gains | Hop size | Peak overshoot |
|---|---|---|
| P=25, **I=900**, D=0 | +10.1 K | **+0.165 K** |
| P=25, **I=400**, D=0 | +9.8 K | **+0.343 K** |

Halving the integral time **roughly doubled the overshoot**. Peak heater was
21.3% against a 70% cap, so this is not clipping - it is ordinary linear
windup during the ramp. **I=900 remains the best configuration found.**

**Why, physically.** During a constant-rate ramp the integrator must supply the
ramp power: `C * rate` = 520 x (1/60) = 8.67 W = 17.3% of HI, on top of the hold
power (~6.8% at 355 K). At the moment the ramp setpoint arrives, the integrator
therefore holds ~24% while only ~7% is needed to hold station. **That excess is
what drives the remaining overshoot**, and a shorter Ti lets the integrator load
up faster during the ramp, so there is more to shed at arrival.

With PI control and a fixed ramp rate, peak overshoot and settling time are
coupled through Ti and cannot both be minimised. Choose one:

- **I=900** - lowest overshoot (+0.165 K on a 10 K hop), ~21 min to converge.
- **I=400** - faster convergence, but double the overshoot. Not recommended.

## 14. Untested lever: the D term, in the now-unsaturated regime

Section 9 lists "raise D to damp the approach" as SUPERSEDED. **That conclusion
was correct for the conditions it was measured in, and does not apply here.**
It was drawn from runs with P=2 where the heater was *clipped at the MAXPWR
cap*, and two things follow from that:

1. While the actuator is saturated, **no** controller term can do anything -
   the output is pinned regardless of what P, I or D compute.
2. Even unsaturated, with P=2 the D contribution was
   `2 x 80 x 0.0167 K/s = 2.7%` - negligible against a ~30% excess.

The situation is now different: P=25 and the loop never saturates. The D term
is `Pgain x Dgain x de/dt`, so at arrival, with the temperature still rising at
1 K/min (0.0167 K/s):

```
D=40  ->  25 x 40 x 0.0167  =  16.7%
```

which is almost exactly the excess ramp power that must be shed. **D=40 should
therefore cancel the ramp momentum right at arrival**, which is precisely what
derivative action is for. This is the most promising remaining lever and has
never been tested at a useful magnitude.

Caveat: D amplifies sensor noise, and the manual recommends D=0 for cryogenic
systems. This sensor is quiet (readings smooth to ~0.005 K), so the predicted
noise contribution is ~1% of output. Test before trusting.

**Guaranteed fallback if D does not work:** overshoot is proportional to the
excess ramp power, which is proportional to **ramp rate**. Halving the rate to
0.5 K/min roughly halves the overshoot, with no tuning risk at all - it just
costs time (a 100 K climb goes from ~1.7 h to ~3.3 h).
