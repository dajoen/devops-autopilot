"""Health check models."""

from datetime import datetime
from typing import Optional
from enum import Enum
from .base import BaseModel


class HealthStatus(str, Enum):
    """Health status enumeration."""
    
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


class DatabaseStatus(BaseModel):
    """Database connection status model."""
    
    name: str
    status: HealthStatus
    response_time_ms: Optional[float] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: HealthStatus
    timestamp: datetime
    version: str
    uptime_seconds: float
    databases: list[DatabaseStatus]