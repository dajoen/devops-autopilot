"""Base model for common functionality."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel as PydanticBaseModel, Field
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

# SQLAlchemy Base
SQLAlchemyBase = declarative_base()


class BaseModel(PydanticBaseModel):
    """Base Pydantic model with common configuration."""
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BaseTable(SQLAlchemyBase):
    """Base SQLAlchemy model with common fields."""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class TimestampMixin(BaseModel):
    """Mixin for models with timestamp fields."""
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None