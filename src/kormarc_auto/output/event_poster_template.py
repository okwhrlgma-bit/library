"""행사·포스터 자동 템플릿 — Part 80 페인 #19 정합.

사서 페인 (Part 80):
- 사서 = 일러스트·포토샵 독학 부담
- 행사 포스터 = 사서 멀티플레이어
- 도서관 주간·북스타트·저자 강연 매월

해결: HTML/CSS 템플릿 자동 (브라우저 print → PDF).
"""
from __future__ import annotations

from datetime import date
from typing import Literal

EventType = Literal[
    "library_week",      # 도서관 주간 (4월·9월)
    "library_day",       # 도서관의 날 (4/12)
    "bookstart",         # 북스타트 (영유아)
    "author_talk",       # 저자 강연
    "reading_club",      # 독서 동아리
    "exhibition",        # 전시
    "kid_event",         # 어린이 행사
    "general",
]


THEME_COLORS = {
    "library_week": "#2C5282",      # 네이비
    "library_day": "#ED8936",       # 살구
    "bookstart": "#FED7D7",         # 연분홍 (영유아)
    "author_talk": "#38A169",       # 초록
    "reading_club": "#805AD5",      # 보라
    "exhibition": "#D69E2E",        # 황금
    "kid_event": "#F6AD55",         # 주황
    "general": "#2C5282",
}


def render_event_poster(
    *,
    title: str,
    event_type: EventType,
    library_name: str,
    event_date: date,
    location: str,
    description: str,
    contact: str = "",
    image_url: str = "",
) -> str:
    """행사 포스터 HTML 자동 생성 (A4·인쇄 가능).

    Args:
        title: 행사 제목
        event_type: 행사 유형
        library_name: 자관명
        event_date: 행사 일자
        location: 장소
        description: 설명
        contact: 연락처
        image_url: 이미지 (선택)

    Returns:
        HTML (브라우저 print → PDF·SNS 공유 가능)
    """
    color = THEME_COLORS.get(event_type, "#2C5282")
    weekdays_kr = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
    date_str = (
        f"{event_date.year}년 {event_date.month}월 {event_date.day}일 "
        f"({weekdays_kr[event_date.weekday()]})"
    )

    image_html = (
        f'<img src="{image_url}" style="width: 100%; max-height: 200mm; object-fit: cover;" />'
        if image_url
        else ""
    )

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>{title} — {library_name}</title>
<style>
@page {{ size: A4; margin: 0; }}
body {{
  margin: 0; padding: 0;
  font-family: 'Pretendard', 'Noto Sans KR', sans-serif;
  background: #FAFAF7;
  color: #1A202C;
}}
.poster {{
  width: 210mm; height: 297mm;
  margin: 0 auto;
  padding: 20mm;
  box-sizing: border-box;
  background: white;
  display: flex;
  flex-direction: column;
}}
.header {{
  text-align: center;
  border-bottom: 4px solid {color};
  padding-bottom: 15mm;
  margin-bottom: 20mm;
}}
.library {{
  font-size: 12pt; color: #6b7280;
  margin-bottom: 5mm;
}}
.title {{
  font-size: 36pt;
  font-weight: 800;
  color: {color};
  letter-spacing: -0.02em;
  line-height: 1.2;
}}
.image {{
  margin: 15mm 0;
  text-align: center;
}}
.info {{
  background: #F7FAFC;
  border-left: 6px solid {color};
  padding: 10mm;
  border-radius: 4px;
  margin-bottom: 15mm;
}}
.info-row {{
  display: flex;
  margin-bottom: 5mm;
  font-size: 14pt;
}}
.info-label {{
  font-weight: 600;
  color: {color};
  width: 25mm;
}}
.description {{
  font-size: 13pt;
  line-height: 1.7;
  color: #2D3748;
  flex-grow: 1;
}}
.footer {{
  text-align: center;
  font-size: 11pt;
  color: #6b7280;
  border-top: 2px solid #E2E8F0;
  padding-top: 8mm;
}}
@media print {{ body {{ background: white; }} .poster {{ margin: 0; }} }}
</style>
</head>
<body>
  <div class="poster">
    <div class="header">
      <div class="library">{library_name}</div>
      <div class="title">{title}</div>
    </div>
    {image_html}
    <div class="info">
      <div class="info-row">
        <span class="info-label">📅 일시</span>
        <span>{date_str}</span>
      </div>
      <div class="info-row">
        <span class="info-label">📍 장소</span>
        <span>{location}</span>
      </div>
    </div>
    <div class="description">{description}</div>
    <div class="footer">
      {contact if contact else f"문의: {library_name}"} · kormarc-auto 자동 생성
    </div>
  </div>
</body>
</html>"""


__all__ = ["THEME_COLORS", "EventType", "render_event_poster"]
