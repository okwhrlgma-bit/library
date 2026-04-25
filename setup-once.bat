@echo off
chcp 65001 > nul
title kormarc-auto · 최초 셋업 (1회만)
cd /d "%~dp0"

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  kormarc-auto 최초 셋업
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

where python >nul 2>nul
if errorlevel 1 (
  echo [INFO] Python 미설치. winget으로 설치 시도...
  winget install --id Python.Python.3.12 --silent --accept-source-agreements --accept-package-agreements
  echo [INFO] 새 셸을 열어야 PATH 갱신됩니다. 이 창을 닫고 setup-once.bat 다시 실행.
  pause
  exit /b 0
)

if not exist .venv\Scripts\python.exe (
  echo [1/3] 가상환경 생성...
  python -m venv .venv
)

echo [2/3] 의존성 설치 (몇 분 소요)...
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -e .[dev,ui]

echo [3/3] 환경 점검...
.venv\Scripts\python.exe -m kormarc_auto.cli info

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  ✓ 셋업 완료
echo  다음 단계:
echo    1. .env 파일 열어 NL_CERT_KEY · ANTHROPIC_API_KEY 등 채우기
echo    2. start-all.bat 더블클릭으로 시작
echo    3. start-tunnel.bat 으로 모바일 접속 URL 발급
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
pause
