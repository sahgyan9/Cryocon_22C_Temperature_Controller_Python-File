# AI Agent Engineering Playbook & Lessons Learned
## Cryogenic Instrumentation, Real-Time Spectroscopy & Desktop GUI Automation

This document captures architectural rules, hard-earned debugging lessons, and implementation guidelines for AI Agents working on this codebase (Cryo-con 22C, Wayne Kerr 6510B/6500B, Janis Cryostat ST-LN-500, and Tkinter/Matplotlib Desktop GUIs).

---

### 1. Hardware Safety & Anti-Surge Architecture

#### The Physical System
- **Controller**: Cryo-con Model 22C (Firmware 3.33G, Serial 206687).
- **Cryostat**: Janis ST-LN-500 Cryogenic Probe Station with liquid nitrogen transfer line.
- **Samples**: PMN-PT relaxor ferroelectrics (fragile to thermal shock and electric surges).
- **Analyzer**: Wayne Kerr 6510B / 6500B Precision Impedance Analyzer.

#### Non-Negotiable Anti-Surge Ramp Sequence
When starting any ramp (heating or cooling), **NEVER** write a target setpoint directly while control is active. Doing so creates a large instantaneous temperature error ($\Delta T$), causing the PID loop to saturate the heater at 100% (50 W) and surge the sample.

**Strict Sequence (Enforced in `cryocon_controller.py` & `cooling_runner.py`):**
1. Read live stage temperature $T_\text{live}$.
2. Drop to `LOOP 1:TYPE PID` (disables active ramping so setpoint can move instantly without rate limits).
3. Park setpoint at live temperature: `LOOP 1:SETPT <T_live>` (forces temperature error $e = 0.0\text{ K}$).
4. Configure PID tuning, heater range, and rate limits:
   - $P = 70.0$, $I = 900.0\text{ s}$, $D = 0.0$
   - Range: `HI` (50 W), Max Power: `100.0%`
5. Engage loop: Send `CONTROL`.
6. Hold for thermal balance: **2.5 s delay** on physical hardware.
7. Switch mode: `LOOP 1:TYPE RAMPP` (with **0.4 s delay** for 22C microcontroller transition).
8. Arm target: `LOOP 1:SETPT <T_target>`.
9. Verify setpoint with SCPI readback retry.

#### Simulation (Mock) vs. Physical Execution Rule
- **Physical Hardware (`mock=False`)**: Enforce all inter-command sleeps (0.3 s to 2.5 s) and relay delays. Hardware microcontroller buffers will overflow or drop commands without them.
- **Simulation Mode (`mock=True`)**: Compress sleeps to 0.05 s–0.1 s. Never run 5-second physical sleeps in mock mode; it makes unit tests take 40+ seconds and frustrates users.

---

### 2. Zero-Corruption Data Streaming & Disk Saving

#### Core Rules
1. **Never Depend on Manual "Export CSV"**:
   - Laboratory experiments can run for 4 to 8 hours. If the PC sleeps, reboots, or crashes, in-memory data is lost.
   - Stream every point to disk immediately.
2. **Unbuffered Streaming**:
   - Write row $\to$ `file.flush()` $\to$ `os.fsync(file.fileno())`.
   - Guaranteed atomic write to physical storage.
3. **Dual File Strategy**:
   - `<name>.dat`: Tab-separated complete laboratory archive with all raw channels (`Time`, `T`, `f`, `R`, `X`, `Cp`, `TanD`, `Eps_Prime`, `Heater`, `Setpoint`).
   - `<name>.csv`: Comma-separated with requested primary columns first (`T (K)`, `f (Fixed)`, `R (ohm)`, `X (ohm)`, ...).
4. **Dedicated Directory**:
   - Keep data files in a dedicated `Data/` subfolder, never cluttering the root source directory.

---

### 3. Matplotlib & Tkinter High-Performance GUI Traps

#### Trap 1: `tight_layout()` in Live Streaming Loops (Major Performance Killer)
- **Problem**: Calling `fig.tight_layout()` inside the per-point data hook recalculates text bounding boxes and font rasterization metrics. In headless or withdrawn Tk windows (`root.withdraw()`), without a mapped OS window handle, this takes 300–500 ms of pure CPU time per figure.
- **Solution**: Call `fig.tight_layout()` **once** when the figure is constructed in `_build_visualizer()`. **Never** call `tight_layout()` in live acquisition redraw methods (`_redraw_*`).

#### Trap 2: Redrawing Inactive Tabs in Multi-Tab Notebooks
- **Problem**: When a GUI has 5 or 6 Matplotlib tabs, redrawing all canvases on every measurement point wastes 80–90% CPU redrawing invisible figures.
- **Solution**:
  1. In the live streaming loop, query `self.notebook.select()` and redraw **only the currently visible tab**.
  2. Bind `self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)` so that whenever the user clicks a tab, it refreshes instantly.
  3. Redraw all tabs (`force_all=True`) only when the experiment finishes.

#### Trap 3: GUI Freezes & Event Throttling
- Stream measurements at high pace (e.g. 10 Hz) in a background worker thread.
- Queue UI updates via `queue.Queue`.
- Rate-limit GUI plot redraws to max 2 Hz (0.5 s) using a timestamp check (`if now - self.last_chart_draw >= 0.5:`).
- Use `canvas.draw_idle()` instead of `canvas.draw()` so Tkinter can coalesce multiple draw requests.

---

### 4. Headless Testing & Test Runner Best Practices

#### Trap 1: Multiple `tk.Tk()` Roots in the Same Process
- **Problem**: Calling `root = tk.Tk()`, destroying it with `root.destroy()`, and then creating a new `root = tk.Tk()` in the same process leaves the shared Tcl interpreter with broken callback handles. It throws `_tkinter.TclError: invalid command name "..._poll_queue"`.
- **Solution**: Use a single `tk.Tk()` instance per test suite run. Combine GUI tests into a unified lifecycle test session.

#### Trap 2: Dangling `root.after()` Timers
- **Problem**: Background polling methods like `_poll_queue` schedule themselves repeatedly with `self.root.after(100, _poll_queue)`. If the test finishes or the window closes, Tcl tries to call the destroyed function.
- **Solution**:
  - Always store the job ID: `self._poll_job = self.root.after(...)`.
  - Provide a clean shutdown method:
    ```python
    def destroy_cleanly(self):
        self._alive = False
        if self._poll_job is not None:
            try:
                self.root.after_cancel(self._poll_job)
            except Exception:
                pass
            self._poll_job = None
    ```

#### Trap 3: Modal Dialogs Hanging Automated Tests
- Always monkeypatch modal dialogs at the top of headless test scripts:
  ```python
  import tkinter.messagebox as msgbox
  msgbox.showwarning = lambda *args, **kwargs: None
  msgbox.showinfo = lambda *args, **kwargs: None
  msgbox.showerror = lambda *args, **kwargs: None
  msgbox.askyesno = lambda *args, **kwargs: True
  ```

#### Trap 4: Python `sys.path` Subfolder Shadowing
- When a project has both a root controller and a subfolder controller, inserting `..` first into `sys.path` will cause Python to import the root file instead of the subfolder file.
- **Solution**: Always ensure the test script's own folder has top priority:
  ```python
  SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
  sys.path.insert(0, os.path.abspath(os.path.join(SCRIPT_DIR, "..")))
  sys.path.insert(0, SCRIPT_DIR)  # SCRIPT_DIR has index 0 (top priority)
  ```

---

### 5. Windows Hardware Concurrency (Exclusive COM & GPIB Access)
- On Windows, serial ports (e.g. `COM5` for Cryo-con) and VISA GPIB interfaces (e.g. `GPIB0::6::INSTR` for Wayne Kerr) permit **only one open handle at a time across the entire operating system**.
- If another script or GUI (e.g. `unified_gui.py`) is running, opening the port in a new GUI will fail with `PermissionError` or `SerialException`.
- **Action**: Always check running processes (`Get-Process python`) and advise the user to disconnect or close previous GUIs before starting a new experiment.

---

*Compiled and verified by Antigravity AI Pair Programmer — September 2026*
