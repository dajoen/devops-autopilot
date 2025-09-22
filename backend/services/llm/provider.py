"""LLM provider abstractions and registry."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Type, Callable

from ...core.settings import Settings


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    name: str = "abstract"

    @abstractmethod
    def complete(self, prompt: str, **params: Any) -> str:  # sync for now
        """Return a completion for the given prompt.

        Implementations should return a plain text string response.
        """

    @classmethod
    def from_settings(cls, settings: Settings) -> "LLMProvider":
        """Factory: build a concrete provider instance from Settings.

        Uses the global provider registry based on Settings().provider().
        """
        provider_name = settings.provider()
        try:
            factory = _PROVIDER_REGISTRY[provider_name]
        except KeyError as e:
            raise ValueError(
                f"Unknown LLM provider '{provider_name}'. Register a provider or set LLM_PROVIDER accordingly."
            ) from e
        return factory(settings)


# --- Registry ---
_PROVIDER_REGISTRY: Dict[str, Callable[[Settings], LLMProvider]] = {}


def register_provider(name: str):
    """Decorator to register a provider factory by name."""

    def _wrap(factory: Callable[[Settings], LLMProvider]):
        _PROVIDER_REGISTRY[name] = factory
        return factory

    return _wrap


# --- Dummy implementation for local/dev ---
class DummyProvider(LLMProvider):
    name = "dummy"

    def __init__(self, model: str | None = None):
        self.model = model or "dummy"

    def complete(self, prompt: str, **params: Any) -> str:
        suffix = params.get("suffix", "")
        return f"[dummy:{self.model}] {prompt}{(' ' + suffix) if suffix else ''}"


@register_provider("dummy")
def _build_dummy(settings: Settings) -> LLMProvider:
    llm = settings._config.external_apis.llm if settings._config.external_apis else None  # type: ignore[attr-defined]
    model = llm.model if llm and llm.model else None
    return DummyProvider(model=model)


__all__ = [
    "LLMProvider",
    "DummyProvider",
    "register_provider",
    "LocalAIProvider",
]


# --- LocalAI implementation ---
class LocalAIProvider(LLMProvider):
    name = "localai"

    def __init__(self, base_url: str, model: str, temperature: float | None = None, max_tokens: int | None = None,
                 requester: Callable[..., Any] | None = None):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        # Dependency injection for unit tests
        self._requester = requester or _httpx_post

    def complete(self, prompt: str, **params: Any) -> str:
        payload = {
            "model": params.get("model", self.model),
            "prompt": prompt,
            "temperature": params.get("temperature", self.temperature),
            "max_tokens": params.get("max_tokens", self.max_tokens),
            "stream": False,
        }
        # Clean None values
        payload = {k: v for k, v in payload.items() if v is not None}

        url = f"{self.base_url}/v1/completions"
        resp = self._requester(url, json=payload, timeout=30)
        if resp.status_code >= 400:
            body = _safe_snippet(resp)
            raise RuntimeError(f"LocalAI error {resp.status_code} at /v1/completions: {body}")
        data = resp.json()
        # Expected format: { choices: [ { text: "..." } ] }
        try:
            return data["choices"][0]["text"]
        except Exception as e:
            raise ValueError(f"Unexpected LocalAI response format: {data}") from e


def _httpx_post(url: str, **kwargs: Any) -> Any:
    # Lazy import to avoid requiring httpx outside runtime
    import httpx  # type: ignore
    return httpx.post(url, **kwargs)


def _safe_snippet(resp: Any, limit: int = 300) -> str:
    try:
        txt = resp.text
    except Exception:
        return "<no body>"
    return (txt[:limit] + ("…" if len(txt) > limit else ""))


@register_provider("localai")
def _build_localai(settings: Settings) -> LLMProvider:
    cfg = settings._config  # type: ignore[attr-defined]
    llm = cfg.external_apis.llm if cfg.external_apis else None
    if not llm or not llm.base_url:
        raise ValueError("LocalAI requires external_apis.llm.base_url or LLM_BASE_URL env var")
    model = llm.model or "gpt-3.5-turbo"
    # Temperature and max_tokens are optional; not present in config yet.
    temperature = None
    max_tokens = None
    return LocalAIProvider(
        base_url=str(llm.base_url),
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )

