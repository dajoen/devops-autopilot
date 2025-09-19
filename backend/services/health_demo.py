"""Simplified health check service without database connections."""

import time
from datetime import datetime
from typing import List
from ..models.health import HealthResponse, DatabaseStatus, HealthStatus


class HealthServiceDemo:
    """Demo service for health checks without actual database connections."""
    
    def __init__(self):
        """Initialize health service."""
        self.start_time = time.time()
    
    async def get_health_status(self, app_version: str) -> HealthResponse:
        """Get comprehensive health status (demo mode)."""
        # Mock database status
        databases = [
            DatabaseStatus(
                name="PostgreSQL",
                status=HealthStatus.HEALTHY,
                response_time_ms=15.5,
                error=None
            ),
            DatabaseStatus(
                name="InfluxDB",
                status=HealthStatus.HEALTHY,
                response_time_ms=12.3,
                error=None
            )
        ]
        
        # Calculate uptime
        uptime_seconds = time.time() - self.start_time
        
        return HealthResponse(
            status=HealthStatus.HEALTHY,
            timestamp=datetime.utcnow(),
            version=app_version,
            uptime_seconds=uptime_seconds,
            databases=databases
        )