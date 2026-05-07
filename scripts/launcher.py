"""Cycle 65 (사서 자가 설치 친화) — `.exe` 더블클릭 진입점.

사서 더블클릭 → Streamlit 서버 자동 실행 → 브라우저 자동 열림 → 즉시 사용.
PyInstaller --onefile 빌드 시 = Windows .exe·Mac .app·Linux binary.

원칙:
- Python 설치 X (PyInstaller 번들)
- 명령어 X (더블클릭 1회)
- 인터넷 차단 시 = offline demo 모드 자동 (KORMARC_DEMO_MODE=1)
- 에러 시 = 사서 친화 메시지 + "PO에게 보내기" link
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def find_free_port() -> int:
    """Streamlit 포트 자동 (8501·이미 사용 중이면 +1)."""
    for port in range(8501, 8520):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return 8501  # fallback


def get_streamlit_app_path() -> Path:
    """PyInstaller 번들 또는 dev 환경 = streamlit_app.py 경로."""
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller 번들 = sys._MEIPASS 안에 패키지 포함
        bundle = Path(sys._MEIPASS)
        return bundle / "kormarc_auto" / "ui" / "streamlit_app.py"
    # dev 환경
    return (
        Path(__file__).resolve().parent.parent / "src" / "kormarc_auto" / "ui" / "streamlit_app.py"
    )


def main() -> int:
    print("=" * 60)
    print("kormarc-auto · 한국 도서관 KORMARC 자동 생성 SaaS")
    print("=" * 60)
    print()
    print("⏳ 잠시만 기다려주세요·자동으로 브라우저가 열립니다...")
    print()

    # 사서 친화 = offline demo 모드 자동 (외부 API 키 0개로 작동)
    if not os.getenv("KORMARC_DEMO_MODE"):
        os.environ["KORMARC_DEMO_MODE"] = "1"
        print("ℹ 키 0개 데모 모드 자동 활성·SAMPLE 7건 + SENTINEL 5건 즉시 사용 가능")
    print()

    app_path = get_streamlit_app_path()
    if not app_path.exists():
        print(f"❌ 앱 파일 미발견: {app_path}")
        print()
        print("🆘 PO에게 알려주세요:")
        print("   GitHub Issues: https://github.com/okwhrlgma-bit/library/issues")
        print("   이메일: contact@kormarc-auto.example")
        input("Enter 키 = 종료...")
        return 1

    port = find_free_port()
    url = f"http://localhost:{port}"

    print(f"📚 kormarc-auto 시작·포트 {port}")
    print(f"🌐 브라우저 URL: {url}")
    print()
    print("🔴 종료 = 이 창 닫기 또는 Ctrl+C")
    print("=" * 60)

    # Streamlit 서버 백그라운드 실행
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.port",
        str(port),
        "--server.headless",
        "true",
        "--server.address",
        "127.0.0.1",
        "--browser.gatherUsageStats",
        "false",
    ]

    try:
        proc = subprocess.Popen(cmd)
    except Exception as e:
        print(f"❌ Streamlit 실행 실패: {type(e).__name__}: {e}")
        print()
        print("🆘 사서님 안녕하세요·이 메시지를 PO에게 보내주세요:")
        print(f"   에러: {type(e).__name__}: {e}")
        print(f"   OS: {sys.platform}·Python: {sys.version}")
        print("   GitHub Issues: https://github.com/okwhrlgma-bit/library/issues")
        input("Enter 키 = 종료...")
        return 1

    # 5초 대기 후 브라우저 자동 열기 (Streamlit 부팅 시간)
    time.sleep(5)
    try:
        webbrowser.open(url)
    except Exception:
        print(f"⚠ 브라우저 자동 열기 실패·직접 접속: {url}")

    # Streamlit 프로세스 대기 (Ctrl+C 또는 창 닫기)
    try:
        proc.wait()
    except KeyboardInterrupt:
        print()
        print("👋 종료 중...")
        proc.terminate()
        proc.wait(timeout=5)
    return proc.returncode or 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
