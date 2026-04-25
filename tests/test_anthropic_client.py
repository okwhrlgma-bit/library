"""_anthropic_client 단위 테스트."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from kormarc_auto import _anthropic_client as ac  # noqa: E402


def test_make_image_cache_key_deterministic():
    k1 = ac.make_image_cache_key([b"abc"], "v1", "model")
    k2 = ac.make_image_cache_key([b"abc"], "v1", "model")
    k3 = ac.make_image_cache_key([b"abd"], "v1", "model")
    assert k1 == k2
    assert k1 != k3


def test_make_text_cache_key_deterministic():
    k1 = ac.make_text_cache_key(prompt_kind="kdc", model="m", prompt_version="v1", payload="x")
    k2 = ac.make_text_cache_key(prompt_kind="kdc", model="m", prompt_version="v1", payload="x")
    assert k1 == k2


def test_ensure_cache_control_on_string():
    out = ac._ensure_cache_control_on_system("hello")
    assert isinstance(out, list)
    assert out[0]["text"] == "hello"
    assert out[0]["cache_control"] == {"type": "ephemeral"}


def test_ensure_cache_control_on_blocks():
    out = ac._ensure_cache_control_on_system(
        [{"type": "text", "text": "a"}, {"type": "text", "text": "b", "cache_control": {"type": "ephemeral"}}]
    )
    assert len(out) == 2
    assert all("cache_control" in b for b in out)


def test_extract_tool_input_finds_block():
    fake_block = MagicMock()
    fake_block.type = "tool_use"
    fake_block.name = "report_isbn"
    fake_block.input = {"isbn13": "9788936434120"}
    response = MagicMock()
    response.content = [fake_block]
    out = ac._extract_tool_input(response, "report_isbn")
    assert out == {"isbn13": "9788936434120"}


def test_extract_tool_input_returns_none_when_missing():
    response = MagicMock()
    response.content = []
    assert ac._extract_tool_input(response, "report_isbn") is None


@patch("kormarc_auto._anthropic_client.get_anthropic_client")
@patch("kormarc_auto._anthropic_client.get_anthropic_cache")
def test_cached_messages_returns_cached_hit(mock_cache_get, mock_client_get):
    fake_cache = MagicMock()
    fake_cache.get.return_value = {"tool_input": {"x": 1}, "text": None, "cached": False}
    mock_cache_get.return_value = fake_cache

    out = ac.cached_messages(
        cache_key="test",
        model="m",
        system="sys",
        messages=[],
        max_tokens=100,
    )
    assert out["cached"] is True
    assert out["tool_input"] == {"x": 1}
    mock_client_get.assert_not_called()


@patch("kormarc_auto._anthropic_client.get_anthropic_client")
@patch("kormarc_auto._anthropic_client.get_anthropic_cache")
def test_cached_messages_calls_client_on_miss(mock_cache_get, mock_client_get):
    fake_cache = MagicMock()
    fake_cache.get.return_value = None
    mock_cache_get.return_value = fake_cache

    fake_block = MagicMock()
    fake_block.type = "tool_use"
    fake_block.name = "report_isbn"
    fake_block.input = {"isbn13": "9788936434120"}
    fake_response = MagicMock()
    fake_response.content = [fake_block]

    fake_client = MagicMock()
    fake_client.messages.create.return_value = fake_response
    mock_client_get.return_value = fake_client

    out = ac.cached_messages(
        cache_key="test2",
        model="m",
        system="sys",
        messages=[{"role": "user", "content": "x"}],
        tools=[{"name": "report_isbn"}],
        tool_name="report_isbn",
    )
    assert out["cached"] is False
    assert out["tool_input"] == {"isbn13": "9788936434120"}
    fake_cache.set.assert_called_once()
