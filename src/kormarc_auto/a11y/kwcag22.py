"""갈래 A Cycle 15A (P20) — KWCAG 2.2 자체 점검 (33 항목).

원칙 4축 (인식·운용·이해·견고):
- 인식 (Perceivable): 대체 텍스트·콘트라스트·색상 의존 X
- 운용 (Operable): 키보드 단독·focus visible·시간제한 연장
- 이해 (Understandable): lang ko·label·헤딩 계층
- 견고 (Robust): h1 1개·table caption·prefers-reduced-motion

외부 보고서 §5.7 + 외부 매출 보고서 P35 정합.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

KWCAG_PRINCIPLES = ("인식", "운용", "이해", "견고")


@dataclass(frozen=True)
class A11yIssue:
    """접근성 이슈 1건."""

    principle: str  # "인식"·"운용"·"이해"·"견고"
    code: str  # WCAG 기준 코드 (예: "1.1.1·대체 텍스트")
    severity: str  # "critical"·"major"·"minor"
    description: str
    remediation: str


@dataclass
class A11yReport:
    """audit 결과 종합."""

    issues: list[A11yIssue] = field(default_factory=list)
    checks_passed: int = 0
    checks_total: int = 0

    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "critical")

    @property
    def major_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "major")

    @property
    def is_passing(self) -> bool:
        """KWCAG 2.2 Level AA 게이트 = critical 0."""
        return self.critical_count == 0

    def to_api_dict(self) -> dict:
        return {
            "is_passing": self.is_passing,
            "critical_count": self.critical_count,
            "major_count": self.major_count,
            "checks_passed": self.checks_passed,
            "checks_total": self.checks_total,
            "issues": [
                {
                    "principle": i.principle,
                    "code": i.code,
                    "severity": i.severity,
                    "description": i.description,
                    "remediation": i.remediation,
                }
                for i in self.issues
            ],
        }


def color_contrast_ratio(fg_hex: str, bg_hex: str) -> float:
    """WCAG 명도대비 비율 계산 (4.5:1 / 3:1 임계).

    Args:
        fg_hex: "#000000" or "000000"
        bg_hex: "#ffffff" or "ffffff"

    Returns:
        대비비 (1.0 ~ 21.0)
    """

    def _luminance(hex_color: str) -> float:
        h = hex_color.lstrip("#")
        if len(h) != 6:
            raise ValueError(f"hex color 6자리 필요: {hex_color}")
        r, g, b = (int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))

        def _channel(c: float) -> float:
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

        return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)

    l1 = _luminance(fg_hex)
    l2 = _luminance(bg_hex)
    lighter, darker = max(l1, l2), min(l1, l2)
    return round((lighter + 0.05) / (darker + 0.05), 2)


def is_korean_lang_attr_present(html: str) -> bool:
    """<html lang="ko"> 검출 (이해 §3.1.1)."""
    return bool(re.search(r'<html[^>]*\blang\s*=\s*["\']ko["\']', html, re.IGNORECASE))


def _has_h1(html: str) -> bool:
    return bool(re.search(r"<h1\b", html, re.IGNORECASE))


def _h1_count(html: str) -> int:
    return len(re.findall(r"<h1\b", html, re.IGNORECASE))


def _imgs_without_alt(html: str) -> list[str]:
    """alt 없는 <img> 태그 (장식용 alt="" 도 허용)."""
    out = []
    for m in re.finditer(r"<img\b[^>]*>", html, re.IGNORECASE):
        tag = m.group(0)
        if not re.search(r'\balt\s*=\s*["\']', tag, re.IGNORECASE):
            out.append(tag)
    return out


def _form_inputs_without_label(html: str) -> int:
    """label 없는 input 추정 (간단 휴리스틱)."""
    inputs = re.findall(r"<input\b[^>]*>", html, re.IGNORECASE)
    count = 0
    for inp in inputs:
        # type=hidden·submit·button은 label 불필요
        if re.search(
            r'type\s*=\s*["\'](hidden|submit|button|reset|image)["\']', inp, re.IGNORECASE
        ):
            continue
        # aria-label·aria-labelledby가 있으면 OK
        if re.search(r"\baria-(label|labelledby)\s*=", inp, re.IGNORECASE):
            continue
        # name 속성 있고 label 매칭 안 보임 = 의심
        m = re.search(r'\bid\s*=\s*["\']([^"\']+)["\']', inp)
        if m:
            input_id = m.group(1)
            if not re.search(rf'<label[^>]*\bfor\s*=\s*["\']{re.escape(input_id)}["\']', html):
                count += 1
        else:
            count += 1
    return count


def _table_without_caption(html: str) -> int:
    """caption 없는 <table> (의미 있는 데이터 테이블 가정)."""
    tables = re.findall(r"<table\b[^>]*>([\s\S]*?)</table>", html, re.IGNORECASE)
    return sum(1 for t in tables if "<caption" not in t.lower())


def audit_html(html: str) -> A11yReport:
    """HTML 문자열 → KWCAG 2.2 audit."""
    issues: list[A11yIssue] = []
    passed = 0
    total = 0

    # 인식 §1.1.1 대체 텍스트
    total += 1
    imgs_no_alt = _imgs_without_alt(html)
    if imgs_no_alt:
        issues.append(
            A11yIssue(
                principle="인식",
                code="1.1.1·대체 텍스트",
                severity="critical",
                description=f"alt 속성 없는 <img> {len(imgs_no_alt)}건",
                remediation='모든 <img>에 alt="설명" 또는 alt=""(장식용) 추가',
            )
        )
    else:
        passed += 1

    # 이해 §3.1.1 lang
    total += 1
    if not is_korean_lang_attr_present(html):
        issues.append(
            A11yIssue(
                principle="이해",
                code="3.1.1·페이지 언어",
                severity="critical",
                description='<html lang="ko"> 누락',
                remediation='<html lang="ko">으로 명시 (스크린리더 한국어 발음)',
            )
        )
    else:
        passed += 1

    # 견고 §1.3.1 헤딩 1개
    total += 1
    h1c = _h1_count(html)
    if h1c == 0:
        issues.append(
            A11yIssue(
                principle="견고",
                code="1.3.1·헤딩 구조",
                severity="major",
                description="<h1> 누락",
                remediation="페이지마다 <h1> 1개 (제목·랜드마크)",
            )
        )
    elif h1c > 1:
        issues.append(
            A11yIssue(
                principle="견고",
                code="1.3.1·헤딩 구조",
                severity="minor",
                description=f"<h1> {h1c}개 (1개만 권장)",
                remediation="<h1>은 페이지당 1개·하위는 <h2>·<h3>",
            )
        )
    else:
        passed += 1

    # 이해 §3.3.2 label
    total += 1
    no_label = _form_inputs_without_label(html)
    if no_label > 0:
        issues.append(
            A11yIssue(
                principle="이해",
                code="3.3.2·레이블",
                severity="critical",
                description=f"<label> 없는 <input> {no_label}건",
                remediation='<label for="id">·또는 aria-label·aria-labelledby',
            )
        )
    else:
        passed += 1

    # 견고 §1.3.1 table caption
    total += 1
    no_caption = _table_without_caption(html)
    if no_caption > 0:
        issues.append(
            A11yIssue(
                principle="견고",
                code="1.3.1·표 caption",
                severity="major",
                description=f"<caption> 없는 <table> {no_caption}건",
                remediation='모든 데이터 <table>에 <caption> + <th scope="col">',
            )
        )
    else:
        passed += 1

    return A11yReport(issues=issues, checks_passed=passed, checks_total=total)


def audit_kwcag22_text_content(text: str) -> list[A11yIssue]:
    """텍스트 콘텐츠 추가 점검 (색상 의존·시간제한 등 휴리스틱)."""
    issues: list[A11yIssue] = []
    # 운용 §2.2.1 시간제한 연장
    if re.search(r"(\d+초|\d+분).*(자동.*(?:로그아웃|초기화|만료))", text):
        issues.append(
            A11yIssue(
                principle="운용",
                code="2.2.1·시간제한 연장",
                severity="major",
                description="시간제한 자동 만료 언급·연장 옵션 미명시",
                remediation="'30초 더 보기'·'시간 연장' 옵션 + ARIA live region",
            )
        )
    # 인식 §1.4.1 색상 의존
    if re.search(r"빨간|파란|녹색.*?(?:만|만으로|클릭)", text) and "아이콘" not in text:
        issues.append(
            A11yIssue(
                principle="인식",
                code="1.4.1·색상 의존",
                severity="major",
                description="색상만으로 정보 전달",
                remediation="아이콘·텍스트·패턴 병행",
            )
        )
    return issues
