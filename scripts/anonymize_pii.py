"""PII 일괄 익명화 — 자관·페르소나 실명 → 일반명.

PO 명령 (2026-05-03): "각 이름과 도서관명 익명화 필수 / 내부도 혹시 모르니까 익명화"

치환 규칙:
- 자관 실명 → ○○도서관 / PILOT 자관
- 페르소나 사서 실명 → 사서 A·B·C·D·E
- 자관 위치 (은평구공공도서관 11개 중 1개) → 공공도서관 1개

제외 (system reference·public domain):
- 윤동주: 역사적 인물 (책 제목 예시)
- 이재철: KCR4 청구기호 시스템 작자명 (system reference)
- okwhrlgma@gmail.com: 패키지 메타 (pyproject.toml에서 유지)
- okwhr: 패키지 author username

사용:
    python scripts/anonymize_pii.py --dry-run    # 미리보기
    python scripts/anonymize_pii.py --apply       # 실제 적용
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 치환 규칙 (순서 중요 — 긴 매치 먼저)
REPLACEMENTS: list[tuple[str, str]] = [
    # 자관 실명 (긴 매치 우선·언더스코어/공백/약어 모두)
    ("내를건너서 숲으로 도서관", "○○도서관"),
    ("내를건너서_숲으로_도서관", "PILOT_자관"),
    ("내를건너서 숲으로", "PILOT 자관"),
    ("내를건너서_숲으로", "PILOT_자관"),
    ("내를건너서숲으로 도서관", "○○도서관"),
    ("내를건너서숲으로", "PILOT 자관"),
    ("내건숲", "PILOT자관"),
    # 자관 위치 노출
    ("은평구공공도서관 11개 중 1개", "공공도서관 1개"),
    ("은평구 공공도서관 11개 중 1개", "공공도서관 1개"),
    # 페르소나 사서 실명 → 역할
    ("박지수", "사서 A"),
    ("김기수", "사서 B"),
    ("박세진", "사서 C"),
    ("신은미", "사서 D"),
    ("조기흠", "사서 E"),
    ("조기홍", "사서 E"),
]

# 익명화 검증 화이트리스트 (forbidden 리스트·PII guard rules에서 의도적으로 사용)
ANONYMIZE_KEEP_FILES = {
    "anonymize_pii.py",  # 자기 자신
    "test_handover_manual.py",  # 검증용 forbidden 리스트
    "test_school_budget_form.py",  # 검증용 forbidden 리스트
    "qa-validator.md",  # PII guard 검증 패턴
    "compliance-officer.md",  # PII guard 검증 패턴
    "pii-guard-hook-design.md",  # PII guard 디자인
}

# 익명화 제외 경로 (binary·외부 라이브러리·이미지)
EXCLUDE_PATTERNS = [
    "/.git/",
    "/.venv/",
    "/__pycache__/",
    "/node_modules/",
    "/.pytest_cache/",
    "/dist/",
    "/build/",
    "/.mypy_cache/",
    "/.ruff_cache/",
    "/scripts/anonymize_pii.py",  # 자기 자신 제외
]

# 익명화 제외 파일 (메타·라이선스)
EXCLUDE_FILES = {
    "LICENSE",
    "uv.lock",
    "poetry.lock",
}

# 텍스트 파일 확장자만 처리
INCLUDE_EXTS = {
    ".py", ".md", ".txt", ".yml", ".yaml", ".toml", ".json",
    ".sh", ".bat", ".ps1", ".html", ".css", ".js", ".tsx", ".ts",
    ".cfg", ".ini", ".env", ".gitignore", ".dockerignore",
}


def is_excluded(path: Path) -> bool:
    posix = path.as_posix()
    if any(pat in posix for pat in EXCLUDE_PATTERNS):
        return True
    if path.name in EXCLUDE_FILES or path.name in ANONYMIZE_KEEP_FILES:
        return True
    return bool(path.suffix and path.suffix not in INCLUDE_EXTS)


def anonymize_text(text: str) -> tuple[str, int]:
    count = 0
    for old, new in REPLACEMENTS:
        if old in text:
            count += text.count(old)
            text = text.replace(old, new)
    return text, count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("--dry-run 또는 --apply 중 하나 필수", file=sys.stderr)
        return 2

    root = args.root.resolve()
    total_files = 0
    total_count = 0
    changed_files: list[tuple[Path, int]] = []

    for path in root.rglob("*"):
        if not path.is_file() or is_excluded(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue

        new_text, count = anonymize_text(text)
        if count > 0:
            total_files += 1
            total_count += count
            changed_files.append((path, count))
            if args.apply:
                path.write_text(new_text, encoding="utf-8")

    mode = "적용" if args.apply else "DRY-RUN"
    print(f"[{mode}] {total_files} files, {total_count} 치환")
    for p, c in sorted(changed_files, key=lambda x: -x[1])[:20]:
        rel = p.relative_to(root)
        print(f"  {c:4d}  {rel}")
    if len(changed_files) > 20:
        print(f"  ... ({len(changed_files) - 20} more)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
