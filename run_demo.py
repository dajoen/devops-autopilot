"""Demo FastAPI application runner."""

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers - using demo health router
from routers.health_demo import router as health_router
from routers.llm import router as llm_router
from routers.bamboo import router as bamboo_router
from routers.reports import router as reports_router
from routers.config import router as config_router

# Import core components
from backend.core.config import get_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and shutdown events."""
    # Startup
    config = get_config()
    
    print(f"🚀 {config.app.name} v{config.app.version} started")
    print("⚠️  Running in demo mode (databases not connected)")
    print(f"📖 API Documentation: http://{config.app.host}:{config.app.port}/docs")
    print(f"🏥 Health Check: http://{config.app.host}:{config.app.port}/healthz")
    
    yield
    
    # Shutdown
    print("🛑 Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    config = get_config()
    
    app = FastAPI(
        title=config.app.name,
        version=config.app.version,
        description="DevOps Autopilot - Automated DevOps Operations Platform (Demo Mode)",
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
            "message": "FastAPI DevOps Autopilot is running in demo mode",
            "endpoints": {
                "docs": "/docs",
                "health": "/healthz",
                "llm": "/llm",
                "bamboo": "/bamboo", 
                "reports": "/reports",
                "config": "/config"
            }
        }
    
    return app


def main():
    """Main entry point for Poetry script."""
    config = get_config()
    
    print("🔧 DevOps Autopilot - Demo Mode")
    print("=" * 50)
    print("Starting FastAPI application...")
    print(f"App: {config.app.name} v{config.app.version}")
    print(f"Host: {config.app.host}:{config.app.port}")
    print(f"Debug: {config.app.debug}")
    print("=" * 50)
    
    uvicorn.run(
        "run_demo:create_app",
        factory=True,
        host=config.app.host,
        port=config.app.port,
        reload=config.app.debug,
        log_level="info" if not config.app.debug else "debug"
    )


if __name__ == "__main__":
    """Run the application with Uvicorn when executed directly."""
    main()