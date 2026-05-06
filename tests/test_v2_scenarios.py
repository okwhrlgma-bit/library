"""Cycle 38~40 — V2 §3 다중 에이전트 통합 시나리오 회귀.

3 시나리오:
1. N-Vote 환불 (P30 PortOne 결합·결제 사고 차단)
2. Hierarchical KORMARC 9 자료유형 builder 통합
3. Adversarial Red 시나리오 (PII·자관·KORMARC injection)
"""

from __future__ import annotations

from kormarc_auto.consensus import (
    ADVERSARIAL_DAILY_CAP,
    AdversarialFinding,
    Vote,
    aggregate_votes,
    classify_finding,
    decompose_into_units,
)


class TestRefundNVoteScenario:
    """Cycle 38 — 환불 N-Vote (V2 §3.2 + P30 PortOne)."""

    def test_unanimous_50000_refund_approved(self):
        # 5 agent 모두 50,000원 환불 동의 = 자동 처리
        votes = [
            Vote(agent_id=f"haiku-{i}", decision="refund_50000", confidence=0.95) for i in range(5)
        ]
        result = aggregate_votes(votes, threshold=0.8)
        assert result.threshold_met is True
        assert result.winning_decision == "refund_50000"

    def test_split_amount_goes_to_human(self):
        # 환불 금액 의견 갈림 = 사람 큐 (PO 직접 결정)
        votes = [
            Vote(agent_id="a1", decision="refund_30000"),
            Vote(agent_id="a2", decision="refund_50000"),
            Vote(agent_id="a3", decision="refund_50000"),
            Vote(agent_id="a4", decision="reject"),
            Vote(agent_id="a5", decision="reject"),
        ]
        result = aggregate_votes(votes, threshold=0.8)
        assert result.threshold_met is False
        assert "사람 큐" in result.note

    def test_high_value_refund_requires_higher_threshold(self):
        # 100만원 초과 환불 = threshold 0.9 (V2 §3.2 보수적)
        votes = [Vote(agent_id=f"a{i}", decision="refund_1500000") for i in range(8)]
        votes += [Vote(agent_id="a9", decision="reject"), Vote(agent_id="a10", decision="reject")]
        # 8/10 = 80% < 90% = 사람 큐
        result = aggregate_votes(votes, threshold=0.9)
        assert result.threshold_met is False

    def test_korean_decision_strings(self):
        # 환불 사유 한국어 결정 라벨
        votes = [
            Vote(agent_id="a1", decision="cancel_full"),
            Vote(agent_id="a2", decision="cancel_full"),
            Vote(agent_id="a3", decision="cancel_full"),
        ]
        result = aggregate_votes(votes)
        assert result.winning_decision == "cancel_full"


class TestHierarchicalKormarcMigration:
    """Cycle 39 — KORMARC 9 자료유형 builder 통합 (V2 §3.3)."""

    def test_9_material_types_decomposed(self):
        plan = decompose_into_units(
            goal="KORMARC 9 자료유형 builder·validator 통합",
            file_count=9,
            estimated_tokens_per_file=4000,
            parallel_workers=3,
        )
        assert len(plan.units) == 9
        # 각 자료유형 (단행본·연속·비도서·고서·전자책·전자저널·오디오북·멀티미디어·학위논문)

    def test_kormarc_token_budget(self):
        # 9 자료유형 × 4K = 36K + supervisor 5K + reviewer 8K = 49K
        plan = decompose_into_units(goal="X", file_count=9, estimated_tokens_per_file=4000)
        assert plan.total_estimated_tokens() == 49_000

    def test_174_file_full_repo_migration(self):
        # 자관 174 파일 = round-trip 100% baseline 회귀 검사 마이그레이션
        plan = decompose_into_units(
            goal="자관 174 파일 round-trip 회귀 검증",
            file_count=174,
            estimated_tokens_per_file=2500,
        )
        # supervisor 5K + 174×2.5K + reviewer 8K = 448K
        assert plan.total_estimated_tokens() == 5000 + 435_000 + 8000


class TestAdversarialRedScenarios:
    """Cycle 40 — Adversarial Red 시나리오 (V2 §3.4·PII·자관·KORMARC injection)."""

    def test_daily_cap_enforced(self):
        # V2 §3.4 일일 50회 캡 (비용 폭주 차단)
        assert ADVERSARIAL_DAILY_CAP == 50

    def test_pii_leak_finding(self):
        f = AdversarialFinding(
            finding_kind="data_leak",
            severity="critical",
            target_module="src/kormarc_auto/api/aggregator.py",
            repro_steps="ISBN 응답에 사용자 이메일 포함된 케이스",
            fix_proposal="email 필드 sanitize·anonymize_pii.py 정합",
        )
        assert f.finding_kind == "data_leak"
        assert f.severity == "critical"

    def test_marc_injection_finding(self):
        # MARC subfield delimiter (\x1f) injection 시나리오
        kind = classify_finding("input에 \\x1f 포함 시 MARC builder round-trip fail")
        # 'input' 키워드 = input_validation
        assert kind in ("injection", "input_validation", "logic_flaw")

    def test_korean_bypass_pattern(self):
        # 한국어 권한 우회 시나리오
        assert classify_finding("관리자 권한 우회") == "auth_bypass"
        assert classify_finding("인증 헤더 조작") == "auth_bypass"

    def test_jagwan_data_leak(self):
        # 자관 데이터 누설 = critical (헌법 위반·invariants)
        finding = AdversarialFinding(
            finding_kind="data_leak",
            severity="critical",
            target_module="src/kormarc_auto/api/search.py",
            repro_steps=("검색 응답에 D:\\내를건너서 숲으로 도서관 경로 노출 (자관 누설 시도)"),
            fix_proposal="anonymize_pii.py REPLACEMENTS 적용·자동 차단 hook",
        )
        assert "자관" in finding.repro_steps or "내를건너서" in finding.repro_steps
        assert finding.severity == "critical"

    def test_classify_8_kinds_coverage(self):
        # 8 finding_kind 모두 분류 가능
        cases = {
            "SQL injection": "injection",
            "인증 우회": "auth_bypass",
            "race condition": "race_condition",
            "메모리 고갈": "resource_exhaustion",
            "PII 누설": "data_leak",
            "MD5 weak": "crypto_weakness",
            "input validation 누락": "input_validation",
            "이상한 로직": "logic_flaw",
        }
        for desc, expected in cases.items():
            assert classify_finding(desc) == expected
