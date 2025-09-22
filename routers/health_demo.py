"""Simplified health check router."""

from fastapi import APIRouter
from backend.models.health import HealthResponse
from backend.services.health_demo import HealthServiceDemo
from backend.core.config import get_config

router = APIRouter(prefix="/healthz", tags=["health"])
health_service = HealthServiceDemo()


@router.get("", response_model=HealthResponse)
@router.get("/", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Get comprehensive health status of the application.
    
    Returns:
        HealthResponse: Detailed health information including:
        - Overall status (healthy/unhealthy/degraded)
        - Application version and uptime
        - Database connectivity status (mocked in demo mode)
        - Response times for each service
    """
    config = get_config()
    return await health_service.get_health_status(config.app.version)


@router.get("/ping")
async def ping() -> dict:
    """
    Simple ping endpoint for basic health checks.
    
    Returns:
        dict: Simple pong response
    """
    return {"status": "ok", "message": "pong", "mode": "demo"}