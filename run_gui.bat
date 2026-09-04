@echo off
title Cryocon 22C Temperature Controller - Dashboard
cd /d "%~dp0"
echo ===================================================
echo   Starting Cryocon 22C Temperature Controller GUI
echo ===================================================

if exist "%USERPROFILE%\anaconda3\python.exe" (
    "%USERPROFILE%\anaconda3\python.exe" cryocon_gui.py
) else if exist "C:\Users\SRMAP\anaconda3\python.exe" (
    "C:\Users\SRMAP\anaconda3\python.exe" cryocon_gui.py
) else (
    python cryocon_gui.py
)

if errorlevel 1 (
    echo.
    echo [ERROR] GUI exited with an error.
    pause
)
