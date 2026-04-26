"""바이너리 어셔션 셋 — PO 자율성 가이드 레벨 3 (Eval-Driven).

Anthropic "Demystifying Evals" 패턴: true/false 단언만, 점수 없음.
매 commit 또는 야간 cron으로 실행. 실패 패턴 누적 → 다음 자율 디벨롭 우선순위 입력.

사용:
    python scripts/binary_assertions.py            # 전체 평가
    python scripts/binary_assertions.py --json     # JSON 출력 (CI/cron용)
    python scripts/binary_assertions.py --strict   # 1개 실패 시 exit 1
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
if not PYTHON.exists():
    PYTHON = Path(sys.executable)


def _run(cmd: list[str], *, timeout: int = 120) -> tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    return proc.returncode, proc.stdout, proc.stderr


# ── 어셔션 정의 (각각 (이름, 함수) 튜플; 함수는 True/False 반환) ────────────


def assert_pytest_passes() -> bool:
    rc, _, _ = _run([str(PYTHON), "-m", "pytest", "-q", "--no-header"], timeout=300)
    return rc == 0


def assert_ruff_clean() -> bool:
    rc, _, _ = _run([str(PYTHON), "-m", "ruff", "check", "src", "tests", "scripts"])
    return rc == 0


def assert_no_print_in_src() -> bool:
    """src/ 라이브러리 영역에 print() 디버깅 잔존 금지 (CLAUDE.md §4.1).
    CLI(cli.py)는 사용자 출력 목적이라 예외.
    """
    rc, _out, _ = _run(
        [
            str(PYTHON),
            "-c",
            "import re, pathlib, sys; bad = [p for p in pathlib.Path('src').rglob('*.py') if p.name != 'cli.py' and re.search(r'^\\s*print\\(', p.read_text(encoding=\"utf-8\", errors=\"replace\"), re.M)]; sys.exit(1 if bad else 0)",
        ]
    )
    return rc == 0


def assert_no_hardcoded_keys() -> bool:
    """src/에 sk-ant-api03 / kma_ 평문 키 금지."""
    rc, _, _ = _run(
        [
            str(PYTHON),
            "-c",
            "import re, pathlib, sys; bad = [p for p in pathlib.Path('src').rglob('*.py') if re.search(r'sk-ant-api03-[A-Za-z0-9]{20,}|kma_[A-Za-z0-9_-]{20,}', p.read_text(encoding=\"utf-8\", errors=\"replace\"))]; sys.exit(1 if bad else 0)",
        ]
    )
    return rc == 0


def assert_claude_md_exists() -> bool:
    return (ROOT / "CLAUDE.md").exists()


def assert_learnings_recent() -> bool:
    """learnings.md가 30일 이내 갱신."""
    p = ROOT / "learnings.md"
    if not p.exists():
        return False
    return (time.time() - p.stat().st_mtime) < 30 * 86400


def assert_tests_count_min() -> bool:
    """테스트가 최소 200건 이상 (회귀 방지)."""
    rc, out, _ = _run(
        [str(PYTHON), "-m", "pytest", "--collect-only", "-q"], timeout=60
    )
    if rc != 0:
        return False
    import re
    # "214 tests collected" — 라인 어디든
    for line in out.splitlines()[::-1]:
        m = re.search(r"(\d+)\s+tests?\s+collected", line)
        if m:
            return int(m.group(1)) >= 200
    return False


def assert_no_broken_imports() -> bool:
    rc, _, _ = _run(
        [
            str(PYTHON),
            "-c",
            "import kormarc_auto, kormarc_auto.cli, kormarc_auto.server.app, kormarc_auto.ui.streamlit_app, kormarc_auto.legal.deposit_form, kormarc_auto.acquisition.wishlist, kormarc_auto.interlibrary.exporters, kormarc_auto.classification.nlsh_relations, kormarc_auto.output.disposal_form, kormarc_auto.output.annual_statistics",
        ]
    )
    return rc == 0


def assert_pyproject_valid() -> bool:
    p = ROOT / "pyproject.toml"
    if not p.exists():
        return False
    rc, _, _ = _run(
        [str(PYTHON), "-c", "import tomllib; tomllib.loads(open('pyproject.toml', encoding='utf-8').read())"]
    )
    return rc == 0


def assert_legal_docs_present() -> bool:
    """이용약관 + 개인정보처리방침 + 베타 약관 모두 존재 (운영 감사 HIGH #1)."""
    return all(
        (ROOT / "docs" / name).exists()
        for name in ("terms-of-service.md", "privacy-policy.md", "terms-beta.md")
    )


def assert_server_endpoints_documented() -> bool:
    """주요 신규 엔드포인트가 코드에 존재."""
    p = ROOT / "src" / "kormarc_auto" / "server" / "app.py"
    if not p.exists():
        return False
    text = p.read_text(encoding="utf-8")
    required = (
        "/batch-vendor",
        "/migrate-from-kolas",
        "/billing/monthly",
        "/account/export",
        "/account/delete",
        "/legal/deposit-form",
    )
    return all(ep in text for ep in required)


def assert_ops_scripts_present() -> bool:
    """운영 자율성 핵심 스크립트 5종 존재 (PO 가이드 1·2·3·4단)."""
    required = [
        "scripts/binary_assertions.py",
        "scripts/golden_check.py",
        "scripts/aggregate_interviews.py",
        "scripts/rotate_logs.py",
        "scripts/backup_logs.py",
    ]
    return all((ROOT / r).exists() for r in required)


def assert_us_module_inactive() -> bool:
    """§33 미국 동아시아 모듈은 한국 BEP 전 inactive 유지 (ADR 0009)."""
    p = ROOT / "src" / "kormarc_auto" / "conversion" / "marc21_east_asian.py"
    if not p.exists():
        return False
    text = p.read_text(encoding="utf-8")
    return "ACTIVATED = False" in text


def assert_adr_count_min() -> bool:
    """ADR 7건 이상 (큰 결정 추적, PO 가이드 1단)."""
    adr_dir = ROOT / "docs" / "adr"
    if not adr_dir.exists():
        return False
    files = [p for p in adr_dir.glob("[0-9][0-9][0-9][0-9]-*.md") if p.is_file()]
    return len(files) >= 7


def assert_external_calls_have_timeout() -> bool:
    """src/kormarc_auto/api/ 외부 호출에 timeout 명시 (CLAUDE.md §4.2)."""
    rc, _, _ = _run(
        [
            str(PYTHON),
            "-c",
            "import re, pathlib, sys; pat = re.compile(r'(requests|httpx|http_session|session)\\.(get|post|put|delete|head)\\s*\\('); bad = []; "
            "[bad.extend([(str(p), i+1) for i, line in enumerate(p.read_text(encoding='utf-8', errors='replace').splitlines()) if pat.search(line) and 'timeout' not in line and 'timeout' not in (p.read_text(encoding='utf-8', errors='replace').splitlines() + [''])[i+1:i+5][0:4].__str__()]) for p in pathlib.Path('src/kormarc_auto/api').rglob('*.py') if p.exists()]; "
            "sys.exit(1 if bad else 0)",
        ]
    )
    return rc == 0


def assert_streamlit_tabs_count() -> bool:
    """Streamlit 도구 탭 14개 이상."""
    p = ROOT / "src" / "kormarc_auto" / "ui" / "streamlit_app.py"
    if not p.exists():
        return False
    text = p.read_text(encoding="utf-8")
    # 도구 탭 라벨 카운트
    tabs = (
        "로마자",
        "라벨 PDF",
        "자관 검색",
        "KDC 트리",
        "식별기호",
        "장서점검",
        "보고서",
        "알림",
        "납본",
        "등록번호",
        "상호대차",
        "수서 분석",
        "제적·폐기",
        "연간 통계",
    )
    return sum(1 for t in tabs if t in text) >= 14


# ── 실행 ───────────────────────────────────────────────────────────


ASSERTIONS: list[tuple[str, Callable[[], bool]]] = [
    ("pytest 모두 통과", assert_pytest_passes),
    ("ruff 위반 0", assert_ruff_clean),
    ("src/에 print() 디버깅 없음", assert_no_print_in_src),
    ("src/에 평문 API 키 없음", assert_no_hardcoded_keys),
    ("CLAUDE.md 존재", assert_claude_md_exists),
    ("learnings.md 30일 내 갱신", assert_learnings_recent),
    ("테스트 200건 이상", assert_tests_count_min),
    ("핵심 모듈 import 정상", assert_no_broken_imports),
    ("pyproject.toml 유효", assert_pyproject_valid),
    ("법적 문서 3종 존재", assert_legal_docs_present),
    ("신규 엔드포인트 6종 존재", assert_server_endpoints_documented),
    ("Streamlit 도구 탭 14개", assert_streamlit_tabs_count),
    ("외부 API 호출에 timeout 명시", assert_external_calls_have_timeout),
    ("운영 스크립트 5종 존재", assert_ops_scripts_present),
    ("ADR 7건 이상", assert_adr_count_min),
    ("§33 미국 모듈 inactive 유지", assert_us_module_inactive),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="바이너리 어셔션 평가")
    parser.add_argument("--json", action="store_true", help="JSON 출력")
    parser.add_argument("--strict", action="store_true", help="1개 실패 시 exit 1")
    args = parser.parse_args()

    results: list[dict[str, object]] = []
    for name, fn in ASSERTIONS:
        try:
            ok = fn()
        except Exception as e:
            ok = False
            results.append({"name": name, "ok": False, "error": str(e)})
            continue
        results.append({"name": name, "ok": ok})

    passed = sum(1 for r in results if r["ok"])
    total = len(results)
    rate = passed / total if total else 0

    if args.json:
        print(
            json.dumps(
                {
                    "passed": passed,
                    "total": total,
                    "rate": rate,
                    "results": results,
                    "ts": int(time.time()),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(f"바이너리 어셔션: {passed}/{total} ({rate:.0%})")
        for r in results:
            mark = "✓" if r["ok"] else "❌"
            line = f"  {mark} {r['name']}"
            if not r["ok"] and "error" in r:
                line += f" — {r['error']}"
            print(line)

    # 누적 로그 (PO 가이드 레벨 3 — eval/benchmark_results)
    log_path = ROOT / "logs" / "evals" / "binary_assertions.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(
            json.dumps(
                {"ts": int(time.time()), "passed": passed, "total": total, "rate": rate},
                ensure_ascii=False,
            )
            + "\n"
        )

    return 1 if (args.strict and passed < total) else 0


if __name__ == "__main__":
    sys.exit(main())
