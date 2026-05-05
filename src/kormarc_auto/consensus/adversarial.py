"""갈래 B Cycle 33 (V2 §3.4) — Adversarial Pair (Red·Blue).

Red agent = 코드/입력 깨뜨릴 시나리오 생성·Blue agent = 패치.
일일 50회 캡 (V2 §3.4 비용 폭주 방지).

본 모듈 = scaffolding·LLM 호출은 외부.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ADVERSARIAL_DAILY_CAP: int = 50

FindingKind = Literal[
    "input_validation",  # 입력 검증 누락
    "auth_bypass",  # 인증 우회
    "injection",  # SQL·command·prompt injection
    "race_condition",  # 동시성
    "resource_exhaustion",  # CPU·메모리·디스크
    "data_leak",  # PII·자관 누설
    "crypto_weakness",  # 암호 취약
    "logic_flaw",  # 비즈니스 로직 결함
]


@dataclass(frozen=True)
class AdversarialFinding:
    """Red agent 발견."""

    finding_kind: FindingKind
    severity: str  # "critical"·"high"·"medium"·"low"
    target_module: str
    repro_steps: str
    fix_proposal: str = ""

    def to_dict(self) -> dict:
        return {
            "finding_kind": self.finding_kind,
            "severity": self.severity,
            "target_module": self.target_module,
            "repro_steps": self.repro_steps,
            "fix_proposal": self.fix_proposal,
        }


def classify_finding(description: str) -> FindingKind:
    """설명 텍스트 → finding kind 자동 분류 (단순 휴리스틱)."""
    desc = description.lower()
    if any(k in desc for k in ("sql", "injection", "prompt", "xss", "command")):
        return "injection"
    if any(k in desc for k in ("auth", "인증", "권한", "bypass", "우회")):
        return "auth_bypass"
    if any(k in desc for k in ("race", "동시", "concurrent", "deadlock")):
        return "race_condition"
    if any(k in desc for k in ("memory", "cpu", "disk", "메모리", "고갈", "exhaust")):
        return "resource_exhaustion"
    if any(k in desc for k in ("leak", "누설", "pii", "자관", "개인정보")):
        return "data_leak"
    if any(k in desc for k in ("crypto", "암호", "weak", "md5", "sha1")):
        return "crypto_weakness"
    if any(k in desc for k in ("validation", "검증", "input")):
        return "input_validation"
    return "logic_flaw"
