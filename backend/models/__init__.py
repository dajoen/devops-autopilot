"""Backend models package (import-light).

This package exposes model symbols lazily to avoid importing heavy dependencies
like SQLAlchemy at package import time. Symbols are loaded on first attribute
access using PEP 562 (__getattr__).
"""

from __future__ import annotations

import importlib
from typing import Any, Dict

_EXPORTS: Dict[str, tuple[str, str]] = {
    # config
    "ConfigModel": ("backend.models.config", "ConfigModel"),
    "DatabaseConfig": ("backend.models.config", "DatabaseConfig"),
    "InfluxDBConfig": ("backend.models.config", "InfluxDBConfig"),
    # health
    "HealthResponse": ("backend.models.health", "HealthResponse"),
    "DatabaseStatus": ("backend.models.health", "DatabaseStatus"),
    # runs
    "Run": ("backend.models.runs", "Run"),
    "RunCreate": ("backend.models.runs", "RunCreate"),
    "RunUpdate": ("backend.models.runs", "RunUpdate"),
    # logs
    "Log": ("backend.models.logs", "Log"),
    "LogCreate": ("backend.models.logs", "LogCreate"),
    # base (SQLAlchemy)
    "BaseModel": ("backend.models.base", "BaseModel"),
}


def __getattr__(name: str) -> Any:  # pragma: no cover - trivial
    try:
        module_name, attr = _EXPORTS[name]
    except KeyError as e:
        raise AttributeError(name) from e
    mod = importlib.import_module(module_name)
    return getattr(mod, attr)


def __dir__() -> list[str]:  # pragma: no cover - trivial
    return sorted(list(globals().keys()) + list(_EXPORTS.keys()))