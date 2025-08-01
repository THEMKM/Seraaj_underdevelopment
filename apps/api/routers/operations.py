"""
Operations Status API Router
Provides endpoints for checking the status of long-running operations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Annotated, Dict, Any, Optional
from datetime import datetime

from database import get_session
from models import User
from routers.auth import get_current_user
from middleware.loading_states import loading_manager, create_progress_stream
from middleware.error_handler import raise_not_found, raise_forbidden

router = APIRouter(prefix="/v1/operations", tags=["operations"])


@router.get("/{operation_id}/status")
async def get_operation_status(
    operation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Get the status of a long-running operation"""
    
    loading_state = loading_manager.get_loading_state(operation_id)
    
    if not loading_state:
        raise_not_found(
            "Operation not found or has expired",
            resource_type="operation",
            resource_id=operation_id
        )
    
    # Check if user has permission to view this operation
    # (In a real implementation, you'd check operation ownership)
    if not _user_can_access_operation(current_user.id, operation_id):
        raise_forbidden("You don't have permission to view this operation")
    
    operation_data = loading_state.to_dict()
    
    # Add additional metadata
    operation_data.update({
        "can_cancel": _operation_can_be_cancelled(operation_id),
        "retry_available": loading_state.status == "failed",
        "result_available": loading_state.status == "completed",
        "logs_available": len(loading_state.steps) > 0
    })
    
    return {
        "operation": operation_data,
        "endpoints": {
            "status": f"/v1/operations/{operation_id}/status",
            "stream": f"/v1/operations/{operation_id}/stream",
            "cancel": f"/v1/operations/{operation_id}/cancel",
            "logs": f"/v1/operations/{operation_id}/logs"
        }
    }


@router.get("/{operation_id}/stream")
async def stream_operation_progress(
    operation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Stream real-time progress updates for an operation"""
    
    loading_state = loading_manager.get_loading_state(operation_id)
    
    if not loading_state:
        raise_not_found(
            "Operation not found or has expired",
            resource_type="operation",
            resource_id=operation_id
        )
    
    # Check permissions
    if not _user_can_access_operation(current_user.id, operation_id):
        raise_forbidden("You don't have permission to view this operation")
    
    return create_progress_stream(operation_id)


@router.post("/{operation_id}/cancel")
async def cancel_operation(
    operation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Cancel a running operation"""
    
    loading_state = loading_manager.get_loading_state(operation_id)
    
    if not loading_state:
        raise_not_found(
            "Operation not found or has expired",
            resource_type="operation",
            resource_id=operation_id
        )
    
    # Check permissions
    if not _user_can_access_operation(current_user.id, operation_id):
        raise_forbidden("You don't have permission to cancel this operation")
    
    # Check if operation can be cancelled
    if not _operation_can_be_cancelled(operation_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This operation cannot be cancelled"
        )
    
    # Mark operation as cancelled
    loading_manager.fail_loading_state(
        operation_id,
        "Operation cancelled by user",
        {"cancelled_by": current_user.id, "cancelled_at": datetime.now(datetime.timezone.utc).isoformat()}
    )
    
    return {
        "message": "Operation cancelled successfully",
        "operation_id": operation_id,
        "cancelled_at": datetime.now(datetime.timezone.utc).isoformat()
    }


@router.get("/{operation_id}/logs")
async def get_operation_logs(
    operation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Get detailed logs for an operation"""
    
    loading_state = loading_manager.get_loading_state(operation_id)
    
    if not loading_state:
        raise_not_found(
            "Operation not found or has expired",
            resource_type="operation",
            resource_id=operation_id
        )
    
    # Check permissions
    if not _user_can_access_operation(current_user.id, operation_id):
        raise_forbidden("You don't have permission to view operation logs")
    
    # Format logs for display
    formatted_logs = []
    for step in loading_state.steps:
        formatted_logs.append({
            "step": step["step"],
            "description": step["description"],
            "timestamp": datetime.fromtimestamp(step["timestamp"]).isoformat(),
            "data": step.get("data", {}),
            "duration": _calculate_step_duration(loading_state.steps, step)
        })
    
    return {
        "operation_id": operation_id,
        "operation_type": loading_state.operation_type,
        "total_logs": len(formatted_logs),
        "logs": formatted_logs,
        "summary": {
            "total_duration": time.time() - loading_state.start_time,
            "steps_completed": loading_state.current_step,
            "total_steps": loading_state.total_steps,
            "success_rate": _calculate_success_rate(loading_state.steps)
        }
    }


@router.get("/my-operations")
async def get_my_operations(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    status_filter: Optional[str] = None,
    operation_type: Optional[str] = None,
    limit: int = 20
):
    """Get all operations for the current user"""
    
    user_operations = loading_manager.get_user_loading_states(current_user.id)
    
    # Apply filters
    filtered_operations = {}
    for op_id, operation in user_operations.items():
        # Status filter
        if status_filter and operation["status"] != status_filter:
            continue
        
        # Operation type filter
        if operation_type and operation["operation_type"] != operation_type:
            continue
        
        filtered_operations[op_id] = operation
    
    # Sort by start time (most recent first)
    sorted_operations = sorted(
        filtered_operations.items(),
        key=lambda x: x[1].get("elapsed_time", 0),
        reverse=True
    )
    
    # Apply limit
    limited_operations = dict(sorted_operations[:limit])
    
    # Add metadata to each operation
    for op_id, operation in limited_operations.items():
        operation.update({
            "can_cancel": _operation_can_be_cancelled(op_id),
            "can_retry": operation["status"] == "failed",
            "endpoints": {
                "status": f"/v1/operations/{op_id}/status",
                "stream": f"/v1/operations/{op_id}/stream",
                "logs": f"/v1/operations/{op_id}/logs"
            }
        })
    
    return {
        "operations": limited_operations,
        "total_count": len(limited_operations),
        "filtered_count": len(user_operations),
        "filters": {
            "status": status_filter,
            "operation_type": operation_type
        }
    }


@router.delete("/{operation_id}")
async def delete_operation(
    operation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Remove an operation from history"""
    
    loading_state = loading_manager.get_loading_state(operation_id)
    
    if not loading_state:
        raise_not_found(
            "Operation not found",
            resource_type="operation",
            resource_id=operation_id
        )
    
    # Check permissions
    if not _user_can_access_operation(current_user.id, operation_id):
        raise_forbidden("You don't have permission to delete this operation")
    
    # Only allow deletion of completed or failed operations
    if loading_state.status == "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete an operation that is still in progress"
        )
    
    # Remove the operation
    success = loading_manager.remove_loading_state(operation_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete operation"
        )
    
    return {
        "message": "Operation deleted successfully",
        "operation_id": operation_id,
        "deleted_at": datetime.now(datetime.timezone.utc).isoformat()
    }


@router.get("/stats")
async def get_operations_statistics(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Get operations statistics for the current user"""
    
    user_operations = loading_manager.get_user_loading_states(current_user.id)
    
    if not user_operations:
        return {
            "total_operations": 0,
            "status_breakdown": {},
            "operation_type_breakdown": {},
            "average_completion_time": 0,
            "success_rate": 0
        }
    
    # Calculate statistics
    total_operations = len(user_operations)
    status_counts = {}
    type_counts = {}
    completion_times = []
    successful_operations = 0
    
    for operation in user_operations.values():
        # Count by status
        status = operation["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count by type
        op_type = operation["operation_type"]
        type_counts[op_type] = type_counts.get(op_type, 0) + 1
        
        # Track completion times
        if status in ["completed", "failed"]:
            completion_times.append(operation["elapsed_time"])
        
        # Count successful operations
        if status == "completed":
            successful_operations += 1
    
    # Calculate averages
    avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
    success_rate = (successful_operations / total_operations) * 100 if total_operations > 0 else 0
    
    return {
        "total_operations": total_operations,
        "status_breakdown": status_counts,
        "operation_type_breakdown": type_counts,
        "average_completion_time": round(avg_completion_time, 2),
        "success_rate": round(success_rate, 2),
        "recent_operations": len([
            op for op in user_operations.values()
            if (time.time() - op.get("elapsed_time", 0)) < 86400  # Last 24 hours
        ])
    }


# Helper functions
def _user_can_access_operation(user_id: int, operation_id: str) -> bool:
    """Check if user can access the operation"""
    loading_state = loading_manager.get_loading_state(operation_id)
    if not loading_state:
        return False
    
    # Check if user owns the operation or is an admin
    # Operations store user_id in their metadata
    operation_user_id = loading_state.metadata.get("user_id") if loading_state.metadata else None
    
    if operation_user_id == user_id:
        return True
    
    # Allow access if operation_id contains user_id (fallback for legacy operations)
    return f"_{user_id}_" in operation_id or operation_id.endswith(f"_{user_id}")


def _operation_can_be_cancelled(operation_id: str) -> bool:
    """Check if an operation can be cancelled"""
    loading_state = loading_manager.get_loading_state(operation_id)
    if not loading_state:
        return False
    
    # Only in-progress operations can be cancelled
    if loading_state.status != "in_progress":
        return False
    
    # Some operation types might not be cancellable
    non_cancellable_types = ["database_migration", "critical_update"]
    return loading_state.operation_type not in non_cancellable_types


def _calculate_step_duration(steps: list, current_step: dict) -> float:
    """Calculate the duration of a specific step"""
    current_time = current_step["timestamp"]
    
    # Find the previous step
    previous_step = None
    for step in steps:
        if step["timestamp"] < current_time:
            if not previous_step or step["timestamp"] > previous_step["timestamp"]:
                previous_step = step
    
    if previous_step:
        return current_time - previous_step["timestamp"]
    else:
        # First step - duration from operation start
        # This would require access to loading_state.start_time
        return 0


def _calculate_success_rate(steps: list) -> float:
    """Calculate success rate of operation steps"""
    if not steps:
        return 0
    
    error_steps = len([step for step in steps if step["step"] == "error"])
    total_steps = len(steps)
    
    return ((total_steps - error_steps) / total_steps) * 100 if total_steps > 0 else 0


import time