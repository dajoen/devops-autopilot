"""InfluxDB connection management."""

from typing import Optional
from datetime import datetime
import asyncio
from ..models.config import InfluxDBConfig


class InfluxDBManager:
    """Singleton InfluxDB manager for metrics and time series data."""
    
    _instance: Optional["InfluxDBManager"] = None
    _client = None
    _write_api = None
    _query_api = None
    _config: Optional[InfluxDBConfig] = None
    
    def __new__(cls) -> "InfluxDBManager":
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self, config: InfluxDBConfig) -> None:
        """Initialize InfluxDB connection."""
        self._config = config
        
        try:
            # Import influxdb_client here to avoid import errors if not installed
            from influxdb_client import InfluxDBClient
            from influxdb_client.client.write_api import SYNCHRONOUS
            
            self._client = InfluxDBClient(
                url=config.url,
                token=config.token,
                org=config.org
            )
            
            self._write_api = self._client.write_api(write_options=SYNCHRONOUS)
            self._query_api = self._client.query_api()
            
        except ImportError:
            # InfluxDB client not installed - create mock objects
            self._client = None
            self._write_api = None
            self._query_api = None
    
    @property
    def client(self):
        """Get InfluxDB client."""
        return self._client
    
    @property
    def write_api(self):
        """Get InfluxDB write API."""
        return self._write_api
    
    @property
    def query_api(self):
        """Get InfluxDB query API."""
        return self._query_api
    
    def write_point(self, measurement: str, fields: dict, tags: dict = None, timestamp: datetime = None) -> bool:
        """Write a single point to InfluxDB."""
        if not self._write_api or not self._config:
            return False
        
        try:
            from influxdb_client import Point
            
            point = Point(measurement)
            
            # Add tags
            if tags:
                for key, value in tags.items():
                    point = point.tag(key, value)
            
            # Add fields
            for key, value in fields.items():
                point = point.field(key, value)
            
            # Add timestamp
            if timestamp:
                point = point.time(timestamp)
            
            self._write_api.write(bucket=self._config.bucket, record=point)
            return True
            
        except Exception as e:
            print(f"Error writing to InfluxDB: {e}")
            return False
    
    def write_points(self, points: list) -> bool:
        """Write multiple points to InfluxDB."""
        if not self._write_api or not self._config:
            return False
        
        try:
            self._write_api.write(bucket=self._config.bucket, record=points)
            return True
        except Exception as e:
            print(f"Error writing points to InfluxDB: {e}")
            return False
    
    async def query(self, query: str) -> list:
        """Execute a query against InfluxDB."""
        if not self._query_api:
            return []
        
        try:
            # Run query in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self._query_api.query,
                query
            )
            return result
        except Exception as e:
            print(f"Error querying InfluxDB: {e}")
            return []
    
    async def check_connection(self) -> bool:
        """Check if InfluxDB connection is healthy."""
        if not self._client:
            return False
        
        try:
            # Run health check in thread pool
            loop = asyncio.get_event_loop()
            health = await loop.run_in_executor(None, self._client.health)
            return health.status == "pass"
        except Exception:
            return False
    
    def close(self) -> None:
        """Close InfluxDB connections."""
        if self._client:
            self._client.close()
            self._client = None
            self._write_api = None
            self._query_api = None


# Global InfluxDB manager instance
influxdb_manager = InfluxDBManager()