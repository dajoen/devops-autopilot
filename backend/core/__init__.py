"""Core package initialization with optional heavy imports."""

from .config import ConfigManager, get_config
from .settings import Settings

try:  # Optional: may require SQLAlchemy
    from .database import DatabaseManager
except Exception:  # pragma: no cover
    DatabaseManager = None  # type: ignore

try:  # Optional: may require influxdb-client
    from .influxdb import InfluxDBManager
except Exception:  # pragma: no cover
    InfluxDBManager = None  # type: ignore

__all__ = [
    "ConfigManager",
    "get_config",
    "DatabaseManager",
    "InfluxDBManager",
    "Settings",
]