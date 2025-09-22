"""Settings facade around ConfigModel with strict helpers.

Provides:
- provider(): returns current LLM provider (str)
- bamboo_auth(): returns (base_url, username, token)
- influx_config(): returns (url, org, bucket, token)
- postgres_dsn(): returns DSN string for asyncpg
"""

from __future__ import annotations

from typing import Tuple
from pydantic import ValidationError

from .config import get_config
from ..models.config import ConfigModel


class Settings:
    """High-level validated settings accessors."""

    def __init__(self, config: ConfigModel | None = None):
        self._config = config or get_config()

    # ---- LLM ----
    def provider(self) -> str:
        """Return the configured LLM provider.

        Raises:
            ValueError: if LLM provider is not configured.
        """
        llm = self._config.external_apis.llm if self._config.external_apis else None
        if not llm or not llm.provider:
            raise ValueError(
                "LLM provider is not configured. Set external_apis.llm.provider in config or LLM_PROVIDER env var."
            )
        return llm.provider

    # ---- Bamboo ----
    def bamboo_auth(self) -> Tuple[str, str, str]:
        """Return Bamboo (base_url, username, token).

        Returns:
            tuple[str, str, str]: base_url, username, token

        Raises:
            ValueError: if Bamboo is not fully configured.
        """
        bamboo = self._config.external_apis.bamboo if self._config.external_apis else None
        if not bamboo:
            raise ValueError(
                "Bamboo configuration missing. Provide external_apis.bamboo.{base_url,username,token} or envs "
                "BAMBOO_BASE_URL, BAMBOO_USERNAME, BAMBOO_TOKEN."
            )
        base_url = str(bamboo.base_url)
        username = bamboo.username
        token = bamboo.token.get_secret_value()
        if not base_url or not username or not token:
            raise ValueError("Incomplete Bamboo config: base_url/username/token must all be set")
        return base_url, username, token

    # ---- InfluxDB ----
    def influx_config(self) -> Tuple[str, str, str, str]:
        """Return Influx settings (url, org, bucket, token)."""
        inf = self._config.influxdb
        try:
            url = str(inf.url)
            org = inf.org
            bucket = inf.bucket
            token = inf.token.get_secret_value()
        except ValidationError as e:
            raise ValueError(f"Invalid InfluxDB configuration: {e}") from e
        return url, org, bucket, token

    # ---- Postgres ----
    def postgres_dsn(self) -> str:
        """Return async SQLAlchemy DSN for Postgres/asyncpg."""
        db = self._config.database
        return db.url


__all__ = ["Settings"]
