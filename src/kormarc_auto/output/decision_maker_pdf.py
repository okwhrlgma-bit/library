"""결제자 1페이지 PDF 자동 생성 — 페르소나 01·02 100점 보완.

페르소나 01 김지원 (사서교사) deal-breaker:
- 결제권자 = 행정실장 (사서 X) → 1페이지 결재 양식 필요
- "사서가 행정실장에게 보여줄 자료 = 30초 안에 이해 가능"

페르소나 02 박서연 (작은도서관 관장) Phase 2:
- 본인 결제이지만 자치구 보고용 1페이지 필요

PDF 구성 (A4 1페이지):
1. 헤더: 도서관명·작성일·작성 사서명
2. ROI 요약 표: 권당 시간·연 절감·도입 비용 vs 절감액
3. 핵심 기능 5개 불릿
4. 도입 후 변화 (Before/After 표)
5. 비용 매트릭스 (월정액·권당·무료 tier)
6. 리스크·법무 (PIPA·알라딘 약관)
7. 다음 단계 (PILOT 30일 무료·계약 절차)

한국 결재 문화 정합:
- 표 위주 (텍스트 최소)
- 결재선 (검토·기안·확인·결재) 영역 빈칸
- 자치구 양식과 호환 (A4 세로·여백 25mm)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DecisionMakerProfile:
    """결제자 1페이지 PDF 입력."""

    library_name: str  # 자관명 (예: "○○중학교 도서관")
    librarian_name: str  # 작성 사서 (행정실 제출자)
    decision_maker_role: str  # "행정실장" / "관장" / "본관 관장" / "교육청 담당"
    annual_book_count: int  # 연간 신규 도서 권수 (입력)
    plan_won_per_month: int = 100_000  # 권장 plan 월정액
    metered_won_per_book: int = 200  # 권당 종량
    pilot_days: int = 30  # 무료 PILOT 기간


@dataclass(frozen=True)
class RoiSummary:
    """ROI 계산 결과."""

    annual_minutes_saved: int  # 연간 절감 분
    annual_hours_saved: float
    librarian_hourly_won: int = 18_000  # 사서 평균 시급 (공무원 7급 기준)
    annual_cost_won: int = 0
    annual_savings_won: int = 0
    payback_months: float = 0.0
    roi_multiple: float = 0.0


def calculate_roi(profile: DecisionMakerProfile) -> RoiSummary:
    """연간 ROI 계산.

    가정:
    - 권당 시간 단축: 8분 → 1.5분 (Part 87 측정)
    - 절감 = (8 - 1.5) × 권수 = 6.5분/권
    - 연간 절감 분 = 6.5 × annual_book_count
    """
    minutes_per_book_saved = 6.5  # 8 → 1.5
    annual_minutes = int(minutes_per_book_saved * profile.annual_book_count)
    annual_hours = round(annual_minutes / 60, 1)

    annual_cost = profile.plan_won_per_month * 12
    annual_savings = int(annual_hours * 18_000)  # 사서 시급
    payback = round(annual_cost / annual_savings * 12, 1) if annual_savings > 0 else 999.0
    roi_multiple = round(annual_savings / annual_cost, 1) if annual_cost > 0 else 0.0

    return RoiSummary(
        annual_minutes_saved=annual_minutes,
        annual_hours_saved=annual_hours,
        annual_cost_won=annual_cost,
        annual_savings_won=annual_savings,
        payback_months=payback,
        roi_multiple=roi_multiple,
    )


def render_decision_pdf_html(
    profile: DecisionMakerProfile,
    roi: RoiSummary | None = None,
) -> str:
    """결제자 1페이지 HTML 생성 (브라우저 PDF 변환·또는 weasyprint).

    HTML 출력 = PDF 변환 도구 다양 (weasyprint·pdfkit·browser print).
    한국 결재 양식 호환 = A4 세로·여백 25mm.
    """
    if roi is None:
        roi = calculate_roi(profile)

    today = date.today().strftime("%Y-%m-%d")

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>kormarc-auto 도입 결재 자료 — {profile.library_name}</title>
<style>
  @page {{ size: A4; margin: 25mm; }}
  body {{ font-family: 'Pretendard', sans-serif; font-size: 11pt; line-height: 1.4; }}
  .header {{ border-bottom: 2px solid #333; padding-bottom: 8pt; margin-bottom: 12pt; }}
  .header h1 {{ font-size: 16pt; margin: 0; }}
  .header .meta {{ font-size: 9pt; color: #666; margin-top: 4pt; }}
  .section {{ margin: 10pt 0; }}
  .section h2 {{ font-size: 12pt; background: #eee; padding: 4pt 8pt; margin-bottom: 6pt; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 10pt; }}
  th, td {{ border: 1px solid #999; padding: 4pt 6pt; text-align: left; }}
  th {{ background: #f5f5f5; font-weight: bold; }}
  .roi-highlight {{ font-size: 14pt; font-weight: bold; color: #c00; }}
  .approval {{ position: fixed; bottom: 25mm; left: 25mm; right: 25mm;
              border-top: 1px solid #333; padding-top: 8pt; font-size: 9pt; }}
  .approval table {{ width: 100%; }}
  .approval td {{ height: 40pt; text-align: center; }}
</style>
</head>
<body>
  <div class="header">
    <h1>kormarc-auto SaaS 도입 결재 자료</h1>
    <div class="meta">
      자관: {profile.library_name} | 결제 검토: {profile.decision_maker_role} |
      작성: {profile.librarian_name} | 작성일: {today}
    </div>
  </div>

  <div class="section">
    <h2>1. ROI 요약 (한 줄)</h2>
    <p class="roi-highlight">
      연간 {roi.annual_hours_saved}시간 절감 = {roi.annual_savings_won:,}원 절감 |
      도입 비용 회수 {roi.payback_months}개월 | ROI {roi.roi_multiple}배
    </p>
  </div>

  <div class="section">
    <h2>2. 비용 vs 절감 매트릭스</h2>
    <table>
      <tr><th>항목</th><th>금액 (연간)</th></tr>
      <tr><td>도입 비용 (월 {profile.plan_won_per_month:,}원 × 12개월)</td>
          <td>{roi.annual_cost_won:,}원</td></tr>
      <tr><td>사서 시간 절감 (시급 18,000원 × {roi.annual_hours_saved}시간)</td>
          <td>{roi.annual_savings_won:,}원</td></tr>
      <tr><td><b>순 절감</b></td><td><b>{roi.annual_savings_won - roi.annual_cost_won:,}원</b></td></tr>
    </table>
  </div>

  <div class="section">
    <h2>3. 핵심 기능 5개</h2>
    <ul>
      <li><b>ISBN 1번 입력 → KORMARC .mrc 5초 출력</b> (KOLAS·DLS·알파스 즉시 반입)</li>
      <li><b>9 자료유형 → KORMARC 표준 8 카테고리</b> (단행본·연속·전자·지도·녹음·시청각·고서·복합)</li>
      <li><b>KDC 자동 분류</b> (NL Korea → 부가기호 → AI 추천 3개·사서 검토)</li>
      <li><b>880 한자 병기 자동</b> (NLK 「서지데이터 로마자 표기 지침(2021)」 정합)</li>
      <li><b>자관 049 prefix·별치 자동</b> (자관 정책 학습·5분 도입)</li>
    </ul>
  </div>

  <div class="section">
    <h2>4. Before / After</h2>
    <table>
      <tr><th></th><th>Before (기존)</th><th>After (도입 후)</th></tr>
      <tr><td>권당 마크 시간</td><td>8분</td><td>1.5분 (75%↓)</td></tr>
      <tr><td>외주 의존</td><td>예 (권당 3,000~5,000원)</td><td>아니오 (권당 200원)</td></tr>
      <tr><td>KOLAS 반입</td><td>수동 복사·붙여넣기</td><td>자동 (.mrc 폴더)</td></tr>
      <tr><td>사서 검수</td><td>전부 수기</td><td>AI 1차 + 사서 최종 (보존)</td></tr>
    </table>
  </div>

  <div class="section">
    <h2>5. 리스크·법무</h2>
    <ul>
      <li>PIPA 2026.09.11 시행 정합 (개인정보처리방침·DPA·SLA·환불 약관 완비)</li>
      <li>알라딘 약관 = 도서관 자체 키 위임 (kormarc-auto 자체 키 X)</li>
      <li>1주 100% 환불·계약 종료 후 30일 데이터 export</li>
      <li>KORMARC KS X 6006-0:2023.12 100% 정합</li>
    </ul>
  </div>

  <div class="section">
    <h2>6. 다음 단계</h2>
    <ol>
      <li><b>{profile.pilot_days}일 무료 PILOT</b> (50건 무료·해지 자유)</li>
      <li>PILOT 만족 시 → 월 {profile.plan_won_per_month:,}원 정식 계약</li>
      <li>또는 권당 {profile.metered_won_per_book}원 종량제 (외주 대비 1/15~1/25)</li>
      <li>문의: PO 직접 연락 가능 (사서 출신 1인 개발자)</li>
    </ol>
  </div>

  <div class="approval">
    <table>
      <tr>
        <td>기안<br>{profile.librarian_name}</td>
        <td>검토</td>
        <td>확인</td>
        <td>{profile.decision_maker_role}</td>
      </tr>
    </table>
  </div>
</body>
</html>
"""


__all__ = [
    "DecisionMakerProfile",
    "RoiSummary",
    "calculate_roi",
    "render_decision_pdf_html",
]
