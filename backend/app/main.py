"""
EcoPulse - Main FastAPI Application

Environmental Pollution Monitoring and Analysis System
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import check_database_health
from app.workers.data_collector import data_collector
from app.ai.groq_client import check_groq_health

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-30s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ecopulse")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    # ── Startup ──
    logger.info("=" * 60)
    logger.info("EcoPulse Environmental Intelligence Platform")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Data Provider: {settings.data_provider}")
    logger.info(f"Demo Mode: {settings.demo_mode}")
    logger.info(f"Database: {'configured' if settings.has_database else 'NOT configured'}")
    logger.info(f"Groq AI: {'configured' if settings.has_groq else 'NOT configured'}")
    logger.info("=" * 60)

    # Start data collector if database is configured
    if settings.has_database and (settings.demo_mode or settings.data_provider != "none"):
        await data_collector.start()
        logger.info("Data collector started")

    yield

    # ── Shutdown ──
    await data_collector.stop()
    logger.info("EcoPulse shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="EcoPulse API",
    description="Real-Time Environmental Pollution Monitoring and Analysis System",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ──
from app.api.dashboard import router as dashboard_router
from app.api.pollution import router as pollution_router
from app.api.sensors import locations_router, sensors_router
from app.api.alerts import router as alerts_router
from app.api.analytics import router as analytics_router
from app.api.prediction import predictions_router, insights_router

app.include_router(dashboard_router)
app.include_router(pollution_router)
app.include_router(locations_router)
app.include_router(sensors_router)
app.include_router(alerts_router)
app.include_router(analytics_router)
app.include_router(predictions_router)
app.include_router(insights_router)


# ── Health Check ──

@app.get("/health", tags=["System"])
async def health_check():
    """System health check."""
    db_health = await check_database_health()
    ai_health = await check_groq_health()
    collector = data_collector.get_status()

    provider_status = "ONLINE" if collector.get("running") else "OFFLINE"
    if collector.get("last_error"):
        provider_status = "DEGRADED"

    overall = "healthy"
    if db_health.get("status") != "healthy":
        overall = "degraded"

    return {
        "status": overall,
        "database": db_health.get("status", "not_configured"),
        "provider": provider_status,
        "ai": ai_health.get("status", "not_configured"),
        "version": "1.0.0",
    }


@app.get("/api/system/status", tags=["System"])
async def system_status():
    """Detailed system status."""
    db_health = await check_database_health()
    ai_health = await check_groq_health()
    collector = data_collector.get_status()

    return {
        "success": True,
        "data": {
            "api": {"status": "ONLINE"},
            "database": db_health,
            "realtime": {"status": "ONLINE" if settings.has_supabase else "not_configured"},
            "data_provider": collector,
            "ai": ai_health,
            "config": {
                "environment": settings.app_env,
                "demo_mode": settings.demo_mode,
                "data_provider": settings.data_provider,
            },
        },
    }


# ── Simulator Control (Demo Mode) ──

@app.post("/api/system/scenario", tags=["System"])
async def set_scenario(scenario: str):
    """Change the simulator scenario (demo mode only)."""
    valid = ["normal", "rush_hour", "high_pollution", "pollution_spike", "sensor_failure"]
    if scenario not in valid:
        return {"success": False, "error": {"code": "INVALID_SCENARIO", "message": f"Valid: {valid}"}}

    success = data_collector.set_scenario(scenario)
    if not success:
        return {"success": False, "error": {"code": "NOT_SIMULATOR", "message": "Only works with simulator provider"}}

    return {"success": True, "message": f"Scenario changed to: {scenario}"}


@app.get("/", tags=["System"])
async def root():
    """API root."""
    return {
        "name": "EcoPulse API",
        "description": "Environmental Pollution Monitoring and Analysis System",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
