@echo off
title kormarc-auto Cloudflare Tunnel
cd /d "%~dp0"

where cloudflared >nul 2>nul
if errorlevel 1 (
  echo [ERROR] cloudflared not in PATH.
  echo   Install: winget install --id Cloudflare.cloudflared --silent
  pause
  exit /b 1
)

echo ================================================
echo  Cloudflare Tunnel - one-shot
echo  Wait for the https://*.trycloudflare.com URL.
echo  Press Ctrl+C to stop.
echo ================================================
echo.
echo [1] UI (Streamlit, port 8501) - default
echo [2] API (FastAPI, port 8000)
echo [3] Both (UI + API)
set /p choice="Select (1/2/3, default 1): "
if "%choice%"=="" set choice=1
if "%choice%"=="1" cloudflared tunnel --url http://localhost:8501
if "%choice%"=="2" cloudflared tunnel --url http://localhost:8000
if "%choice%"=="3" (
  start "tunnel-api" cloudflared tunnel --url http://localhost:8000
  cloudflared tunnel --url http://localhost:8501
)
pause
