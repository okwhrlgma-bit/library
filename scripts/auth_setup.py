"""PO 인증 셋업 (Part G Step 2·7) — 1회 실행 후 또는 90일 회전 시.

PO가 인터랙티브로 비밀번호 입력 → bcrypt 해시 + 32자 cookie key 생성 →
.streamlit/auth_config.yaml 작성. 평문 비밀번호는 메모리에서만 사용·미저장.

회전: 90일마다 재실행 (PO 마스터 §G.5 정기 보안 감사).
"""

from __future__ import annotations

import contextlib
import getpass
import os
import secrets
import sys
from pathlib import Path

# Windows cp949 회피 (PostCompact·기타 hook과 동일 패턴)
with contextlib.suppress(AttributeError, OSError):
    sys.stdout.reconfigure(encoding="utf-8")

import bcrypt
import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / ".streamlit" / "auth_config.yaml"
TEMPLATE = ROOT / ".streamlit" / "auth_config.yaml.example"

MIN_PASSWORD_LEN = 12  # PO 마스터 §G.5 보안 감사 권장


def main() -> int:
    print("=== KORMARC Auto 인증 셋업 (Part G Step 2·7) ===")
    print(f"출력: {OUT}")
    print(f"기존 파일: {'있음 (덮어씀)' if OUT.exists() else '없음 (신규)'}")
    print()
    print(f"비밀번호 정책: {MIN_PASSWORD_LEN}자 이상, 영문·숫자·특수문자 권장.")
    print("이 스크립트는 평문 비밀번호를 저장하지 않습니다 (bcrypt 해시만).")
    print()

    pw = getpass.getpass("PO 비밀번호 입력: ")
    if len(pw) < MIN_PASSWORD_LEN:
        print(f"❌ {MIN_PASSWORD_LEN}자 미만. 보안 정책 위반.")
        return 1

    pw_confirm = getpass.getpass("PO 비밀번호 재입력: ")
    if pw != pw_confirm:
        print("❌ 일치하지 않음.")
        return 1

    # bcrypt rounds=12 — 2026 OWASP 권장 (rounds 10~14 적정)
    pw_hash = bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")
    cookie_key = secrets.token_urlsafe(32)

    # 평문 비밀번호 메모리 zero-out 시도 (Python str immutable이라 best-effort)
    del pw, pw_confirm

    config = {
        "credentials": {
            "usernames": {
                "okwhrlgma": {
                    "email": "okwhrlgma@gmail.com",
                    "name": "PO",
                    "password": pw_hash,
                    "logged_in": False,
                    "first_name": "",
                    "last_name": "",
                    "roles": ["admin"],
                    "failed_login_attempts": 0,
                }
            }
        },
        "cookie": {
            "name": "kormarc_auth",
            "key": cookie_key,
            "expiry_days": 7,
        },
        "pre-authorized": {
            "emails": ["okwhrlgma@gmail.com"],
        },
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

    # Windows 파일 권한: 가능하면 user-only 읽기. 실패해도 .gitignore 보호 있음.
    # Windows는 chmod 효과 제한적, .gitignore가 1차 방어.
    with contextlib.suppress(OSError):
        os.chmod(OUT, 0o600)

    print()
    print(f"✅ {OUT.relative_to(ROOT)} 생성 완료")
    print("   - 사용자: okwhrlgma@gmail.com")
    print(f"   - 해시: bcrypt rounds=12 ({len(pw_hash)} chars)")
    print(f"   - cookie key: {cookie_key[:8]}...{cookie_key[-4:]} (32 chars)")
    print()
    print("⚠️  검증:")
    print("   - .gitignore에 .streamlit/auth_config.yaml 등재 확인")
    print("   - 90일 후 본 스크립트 재실행으로 cookie key·비밀번호 회전")
    print("   - streamlit run 후 인증 화면 → 로그인 흐름 검증")
    return 0


if __name__ == "__main__":
    sys.exit(main())
