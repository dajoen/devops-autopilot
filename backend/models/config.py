"""Configuration models."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class DatabaseConfig(BaseModel):
    """Database configuration model."""
    
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, description="Database port")
    database: str = Field(description="Database name")
    username: str = Field(description="Database username")
    password: str = Field(description="Database password")
    
    @property
    def url(self) -> str:
        """Get database URL."""
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class InfluxDBConfig(BaseModel):
    """InfluxDB configuration model."""
    
    url: str = Field(default="http://localhost:8086", description="InfluxDB URL")
    token: str = Field(description="InfluxDB token")
    org: str = Field(description="InfluxDB organization")
    bucket: str = Field(description="InfluxDB bucket")


class CORSConfig(BaseModel):
    """CORS configuration model."""
    
    origins: list[str] = Field(default=["http://localhost:3000"], description="Allowed origins")
    methods: list[str] = Field(default=["*"], description="Allowed methods")
    headers: list[str] = Field(default=["*"], description="Allowed headers")


class AppConfig(BaseModel):
    """Application configuration model."""
    
    name: str = Field(default="DevOps Autopilot", description="Application name")
    version: str = Field(default="1.0.0", description="Application version")
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")


class ConfigModel(BaseModel):
    """Main configuration model."""
    
    app: AppConfig = Field(default_factory=AppConfig)
    database: DatabaseConfig = Field(description="Database configuration")
    influxdb: InfluxDBConfig = Field(description="InfluxDB configuration")
    cors: CORSConfig = Field(default_factory=CORSConfig)
    
    class Config:
        env_nested_delimiter = "__"