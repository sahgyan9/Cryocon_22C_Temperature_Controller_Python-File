import os
import glob
import csv
import json

def analyze_file(filepath):
    filename = os.path.basename(filepath)
    with open(filepath, 'r', newline='', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    if not rows:
        return {"filename": filename, "error": "Empty file"}
    
    fields = reader.fieldnames
    
    # Handle staged log differently if needed
    is_staged = "Stage_Idx" in fields or "Stage_Target_K" in fields
    
    try:
        t_start = float(rows[0].get("Elapsed_Sec", 0))
        t_end = float(rows[-1].get("Elapsed_Sec", 0))
        duration = t_end - t_start
    except Exception:
        duration = len(rows)
    
    # Get parameters
    r0 = rows[0]
    r_mid = rows[len(rows)//2]
    
    p_gain = r_mid.get("P_Gain", r0.get("P_Gain", "N/A"))
    i_gain = r_mid.get("I_Gain", r0.get("I_Gain", "N/A"))
    d_gain = r_mid.get("D_Gain", r0.get("D_Gain", "N/A"))
    range_val = r_mid.get("Range", r0.get("Range", "N/A"))
    max_pwr = r_mid.get("MaxPwr_Pct", r0.get("MaxPwr_Pct", "N/A"))
    rate = r_mid.get("Ramp_Rate_K_min", r0.get("Ramp_Rate_K_min", "N/A"))
    
    temps = []
    setpoints = []
    heaters = []
    elapseds = []
    errors = []
    
    for r in rows:
        try:
            t_val = float(r.get("Temp_A_K", r.get("Temp_K", 0)))
            sp_val = float(r.get("Setpoint_K", r.get("Stage_Target_K", 0)))
            h_val = float(r.get("Heater_Pct", 0))
            el_val = float(r.get("Elapsed_Sec", 0))
            err_val = float(r.get("Error_K", t_val - sp_val))
            
            temps.append(t_val)
            setpoints.append(sp_val)
            heaters.append(h_val)
            elapseds.append(el_val)
            errors.append(err_val)
        except Exception:
            continue
            
    if not temps:
        return {"filename": filename, "error": "No temperature data"}
        
    start_temp = temps[0]
    final_temp = temps[-1]
    final_sp = setpoints[-1]
    max_temp = max(temps)
    peak_overshoot = max_temp - final_sp
    final_err = final_temp - final_sp
    
    # Post-0% heater climb (thermal coast)
    heater_was_on = False
    first_zero_idx = None
    for idx, h in enumerate(heaters):
        if h > 1.0:
            heater_was_on = True
        if heater_was_on and h <= 0.05:
            first_zero_idx = idx
            break
            
    coast_climb = 0.0
    temp_at_zero = 0.0
    max_temp_after_zero = 0.0
    if first_zero_idx is not None:
        temp_at_zero = temps[first_zero_idx]
        temps_after = temps[first_zero_idx:]
        max_temp_after_zero = max(temps_after)
        coast_climb = max_temp_after_zero - temp_at_zero

    # Saturation analysis
    try:
        mp_num = float(max_pwr) if max_pwr != "N/A" else 100.0
    except Exception:
        mp_num = 100.0
    sat_seconds = 0.0
    for idx, h in enumerate(heaters):
        if h >= mp_num - 0.5:
            dt = elapseds[idx] - elapseds[idx-1] if idx > 0 else 1.0
            if 0 < dt < 10:
                sat_seconds += dt

    return {
        "filename": filename,
        "is_staged": is_staged,
        "rows": len(rows),
        "duration_s": duration,
        "start_temp": start_temp,
        "final_sp": final_sp,
        "final_temp": final_temp,
        "max_temp": max_temp,
        "peak_overshoot": peak_overshoot,
        "final_err": final_err,
        "p_gain": p_gain,
        "i_gain": i_gain,
        "d_gain": d_gain,
        "range": range_val,
        "max_pwr": max_pwr,
        "rate": rate,
        "first_zero_idx": first_zero_idx,
        "temp_at_zero": temp_at_zero,
        "max_temp_after_zero": max_temp_after_zero,
        "coast_climb": coast_climb,
        "sat_seconds": sat_seconds
    }

def main():
    files = sorted(glob.glob("cryocon_log_*.csv"))
    print(f"Found {len(files)} files.")
    results = []
    for f in files:
        res = analyze_file(f)
        results.append(res)
        
    print(f"{'Filename':<38} | {'SP':<5} | {'P':<4} | {'I':<5} | {'D':<4} | {'Cap':<4} | {'Rate':<4} | {'PeakOver':<9} | {'FinalErr':<9} | {'Coast':<7} | {'Dur(m)':<6}")
    print("-" * 115)
    for r in results:
        if "error" in r:
            print(f"{r['filename']:<38} | ERROR: {r['error']}")
            continue
        print(f"{r['filename']:<38} | {r['final_sp']:<5.1f} | {str(r['p_gain']):<4} | {str(r['i_gain']):<5} | {str(r['d_gain']):<4} | {str(r['max_pwr']):<4} | {str(r['rate']):<4} | {r['peak_overshoot']:>+8.3f}K | {r['final_err']:>+8.3f}K | {r['coast_climb']:>+6.3f}K | {r['duration_s']/60:>5.1f}")
        
    with open("analysis_summary.json", "w") as jf:
        json.dump(results, jf, indent=2)

if __name__ == "__main__":
    main()
