@echo off
title Wayne Kerr 6510B & Cryo-con 22C — Unified Impedance Spectroscopy
cd /d "%~dp0"
echo ===============================================================================
echo   Wayne Kerr 6510B & Cryo-con 22C — Unified Impedance Spectroscopy Suite
echo ===============================================================================
echo.
echo Launching GUI...
python unified_gui.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Application exited with code %ERRORLEVEL%.
    pause
)
