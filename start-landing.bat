@echo off
chcp 65001 > nul
title kormarc-auto · 랜딩 페이지 (정적 호스팅, 8080)
cd /d "%~dp0\landing"

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  랜딩 페이지 (정적) 시작
echo  주소: http://localhost:8080
echo  사서 가입 폼은 API 서버(8000)가 떠있을 때 작동
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"%~dp0\.venv\Scripts\python.exe" -m http.server 8080
pause
