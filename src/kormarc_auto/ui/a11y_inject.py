"""Cycle 60 (UI/UX·헌법 §12 정합) — Streamlit a11y/Pretendard 글로벌 inject.

KWCAG 2.2 Level AA + KRDS + Pretendard CDN을 모든 페이지 진입점에 적용.
헌법 §12: "모든 UI = KWCAG 2.2 Level AA·KRDS 색상 토큰·Pretendard CDN".

사용:
    import streamlit as st
    from kormarc_auto.ui.a11y_inject import inject_global_a11y

    st.set_page_config(...)  # 먼저
    inject_global_a11y()      # 다음 = lang ko·Pretendard·skip-link 글로벌 적용
"""

from __future__ import annotations

from kormarc_auto.a11y.krds import (
    KRDS_COLOR_TOKENS,
    PRETENDARD_CDN_URL,
)

# Pretendard CDN + 글로벌 a11y CSS 통합 (KWCAG 2.2 정합)
A11Y_GLOBAL_CSS = f"""
<link rel="stylesheet" href="{PRETENDARD_CDN_URL}" />
<style>
  /* KWCAG 1.3.1 lang ko 명시 (HTML 자체는 streamlit 제어) */
  html, body {{ lang: ko; }}

  /* Pretendard 우선·Apple SD Gothic Neo·맑은 고딕 fallback (헌법 §12) */
  html, body, [class*="css"] {{
    font-family: 'Pretendard', -apple-system, 'Apple SD Gothic Neo',
                 'Malgun Gothic', 'Noto Sans KR', sans-serif !important;
  }}

  /* KWCAG 1.4.4 = 200% 확대 시에도 가독 = base 16px */
  html {{ font-size: 16px; }}

  /* KWCAG 1.4.3 = 4.5:1 대비 = gray_90 본문·korea_blue_60 링크 */
  body {{ color: {KRDS_COLOR_TOKENS["gray_90"]}; }}
  a {{ color: {KRDS_COLOR_TOKENS["korea_blue_60"]}; }}

  /* KWCAG 2.4.7 focus visible = 항상 보이는 포커스 표시 */
  *:focus-visible {{
    outline: 3px solid {KRDS_COLOR_TOKENS["korea_blue_60"]} !important;
    outline-offset: 2px !important;
  }}

  /* KWCAG 2.5.5 = 터치 타겟 최소 44x44px (모바일·태블릿) */
  button, [role="button"], input[type="checkbox"], input[type="radio"] {{
    min-height: 44px;
  }}

  /* KWCAG 1.4.13 = 호버/포커스 콘텐츠 닫기 가능 (Streamlit popover 정합) */

  /* KWCAG 2.3.3 = prefers-reduced-motion 정합 = 애니메이션 즉시 차단 */
  @media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
    }}
  }}

  /* KWCAG 2.4.1 = skip link (사서 키보드 사용자) */
  .skip-link {{
    position: absolute;
    left: -999px;
    top: 8px;
    background: {KRDS_COLOR_TOKENS["korea_blue_60"]};
    color: white;
    padding: 8px 16px;
    border-radius: 4px;
    z-index: 9999;
    text-decoration: none;
  }}
  .skip-link:focus {{
    left: 8px;
  }}

  /* 사서 친화 = 시각 위계 강화 (h1·h2·h3) */
  h1 {{ font-size: 1.875rem; font-weight: 700;
        color: {KRDS_COLOR_TOKENS["korea_blue_60"]}; }}
  h2 {{ font-size: 1.5rem; font-weight: 600;
        margin-top: 2rem; }}
  h3 {{ font-size: 1.25rem; font-weight: 600;
        margin-top: 1.5rem; }}

  /* 신뢰도 chip (Cycle 13A·카테고리형 신뢰 정합) */
  .conf-chip {{
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.875rem;
    font-weight: 600;
  }}
  .conf-chip-high {{
    background: {KRDS_COLOR_TOKENS["green_50"]};
    color: white;
  }}
  .conf-chip-mid {{
    background: {KRDS_COLOR_TOKENS["amber_50"]};
    color: white;
  }}
  .conf-chip-low {{
    background: {KRDS_COLOR_TOKENS["red_50"]};
    color: white;
  }}

  /* AI 생성 ghost text (Cycle 10A·헌법 §10·인공지능 기본법 §31) */
  .ai-ghost {{
    color: {KRDS_COLOR_TOKENS["gray_50"]};
    font-style: italic;
    border-left: 3px solid {KRDS_COLOR_TOKENS["amber_50"]};
    padding-left: 8px;
  }}
</style>
<a href="#main-content" class="skip-link">본문 바로가기</a>
"""


def inject_global_a11y() -> None:
    """모든 Streamlit 페이지 진입점에서 1회 호출.

    KWCAG 2.2 Level AA 정합:
    - 1.3.1 lang ko·1.4.3 4.5:1 대비·1.4.4 200% 확대·1.4.13 호버 콘텐츠
    - 2.3.3 reduced-motion·2.4.1 skip link·2.4.7 focus visible·2.5.5 터치 타겟 44px

    Pretendard CDN inject + KRDS 색상 토큰 적용.
    """
    try:
        import streamlit as st

        st.markdown(A11Y_GLOBAL_CSS, unsafe_allow_html=True)
    except ImportError:
        # Streamlit 미설치 환경 (테스트·CLI) = silent
        pass


def render_confidence_chip(category: str, label: str | None = None) -> str:
    """신뢰도 chip HTML (Cycle 13A·카테고리형 신뢰 정합).

    category = 'high' (확실) | 'mid' (검토 필요) | 'low' (불확실).
    raw % UI 금지 (헌법 §11·ADR 0030).
    """
    label_map = {
        "high": label or "확실",
        "mid": label or "검토 필요",
        "low": label or "불확실",
    }
    if category not in label_map:
        category = "mid"
    return f'<span class="conf-chip conf-chip-{category}">{label_map[category]}</span>'


def render_ai_ghost(text: str) -> str:
    """AI 생성 ghost text HTML (Cycle 10A·헌법 §10).

    인공지능 기본법 §31 = AI 생성 사실 표시 의무.
    UI ghost text + KORMARC 588 + audit log 4곳 동시 명시.
    """
    return f'<div class="ai-ghost">🤖 {text}</div>'


__all__ = [
    "A11Y_GLOBAL_CSS",
    "inject_global_a11y",
    "render_ai_ghost",
    "render_confidence_chip",
]
