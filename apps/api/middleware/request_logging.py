"""
Request/Response Logging Middleware for Seraaj API
Provides comprehensive logging of API requests and responses for debugging and monitoring
"""

import time
import json
import uuid
from datetime import datetime
from typing import Dict, Any
from fastapi import Request
from starlette.types import ASGIApp, Receive, Scope, Send
import logging

# Configure logger for request/response logging
logger = logging.getLogger("seraaj.requests")


class RequestLoggingMiddleware:
    """ASGI Middleware for logging API requests and responses"""

    def __init__(
        self, app: ASGIApp, log_level: str = "INFO", exclude_paths: list = None
    ):
        self.app = app
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.exclude_paths = exclude_paths or [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """ASGI callable"""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)

        # Skip logging for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            await self.app(scope, receive, send)
            return

        # Generate request ID for correlation
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Start timing
        start_time = time.time()

        # Log request
        await self._log_request(request, request_id)

        # Create response wrapper to capture response data
        response_data = {"status_code": 200, "headers": {}}

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                response_data["status_code"] = message["status"]
                response_data["headers"] = dict(message["headers"])
                # Add request ID to response headers
                message["headers"].append((b"x-request-id", request_id.encode()))
                message["headers"].append(
                    (b"x-process-time", f"{time.time() - start_time:.4f}".encode())
                )
            await send(message)

        # Process request
        await self.app(scope, receive, send_wrapper)

        # Calculate processing time and log response
        process_time = time.time() - start_time
        await self._log_response(request, response_data, request_id, process_time)

    async def _log_request_old_method(self, request: Request, call_next):
        """Legacy method kept for backward compatibility - not used in ASGI version"""
        pass

    async def _log_request(self, request: Request, request_id: str):
        """Log incoming request details"""

        # Extract request information
        method = request.method
        url = str(request.url)
        path = request.url.path
        query_params = dict(request.query_params)
        headers = dict(request.headers)
        client_ip = request.client.host if request.client else "unknown"
        user_agent = headers.get("user-agent", "unknown")

        # Get user information if available from auth middleware
        user_id = getattr(request.state, "user_id", None)
        user_role = getattr(request.state, "user_role", None)

        # Try to read request body (for POST/PUT requests)
        request_body = None
        if method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    # Try to parse as JSON, fallback to string
                    try:
                        request_body = json.loads(body.decode())
                        # Remove sensitive fields
                        request_body = self._sanitize_data(request_body)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        request_body = f"<binary data: {len(body)} bytes>"
            except Exception:
                request_body = "<failed to read body>"

        # Create log entry
        log_data = {
            "type": "request",
            "request_id": request_id,
            "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
            "method": method,
            "path": path,
            "url": url,
            "query_params": query_params,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "user_id": user_id,
            "user_role": user_role,
            "content_type": headers.get("content-type"),
            "content_length": headers.get("content-length"),
            "request_body": request_body,
        }

        # Log the request
        logger.log(
            self.log_level,
            f"REQUEST [{request_id}] {method} {path}",
            extra={"request_data": log_data},
        )

    async def _log_response(
        self,
        request: Request,
        response_data: Dict[str, Any],
        request_id: str,
        process_time: float,
    ):
        """Log outgoing response details"""

        # Extract response information
        status_code = response_data["status_code"]
        headers = response_data["headers"]

        # For ASGI middleware, we can't easily read response body without consuming it
        # So we'll log the content type and size instead
        content_type = headers.get(b"content-type", b"unknown").decode("latin-1")
        content_length = headers.get(b"content-length", b"unknown").decode("latin-1")
        response_body = f"<{content_type}:{content_length} bytes>"

        # Create log entry
        log_data = {
            "type": "response",
            "request_id": request_id,
            "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
            "method": request.method,
            "path": request.url.path,
            "status_code": status_code,
            "process_time": round(process_time, 4),
            "content_type": headers.get("content-type"),
            "content_length": headers.get("content-length"),
            "response_body": response_body,
        }

        # Determine log level based on status code
        if status_code >= 500:
            log_level = logging.ERROR
        elif status_code >= 400:
            log_level = logging.WARNING
        elif process_time > 2.0:  # Slow response
            log_level = logging.WARNING
        else:
            log_level = self.log_level

        # Log the response
        logger.log(
            log_level,
            f"RESPONSE [{request_id}] {status_code} {request.method} {request.url.path} ({process_time:.4f}s)",
            extra={"response_data": log_data},
        )

    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from request data"""

        sensitive_fields = [
            "password",
            "token",
            "secret",
            "key",
            "auth",
            "authorization",
            "cookie",
            "session",
            "csrf",
            "api_key",
            "access_token",
            "refresh_token",
        ]

        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in sensitive_fields):
                    sanitized[key] = "<redacted>"
                elif isinstance(value, dict):
                    sanitized[key] = self._sanitize_data(value)
                elif isinstance(value, list):
                    sanitized[key] = [
                        self._sanitize_data(item) if isinstance(item, dict) else item
                        for item in value
                    ]
                else:
                    sanitized[key] = value
            return sanitized

        return data


class APIMetricsMiddleware:
    """ASGI Middleware for collecting API metrics"""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """ASGI callable"""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        start_time = time.time()

        # Create response wrapper to capture response data
        response_data = {"status_code": 200}

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                response_data["status_code"] = message["status"]
            await send(message)

        # Process request
        await self.app(scope, receive, send_wrapper)

        # Calculate processing time and update metrics
        process_time = time.time() - start_time
        self._update_metrics(request, response_data, process_time)

    def _update_metrics(
        self, request: Request, response_data: Dict[str, Any], process_time: float
    ):
        """Update API metrics"""

        method = request.method
        path = request.url.path
        status_code = response_data["status_code"]

        # Update global counters
        _global_metrics["total_requests"] += 1

        # By method
        _global_metrics["requests_by_method"][method] = (
            _global_metrics["requests_by_method"].get(method, 0) + 1
        )

        # By status code
        status_range = f"{status_code // 100}xx"
        _global_metrics["requests_by_status"][status_range] = (
            _global_metrics["requests_by_status"].get(status_range, 0) + 1
        )

        # By path (group similar paths)
        normalized_path = self._normalize_path(path)
        _global_metrics["requests_by_path"][normalized_path] = (
            _global_metrics["requests_by_path"].get(normalized_path, 0) + 1
        )

        # Slow requests
        if process_time > 2.0:
            _global_metrics["slow_requests"] += 1

        # Error requests
        if status_code >= 400:
            _global_metrics["error_requests"] += 1

    def _normalize_path(self, path: str) -> str:
        """Normalize paths for metrics grouping"""

        # Replace IDs with placeholders
        import re

        # Replace numeric IDs
        path = re.sub(r"/\d+", "/{id}", path)
        # Replace UUIDs
        path = re.sub(
            r"/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            "/{uuid}",
            path,
        )

        return path

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return _global_metrics.copy()


# Global metrics storage
_global_metrics = {
    "total_requests": 0,
    "requests_by_method": {},
    "requests_by_status": {},
    "requests_by_path": {},
    "slow_requests": 0,
    "error_requests": 0,
}


def get_api_metrics() -> Dict[str, Any]:
    """Get current API metrics"""
    return _global_metrics.copy()
