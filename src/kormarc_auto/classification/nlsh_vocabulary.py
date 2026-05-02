"""NLSH 주제명 표준 어휘 — NL Korea 「주제명표목 업무지침」(2021) 기반.

NLSH = 국립중앙도서관 주제명표목표.
650 ▾a 주제어 + ▾2 8 (NLSH 출처)

본 모듈은 NLSH의 주요 어휘 클러스터·계층 구조 일부 내장.
완전 NLSH 어휘는 NL 보유 (52p 지침). 본 PoC는 핵심 카테고리.

향후 PO 자료 폴더의 「주제명표목 업무지침(2021).pdf」 정독 후
표준 어휘 매핑 자동 갱신 가능.
"""

from __future__ import annotations

# NLSH 핵심 주제 카테고리 (지침 기반 추정)
NLSH_CATEGORIES = {
    "문학": {
        "주제어": ["한국문학", "한국소설", "한국시", "한국수필", "한국희곡", "한국아동문학"],
        "kdc_prefix": "81",
    },
    "역사": {
        "주제어": [
            "한국사",
            "한국현대사",
            "조선사",
            "고려사",
            "삼국사",
            "한국독립운동",
            "한국전쟁",
        ],
        "kdc_prefix": "911",
    },
    "사회과학": {
        "주제어": ["사회학", "정치학", "경제학", "교육학", "법학", "행정학", "사회복지"],
        "kdc_prefix": "3",
    },
    "철학": {
        "주제어": ["철학", "동양철학", "서양철학", "윤리학", "심리학", "미학", "논리학"],
        "kdc_prefix": "1",
    },
    "종교": {
        "주제어": ["불교", "기독교", "유교", "천주교", "이슬람교", "도교", "한국 종교"],
        "kdc_prefix": "2",
    },
    "자연과학": {
        "주제어": ["수학", "물리학", "화학", "생물학", "천문학", "지구과학"],
        "kdc_prefix": "4",
    },
    "기술": {
        "주제어": [
            "의학",
            "농학",
            "공학",
            "건축",
            "기계공학",
            "전기공학",
            "화학공학",
            "컴퓨터과학",
        ],
        "kdc_prefix": "5",
    },
    "예술": {
        "주제어": ["미술", "음악", "공연예술", "사진", "영화", "디자인", "스포츠"],
        "kdc_prefix": "6",
    },
    "어학": {
        "주제어": ["한국어", "영어", "중국어", "일본어", "독일어", "프랑스어"],
        "kdc_prefix": "7",
    },
}


def map_kdc_to_nlsh_topics(kdc: str) -> list[str]:
    """KDC → NLSH 주제어 후보.

    예: '813.7' → ['한국문학', '한국소설']
    """
    if not kdc:
        return []
    out: list[str] = []
    for category, info in NLSH_CATEGORIES.items():
        prefix = info["kdc_prefix"]
        if kdc.startswith(prefix):
            out.append(category)
            out.extend(info["주제어"][:3])  # 상위 3개만
    return out


def normalize_subject_term(term: str) -> str:
    """주제어 정규화 — 띄어쓰기·기호 표준화.

    NLSH는 '한국 소설' 보다 '한국소설' 같은 결합형 선호.
    """
    if not term:
        return ""
    cleaned = term.strip()
    # 자주 보이는 결합 패턴
    replacements = [
        ("한국 문학", "한국문학"),
        ("한국 소설", "한국소설"),
        ("한국 사", "한국사"),
        ("현대 사", "현대사"),
    ]
    for src, dst in replacements:
        cleaned = cleaned.replace(src, dst)
    return cleaned


def is_nlsh_compatible(term: str) -> bool:
    """주제어가 NLSH 표준 어휘에 가까운지 휴리스틱 검증.

    완전 검증은 NL의 NLSH DB 조회 필요. 본 PoC는 결합형·과도한 띄어쓰기만 체크.
    """
    if not term:
        return False
    if len(term) > 30:
        return False  # 너무 긴 어구
    return term.count(" ") <= 2  # 띄어쓰기 2 이하
