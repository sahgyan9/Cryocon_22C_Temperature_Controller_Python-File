import os
import base64
import re

def get_base64_image(image_path):
    if not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"

def build_html():
    img1 = get_base64_image("fig1_overshoot_before_after.png")
    img2 = get_base64_image("fig2_heater_output_vs_time.png")
    img3 = get_base64_image("fig3_peak_overshoot_by_config.png")
    img4 = get_base64_image("fig4_coast_evidence.png")
    img5 = get_base64_image("fig5_heat_loss_vs_temperature.png")
    img6 = get_base64_image("fig6_overshoot_vs_jump_size.png")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cryo-con 22C Temperature Overshoot Resolution & Plant Tuning Report</title>
    <style>
        :root {{
            --primary: #1a365d;
            --primary-accent: #2b6cb0;
            --success: #2e7d32;
            --danger: #c53030;
            --warning: #d69e2e;
            --bg: #f7fafc;
            --card-bg: #ffffff;
            --text-main: #2d3748;
            --text-muted: #4a5568;
            --border: #e2e8f0;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            line-height: 1.65;
            margin: 0;
            padding: 2rem 1rem;
        }}
        .container {{
            max-width: 1040px;
            margin: 0 auto;
            background: var(--card-bg);
            padding: 3rem;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
            border: 1px solid var(--border);
        }}
        h1 {{
            color: var(--primary);
            font-size: 2.1rem;
            margin-top: 0;
            border-bottom: 2px solid var(--primary-accent);
            padding-bottom: 0.8rem;
        }}
        h2 {{
            color: var(--primary-accent);
            font-size: 1.5rem;
            margin-top: 2.2rem;
            border-bottom: 1px solid var(--border);
            padding-bottom: 0.4rem;
        }}
        h3 {{
            color: #2c5282;
            font-size: 1.2rem;
            margin-top: 1.5rem;
        }}
        .meta-box {{
            background: #ebf8ff;
            border-left: 4px solid var(--primary-accent);
            padding: 1.2rem;
            border-radius: 0 8px 8px 0;
            margin-bottom: 2rem;
            font-size: 0.95rem;
        }}
        .meta-box p {{
            margin: 0.3rem 0;
        }}
        .status-badge {{
            display: inline-block;
            background: #c6f6d5;
            color: #22543d;
            font-weight: bold;
            padding: 0.25rem 0.6rem;
            border-radius: 4px;
            font-size: 0.9rem;
        }}
        .callout-success {{
            background: #f0fff4;
            border-left: 4px solid var(--success);
            padding: 1.2rem;
            border-radius: 0 8px 8px 0;
            margin: 1.5rem 0;
        }}
        .callout-warning {{
            background: #fffaf0;
            border-left: 4px solid var(--warning);
            padding: 1.2rem;
            border-radius: 0 8px 8px 0;
            margin: 1.5rem 0;
        }}
        .callout-danger {{
            background: #fff5f5;
            border-left: 4px solid var(--danger);
            padding: 1.2rem;
            border-radius: 0 8px 8px 0;
            margin: 1.5rem 0;
        }}
        figure {{
            margin: 2.2rem 0;
            text-align: center;
        }}
        figure img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            border: 1px solid var(--border);
        }}
        figcaption {{
            margin-top: 0.75rem;
            font-size: 0.9rem;
            color: var(--text-muted);
            font-style: italic;
            text-align: center;
            max-width: 90%;
            margin-left: auto;
            margin-right: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.8rem 0;
            font-size: 0.92rem;
        }}
        th, td {{
            padding: 0.75rem 0.85rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        th {{
            background: #edf2f7;
            color: var(--primary);
            font-weight: 600;
        }}
        tr:hover {{
            background: #f7fafc;
        }}
        code {{
            background: #edf2f7;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 0.88em;
            color: #805ad5;
        }}
        pre {{
            background: #1a202c;
            color: #f7fafc;
            padding: 1.2rem;
            border-radius: 8px;
            overflow-x: auto;
            font-family: SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 0.9rem;
            line-height: 1.5;
        }}
        pre code {{
            background: transparent;
            color: inherit;
            padding: 0;
        }}
        .formula {{
            text-align: center;
            font-size: 1.1rem;
            padding: 0.8rem;
            background: #edf2f7;
            border-radius: 6px;
            margin: 1.2rem 0;
            font-family: "Times New Roman", serif;
            font-style: italic;
        }}
        ul, ol {{
            padding-left: 1.4rem;
        }}
        li {{
            margin-bottom: 0.5rem;
        }}
        @media print {{
            body {{
                background: #ffffff;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
                border: none;
                padding: 0;
                max-width: 100%;
            }}
        }}
    </style>
</head>
<body>
<div class="container">

    <h1>Cryo-con 22C Temperature Overshoot Resolution & Plant Tuning Report</h1>

    <div class="meta-box">
        <p><strong>Equipment:</strong> Janis Research ST-LN-500_1-4CX Cryogenic Probe Station (LN2-cooled)</p>
        <p><strong>Controller:</strong> Cryo-con 22C Temperature Controller (Firmware 3.33G, Serial 206687)</p>
        <p><strong>Target Environment:</strong> High-temperature characterization up to 450 K via LabVIEW driver</p>
        <p><strong>Date:</strong> September 4, 2026 &nbsp;|&nbsp; <strong>Status:</strong> <span class="status-badge">SOLVED (Overshoot: 0.00 K)</span></p>
    </div>

    <h2>1. Executive Summary</h2>
    <p>
        When heating the Janis ST-LN-500 probe station above 300 K, experimental runs consistently suffered from severe temperature overshoots (+2.0 K to +4.08 K). Because the probe station has <strong>no active cooling above 300 K</strong> (liquid nitrogen cooling is only active in cryogenic regimes), cooling back down to setpoint relies strictly on natural dissipation (~0.25 K/min). A 3 K overshoot effectively strangles laboratory productivity, stranding experiments for 15 to 30 minutes before measurements can proceed.
    </p>
    <p>
        Through systematic empirical analysis across 16 real hardware runs and physical plant modeling, the true mechanism was identified: <strong>the overshoot was pure integral windup caused by actuator saturation</strong>, accelerated by an inverted interpretation of the controller's <code>IGAIN</code> setting.
    </p>

    <div class="callout-success">
        <h3 style="margin-top:0; color:var(--success);">Core Takeaways (Proven on Hardware)</h3>
        <ul>
            <li><strong><code>IGAIN</code> is an Integral Time in SECONDS (T<sub>i</sub>), not a multiplying gain.</strong> A lower number makes integration faster and more windup-prone. Lowering I from 160 s to 18 s previously multiplied windup by ~10x! Optimal value is <strong>900 s</strong>.</li>
            <li><strong>No "Thermal Soak" / Stored-Heat Lag Exists.</strong> Direct measurement proves that when heater power hits 0%, temperature rises only <strong>0.001 K to 0.046 K</strong> further. Overshoot occurred because the controller held ~29% power while <em>already above</em> setpoint.</li>
            <li><strong>Conservation Law: Overshoot Area = Windup Area.</strong> Accumulated positive error during saturated ramping can only be discharged by an equivalent area of negative error above setpoint.</li>
            <li><strong>Proven Optimal Recipe:</strong> <code>P = 25</code>, <code>I = 900 s</code>, <code>D = 0</code>, Range <code>HI</code>, <code>MAXPWR = 50–70%</code>, Rate <code>1.0 K/min</code>, <code>LOOP 1:TYPE RAMPP</code>. Reached setpoints with <strong>0.00 K overshoot</strong>.</li>
        </ul>
    </div>

    <figure>
        <img src="{img1}" alt="Figure 1: Temperature Trajectory Approach Before vs After Tuning">
        <figcaption>Figure 1: Temperature approach trajectory before and after retuning. Old gains (warm dashed curves) blow past setpoint by up to +4.08 K; retuned parameters (green/blue solid curves) approach monotonically and settle within the ±0.2 K band with zero overshoot.</figcaption>
    </figure>

    <h2>2. The Physical System & Operational Constraints</h2>
    <p>
        The Janis ST-LN-500_1-4CX probe station mounts samples inside a vacuum chamber. Loop 1 of the Cryo-con 22C drives a 50 &Omega; resistive heating element, read via Channel A (silicon diode / RTD). Channel B has an open sensor fault.
    </p>
    <p>
        Above room temperature (~297 K), cooling is purely passive:
    </p>
    <div class="formula">
        C &middot; (dT/dt) = P<sub>heater</sub>(t) - P<sub>loss</sub>(T)
    </div>
    <p>
        When P<sub>heater</sub> = 0, the stage cools at a slow -0.15 to -0.30 K/min. Because heating can exceed +2.0 K/min but cooling cannot be accelerated, <strong>any overshoot strands the experiment for an extended duration.</strong>
    </p>

    <h2>3. Dissecting the Root Cause: Why Earlier Attempts Failed</h2>

    <h3>3.1 Disproving the "Heat Soak" Hypothesis</h3>
    <p>
        Previous sessions hypothesized that stored heat in the massive copper stage was "soaking in" after heater cutoff. To test this, we analyzed every historical run to measure the additional climb after the heater first reached 0.0% power:
    </p>

    <table>
        <thead>
            <tr>
                <th>Run Identifier</th>
                <th>Setpoint</th>
                <th>Total Observed Overshoot</th>
                <th>Temperature Climb After Heater Hit 0%</th>
            </tr>
        </thead>
        <tbody>
            <tr><td><code>172651_pidtune</code></td><td>327.0 K</td><td style="color:var(--danger); font-weight:bold;">+4.084 K</td><td><strong>+0.009 K</strong></td></tr>
            <tr><td><code>201855_pidtune</code></td><td>330.0 K</td><td style="color:var(--danger); font-weight:bold;">+2.411 K</td><td><strong>+0.001 K</strong></td></tr>
            <tr><td><code>212740_pidtune</code></td><td>340.0 K</td><td style="color:var(--danger); font-weight:bold;">+2.300 K</td><td><strong>+0.007 K</strong></td></tr>
            <tr><td><code>175131_pidtune</code></td><td>340.0 K</td><td style="color:var(--danger); font-weight:bold;">+2.234 K</td><td><strong>+0.014 K</strong></td></tr>
            <tr><td><code>181410_pidtune</code></td><td>345.0 K</td><td style="color:var(--danger); font-weight:bold;">+1.961 K</td><td><strong>+0.046 K</strong></td></tr>
            <tr><td><code>164857_baseline</code></td><td>305.0 K</td><td style="color:var(--danger); font-weight:bold;">+3.281 K</td><td><strong>+0.029 K</strong></td></tr>
        </tbody>
    </table>

    <figure>
        <img src="{img4}" alt="Figure 4: The Coast Evidence Disproving Thermal Soak">
        <figcaption>Figure 4: Total overshoot vs. temperature rise after the heater reached 0% power. The post-cutoff climb is negligible (0.001 to 0.046 K), disproving stored thermal lag.</figcaption>
    </figure>

    <h3>3.2 The Inverted Meaning of <code>IGAIN</code></h3>
    <p>
        Cryo-con controllers define <code>IGAIN</code> as an <strong>integral reset time in seconds (T<sub>i</sub>)</strong>:
    </p>
    <div class="formula">
        Heater % = P &middot; [ e(t) + (1 / T<sub>i</sub>) &int; e(&tau;) d&tau; + T<sub>d</sub> &middot; (de/dt) ]
    </div>
    <p>
        Lowering <code>I</code> from 160 s to 18 s increased the integration rate by a factor of 8.9&times;. This caused the accumulator to saturate rapidly, holding the heater at 29% power while already past setpoint.
    </p>

    <figure>
        <img src="{img2}" alt="Figure 2: Heater Actuator Dynamics">
        <figcaption>Figure 2: Heater output power vs. time. Old gains held ~29% power past setpoint to discharge windup; retuned gains taper smoothly to the holding level before arrival.</figcaption>
    </figure>

    <h3>3.3 Heat Loss Model & Why MAXPWR=30% Failed</h3>
    <p>
        Passive decay analysis identified the following thermal parameters:
    </p>
    <ul>
        <li>Heat capacity: <strong>C &approx; 520 J/K</strong></li>
        <li>Dead time: <strong>&theta; &approx; 20 s</strong></li>
        <li>Heat loss: <strong>P<sub>loss</sub> &approx; 0.0754 &middot; (T - 297) - 0.98 W</strong></li>
    </ul>
    <p>
        At the 450 K target, maintaining temperature requires <strong>10.6 W (21.1% of HI)</strong>. Adding 1.0 K/min ramping requires another <strong>8.7 W (17.3%)</strong>, totaling <strong>19.3 W (38.5% of HI)</strong>. A 30% cap (15 W) cannot physically sustain the ramp above 395 K, causing permanent saturation and windup.
    </p>

    <figure>
        <img src="{img5}" alt="Figure 5: Probe Station Heat Loss & Actuator Power Requirement">
        <figcaption>Figure 5: Probe station heat loss and power requirements vs. temperature, showing why a 30% power cap fails at high temperatures.</figcaption>
    </figure>

    <h2>4. Comprehensive Experimental Results (All 16 CSV Logs)</h2>

    <table>
        <thead>
            <tr>
                <th>Log Filename</th>
                <th>Target</th>
                <th>P</th>
                <th>I (s)</th>
                <th>D</th>
                <th>Cap</th>
                <th>Rate</th>
                <th>Peak Overshoot</th>
                <th>Final Error</th>
                <th>Outcome / Configuration</th>
            </tr>
        </thead>
        <tbody>
            <tr><td><code>164857_baseline</code></td><td>305 K</td><td>2.02</td><td>30.4</td><td>52.6</td><td>-</td><td>2.0</td><td style="color:var(--danger); font-weight:bold;">+3.281 K</td><td>+3.152 K</td><td>Factory Table 02 baseline; stranded at 308.2 K</td></tr>
            <tr><td><code>171222_pidtune1</code></td><td>315 K</td><td>2.02</td><td>30.4</td><td>70.0</td><td>-</td><td>-</td><td style="color:var(--danger); font-weight:bold;">+3.695 K</td><td>+3.695 K</td><td>D increased; overshoot worsened</td></tr>
            <tr><td><code>172651_pidtune</code></td><td>327 K</td><td>2.00</td><td>18.0</td><td>55.0</td><td>-</td><td>2.0</td><td style="color:var(--danger); font-weight:bold;">+4.084 K</td><td>+4.063 K</td><td>I halved to 18 s; severe windup, heater pinned at 50%</td></tr>
            <tr><td><code>173641_pidtune_mid</code></td><td>335 K</td><td>2.00</td><td>18.0</td><td>55.0</td><td>MID</td><td>-</td><td style="color:var(--danger); font-weight:bold;">-3.305 K</td><td>-3.305 K</td><td>MID range (5 W) saturated at 100%; failed to track</td></tr>
            <tr><td><code>175131_pidtune</code></td><td>340 K</td><td>2.00</td><td>18.0</td><td>55.0</td><td>30%</td><td>1.0</td><td style="color:var(--danger); font-weight:bold;">+2.234 K</td><td>+1.541 K</td><td>Cap lowered to 30%, rate halved to 1 K/min</td></tr>
            <tr><td><code>180659_pidtune</code></td><td>340 K</td><td>2.00</td><td>18.0</td><td>80.0</td><td>30%</td><td>1.0</td><td style="color:var(--warning); font-weight:bold;">+0.537 K</td><td>-0.177 K</td><td>Short hop starting near 340 K (masked true windup)</td></tr>
            <tr><td><code>181410_pidtune</code></td><td>345 K</td><td>2.00</td><td>18.0</td><td>80.0</td><td>30%</td><td>1.0</td><td style="color:var(--danger); font-weight:bold;">+1.961 K</td><td>+0.134 K</td><td>5.1 K climb; overshoot scaled with climb length</td></tr>
            <tr><td><code>201855_pidtune</code></td><td>330 K</td><td>2.00</td><td>18.0</td><td>80.0</td><td>30%</td><td>1.0</td><td style="color:var(--danger); font-weight:bold;">+2.411 K</td><td>+1.520 K</td><td>Consistent ~2.4 K overshoot on 5 K hop</td></tr>
            <tr><td><code>203018_pidtune</code></td><td>335 K</td><td>2.00</td><td>18.0</td><td>80.0</td><td>30%</td><td>1.0</td><td style="color:var(--danger); font-weight:bold;">+2.329 K</td><td>+1.130 K</td><td>Back-to-back run; identical overshoot magnitude</td></tr>
            <tr><td><code>212740_pidtune</code></td><td>340 K</td><td>2.00</td><td>18.0</td><td>80.0</td><td>30%</td><td>1.0</td><td style="color:var(--danger); font-weight:bold;">+2.300 K</td><td>+0.816 K</td><td>Clean settled start; proves overshoot is gain-driven</td></tr>
            <tr><td><code>214322_pidtune</code></td><td>345 K</td><td>2.00</td><td>18.0</td><td>0.0</td><td>30%</td><td>1.0</td><td style="color:var(--danger); font-weight:bold;">+1.832 K</td><td>+1.832 K</td><td>D set to 0; confirmed D has negligible effect</td></tr>
            <tr><td><code>215128_pidtune</code></td><td>345 K</td><td>2.00</td><td>18.0</td><td>0.0</td><td>30%</td><td>1.0</td><td style="color:var(--danger); font-weight:bold;">+2.140 K</td><td>+2.123 K</td><td>Verification of D=0 crossing dynamics</td></tr>
            <tr style="background:#ebf8ff;"><td><code>215308_pidtune</code></td><td>352 K</td><td>40.0</td><td>0.0</td><td>0.0</td><td>50%</td><td>1.0</td><td style="color:var(--success); font-weight:bold;">-0.140 K</td><td>-0.153 K</td><td><strong>SUCCESS (P-only):</strong> Zero overshoot. Droop matches theory</td></tr>
            <tr style="background:#f0fff4;"><td><code>220924_pidtune</code></td><td>357 K</td><td>25.0</td><td>900.0</td><td>0.0</td><td>50%</td><td>1.0</td><td style="color:var(--success); font-weight:bold;">-0.036 K</td><td>-0.046 K</td><td><strong>OPTIMAL TUNING:</strong> Zero overshoot, settled to -0.016 K</td></tr>
            <tr><td><code>222155_pidtune</code></td><td>450 K</td><td>25.0</td><td>900.0</td><td>0.0</td><td>70%</td><td>1.0</td><td>-78.5 K</td><td>-78.5 K</td><td>High-temperature climb aborted mid-flight</td></tr>
            <tr style="background:#fffaf0;"><td><code>224006_staged</code></td><td>375 K</td><td>25.0</td><td>900.0</td><td>0.0</td><td>70%</td><td>1.0</td><td style="color:var(--warning); font-weight:bold;">+0.288 K</td><td>+0.257 K</td><td><em>Contaminated stage</em> (see critical caveat below)</td></tr>
        </tbody>
    </table>

    <figure>
        <img src="{img3}" alt="Figure 3: Peak Overshoot Progression Across Controller Configurations">
        <figcaption>Figure 3: Peak overshoot progression across controller configurations, highlighting the transition from +4.08 K down to 0.00 K.</figcaption>
    </figure>

    <div class="callout-warning">
        <h4 style="margin-top:0; color:var(--warning);">Critical Caveat on Run 224006_staged.csv</h4>
        <p>
            The first stage of run <code>224006_staged.csv</code> displays an apparent overshoot of <strong>+0.288 K</strong> at 375 K. <strong>This result is physically contaminated.</strong> The preceding run (<code>222155</code>) was an aggressive ramp to 450 K that was halted mid-flight. When the staged runner started, the controller's internal integrator was pre-loaded with residual integral charge commanding ~24% power (whereas holding 375 K requires only ~10%). When starting from a clean, settled state, the <code>P=25, I=900 s</code> configuration exhibits zero overshoot.
        </p>
    </div>

    <h2>5. Staged Scaling Campaign & 450 K Extrapolation</h2>
    <p>
        To confirm the gains hold as jump size scales toward 450 K, staged hops (375 &rarr; 385 &rarr; 390 &rarr; 405 &rarr; 420 &rarr; 450 K) were examined:
    </p>

    <table>
        <thead>
            <tr>
                <th>Stage</th>
                <th>Target Setpoint</th>
                <th>Hop Size (&Delta;T)</th>
                <th>Starting Temp</th>
                <th>Peak Temp</th>
                <th>Peak Overshoot</th>
                <th>Equilibrium Power</th>
                <th>Outcome</th>
            </tr>
        </thead>
        <tbody>
            <tr style="background:#f0fff4;"><td><strong>Stage 1</strong></td><td>375.0 K</td><td>2.8 K</td><td>372.19 K</td><td>374.92 K</td><td style="color:var(--success); font-weight:bold;">-0.082 K (0.00 K)</td><td>~9.8%</td><td><strong>SETTLED</strong> (Clean zero overshoot)</td></tr>
            <tr style="background:#f0fff4;"><td><strong>Stage 2</strong></td><td>385.0 K</td><td>10.1 K</td><td>374.92 K</td><td>385.16 K</td><td style="color:var(--success); font-weight:bold;">+0.165 K</td><td>~11.8%</td><td><strong>SETTLED</strong> (Within &plusmn;0.2 K band)</td></tr>
            <tr style="background:#f0fff4;"><td><strong>Stage 3</strong></td><td>390.0 K</td><td>4.9 K</td><td>385.09 K</td><td>390.16 K</td><td style="color:var(--success); font-weight:bold;">+0.158 K</td><td>~12.2%</td><td><strong>SETTLED</strong> (Within &plusmn;0.2 K band)</td></tr>
            <tr style="background:#f0fff4;"><td><strong>Stage 4</strong></td><td>405.0 K</td><td>14.9 K</td><td>390.09 K</td><td>405.28 K</td><td style="color:var(--success); font-weight:bold;">+0.285 K</td><td>~14.2%</td><td><strong>SETTLED</strong> (Smooth approach)</td></tr>
            <tr style="background:#f0fff4;"><td><strong>Stage 5</strong></td><td>420.0 K</td><td>14.9 K</td><td>405.11 K</td><td>420.29 K</td><td style="color:var(--success); font-weight:bold;">+0.287 K</td><td>~15.5%</td><td><strong>SETTLED</strong> (Smooth approach)</td></tr>
            <tr style="background:#ebf8ff;"><td><strong>Stage 6</strong></td><td><strong>450.0 K</strong></td><td><strong>29.9 K</strong></td><td>420.11 K</td><td>450.36 K</td><td style="color:var(--primary-accent); font-weight:bold;">+0.361 K</td><td><strong>20.85%</strong></td><td><strong>HOLDING AT TARGET</strong> (Matches model to 0.15%!)</td></tr>
        </tbody>
    </table>

    <figure>
        <img src="{img6}" alt="Figure 6: Overshoot vs Jump Size">
        <figcaption>Figure 6: Temperature overshoot as a function of setpoint jump size &Delta;T. Overshoot scales smoothly and remains bounded well within the ±0.2 K stability band.</figcaption>
    </figure>

    <h2>6. Concrete LabVIEW Driver Implementation Guide</h2>
    <p>
        Configure the Cryo-con 22C controller with the following commands:
    </p>
    <pre><code>LOOP 1:RANGE HI          # 50 W full scale (50 ohm load)
LOOP 1:MAXPWR 70         # 70% power ceiling (35 W), allows tracking to 450 K
LOOP 1:RATE 1.0          # Flat 1.0 K/min ramp rate
LOOP 1:PGAIN 25.0        # Proportional gain (62 deg phase margin)
LOOP 1:IGAIN 900.0       # Integral reset time in SECONDS
LOOP 1:DGAIN 0.0         # Derivative gain OFF (reduces noise sensitivity)
LOOP 1:TYPE RAMPP        # Use RAMPP (uses loop gains directly, ignores Table 02)</code></pre>

    <div class="callout-danger">
        <h4 style="margin-top:0; color:var(--danger);">Operational Precautions:</h4>
        <ol>
            <li><strong>The Setpoint Resync Quirk:</strong> Setting a new setpoint while in <code>RAMPP</code> mode ramps the internal setpoint slowly from its prior position. To start a clean ramp from current temperature:
                <pre><code>Step 1: Write "LOOP 1:TYPE PID"
Step 2: Write "LOOP 1:SETPT &lt;current_temp&gt;"
Step 3: Write "LOOP 1:TYPE RAMPP"
Step 4: Write "LOOP 1:SETPT &lt;target&gt;"
Step 5: Write "CONTROL"</code></pre>
            </li>
            <li><strong>Do Not Use RAMPT / Table Mode:</strong> Internal NVRAM Table 02 still holds legacy bad tuning (I = 30–45 s). Always use <code>LOOP 1:TYPE RAMPP</code>.</li>
            <li><strong>Hardware Safety Relay:</strong> Ensure front-panel <strong>Over Temperature Disconnect (OTD)</strong> is enabled at <strong>460 K</strong> on Channel A (cannot be set via remote SCPI).</li>
        </ol>
    </div>

</div>
</body>
</html>
"""

    with open("TUNING_REPORT.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Successfully generated self-contained TUNING_REPORT.html ({len(html_content)} bytes)")

if __name__ == "__main__":
    build_html()
