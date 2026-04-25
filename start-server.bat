@echo off
chcp 65001 > nul
title kormarc-auto · API 서버
cd /d "%~dp0"

if not exist .venv\Scripts\python.exe (
  echo [ERROR] .venv 가 없습니다. 다음 명령을 한 번 실행하세요:
  echo   python -m venv .venv ^&^& .venv\Scripts\pip install -e .[dev]
  pause
  exit /b 1
)

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  kormarc-auto API 서버 시작 (Ctrl+C 로 종료)
echo  로컬 주소: http://localhost:8000
echo  Swagger:   http://localhost:8000/docs
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
.venv\Scripts\python.exe -m kormarc_auto.server.app
pause
