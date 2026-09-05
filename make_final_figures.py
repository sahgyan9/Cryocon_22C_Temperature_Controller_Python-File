"""
Final report figures for the Cryocon 22C overshoot study.

Every figure is generated with constrained_layout and generous spacing so that
nothing overlaps: legends sit outside the data area, annotations are anchored
clear of the curves, and each panel carries at most a handful of traces.

    python make_final_figures.py
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "figure.dpi": 130,
    "savefig.dpi": 160,
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.labelsize": 10.5,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "legend.frameon": True,
    "legend.framealpha": 0.92,
    "legend.fontsize": 9,
})

OK, BAD, MID = "#1a7f37", "#c1121f", "#0b6bcb"


DATA = "data"
FIGS = "figures"


def load(fn):
    if not os.path.exists(fn):
        fn = os.path.join(DATA, fn)
    with open(fn, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def series(fn, target=None):
    """-> (minutes, error, heater, temp) for one run."""
    rows = load(fn)
    t, e, h, T = [], [], [], []
    t0 = float(rows[0]["Elapsed_Sec"])
    for r in rows:
        try:
            tgt = target if target is not None else float(
                r.get("Stage_Target_K") or r.get("Setpoint_K"))
            temp = float(r["Temp_A_K"])
            t.append((float(r["Elapsed_Sec"]) - t0) / 60.0)
            T.append(temp)
            e.append(temp - tgt)
            h.append(float(r["Heater_Pct"]))
        except (ValueError, TypeError):
            pass
    return t, e, h, T


def stage(fn, idx):
    """One stage out of a staged log."""
    rows = [r for r in load(fn) if r["Stage_Idx"] == str(idx)]
    t0 = float(rows[0]["Elapsed_Sec"])
    tgt = float(rows[0]["Stage_Target_K"])
    t = [(float(r["Elapsed_Sec"]) - t0) / 60 for r in rows]
    e = [float(r["Temp_A_K"]) - tgt for r in rows]
    h = [float(r["Heater_Pct"]) for r in rows]
    T = [float(r["Temp_A_K"]) for r in rows]
    return t, e, h, T


# --------------------------------------------------------------------------
# FIG 1 - headline before / after
# --------------------------------------------------------------------------
def fig1():
    fig, ax = plt.subplots(2, 1, figsize=(9.5, 8), sharex=True,
                           constrained_layout=True)

    runs = [
        ("cryocon_log_20260904_172651_pidtune.csv", 327.0,
         "BEFORE   P=2  I=18  D=55", BAD, "--"),
        ("cryocon_log_20260904_212740_pidtune.csv", 340.0,
         "BEFORE   P=2  I=18  D=80", BAD, ":"),
    ]
    for fn, tgt, lab, c, ls in runs:
        if not (os.path.exists(fn) or os.path.exists(os.path.join(DATA, fn))):
            continue
        t, e, h, _ = series(fn, tgt)
        ax[0].plot(t, e, ls, color=c, lw=1.9, label=lab)
        ax[1].plot(t, h, ls, color=c, lw=1.9, label=lab)

    t, e, h, _ = stage("cryocon_log_20260905_081200_staged.csv", 1)
    ax[0].plot(t, e, "-", color=OK, lw=2.4, label="AFTER   P=40  I=900  D=0")
    ax[1].plot(t, h, "-", color=OK, lw=2.4, label="AFTER   P=40  I=900  D=0")

    ax[0].axhspan(-0.1, 0.1, color=OK, alpha=0.13, zorder=0)
    ax[0].axhline(0, color="0.3", lw=1)
    ax[0].set_ylabel("Temperature − setpoint  (K)")
    ax[0].set_title("Overshoot before and after retuning")
    ax[0].set_ylim(-11, 5)
    ax[0].legend(loc="lower right")
    ax[0].annotate("±0.1 K target band", xy=(0.985, 0.1), xycoords=("axes fraction", "data"),
                   ha="right", va="bottom", fontsize=8.5, color=OK)

    ax[1].set_ylabel("Heater output  (% of full scale)")
    ax[1].set_xlabel("Time from start of ramp  (minutes)")
    ax[1].set_title("Heater output — the cause is visible here")
    ax[1].set_xlim(0, 22)
    ax[1].legend(loc="upper right")

    fig.savefig(os.path.join(FIGS, "final_fig1_before_after.png"))
    plt.close(fig)
    print("final_fig1_before_after.png")


# --------------------------------------------------------------------------
# FIG 2 - what actually moved the needle
# --------------------------------------------------------------------------
def fig2():
    data = [
        ("P=2   I=18   D=55   rate 1.0", 4.084, BAD, "baseline"),
        ("P=2   I=18   D=80   rate 1.0", 2.300, BAD, "baseline"),
        ("P=2   I=18   D=0    rate 1.0", 2.060, BAD, "baseline"),
        ("P=25  I=900  D=40   rate 1.0", 0.464, MID, "D changed"),
        ("P=25  I=400  D=0    rate 1.0", 0.343, MID, "I changed"),
        ("P=25  I=900  D=0    rate 1.0", 0.326, MID, "reference"),
        ("P=25  I=900  D=0    rate 0.5", 0.301, MID, "rate changed"),
        ("P=40  I=900  D=0    rate 2.0", 0.250, OK, "P changed"),
        ("P=40  I=900  D=0    rate 1.0", 0.222, OK, "P changed"),
    ]
    fig, ax = plt.subplots(figsize=(9.5, 5.6), constrained_layout=True)
    labels = [d[0] for d in data][::-1]
    vals = [d[1] for d in data][::-1]
    cols = [d[2] for d in data][::-1]
    y = range(len(vals))
    ax.barh(list(y), vals, color=cols, height=0.66)
    for i, v in zip(y, vals):
        ax.text(v + 0.06, i, f"{v:+.3f} K", va="center", fontsize=9.5)
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontfamily="monospace", fontsize=9)
    ax.axvline(0.1, color=OK, ls="--", lw=1.6)
    ax.text(0.1, len(vals) - 0.35, "  ±0.1 K target", color=OK, fontsize=9, va="top")
    ax.set_xlabel("Peak overshoot  (K)   — lower is better")
    ax.set_title("Every configuration tested, ~10 K setpoint change")
    ax.set_xlim(0, 4.6)
    ax.grid(axis="y", visible=False)
    fig.savefig(os.path.join(FIGS, "final_fig2_configurations.png"))
    plt.close(fig)
    print("final_fig2_configurations.png")


# --------------------------------------------------------------------------
# FIG 3 - the key discovery: overshoot does not depend on hop size
# --------------------------------------------------------------------------
def fig3():
    fig, ax = plt.subplots(1, 2, figsize=(10.5, 4.6), constrained_layout=True)

    hops = [0.78, 4.76, 9.73]
    peaks = [0.2174, 0.2393, 0.2220]
    ax[0].plot(hops, peaks, "o-", color=OK, ms=10, lw=2)
    for x, y in zip(hops, peaks):
        ax[0].annotate(f"{y:+.3f} K", (x, y), textcoords="offset points",
                       xytext=(0, 14), ha="center", fontsize=9)
    ax[0].axhspan(0, 0.1, color=OK, alpha=0.13)
    ax[0].set_xlabel("Size of setpoint change  (K)")
    ax[0].set_ylabel("Peak overshoot  (K)")
    ax[0].set_title("Overshoot is independent of\nhow far you travel")
    ax[0].set_ylim(0, 0.36)
    ax[0].set_xlim(0, 11)

    rates = [1.0, 2.0]
    rpeaks = [0.222, 0.250]
    ax[1].plot(rates, rpeaks, "s-", color=MID, ms=10, lw=2)
    for x, y in zip(rates, rpeaks):
        ax[1].annotate(f"{y:+.3f} K", (x, y), textcoords="offset points",
                       xytext=(0, 14), ha="center", fontsize=9)
    ax[1].axhspan(0, 0.1, color=OK, alpha=0.13)
    ax[1].set_xlabel("Ramp rate  (K/min)")
    ax[1].set_ylabel("Peak overshoot  (K)")
    ax[1].set_title("…and barely depends on\nramp rate either")
    ax[1].set_ylim(0, 0.36)
    ax[1].set_xlim(0.5, 2.5)

    fig.suptitle("Both plots at P=40, I=900, D=0 — only P changes the outcome",
                 fontsize=11)
    fig.savefig(os.path.join(FIGS, "final_fig3_invariance.png"))
    plt.close(fig)
    print("final_fig3_invariance.png")


# --------------------------------------------------------------------------
# FIG 4 - mechanism: heater vs temperature through the crossing
# --------------------------------------------------------------------------
def fig4():
    fig, ax = plt.subplots(figsize=(9.5, 5.4), constrained_layout=True)

    for fn, idx, tgt, lab, c, hold in [
        ("cryocon_log_20260905_075250_staged.csv", 1, 385.0, "P=25", MID, 11.3),
        ("cryocon_log_20260905_081200_staged.csv", 1, 395.0, "P=40", OK, 12.8),
    ]:
        t, e, h, T = stage(fn, idx)
        x = [temp - tgt for temp in T]
        keep = [(a, b) for a, b in zip(x, h) if -2.0 <= a <= 0.45]
        ax.plot([a for a, _ in keep], [b for _, b in keep], "-", color=c, lw=2.3,
                label=f"{lab}   (peak {'+0.326' if lab=='P=25' else '+0.222'} K)")
        ax.axhline(hold, color=c, ls=":", lw=1.3)

    ax.axvline(0, color="0.25", lw=1.5)
    ax.text(0.02, 0.97, "setpoint reached →", transform=ax.transAxes,
            fontsize=9, va="top", color="0.3")
    ax.set_xlabel("Temperature relative to setpoint  (K)")
    ax.set_ylabel("Heater output  (%)")
    ax.set_title("Why it still overshoots: the heater is above hold power at the crossing\n"
                 "(dotted lines = power needed to simply hold that temperature)")
    ax.set_xlim(-2.0, 0.45)
    ax.legend(loc="lower left")
    fig.savefig(os.path.join(FIGS, "final_fig4_mechanism.png"))
    plt.close(fig)
    print("final_fig4_mechanism.png")


# --------------------------------------------------------------------------
# FIG 5 - the coast test that disproved "heat soak"
# --------------------------------------------------------------------------
def fig5():
    runs = [("327 K", 4.084, 0.009), ("340 K", 2.234, 0.014),
            ("345 K", 1.961, 0.046), ("330 K", 2.411, 0.001),
            ("340 K", 2.300, 0.007)]
    fig, ax = plt.subplots(figsize=(9.5, 5.0), constrained_layout=True)
    x = range(len(runs))
    w = 0.38
    ax.bar([i - w / 2 for i in x], [r[1] for r in runs], w,
           color=BAD, label="Total overshoot")
    ax.bar([i + w / 2 for i in x], [r[2] for r in runs], w,
           color="#8d99ae", label="Further rise after heater reached 0%")
    for i, r in enumerate(runs):
        ax.text(i - w / 2, r[1] + 0.09, f"{r[1]:.2f}", ha="center", fontsize=9)
        ax.text(i + w / 2, r[2] + 0.09, f"{r[2]:.3f}", ha="center", fontsize=8.5)
    ax.set_xticks(list(x))
    ax.set_xticklabels([r[0] for r in runs])
    ax.set_xlabel("Run (setpoint)")
    ax.set_ylabel("Temperature rise  (K)")
    ax.set_title("There is no “heat soak”: once the heater is off, the temperature stops\n"
                 "Overshoot was heat still being applied, not heat arriving late")
    ax.set_ylim(0, 4.8)
    ax.legend(loc="upper right")
    fig.savefig(os.path.join(FIGS, "final_fig5_coast_test.png"))
    plt.close(fig)
    print("final_fig5_coast_test.png")


# --------------------------------------------------------------------------
# FIG 6 - power budget
# --------------------------------------------------------------------------
def fig6():
    pts = [(341.9, 2.75), (346.0, 2.81), (332.0, 1.66),
           (336.7, 1.95), (341.6, 2.19), (346.6, 2.60)]
    m, c = 0.0754, -0.98
    fig, ax = plt.subplots(figsize=(9.5, 5.2), constrained_layout=True)
    ax.plot([p[0] for p in pts], [p[1] for p in pts], "o", color=MID, ms=8,
            label="Measured (passive cooling rate)")
    xs = [300 + i for i in range(0, 161, 5)]
    ax.plot(xs, [m * (x - 297) + c for x in xs], "-", color=MID, lw=1.8,
            label=f"Fit:  {m:.4f}·(T−297) − {abs(c):.2f}  W")
    ax.axvspan(347, 460, color="0.85", alpha=0.5, zorder=0)
    ax.text(404, 1.0, "extrapolated\n(beyond measured data)", ha="center",
            fontsize=9, color="0.35")

    for T, note in ((450, "hold 450 K\n10.6 W = 21% of HI"),):
        ax.plot([T], [m * (T - 297) + c], "*", color=BAD, ms=17, zorder=5)
        ax.annotate(note, (T, m * (T - 297) + c), textcoords="offset points",
                    xytext=(-12, -38), ha="right", fontsize=9, color=BAD)

    ax.set_xlabel("Temperature  (K)")
    ax.set_ylabel("Heat loss to surroundings  (W)")
    ax.set_title("Power budget — why the old 30 % power cap could never reach 450 K\n"
                 "(a 1 K/min ramp at 450 K needs ≈39 % of the HI range)")
    ax.set_xlim(325, 462)
    ax.set_ylim(0, 12.5)
    ax.legend(loc="upper left")
    fig.savefig(os.path.join(FIGS, "final_fig6_power_budget.png"))
    plt.close(fig)
    print("final_fig6_power_budget.png")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.makedirs(FIGS, exist_ok=True)
    fig1(); fig2(); fig3(); fig4(); fig5(); fig6()
    print("\nall figures written")
