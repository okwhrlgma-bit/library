"""배치 처리 예제 — ISBN 목록 파일 → 다수 .mrc.

CLI로도 가능: `kormarc-auto batch examples/sample_isbns.txt`
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from kormarc_auto.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.argv = ["kormarc-auto", "batch", str(Path(__file__).parent / "sample_isbns.txt")]
    sys.exit(main())
