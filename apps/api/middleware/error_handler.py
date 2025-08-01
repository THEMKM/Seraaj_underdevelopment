"""
Advanced Error Handling Middleware for Seraaj API
Provides comprehensive error handling, logging, and user-friendly responses
"""

import traceback
import uuid
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError
import logging

# Configure logger
logger = logging.getLogger(__name__)


class SeraajError(Exception):
    """Base exception class for Seraaj-specific errors"""

    def __init__(
        self,
        message: str,
        error_code: str = None,
        details: Dict[str, Any] = None,
        status_code: int = 500,
    ):
        self.message = message
        self.error_code = error_code or "SERAAJ_ERROR"
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)


class BusinessLogicError(SeraajError):
    """Business logic validation errors"""

    def __init__(
        self, message: str, error_code: str = None, details: Dict[str, Any] = None
    ):
        super().__init__(message, error_code or "BUSINESS_LOGIC_ERROR", details, 400)


class ResourceNotFoundError(SeraajError):
    """Resource not found errors"""

    def __init__(
        self, message: str, resource_type: str = None, resource_id: str = None
    ):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id

        super().__init__(message, "RESOURCE_NOT_FOUND", details, 404)


class AuthenticationError(SeraajError):
    """Authentication related errors"""

    def __init__(
        self, message: str = "Authentication failed", details: Dict[str, Any] = None
    ):
        super().__init__(message, "AUTHENTICATION_ERROR", details, 401)


class AuthorizationError(SeraajError):
    """Authorization related errors"""

    def __init__(self, message: str = "Access denied", details: Dict[str, Any] = None):
        super().__init__(message, "AUTHORIZATION_ERROR", details, 403)


class RateLimitError(SeraajError):
    """Rate limiting errors"""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(message, "RATE_LIMIT_ERROR", details, 429)


class ExternalServiceError(SeraajError):
    """External service integration errors"""

    def __init__(self, message: str, service: str, details: Dict[str, Any] = None):
        error_details = {"service": service}
        if details:
            error_details.update(details)
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", error_details, 502)


class PaymentError(SeraajError):
    """Payment processing errors"""

    def __init__(
        self,
        message: str = "Payment processing failed",
        payment_id: str = None,
        details: Dict[str, Any] = None,
    ):
        error_details = details or {}
        if payment_id:
            error_details["payment_id"] = payment_id

        super().__init__(message, "PAYMENT_ERROR", error_details, 400)


class DataValidationError(SeraajError):
    """Data validation errors"""

    def __init__(self, message: str, field: str = None, value: Any = None):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        super().__init__(message, "DATA_VALIDATION_ERROR", details, 422)


class ErrorHandler:
    """Centralized error handling with logging and user-friendly responses"""

    def __init__(self):
        self.error_mappings = {
            # HTTP Exceptions
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            409: "Conflict",
            422: "Validation Error",
            429: "Too Many Requests",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable",
        }

    async def handle_error(
        self, request: Request, error: Exception, error_id: str = None
    ) -> JSONResponse:
        """Main error handling method"""

        if not error_id:
            error_id = str(uuid.uuid4())

        # Log the error
        await self._log_error(request, error, error_id)

        # Handle different error types
        if isinstance(error, SeraajError):
            return await self._handle_seraaj_error(error, error_id)
        elif isinstance(error, RequestValidationError):
            return await self._handle_validation_error(error, error_id)
        elif isinstance(error, HTTPException):
            return await self._handle_http_exception(error, error_id)
        elif isinstance(error, StarletteHTTPException):
            return await self._handle_starlette_exception(error, error_id)
        elif isinstance(error, SQLAlchemyError):
            return await self._handle_database_error(error, error_id)
        elif isinstance(error, ValidationError):
            return await self._handle_pydantic_error(error, error_id)
        else:
            return await self._handle_generic_error(error, error_id)

    async def _handle_seraaj_error(
        self, error: SeraajError, error_id: str
    ) -> JSONResponse:
        """Handle custom Seraaj errors"""

        response_data = {
            "error": True,
            "error_id": error_id,
            "error_code": error.error_code,
            "message": error.message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": error.details,
        }

        # Add retry information for rate limit errors
        headers = {}
        if isinstance(error, RateLimitError) and error.details.get("retry_after"):
            headers["Retry-After"] = str(error.details["retry_after"])

        return JSONResponse(
            status_code=error.status_code, content=response_data, headers=headers
        )

    async def _handle_validation_error(
        self, error: RequestValidationError, error_id: str
    ) -> JSONResponse:
        """Handle FastAPI validation errors"""

        validation_errors = []
        for err in error.errors():
            validation_errors.append(
                {
                    "field": " -> ".join(str(x) for x in err["loc"]),
                    "message": err["msg"],
                    "type": err["type"],
                    "input": err.get("input"),
                }
            )

        response_data = {
            "error": True,
            "error_id": error_id,
            "error_code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": {
                "validation_errors": validation_errors,
                "error_count": len(validation_errors),
            },
        }

        return JSONResponse(status_code=422, content=response_data)

    async def _handle_http_exception(
        self, error: HTTPException, error_id: str
    ) -> JSONResponse:
        """Handle FastAPI HTTP exceptions"""

        response_data = {
            "error": True,
            "error_id": error_id,
            "error_code": f"HTTP_{error.status_code}",
            "message": (
                error.detail
                if error.detail
                else self.error_mappings.get(error.status_code, "HTTP Error")
            ),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": {},
        }

        return JSONResponse(
            status_code=error.status_code, content=response_data, headers=error.headers
        )

    async def _handle_starlette_exception(
        self, error: StarletteHTTPException, error_id: str
    ) -> JSONResponse:
        """Handle Starlette HTTP exceptions"""

        response_data = {
            "error": True,
            "error_id": error_id,
            "error_code": f"HTTP_{error.status_code}",
            "message": (
                error.detail
                if hasattr(error, "detail")
                else self.error_mappings.get(error.status_code, "HTTP Error")
            ),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": {},
        }

        return JSONResponse(status_code=error.status_code, content=response_data)

    async def _handle_database_error(
        self, error: SQLAlchemyError, error_id: str
    ) -> JSONResponse:
        """Handle SQLAlchemy database errors"""

        if isinstance(error, IntegrityError):
            # Handle database constraint violations
            message = "Data integrity constraint violation"
            error_code = "INTEGRITY_ERROR"
            status_code = 409

            # Try to extract meaningful information from the error
            error_str = str(error.orig) if hasattr(error, "orig") else str(error)
            details = {"database_error": error_str}

            # Common integrity error patterns
            if "UNIQUE constraint failed" in error_str:
                message = "A record with this information already exists"
            elif "FOREIGN KEY constraint failed" in error_str:
                message = "Referenced record does not exist"
            elif "NOT NULL constraint failed" in error_str:
                message = "Required field is missing"

        else:
            message = "Database operation failed"
            error_code = "DATABASE_ERROR"
            status_code = 500
            details = {"error_type": type(error).__name__}

        response_data = {
            "error": True,
            "error_id": error_id,
            "error_code": error_code,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details,
        }

        return JSONResponse(status_code=status_code, content=response_data)

    async def _handle_pydantic_error(
        self, error: ValidationError, error_id: str
    ) -> JSONResponse:
        """Handle Pydantic validation errors"""

        validation_errors = []
        for err in error.errors():
            validation_errors.append(
                {
                    "field": " -> ".join(str(x) for x in err["loc"]),
                    "message": err["msg"],
                    "type": err["type"],
                }
            )

        response_data = {
            "error": True,
            "error_id": error_id,
            "error_code": "PYDANTIC_VALIDATION_ERROR",
            "message": "Data validation failed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": {
                "validation_errors": validation_errors,
                "error_count": len(validation_errors),
            },
        }

        return JSONResponse(status_code=422, content=response_data)

    async def _handle_generic_error(
        self, error: Exception, error_id: str
    ) -> JSONResponse:
        """Handle unexpected errors"""

        response_data = {
            "error": True,
            "error_id": error_id,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Please try again later.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": {"error_type": type(error).__name__},
        }

        return JSONResponse(status_code=500, content=response_data)

    async def _log_error(self, request: Request, error: Exception, error_id: str):
        """Log error details for debugging and monitoring"""

        # Extract request information
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        method = request.method
        url = str(request.url)

        # Get user information if available
        user_id = getattr(request.state, "user_id", None)
        user_role = getattr(request.state, "user_role", None)

        # Create log context
        log_context = {
            "error_id": error_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "request_method": method,
            "request_url": url,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "user_id": user_id,
            "user_role": user_role,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Log based on error severity
        if isinstance(error, (SeraajError, HTTPException, RequestValidationError)):
            if hasattr(error, "status_code") and error.status_code < 500:
                # Client errors - log as warning
                logger.warning(f"Client error [{error_id}]: {error}", extra=log_context)
            else:
                # Server errors - log as error
                logger.error(f"Server error [{error_id}]: {error}", extra=log_context)
        else:
            # Unexpected errors - log as critical with full traceback
            logger.critical(
                f"Unexpected error [{error_id}]: {error}\n{traceback.format_exc()}",
                extra=log_context,
            )


# Global error handler instance
error_handler = ErrorHandler()


# Middleware function
async def error_handling_middleware(request: Request, call_next):
    """Error handling middleware"""
    try:
        response = await call_next(request)
        return response
    except Exception as error:
        return await error_handler.handle_error(request, error)


# Helper functions for common error scenarios
def raise_not_found(
    message: str = "Resource not found",
    resource_type: str = None,
    resource_id: str = None,
):
    """Raise a standardized not found error"""
    raise ResourceNotFoundError(message, resource_type, resource_id)


def raise_forbidden(message: str = "Access denied", details: Dict[str, Any] = None):
    """Raise a standardized forbidden error"""
    raise AuthorizationError(message, details)


def raise_bad_request(message: str, details: Dict[str, Any] = None):
    """Raise a standardized bad request error"""
    raise BusinessLogicError(message, "BAD_REQUEST", details)


def raise_validation_error(message: str, field: str = None, value: Any = None):
    """Raise a standardized validation error"""
    raise DataValidationError(message, field, value)


def raise_conflict(message: str = "Resource conflict", details: Dict[str, Any] = None):
    """Raise a standardized conflict error"""
    raise BusinessLogicError(message, "CONFLICT", details)


def raise_rate_limit(message: str = "Rate limit exceeded", retry_after: int = None):
    """Raise a standardized rate limit error"""
    raise RateLimitError(message, retry_after)


def raise_external_service_error(
    message: str, service: str, details: Dict[str, Any] = None
):
    """Raise a standardized external service error"""
    raise ExternalServiceError(message, service, details)
