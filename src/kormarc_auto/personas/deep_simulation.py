"""Cycle 61 (Part 96·ADR 0045) — 8 ICP 사서 페르소나 깊이 시뮬.

PO 명령 (2026-05-06): "사서 페르소나로 앱 전반 모든 부분 약간의 놓침도 없이 확인".

8 페르소나 × 앱 5 영역 (UI·기능·가격·영업·법무) = 40 매트릭스.
"""

from __future__ import annotations

from dataclasses import dataclass

PMF_THRESHOLD = 70  # 종합 점수 ≥ 70 = PMF 정합 (Beta ACCEPT)


@dataclass(frozen=True)
class Persona:
    """8 ICP 페르소나 = Part 96 정합."""

    id: str
    name: str
    age: int
    role: str
    market_size: int  # 관 수
    payment_intent: int  # 0~100
    payment_authority: int  # 0~100
    primary_pain: str
    primary_message: str
    secondary_message: str
    decision_maker: str
    sales_channel: str


# 8 ICP 페르소나 (Part 96·외부 자료 종합·인터뷰 0건·가설)
EIGHT_ICP_PERSONAS: tuple[Persona, ...] = (
    Persona(
        id="P1",
        name="김민지",
        age=30,
        role="작은도서관 1인 사서 (자치구 운영)",
        market_size=6_830,
        payment_intent=90,
        payment_authority=10,  # 자치구 예산
        primary_pain="KOLAS III·KORMARC 학습 시간 X·신착 권당 8~12분",
        primary_message="퇴근 시간을 돌려드립니다",
        secondary_message="야근 = 권당 1.5분이 결정",
        decision_maker="자치구 문화과·구청",
        sales_channel="자치구 단관 수의계약 2천만원·디지털서비스몰",
    ),
    Persona(
        id="P2",
        name="박지혜",
        age=45,
        role="학교도서관 사서교사 1인",
        market_size=1_700,
        payment_intent=85,
        payment_authority=50,  # 학교운영위
        primary_pain="자료구입비 3% 의무·신학기 집중·KOLAS III 종료",
        primary_message="자료구입비 3% 효율",
        secondary_message="신학기 신착 100권 = 5시간 절감",
        decision_maker="학교운영위·교장",
        sales_channel="학교장터 s2b.kr",
    ),
    Persona(
        id="P3",
        name="최지영",
        age=52,
        role="공공도서관 일반 사서 (계약직)",
        market_size=1_296,  # 다중 사서
        payment_intent=60,  # 월급제·시간 절감 ≠ 동기
        payment_authority=5,  # 시·군·구청
        primary_pain="KOLAS III 종료 마이그레이션·결정권 X",
        primary_message="민원 ↓ + 오류 ↓",
        secondary_message="KOLAS III 종료 마이그레이션 자동",
        decision_maker="시·군·구청·CSAP 인증 요구",
        sales_channel="공공기관 (인증 후·자치구 일괄)",
    ),
    Persona(
        id="P4",
        name="이수진",
        age=28,
        role="대학도서관 사서 (3년차)",
        market_size=400,
        payment_intent=80,
        payment_authority=20,  # 도서관장·시스템팀
        primary_pain="학술 RDA·MODS·SCI·DOI 통합 X",
        primary_message="RDA·MODS 통합·국산",
        secondary_message="ProQuest 대체",
        decision_maker="도서관장·시스템팀",
        sales_channel="KERIS·학술도서관 컨소시엄",
    ),
    Persona(
        id="P5",
        name="정현우",
        age=38,
        role="자관 사서 (PO 자관·8명 운영)",
        market_size=1,  # PO 자관 1관
        payment_intent=100,  # PO 본인
        payment_authority=95,  # 운영위 직접 영향
        primary_pain="N=1·외부 검증 X",
        primary_message="자관 양식·6년 NPS·즉시 도입",
        secondary_message="외부 검증 0관·일반화 위험",
        decision_maker="PO 운영위 직접",
        sales_channel="N/A (베타 PILOT 1관)",
    ),
    Persona(
        id="P6",
        name="윤서연",
        age=24,
        role="자원봉사 카탈로깅 + 사서교사 사후 검수",
        market_size=10_500,  # 86% 학교 = 12,200 × 0.86
        payment_intent=70,  # 시간·자원봉사
        payment_authority=15,  # 사서교사 P2 경유
        primary_pain="KORMARC 표준 X·정형화 위저드 부재",
        primary_message="자원봉사도 5분 안",
        secondary_message="사서교사 검수 부담 ↓",
        decision_maker="학교운영위 (P2 경유)",
        sales_channel="P2 경유·학교장터",
    ),
    Persona(
        id="P7",
        name="강민호",
        age=48,
        role="1인 작은도서관 + 책나래 (장애인)",
        market_size=5,  # 특수
        payment_intent=85,
        payment_authority=30,  # 자치구·문화재단·복지재단 다중
        primary_pain="책나래·책바다·책이음·책두레·책단비 5종 + 점자",
        primary_message="책나래 5종 통합",
        secondary_message="장애인 도서관 SaaS 1호",
        decision_maker="자치구·문화재단·복지재단",
        sales_channel="다중·복지재단 협력",
    ),
    Persona(
        id="P8",
        name="이태경",
        age=55,
        role="도서관장 (2~3관 운영)",
        market_size=200,
        payment_intent=90,
        payment_authority=90,  # 직접 결재
        primary_pain="사서 야근 = 본인 책임·KOLAS III 마이그 결정",
        primary_message="사서 야근 ↓ = 본인 평판 ↑",
        secondary_message="민원 ↓·자료구입비 효율",
        decision_maker="도서관장 직접 (월 30~50만원)",
        sales_channel="KLMA·KLA·도서관 백서 광고",
    ),
)


@dataclass(frozen=True)
class PersonaScore:
    """페르소나별 앱 5 영역 점수 (Part 96 매트릭스 정합)."""

    persona_id: str
    ui_score: int  # UI/UX 적합도
    feature_score: int  # 기능 적합도
    price_score: int  # 가격 적합도
    sales_score: int  # 영업 가능성
    legal_score: int  # 법무·인증
    total_pmf: int  # 가중 평균 (UI 15·feature 30·price 20·sales 25·legal 10)
    gaps: tuple[str, ...]


def score_app_for_persona(persona: Persona) -> PersonaScore:
    """페르소나별 앱 5 영역 점수 계산 (Cycle 61 = 가설).

    가중치 (외부 매출 보고서 + Part 51 정합):
    - UI 15%·기능 30%·가격 20%·영업 25%·법무 10%
    """
    if persona.id == "P1":
        ui, feat, price, sales, legal = 90, 85, 70, 60, 80
        gaps = ("자치구 채널 미진입", "결제 권한 X")
    elif persona.id == "P2":
        ui, feat, price, sales, legal = 85, 80, 80, 70, 80
        gaps = ("학교장터 등록 X 사업자 등록 후",)
    elif persona.id == "P3":
        ui, feat, price, sales, legal = 70, 75, 50, 30, 50
        gaps = ("CSAP 인증 X", "월급제 = 시간 절감 ≠ 동기", "결제 권한 0")
    elif persona.id == "P4":
        ui, feat, price, sales, legal = 80, 65, 60, 40, 75
        gaps = ("학술 RDA·MODS 통합 X", "DOI·SCI 식별자 X")
    elif persona.id == "P5":
        ui, feat, price, sales, legal = 95, 95, 100, 100, 100
        gaps = ("N=1 편향",)
    elif persona.id == "P6":
        ui, feat, price, sales, legal = 90, 75, 80, 60, 75
        gaps = ("단순 모드 위저드 부재", "자원봉사 친화 ↓")
    elif persona.id == "P7":
        ui, feat, price, sales, legal = 85, 70, 75, 50, 70
        gaps = ("책나래 5종 통합 부분 (책이음만)", "점자·DAISY 표준 X")
    elif persona.id == "P8":
        ui, feat, price, sales, legal = 75, 85, 90, 80, 85
        gaps = ("경영자 어휘·KPI 대시보드 부재",)
    else:
        ui, feat, price, sales, legal = 50, 50, 50, 50, 50
        gaps = ("미정의",)

    total = round(ui * 0.15 + feat * 0.30 + price * 0.20 + sales * 0.25 + legal * 0.10)
    return PersonaScore(
        persona_id=persona.id,
        ui_score=ui,
        feature_score=feat,
        price_score=price,
        sales_score=sales,
        legal_score=legal,
        total_pmf=total,
        gaps=gaps,
    )


def app_coverage_matrix() -> list[PersonaScore]:
    """8 페르소나 × 5 영역 매트릭스 (Cycle 61 시뮬)."""
    return [score_app_for_persona(p) for p in EIGHT_ICP_PERSONAS]


def find_underserved_personas(threshold: int = PMF_THRESHOLD) -> list[Persona]:
    """PMF threshold 미달 페르소나 (적용 우선순위 후보)."""
    matrix = app_coverage_matrix()
    persona_map = {p.id: p for p in EIGHT_ICP_PERSONAS}
    return [persona_map[s.persona_id] for s in matrix if s.total_pmf < threshold]


def cumulative_market_pmf() -> dict[str, int]:
    """PMF 정합 페르소나의 누적 시장 = 영업 가능 TAM."""
    matrix = {s.persona_id: s for s in app_coverage_matrix()}
    persona_map = {p.id: p for p in EIGHT_ICP_PERSONAS}

    pmf_pass_market = sum(
        p.market_size for pid, p in persona_map.items() if matrix[pid].total_pmf >= PMF_THRESHOLD
    )
    pmf_fail_market = sum(
        p.market_size for pid, p in persona_map.items() if matrix[pid].total_pmf < PMF_THRESHOLD
    )
    total_market = pmf_pass_market + pmf_fail_market

    return {
        "pmf_pass_market": pmf_pass_market,
        "pmf_fail_market": pmf_fail_market,
        "total_market": total_market,
        "pmf_pass_pct": round(pmf_pass_market / total_market * 100) if total_market else 0,
    }


def render_persona_summary() -> str:
    """CLI/report 인용용 매트릭스 텍스트."""
    lines = ["=== 8 ICP × 앱 5 영역 매트릭스 (Cycle 61·시뮬) ==="]
    lines.append(
        f"{'ID':4}{'이름':10}{'UI':>5}{'기능':>5}{'가격':>5}{'영업':>5}{'법무':>5}{'PMF':>5}"
    )
    lines.append("-" * 60)
    for s in app_coverage_matrix():
        p = next(pp for pp in EIGHT_ICP_PERSONAS if pp.id == s.persona_id)
        flag = "✓" if s.total_pmf >= PMF_THRESHOLD else "✗"
        lines.append(
            f"{p.id:4}{p.name:10}"
            f"{s.ui_score:>5}{s.feature_score:>5}{s.price_score:>5}"
            f"{s.sales_score:>5}{s.legal_score:>5}{s.total_pmf:>5}{flag}"
        )
    market = cumulative_market_pmf()
    lines.append("")
    lines.append(
        f"PMF 정합 시장: {market['pmf_pass_market']:,}관 / {market['total_market']:,}관 "
        f"({market['pmf_pass_pct']}%)"
    )
    lines.append("⚠ 가설·시뮬·인터뷰 0건. 실 PMF 결정 = SALES-1 사서 5명 인터뷰 후.")
    return "\n".join(lines)


__all__ = [
    "EIGHT_ICP_PERSONAS",
    "PMF_THRESHOLD",
    "Persona",
    "PersonaScore",
    "app_coverage_matrix",
    "cumulative_market_pmf",
    "find_underserved_personas",
    "render_persona_summary",
    "score_app_for_persona",
]
