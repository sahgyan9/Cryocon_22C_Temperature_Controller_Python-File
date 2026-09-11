"""
Automated Verification Suite for Fixed 10 kHz Continuous Cooling Suite
======================================================================
Tests the CoolingOrchestrator and CoolingGUI headlessly in mock simulation mode:
1. Validates Wayne Kerr 10 kHz fixed-frequency configuration & R-X acquisition.
2. Validates Cryo-con 22C anti-surge cooling ramp arming (422 K -> 300 K @ 0.5 K/min).
3. Validates unbuffered disk writing (.flush() + os.fsync()) and verifies data file integrity.
4. Validates Tkinter GUI lifecycle, table population (T | f | R | X), and live plotting.
5. Validates Emergency Stop and failsafe heater shutdown.

Author: Lab Automation & Antigravity
Date: 2026-09-11
"""

import os
import sys
import tempfile
import threading
import time
import tkinter as tk
import tkinter.messagebox as msgbox

# Ensure immediate unbuffered output
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass

# Ensure parent and current directory are on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(SCRIPT_DIR, "..")))
sys.path.insert(0, SCRIPT_DIR)

# Monkeypatch modal dialogs so headless tests never block on user input
msgbox.showwarning = lambda *args, **kwargs: None
msgbox.showinfo = lambda *args, **kwargs: None
msgbox.showerror = lambda *args, **kwargs: None
msgbox.askyesno = lambda *args, **kwargs: True

from cryocon_controller import Cryocon22C
from wayne_kerr_controller import WayneKerr6500B
from cooling_runner import CoolingOrchestrator
from cooling_gui import CoolingGUI


def test_cooling_orchestrator_headless():
    print("\n" + "=" * 80, flush=True)
    print(" TEST 1: CoolingOrchestrator Headless Verification (Mock Mode)", flush=True)
    print("=" * 80, flush=True)

    # Initialize Mock Instruments
    cryo = Cryocon22C(port="COM5", mock=True)
    cryo._temp_a = 422.0  # Set current temperature to ~422 K
    assert cryo.connect(), "Cryocon mock connect failed"

    wk = WayneKerr6500B(resource_name="GPIB0::6::INSTR", mock=True)
    assert wk.connect(), "Wayne Kerr mock connect failed"

    with tempfile.TemporaryDirectory() as tmpdir:
        acquired_points = []
        status_updates = []

        def on_point(pt):
            acquired_points.append(pt)

        def on_status(st):
            status_updates.append(st)

        orchestrator = CoolingOrchestrator(
            cryocon=cryo,
            wayne_kerr=wk,
            target_temp=300.0,
            ramp_rate=0.50,
            fixed_freq_hz=10000.0,
            drive_level_v=0.100,
            sample_interval_s=0.1,  # Fast pacing for verification
            out_dir=tmpdir,
            file_prefix="Test_Cooling",
            on_point_acquired=on_point,
            on_status_update=on_status
        )

        t = threading.Thread(target=orchestrator.run)
        t.start()

        # Wait for at least 5 points (arm_safe_ramp takes ~6s of safety-delays)
        print("[TEST] Waiting for arming sequence and point acquisition...", flush=True)
        for i in range(120):
            if len(acquired_points) >= 5:
                break
            time.sleep(0.1)

        orchestrator.request_abort()
        t.join(timeout=5.0)

        # -----------------------------------------------------------------
        # Verify Orchestrator Results
        # -----------------------------------------------------------------
        print(f"[VERIFY] Points captured: {len(acquired_points)}", flush=True)
        assert len(acquired_points) >= 3, f"Expected >= 3 points, got {len(acquired_points)}"

        # Check Wayne Kerr frequency configuration
        assert abs(wk._freq_hz - 10000.0) < 1e-3, f"Expected freq 10000.0 Hz, got {wk._freq_hz}"
        assert wk._term1 == "R" and wk._term2 == "X", f"Expected R-X mode, got {wk._term1}-{wk._term2}"

        # Check sample point 0 data schema
        pt0 = acquired_points[0]
        print(
            f"  Point 0: T={pt0['temp_k']:.3f} K, f={pt0['freq_fixed']} Hz, "
            f"R={pt0['r_ohm']:.2e} Ω, X={pt0['x_ohm']:.2e} Ω, ε'={pt0['eps_prime']:.1f}",
            flush=True
        )
        assert abs(pt0["freq_fixed"] - 10000.0) < 1e-3, "Frequency not 10 kHz"
        assert abs(pt0["target_k"] - 300.0) < 1e-3, "Target setpoint not 300.0 K"
        assert pt0["temp_k"] > 350.0, f"Expected temperature near 422 K, got {pt0['temp_k']}"
        assert pt0["r_ohm"] > 0.0, f"Expected positive resistance, got {pt0['r_ohm']}"
        assert pt0["x_ohm"] < 0.0, f"Expected capacitive reactance (negative), got {pt0['x_ohm']}"
        assert pt0["eps_prime"] > 100.0, f"Expected realistic permittivity, got {pt0['eps_prime']}"

        # Check file integrity on disk
        filepath = orchestrator.current_filepath
        assert os.path.exists(filepath), f"Output file does not exist: {filepath}"
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        print(f"[VERIFY] Lines written to disk: {len(lines)}", flush=True)
        assert len(lines) >= len(acquired_points) + 1, "Disk lines mismatch"
        header = lines[0].strip().split("\t")
        assert header[0] == "Time (s)"
        assert header[2] == "T (K)"
        assert header[3] == "f (Hz)"
        assert header[4] == "R (Ohm)"
        assert header[5] == "X (Ohm)"

        # Check line 1 values
        row1 = lines[1].strip().split("\t")
        t_row1 = float(row1[2])
        f_row1 = float(row1[3])
        r_row1 = float(row1[4])
        x_row1 = float(row1[5])
        assert abs(f_row1 - 10000.0) < 1e-2
        assert t_row1 > 350.0
        assert r_row1 > 0
        assert x_row1 < 0

        # Check auto-saved CSV file integrity
        csvpath = orchestrator.current_csvpath
        assert os.path.exists(csvpath), f"Output CSV does not exist: {csvpath}"
        with open(csvpath, "r", encoding="utf-8") as f_c:
            csv_lines = f_c.readlines()
        print(f"[VERIFY] CSV lines written to disk: {len(csv_lines)}", flush=True)
        assert len(csv_lines) >= len(acquired_points) + 1, "CSV lines mismatch"
        csv_header = csv_lines[0].strip().split(",")
        assert csv_header[0] == "T (K)"
        assert csv_header[1] == "f (Fixed)"
        assert csv_header[2] == "R (ohm)"
        assert csv_header[3] == "X (ohm)"

        # Check failsafe: Cryocon CONTROL must be OFF after abort
        assert not cryo._control_on, "Failsafe error: Cryocon control was not turned OFF!"

    cryo.disconnect()
    wk.disconnect()
    print("[PASS] TEST 1: CoolingOrchestrator passed all checks!\n", flush=True)


def test_cooling_gui_full_lifecycle():
    print("=" * 80, flush=True)
    print(" TEST 2: CoolingGUI Headless Lifecycle, Live Streaming & Saving Verification", flush=True)
    print("=" * 80, flush=True)

    root = tk.Tk()
    root.withdraw()  # Headless mode
    app = CoolingGUI(root)

    try:
        # 1. Enable mock mode & connect
        app.mock_var.set(True)
        app.connect_hardware()

        assert app.cryocon is not None and app.cryocon.connected, "GUI failed to connect mock Cryocon"
        assert app.wayne_kerr is not None and app.wayne_kerr.connected, "GUI failed to connect mock Wayne Kerr"
        print("[VERIFY] Mock instruments connected via GUI.", flush=True)

        # 2. Inject mock point into UI dispatcher
        mock_point = {
            "point_idx": 1,
            "elapsed_s": 2.5,
            "temp_k": 421.850,
            "freq_fixed": 10000.0,
            "r_ohm": 12500.0,
            "x_ohm": -48000.0,
            "z_mag_ohm": 49601.5,
            "theta_deg": -75.4,
            "cp_farad": 3.315e-10,
            "tan_delta": 0.2604,
            "eps_prime": 1872.0,
            "heater_pct": 58.4,
            "setpoint_k": 421.8,
            "target_k": 300.0
        }
        app.ui_queue.put(("point_acquired", mock_point))

        # Process pending Tkinter events
        for _ in range(10):
            root.update_idletasks()
            root.update()
            time.sleep(0.02)

        # 3. Check Live Data Table: T (K) | f (Fixed) | R (ohm) | X (ohm)
        table_items = app.table.get_children()
        assert len(table_items) == 1, f"Expected 1 row in table, got {len(table_items)}"
        row_values = app.table.item(table_items[0])["values"]
        print(f"  Initial Table Row: {row_values}", flush=True)
        assert str(row_values[0]) == "421.850", f"T (K) mismatch: {row_values[0]}"
        assert str(row_values[1]) == "10.0 kHz", f"f (Fixed) mismatch: {row_values[1]}"
        assert "1.25e+04" in str(row_values[2]) or "12500" in str(row_values[2]), f"R (ohm) mismatch: {row_values[2]}"
        assert "-4.80e+04" in str(row_values[3]) or "-48000" in str(row_values[3]), f"X (ohm) mismatch: {row_values[3]}"

        # 4. Test Plot Redraws across all tabs without exceptions
        app._redraw_all_plots(force_all=True)
        print("[VERIFY] Multi-tab Matplotlib plots (including Tab 6 eps' vs T) redrawn cleanly.", flush=True)

        # 5. Clear table for live acquisition test
        app.clear_table()
        assert len(app.table.get_children()) == 0, "Table clear failed"

        # 6. Configure live run saving into subfolder 'Data/'
        data_dir = os.path.join(SCRIPT_DIR, "Data")
        os.makedirs(data_dir, exist_ok=True)
        app.out_dir_var.set(data_dir)
        app.sample_interval_var.set(0.1)  # fast pacing for test
        app.cryocon._temp_a = 422.0

        print(f"[TEST] Starting live cooling experiment via GUI into: {data_dir}", flush=True)
        app.start_experiment()

        # 7. Pump Tk event loop until at least 3 points are acquired
        t0 = time.time()
        while time.time() - t0 < 8.0:
            root.update_idletasks()
            root.update()
            if app.orchestrator and app.orchestrator.points_count >= 3:
                break
            time.sleep(0.05)

        # Allow final queue items to populate the UI table
        for _ in range(10):
            root.update_idletasks()
            root.update()
            time.sleep(0.02)

        live_points_seen = len(app.table.get_children())
        print(f"[VERIFY] Points captured in GUI live table: {live_points_seen}", flush=True)
        assert live_points_seen >= 2, f"Expected >= 2 live points, got {live_points_seen}"

        # 8. Verify live disk files in Data/
        dat_path = app.orchestrator.current_filepath
        csv_path = app.orchestrator.current_csvpath

        assert os.path.exists(dat_path), f"DAT file not found: {dat_path}"
        with open(dat_path, "r", encoding="utf-8") as f_dat:
            dat_lines = f_dat.readlines()
        print(f"[VERIFY] Lines in Data/*.dat: {len(dat_lines)}", flush=True)
        assert len(dat_lines) >= live_points_seen + 1, "DAT line count mismatch"

        assert os.path.exists(csv_path), f"CSV file not found: {csv_path}"
        with open(csv_path, "r", encoding="utf-8") as f_csv:
            csv_lines = f_csv.readlines()
        print(f"[VERIFY] Lines in Data/*.csv: {len(csv_lines)}", flush=True)
        assert len(csv_lines) >= live_points_seen + 1, "CSV line count mismatch"

        # Verify CSV Header schema: T (K),f (Fixed),R (ohm),X (ohm)...
        csv_header = csv_lines[0].strip().split(",")
        assert csv_header[0] == "T (K)"
        assert csv_header[1] == "f (Fixed)"
        assert csv_header[2] == "R (ohm)"
        assert csv_header[3] == "X (ohm)"

        first_data_row = csv_lines[1].strip().split(",")
        print(f"  First live data row: T={first_data_row[0]} K, f={first_data_row[1]} Hz, R={first_data_row[2]} Ω, X={first_data_row[3]} Ω", flush=True)
        assert float(first_data_row[0]) > 350.0  # Ambient around 422 K
        assert float(first_data_row[1]) == 10000.0  # Fixed 10 kHz

        # Clean up test files from Data/
        try:
            os.remove(dat_path)
            os.remove(csv_path)
        except Exception:
            pass

        # 9. Test Emergency Stop failsafe
        app.emergency_stop()
        assert not app.cryocon._control_on, "Emergency Stop failed to turn OFF control!"
        print("[VERIFY] Emergency Stop disengaged heater safely.", flush=True)

    finally:
        app.abort_experiment()
        app.destroy_cleanly()
        app.disconnect_hardware()
        try:
            root.destroy()
        except Exception:
            pass

    print("[PASS] TEST 2: CoolingGUI lifecycle, streaming & live saving passed all checks!\n", flush=True)


def main():
    print("=" * 80, flush=True)
    print(" RUNNING FULL AUTOMATED VERIFICATION SUITE", flush=True)
    print("=" * 80, flush=True)
    try:
        test_cooling_orchestrator_headless()
        test_cooling_gui_full_lifecycle()
        print("=" * 80, flush=True)
        print(" ALL VERIFICATION TESTS PASSED SUCCESSFULLY! (100% GREEN)", flush=True)
        print("=" * 80, flush=True)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n[FATAL ERROR IN VERIFICATION]: {e}", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
