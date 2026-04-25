@echo off
title kormarc-auto API server
cd /d "%~dp0"

if not exist .venv\Scripts\python.exe (
  echo [ERROR] .venv not found. Run setup-once.bat first.
  pause
  exit /b 1
)

echo ================================================
echo  kormarc-auto API server
echo  Local:    http://localhost:8000
echo  Swagger:  http://localhost:8000/docs
echo  Press Ctrl+C to stop.
echo ================================================
.venv\Scripts\python.exe -m kormarc_auto.server.app
pause
