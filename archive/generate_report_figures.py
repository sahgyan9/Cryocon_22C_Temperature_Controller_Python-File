"""
Generate all figures for the Cryocon 22C Overshoot Tuning Report
================================================================
Produces:
  1. fig1_overshoot_before_after.png  (Trajectory comparison: old vs new)
  2. fig2_heater_output_vs_time.png   (Heater power dynamics: old saturation vs new proactive taper)
  3. fig3_peak_overshoot_by_config.png (Horizontal bar chart of overshoot progression)
  4. fig4_coast_evidence.png          (Proof disproving 'heat soak': total overshoot vs post-0% climb)
  5. fig5_heat_loss_vs_temperature.png (Passive decay heat loss fit & 450 K power requirement)
  6. fig6_overshoot_vs_jump_size.png  (Staged ramp hops vs overshoot)
"""

import os
import glob
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 14,
    'figure.autolayout': False
})

def load_run(fn):
    t, temp, sp, err, heat = [], [], [], [], []
    with open(fn, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            try:
                el = float(r["Elapsed_Sec"])
                ta = float(r.get("Temp_A_K", r.get("Temp_K", 0)))
                s = float(r.get("Setpoint_K", r.get("Stage_Target_K", 0)))
                h = float(r.get("Heater_Pct", 0))
                e = ta - s
                t.append(el)
                temp.append(ta)
                sp.append(s)
                err.append(e)
                heat.append(h)
            except (ValueError, TypeError, KeyError):
                continue
    return np.array(t), np.array(temp), np.array(sp), np.array(err), np.array(heat)

def make_fig1_and_fig2():
    # Comparison runs
    runs = [
        ("cryocon_log_20260904_172651_pidtune.csv", "Old: P=2, I=18s, D=55, Cap 50%, 2 K/min (327 K)", "#b2182b", "--", 2.0),
        ("cryocon_log_20260904_175131_pidtune.csv", "Old: P=2, I=18s, D=55, Cap 30%, 1 K/min (340 K)", "#d6604d", "--", 2.0),
        ("cryocon_log_20260904_212740_pidtune.csv", "Old: P=2, I=18s, D=80, Cap 30%, 1 K/min (340 K)", "#f4a582", "--", 2.0),
        ("cryocon_log_20260904_214322_pidtune.csv", "Old: P=2, I=18s, D=0,  Cap 30%, 1 K/min (345 K)", "#92c5de", ":", 1.8),
        ("cryocon_log_20260904_215308_pidtune.csv", "New (P-only): P=40, I=0, D=0, Cap 50% (352 K)", "#2166ac", "-", 2.2),
        ("cryocon_log_20260904_220924_pidtune.csv", "New (Optimal): P=25, I=900s, D=0, Cap 50% (357 K)", "#1a9850", "-", 2.5),
    ]

    # --- FIGURE 1: Overshoot Trajectory ---
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    for fn, label, color, ls, lw in runs:
        if not os.path.exists(fn): continue
        t, temp, sp, err, heat = load_run(fn)
        if len(t) == 0: continue
        # Normalize time: align t=0 to when error crossed -1.0 K (or just elapsed time / 60)
        ax1.plot(t / 60.0, err, color=color, linestyle=ls, linewidth=lw, label=label)

    ax1.axhline(0, color="black", linestyle="-", linewidth=1.0, alpha=0.8)
    ax1.axhspan(-0.2, 0.2, color="#4daf4a", alpha=0.18, label="Target Stability Band (±0.2 K)")
    ax1.set_xlabel("Elapsed Time (minutes)", fontweight="bold")
    ax1.set_ylabel("Temperature Error: $T - T_{setpoint}$ (K)", fontweight="bold")
    ax1.set_title("Figure 1: Temperature Trajectory Approach — Before vs. After Tuning", fontweight="bold", pad=12)
    ax1.set_ylim(-6.0, 5.0)
    ax1.set_xlim(0, 16)
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(loc="upper right", framealpha=0.92, fontsize=9)
    fig1.tight_layout()
    fig1.savefig("fig1_overshoot_before_after.png", dpi=160)
    plt.close(fig1)
    print("Wrote fig1_overshoot_before_after.png")

    # --- FIGURE 2: Heater Output vs Time ---
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    for fn, label, color, ls, lw in runs:
        if not os.path.exists(fn): continue
        t, temp, sp, err, heat = load_run(fn)
        if len(t) == 0: continue
        ax2.plot(t / 60.0, heat, color=color, linestyle=ls, linewidth=lw, label=label)

    ax2.set_xlabel("Elapsed Time (minutes)", fontweight="bold")
    ax2.set_ylabel("Heater Output Power (%)", fontweight="bold")
    ax2.set_title("Figure 2: Heater Actuator Dynamics — The Root Mechanism Revealed", fontweight="bold", pad=12)
    ax2.set_ylim(-1, 55)
    ax2.set_xlim(0, 16)
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend(loc="upper right", framealpha=0.92, fontsize=9)
    
    # Annotations explaining mechanism
    ax2.annotate("Old gains hold ~29% power\nwhile ALREADY above setpoint!\n(Unwinding saturated integrator)",
                 xy=(7.2, 28), xytext=(8.5, 38),
                 arrowprops=dict(facecolor="#b2182b", shrink=0.08, width=1.5, headwidth=7),
                 fontsize=9.5, fontweight="bold", color="#b2182b",
                 bbox=dict(boxstyle="round,pad=0.3", fc="#fddbc7", ec="#b2182b", alpha=0.9))

    ax2.annotate("New gains (P=25, I=900s)\nproactively taper to ~6% hold power\nBEFORE setpoint arrival",
                 xy=(5.5, 8.5), xytext=(7.5, 16),
                 arrowprops=dict(facecolor="#1a9850", shrink=0.08, width=1.5, headwidth=7),
                 fontsize=9.5, fontweight="bold", color="#1a9850",
                 bbox=dict(boxstyle="round,pad=0.3", fc="#d9f0d3", ec="#1a9850", alpha=0.9))

    fig2.tight_layout()
    fig2.savefig("fig2_heater_output_vs_time.png", dpi=160)
    plt.close(fig2)
    print("Wrote fig2_heater_output_vs_time.png")

def make_fig3_bar_chart():
    # Peak overshoot across key configurations
    configs = [
        ("327 K (P=2, I=18s, D=55, Cap 50%, 2 K/min)", 4.084, "#b2182b"),
        ("315 K (P=2.02, I=30.4s, D=70, 2 K/min)", 3.695, "#d6604d"),
        ("305 K Baseline (Table 02, 2 K/min)", 3.281, "#e08214"),
        ("330 K (P=2, I=18s, D=80, Cap 30%, 1 K/min)", 2.411, "#f4a582"),
        ("335 K (P=2, I=18s, D=80, Cap 30%, 1 K/min)", 2.329, "#f4a582"),
        ("340 K Clean Start (P=2, I=18s, D=80, Cap 30%)", 2.300, "#f4a582"),
        ("340 K Initial (P=2, I=18s, D=55, Cap 30%)", 2.234, "#fddbc7"),
        ("345 K Zero-D Check (P=2, I=18s, D=0, Cap 30%)", 2.060, "#d1e5f0"),
        ("345 K Climb (P=2, I=18s, D=80, Cap 30%)", 1.961, "#92c5de"),
        ("352 K P-only (P=40, I=0, D=0, Cap 50%)", 0.000, "#2166ac"),
        ("357 K Optimal (P=25, I=900s, D=0, Cap 50%)", 0.000, "#1a9850"),
    ]

    labels = [c[0] for c in configs]
    overshoots = [c[1] for c in configs]
    colors = [c[2] for c in configs]

    fig, ax = plt.subplots(figsize=(10, 6.5))
    y_pos = np.arange(len(labels))
    bars = ax.barh(y_pos, overshoots, color=colors, height=0.65, edgecolor="black", linewidth=0.7)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9.5)
    ax.invert_yaxis()  # Top-down order
    ax.set_xlabel("Peak Temperature Overshoot (K) Above Setpoint", fontweight="bold")
    ax.set_title("Figure 3: Peak Overshoot Progression Across Controller Configurations", fontweight="bold", pad=12)
    ax.grid(axis="x", linestyle="--", alpha=0.5)

    # Add numeric labels to each bar
    for bar, val in zip(bars, overshoots):
        x = bar.get_width()
        if val > 0:
            ax.text(x + 0.08, bar.get_y() + bar.get_height()/2.0, f"+{val:.2f} K",
                    va='center', ha='left', fontsize=9.5, fontweight="bold")
        else:
            ax.text(0.08, bar.get_y() + bar.get_height()/2.0, "0.00 K (Zero Overshoot)",
                    va='center', ha='left', fontsize=9.5, fontweight="bold", color="#1a9850")

    ax.set_xlim(0, 4.8)
    fig.tight_layout()
    fig.savefig("fig3_peak_overshoot_by_config.png", dpi=160)
    plt.close(fig)
    print("Wrote fig3_peak_overshoot_by_config.png")

def make_fig4_coast_evidence():
    # Disproving 'heat soak'
    runs = [
        ("Run 172651 (327 K)", 4.084, 0.009),
        ("Run 201855 (330 K)", 2.411, 0.001),
        ("Run 212740 (340 K)", 2.300, 0.007),
        ("Run 175131 (340 K)", 2.234, 0.014),
        ("Run 181410 (345 K)", 1.961, 0.046),
        ("Run 164857 (305 K)", 3.281, 0.029),
    ]

    labels = [r[0] for r in runs]
    total_over = [r[1] for r in runs]
    post_zero = [r[2] for r in runs]

    x = np.arange(len(labels))
    width = 0.38

    fig, ax = plt.subplots(figsize=(10, 5.8))
    rects1 = ax.bar(x - width/2, total_over, width, label='Total Overshoot Above Setpoint',
                    color='#d6604d', edgecolor='black', linewidth=0.7)
    rects2 = ax.bar(x + width/2, post_zero, width, label='Further Temp Rise After Heater Reached 0% Power',
                    color='#4393c3', edgecolor='black', linewidth=0.7)

    ax.set_ylabel('Temperature Rise (K)', fontweight='bold')
    ax.set_title("Figure 4: The 'Coast' Evidence — Disproving the 'Heat Soak' Hypothesis", fontweight='bold', pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=15, ha="right", fontsize=9.5)
    ax.legend(loc='upper right', framealpha=0.95)
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    # Add text labels on top of bars
    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f'+{h:.2f} K', xy=(rect.get_x() + rect.get_width()/2, h),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom',
                    fontsize=9, fontweight='bold')

    for rect in rects2:
        h = rect.get_height()
        ax.annotate(f'+{h:.3f} K', xy=(rect.get_x() + rect.get_width()/2, h),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom',
                    fontsize=9, fontweight='bold', color='#2166ac')

    ax.set_ylim(0, 4.8)
    
    # Text explanation box
    text_box = (
        "Physical Fact: When heater power reaches 0%, temperature rises only +0.001 to +0.046 K.\n"
        "Thermal lag (dead time) is only ~20 s. Overshoot is caused by the heater remaining ON\n"
        "at 25–29% while ALREADY above setpoint (due to integral windup), NOT stored heat soaking in."
    )
    ax.text(0.5, 0.72, text_box, transform=ax.transAxes, ha='center', va='center',
            fontsize=9.5, bbox=dict(boxstyle='round,pad=0.5', fc='#f7f7f7', ec='#999999', alpha=0.9))

    fig.tight_layout()
    fig.savefig("fig4_coast_evidence.png", dpi=160)
    plt.close(fig)
    print("Wrote fig4_coast_evidence.png")

def make_fig5_heat_loss():
    # Heat loss measurements from passive decay tails
    # Data: (Temp_K, Rate_K_min, Ploss_W)
    tail_data = [
        (308.23, 0.082, 0.71),
        (330.07, 0.216, 1.87),
        (331.38, 0.177, 1.53),
        (331.97, 0.180, 1.56),
        (336.73, 0.213, 1.85),
        (340.30, 0.282, 2.44),
        (341.56, 0.239, 2.07),
        (341.89, 0.299, 2.59),
        (346.02, 0.307, 2.66),
        (346.64, 0.284, 2.46)
    ]

    temps = np.array([d[0] for d in tail_data])
    ploss = np.array([d[2] for d in tail_data])

    # Linear fit: Ploss = a * (T - 297) + b
    p_fit = np.polyfit(temps - 297.0, ploss, 1) # [slope, intercept]
    a, b = p_fit[0], p_fit[1] # approx 0.0754 and -0.98

    t_extrap = np.linspace(295, 460, 100)
    ploss_extrap = a * (t_extrap - 297.0) + b
    
    # Power needed for 1.0 K/min ramp: P_ramp = C * (1 K / 60 s) = 520 / 60 = 8.67 W
    p_ramp = 520.0 / 60.0
    ptotal_extrap = ploss_extrap + p_ramp

    # Convert to % of HI range (50 W full scale)
    pct_hold = (ploss_extrap / 50.0) * 100.0
    pct_ramp = (ptotal_extrap / 50.0) * 100.0

    fig, ax1 = plt.subplots(figsize=(10, 6.2))
    ax2 = ax1.twinx()

    # Scatter of measured data
    ax1.scatter(temps, ploss, color="#b2182b", s=60, zorder=5, label="Measured Passive Decay ($C = 520$ J/K)")
    
    # Fitted curves
    ax1.plot(t_extrap, ploss_extrap, color="#2166ac", linestyle="--", linewidth=2.0,
             label=f"Holding Loss Fit: $P_{{loss}} = {a:.4f}(T - 297) {b:+.2f}$ W")
    ax1.plot(t_extrap, ptotal_extrap, color="#1a9850", linestyle="-", linewidth=2.2,
             label=f"Total Power for 1.0 K/min Ramp ($P_{{loss}} + 8.67$ W)")

    # Horizontal cap lines
    ax1.axhline(15.0, color="#d95f02", linestyle=":", linewidth=2.0, label="Old MAXPWR = 30% Cap (15.0 W)")
    ax1.axhline(35.0, color="#7570b3", linestyle=":", linewidth=2.0, label="Recommended MAXPWR = 70% Cap (35.0 W)")

    ax1.set_xlabel("Sample Stage Temperature (K)", fontweight="bold")
    ax1.set_ylabel("Heater Power (Watts)", fontweight="bold")
    ax2.set_ylabel("Equivalent Heater Output (% of HI Range 50 W)", fontweight="bold", color="#555555")

    ax1.set_xlim(295, 460)
    ax1.set_ylim(0, 42)
    ax2.set_ylim(0, 42 / 50.0 * 100.0)

    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(loc="upper left", framealpha=0.92, fontsize=9.5)
    ax1.set_title("Figure 5: Probe Station Heat Loss & Actuator Power Requirement vs. Temperature",
                  fontweight="bold", pad=12)

    # Annotate 450 K requirement
    p_450_hold = a * (450 - 297) + b
    p_450_ramp = p_450_hold + p_ramp
    pct_450_hold = p_450_hold / 50.0 * 100.0
    pct_450_ramp = p_450_ramp / 50.0 * 100.0

    ax1.plot([450, 450], [0, p_450_ramp], color="gray", linestyle="--", linewidth=1.0)
    ax1.annotate(f"At Target 450 K:\n• Hold power: {p_450_hold:.1f} W ({pct_450_hold:.1f}%)\n• 1 K/min ramp: {p_450_ramp:.1f} W ({pct_450_ramp:.1f}%)\n★ Old 30% cap (15 W) IMPOSSIBLE!",
                 xy=(450, p_450_ramp), xytext=(365, 27),
                 arrowprops=dict(facecolor="black", shrink=0.08, width=1.2, headwidth=6),
                 fontsize=9.5, fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.4", fc="#ffffbf", ec="#d95f02", linewidth=1.5, alpha=0.95))

    fig.tight_layout()
    fig.savefig("fig5_heat_loss_vs_temperature.png", dpi=160)
    plt.close(fig)
    print("Wrote fig5_heat_loss_vs_temperature.png")

def make_fig6_staged(latest_staged_csv=None):
    # Check if a staged run exists
    staged_files = sorted(glob.glob("cryocon_log_*_staged.csv"))
    if not staged_files:
        print("No staged files found yet.")
        return

    # If user provided a specific file or we pick the most complete one
    fn = latest_staged_csv if latest_staged_csv else staged_files[-1]
    print(f"Plotting staged data from: {fn}")

    # Parse stages
    stages = {}
    with open(fn, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            try:
                s_idx = int(r["Stage_Idx"])
                el = float(r["Elapsed_Sec"])
                ta = float(r["Temp_A_K"])
                tg = float(r["Stage_Target_K"])
                err = float(r["Error_K"])
                ht = float(r["Heater_Pct"])
                phase = r.get("Phase", "")
                if s_idx not in stages:
                    stages[s_idx] = {"target": tg, "t": [], "temp": [], "err": [], "heat": [], "phase": []}
                stages[s_idx]["t"].append(el)
                stages[s_idx]["temp"].append(ta)
                stages[s_idx]["err"].append(err)
                stages[s_idx]["heat"].append(ht)
                stages[s_idx]["phase"].append(phase)
            except Exception:
                continue

    if not stages:
        return

    # Extract jump sizes and peak overshoots
    jumps = []
    peak_overs = []
    targets = []
    stage_nums = []

    last_end_temp = None
    for s_idx in sorted(stages.keys()):
        s = stages[s_idx]
        if len(s["temp"]) < 5: continue
        tg = s["target"]
        start_t = s["temp"][0] if last_end_temp is None else last_end_temp
        jump = tg - start_t
        last_end_temp = s["temp"][-1]
        
        # Max overshoot is peak temperature minus target
        max_t = max(s["temp"])
        over = max(0.0, max_t - tg)
        
        # Check if first stage was contaminated
        is_contaminated = (s_idx == 1 and "224006" in fn)
        
        jumps.append((jump, over, tg, s_idx, is_contaminated))

    fig, ax = plt.subplots(figsize=(9, 5.5))
    clean_jumps = [j[0] for j in jumps if not j[4]]
    clean_overs = [j[1] for j in jumps if not j[4]]
    clean_targs = [f"Stage {j[3]} ({j[2]:.0f}K)" for j in jumps if not j[4]]

    contam_jumps = [j[0] for j in jumps if j[4]]
    contam_overs = [j[1] for j in jumps if j[4]]

    if clean_jumps:
        ax.scatter(clean_jumps, clean_overs, color="#1a9850", s=90, zorder=5, label="Verified Staged Runs (P=25, I=900, D=0)")
        for x, y, lbl in zip(clean_jumps, clean_overs, clean_targs):
            ax.annotate(f"{lbl}\n{y:+.3f} K", (x, y), xytext=(0, 10), textcoords="offset points",
                        ha='center', fontsize=9, fontweight="bold", color="#1a9850")

    if contam_jumps:
        ax.scatter(contam_jumps, contam_overs, color="#d6604d", s=90, marker="x", zorder=5,
                   label="Contaminated Stage (Pre-loaded integrator from abort)")
        ax.annotate("Contaminated\n(+0.288 K)", (contam_jumps[0], contam_overs[0]), xytext=(15, -10),
                    textcoords="offset points", fontsize=8.5, color="#b2182b", fontweight="bold")

    # Linear model prediction line: over ~ 0.015 * jump
    x_line = np.linspace(0, 35, 50)
    ax.plot(x_line, 0.018 * x_line, linestyle="--", color="#2166ac", label="Theoretical Model Upper Bound ($< 0.6$ K at 30 K hop)")
    ax.axhspan(0, 0.2, color="#4daf4a", alpha=0.15, label="Target Stability Band (±0.2 K)")

    ax.set_xlabel("Setpoint Jump Size $\Delta T$ (K)", fontweight="bold")
    ax.set_ylabel("Peak Overshoot Above Setpoint (K)", fontweight="bold")
    ax.set_title("Figure 6: Temperature Overshoot vs. Setpoint Jump Size (Staged Campaign)", fontweight="bold", pad=12)
    ax.set_xlim(0, 35)
    ax.set_ylim(-0.05, 1.0)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper left", framealpha=0.92, fontsize=9.5)

    fig.tight_layout()
    fig.savefig("fig6_overshoot_vs_jump_size.png", dpi=160)
    plt.close(fig)
    print("Wrote fig6_overshoot_vs_jump_size.png")

if __name__ == "__main__":
    make_fig1_and_fig2()
    make_fig3_bar_chart()
    make_fig4_coast_evidence()
    make_fig5_heat_loss()
    make_fig6_staged()
    print("All figures successfully generated.")
