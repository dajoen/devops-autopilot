"""Log models for tracking system events."""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from .base import BaseModel, TimestampMixin


class LogLevel(str, Enum):
    """Log level enumeration."""
    
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogBase(BaseModel):
    """Base log model."""
    
    level: LogLevel
    message: str
    source: str
    run_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class LogCreate(LogBase):
    """Log creation model."""
    pass


class Log(LogBase, TimestampMixin):
    """Complete log model."""
    
    id: int