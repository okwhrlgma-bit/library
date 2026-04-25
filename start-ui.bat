@echo off
title kormarc-auto Streamlit UI
cd /d "%~dp0"

if not exist .venv\Scripts\python.exe (
  echo [ERROR] .venv not found. Run setup-once.bat first.
  pause
  exit /b 1
)

echo ================================================
echo  kormarc-auto Streamlit UI
echo  Browser will open: http://localhost:8501
echo  Press Ctrl+C to stop.
echo ================================================
.venv\Scripts\python.exe -m streamlit run src\kormarc_auto\ui\streamlit_app.py --server.port 8501 --server.address 127.0.0.1 --browser.gatherUsageStats false
pause
