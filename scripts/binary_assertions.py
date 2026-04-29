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


def assert_payment_adapter_present() -> bool:
    """PG 어댑터 stub 존재 (ADR 0007·0011 — 캐시카우 자동화 1축)."""
    p = ROOT / "src" / "kormarc_auto" / "server" / "payment_adapter.py"
    if not p.exists():
        return False
    text = p.read_text(encoding="utf-8")
    return all(
        s in text
        for s in (
            "class LocalManualAdapter",
            "class PortOneAdapter",
            "class StripeAdapter",
            "def get_adapter",
            "Protocol",
        )
    )


def assert_billing_pg_integrated() -> bool:
    """billing.py가 PG 어댑터 통합 (월말 자동 결제)."""
    p = ROOT / "src" / "kormarc_auto" / "server" / "billing.py"
    if not p.exists():
        return False
    text = p.read_text(encoding="utf-8")
    return "charge_monthly_via_pg" in text and "payment_adapter" in text


def assert_plan_act_agents() -> bool:
    """Explore-Plan-Act 3 에이전트 분리 (PO 가이드 §2.2·§2.4)."""
    agents_dir = ROOT / ".claude" / "agents"
    return all(
        (agents_dir / f"{name}.md").exists()
        for name in ("planner", "implementer", "explorer")
    )


def assert_pattern_library_exists() -> bool:
    """RSI Stage 2 패턴 라이브러리 누적 (PO 가이드 §5.6 Stage 2)."""
    pdir = ROOT / ".claude" / "patterns"
    if not pdir.exists():
        return False
    return len(list(pdir.glob("*.md"))) >= 10


def assert_stop_double_gate_hook() -> bool:
    """이중 게이트 Stop hook 존재 (PO 가이드 §8.11)."""
    p = ROOT / ".claude" / "hooks" / "stop-double-gate.py"
    if not p.exists():
        return False
    text = p.read_text(encoding="utf-8")
    return all(
        s in text for s in ("<<<TASK_COMPLETE>>>", "stop_hook_active", "binary_assertions")
    )


def assert_trust_counter_hook() -> bool:
    """Trust Counter hook 존재 (RSI Stage 1)."""
    p = ROOT / ".claude" / "hooks" / "post-trust.py"
    return p.exists() and "trust.json" in p.read_text(encoding="utf-8")


def assert_irreversible_guard_present() -> bool:
    """PreToolUse 정규식 가드 hook 존재 (PO 가이드 §8.10)."""
    p = ROOT / ".claude" / "hooks" / "irreversible-guard.sh"
    if not p.exists():
        return False
    text = p.read_text(encoding="utf-8")
    # 핵심 패턴 7개 모두 검사
    required = [
        "rm",
        "mkfs",
        "push.*--force",
        "filter-branch",
        "DROP",
        "FLUSHALL",
        "KORMARC_EAST_ASIAN_ACTIVATED",
    ]
    return all(p in text for p in required)


def assert_rules_present() -> bool:
    """`.claude/rules/` 도메인·자율 게이트 룰 파일 존재 (Phase 2)."""
    rules_dir = ROOT / ".claude" / "rules"
    return (
        rules_dir.exists()
        and (rules_dir / "kormarc-domain.md").exists()
        and (rules_dir / "autonomy-gates.md").exists()
    )


def assert_agents_have_memory() -> bool:
    """모든 에이전트 frontmatter에 `memory: project` (PO 가이드 §1.5)."""
    agents_dir = ROOT / ".claude" / "agents"
    if not agents_dir.exists():
        return False
    for p in agents_dir.glob("*.md"):
        text = p.read_text(encoding="utf-8")
        if "memory:" not in text:
            return False
    return True


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


def assert_application_level_module() -> bool:
    """KORMARC 2023.12 M/A/O 적용 수준 모듈 + validate_record_full 존재."""
    rc, _, _ = _run([
        str(PYTHON), "-c",
        "import sys; sys.path.insert(0, 'src'); "
        "from kormarc_auto.kormarc.application_level import "
        "M_FIELDS, M_FIELD_GROUPS, A_FIELD_GROUPS, "
        "determine_application_level, validate_application_level; "
        "from kormarc_auto.kormarc.validator import validate_record_full; "
        "assert len(M_FIELDS) >= 5 and len(M_FIELD_GROUPS) >= 3",
    ])
    return rc == 0


def assert_real_mrc_validator_present() -> bool:
    """자관 .mrc 174 전수 검증 스크립트 + 인코딩 fallback 정합 (영업 정량 ★)."""
    p = ROOT / "scripts" / "validate_real_mrc.py"
    if not p.exists():
        return False
    text = p.read_text(encoding="utf-8")
    return "validate_application_level" in text and "_parse_mrc_any_encoding" in text


def assert_prefix_discovery_module() -> bool:
    """049 prefix 자동 발견 모듈 (다른 자관 PILOT 즉시 정합 ★)."""
    rc, _, _ = _run([
        str(PYTHON), "-c",
        "import sys; sys.path.insert(0, 'src'); "
        "from kormarc_auto.librarian_helpers.prefix_discovery import "
        "PrefixDiscoverer, PrefixSummary; "
        "summary = PrefixSummary(0, {}, (), 1.0); "
        "assert 'registration_prefix' in summary.to_yaml_snippet()",
    ])
    return rc == 0


def assert_portone_webhook_module() -> bool:
    """포트원 v2 webhook 처리 모듈 (ADR 0007 트리거 후 활성)."""
    rc, _, _ = _run([
        str(PYTHON), "-c",
        "import sys; sys.path.insert(0, 'src'); "
        "from kormarc_auto.server.portone_webhook import "
        "WebhookEvent, parse_event, verify_signature, handle_event; "
        "import inspect; "
        "assert callable(verify_signature)",
    ])
    return rc == 0


def assert_pilot_collect_script() -> bool:
    """PILOT 시연 결과 수집 스크립트 (4 페르소나 정합)."""
    p = ROOT / "scripts" / "pilot_collect.py"
    if not p.exists():
        return False
    text = p.read_text(encoding="utf-8")
    return all(persona in text for persona in ("macro", "acquisition", "general", "video"))


def assert_changelog_v0_4_37() -> bool:
    """CHANGELOG_NIGHT v0.4.37 갱신 (33+ commit 시리즈 통합)."""
    p = ROOT / "CHANGELOG_NIGHT.md"
    if not p.exists():
        return False
    text = p.read_text(encoding="utf-8")
    return "v0.4.37" in text and "99.82" in text


def assert_sales_funnel_module() -> bool:
    """영업 funnel tracker (가입→활성→한도→결제) + 페르소나별 분석."""
    p = ROOT / "scripts" / "sales_funnel.py"
    if not p.exists():
        return False
    text = p.read_text(encoding="utf-8")
    return all(name in text for name in ("compute_funnel", "FunnelMetrics", "funnel_by_persona"))


def assert_aggregate_by_persona_function() -> bool:
    """aggregate_interviews.by_persona — 4 페르소나별 NPS·시간 절감 분석."""
    p = ROOT / "scripts" / "aggregate_interviews.py"
    if not p.exists():
        return False
    text = p.read_text(encoding="utf-8")
    return "def by_persona" in text and "kla_quotable_count" in text


def assert_librarian_5min_cheatsheet() -> bool:
    """사서 5분 cheat sheet (PILOT 1주차 사서 친화 종이 한 장)."""
    p = ROOT / "docs" / "sales" / "librarian-5min-cheatsheet.md"
    if not p.exists():
        return False
    text = p.read_text(encoding="utf-8")
    return "kormarc-auto isbn" in text and "99.82" in text


def assert_claude_md_slim() -> bool:
    """CLAUDE.md 250줄 이하 유지 (Anthropic 200 권장·여유 50줄·ADR-0013)."""
    p = ROOT / "CLAUDE.md"
    if not p.exists():
        return False
    line_count = sum(1 for _ in p.open(encoding="utf-8"))
    return line_count <= 250


def assert_cli_pilot_funnel_commands() -> bool:
    """CLI 3 명령 (prefix-discover·pilot-collect·sales-funnel) 통합."""
    p = ROOT / "src" / "kormarc_auto" / "cli.py"
    if not p.exists():
        return False
    text = p.read_text(encoding="utf-8")
    return all(cmd in text for cmd in ('"prefix-discover"', '"pilot-collect"', '"sales-funnel"'))


def assert_pilot_week_manuals() -> bool:
    """PILOT 4주차 액션 매뉴얼 시리즈 (week1·2·3·4 모두)."""
    base = ROOT / "docs" / "sales"
    return all((base / f"pilot-week{n}-action-manual.md").exists() for n in range(1, 5))


def assert_research_14_part_manuals() -> bool:
    """14-Part 종합 매뉴얼 (research/part1~14) 모두 존재 ★."""
    base = ROOT / "docs" / "research"
    part_files = list(base.glob("part*.md"))
    # part1~6 + part7~14 = 14건 이상
    part_numbers = set()
    for p in part_files:
        # 파일명 'part14-...' 같은 패턴에서 숫자 추출
        name = p.stem
        if name.startswith("part") and "-" in name:
            try:
                num = int(name.split("-")[0][4:])
                part_numbers.add(num)
            except ValueError:
                pass
    return len(part_numbers) >= 14 and 14 in part_numbers


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
    (".claude/rules/ 룰 파일 존재", assert_rules_present),
    ("에이전트 memory:project 모두 적용", assert_agents_have_memory),
    ("PreToolUse 정규식 가드 7패턴", assert_irreversible_guard_present),
    ("이중 게이트 Stop hook", assert_stop_double_gate_hook),
    ("Trust Counter hook (RSI 1단)", assert_trust_counter_hook),
    ("Explore-Plan-Act 3 에이전트", assert_plan_act_agents),
    ("Pattern Library 누적 ≥10", assert_pattern_library_exists),
    ("PG 어댑터 stub (ADR 0007·0011)", assert_payment_adapter_present),
    ("billing.py PG 통합", assert_billing_pg_integrated),
    ("M/A/O 적용 수준 모듈 (KORMARC 2023.12)", assert_application_level_module),
    ("자관 .mrc 174 검증 스크립트", assert_real_mrc_validator_present),
    ("049 prefix 자동 발견 모듈", assert_prefix_discovery_module),
    ("포트원 v2 webhook 처리 모듈", assert_portone_webhook_module),
    ("PILOT 시연 수집 스크립트 (4 페르소나)", assert_pilot_collect_script),
    ("CHANGELOG_NIGHT v0.4.37 갱신", assert_changelog_v0_4_37),
    ("영업 funnel tracker (페르소나별 결제 전환률)", assert_sales_funnel_module),
    ("aggregate_interviews.by_persona (KLA 데이터)", assert_aggregate_by_persona_function),
    ("사서 5분 cheat sheet (PILOT 친화)", assert_librarian_5min_cheatsheet),
    ("CLAUDE.md 250줄 이하 (Anthropic 200 권장·ADR-0013)", assert_claude_md_slim),
    ("CLI 3 명령 (prefix·pilot·funnel) 통합", assert_cli_pilot_funnel_commands),
    ("PILOT 4주차 매뉴얼 시리즈 (week1~4)", assert_pilot_week_manuals),
    ("14-Part 종합 매뉴얼 (research/part1~14)", assert_research_14_part_manuals),
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
