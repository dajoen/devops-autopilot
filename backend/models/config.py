"""Configuration models with strict validation for app settings.

Includes database, InfluxDB, CORS, and external APIs (LLM, Bamboo).
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field, AnyHttpUrl, SecretStr, ConfigDict
from pydantic import field_validator


class DatabaseConfig(BaseModel):
    """Database configuration model (PostgreSQL)."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, ge=1, le=65535, description="Database port")
    database: str = Field(description="Database name")
    username: str = Field(description="Database username")
    password: SecretStr = Field(description="Database password")

    @field_validator("database", "username", mode="before")
    @classmethod
    def _non_empty(cls, v: str) -> str:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            raise ValueError("must not be empty")
        return v

    @property
    def url(self) -> str:
        """Return async SQLAlchemy DSN for asyncpg driver."""
        pw = self.password.get_secret_value()
        return f"postgresql+asyncpg://{self.username}:{pw}@{self.host}:{self.port}/{self.database}"


class InfluxDBConfig(BaseModel):
    """InfluxDB configuration model."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    url: AnyHttpUrl = Field(description="InfluxDB URL")
    token: SecretStr = Field(description="InfluxDB token")
    org: str = Field(description="InfluxDB organization")
    bucket: str = Field(description="InfluxDB bucket")

    @field_validator("org", "bucket", mode="before")
    @classmethod
    def _non_empty(cls, v: str) -> str:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            raise ValueError("must not be empty")
        return v


class CORSConfig(BaseModel):
    """CORS configuration model."""

    model_config = ConfigDict(extra="forbid")

    origins: list[str] = Field(default=["http://localhost:3000"], description="Allowed origins")
    methods: list[str] = Field(default=["*"], description="Allowed methods")
    headers: list[str] = Field(default=["*"], description="Allowed headers")


class AppConfig(BaseModel):
    """Application configuration model."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(default="DevOps Autopilot", description="Application name")
    version: str = Field(default="1.0.0", description="Application version")
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, ge=1, le=65535, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")


class LLMConfig(BaseModel):
    """Large Language Model provider configuration."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    provider: str = Field(description="LLM provider identifier (e.g., openai, azure, anthropic, ollama)")
    api_key: Optional[SecretStr] = Field(default=None, description="API key for the LLM provider")
    model: Optional[str] = Field(default=None, description="Default model identifier")
    base_url: Optional[AnyHttpUrl] = Field(default=None, description="Custom endpoint base URL (for self-hosted)")

    @field_validator("provider", mode="before")
    @classmethod
    def _non_empty_provider(cls, v: str) -> str:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            raise ValueError("LLM provider must be set (env LLM_PROVIDER or config external_apis.llm.provider)")
        return v


class BambooConfig(BaseModel):
    """Bamboo CI configuration."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    base_url: AnyHttpUrl = Field(description="Bamboo base URL")
    username: str = Field(description="Bamboo username")
    token: SecretStr = Field(description="Bamboo API token")

    @field_validator("username", mode="before")
    @classmethod
    def _non_empty_user(cls, v: str) -> str:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            raise ValueError("Bamboo username must not be empty (env BAMBOO_USERNAME)")
        return v


class ExternalAPIs(BaseModel):
    """External API configurations."""

    model_config = ConfigDict(extra="forbid")

    bamboo: Optional[BambooConfig] = Field(default=None, description="Bamboo CI settings")
    llm: Optional[LLMConfig] = Field(default=None, description="LLM provider settings")


class ConfigModel(BaseModel):
    """Main configuration model."""

    model_config = ConfigDict(extra="forbid")

    app: AppConfig = Field(default_factory=AppConfig)
    database: DatabaseConfig = Field(description="Database configuration")
    influxdb: InfluxDBConfig = Field(description="InfluxDB configuration")
    cors: CORSConfig = Field(default_factory=CORSConfig)
    external_apis: Optional[ExternalAPIs] = Field(default=None, description="External APIs configuration")