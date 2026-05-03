@echo off
REM B안 Cycle 3 (P2) — .bat deprecation 안내·기능은 유지
REM 권장: uv tool install kormarc-auto·이후 'kormarc-auto serve' / 'kormarc-auto ui'
title kormarc-auto Start All
cd /d "%~dp0"
echo.
echo [INFO] uv tool install kormarc-auto 완료 시 = kormarc-auto serve / ui / demo
echo [INFO] 본 .bat는 .venv 환경 호환 보존용 (v0.7+ 제거 예정)
echo.

if not exist .venv\Scripts\python.exe (
  echo [ERROR] .venv not found. Run setup-once.bat first.
  pause
  exit /b 1
)

echo ================================================
echo  Starting kormarc-auto (3 windows)
echo   API:      http://localhost:8000
echo   UI:       http://localhost:8501
echo   Landing:  http://localhost:8080
echo  Do NOT close those windows.
echo ================================================

start "kormarc-server" cmd /c "%~dp0\start-server.bat"
timeout /t 3 > nul
start "kormarc-ui" cmd /c "%~dp0\start-ui.bat"
start "kormarc-landing" cmd /c "%~dp0\start-landing.bat"

echo.
echo OK - 3 windows started.
echo To share with phone: run start-tunnel.bat
echo.
pause
