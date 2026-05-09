"""Streamlit Cloud root entry point (Cycle 672·Day 1 즉시 배포).

Streamlit Cloud (https://share.streamlit.io) 표준 = `streamlit_app.py` (root).
PO Day 1 외부 작업 (25분):
1. Streamlit Cloud → New app → repo 선택 → Main file = `streamlit_app.py` → Deploy
2. Settings → Secrets → `.streamlit/secrets.toml.example` 내용 + LemonSqueezy + MongoDB 입력
3. 배포 URL = `kormarc-auto.streamlit.app` (커스텀 가능)

기존 본체 = `src/kormarc_auto/ui/streamlit_app.py` (Cycle 63·정교한 4 탭 UI).
본 root = thin wrapper + Day 1 LemonSqueezy CTA bar + MongoDB health.

헌법 §3 정합 (env from secrets.toml·하드코딩 X)·§14 정합 (자관 데이터 수집 X).
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

# _shared 등록 (Cycle 168 분리·Plan C·local sub-package)
SHARED_PATH = REPO_ROOT.parent / "30-apps" / "_shared"
if SHARED_PATH.exists() and str(SHARED_PATH) not in sys.path:
    sys.path.insert(0, str(SHARED_PATH))


def _get_secret(key: str, default: str = "") -> str:
    """Streamlit Cloud secrets 또는 환경변수에서 읽기 (양쪽 호환)."""
    import os

    try:
        import streamlit as st  # type: ignore[import-not-found]

        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key])
    except Exception:  # noqa: BLE001 — Streamlit secrets 미설정 시 graceful fallback
        pass
    return os.environ.get(key, default)


def _render_health_sidebar() -> None:
    """사이드바 = MongoDB·LemonSqueezy 연결 상태 표시 (Day 1 검증용)."""
    import streamlit as st  # type: ignore[import-not-found]

    with st.sidebar:
        st.divider()
        st.caption("⚙️ Day 1 통합 상태")

        mongodb_uri = _get_secret("MONGODB_URI")
        if mongodb_uri:
            try:
                from mongodb_helper import is_mongo_available  # type: ignore[import-not-found]

                if is_mongo_available():
                    st.success("✅ MongoDB Atlas 연결")
                else:
                    st.warning("⚠️ MongoDB URI 등록·연결 미확인")
            except ImportError:
                st.info("ℹ️ MongoDB 선택 (pymongo 설치 시 활성)")
        else:
            st.info("ℹ️ MongoDB 미설정 (선택·session 모드)")

        ls_key = _get_secret("LEMONSQUEEZY_API_KEY")
        if ls_key:
            st.success("✅ LemonSqueezy 결제 활성")
        else:
            st.info("ℹ️ LemonSqueezy 미설정 (Day 1 PO 외부 작업)")


def _render_lemonsqueezy_cta() -> None:
    """LemonSqueezy 결제 CTA bar (Day 1 매출 시작점)."""
    import streamlit as st  # type: ignore[import-not-found]

    ls_key = _get_secret("LEMONSQUEEZY_API_KEY")
    store_id = _get_secret("LEMONSQUEEZY_STORE_ID")
    variant_id = _get_secret("LEMONSQUEEZY_VARIANT_ID")

    if not (ls_key and store_id and variant_id):
        return  # 미설정 = CTA 표시 X (헌법 §3·정직)

    checkout_url = (
        f"https://app.lemonsqueezy.com/buy/{variant_id}"
        if variant_id
        else "https://app.lemonsqueezy.com"
    )
    st.info(
        f"💳 **Pro 구독 결제** → [LemonSqueezy 결제 페이지]({checkout_url})·KRW·세금계산서 자동"
    )


def main() -> None:
    """Streamlit Cloud entry point."""
    # 본체 streamlit_app 호출 (Cycle 63 정교한 4 탭 UI 재사용)
    try:
        from kormarc_auto.ui import streamlit_app  # type: ignore[import-not-found]
    except ImportError as exc:
        import streamlit as st  # type: ignore[import-not-found]

        st.error(f"본체 UI 로드 실패: {exc}")
        st.info(
            "fallback: `pip install -e .` 또는 Streamlit Cloud requirements.txt 확인 의무"
        )
        return

    _render_health_sidebar()
    _render_lemonsqueezy_cta()

    # 본체 main 호출 (Cycle 63 4 탭 UI)
    if hasattr(streamlit_app, "main"):
        streamlit_app.main()
    else:
        import streamlit as st  # type: ignore[import-not-found]

        st.warning("본체 main() 함수 부재·src/kormarc_auto/ui/streamlit_app.py 직접 실행 권장")


if __name__ == "__main__":
    main()
