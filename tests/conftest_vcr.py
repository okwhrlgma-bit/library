"""pytest-recording (vcrpy) conftest — 옵션 3 (Part 92 §A.1).

PO 명령: "data4library·KAKAO·PUBMED 실 녹화·conftest vcr_config·--block-network"

활성화: tests/conftest.py에서 `from .conftest_vcr import vcr_config` import.
또는 `pytest --vcr-record=once` 직접 사용.

키 마스킹 (PIPA·git push 안전):
- x-api-key·Authorization·authKey·api_key·cert_key·ttbkey 모두 REDACTED
- 본문 응답에 키 잔존 시도 = vcr 자동 detect 실패 → 수동 검토
"""

from __future__ import annotations

import pytest


@pytest.fixture(scope="module")
def vcr_config():
    """VCR.py 설정 (모든 외부 API 호출 녹화·재생)."""
    return {
        "filter_headers": [
            ("x-api-key", "REDACTED"),
            ("authorization", "REDACTED"),
            ("api-key", "REDACTED"),
        ],
        "filter_query_parameters": [
            ("authKey", "REDACTED"),
            ("api_key", "REDACTED"),
            ("cert_key", "REDACTED"),
            ("ttbkey", "REDACTED"),
            ("TTBKey", "REDACTED"),
            ("key", "REDACTED"),  # NL Korea 통합 search.do
        ],
        "filter_post_data_parameters": [
            ("api_key", "REDACTED"),
            ("authKey", "REDACTED"),
        ],
        "decode_compressed_response": True,
        "record_mode": "once",  # 처음 1회만 실 호출·이후 재생
        "match_on": ["method", "scheme", "host", "port", "path"],  # query/body 변경 OK
        "cassette_library_dir": "tests/cassettes",
    }


def pytest_collection_modifyitems(config, items):
    """--block-network 옵션 시 vcr 마크 X 테스트 skip."""
    if config.getoption("--block-network", default=False):
        for item in items:
            if "vcr" not in item.keywords and any(
                marker in item.name for marker in ("real_api", "live_call", "external")
            ):
                item.add_marker(pytest.mark.skip(reason="--block-network 활성·vcr cassette 필요"))


def pytest_addoption(parser):
    """--block-network 플래그 추가."""
    parser.addoption(
        "--block-network",
        action="store_true",
        default=False,
        help="외부 네트워크 호출 차단·VCR cassette만 사용 (CI 게이트)",
    )
