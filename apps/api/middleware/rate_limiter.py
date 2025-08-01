"""
Advanced Rate Limiting Middleware for Seraaj API
Provides sophisticated rate limiting with different strategies and user-based limits
"""

import time
from typing import Dict, Any, Optional
from collections import defaultdict, deque
from datetime import datetime
from fastapi import Request
from fastapi.responses import JSONResponse
import logging
import json
import hashlib


logger = logging.getLogger(__name__)


class RateLimitStrategy:
    """Base class for rate limiting strategies"""

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds

    async def is_allowed(self, key: str) -> tuple[bool, Dict[str, Any]]:
        """Check if request is allowed, return (allowed, metadata)"""
        raise NotImplementedError

    def get_reset_time(self, key: str) -> int:
        """Get reset time for the rate limit window"""
        raise NotImplementedError


class TokenBucketStrategy(RateLimitStrategy):
    """Token bucket rate limiting strategy"""

    def __init__(
        self, limit: int, window_seconds: int, refill_rate: Optional[int] = None
    ):
        super().__init__(limit, window_seconds)
        self.refill_rate = refill_rate or limit  # Tokens per window
        self.buckets: Dict[str, Dict[str, Any]] = {}
        self.cleanup_interval = 3600  # Clean up old buckets every hour
        self.last_cleanup = time.time()

    async def is_allowed(self, key: str) -> tuple[bool, Dict[str, Any]]:
        """Check if request is allowed using token bucket algorithm"""
        current_time = time.time()

        # Clean up old buckets periodically
        if current_time - self.last_cleanup > self.cleanup_interval:
            await self._cleanup_old_buckets(current_time)

        # Get or create bucket for this key
        if key not in self.buckets:
            self.buckets[key] = {
                "tokens": self.limit,
                "last_refill": current_time,
                "created_at": current_time,
            }

        bucket = self.buckets[key]

        # Calculate tokens to add based on time elapsed
        time_elapsed = current_time - bucket["last_refill"]
        tokens_to_add = (time_elapsed / self.window_seconds) * self.refill_rate

        # Update bucket
        bucket["tokens"] = min(self.limit, bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = current_time

        # Check if request is allowed
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            allowed = True
        else:
            allowed = False

        metadata = {
            "remaining": int(bucket["tokens"]),
            "limit": self.limit,
            "reset_time": int(current_time + self.window_seconds),
            "retry_after": (
                int(
                    self.window_seconds
                    - (bucket["tokens"] * self.window_seconds / self.refill_rate)
                )
                if not allowed
                else 0
            ),
        }

        return allowed, metadata

    def get_reset_time(self, key: str) -> int:
        """Get reset time for the rate limit window"""
        if key in self.buckets:
            return int(self.buckets[key]["last_refill"] + self.window_seconds)
        return int(time.time() + self.window_seconds)

    async def _cleanup_old_buckets(self, current_time: float):
        """Clean up buckets that haven't been used recently"""
        cutoff_time = current_time - (self.cleanup_interval * 2)
        keys_to_remove = [
            key
            for key, bucket in self.buckets.items()
            if bucket["created_at"] < cutoff_time
        ]

        for key in keys_to_remove:
            del self.buckets[key]

        self.last_cleanup = current_time

        if keys_to_remove:
            logger.info(f"Cleaned up {len(keys_to_remove)} old rate limit buckets")


class SlidingWindowStrategy(RateLimitStrategy):
    """Sliding window rate limiting strategy"""

    def __init__(self, limit: int, window_seconds: int):
        super().__init__(limit, window_seconds)
        self.windows: Dict[str, deque] = defaultdict(deque)
        self.cleanup_interval = 3600
        self.last_cleanup = time.time()

    async def is_allowed(self, key: str) -> tuple[bool, Dict[str, Any]]:
        """Check if request is allowed using sliding window algorithm"""
        current_time = time.time()
        window_start = current_time - self.window_seconds

        # Clean up old windows periodically
        if current_time - self.last_cleanup > self.cleanup_interval:
            await self._cleanup_old_windows()

        # Get window for this key
        window = self.windows[key]

        # Remove old entries from the window
        while window and window[0] <= window_start:
            window.popleft()

        # Check if request is allowed
        if len(window) < self.limit:
            window.append(current_time)
            allowed = True
            remaining = self.limit - len(window)
        else:
            allowed = False
            remaining = 0

        # Calculate reset time (when the oldest entry expires)
        reset_time = (
            int(window[0] + self.window_seconds)
            if window
            else int(current_time + self.window_seconds)
        )

        metadata = {
            "remaining": remaining,
            "limit": self.limit,
            "reset_time": reset_time,
            "retry_after": int(reset_time - current_time) if not allowed else 0,
        }

        return allowed, metadata

    def get_reset_time(self, key: str) -> int:
        """Get reset time for the rate limit window"""
        window = self.windows[key]
        if window:
            return int(window[0] + self.window_seconds)
        return int(time.time() + self.window_seconds)

    async def _cleanup_old_windows(self):
        """Clean up empty windows"""
        current_time = time.time()
        window_start = current_time - self.window_seconds

        keys_to_remove = []
        for key, window in self.windows.items():
            # Remove old entries
            while window and window[0] <= window_start:
                window.popleft()

            # Mark empty windows for removal
            if not window:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.windows[key]

        self.last_cleanup = current_time

        if keys_to_remove:
            logger.info(f"Cleaned up {len(keys_to_remove)} empty sliding windows")


class AdaptiveRateLimiter:
    """Adaptive rate limiter that adjusts limits based on system load and user behavior"""

    def __init__(self):
        self.base_limits = {
            # Endpoint-specific limits (requests per minute)
            "auth_login": {"limit": 5, "window": 60, "strategy": "sliding_window"},
            "auth_register": {"limit": 3, "window": 60, "strategy": "sliding_window"},
            "file_upload": {"limit": 10, "window": 60, "strategy": "token_bucket"},
            "api_general": {"limit": 100, "window": 60, "strategy": "token_bucket"},
            "search": {"limit": 50, "window": 60, "strategy": "sliding_window"},
            "websocket": {"limit": 1000, "window": 60, "strategy": "token_bucket"},
        }

        # User role-based multipliers
        self.role_multipliers = {"volunteer": 1.0, "organization": 1.5, "admin": 5.0}

        # Premium user multipliers
        self.premium_multipliers = {"basic": 1.0, "premium": 2.0, "enterprise": 5.0}

        # Strategy instances
        self.strategies: Dict[str, Dict[str, RateLimitStrategy]] = {}
        self._initialize_strategies()

        # System load monitoring
        self.system_load_factor = 1.0
        self.last_load_check = time.time()

        # Suspicious activity detection
        self.suspicious_patterns = {}
        self.blocked_ips = {}

    def _initialize_strategies(self):
        """Initialize rate limiting strategies"""
        for endpoint, config in self.base_limits.items():
            self.strategies[endpoint] = {}

            if config["strategy"] == "token_bucket":
                self.strategies[endpoint]["default"] = TokenBucketStrategy(
                    config["limit"], config["window"]
                )
            elif config["strategy"] == "sliding_window":
                self.strategies[endpoint]["default"] = SlidingWindowStrategy(
                    config["limit"], config["window"]
                )

    async def check_rate_limit(
        self,
        request: Request,
        endpoint_type: str = "api_general",
        user_id: Optional[int] = None,
        user_role: Optional[str] = None,
    ) -> tuple[bool, Dict[str, Any]]:
        """Check if request should be rate limited"""

        # Get client identifier
        client_key = self._get_client_key(request, user_id)

        # Check if IP is blocked
        client_ip = self._get_client_ip(request)
        if await self._is_ip_blocked(client_ip):
            return False, {
                "limit": 0,
                "remaining": 0,
                "reset_time": int(time.time() + 3600),
                "retry_after": 3600,
                "reason": "ip_blocked",
            }

        # Detect suspicious patterns
        await self._detect_suspicious_activity(request, client_ip, endpoint_type)

        # Calculate effective limits
        effective_limit = await self._calculate_effective_limit(
            endpoint_type, user_role, user_id
        )

        # Get appropriate strategy
        strategy = self._get_strategy(endpoint_type, effective_limit)

        # Check rate limit
        allowed, metadata = await strategy.is_allowed(client_key)

        # Log rate limit events
        if not allowed:
            await self._log_rate_limit_event(
                request, client_key, endpoint_type, metadata
            )

        return allowed, metadata

    def _get_client_key(self, request: Request, user_id: Optional[int] = None) -> str:
        """Generate unique client key for rate limiting"""
        if user_id:
            return f"user_{user_id}"

        # Fallback to IP-based limiting
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")

        # Create fingerprint from IP and User-Agent
        fingerprint = hashlib.md5(f"{client_ip}_{user_agent}".encode()).hexdigest()[:12]
        return f"anon_{fingerprint}"

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded headers (when behind proxy)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback to direct connection
        return request.client.host if request.client else "unknown"

    async def _calculate_effective_limit(
        self,
        endpoint_type: str,
        user_role: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Calculate effective rate limit based on user and system factors"""

        base_config = self.base_limits.get(
            endpoint_type, self.base_limits["api_general"]
        )
        base_limit = base_config["limit"]

        # Apply role multiplier
        role_multiplier = (
            self.role_multipliers.get(user_role, 1.0) if user_role else 0.5
        )

        # Apply premium multiplier (this would come from user profile)
        premium_multiplier = 1.0  # Would be determined from user subscription

        # Apply system load factor
        await self._update_system_load()

        # Calculate final limit
        effective_limit = int(
            base_limit * role_multiplier * premium_multiplier * self.system_load_factor
        )

        return {
            "limit": max(effective_limit, 1),  # Ensure at least 1 request
            "window": base_config["window"],
            "strategy": base_config["strategy"],
        }

    def _get_strategy(
        self, endpoint_type: str, effective_config: Dict[str, Any]
    ) -> RateLimitStrategy:
        """Get or create rate limiting strategy"""

        strategy_key = f"{effective_config['limit']}_{effective_config['window']}"

        if endpoint_type not in self.strategies:
            self.strategies[endpoint_type] = {}

        if strategy_key not in self.strategies[endpoint_type]:
            if effective_config["strategy"] == "token_bucket":
                self.strategies[endpoint_type][strategy_key] = TokenBucketStrategy(
                    effective_config["limit"], effective_config["window"]
                )
            else:
                self.strategies[endpoint_type][strategy_key] = SlidingWindowStrategy(
                    effective_config["limit"], effective_config["window"]
                )

        return self.strategies[endpoint_type][strategy_key]

    async def _update_system_load(self):
        """Update system load factor"""
        current_time = time.time()

        # Check system load every 30 seconds
        if current_time - self.last_load_check < 30:
            return

        try:
            import psutil

            # Get system metrics
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent

            # Calculate load factor (reduce limits when system is under stress)
            if cpu_percent > 80 or memory_percent > 85:
                self.system_load_factor = 0.5  # Reduce limits by 50%
            elif cpu_percent > 60 or memory_percent > 70:
                self.system_load_factor = 0.75  # Reduce limits by 25%
            else:
                self.system_load_factor = 1.0  # Normal limits

            self.last_load_check = current_time

            if self.system_load_factor < 1.0:
                logger.warning(
                    f"System under load - CPU: {cpu_percent}%, Memory: {memory_percent}%, "
                    f"Rate limits reduced to {self.system_load_factor * 100}%"
                )

        except Exception as e:
            logger.error(f"Error checking system load: {e}")
            self.system_load_factor = 1.0

    async def _detect_suspicious_activity(
        self, request: Request, client_ip: str, endpoint_type: str
    ):
        """Detect and handle suspicious activity patterns"""

        current_time = time.time()

        # Initialize tracking for this IP
        if client_ip not in self.suspicious_patterns:
            self.suspicious_patterns[client_ip] = {
                "requests": deque(),
                "failed_attempts": 0,
                "endpoints": defaultdict(int),
                "first_seen": current_time,
            }

        pattern = self.suspicious_patterns[client_ip]

        # Track request
        pattern["requests"].append(current_time)
        pattern["endpoints"][endpoint_type] += 1

        # Remove old requests (older than 5 minutes)
        cutoff_time = current_time - 300
        while pattern["requests"] and pattern["requests"][0] < cutoff_time:
            pattern["requests"].popleft()

        # Check for suspicious patterns
        requests_per_minute = len(pattern["requests"]) / 5  # 5-minute window

        # Pattern 1: Too many requests per minute
        if requests_per_minute > 100:
            await self._handle_suspicious_activity(
                client_ip,
                "high_frequency",
                {"requests_per_minute": requests_per_minute},
            )

        # Pattern 2: Hitting too many different endpoints
        if len(pattern["endpoints"]) > 50:
            await self._handle_suspicious_activity(
                client_ip,
                "endpoint_scanning",
                {"unique_endpoints": len(pattern["endpoints"])},
            )

        # Pattern 3: Consistent patterns suggesting automation
        if len(pattern["requests"]) > 20:
            intervals = [
                pattern["requests"][i] - pattern["requests"][i - 1]
                for i in range(1, len(pattern["requests"]))
            ]
            avg_interval = sum(intervals) / len(intervals)
            interval_variance = sum((x - avg_interval) ** 2 for x in intervals) / len(
                intervals
            )

            # Very consistent intervals suggest automation
            if interval_variance < 0.1 and avg_interval < 2:
                await self._handle_suspicious_activity(
                    client_ip, "automation_detected", {"avg_interval": avg_interval}
                )

    async def _handle_suspicious_activity(
        self, client_ip: str, activity_type: str, details: Dict[str, Any]
    ):
        """Handle detected suspicious activity"""

        logger.warning(
            f"Suspicious activity detected from {client_ip}: {activity_type}",
            extra={
                "client_ip": client_ip,
                "activity_type": activity_type,
                "details": details,
            },
        )

        # Implement progressive blocking
        current_time = time.time()

        if activity_type == "high_frequency":
            # Block for 10 minutes
            self.blocked_ips[client_ip] = current_time + 600
        elif activity_type == "endpoint_scanning":
            # Block for 30 minutes
            self.blocked_ips[client_ip] = current_time + 1800
        elif activity_type == "automation_detected":
            # Block for 1 hour
            self.blocked_ips[client_ip] = current_time + 3600

    async def _is_ip_blocked(self, client_ip: str) -> bool:
        """Check if IP is currently blocked"""
        if client_ip in self.blocked_ips:
            if time.time() < self.blocked_ips[client_ip]:
                return True
            else:
                # Block expired, remove it
                del self.blocked_ips[client_ip]

        return False

    async def _log_rate_limit_event(
        self,
        request: Request,
        client_key: str,
        endpoint_type: str,
        metadata: Dict[str, Any],
    ):
        """Log rate limit events for monitoring"""

        event_data = {
            "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
            "client_key": client_key,
            "client_ip": self._get_client_ip(request),
            "endpoint": str(request.url),
            "method": request.method,
            "endpoint_type": endpoint_type,
            "user_agent": request.headers.get("user-agent", "unknown"),
            "metadata": metadata,
        }

        logger.warning(f"Rate limit exceeded: {json.dumps(event_data)}")


# Global rate limiter instance
rate_limiter = AdaptiveRateLimiter()


async def rate_limiting_middleware(request: Request, call_next):
    """Rate limiting middleware"""

    # Skip rate limiting for health checks and docs
    if request.url.path in ["/health", "/v1/docs", "/v1/redoc", "/v1/openapi.json"]:
        return await call_next(request)

    # Determine endpoint type
    endpoint_type = _determine_endpoint_type(request.url.path, request.method)

    # Get user information if available
    user_id = getattr(request.state, "user_id", None)
    user_role = getattr(request.state, "user_role", None)

    # Check rate limit
    allowed, metadata = await rate_limiter.check_rate_limit(
        request, endpoint_type, user_id, user_role
    )

    if not allowed:
        # Create rate limit error response
        return JSONResponse(
            status_code=429,
            content={
                "error": True,
                "error_code": "RATE_LIMIT_EXCEEDED",
                "message": "Rate limit exceeded. Please try again later.",
                "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
                "details": {
                    "limit": metadata["limit"],
                    "retry_after": metadata["retry_after"],
                    "reset_time": metadata["reset_time"],
                },
            },
            headers={
                "X-RateLimit-Limit": str(metadata["limit"]),
                "X-RateLimit-Remaining": str(metadata["remaining"]),
                "X-RateLimit-Reset": str(metadata["reset_time"]),
                "Retry-After": str(metadata["retry_after"]),
            },
        )

    # Process request and add rate limit headers to response
    response = await call_next(request)

    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(metadata["limit"])
    response.headers["X-RateLimit-Remaining"] = str(metadata["remaining"])
    response.headers["X-RateLimit-Reset"] = str(metadata["reset_time"])

    return response


def _determine_endpoint_type(path: str, method: str) -> str:
    """Determine endpoint type for rate limiting"""

    # Authentication endpoints
    if "/auth/login" in path:
        return "auth_login"
    elif "/auth/register" in path:
        return "auth_register"

    # File operations
    elif "/files/upload" in path:
        return "file_upload"

    # Search operations
    elif "/search" in path or "/opportunities/search" in path:
        return "search"

    # WebSocket connections
    elif "/ws" in path:
        return "websocket"

    # Default
    else:
        return "api_general"
