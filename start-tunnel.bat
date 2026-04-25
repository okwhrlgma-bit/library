@echo off
chcp 65001 > nul
title kormarc-auto · Cloudflare 터널 (모바일 접속)
cd /d "%~dp0"

where cloudflared >nul 2>nul
if errorlevel 1 (
  echo [ERROR] cloudflared 가 PATH에 없습니다.
  echo   설치 명령: winget install --id Cloudflare.cloudflared --silent
  pause
  exit /b 1
)

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  단발 Cloudflare 터널 시작
echo  몇 초 후 출력되는 https://*.trycloudflare.com 주소를 폰에서 접속
echo  종료: Ctrl+C
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo [1] UI (Streamlit, 8501)
echo [2] API (FastAPI, 8000)
echo [3] 둘 다 (UI 권장)
set /p choice="선택 (1/2/3, 기본 1): "
if "%choice%"=="" set choice=1
if "%choice%"=="1" cloudflared tunnel --url http://localhost:8501
if "%choice%"=="2" cloudflared tunnel --url http://localhost:8000
if "%choice%"=="3" (
  start "tunnel-api" cloudflared tunnel --url http://localhost:8000
  cloudflared tunnel --url http://localhost:8501
)
pause
