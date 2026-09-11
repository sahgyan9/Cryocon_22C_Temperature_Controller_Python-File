@echo off
title Cryocon 22C Temperature Controller - Dashboard
cd /d "%~dp0"
echo ===================================================
echo   Starting Cryocon 22C Temperature Controller GUI
echo ===================================================

:: Detect Python executable (check Anaconda first, then local/system Python)
set "PYTHON_EXE="
if exist "%USERPROFILE%\anaconda3\python.exe" set "PYTHON_EXE=%USERPROFILE%\anaconda3\python.exe"
if not defined PYTHON_EXE if exist "C:\Users\SRMAP\anaconda3\python.exe" set "PYTHON_EXE=C:\Users\SRMAP\anaconda3\python.exe"
if not defined PYTHON_EXE if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if not defined PYTHON_EXE if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not defined PYTHON_EXE if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
if not defined PYTHON_EXE if exist "C:\ProgramData\anaconda3\python.exe" set "PYTHON_EXE=C:\ProgramData\anaconda3\python.exe"
if not defined PYTHON_EXE set "PYTHON_EXE=python"

"%PYTHON_EXE%" cryocon_gui.py

if errorlevel 1 (
    echo.
    echo [ERROR] GUI exited with an error.
    pause
)
