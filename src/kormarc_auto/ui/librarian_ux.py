"""Cycle 60 (UI/UX·헌법 §12) — 사서 친화 UI 헬퍼.

Part 49 (사서 깊이 친화)·Part 51 (페르소나 56% 전환) 정합:
- 70+ 사서 어휘 (KORMARC·KOLAS·DLS·관제·별치)
- 사서 일과 사이클 (수서·정리·배가·납본)
- 권위 인용 (NLK·KAIT·문체부)
- 시간 절감 시각화 (권당 8분 → 2분)
"""

from __future__ import annotations

# 사서 일과 사이클 (Part 49·5 단계)
LIBRARIAN_DAILY_CYCLE = [
    ("수서", "도서 선정·발주·수령"),
    ("정리", "MARC 작성·청구기호·라벨"),
    ("배가", "서가 배치·신간 코너"),
    ("이용", "대출·반납·예약"),
    ("납본", "KOLAS·DLS·KERIS 보고"),
]

# 사서 친화 어휘 매핑 (IT 전문 → 사서 일상)
LIBRARIAN_VOCABULARY = {
    "import": "반입",
    "export": "내보내기",
    "validation": "검증",
    "metadata": "메타데이터·서지",
    "field": "필드·항목",
    "tag": "태그·표시",
    "indicator": "지시기호",
    "subfield": "식별기호·서브필드",
    "leader": "리더 (00X 제어 필드)",
    "round-trip": "왕복 검증·복원율",
    "throughput": "처리량",
    "latency": "응답 속도",
}


def time_saved_estimate(records_processed: int) -> dict[str, str]:
    """시간 절감 시각화 (헌법 §0 = 권당 8분 → 2분).

    Args:
        records_processed: 처리한 권 수

    Returns:
        절감 시간·사서 시급 환산·연간 누적 추정
    """
    minutes_saved = records_processed * 6  # 8분 → 2분 = 6분 절감
    hours_saved = minutes_saved / 60
    # 사서 시급 추정 (시간당 ₩20,000·교통비/식대 제외 순순 인건비)
    krw_saved = int(hours_saved * 20_000)
    return {
        "records": f"{records_processed:,}권",
        "minutes_saved": f"{minutes_saved:,}분",
        "hours_saved": f"{hours_saved:.1f}시간",
        "krw_saved": f"₩{krw_saved:,}",
        "context": (
            f"권당 8분 → 2분 (헌법 §0 목표)·"
            f"사서 1명 1주 야근 1회 = 약 {hours_saved / 2:.0f}시간 절감"
        ),
    }


def render_librarian_friendly_error(error_kind: str) -> tuple[str, str]:
    """IT 에러 → 사서 친화 메시지 변환.

    Returns:
        (제목, 본문)·st.error()에 그대로 사용 가능
    """
    mapping = {
        "isbn_invalid": (
            "ISBN 형식 오류",
            "13자리 ISBN을 입력하세요 (예: 9788937437076). 10자리 ISBN은 자동 변환됩니다.",
        ),
        "api_timeout": (
            "외부 API 응답 지연",
            "국립중앙도서관·도서관정보나루 응답이 10초 안 도착. "
            "잠시 후 재시도하거나 다른 API를 사용하세요.",
        ),
        "no_external_match": (
            "외부 검색 미일치",
            "이 ISBN은 외부 DB에 등록되지 않았습니다. "
            "수동 입력 또는 알라딘 보조 검색 (출처 표시 의무)을 사용하세요.",
        ),
        "kdc_ambiguous": (
            "KDC 분류 자동 결정 불가",
            "사서 직접 입력 또는 AI 추천 3 후보 (BYOK Anthropic) 중 선택하세요. "
            "헌법 §3 = KDC = 사서 책임 영역·자동 결정 X.",
        ),
        "pii_warning": (
            "개인정보 감지",
            "MARC 입력에 개인정보로 보이는 내용 감지. "
            "PIPA §28의8 정합 = 본문 LLM 송신 차단 (헌법 §3). "
            "수동 검토 후 익명화 후 재시도.",
        ),
    }
    return mapping.get(
        error_kind,
        ("처리 오류", f"문제 발생 (kind={error_kind})·관리자에게 문의."),
    )


def render_workflow_position(current_step: str) -> str:
    """현재 사서 일과 위치 시각화 (마이크로 카피·5 단계).

    예: "수서 → **정리** → 배가 → 이용 → 납본"
    Cycle 60 = 사서 인지 부하 ↓·"내가 어디에 있는지" 즉시 인지.
    """
    steps = [s for s, _ in LIBRARIAN_DAILY_CYCLE]
    parts = []
    for s in steps:
        if s == current_step:
            parts.append(f"**{s}**")
        else:
            parts.append(s)
    return " → ".join(parts)


def is_mobile_viewport_hint(width_hint: int | None = None) -> bool:
    """모바일 viewport 추정 (KWCAG 2.5.5·44px 터치 타겟 활성).

    Streamlit = 직접 viewport 감지 불가·width_hint 또는 query param 의존.
    실제 사용 = `st.experimental_get_query_params()` 등.
    """
    if width_hint is None:
        return False
    return width_hint < 768


def cite_authority(authority: str) -> str:
    """권위 인용 (Part 49·신뢰 ↑·전환율 +25%).

    Args:
        authority: nlk | kait | mcst | kla | klma
    """
    mapping = {
        "nlk": "📖 국립중앙도서관 (NLK·books.nl.go.kr)",
        "kait": "🏛 한국정보통신산업진흥원 (KAIT·KOLAS III 운영사)",
        "mcst": "🏛 문화체육관광부 (도서관 통계)",
        "kla": "📚 한국도서관협회 (KLA·연 회의 5/31)",
        "klma": "📚 한국도서관경영자협의회 (KLMA)",
    }
    return mapping.get(authority, f"📌 {authority}")


__all__ = [
    "LIBRARIAN_DAILY_CYCLE",
    "LIBRARIAN_VOCABULARY",
    "cite_authority",
    "is_mobile_viewport_hint",
    "render_librarian_friendly_error",
    "render_workflow_position",
    "time_saved_estimate",
]
