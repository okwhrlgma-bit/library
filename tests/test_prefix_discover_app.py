"""prefix_discover_app standalone Streamlit 모듈 import 테스트."""

from __future__ import annotations


def test_app_module_imports():
    """모듈 import 정상 (streamlit + PrefixDiscoverer 의존성 충족)."""
    from kormarc_auto.ui import prefix_discover_app

    assert callable(prefix_discover_app.main)
    assert callable(prefix_discover_app._setup)
