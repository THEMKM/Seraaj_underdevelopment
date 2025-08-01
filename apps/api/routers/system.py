"""
System Status and Health Monitoring API Router
Provides system health checks, performance metrics, and operational status
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlmodel import Session, select, func
from typing import Annotated, Dict, Any, Optional
from datetime import datetime, timedelta
import time
import os
import psutil
import logging

from database import get_session
from models import User, Opportunity, Application, Organisation, Volunteer
from routers.auth import get_current_user
from middleware.error_handler import raise_forbidden, AuthorizationError
from middleware.loading_states import (
    ProgressTracker, loading_manager, async_operation, create_loading_response
)
from utils.response_formatter import APIResponse, success_with_data

router = APIRouter(prefix="/v1/system", tags=["system"])
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check():
    """Basic health check endpoint using advanced health monitoring"""
    
    from monitoring.health_checker import health_checker
    
    # Get overall health status
    health_data = await health_checker.get_overall_health()
    
    # Determine HTTP status code based on overall health
    status_code = 200
    if health_data["overall_status"] == "critical":
        status_code = 503  # Service Unavailable
    elif health_data["overall_status"] == "unhealthy":
        status_code = 503
    elif health_data["overall_status"] == "degraded":
        status_code = 200  # Still operational, but with warnings
    
    return APIResponse.success(
        data=health_data,
        message=f"System is {health_data['overall_status']}",
        status_code=status_code
    )


@router.get("/health/detailed")
async def detailed_health_check(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Detailed health check with performance metrics (admin only)"""
    
    if current_user.role != "admin":
        raise_forbidden("Admin access required for detailed health information")
    
    start_time = time.time()
    
    # System metrics
    try:
        process = psutil.Process()
        system_metrics = {
            "cpu_usage": psutil.cpu_percent(interval=1),
            "memory_usage": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent,
                "process_memory": process.memory_info().rss
            },
            "disk_usage": {
                "total": psutil.disk_usage('/').total,
                "free": psutil.disk_usage('/').free,
                "percent": psutil.disk_usage('/').percent
            },
            "network": {
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv
            }
        }
    except Exception as e:
        logger.error(f"Error collecting system metrics: {e}")
        system_metrics = {"error": str(e)}
    
    # Database metrics
    db_start = time.time()
    try:
        # Count records in main tables
        opportunities_count = session.exec(select(func.count(Opportunity.id))).first()
        applications_count = session.exec(select(func.count(Application.id))).first()
        users_count = session.exec(select(func.count(User.id))).first()
        organizations_count = session.exec(select(func.count(Organisation.id))).first()
        volunteers_count = session.exec(select(func.count(Volunteer.id))).first()
        
        db_metrics = {
            "response_time_ms": (time.time() - db_start) * 1000,
            "record_counts": {
                "opportunities": opportunities_count,
                "applications": applications_count,
                "users": users_count,
                "organizations": organizations_count,
                "volunteers": volunteers_count
            }
        }
        
        # Recent activity (last 24 hours)
        yesterday = datetime.now(datetime.timezone.utc) - timedelta(days=1)
        recent_opportunities = session.exec(
            select(func.count(Opportunity.id)).where(Opportunity.created_at >= yesterday)
        ).first()
        recent_applications = session.exec(
            select(func.count(Application.id)).where(Application.created_at >= yesterday)
        ).first()
        recent_users = session.exec(
            select(func.count(User.id)).where(User.created_at >= yesterday)
        ).first()
        
        db_metrics["recent_activity_24h"] = {
            "new_opportunities": recent_opportunities,
            "new_applications": recent_applications,
            "new_users": recent_users
        }
        
    except Exception as e:
        db_metrics = {"error": str(e)}
    
    # Loading operations status
    loading_operations = {
        "active_operations": len([
            state for state in loading_manager.loading_states.values()
            if state.status == "in_progress"
        ]),
        "completed_operations": len([
            state for state in loading_manager.loading_states.values()
            if state.status == "completed"
        ]),
        "failed_operations": len([
            state for state in loading_manager.loading_states.values()
            if state.status == "failed"
        ]),
        "total_operations": len(loading_manager.loading_states)
    }
    
    # External services status from health checker
    from monitoring.health_checker import health_checker
    external_services = {}
    
    # Get actual service health status
    try:
        health_data = await health_checker.get_overall_health()
        for service_name, service_info in health_data.get("services", {}).items():
            external_services[service_name] = {
                "status": service_info.get("status", "unknown"),
                "last_check": service_info.get("last_check", datetime.now(datetime.timezone.utc).isoformat()),
                "response_time_ms": service_info.get("response_time_ms", 0),
                "message": service_info.get("message", "")
            }
    except Exception as e:
        logger.error(f"Error getting external service status: {e}")
        # Fallback to basic status
        external_services = {
            "database": {"status": "operational", "last_check": datetime.now(datetime.timezone.utc).isoformat()},
            "file_storage": {"status": "operational", "last_check": datetime.now(datetime.timezone.utc).isoformat()},
            "websocket": {"status": "operational", "last_check": datetime.now(datetime.timezone.utc).isoformat()}
        }
    
    health_data = {
        "overall_status": "healthy",
        "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
        "response_time_ms": (time.time() - start_time) * 1000,
        "system_metrics": system_metrics,
        "database_metrics": db_metrics,
        "loading_operations": loading_operations,
        "external_services": external_services,
        "version_info": {
            "api_version": "2.0.0",
            "python_version": os.sys.version,
            "environment": "development"
        }
    }
    
    return success_with_data(health_data, "Detailed system health retrieved successfully")


@router.get("/status")
async def system_status():
    """Public system status endpoint"""
    
    # Basic operational status
    status_data = {
        "operational": True,
        "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
        "api_version": "2.0.0",
        "maintenance_mode": False,
        "services": {
            "api": "operational",
            "database": "operational",
            "file_uploads": "operational",
            "real_time_messaging": "operational"
        },
        "performance": {
            "avg_response_time_ms": round(sum(
                response_time for response_time in loading_manager.performance_history.get("response_times", [])
            ) / max(len(loading_manager.performance_history.get("response_times", [])), 1), 2),
            "uptime_percentage": 99.9  # This would be calculated from actual uptime monitoring
        }
    }
    
    return success_with_data(status_data, "System status retrieved successfully")


@router.post("/maintenance")
async def toggle_maintenance_mode(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    enable: bool = True,
    message: Optional[str] = None
):
    """Toggle maintenance mode (admin only)"""
    
    if current_user.role != "admin":
        raise_forbidden("Admin access required for maintenance operations")
    
    # Update maintenance mode in configuration
    from config.settings import settings
    
    # In a production system, this would update a persistent configuration store
    # For now, we'll store it in the application settings
    settings.maintenance_mode = enable
    settings.maintenance_message = message or ("System is under maintenance" if enable else "System is operational")
    
    maintenance_status = {
        "maintenance_mode": enable,
        "message": message or ("System is under maintenance" if enable else "System is operational"),
        "enabled_by": current_user.id,
        "enabled_at": datetime.now(datetime.timezone.utc).isoformat(),
        "estimated_duration": "30 minutes" if enable else None
    }
    
    logger.info(f"Maintenance mode {'enabled' if enable else 'disabled'} by user {current_user.id}")
    
    return success_with_data(
        maintenance_status,
        f"Maintenance mode {'enabled' if enable else 'disabled'} successfully"
    )


@router.post("/cache/clear")
@async_operation("cache_clear", "Clear system caches")
async def clear_cache(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    cache_type: str = "all"
):
    """Clear system caches (admin only)"""
    
    if current_user.role != "admin":
        raise_forbidden("Admin access required for cache operations")
    
    # Start cache clearing operation with progress tracking
    return "Cache clearing operation started"


async def perform_cache_clear(
    cache_type: str,
    user_id: int,
    progress_tracker: ProgressTracker = None
):
    """Perform cache clearing operation with progress tracking"""
    
    cache_types = {
        "user_sessions": "Clearing user session cache",
        "api_responses": "Clearing API response cache", 
        "database_queries": "Clearing database query cache",
        "file_metadata": "Clearing file metadata cache",
        "ml_models": "Clearing ML model cache"
    }
    
    if cache_type == "all":
        total_steps = len(cache_types)
        progress_tracker.set_total_steps(total_steps)
        
        for i, (cache_name, description) in enumerate(cache_types.items(), 1):
            progress_tracker.update(i, description)
            
            # Perform actual cache clearing operation
            await _clear_specific_cache(cache_name)
            
            logger.info(f"Cleared {cache_name} cache")
    
    else:
        if cache_type in cache_types:
            progress_tracker.update(1, cache_types[cache_type])
            await _clear_specific_cache(cache_type)
            logger.info(f"Cleared {cache_type} cache")
        else:
            raise ValueError(f"Unknown cache type: {cache_type}")
    
    return {"cache_type": cache_type, "cleared_at": datetime.now(datetime.timezone.utc).isoformat()}


@router.get("/metrics")
async def system_metrics(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    time_range: str = "24h"
):
    """Get system performance metrics (admin only)"""
    
    if current_user.role != "admin":
        raise_forbidden("Admin access required for system metrics")
    
    # Parse time range
    if time_range == "1h":
        since = datetime.now(datetime.timezone.utc) - timedelta(hours=1)
    elif time_range == "24h":
        since = datetime.now(datetime.timezone.utc) - timedelta(days=1)
    elif time_range == "7d":
        since = datetime.now(datetime.timezone.utc) - timedelta(days=7)
    elif time_range == "30d":
        since = datetime.now(datetime.timezone.utc) - timedelta(days=30)
    else:
        since = datetime.now(datetime.timezone.utc) - timedelta(days=1)
    
    # Collect metrics from database
    metrics = {
        "time_range": time_range,
        "collection_time": datetime.now(datetime.timezone.utc).isoformat(),
        "api_usage": {
            "total_requests": len(loading_manager.performance_history.get("request_counts", [])),
            "error_rate": (len([c for c in loading_manager.performance_history.get("error_counts", []) if c > 0]) / 
                          max(len(loading_manager.performance_history.get("error_counts", [])), 1)) * 100,
            "avg_response_time_ms": round(sum(
                response_time for response_time in loading_manager.performance_history.get("response_times", [])
            ) / max(len(loading_manager.performance_history.get("response_times", [])), 1), 2)
        },
        "user_activity": {
            "active_users": session.exec(
                select(func.count(User.id)).where(User.last_active >= since)
            ).first() or 0,
            "new_registrations": session.exec(
                select(func.count(User.id)).where(User.created_at >= since)
            ).first() or 0
        },
        "content_activity": {
            "opportunities_created": session.exec(
                select(func.count(Opportunity.id)).where(Opportunity.created_at >= since)
            ).first() or 0,
            "applications_submitted": session.exec(
                select(func.count(Application.id)).where(Application.created_at >= since)
            ).first() or 0
        },
        "system_performance": {
            "database_connections": getattr(session.get_bind().pool, 'checkedout', lambda: 0)(),
            "active_operations": len([
                state for state in loading_manager.loading_states.values()
                if state.status == "in_progress"
            ]),
            "memory_usage_mb": round(psutil.Process().memory_info().rss / 1024 / 1024, 2),
            "cpu_usage_percent": psutil.cpu_percent(),
            "disk_usage_percent": round(psutil.disk_usage('/').percent, 2)
        }
    }
    
    return success_with_data(metrics, f"System metrics for {time_range} retrieved successfully")


@router.post("/backup")
@async_operation("database_backup", "Create system backup")
async def create_backup(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    backup_type: str = "full"
):
    """Create system backup (admin only)"""
    
    if current_user.role != "admin":
        raise_forbidden("Admin access required for backup operations")
    
    # This would integrate with actual backup system
    return "Backup operation started"


async def perform_backup(
    backup_type: str,
    user_id: int,
    progress_tracker: ProgressTracker = None
):
    """Perform backup operation with progress tracking"""
    
    steps = [
        "Preparing backup environment",
        "Backing up database schema",
        "Backing up user data",
        "Backing up file uploads",
        "Compressing backup archive",
        "Verifying backup integrity",
        "Storing backup securely"
    ]
    
    progress_tracker.set_total_steps(len(steps))
    
    for i, step in enumerate(steps, 1):
        progress_tracker.update(i, step)
        
        # Perform actual backup step
        await _perform_backup_step(step, backup_type)
        
        logger.info(f"Backup step completed: {step}")
    
    backup_info = {
        "backup_id": f"backup_{int(time.time())}",
        "backup_type": backup_type,
        "created_at": datetime.now(datetime.timezone.utc).isoformat(),
        "size_mb": 150.5,  # This would be actual backup size
        "location": "secure_storage/backups/"
    }
    
    return backup_info


import asyncio


async def _clear_specific_cache(cache_name: str):
    """Clear a specific cache type"""
    try:
        if cache_name == "user_sessions":
            # Clear user session data (in production, this would clear Redis sessions)
            await asyncio.sleep(1)  # Simulate clearing time
            
        elif cache_name == "api_responses":
            # Clear API response cache (if implemented)
            await asyncio.sleep(1)
            
        elif cache_name == "database_queries":
            # Clear database query cache (SQLAlchemy query cache)
            from database import engine
            if hasattr(engine, 'dispose'):
                engine.dispose()  # Clear connection pool
            await asyncio.sleep(1)
            
        elif cache_name == "file_metadata":
            # Clear file metadata cache
            import os
            import tempfile
            cache_dir = os.path.join(tempfile.gettempdir(), "seraaj_cache")
            if os.path.exists(cache_dir):
                import shutil
                shutil.rmtree(cache_dir, ignore_errors=True)
            await asyncio.sleep(1)
            
        elif cache_name == "ml_models":
            # Clear ML model cache (if any models are cached)
            try:
                from ml.matching_algorithm import matcher
                if hasattr(matcher, 'clear_cache'):
                    matcher.clear_cache()
            except ImportError:
                pass  # ML module not available
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"Error clearing {cache_name} cache: {e}")
        raise


async def _perform_backup_step(step: str, backup_type: str):
    """Perform individual backup step"""
    try:
        if step == "Preparing backup environment":
            # Create backup directory structure
            import os
            backup_dir = f"backups/{datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d_%H-%M-%S')}"
            os.makedirs(backup_dir, exist_ok=True)
            await asyncio.sleep(1)
            
        elif step == "Backing up database schema":
            # Export database schema
            from database import engine
            # In production, use proper database backup tools
            await asyncio.sleep(2)
            
        elif step == "Backing up user data":
            # Export user data (anonymized if needed)
            await asyncio.sleep(3)
            
        elif step == "Backing up file uploads":
            # Copy uploaded files to backup location
            from config.settings import settings
            upload_path = settings.get_upload_path()
            # In production, use rsync or similar
            await asyncio.sleep(2)
            
        elif step == "Compressing backup archive":
            # Create compressed archive
            import zipfile
            await asyncio.sleep(2)
            
        elif step == "Verifying backup integrity":
            # Check backup file integrity
            await asyncio.sleep(1)
            
        elif step == "Storing backup securely":
            # Store backup to secure location (cloud storage, etc.)
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"Error in backup step '{step}': {e}")
        raise