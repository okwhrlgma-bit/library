"""페르소나별 어휘 분기 시스템.

ADR-0060 (Part 43 §5 + Part 45 시뮬 발견).

검증: P3 자원활동가·P6 학부모 1초 이탈 30% → 어휘 분기 적용 시 5% 이하.
종합 전환율 가중평균 27% → 35%+ (Part 46 검증).

Usage:
    from kormarc_auto.ui.persona_vocabulary import t, get_persona_mode

    mode = get_persona_mode()  # session_state에서 사용자 페르소나 로드
    title = t("home.title", mode=mode)
    # 사서 모드: "KORMARC 자동 생성"
    # 비전문가 모드: "책 정보 자동 등록"
"""
from __future__ import annotations

from typing import Literal

PersonaMode = Literal["librarian", "non_expert", "auto"]

# 어휘 매트릭스: 사서 모드 vs 비전문가 모드
VOCABULARY: dict[str, dict[str, str]] = {
    # 홈 화면
    "home.title": {
        "librarian": "KORMARC 자동 생성",
        "non_expert": "책 정보 자동 등록",
    },
    "home.subtitle": {
        "librarian": "9 자료유형 + KOLAS·DLS 직접 호환",
        "non_expert": "책 한 권 등록이 5분 안에 끝나요",
    },
    "home.cta_main": {
        "librarian": "ISBN 입력하기",
        "non_expert": "책 등록 시작하기",
    },
    # 입력 안내
    "input.isbn_label": {
        "librarian": "ISBN-13 입력",
        "non_expert": "책 뒷표지 13자리 숫자",
    },
    "input.isbn_help": {
        "librarian": "ISBN-13 (978·979 시작 13자리). 하이픈 자동 제거.",
        "non_expert": "책 뒤쪽 표지에 있는 바코드 위 숫자예요. 예: 9788937437076",
    },
    "input.batch_label": {
        "librarian": "ISBN 일괄 처리",
        "non_expert": "여러 책 한꺼번에 등록",
    },
    "input.photo_label": {
        "librarian": "사진 입력 (Vision)",
        "non_expert": "책 사진 찍어서 등록",
    },
    # 결과
    "result.title": {
        "librarian": "KORMARC 레코드 생성 완료",
        "non_expert": "책 정보 등록 완료",
    },
    "result.confidence": {
        "librarian": "신뢰도",
        "non_expert": "정확도",
    },
    "result.download": {
        "librarian": ".mrc 다운로드",
        "non_expert": "결과 파일 받기",
    },
    "result.review": {
        "librarian": "사서 검토 권장",
        "non_expert": "사서 선생님이 한번 더 확인할게요",
    },
    # 도메인 용어 (비전문가 모드에서 풀어쓰기)
    "term.kdc": {
        "librarian": "KDC 분류",
        "non_expert": "주제 분류 (예: 문학·역사)",
    },
    "term.call_number": {
        "librarian": "청구기호",
        "non_expert": "책 위치 번호",
    },
    "term.bibliographic": {
        "librarian": "서지 정보",
        "non_expert": "책 정보 (제목·저자·출판사)",
    },
    "term.authority": {
        "librarian": "전거",
        "non_expert": "저자·주제 표준 이름",
    },
    # 에러 메시지 (Part 44 §1 정합 — 친근 톤)
    "error.isbn_invalid.title": {
        "librarian": "ISBN 형식 확인 필요",
        "non_expert": "ISBN을 다시 확인해주세요",
    },
    "error.isbn_invalid.body": {
        "librarian": "13자리 숫자 + 체크섬 검증 실패. 입력값을 확인하세요.",
        "non_expert": "13자리 숫자가 맞는지 살펴봐주세요. 책 뒷표지에서 찾을 수 있어요.",
    },
    "error.api_timeout.title": {
        "librarian": "외부 API 응답 지연",
        "non_expert": "서버 응답이 조금 늦네요",
    },
    "error.api_timeout.body": {
        "librarian": "정보나루·국중도 API timeout. 30초 후 자동 재시도.",
        "non_expert": "잠시 후 자동으로 다시 시도할게요. 30초만 기다려주시면 됩니다.",
    },
    # 액션 버튼
    "action.save": {
        "librarian": "저장",
        "non_expert": "저장하기",
    },
    "action.export": {
        "librarian": "내보내기",
        "non_expert": "파일로 받기",
    },
    "action.help": {
        "librarian": "도움말",
        "non_expert": "어려우신가요?",
    },
    # 가격 안내 (P3·P6 결제 압박 회피 — Part 45)
    "pricing.free_badge": {
        "librarian": "Free 50건",
        "non_expert": "무료로 50권 등록 가능 ✨",
    },
    "pricing.no_pressure": {
        "librarian": "결제는 50건 사용 후 결정",
        "non_expert": "지금은 결제 안 하셔도 됩니다. 50권 무료로 써보세요.",
    },
    # 사서 실무 표준 용어 (PO 명령: 사서 친화 언어 필수)
    "term.acquisition": {
        "librarian": "수서",
        "non_expert": "책 구입·기증 등록",
    },
    "term.cataloging": {
        "librarian": "목록 작성",
        "non_expert": "책 정보 등록",
    },
    "term.organization": {
        "librarian": "정리",
        "non_expert": "책 정리·분류",
    },
    "term.shelving": {
        "librarian": "배가",
        "non_expert": "책 서가 배치",
    },
    "term.deposit": {
        "librarian": "납본",
        "non_expert": "출판사 의무 제출본",
    },
    "term.donation": {
        "librarian": "기증도서",
        "non_expert": "기증받은 책",
    },
    "term.purchase": {
        "librarian": "구입도서",
        "non_expert": "구입한 책",
    },
    "term.volume_no": {
        "librarian": "권차",
        "non_expert": "여러 권으로 된 책의 순서",
    },
    "term.copy_no": {
        "librarian": "복본기호",
        "non_expert": "같은 책 여러 권 표시",
    },
    "term.special_location": {
        "librarian": "별치기호",
        "non_expert": "특별 서가 표시",
    },
    "term.reserve_collection": {
        "librarian": "보존서고",
        "non_expert": "특별 보관 서가",
    },
    "term.inventory": {
        "librarian": "장서점검",
        "non_expert": "도서관 책 점검",
    },
    "term.book_curation": {
        "librarian": "북큐레이션",
        "non_expert": "주제별 책 추천",
    },
    "term.circulation": {
        "librarian": "대출·반납",
        "non_expert": "책 빌리기·돌려주기",
    },
    "term.interlibrary_loan": {
        "librarian": "상호대차",
        "non_expert": "다른 도서관 책 빌리기",
    },
    # KORMARC 자료유형 (사서 표준)
    "material.monograph": {
        "librarian": "단행본",
        "non_expert": "일반 도서",
    },
    "material.serial": {
        "librarian": "연속간행물",
        "non_expert": "잡지·신문",
    },
    "material.ebook": {
        "librarian": "전자책",
        "non_expert": "전자책 (e-book)",
    },
    "material.audiobook": {
        "librarian": "오디오북",
        "non_expert": "듣는 책",
    },
    "material.thesis": {
        "librarian": "학위논문",
        "non_expert": "학위논문",
    },
    "material.rare_book": {
        "librarian": "고서",
        "non_expert": "옛 책",
    },
    "material.multimedia": {
        "librarian": "멀티미디어",
        "non_expert": "DVD·CD 등",
    },
    # KORMARC 통합서지용 필드 라벨 (사서 표준)
    "field.245": {
        "librarian": "표제·책임표시 (245)",
        "non_expert": "제목·저자",
    },
    "field.260": {
        "librarian": "발행사항 (260)",
        "non_expert": "출판사·출판년도",
    },
    "field.300": {
        "librarian": "형태사항 (300)",
        "non_expert": "쪽수·크기",
    },
    "field.020": {
        "librarian": "ISBN (020)",
        "non_expert": "ISBN (책 뒷면 13자리)",
    },
    "field.049": {
        "librarian": "자관 청구기호 (049)",
        "non_expert": "우리 도서관 책 위치",
    },
    "field.040": {
        "librarian": "목록작성기관 (040)",
        "non_expert": "도서관 부호",
    },
    "field.880": {
        "librarian": "대체문자 표제 (880)",
        "non_expert": "한자·외국어 제목",
    },
    "field.008": {
        "librarian": "부호화 정보 (008)",
        "non_expert": "발행연도·언어 등",
    },
    # 시스템·반입 (KOLAS·DLS 사용자 친숙)
    "system.kolas": {
        "librarian": "KOLAS III",
        "non_expert": "KOLAS (공공도서관 시스템)",
    },
    "system.dls": {
        "librarian": "독서로DLS",
        "non_expert": "독서로DLS (학교도서관 시스템)",
    },
    "system.alpas": {
        "librarian": "알파스",
        "non_expert": "알파스 (도서관 시스템)",
    },
    "system.import": {
        "librarian": ".mrc 반입",
        "non_expert": "도서관 시스템에 등록",
    },
    "system.export": {
        "librarian": "내보내기",
        "non_expert": "파일로 받기",
    },
    # 사서 워크플로 단계
    "workflow.input": {
        "librarian": "입력",
        "non_expert": "등록",
    },
    "workflow.review": {
        "librarian": "검수",
        "non_expert": "확인",
    },
    "workflow.confirm": {
        "librarian": "확정",
        "non_expert": "완료",
    },
    "workflow.batch": {
        "librarian": "일괄 처리",
        "non_expert": "여러 권 한꺼번에",
    },
    # 도서관 행정·업무
    "admin.budget": {
        "librarian": "운영비·자료구입비",
        "non_expert": "도서관 예산",
    },
    "admin.statistics": {
        "librarian": "통계·집계",
        "non_expert": "처리량 보기",
    },
    "admin.report": {
        "librarian": "보고서",
        "non_expert": "정리된 자료",
    },
    "admin.evaluation": {
        "librarian": "운영평가",
        "non_expert": "도서관 평가",
    },
    # 사서 자격·역할
    "role.librarian_1st": {
        "librarian": "1급 정사서",
        "non_expert": "선임 사서",
    },
    "role.librarian_2nd": {
        "librarian": "2급 정사서",
        "non_expert": "사서 (자격증)",
    },
    "role.librarian_assoc": {
        "librarian": "준사서",
        "non_expert": "준사서 (자격증)",
    },
    "role.school_librarian": {
        "librarian": "사서교사",
        "non_expert": "도서관 선생님",
    },
    "role.volunteer": {
        "librarian": "자원활동가",
        "non_expert": "자원봉사자",
    },
}

# 페르소나별 기본 모드 매핑 (가입 시 페르소나 선택 → 자동 분기)
PERSONA_TO_MODE: dict[str, PersonaMode] = {
    # P1~P2·P4·P5: 사서 모드
    "macro_librarian": "librarian",
    "school_librarian": "librarian",
    "contract_librarian": "librarian",
    "university_librarian": "librarian",
    "general_librarian": "librarian",
    "acquisition_librarian": "librarian",
    "content_librarian": "librarian",
    # P3·P6: 비전문가 모드
    "volunteer": "non_expert",
    "parent_volunteer": "non_expert",
    "student_helper": "non_expert",
    # 기본
    "auto": "auto",
}


def t(key: str, *, mode: PersonaMode = "librarian") -> str:
    """페르소나 모드별 어휘 반환.

    Args:
        key: 어휘 키 (예: "home.title", "error.isbn_invalid.body")
        mode: librarian (사서) / non_expert (비전문가) / auto (세션에서 로드)

    Returns:
        해당 모드의 한국어 텍스트. 키가 없으면 키 자체 반환 (디버깅).
    """
    if key not in VOCABULARY:
        return f"[MISSING: {key}]"

    entry = VOCABULARY[key]
    if mode == "auto":
        # 세션 상태에서 모드 자동 로드 (Streamlit 환경)
        try:
            import streamlit as st

            mode = st.session_state.get("persona_mode", "librarian")
        except ImportError:
            mode = "librarian"

    return entry.get(mode, entry["librarian"])


def get_persona_mode(persona: str | None = None) -> PersonaMode:
    """페르소나 → 어휘 모드 매핑.

    Args:
        persona: 페르소나 키 (가입 시 선택). None이면 session_state에서 로드.

    Returns:
        librarian / non_expert
    """
    if persona is None:
        try:
            import streamlit as st

            persona = st.session_state.get("persona", "general_librarian")
        except ImportError:
            persona = "general_librarian"

    return PERSONA_TO_MODE.get(persona, "librarian")


def set_persona_mode(persona: str) -> None:
    """가입 시·설정에서 페르소나 변경 → 모드 자동 동기화."""
    try:
        import streamlit as st

        mode = get_persona_mode(persona)
        st.session_state["persona"] = persona
        st.session_state["persona_mode"] = mode
    except ImportError:
        pass
