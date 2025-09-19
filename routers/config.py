"""Configuration management router."""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.core.config import get_config, ConfigManager

router = APIRouter(prefix="/config", tags=["config"])


class ConfigResponse(BaseModel):
    """Configuration response model."""
    app: Dict[str, Any]
    cors: Dict[str, Any]
    database: Dict[str, Any]
    # Note: Exclude sensitive fields like passwords


class ConfigUpdate(BaseModel):
    """Configuration update model."""
    app: Optional[Dict[str, Any]] = None
    cors: Optional[Dict[str, Any]] = None


@router.get("/", response_model=ConfigResponse)
async def get_current_config() -> ConfigResponse:
    """
    Get current application configuration.
    
    Returns:
        ConfigResponse: Current configuration (excluding sensitive data)
    """
    config = get_config()
    
    # Return configuration without sensitive fields
    return ConfigResponse(
        app={
            "name": config.app.name,
            "version": config.app.version,
            "host": config.app.host,
            "port": config.app.port,
            "debug": config.app.debug
        },
        cors={
            "origins": config.cors.origins,
            "methods": config.cors.methods,
            "headers": config.cors.headers
        },
        database={
            "host": config.database.host,
            "port": config.database.port,
            "database": config.database.database,
            "username": config.database.username
            # Exclude password for security
        }
    )


@router.put("/reload")
async def reload_configuration() -> dict:
    """
    Reload configuration from file and environment variables.
    
    Returns:
        dict: Reload status
    """
    try:
        config_manager = ConfigManager()
        config = config_manager.reload()
        
        return {
            "status": "success",
            "message": "Configuration reloaded successfully",
            "version": config.app.version
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reload configuration: {str(e)}")


@router.get("/env-vars")
async def get_environment_variables() -> List[str]:
    """
    Get list of recognized environment variables.
    
    Returns:
        List[str]: List of environment variable names that affect configuration
    """
    return [
        "APP_NAME",
        "APP_VERSION", 
        "APP_HOST",
        "APP_PORT",
        "APP_DEBUG",
        "DB_HOST",
        "DB_PORT",
        "DB_DATABASE",
        "DB_USERNAME",
        "DB_PASSWORD",
        "INFLUXDB_URL",
        "INFLUXDB_TOKEN",
        "INFLUXDB_ORG",
        "INFLUXDB_BUCKET",
        "CORS_ORIGINS",
        "CONFIG_PATH"
    ]


@router.get("/validation")
async def validate_configuration() -> dict:
    """
    Validate current configuration.
    
    Returns:
        dict: Validation results
    """
    config = get_config()
    errors = []
    warnings = []
    
    # Validate database configuration
    if not config.database.database:
        errors.append("Database name is required")
    if not config.database.username:
        errors.append("Database username is required")
    if not config.database.password:
        errors.append("Database password is required")
    
    # Validate InfluxDB configuration
    if not config.influxdb.token:
        warnings.append("InfluxDB token is missing - metrics collection will be disabled")
    if not config.influxdb.org:
        warnings.append("InfluxDB organization is missing")
    if not config.influxdb.bucket:
        warnings.append("InfluxDB bucket is missing")
    
    # Validate CORS configuration
    if not config.cors.origins:
        warnings.append("No CORS origins configured - API will reject cross-origin requests")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "validation_time": "2024-01-01T00:00:00Z"  # Mock timestamp
    }