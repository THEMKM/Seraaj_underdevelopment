"""
Loading States and Progress Tracking Middleware for Seraaj API
Provides loading indicators, progress tracking, and response timing
"""

import time
import asyncio
from typing import Dict, Any, Optional, Callable
from fastapi import Request
from fastapi.responses import JSONResponse, StreamingResponse
import json
import logging

logger = logging.getLogger(__name__)


class LoadingState:
    """Represents a loading state for long-running operations"""

    def __init__(
        self,
        operation_id: str,
        operation_type: str,
        total_steps: int = None,
        description: str = None,
    ):
        self.operation_id = operation_id
        self.operation_type = operation_type
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.status = "in_progress"
        self.progress_percentage = 0
        self.start_time = time.time()
        self.estimated_completion = None
        self.steps = []
        self.current_step_description = None
        self.error = None

    def update_progress(
        self,
        step: int = None,
        description: str = None,
        step_data: Dict[str, Any] = None,
    ):
        """Update the progress of the operation"""
        if step is not None:
            self.current_step = step
            if self.total_steps:
                self.progress_percentage = min((step / self.total_steps) * 100, 100)

        if description:
            self.current_step_description = description

        # Add step to history
        step_info = {
            "step": self.current_step,
            "description": description or self.current_step_description,
            "timestamp": time.time(),
            "data": step_data or {},
        }
        self.steps.append(step_info)

        # Estimate completion time based on progress
        if self.current_step > 0 and self.total_steps:
            elapsed_time = time.time() - self.start_time
            avg_time_per_step = elapsed_time / self.current_step
            remaining_steps = self.total_steps - self.current_step
            self.estimated_completion = time.time() + (
                remaining_steps * avg_time_per_step
            )

    def complete(self, result: Dict[str, Any] = None):
        """Mark the operation as completed"""
        self.status = "completed"
        self.progress_percentage = 100
        self.current_step = self.total_steps or self.current_step
        if result:
            self.steps.append(
                {
                    "step": "completion",
                    "description": "Operation completed successfully",
                    "timestamp": time.time(),
                    "data": result,
                }
            )

    def fail(self, error: str, error_details: Dict[str, Any] = None):
        """Mark the operation as failed"""
        self.status = "failed"
        self.error = error
        self.steps.append(
            {
                "step": "error",
                "description": f"Operation failed: {error}",
                "timestamp": time.time(),
                "data": error_details or {},
            }
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert loading state to dictionary"""
        elapsed_time = time.time() - self.start_time

        return {
            "operation_id": self.operation_id,
            "operation_type": self.operation_type,
            "status": self.status,
            "progress_percentage": round(self.progress_percentage, 2),
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "current_step_description": self.current_step_description,
            "description": self.description,
            "elapsed_time": round(elapsed_time, 2),
            "estimated_completion": self.estimated_completion,
            "steps_completed": len([s for s in self.steps if s["step"] != "error"]),
            "error": self.error,
        }


class LoadingStateManager:
    """Manages loading states for long-running operations"""

    def __init__(self):
        self.loading_states: Dict[str, LoadingState] = {}
        self.cleanup_interval = 3600  # 1 hour
        self.max_history = 1000

    def create_loading_state(
        self,
        operation_id: str,
        operation_type: str,
        total_steps: int = None,
        description: str = None,
    ) -> LoadingState:
        """Create a new loading state"""
        loading_state = LoadingState(
            operation_id, operation_type, total_steps, description
        )
        self.loading_states[operation_id] = loading_state

        # Cleanup old states
        self._cleanup_old_states()

        return loading_state

    def get_loading_state(self, operation_id: str) -> Optional[LoadingState]:
        """Get a loading state by operation ID"""
        return self.loading_states.get(operation_id)

    def update_loading_state(
        self,
        operation_id: str,
        step: int = None,
        description: str = None,
        step_data: Dict[str, Any] = None,
    ) -> bool:
        """Update a loading state"""
        loading_state = self.loading_states.get(operation_id)
        if loading_state:
            loading_state.update_progress(step, description, step_data)
            return True
        return False

    def complete_loading_state(
        self, operation_id: str, result: Dict[str, Any] = None
    ) -> bool:
        """Mark a loading state as completed"""
        loading_state = self.loading_states.get(operation_id)
        if loading_state:
            loading_state.complete(result)
            return True
        return False

    def fail_loading_state(
        self, operation_id: str, error: str, error_details: Dict[str, Any] = None
    ) -> bool:
        """Mark a loading state as failed"""
        loading_state = self.loading_states.get(operation_id)
        if loading_state:
            loading_state.fail(error, error_details)
            return True
        return False

    def remove_loading_state(self, operation_id: str) -> bool:
        """Remove a loading state"""
        if operation_id in self.loading_states:
            del self.loading_states[operation_id]
            return True
        return False

    def get_user_loading_states(self, user_id: int) -> Dict[str, Dict[str, Any]]:
        """Get all loading states for a specific user"""
        user_states = {}
        for operation_id, state in self.loading_states.items():
            # Assuming operation_id contains user_id (e.g., "upload_123_456")
            if f"_{user_id}_" in operation_id or operation_id.endswith(f"_{user_id}"):
                user_states[operation_id] = state.to_dict()
        return user_states

    def _cleanup_old_states(self):
        """Remove old completed or failed states"""
        current_time = time.time()
        to_remove = []

        for operation_id, state in self.loading_states.items():
            # Remove states older than cleanup_interval
            if (current_time - state.start_time) > self.cleanup_interval:
                to_remove.append(operation_id)

        for operation_id in to_remove:
            del self.loading_states[operation_id]

        # Keep only the most recent states if we exceed max_history
        if len(self.loading_states) > self.max_history:
            sorted_states = sorted(
                self.loading_states.items(), key=lambda x: x[1].start_time, reverse=True
            )

            # Keep only the most recent max_history states
            self.loading_states = dict(sorted_states[: self.max_history])


# Global loading state manager
loading_manager = LoadingStateManager()


class ProgressTracker:
    """Context manager for tracking operation progress"""

    def __init__(
        self,
        operation_id: str,
        operation_type: str,
        total_steps: int = None,
        description: str = None,
    ):
        self.operation_id = operation_id
        self.loading_state = loading_manager.create_loading_state(
            operation_id, operation_type, total_steps, description
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # Completed successfully
            loading_manager.complete_loading_state(self.operation_id)
        else:
            # Failed with exception
            error_message = str(exc_val) if exc_val else "Unknown error"
            loading_manager.fail_loading_state(
                self.operation_id,
                error_message,
                {"exception_type": exc_type.__name__ if exc_type else None},
            )

    def update(
        self,
        step: int = None,
        description: str = None,
        step_data: Dict[str, Any] = None,
    ):
        """Update progress"""
        loading_manager.update_loading_state(
            self.operation_id, step, description, step_data
        )

    def set_total_steps(self, total_steps: int):
        """Update total steps"""
        self.loading_state.total_steps = total_steps
        if self.loading_state.current_step > 0:
            self.loading_state.progress_percentage = (
                self.loading_state.current_step / total_steps
            ) * 100


async def response_timing_middleware(request: Request, call_next):
    """Middleware to add response timing information"""
    start_time = time.time()

    # Add timing info to request state
    request.state.start_time = start_time

    response = await call_next(request)

    # Calculate response time
    end_time = time.time()
    response_time = end_time - start_time

    # Add timing headers
    response.headers["X-Response-Time"] = f"{response_time:.3f}s"
    response.headers["X-Process-Time"] = f"{response_time * 1000:.2f}ms"

    # Log slow responses
    if response_time > 2.0:  # Log responses slower than 2 seconds
        logger.warning(
            f"Slow response: {request.method} {request.url} took {response_time:.3f}s",
            extra={
                "method": request.method,
                "url": str(request.url),
                "response_time": response_time,
                "status_code": response.status_code,
            },
        )

    return response


def create_loading_response(
    operation_id: str,
    operation_type: str,
    message: str = "Operation started",
    total_steps: int = None,
    description: str = None,
) -> JSONResponse:
    """Create a response indicating that a long-running operation has started"""

    loading_state = loading_manager.create_loading_state(
        operation_id, operation_type, total_steps, description
    )

    response_data = {
        "loading": True,
        "operation_id": operation_id,
        "operation_type": operation_type,
        "message": message,
        "progress": loading_state.to_dict(),
        "status_endpoint": f"/v1/operations/{operation_id}/status",
        "estimated_completion": "calculating...",
        "can_cancel": False,  # Can be updated based on operation type
    }

    return JSONResponse(
        status_code=202,  # Accepted
        content=response_data,
        headers={"X-Operation-ID": operation_id, "X-Operation-Type": operation_type},
    )


def create_progress_stream(operation_id: str) -> StreamingResponse:
    """Create a server-sent events stream for progress updates"""

    async def generate_progress_stream():
        """Generate progress updates as server-sent events"""
        loading_state = loading_manager.get_loading_state(operation_id)

        if not loading_state:
            yield f"data: {json.dumps({'error': 'Operation not found'})}\n\n"
            return

        last_step = -1

        while loading_state.status == "in_progress":
            current_data = loading_state.to_dict()

            # Only send update if there's new progress
            if loading_state.current_step > last_step:
                yield f"data: {json.dumps(current_data)}\n\n"
                last_step = loading_state.current_step

            await asyncio.sleep(0.5)  # Check every 500ms

        # Send final status
        final_data = loading_state.to_dict()
        yield f"data: {json.dumps(final_data)}\n\n"

        # Close the stream
        yield "event: close\n"
        yield "data: Stream closed\n\n"

    return StreamingResponse(
        generate_progress_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


# Decorators for common loading state patterns
def track_progress(
    operation_type: str,
    total_steps: int = None,
    description: str = None,
    generate_operation_id: Callable[[Any], str] = None,
) -> Callable:
    """Decorator to automatically track progress for a function"""

    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            # Generate operation ID
            if generate_operation_id:
                operation_id = generate_operation_id(args, kwargs)
            else:
                operation_id = f"{operation_type}_{int(time.time())}_{id(func)}"

            # Create progress tracker
            with ProgressTracker(
                operation_id, operation_type, total_steps, description
            ) as tracker:
                # Pass tracker to function if it accepts it
                import inspect

                sig = inspect.signature(func)
                if "progress_tracker" in sig.parameters:
                    kwargs["progress_tracker"] = tracker

                return await func(*args, **kwargs)

        return wrapper

    return decorator


def async_operation(
    operation_type: str, description: str = None, total_steps: int = None
) -> Callable:
    """Decorator to mark a function as an async operation that returns immediately"""

    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            import uuid

            operation_id = f"{operation_type}_{uuid.uuid4().hex[:8]}"

            # Start the operation in the background
            asyncio.create_task(
                run_async_operation(func, operation_id, operation_type, args, kwargs)
            )

            # Return loading response immediately
            return create_loading_response(
                operation_id,
                operation_type,
                f"{operation_type.replace('_', ' ').title()} started",
                total_steps,
                description,
            )

        return wrapper

    return decorator


async def run_async_operation(
    func: Callable, operation_id: str, operation_type: str, args: tuple, kwargs: dict
):
    """Run an async operation with progress tracking"""
    try:
        with ProgressTracker(operation_id, operation_type) as tracker:
            # Pass tracker to function if it accepts it
            import inspect

            sig = inspect.signature(func)
            if "progress_tracker" in sig.parameters:
                kwargs["progress_tracker"] = tracker

            result = await func(*args, **kwargs)

            # Store result in loading state
            loading_manager.complete_loading_state(operation_id, {"result": result})

    except Exception as e:
        logger.error(f"Async operation {operation_id} failed: {e}")
        loading_manager.fail_loading_state(operation_id, str(e))
