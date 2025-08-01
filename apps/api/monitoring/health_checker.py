"""
Advanced Health Monitoring System for Seraaj API
Provides comprehensive health checks, performance monitoring, and alerting
"""
import asyncio
import time
import psutil
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from collections import deque
import json

from config.settings import settings
from middleware.loading_states import ProgressTracker
from middleware.error_handler import ExternalServiceError

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


class ServiceType(str, Enum):
    """Types of services to monitor"""
    DATABASE = "database"
    REDIS = "redis"
    FILE_STORAGE = "file_storage"
    EMAIL = "email"
    EXTERNAL_API = "external_api"
    WEBSOCKET = "websocket"
    ML_SERVICE = "ml_service"


@dataclass
class HealthMetric:
    """Individual health metric"""
    name: str
    value: float
    unit: str
    status: HealthStatus
    threshold_warning: float
    threshold_critical: float
    message: str = ""
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def update(self, value: float, message: str = ""):
        """Update metric value and determine status"""
        self.value = value
        self.message = message
        self.last_updated = datetime.now(datetime.timezone.utc)
        
        if value >= self.threshold_critical:
            self.status = HealthStatus.CRITICAL
        elif value >= self.threshold_warning:
            self.status = HealthStatus.DEGRADED
        else:
            self.status = HealthStatus.HEALTHY
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "status": self.status.value,
            "threshold_warning": self.threshold_warning,
            "threshold_critical": self.threshold_critical,
            "message": self.message,
            "last_updated": self.last_updated.isoformat()
        }


@dataclass
class ServiceHealth:
    """Health status of a service"""
    service_type: ServiceType
    status: HealthStatus
    response_time_ms: float
    error_count: int
    last_check: datetime
    message: str = ""
    metrics: Dict[str, HealthMetric] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "service_type": self.service_type.value,
            "status": self.status.value,
            "response_time_ms": self.response_time_ms,
            "error_count": self.error_count,
            "last_check": self.last_check.isoformat(),
            "message": self.message,
            "metrics": {name: metric.to_dict() for name, metric in self.metrics.items()}
        }


class HealthChecker:
    """Comprehensive health checking system"""
    
    def __init__(self):
        # Service health trackers
        self.services: Dict[ServiceType, ServiceHealth] = {}
        
        # System metrics
        self.system_metrics: Dict[str, HealthMetric] = {
            "cpu_usage": HealthMetric("CPU Usage", 0, "%", HealthStatus.HEALTHY, 70, 90),
            "memory_usage": HealthMetric("Memory Usage", 0, "%", HealthStatus.HEALTHY, 80, 95),
            "disk_usage": HealthMetric("Disk Usage", 0, "%", HealthStatus.HEALTHY, 85, 95),
            "response_time": HealthMetric("Avg Response Time", 0, "ms", HealthStatus.HEALTHY, 1000, 3000),
            "error_rate": HealthMetric("Error Rate", 0, "%", HealthStatus.HEALTHY, 1, 5),
            "active_connections": HealthMetric("Active Connections", 0, "count", HealthStatus.HEALTHY, 800, 1000)
        }
        
        # Performance history
        self.performance_history: Dict[str, deque] = {
            "response_times": deque(maxlen=100),
            "error_counts": deque(maxlen=100),
            "request_counts": deque(maxlen=100)
        }
        
        # Health check configurations
        self.check_intervals = {
            ServiceType.DATABASE: 30,  # seconds
            ServiceType.REDIS: 60,
            ServiceType.FILE_STORAGE: 120,
            ServiceType.EMAIL: 300,
            ServiceType.WEBSOCKET: 60,
            ServiceType.ML_SERVICE: 180
        }
        
        # Alert configurations
        self.alert_thresholds = {
            "consecutive_failures": 3,
            "error_rate_threshold": 5.0,
            "response_time_threshold": 3000.0
        }
        
        # Health check tasks
        self.check_tasks: Dict[ServiceType, asyncio.Task] = {}
        self.monitoring_active = False
        
        # Initialize services
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize service health trackers"""
        for service_type in ServiceType:
            self.services[service_type] = ServiceHealth(
                service_type=service_type,
                status=HealthStatus.HEALTHY,
                response_time_ms=0,
                error_count=0,
                last_check=datetime.now(datetime.timezone.utc)
            )
    
    async def start_monitoring(self):
        """Start continuous health monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        logger.info("Starting health monitoring system")
        
        # Start health check tasks for each service
        for service_type, interval in self.check_intervals.items():
            self.check_tasks[service_type] = asyncio.create_task(
                self._periodic_health_check(service_type, interval)
            )
        
        # Start system metrics monitoring
        self.check_tasks["system_metrics"] = asyncio.create_task(
            self._monitor_system_metrics()
        )
    
    async def stop_monitoring(self):
        """Stop health monitoring"""
        self.monitoring_active = False
        logger.info("Stopping health monitoring system")
        
        # Cancel all health check tasks
        for task in self.check_tasks.values():
            if not task.done():
                task.cancel()
        
        self.check_tasks.clear()
    
    async def _periodic_health_check(self, service_type: ServiceType, interval: int):
        """Perform periodic health checks for a service"""
        while self.monitoring_active:
            try:
                await self._check_service_health(service_type)
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic health check for {service_type}: {e}")
                await asyncio.sleep(interval)
    
    async def _check_service_health(self, service_type: ServiceType):
        """Check health of a specific service"""
        start_time = time.time()
        service_health = self.services[service_type]
        
        try:
            # Perform service-specific health check
            if service_type == ServiceType.DATABASE:
                await self._check_database_health(service_health)
            elif service_type == ServiceType.REDIS:
                await self._check_redis_health(service_health)
            elif service_type == ServiceType.FILE_STORAGE:
                await self._check_file_storage_health(service_health)
            elif service_type == ServiceType.EMAIL:
                await self._check_email_health(service_health)
            elif service_type == ServiceType.WEBSOCKET:
                await self._check_websocket_health(service_health)
            elif service_type == ServiceType.ML_SERVICE:
                await self._check_ml_service_health(service_health)
            
            # Update response time
            response_time = (time.time() - start_time) * 1000
            service_health.response_time_ms = response_time
            service_health.last_check = datetime.now(datetime.timezone.utc)
            
            # If we got here without exception, service is healthy
            if service_health.status == HealthStatus.UNHEALTHY:
                service_health.status = HealthStatus.HEALTHY
                service_health.message = "Service recovered"
                logger.info(f"{service_type.value} service recovered")
        
        except Exception as e:
            # Service check failed
            service_health.error_count += 1
            service_health.status = HealthStatus.UNHEALTHY
            service_health.message = str(e)
            service_health.last_check = datetime.now(datetime.timezone.utc)
            
            logger.error(f"Health check failed for {service_type.value}: {e}")
    
    async def _check_database_health(self, service_health: ServiceHealth):
        """Check database health"""
        from database import engine
        
        # Test database connection
        async with engine.begin() as conn:
            result = await conn.execute("SELECT 1")
            await result.fetchone()
        
        # Add database-specific metrics
        service_health.metrics["connection_pool"] = HealthMetric(
            "Connection Pool Usage", 0, "%", HealthStatus.HEALTHY, 80, 95
        )
        
        service_health.message = "Database connection healthy"
    
    async def _check_redis_health(self, service_health: ServiceHealth):
        """Check Redis health"""
        try:
            if not hasattr(settings, 'redis') or not settings.redis.url:
                service_health.status = HealthStatus.DEGRADED
                service_health.message = "Redis not configured"
                return
            
            # Test Redis connection if available
            try:
                import redis
                r = redis.from_url(settings.redis.url)
                r.ping()
                service_health.message = "Redis connection healthy"
            except ImportError:
                service_health.status = HealthStatus.DEGRADED
                service_health.message = "Redis client not available"
            except Exception as e:
                service_health.status = HealthStatus.UNHEALTHY
                service_health.message = f"Redis connection failed: {str(e)}"
                
        except Exception as e:
            service_health.status = HealthStatus.DEGRADED
            service_health.message = f"Redis check error: {str(e)}"
    
    async def _check_file_storage_health(self, service_health: ServiceHealth):
        """Check file storage health"""
        import os
        
        upload_dir = settings.get_upload_path()
        
        # Check if upload directory is accessible
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, exist_ok=True)
        
        # Check disk space
        disk_usage = psutil.disk_usage(upload_dir)
        free_space_gb = disk_usage.free / (1024**3)
        
        if free_space_gb < 1:  # Less than 1GB free
            service_health.status = HealthStatus.CRITICAL
            service_health.message = f"Low disk space: {free_space_gb:.2f}GB free"
        elif free_space_gb < 5:  # Less than 5GB free
            service_health.status = HealthStatus.DEGRADED
            service_health.message = f"Disk space warning: {free_space_gb:.2f}GB free"
        else:
            service_health.message = f"File storage healthy: {free_space_gb:.2f}GB free"
        
        # Add storage metrics
        service_health.metrics["free_space"] = HealthMetric(
            "Free Space", free_space_gb, "GB", HealthStatus.HEALTHY, 5, 1
        )
    
    async def _check_email_health(self, service_health: ServiceHealth):
        """Check email service health"""
        try:
            if not hasattr(settings, 'email') or not settings.email.smtp_host:
                service_health.status = HealthStatus.DEGRADED
                service_health.message = "Email service not configured"
                return
            
            # Test SMTP connection
            import smtplib
            import socket
            
            try:
                # Try to connect to SMTP server with timeout
                with smtplib.SMTP(settings.email.smtp_host, settings.email.smtp_port, timeout=10) as server:
                    server.noop()  # Simple test command
                service_health.message = "Email service connection healthy"
            except socket.timeout:
                service_health.status = HealthStatus.DEGRADED
                service_health.message = "Email service connection timeout"
            except Exception as e:
                service_health.status = HealthStatus.UNHEALTHY
                service_health.message = f"Email service connection failed: {str(e)}"
                
        except Exception as e:
            service_health.status = HealthStatus.DEGRADED
            service_health.message = f"Email check error: {str(e)}"
    
    async def _check_websocket_health(self, service_health: ServiceHealth):
        """Check WebSocket service health"""
        from middleware.loading_states import loading_manager
        
        # Check active WebSocket connections
        active_operations = len([
            state for state in loading_manager.loading_states.values()
            if state.status == "in_progress"
        ])
        
        service_health.metrics["active_operations"] = HealthMetric(
            "Active Operations", active_operations, "count", HealthStatus.HEALTHY, 50, 100
        )
        
        service_health.message = f"WebSocket service healthy: {active_operations} active operations"
    
    async def _check_ml_service_health(self, service_health: ServiceHealth):
        """Check ML service health"""
        try:
            # Check if ML matching features are enabled
            ml_enabled = getattr(settings, 'ml_matching_enabled', True)
            if not ml_enabled:
                service_health.status = HealthStatus.DEGRADED
                service_health.message = "ML service disabled"
                return
            
            # Test ML service by trying to import required libraries
            try:
                import numpy
                import sklearn
                service_health.message = "ML service dependencies available"
            except ImportError as e:
                service_health.status = HealthStatus.DEGRADED
                service_health.message = f"ML service dependencies missing: {str(e)}"
            
        except Exception as e:
            service_health.status = HealthStatus.DEGRADED
            service_health.message = f"ML service check error: {str(e)}"
    
    async def _monitor_system_metrics(self):
        """Monitor system-level metrics"""
        while self.monitoring_active:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.system_metrics["cpu_usage"].update(cpu_percent)
                
                # Memory usage
                memory = psutil.virtual_memory()
                self.system_metrics["memory_usage"].update(memory.percent)
                
                # Disk usage
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                self.system_metrics["disk_usage"].update(disk_percent)
                
                # Update performance history
                self.performance_history["response_times"].append(
                    self.system_metrics["response_time"].value
                )
                
                await asyncio.sleep(60)  # Update every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error monitoring system metrics: {e}")
                await asyncio.sleep(60)
    
    async def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        # Determine overall status
        service_statuses = [service.status for service in self.services.values()]
        metric_statuses = [metric.status for metric in self.system_metrics.values()]
        all_statuses = service_statuses + metric_statuses
        
        if HealthStatus.CRITICAL in all_statuses:
            overall_status = HealthStatus.CRITICAL
        elif HealthStatus.UNHEALTHY in all_statuses:
            overall_status = HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in all_statuses:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY
        
        # Count services by status
        status_counts = {status: 0 for status in HealthStatus}
        for service in self.services.values():
            status_counts[service.status] += 1
        
        return {
            "overall_status": overall_status.value,
            "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
            "services": {
                service_type.value: service.to_dict()
                for service_type, service in self.services.items()
            },
            "system_metrics": {
                name: metric.to_dict()
                for name, metric in self.system_metrics.items()
            },
            "summary": {
                "total_services": len(self.services),
                "healthy_services": status_counts[HealthStatus.HEALTHY],
                "degraded_services": status_counts[HealthStatus.DEGRADED],
                "unhealthy_services": status_counts[HealthStatus.UNHEALTHY],
                "critical_services": status_counts[HealthStatus.CRITICAL]
            },
            "uptime": self._get_uptime(),
            "version": settings.api.version,
            "environment": settings.environment.value
        }
    
    def _get_uptime(self) -> Dict[str, Any]:
        """Get system uptime information"""
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            
            return {
                "seconds": int(uptime_seconds),
                "formatted": f"{days}d {hours}h {minutes}m",
                "boot_time": datetime.fromtimestamp(boot_time).isoformat()
            }
        except Exception:
            return {"seconds": 0, "formatted": "unknown", "boot_time": None}
    
    async def run_comprehensive_check(self, progress_tracker: ProgressTracker = None) -> Dict[str, Any]:
        """Run comprehensive health check with progress tracking"""
        if progress_tracker:
            progress_tracker.set_total_steps(len(self.services) + 1)
        
        results = {"services": {}, "system_metrics": {}, "issues": []}
        
        # Check each service
        for i, service_type in enumerate(self.services.keys(), 1):
            if progress_tracker:
                progress_tracker.update(i, f"Checking {service_type.value} service")
            
            try:
                await self._check_service_health(service_type)
                results["services"][service_type.value] = self.services[service_type].to_dict()
                
                # Track issues
                if self.services[service_type].status != HealthStatus.HEALTHY:
                    results["issues"].append({
                        "service": service_type.value,
                        "status": self.services[service_type].status.value,
                        "message": self.services[service_type].message
                    })
            
            except Exception as e:
                logger.error(f"Error checking {service_type.value}: {e}")
                results["issues"].append({
                    "service": service_type.value,
                    "status": "error",
                    "message": str(e)
                })
        
        # Update system metrics
        if progress_tracker:
            progress_tracker.update(len(self.services) + 1, "Collecting system metrics")
        
        await self._collect_system_metrics()
        results["system_metrics"] = {
            name: metric.to_dict() for name, metric in self.system_metrics.items()
        }
        
        # Add summary
        results["summary"] = {
            "total_checks": len(self.services),
            "healthy_services": len([s for s in self.services.values() if s.status == HealthStatus.HEALTHY]),
            "issues_found": len(results["issues"]),
            "check_completed_at": datetime.now(datetime.timezone.utc).isoformat()
        }
        
        return results
    
    async def _collect_system_metrics(self):
        """Collect current system metrics"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent()
            self.system_metrics["cpu_usage"].update(cpu_percent, f"CPU at {cpu_percent}%")
            
            # Memory
            memory = psutil.virtual_memory()
            self.system_metrics["memory_usage"].update(
                memory.percent, f"Memory at {memory.percent}% ({memory.used / 1024**3:.1f}GB used)"
            )
            
            # Disk
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.system_metrics["disk_usage"].update(
                disk_percent, f"Disk at {disk_percent}% ({disk.free / 1024**3:.1f}GB free)"
            )
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")


# Global health checker instance
health_checker = HealthChecker()