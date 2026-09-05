"""Before/after comparison of the overshoot tuning effort.

Plots error-vs-time (temperature minus final setpoint) for the baseline runs
and the retuned runs on one axis, so the change in approach shape is visible
regardless of absolute setpoint. Also plots heater output, which is where the
mechanism actually shows: the old gains keep the heater at ~29% while ALREADY
above setpoint, the new ones taper it to the hold value before arrival.
"""
import csv, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RUNS = [
    ("cryocon_log_20260904_172651_pidtune.csv", "OLD  P=2 I=18 D=55  cap50  2K/min  (327K)", "#b2182b", "--"),
    ("cryocon_log_20260904_212740_pidtune.csv", "OLD  P=2 I=18 D=80  cap30  1K/min  (340K)", "#ef8a62", "--"),
    ("cryocon_log_20260904_214322_pidtune.csv", "OLD  P=2 I=18 D=0   cap30  1K/min  (345K)", "#fdae61", "--"),
    ("cryocon_log_20260904_215308_pidtune.csv", "NEW  P=40 I=0 D=0   cap50  1K/min  (352K)", "#2166ac", "-"),
]

def load(fn):
    t, e, h = [], [], []
    with open(fn, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                t.append(float(r["Elapsed_Sec"]))
                e.append(float(r["Temp_A_K"]) - float(r["Setpoint_K"]))
                h.append(float(r["Heater_Pct"]))
            except (ValueError, TypeError, KeyError):
                pass
    return t, e, h

def main(extra=None):
    runs = list(RUNS)
    if extra:
        runs.append((extra, "NEW  P=25 I=900 D=0 cap50 1K/min  (357K)", "#1a9850", "-"))
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8.5), sharex=True)
    for fn, label, color, ls in runs:
        if not os.path.exists(fn):
            print(f"  (skip missing {fn})"); continue
        t, e, h = load(fn)
        if not t: continue
        ax1.plot([x/60 for x in t], e, color=color, ls=ls, lw=1.8, label=label)
        ax2.plot([x/60 for x in t], h, color=color, ls=ls, lw=1.8)
        print(f"  {label:<46} peak {max(e):+.3f} K   final {e[-1]:+.3f} K")

    ax1.axhline(0, color="k", lw=1)
    ax1.axhspan(-0.2, 0.2, color="green", alpha=0.10, label="+/-0.2 K target band")
    ax1.set_ylabel("Temperature - setpoint  (K)")
    ax1.set_title("Cryocon 22C / Janis ST-LN-500: overshoot before and after retuning\n"
                  "(IGAIN is integral time in SECONDS - the old I=18 s was a very fast integrator)",
                  fontsize=11)
    ax1.legend(fontsize=8, loc="upper left")
    ax1.grid(alpha=0.3)
    ax1.set_ylim(-6, 5)

    ax2.set_ylabel("Heater output (%)")
    ax2.set_xlabel("Elapsed time (min)")
    ax2.grid(alpha=0.3)
    ax2.set_title("Heater output - old gains stay near the power cap through the setpoint crossing", fontsize=10)

    fig.tight_layout()
    out = "overshoot_before_after.png"
    fig.savefig(out, dpi=140)
    print(f"\nwrote {out}")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
