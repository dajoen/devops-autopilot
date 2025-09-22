"""Health check service."""

import time
from datetime import datetime
from typing import List
from ..models.health import HealthResponse, DatabaseStatus, HealthStatus
from ..core.database import db_manager
from ..core.influxdb import influxdb_manager


class HealthService:
    """Service for health checks and system status."""
    
    def __init__(self):
        """Initialize health service."""
        self.start_time = time.time()
    
    async def get_health_status(self, app_version: str) -> HealthResponse:
        """Get comprehensive health status."""
        # Check database connections
        databases = await self._check_databases()
        
        # Determine overall status
        overall_status = self._determine_overall_status(databases)
        
        # Calculate uptime
        uptime_seconds = time.time() - self.start_time
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.utcnow(),
            version=app_version,
            uptime_seconds=uptime_seconds,
            databases=databases
        )
    
    async def _check_databases(self) -> List[DatabaseStatus]:
        """Check all database connections."""
        databases = []
        
        # Check PostgreSQL
        postgres_status = await self._check_postgres()
        databases.append(postgres_status)
        
        # Check InfluxDB
        influx_status = await self._check_influxdb()
        databases.append(influx_status)
        
        return databases
    
    async def _check_postgres(self) -> DatabaseStatus:
        """Check PostgreSQL connection."""
        start_time = time.time()
        
        try:
            is_healthy = await db_manager.check_connection()
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return DatabaseStatus(
                name="PostgreSQL",
                status=HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
                error=None if is_healthy else "Connection failed"
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return DatabaseStatus(
                name="PostgreSQL",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
                error=str(e)
            )
    
    async def _check_influxdb(self) -> DatabaseStatus:
        """Check InfluxDB connection."""
        start_time = time.time()
        
        try:
            is_healthy = await influxdb_manager.check_connection()
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return DatabaseStatus(
                name="InfluxDB",
                status=HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
                error=None if is_healthy else "Connection failed"
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return DatabaseStatus(
                name="InfluxDB",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
                error=str(e)
            )
    
    def _determine_overall_status(self, databases: List[DatabaseStatus]) -> HealthStatus:
        """Determine overall system health status."""
        if not databases:
            return HealthStatus.UNHEALTHY
        
        healthy_count = sum(1 for db in databases if db.status == HealthStatus.HEALTHY)
        total_count = len(databases)
        
        if healthy_count == total_count:
            return HealthStatus.HEALTHY
        elif healthy_count > 0:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.UNHEALTHY