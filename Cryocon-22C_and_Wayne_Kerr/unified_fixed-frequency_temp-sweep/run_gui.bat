@echo off
title Wayne Kerr 6510B ^& Cryo-con 22C — 10 kHz Continuous Cooling Spectroscopy
cd /d "%~dp0"
echo ===============================================================================
echo   Wayne Kerr 6510B ^& Cryo-con 22C — Fixed 10 kHz Continuous Cooling Suite
echo   Subfolder: unified_fixed-frequency_temp-sweep
echo   Target   : Cool from ~422 K to 300.0 K @ 0.5 K/min with fixed 10 kHz R-X
echo ===============================================================================
echo.

:: Detect Python executable (check Anaconda first, then local/system Python)
set "PYTHON_EXE="
if exist "%USERPROFILE%\anaconda3\python.exe" set "PYTHON_EXE=%USERPROFILE%\anaconda3\python.exe"
if not defined PYTHON_EXE if exist "C:\Users\SRMAP\anaconda3\python.exe" set "PYTHON_EXE=C:\Users\SRMAP\anaconda3\python.exe"
if not defined PYTHON_EXE if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if not defined PYTHON_EXE if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not defined PYTHON_EXE if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
if not defined PYTHON_EXE if exist "C:\ProgramData\anaconda3\python.exe" set "PYTHON_EXE=C:\ProgramData\anaconda3\python.exe"
if not defined PYTHON_EXE set "PYTHON_EXE=python"

echo Launching Cooling GUI with: %PYTHON_EXE%
echo.
"%PYTHON_EXE%" cooling_gui.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Application exited with code %ERRORLEVEL%.
    pause
)
