"""자료유형 자동 분기 — LDR 06-07, 008 부호화.

KORMARC LDR (지도자) 06: 레코드 유형
  a 어문자료 (단행본·연속간행물)
  c 출판된 음악자료
  d 필사 음악자료
  e 지도자료 (출판)
  f 지도자료 (필사)
  g 시각자료 (영화·DVD·슬라이드)
  i 음향자료 (낭독·강연)
  j 음악자료 (음반)
  k 평면 비투영 시각자료
  m 컴퓨터 파일 (전자책 포함)
  o 키트
  p 복합자료
  r 입체자료·실물·교구
  t 필사 어문자료

LDR 07: 서지 수준
  a 모노그래프 부분
  b 연속간행물 부분
  c 모음·집서
  d 단행본 부분 (분책)
  i 통합자료
  m 모노그래프 (단행본)
  s 연속간행물 (잡지·신문)

008 06: 발행상태 (어문자료)
  s 단일발행 (단행본)
  m 다권물 발행
  c 현행 연속간행물
  d 종간 연속간행물
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class MaterialTypeCodes:
    """자료유형별 LDR·008 부호 묶음."""

    ldr_06: str  # 레코드 유형
    ldr_07: str  # 서지 수준
    field_008_06: str  # 발행상태
    description: str


MATERIAL_TYPES: dict[str, MaterialTypeCodes] = {
    "book_single": MaterialTypeCodes("a", "m", "s", "단행본 (단일 권)"),
    "book_multi": MaterialTypeCodes("a", "m", "m", "다권물 (시리즈·전집)"),
    "book_part": MaterialTypeCodes("a", "a", "s", "단행본 분책"),
    "serial_current": MaterialTypeCodes("a", "s", "c", "연속간행물 (현행)"),
    "serial_ceased": MaterialTypeCodes("a", "s", "d", "연속간행물 (종간)"),
    "ebook": MaterialTypeCodes("m", "m", "s", "전자책"),
    "audiobook": MaterialTypeCodes("i", "m", "s", "오디오북"),
    "dvd": MaterialTypeCodes("g", "m", "s", "DVD·영상자료"),
    "music_cd": MaterialTypeCodes("j", "m", "s", "음반 CD"),
    "map": MaterialTypeCodes("e", "m", "s", "지도자료"),
    "kit": MaterialTypeCodes("o", "m", "s", "키트 (교구·자료 묶음)"),
    "braille": MaterialTypeCodes("a", "m", "s", "점자도서"),  # 008 24 별도 부호화
    "thesis": MaterialTypeCodes("a", "m", "s", "학위논문"),  # 008 24=m + 502 필드
}


def detect_material_type(book_data: dict[str, Any]) -> str:
    """BookData에서 자료유형 자동 감지.

    휴리스틱 기반. 사서 검토 권장.
    """
    title = (book_data.get("title") or "").lower()
    category = (book_data.get("category") or "").lower()
    summary = (book_data.get("summary") or "").lower()
    add_code = book_data.get("additional_code") or ""

    # 명시적 키워드 우선
    if "전자책" in title or "ebook" in title or "e-book" in title:
        return "ebook"
    if "오디오북" in title or "audio" in category:
        return "audiobook"
    if "dvd" in category or "비디오" in category:
        return "dvd"
    if "cd" in category and ("음악" in category or "music" in category):
        return "music_cd"
    if "지도" in title or "지도자료" in category:
        return "map"
    if "점자" in title or "점자도서" in category:
        return "braille"
    if "학위논문" in title or "박사학위" in title or "석사학위" in title or "thesis" in summary:
        return "thesis"

    # ISBN 부가기호 힌트 (5자리)
    # 첫 자리가 9면 기타·전문, 4면 청소년, 7면 아동
    if add_code and len(add_code) >= 1 and add_code[0] == "9":
        # 9는 잡종 — 기본 단행본으로 처리 (placeholder)
        pass

    # 다권물 힌트
    if book_data.get("series_no") or book_data.get("series_title"):
        return "book_multi"

    # 연속간행물 힌트
    if any(kw in (title + category) for kw in ("월간", "주간", "계간", "연감", "magazine", "journal")):
        return "serial_current"

    return "book_single"


def get_codes(material_type: str) -> MaterialTypeCodes:
    """자료유형 키 → 부호 묶음 (없으면 단행본 기본)."""
    return MATERIAL_TYPES.get(material_type, MATERIAL_TYPES["book_single"])


def build_leader(material_type: str = "book_single") -> str:
    """LDR 24자 — 자료유형 반영.

    원래 builder.py는 'nam'(단행본) 고정. 자료유형별 분기.
    """
    codes = get_codes(material_type)
    # leader[5]='n' (신규), leader[6]=ldr_06, leader[7]=ldr_07
    # 기본 패턴: "00000{n}{a}{m} a2200000   4500"
    return f"00000n{codes.ldr_06}{codes.ldr_07} a2200000   4500"
