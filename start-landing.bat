@echo off
title kormarc-auto Landing
cd /d "%~dp0\landing"

echo ================================================
echo  Landing page (static) - http://localhost:8080
echo  Signup form needs API server (port 8000) up.
echo ================================================
"%~dp0\.venv\Scripts\python.exe" -m http.server 8080
pause
