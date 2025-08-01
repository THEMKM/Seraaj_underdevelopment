"""
Response formatting utilities for consistent API responses
"""

from typing import Any, Dict, List
from datetime import datetime
from fastapi.responses import JSONResponse
from middleware.loading_states import LoadingState
from config.settings import settings


class APIResponse:
    """Standardized API response formatter"""

    @staticmethod
    def success(
        data: Any = None,
        message: str = "Operation completed successfully",
        status_code: int = 200,
        metadata: Dict[str, Any] = None,
    ) -> JSONResponse:
        """Create a successful response"""

        response_data = {
            "success": True,
            "message": message,
            "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
            "data": data,
        }

        if metadata:
            response_data["metadata"] = metadata

        return JSONResponse(status_code=status_code, content=response_data)

    @staticmethod
    def created(
        data: Any, message: str = "Resource created successfully", location: str = None
    ) -> JSONResponse:
        """Create a 201 Created response"""

        headers = {}
        if location:
            headers["Location"] = location

        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "message": message,
                "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
                "data": data,
            },
            headers=headers,
        )

    @staticmethod
    def accepted(
        operation_id: str,
        operation_type: str,
        message: str = "Operation accepted and is being processed",
        progress_url: str = None,
    ) -> JSONResponse:
        """Create a 202 Accepted response for async operations"""

        response_data = {
            "success": True,
            "message": message,
            "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
            "operation": {
                "operation_id": operation_id,
                "operation_type": operation_type,
                "status": "accepted",
                "progress_url": progress_url or f"/v1/operations/{operation_id}/status",
            },
        }

        return JSONResponse(
            status_code=202,
            content=response_data,
            headers={
                "X-Operation-ID": operation_id,
                "X-Operation-Type": operation_type,
            },
        )

    @staticmethod
    def paginated(
        data: List[Any],
        total_count: int,
        page: int = 1,
        page_size: int = 20,
        message: str = "Data retrieved successfully",
    ) -> JSONResponse:
        """Create a paginated response"""

        total_pages = (total_count + page_size - 1) // page_size
        has_next = page < total_pages
        has_previous = page > 1

        response_data = {
            "success": True,
            "message": message,
            "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
            "data": data,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_previous": has_previous,
                "next_page": page + 1 if has_next else None,
                "previous_page": page - 1 if has_previous else None,
            },
        }

        return JSONResponse(status_code=200, content=response_data)

    @staticmethod
    def no_content(message: str = "Operation completed successfully") -> JSONResponse:
        """Create a 204 No Content response"""

        return JSONResponse(
            status_code=204, content=None, headers={"X-Message": message}
        )

    @staticmethod
    def loading(
        loading_state: LoadingState, message: str = "Operation in progress"
    ) -> JSONResponse:
        """Create a loading response with progress information"""

        response_data = {
            "success": True,
            "message": message,
            "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
            "loading": True,
            "progress": loading_state.to_dict(),
            "endpoints": {
                "status": f"/v1/operations/{loading_state.operation_id}/status",
                "stream": f"/v1/operations/{loading_state.operation_id}/stream",
                "cancel": f"/v1/operations/{loading_state.operation_id}/cancel",
            },
        }

        return JSONResponse(
            status_code=202,
            content=response_data,
            headers={"X-Operation-ID": loading_state.operation_id, "X-Loading": "true"},
        )


class ValidationErrorFormatter:
    """Format validation errors consistently"""

    @staticmethod
    def format_validation_errors(
        errors: List[Dict[str, Any]], message: str = "Validation failed"
    ) -> Dict[str, Any]:
        """Format validation errors for API response"""

        formatted_errors = []
        field_errors = {}

        for error in errors:
            field = error.get("field", "unknown")
            error_message = error.get("message", "Invalid value")
            value = error.get("value")

            formatted_error = {
                "field": field,
                "message": error_message,
                "code": error.get("code", "VALIDATION_ERROR"),
            }

            if value is not None:
                formatted_error["rejected_value"] = str(value)

            formatted_errors.append(formatted_error)

            # Group by field for easier frontend handling
            if field not in field_errors:
                field_errors[field] = []
            field_errors[field].append(error_message)

        return {
            "error": True,
            "message": message,
            "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
            "validation_errors": formatted_errors,
            "field_errors": field_errors,
            "error_count": len(formatted_errors),
        }


class MetricsCollector:
    """Collect metrics for API responses"""

    @staticmethod
    def add_performance_metrics(
        response_data: Dict[str, Any],
        start_time: float,
        database_query_count: int = 0,
        cache_hits: int = 0,
    ) -> Dict[str, Any]:
        """Add performance metrics to response"""

        import time

        processing_time = time.time() - start_time

        response_data["performance"] = {
            "processing_time_ms": round(processing_time * 1000, 2),
            "database_queries": database_query_count,
            "cache_hits": cache_hits,
            "cache_hit_rate": (
                round(cache_hits / max(database_query_count, 1) * 100, 2)
                if database_query_count > 0
                else 0
            ),
        }

        return response_data

    @staticmethod
    def add_api_version_info(response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add API version information"""

        response_data["api_info"] = {
            "version": "2.0.0",
            "build": "production",
            "environment": settings.environment.value,
            "documentation": settings.api.docs_url,
        }

        return response_data


class ResponseHeaders:
    """Standard response headers"""

    @staticmethod
    def get_standard_headers() -> Dict[str, str]:
        """Get standard headers for all responses"""

        return {
            "X-API-Version": "2.0.0",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }

    @staticmethod
    def get_cors_headers() -> Dict[str, str]:
        """Get CORS headers"""

        return {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            "Access-Control-Max-Age": "86400",
        }

    @staticmethod
    def get_rate_limit_headers(
        limit: int, remaining: int, reset_time: int
    ) -> Dict[str, str]:
        """Get rate limiting headers"""

        return {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_time),
        }


# Helper functions for common response patterns
def success_with_data(data: Any, message: str = None) -> JSONResponse:
    """Quick success response with data"""
    return APIResponse.success(data, message or "Operation completed successfully")


def created_resource(
    data: Any, resource_type: str, resource_id: str = None
) -> JSONResponse:
    """Quick created response for new resources"""
    location = None
    if resource_id:
        location = f"/v1/{resource_type.lower()}s/{resource_id}"

    return APIResponse.created(
        data, f"{resource_type.title()} created successfully", location
    )


def paginated_results(
    data: List[Any], total_count: int, page: int = 1, page_size: int = 20
) -> JSONResponse:
    """Quick paginated response"""
    return APIResponse.paginated(data, total_count, page, page_size)


def async_operation_started(
    operation_id: str, operation_type: str, description: str = None
) -> JSONResponse:
    """Quick async operation response"""
    message = description or f"{operation_type.replace('_', ' ').title()} started"
    return APIResponse.accepted(operation_id, operation_type, message)


# Response decorators
def format_api_response(func):
    """Decorator to automatically format API responses"""

    async def wrapper(*args, **kwargs):
        import time

        start_time = time.time()

        try:
            result = await func(*args, **kwargs)

            # If result is already a JSONResponse, return as is
            if isinstance(result, JSONResponse):
                return result

            # Otherwise, wrap in success response
            return APIResponse.success(result)

        except Exception as e:
            # Let the error handler deal with exceptions
            raise e

    return wrapper


def add_performance_headers(func):
    """Decorator to add performance headers to responses"""

    async def wrapper(*args, **kwargs):
        import time

        start_time = time.time()

        response = await func(*args, **kwargs)

        # Add performance headers
        processing_time = time.time() - start_time
        response.headers["X-Processing-Time"] = f"{processing_time:.3f}s"
        response.headers["X-Timestamp"] = datetime.now(
            datetime.timezone.utc
        ).isoformat()

        return response

    return wrapper


def error_response(
    message: str = "An error occurred",
    status_code: int = 500,
    error_code: str = None,
    details: Any = None,
) -> JSONResponse:
    """Quick error response"""
    response_data = {
        "success": False,
        "error": True,
        "message": message,
        "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
    }

    if error_code:
        response_data["error_code"] = error_code

    if details:
        response_data["details"] = details

    return JSONResponse(status_code=status_code, content=response_data)
