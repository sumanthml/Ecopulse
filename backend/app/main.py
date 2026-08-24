"""
EcoPulse Backend Application Entry Point
Production-ready FastAPI application setup with CORS, middleware, and routers.
"""
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import check_database_health
from app.api.dashboard import router as dashboard_router
from app.api.pollution import router as pollution_router
from app.api.sensors import locations_router, sensors_router
from app.api.alerts import router as alerts_router
from app.api.analytics import router as analytics_router
from app.api.prediction import router as prediction_router
from app.api.ai_insight import router as ai_insight_router
from app.workers.data_collector import data_collector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-30s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ecopulse")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events: start background workers on startup, gracefully stop on shutdown."""
    logger.info("=" * 60)
    logger.info("EcoPulse Environmental Intelligence Platform")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Data Provider: {settings.data_provider}")
    logger.info(f"Demo Mode: {settings.demo_mode}")
    logger.info(f"Database: {'configured' if settings.has_database else 'NOT configured'}")
    logger.info(f"Groq AI: {'configured' if settings.has_groq else 'NOT configured'}")
    logger.info("=" * 60)

    # Start background telemetry data collector worker
    await data_collector.start()
    logger.info("Data collector started")

    yield

    # Shutdown background worker
    await data_collector.stop()
    logger.info("EcoPulse shutdown complete")


app = FastAPI(
    title="EcoPulse API",
    description="Real-Time Environmental Pollution Monitoring and Analysis System API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Configuration — allow localhost, Vercel deployments, and wildcard origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(dashboard_router)
app.include_router(pollution_router)
app.include_router(locations_router)
app.include_router(sensors_router)
app.include_router(alerts_router)
app.include_router(analytics_router)
app.include_router(prediction_router)
app.include_router(ai_insight_router)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Silence browser favicon 404 requests."""
    return Response(status_code=204)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint returning basic metadata."""
    return {
        "name": "EcoPulse API",
        "description": "Environmental Pollution Monitoring and Analysis System",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint verifying database, provider, and AI connectivity."""
    db_health = await check_database_health()
    collector_status = data_collector.get_status()

    is_healthy = db_health.get("status") == "healthy" and collector_status.get("running", False)

    return JSONResponse(
        status_code=200 if is_healthy else 200,
        content={
            "status": "healthy" if is_healthy else "degraded",
            "database": db_health.get("status", "unknown"),
            "provider": "ONLINE" if collector_status.get("running") else "OFFLINE",
            "ai": "available" if settings.has_groq else "unavailable",
            "version": "1.0.0",
        },
    )
