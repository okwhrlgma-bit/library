"""로그 회전·익명화 — 개인정보보호법 §21 (불필요해진 정보 즉시 파기) 준수.

- logs/usage.jsonl: 90일 초과는 월별 .jsonl.gz로 압축, 1년 초과는 익명화
- logs/feedback.jsonl: 90일 초과 익명화 (api_key 해시 → "anon")
- logs/signups.jsonl: 90일 초과 이메일 도메인만 남김 (예: librarian@school.kr → "(domain) school.kr")

매주 cron 또는 Windows 작업 스케줄러로 1회 실행 권장.
운영 환경에서는 백업(scripts/backup_logs.py) 먼저 후 실행.

사용:
    python scripts/rotate_logs.py                         # 기본 (90일/365일 정책)
    python scripts/rotate_logs.py --dry-run               # 시뮬레이션만
    python scripts/rotate_logs.py --max-age-days 60       # 더 짧게
"""

from __future__ import annotations

import argparse
import gzip
import json
import logging
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "logs"
ARCHIVE_DIR = LOG_DIR / "archive"

logger = logging.getLogger(__name__)


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _compress_to_archive(rows: list[dict], year_month: str, kind: str) -> Path:
    """월별 아카이브 .jsonl.gz로."""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    out = ARCHIVE_DIR / f"{kind}-{year_month}.jsonl.gz"
    with gzip.open(out, "wt", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return out


def _anonymize_signup(row: dict) -> dict:
    """이메일에서 도메인만, 도서관명 제거."""
    email = str(row.get("email", ""))
    domain = email.split("@")[-1] if "@" in email else "(unknown)"
    return {
        "ts": row.get("ts"),
        "email_domain": domain,
        "key_hash": row.get("key_hash") or row.get("api_key_hash"),
    }


def _anonymize_feedback(row: dict) -> dict:
    """api_key 해시 → 'anon', 코멘트는 보존 (피드백 가치)."""
    return {
        "ts": row.get("ts"),
        "key_hash": "anon",
        "rating": row.get("rating"),
        "category": row.get("category"),
        "comment": row.get("comment"),
    }


def rotate(
    *,
    max_age_days: int = 90,
    anon_age_days: int = 365,
    dry_run: bool = False,
) -> dict[str, int]:
    """기본 정책: 90일 초과 사용량 로그 → 월별 압축. 1년 초과 → 익명화."""
    now = int(time.time())
    cutoff_archive = now - max_age_days * 86400
    cutoff_anon = now - anon_age_days * 86400
    stats = {"archived": 0, "anonymized": 0, "kept": 0}

    # ── usage.jsonl 회전 ───────────────────────────────
    usage_path = LOG_DIR / "usage.jsonl"
    rows = _read_jsonl(usage_path)
    if rows:
        keep, archive_rows = [], []
        for r in rows:
            ts = int(r.get("ts", now))
            if ts < cutoff_archive:
                archive_rows.append(r)
            else:
                keep.append(r)

        if archive_rows:
            by_month: dict[str, list[dict]] = defaultdict(list)
            for r in archive_rows:
                ym = time.strftime("%Y-%m", time.localtime(r.get("ts", now)))
                by_month[ym].append(r)
            for ym, m_rows in by_month.items():
                if dry_run:
                    print(f"  [dry] usage {ym}: {len(m_rows)}건 → archive")
                else:
                    out = _compress_to_archive(m_rows, ym, "usage")
                    print(f"  ✓ usage {ym}: {len(m_rows)}건 → {out.name}")
                stats["archived"] += len(m_rows)
            if not dry_run:
                _write_jsonl(usage_path, keep)
        stats["kept"] += len(keep)

    # ── signups.jsonl 익명화 ────────────────────────────
    signup_path = LOG_DIR / "signups.jsonl"
    rows = _read_jsonl(signup_path)
    if rows:
        out_rows: list[dict] = []
        anon_count = 0
        for r in rows:
            ts = int(r.get("ts", now))
            if ts < cutoff_anon:
                out_rows.append(_anonymize_signup(r))
                anon_count += 1
            else:
                out_rows.append(r)
        if anon_count:
            if dry_run:
                print(f"  [dry] signups: {anon_count}건 익명화")
            else:
                _write_jsonl(signup_path, out_rows)
                print(f"  ✓ signups: {anon_count}건 익명화")
        stats["anonymized"] += anon_count

    # ── feedback.jsonl 익명화 ──────────────────────────
    fb_path = LOG_DIR / "feedback.jsonl"
    rows = _read_jsonl(fb_path)
    if rows:
        out_rows = []
        anon_count = 0
        for r in rows:
            ts = int(r.get("ts", now))
            if ts < cutoff_anon:
                out_rows.append(_anonymize_feedback(r))
                anon_count += 1
            else:
                out_rows.append(r)
        if anon_count:
            if dry_run:
                print(f"  [dry] feedback: {anon_count}건 익명화")
            else:
                _write_jsonl(fb_path, out_rows)
                print(f"  ✓ feedback: {anon_count}건 익명화")
        stats["anonymized"] += anon_count

    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description="로그 회전·익명화")
    parser.add_argument("--max-age-days", type=int, default=90, help="활성 로그 보관 일수")
    parser.add_argument("--anon-age-days", type=int, default=365, help="익명화 시작 일수")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(f"📋 로그 회전 시작 (활성 ≤{args.max_age_days}일, 익명화 ≥{args.anon_age_days}일)")
    if args.dry_run:
        print("  [dry-run 모드 — 실제 변경 없음]")

    stats = rotate(
        max_age_days=args.max_age_days,
        anon_age_days=args.anon_age_days,
        dry_run=args.dry_run,
    )

    print(
        f"\n✓ 완료 — 아카이브 {stats['archived']}건 / 익명화 {stats['anonymized']}건 / 보존 {stats['kept']}건"
    )
    print("  개인정보보호법 §21 준수 — 매주 1회 실행 권장 (cron/작업 스케줄러)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
