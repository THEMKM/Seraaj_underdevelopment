# Implementation Report: websocket_get_online_users_GET

**Symbol Status:** ❌ INCONSISTENT  
**Commit:** `a602ba5`  
**Analysis Date:** 2025-08-04

## Executive Summary

The `websocket_get_online_users_GET` symbol represents a critical integration failure between the frontend WebSocket implementation and the backend API architecture. While the backend provides both WebSocket and REST endpoints for retrieving online users, the frontend attempts to connect using incorrect URL patterns and lacks proper integration with the REST endpoint.

**Key Issues:**
- Frontend WebSocket URL construction is incompatible with backend endpoints
- Symbol naming convention doesn't match actual implementation paths
- API response format inconsistencies
- Missing integration between WebSocket fallback and REST API

## Detailed Analysis

### Frontend Layer (React/TypeScript)

**File:** `apps/web/contexts/WebSocketContext.tsx`

The WebSocket context attempts to connect using a URL pattern that doesn't match the backend implementation:

```typescript
// Line 312 - INCORRECT URL PATTERN
const wsUrl = `${process.env.NEXT_PUBLIC_API_URL || ''}/ws/${conversationId}?token=${token}`;
```

**Issues:**
- Expected pattern: `/ws/{conversationId}` 
- Actual backend pattern: WebSocket at `/ws/{conversation_id}` (without version prefix)
- REST endpoint at: `/v1/messaging/online-users`
- Falls back to mock data instead of calling REST API on connection failure

### Backend Layer (FastAPI)

**Router Configuration:** `apps/api/routers/websocket.py`

```python
# Line 32 - Router has versioned prefix
router = APIRouter(prefix="/v1/messaging", tags=["messaging"])

# Line 386 - REST endpoint for online users  
@router.get("/online-users")
async def get_online_users(current_user: Annotated[User, Depends(get_current_user)]):
    online_users = connection_manager.get_online_users()
    return {"online_users": online_users, "count": len(online_users)}
```

**WebSocket Endpoint:** `apps/api/routers/websocket.py`

```python 
# Line 53 - WebSocket endpoint WITHOUT version prefix
@ws_router.websocket("/ws/{conversation_id}")
async def conversation_websocket(websocket: WebSocket, conversation_id: int, token: str = Query(...)):
```

### Service Layer

**Connection Manager:** `apps/api/websocket/connection_manager.py`

The underlying service implementation is sound:

```python
# Line 155
def get_online_users(self) -> List[int]:
    """Get list of currently online users"""
    return list(self.active_connections.keys())
```

**Message Handler:** `apps/api/websocket/message_handler.py`

WebSocket message handling supports getting online users:

```python
# Line 343
async def handle_get_online_users(self, data: Dict[str, Any], user_id: int, session: Session):
    online_users = connection_manager.get_online_users()
    return {
        "type": "online_users",
        "data": {
            "online_users": online_users,
            "count": len(online_users),
            "conversation_id": conversation_id,
        },
    }
```

## Critical Defects

### High Severity

1. **Frontend-Backend URL Mismatch**
   - **Location:** `apps/web/contexts/WebSocketContext.tsx:312`
   - **Issue:** Frontend constructs WebSocket URL as `/ws/{conversationId}` but backend expects different structure
   - **Impact:** WebSocket connections will fail, breaking real-time functionality

2. **Symbol Naming Inconsistency**  
   - **Location:** `scripts/targets.json:1066`
   - **Issue:** Symbol named `websocket_get_online_users_GET` suggests one endpoint but implementation is at `/v1/messaging/online-users`
   - **Impact:** API documentation and client expectations don't match implementation

### Medium Severity

3. **Inconsistent URL Versioning**
   - **Location:** `apps/api/routers/websocket.py:53`
   - **Issue:** WebSocket endpoints not prefixed with `/v1/` while REST endpoints are
   - **Impact:** Inconsistent API design, confusion for frontend developers

4. **Missing REST API Integration**
   - **Location:** `apps/web/contexts/WebSocketContext.tsx:341`  
   - **Issue:** Frontend falls back to mock data instead of calling REST endpoint
   - **Impact:** Offline functionality broken, users see stale data

### Low Severity

5. **Inconsistent API Response Format**
   - **Location:** `apps/api/routers/websocket.py:389`
   - **Issue:** Direct return of connection manager data without standard API wrapper
   - **Impact:** Response format differs from other API endpoints

## Recommendations

### Immediate Fixes

1. **Standardize WebSocket URL Pattern**
   ```typescript
   // Frontend: Update WebSocket URL construction
   const wsUrl = `${process.env.NEXT_PUBLIC_API_URL?.replace('http', 'ws') || 'ws://localhost:8000'}/ws/${conversationId}?token=${token}`;
   ```

2. **Add REST API Fallback**
   ```typescript
   // Frontend: Call REST endpoint when WebSocket fails
   const fetchOnlineUsers = async () => {
     try {
       const response = await fetch('/v1/messaging/online-users', {
         headers: { 'Authorization': `Bearer ${token}` }
       });
       const data = await response.json();
       setOnlineUsers(data.online_users);
     } catch (error) {
       console.error('Failed to fetch online users:', error);
     }
   };
   ```

3. **Standardize API Response Format**
   ```python
   # Backend: Wrap response in standard format
   @router.get("/online-users")
   async def get_online_users(current_user: Annotated[User, Depends(get_current_user)]):
       online_users = connection_manager.get_online_users()
       return {
           "success": True,
           "data": {
               "online_users": online_users, 
               "count": len(online_users)
           }
       }
   ```

### Architectural Improvements

1. **Unify WebSocket and REST API versioning**
2. **Implement proper error handling in WebSocket context**
3. **Add comprehensive integration tests**
4. **Update API documentation to reflect actual endpoints**

## Test Coverage Analysis

Current tests in `apps/api/tests/test_websocket.py` use incorrect URL patterns and don't cover the REST endpoint. Missing tests for:
- REST API endpoint `/v1/messaging/online-users`
- WebSocket message type `get_online_users` 
- Frontend-backend integration scenarios
- Error handling and fallback behavior

## Conclusion

The `websocket_get_online_users_GET` symbol represents a fundamental integration issue where the frontend and backend are not properly aligned. While individual components work (connection manager, message handler), the integration points fail due to URL pattern mismatches and missing fallback implementations. This requires immediate architectural fixes to ensure reliable real-time functionality.