"""Main FastAPI application - simplified version without database connections."""

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from routers import (
    health_router,
    llm_router, 
    bamboo_router,
    reports_router,
    config_router
)

# Import core components
from backend.core.config import get_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and shutdown events."""
    # Startup
    config = get_config()
    
    print(f"🚀 {config.app.name} v{config.app.version} started")
    print("⚠️  Running in demo mode (databases not connected)")
    
    yield
    
    # Shutdown
    print("🛑 Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    config = get_config()
    
    app = FastAPI(
        title=config.app.name,
        version=config.app.version,
        description="DevOps Autopilot - Automated DevOps Operations Platform",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors.origins,
        allow_credentials=True,
        allow_methods=config.cors.methods,
        allow_headers=config.cors.headers,
    )
    
    # Include routers
    app.include_router(health_router)
    app.include_router(llm_router)
    app.include_router(bamboo_router)
    app.include_router(reports_router)
    app.include_router(config_router)
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with basic API information."""
        return {
            "name": config.app.name,
            "version": config.app.version,
            "status": "running",
            "mode": "demo",
            "docs_url": "/docs",
            "health_url": "/healthz"
        }
    
    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    """Run the application with Uvicorn when executed directly."""
    config = get_config()
    
    uvicorn.run(
        "main_demo:app",
        host=config.app.host,
        port=config.app.port,
        reload=config.app.debug,
        log_level="info" if not config.app.debug else "debug"
    )