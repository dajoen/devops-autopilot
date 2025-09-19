"""Database connection management for PostgreSQL with async SQLAlchemy."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from ..models.config import DatabaseConfig
from ..models.base import SQLAlchemyBase


class DatabaseManager:
    """Singleton database manager for PostgreSQL connections."""
    
    _instance: Optional["DatabaseManager"] = None
    _engine: Optional[AsyncEngine] = None
    _session_factory: Optional[sessionmaker] = None
    
    def __new__(cls) -> "DatabaseManager":
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self, config: DatabaseConfig) -> None:
        """Initialize database connection."""
        if self._engine is None:
            self._engine = create_async_engine(
                config.url,
                echo=False,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600,
            )
            
            self._session_factory = sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
    
    @property
    def engine(self) -> AsyncEngine:
        """Get database engine."""
        if self._engine is None:
            raise RuntimeError("Database manager not initialized")
        return self._engine
    
    @asynccontextmanager
    async def get_session(self):
        """Get database session context manager."""
        if self._session_factory is None:
            raise RuntimeError("Database manager not initialized")
        
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    async def create_tables(self) -> None:
        """Create all database tables."""
        if self._engine is None:
            raise RuntimeError("Database manager not initialized")
        
        async with self._engine.begin() as conn:
            await conn.run_sync(SQLAlchemyBase.metadata.create_all)
    
    async def drop_tables(self) -> None:
        """Drop all database tables."""
        if self._engine is None:
            raise RuntimeError("Database manager not initialized")
        
        async with self._engine.begin() as conn:
            await conn.run_sync(SQLAlchemyBase.metadata.drop_all)
    
    async def check_connection(self) -> bool:
        """Check if database connection is healthy."""
        if self._engine is None:
            return False
        
        try:
            async with self._engine.begin() as conn:
                await conn.execute("SELECT 1")
                return True
        except Exception:
            return False
    
    async def close(self) -> None:
        """Close database connections."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None


# Global database manager instance
db_manager = DatabaseManager()