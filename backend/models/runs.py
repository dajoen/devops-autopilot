"""Run models for tracking DevOps operations."""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from .base import BaseModel, TimestampMixin


class RunStatus(str, Enum):
    """Run status enumeration."""
    
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RunType(str, Enum):
    """Run type enumeration."""
    
    DEPLOYMENT = "deployment"
    PIPELINE = "pipeline"
    BACKUP = "backup"
    MAINTENANCE = "maintenance"
    TEST = "test"
    OTHER = "other"


class RunBase(BaseModel):
    """Base run model."""
    
    name: str
    type: RunType
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    tags: Optional[Dict[str, str]] = None


class RunCreate(RunBase):
    """Run creation model."""
    pass


class RunUpdate(BaseModel):
    """Run update model."""
    
    status: Optional[RunStatus] = None
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    tags: Optional[Dict[str, str]] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class Run(RunBase, TimestampMixin):
    """Complete run model."""
    
    id: int
    status: RunStatus = RunStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None