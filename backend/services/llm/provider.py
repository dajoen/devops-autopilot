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
]
