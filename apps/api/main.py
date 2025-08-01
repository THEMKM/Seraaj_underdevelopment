# -*- coding: utf-8 -*-
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from database import create_db_and_tables, get_session
from routers import auth
from typing import Annotated
from sqlmodel import Session, text
from middleware.error_handler import error_handler, error_handling_middleware
from middleware.loading_states import response_timing_middleware
from middleware.request_logging import (
    RequestLoggingMiddleware,
    APIMetricsMiddleware,
    get_api_metrics,
)
from config.settings import (
    settings,
    initialize_config,
    get_cors_config,
    get_logging_config,
    Environment,
)
from services.unified_seeding_service import seed_database
from datetime import datetime
import logging

# DIVINE ENCODING CONFIGURATION - Honor the gods of code!
from utils.encoding_config import configure_divine_encoding

configure_divine_encoding()

# Initialize configuration
initialize_config()

# Configure logging
log_config = get_logging_config()
logging.basicConfig(
    level=getattr(logging, log_config["level"]), format=log_config["format"]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events for startup and shutdown"""
    # Startup logic
    try:
        logger.info("Starting database initialization...")
        create_db_and_tables()
        logger.info("Database initialized successfully")

        # Force SQLAlchemy to configure all relationships
        logger.info("Configuring SQLAlchemy relationships...")
        from sqlalchemy.orm import configure_mappers

        configure_mappers()  # Force relationship configuration
        logger.info("SQLAlchemy relationships configured successfully")

        if settings.environment == Environment.DEVELOPMENT:
            logger.info("Seeding database for development environment...")
            try:
                seed_database(clear_existing=True)
            except Exception as seed_err:
                logger.error(f"Database seeding failed: {seed_err}")
            else:
                logger.info("Database seeding completed")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Continue anyway to keep server running
        logger.info("Server continuing without database initialization")

    yield

    # Shutdown logic
    logger.info("API server shutting down...")


app = FastAPI(
    title=settings.api.title,
    description=settings.api.description,
    version=settings.api.version,
    docs_url="/docs",  # Force standard docs URL
    redoc_url="/redoc",  # Force standard redoc URL
    openapi_url="/openapi.json",  # Force standard openapi URL
    debug=settings.debug,
    lifespan=lifespan,
)

# Add CORS middleware FIRST (most important for API access)
cors_config = get_cors_config()
logger.info(f"Environment: {settings.environment}")
logger.info(f"Is Production: {settings.is_production}")
logger.info(f"CORS Configuration: {cors_config}")

# Add CORS middleware - using working configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config["allow_origins"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=["*"],
)

# Re-enable other middleware now that CORS is isolated
# Add middleware in reverse order (last added = first executed, so CORS is last)
# Add request logging middleware
log_level = "INFO" if settings.environment == "production" else "DEBUG"
app.add_middleware(RequestLoggingMiddleware, log_level=log_level)

# Add API metrics middleware
app.add_middleware(APIMetricsMiddleware)

# Add response timing middleware
app.middleware("http")(response_timing_middleware)

# Add error handling middleware (outermost)
app.middleware("http")(error_handling_middleware)

# Add rate limiting middleware (disabled for now)
# from middleware.rate_limiter import rate_limiting_middleware
# app.middleware("http")(rate_limiting_middleware)


# Exception handlers for better error responses
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return await error_handler.handle_error(request, exc)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return await error_handler.handle_error(request, exc)


# BASIC ROUTE DEFINITIONS FIRST (MOVED FROM BOTTOM)
@app.get("/")
async def root():
    return {"message": "Seraaj API v2.0.0"}


# Remove duplicate health endpoint
# @app.get("/health")
# async def health_check():
#     return {"status": "healthy"}
# Remove this later as we have a more detailed health check

# Temporary search endpoint removed - using proper search in opportunities router

# Include routers
app.include_router(auth.router)

# Import other routers after creating them
from routers import (
    opportunities,
    applications,
    profiles,
    reviews,
    files,
    admin,
    match,
    websocket,
    organizations,
)
from routers import (
    verification,
    collaboration,
    operations,
    system,
    guided_tours,
)  # Re-enabled after fixing issues

# Push notifications router - restored after comprehensive relationship recovery
from routers import push_notifications

# from routers import pwa, demo_scenarios, calendar
from routers import pwa, demo_scenarios, calendar

app.include_router(opportunities.router)
app.include_router(applications.router)
app.include_router(profiles.router)
app.include_router(reviews.router)
app.include_router(files.router)
app.include_router(admin.router)
app.include_router(match.router)
app.include_router(websocket.router)
app.include_router(organizations.router)
# Re-enabled routers after fixing dependency issues:
app.include_router(verification.router)
app.include_router(collaboration.router)
app.include_router(operations.router)
app.include_router(system.router)
# Payment router removed - not part of MVP
app.include_router(guided_tours.router)
# Previously disabled routers - now re-enabled after fixing import issues:
app.include_router(calendar.router)
app.include_router(pwa.router)
# Push notifications router - restored after comprehensive relationship recovery
app.include_router(push_notifications.router)
app.include_router(demo_scenarios.router)


@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "message": "API is running"}


# === Legacy API Deprecation Stubs ===
# These endpoints provide graceful deprecation for old API clients


@app.api_route(
    "/api/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
)
async def legacy_api_deprecation(path: str):
    """Handle legacy /api/ prefixed endpoints with deprecation notice"""
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=410,  # Gone
        content={
            "error": True,
            "error_code": "ENDPOINT_DEPRECATED",
            "message": f"The /api/{path} endpoint has been deprecated. Please use /v1/{path} instead.",
            "new_endpoint": f"/v1/{path}",
            "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
            "details": {
                "migration_guide": "https://docs.seraaj.org/api/migration",
                "support_ends": "2025-12-31",
            },
        },
        headers={
            "X-Deprecated": "true",
            "X-Migration-Guide": "https://docs.seraaj.org/api/migration",
            "X-New-Endpoint": f"/v1/{path}",
        },
    )


@app.api_route(
    "/auth/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
)
async def legacy_auth_deprecation(path: str):
    """Handle legacy /auth/ endpoints without v1 prefix"""
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=410,  # Gone
        content={
            "error": True,
            "error_code": "ENDPOINT_DEPRECATED",
            "message": f"The /auth/{path} endpoint has been deprecated. Please use /v1/auth/{path} instead.",
            "new_endpoint": f"/v1/auth/{path}",
            "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
            "details": {
                "migration_guide": "https://docs.seraaj.org/api/migration",
                "support_ends": "2025-12-31",
            },
        },
        headers={
            "X-Deprecated": "true",
            "X-Migration-Guide": "https://docs.seraaj.org/api/migration",
            "X-New-Endpoint": f"/v1/auth/{path}",
        },
    )


@app.get("/health/detailed")
async def detailed_health_check(session: Annotated[Session, Depends(get_session)]):
    """Detailed health check with database connectivity"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
        "version": settings.api.version,
        "environment": settings.environment,
        "services": {"api": "healthy", "database": "unknown"},
    }

    # Test database connectivity
    try:
        # Simple query to test database
        result = session.execute(text("SELECT 1")).scalar()
        if result == 1:
            health_status["services"]["database"] = "healthy"
        else:
            health_status["services"]["database"] = "unhealthy"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
        health_status["database_error"] = str(e)

    # Determine overall status
    if any(service != "healthy" for service in health_status["services"].values()):
        health_status["status"] = "degraded"

    status_code = 200 if health_status["status"] in ["healthy", "degraded"] else 503
    return JSONResponse(content=health_status, status_code=status_code)


@app.get("/metrics")
async def get_metrics():
    """Get API performance metrics"""
    return get_api_metrics()


@app.get("/health/readiness")
async def readiness_check():
    """Kubernetes readiness probe"""
    return {
        "status": "ready",
        "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
    }


@app.get("/health/liveness")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {
        "status": "alive",
        "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
    }


@app.get("/admin/database/health")
async def database_health():
    """Get comprehensive database health report"""
    try:
        from database.optimization import get_database_health

        return get_database_health()
    except ImportError:
        return {"error": "Database optimization module not available"}


@app.post("/admin/database/optimize")
async def optimize_database_endpoint():
    """Run database optimization (admin only)"""
    try:
        from database.optimization import optimize_database

        return optimize_database()
    except ImportError:
        return {"error": "Database optimization module not available"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
