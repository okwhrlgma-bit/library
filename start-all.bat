@echo off
chcp 65001 > nul
title kormarc-auto · 전체 시작
cd /d "%~dp0"

if not exist .venv\Scripts\python.exe (
  echo [ERROR] .venv 가 없습니다. 먼저 다음 명령을 한 번 실행:
  echo   python -m venv .venv ^&^& .venv\Scripts\pip install -e .[dev,ui]
  pause
  exit /b 1
)

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  kormarc-auto 전체 환경 시작
echo  ├─ API 서버:  http://localhost:8000
echo  ├─ Streamlit: http://localhost:8501
echo  └─ 랜딩:      http://localhost:8080
echo  각 창은 별도로 열립니다. 닫지 마세요.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

start "kormarc-server" cmd /c "%~dp0\start-server.bat"
timeout /t 3 > nul
start "kormarc-ui" cmd /c "%~dp0\start-ui.bat"
start "kormarc-landing" cmd /c "%~dp0\start-landing.bat"

echo.
echo ✓ 3개 창 시작됨. 모바일 접속하려면 별도로 start-tunnel.bat 실행
echo.
pause
