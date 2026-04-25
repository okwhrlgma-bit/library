@echo off
chcp 65001 > nul
title kormarc-auto · Streamlit UI
cd /d "%~dp0"

if not exist .venv\Scripts\python.exe (
  echo [ERROR] .venv 가 없습니다. 다음 명령을 한 번 실행하세요:
  echo   python -m venv .venv ^&^& .venv\Scripts\pip install -e .[dev,ui]
  pause
  exit /b 1
)

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  kormarc-auto Streamlit UI 시작 (Ctrl+C 로 종료)
echo  브라우저가 자동으로 열립니다: http://localhost:8501
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
.venv\Scripts\python.exe -m streamlit run src\kormarc_auto\ui\streamlit_app.py --server.port 8501 --server.address 127.0.0.1 --browser.gatherUsageStats false
pause
