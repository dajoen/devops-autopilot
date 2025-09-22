import json
from typing import Any, Dict

import pytest

from backend.services.llm.provider import LocalAIProvider


class _FakeResponse:
    def __init__(self, status_code: int, body: Dict[str, Any] | None = None, text: str = ""):
        self.status_code = status_code
        self._body = body or {}
        self.text = text or json.dumps(self._body)

    def json(self) -> Dict[str, Any]:
        return self._body


def test_localai_success_returns_text():
    sent: Dict[str, Any] = {}

    def requester(url: str, **kwargs: Any):
        sent.update({"url": url, "kwargs": kwargs})
        return _FakeResponse(200, {"choices": [{"text": "hello world"}]})

    p = LocalAIProvider(base_url="http://localhost:8080", model="foo", requester=requester)
    out = p.complete("hi there", max_tokens=10)
    assert out == "hello world"
    assert sent["url"].endswith("/v1/completions")
    payload = sent["kwargs"]["json"]
    assert payload["prompt"] == "hi there"
    assert payload["model"] == "foo"
    assert payload["max_tokens"] == 10


def test_localai_http_error_raises():
    def requester(url: str, **kwargs: Any):
        return _FakeResponse(500, text="internal error")

    p = LocalAIProvider(base_url="http://localhost:8080", model="foo", requester=requester)
    with pytest.raises(RuntimeError) as e:
        p.complete("boom")
    assert "/v1/completions" in str(e.value)


def test_localai_bad_format_raises():
    def requester(url: str, **kwargs: Any):
        return _FakeResponse(200, {"unexpected": True})

    p = LocalAIProvider(base_url="http://localhost:8080", model="foo", requester=requester)
    with pytest.raises(ValueError):
        p.complete("test")
