# Seraaj v2 API Issues & Inconsistencies

## Overview

This document identifies critical API inconsistencies, missing implementations, and architectural issues discovered during development. These issues prevent seamless frontend-backend integration and need resolution.

## Critical Issues

### 1. **Phantom Endpoints in OpenAPI Spec**

**Problem**: The OpenAPI specification shows endpoints that don't exist in the current codebase.

**Examples of Phantom Endpoints:**
- `/opportunity/search` (returns 500 Internal Server Error)
- `/opportunity/{opp_id}`
- `/opportunity/org/{org_id}`
- `/opportunity/search/matched`
- `/application/{opp_id}/apply`
- `/application/org/{org_id}`
- `/applicants`
- `/match/me`
- `/conversation`
- `/workspace/{app_id}`
- `/forum/post`
- `/analytics/record`

**Impact**: 
- Frontend calls these endpoints and receives 500 errors
- Developers waste time debugging non-existent code
- API documentation is misleading

**Root Cause Analysis:**
- These endpoints appear to be generated from a different version of the API
- Possibly from legacy code or a different server instance
- The OpenAPI spec is out of sync with the actual router implementations

**Recommended Fix:**
1. Audit all router files against the OpenAPI spec
2. Remove phantom endpoints from documentation
3. Implement missing critical endpoints (search, messaging, etc.)
4. Establish process to keep OpenAPI spec in sync

### 2. **Dual Router Architecture**

**Problem**: Two different routing patterns exist simultaneously.

**Current Router Pattern** (Working):
```
/auth/*                  ✅ Working
/v1/opportunities/*      ✅ Working  
/v1/applications/*       ✅ Working
/v1/profiles/*          ✅ Working
```

**Legacy Router Pattern** (Broken):
```
/opportunity/*           ❌ 500 Errors
/application/*           ❌ 500 Errors  
/applicants              ❌ 500 Errors
/match/*                 ❌ 500 Errors
```

**Impact**:
- Frontend API client calls wrong endpoints
- Inconsistent URL patterns confuse developers
- Some features completely non-functional

**Recommended Fix:**
1. Standardize on `/v1/` prefix for all endpoints
2. Update frontend API client to use correct endpoints
3. Remove or fix legacy endpoint references

### 3. **Missing Search Implementation**

**Problem**: No working search endpoint for opportunities.

**Current State**:
- `/opportunity/search` returns 500 error
- `/v1/opportunities/search` doesn't exist (but should)
- Frontend expects search functionality

**Impact**:
- Main feed page cannot load opportunities
- Search functionality completely broken
- User cannot discover opportunities

**Recommended Fix**:
```python
# Add to opportunities.py router
@router.get("/search", response_model=List[OpportunityRead])
async def search_opportunities(
    session: Annotated[Session, Depends(get_session)],
    search: Optional[str] = Query(None),
    skills: Optional[List[str]] = Query(None),
    remote_allowed: Optional[bool] = Query(None),
    limit: int = Query(20, ge=1, le=100)
):
    # Implementation here
```

### 4. **Disabled Router Dependencies**

**Problem**: Most routers are commented out due to dependency issues.

**Disabled Routers** (in `main.py`):
```python
# from routers import websocket, admin, reviews, files, verification, 
# collaboration, match, operations, system, payments, guided_tours, 
# push_notifications, pwa, demo_scenarios
```

**Specific Issues**:
- **Parameter Ordering**: Dependencies before Query parameters with defaults
- **Type Annotations**: Missing or incorrect type hints
- **Import Errors**: Missing dependencies or circular imports

**Impact**:
- 80% of planned functionality is unavailable
- Features like messaging, file uploads, payments don't work
- Development is blocked on basic functionality

**Example Fix for Parameter Ordering**:
```python
# ❌ Broken
async def endpoint(
    param: str = Query("default"),
    session: Annotated[Session, Depends(get_session)]
):

# ✅ Fixed
async def endpoint(
    session: Annotated[Session, Depends(get_session)],
    param: str = Query("default")
):
```

### 5. **Database Model Inconsistencies**

**Problem**: Database field naming conflicts with SQLModel parent classes.

**Specific Issues**:
- `metadata` field shadows SQLModel's metadata attribute
- Missing field validations
- Inconsistent foreign key naming

**Examples**:
```python
# ❌ Problematic
class Model(SQLModel, table=True):
    metadata: Dict[str, Any]  # Conflicts with SQLModel.metadata

# ✅ Fixed  
class Model(SQLModel, table=True):
    custom_metadata: Dict[str, Any]
```

## API Standardization Plan

### Phase 1: Critical Fixes (Week 1)
1. **Fix Search Endpoint**
   - Implement `/v1/opportunities/search`
   - Update frontend API client
   - Test with real data

2. **Router Dependency Issues**
   - Fix parameter ordering in all routers
   - Add proper type annotations
   - Enable core routers (websocket, files, admin)

3. **Database Schema Cleanup**
   - Rename conflicting fields
   - Add missing validations
   - Update model relationships

### Phase 2: API Consistency (Week 2)
1. **Endpoint Standardization**
   - All endpoints use `/v1/` prefix
   - Consistent naming conventions
   - Remove phantom endpoints

2. **Response Format Standardization**
   - All responses use APIResponse wrapper
   - Consistent error formats
   - Proper HTTP status codes

3. **Documentation Sync**
   - OpenAPI spec matches implementation
   - Update API client types
   - Integration testing

### Phase 3: Missing Features (Week 3-4)
1. **Messaging System**
   - WebSocket endpoints
   - Conversation management
   - Real-time notifications

2. **File Management**
   - Upload endpoints
   - File permissions
   - Storage integration

3. **Advanced Features**
   - Matching algorithm endpoints
   - Analytics endpoints
   - Payment processing

## Current Workarounds

### For Development
1. **Use Working Endpoints Only**
   - `/auth/*` for authentication
   - `/v1/opportunities/` for basic opportunity listing
   - `/v1/applications/` for applications

2. **Mock Missing Functionality**
   - Use localStorage for search results
   - Implement client-side filtering
   - Use placeholder data for messaging

3. **Frontend Adaptation**
   - Update API client to call correct endpoints
   - Add error handling for missing endpoints
   - Implement graceful degradation

### Testing Strategy
1. **Endpoint Verification**
   ```bash
   curl -X GET "http://localhost:8000/v1/opportunities/"
   curl -X GET "http://localhost:8000/opportunity/search"  # Should fail
   ```

2. **Integration Testing**
   - Test all frontend → backend flows
   - Verify error handling
   - Check data consistency

## Long-term Architecture Recommendations

### 1. **API Versioning Strategy**
- Use semantic versioning for API changes
- Maintain backward compatibility
- Clear deprecation timeline

### 2. **Code Organization**
- Separate routers by domain (auth, opportunities, messaging)
- Shared utilities and middleware
- Consistent error handling

### 3. **Development Process**
- OpenAPI-first development
- Automated endpoint testing
- Contract testing between frontend/backend

### 4. **Monitoring & Observability**
- Endpoint usage analytics
- Error rate monitoring
- Performance tracking per endpoint

---

## Action Items

### Immediate (This Week)
- [ ] Fix `/v1/opportunities/search` endpoint
- [ ] Update frontend API client endpoints
- [ ] Enable core routers (fix dependency issues)

### Short-term (Next 2 Weeks)  
- [ ] Remove phantom endpoints from OpenAPI spec
- [ ] Standardize all endpoints to `/v1/` pattern
- [ ] Implement basic messaging endpoints

### Long-term (Next Month)
- [ ] Complete all missing functionality
- [ ] Establish API testing pipeline
- [ ] Create API versioning strategy

---

*Last Updated: July 29, 2025*
*Priority: HIGH - Blocks core functionality*