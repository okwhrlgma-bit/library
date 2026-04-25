@echo off
title kormarc-auto Setup (one-time)
cd /d "%~dp0"

echo ================================================
echo  kormarc-auto first-time setup
echo ================================================

where python >nul 2>nul
if errorlevel 1 (
  echo [INFO] Python not found. Installing via winget...
  winget install --id Python.Python.3.12 --silent --accept-source-agreements --accept-package-agreements
  echo [INFO] Open a NEW terminal and run setup-once.bat again.
  pause
  exit /b 0
)

if not exist .venv\Scripts\python.exe (
  echo [1/3] Creating venv...
  python -m venv .venv
)

echo [2/3] Installing dependencies (a few minutes)...
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -e .[dev,ui]

echo [3/3] Environment check...
.venv\Scripts\python.exe -m kormarc_auto.cli info

echo.
echo ================================================
echo  OK - setup complete.
echo  Next:
echo    1. Open .env, fill ANTHROPIC_API_KEY etc.
echo    2. Double-click start-all.bat
echo    3. start-tunnel.bat for phone access
echo ================================================
pause
