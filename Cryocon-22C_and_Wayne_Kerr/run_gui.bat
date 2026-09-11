@echo off
title Wayne Kerr 6510B ^& Cryo-con 22C — Unified Impedance Spectroscopy
cd /d "%~dp0"
echo ===============================================================================
echo   Wayne Kerr 6510B ^& Cryo-con 22C — Unified Impedance Spectroscopy Suite
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

echo Launching GUI with: %PYTHON_EXE%
echo.
"%PYTHON_EXE%" unified_gui.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Application exited with code %ERRORLEVEL%.
    pause
)
