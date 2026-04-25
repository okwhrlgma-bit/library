"""운영 데이터 백업·복구.

백업 대상:
- logs/usage.json (키별 사용량 — 이거 잃으면 모든 사서 quota 0으로 리셋!)
- logs/usage.jsonl, logs/feedback.jsonl, logs/signups.jsonl
- .env (시크릿 — 압축에 포함, 주의)

사용:
    python scripts/backup_logs.py                       # 백업 (./backups/<날짜>.zip)
    python scripts/backup_logs.py --restore <zip>       # 복구
    python scripts/backup_logs.py --output /D/backups   # 별 폴더
"""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import sys
import time
import zipfile
from pathlib import Path

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent

BACKUP_TARGETS = [
    "logs/usage.json",
    "logs/usage.jsonl",
    "logs/feedback.jsonl",
    "logs/signups.jsonl",
]

logger = logging.getLogger(__name__)


def do_backup(output_dir: Path, *, include_env: bool = False) -> Path:
    """현재 운영 데이터를 zip으로."""
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    out = output_dir / f"kormarc-backup-{stamp}.zip"

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in BACKUP_TARGETS:
            path = ROOT / rel
            if path.exists():
                zf.write(path, arcname=rel)
                print(f"  ✓ {rel} ({path.stat().st_size} bytes)")
            else:
                print(f"  · {rel} (없음, 스킵)")

        if include_env and (ROOT / ".env").exists():
            zf.write(ROOT / ".env", arcname=".env")
            print("  ⚠ .env 포함 (시크릿) — 백업 파일을 안전하게 보관할 것")

    print(f"\n✓ 백업 완료: {out} ({out.stat().st_size} bytes)")
    return out


def do_restore(zip_path: Path, *, force: bool = False) -> None:
    """zip에서 복구. 기본은 logs/만 복구하고 .env는 .env.restored로."""
    if not zip_path.exists():
        print(f"❌ 파일 없음: {zip_path}")
        sys.exit(1)

    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            target = ROOT / name
            if name == ".env" and not force:
                target = ROOT / ".env.restored"
                print(f"  → {name} 은 .env.restored 로 (기존 .env 보호)")

            target.parent.mkdir(parents=True, exist_ok=True)

            if target.exists() and not force and name != ".env":
                bak = target.with_suffix(target.suffix + ".bak")
                shutil.copy2(target, bak)
                print(f"  · 기존 {name} → {bak.name} 백업")

            with zf.open(name) as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            print(f"  ✓ {name} 복구")

    print(f"\n✓ 복구 완료 from {zip_path}")
    print("  주의: 서버가 실행 중이면 재시작해야 카운터가 갱신됨")


def main() -> int:
    parser = argparse.ArgumentParser(description="운영 데이터 백업·복구")
    parser.add_argument("--output", default="backups", help="백업 저장 폴더")
    parser.add_argument("--include-env", action="store_true", help=".env도 포함 (보안 주의)")
    parser.add_argument("--restore", default=None, help="복구할 zip 파일 경로")
    parser.add_argument("--force", action="store_true", help="복구 시 기존 파일 덮어쓰기")
    args = parser.parse_args()

    if args.restore:
        do_restore(Path(args.restore), force=args.force)
    else:
        out_dir = Path(args.output)
        if not out_dir.is_absolute():
            out_dir = ROOT / out_dir
        do_backup(out_dir, include_env=args.include_env)
    return 0


if __name__ == "__main__":
    sys.exit(main())
