# Cryocon 22C Project - Dev Notes for Future Agents

## Python Executable
- **Use:** `C:\Users\SRMAP\anaconda3\python.exe`
- Do NOT use `python`, `python3`, or `py` -- none resolve on this machine.
- The `.venv` is broken (points to `C:\Program Files\Python312` which no longer exists).
- Anaconda has pyserial already installed.

Run any script like this:
  & "C:\Users\SRMAP\anaconda3\python.exe" script_name.py

## COM Port Rule -- CRITICAL
- The Cryocon 22C uses COM5 at 57600 baud (upgraded from 9600 for ultra-fast 10 Hz telemetry).
- Only ONE process can own COM5 at a time.
- If cryocon_gui.py is running and connected, ALL other scripts will get:
  PermissionError(13, 'Access is denied.') on COM5.
- Fix: Click Disconnect in the GUI before running any standalone script.
- After the script finishes, reconnect in the GUI.

## Launching the GUI
  & "C:\Users\SRMAP\anaconda3\python.exe" cryocon_gui.py

## PID Table 02 - Last Written
- Date: 2026-08-24
- 16 entries, 77K to 475K, all 16 verified OK
- Script: write_pid_table02.py
- Zone 1 (300-475K, no active cooling): I = 30-45, D = 52-70
- Zone 2 (77-300K, LN2 active cooling): I = 50-65, D = 20-52
