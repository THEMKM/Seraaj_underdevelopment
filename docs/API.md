# Seraaj v2 API Documentation

## Overview

The Seraaj API is built with **FastAPI** and provides RESTful endpoints for the volunteer marketplace platform. It features automatic OpenAPI documentation, comprehensive error handling, and JWT-based authentication.

## Base Configuration

- **Base URL**: `http://localhost:8000` (development)
- **Production URL**: TBD (AWS Fargate deployment)
- **Documentation**: `/docs` (Swagger UI) and `/redoc` (ReDoc)
- **OpenAPI Spec**: `/openapi.json`

## Authentication

### JWT Token System

All protected endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Authentication Endpoints

#### `POST /auth/register`
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "volunteer"  // or "organization"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "volunteer",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### `POST /auth/login`
Authenticate existing user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:** Same as registration

#### `POST /auth/refresh`
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### `POST /auth/logout` 🔒
Invalidate refresh token.

#### `GET /auth/me` 🔒
Get current authenticated user information.

## API Router Structure

### Current Working Routers

The API currently has these active routers:

1. **Authentication** (`/auth/*`)
2. **Opportunities** (`/v1/opportunities/*`)
3. **Applications** (`/v1/applications/*`)
4. **Profiles** (`/v1/profiles/*`)

### Disabled Routers

These routers exist but are currently disabled due to dependency issues:
- WebSocket (`/ws/*`)
- Admin (`/admin/*`)
- Reviews (`/reviews/*`)
- Files (`/files/*`)
- Verification (`/verification/*`)
- Calendar (`/calendar/*`)
- Collaboration (`/collaboration/*`)
- Matching (`/match/*`)
- Operations (`/operations/*`)
- System (`/system/*`)
- Payments (`/payments/*`)
- Guided Tours (`/guided-tours/*`)
- Push Notifications (`/push/*`)
- PWA (`/pwa/*`)
- Demo Scenarios (`/demo-scenarios/*`)

## Opportunities API (`/v1/opportunities/`)

### Core Endpoints

#### `GET /v1/opportunities/` 🔒
List opportunities with filtering and pagination.

**Query Parameters:**
- `skip`: Offset for pagination (default: 0)
- `limit`: Number of results (default: 50, max: 100)
- `state`: Filter by opportunity state ("draft", "active", "paused", "filled", "closed")
- `country`: Filter by country
- `causes`: Filter by cause categories
- `skills`: Filter by required skills
- `remote_allowed`: Filter by remote work option
- `urgency`: Filter by urgency level
- `featured`: Filter featured opportunities only
- `search`: Text search in title and description

**Response:**
```json
[
  {
    "id": 1,
    "title": "Community Garden Project",
    "description": "Help create and maintain a community garden",
    "state": "active",
    "org_id": 1,
    "skills_required": ["Gardening", "Physical Work"],
    "location": "Downtown Community Center",
    "remote_allowed": false,
    "urgency": "medium",
    "featured": false,
    "created_at": "2024-01-01T00:00:00Z",
    "view_count": 42
  }
]
```

#### `POST /v1/opportunities/` 🔒
Create a new opportunity (organization role required).

**Request Body:**
```json
{
  "title": "Volunteer Position Title",
  "description": "Detailed description of the role",
  "skills_required": ["Skill1", "Skill2"],
  "location": "City, Country",
  "remote_allowed": false,
  "urgency": "medium",
  "causes": ["Education", "Community"],
  "volunteers_needed": 5,
  "start_date": "2024-02-01",
  "end_date": "2024-06-01"
}
```

#### `GET /v1/opportunities/{opportunity_id}` 🔒
Get a specific opportunity by ID. Increments view count.

#### `PUT /v1/opportunities/{opportunity_id}` 🔒
Update an opportunity (owner or admin only).

#### `DELETE /v1/opportunities/{opportunity_id}` 🔒
Delete an opportunity (owner or admin only).

#### `GET /v1/opportunities/{opportunity_id}/applications` 🔒
Get applications for a specific opportunity (owner or admin only).

### Additional Endpoints

#### `GET /v1/opportunities/featured/list`
Get featured opportunities for homepage (public access).

#### `GET /v1/opportunities/stats/summary`
Get opportunities statistics (public access).

**Response:**
```json
{
  "total_opportunities": 156,
  "active_opportunities": 89,
  "featured_opportunities": 12,
  "urgency_breakdown": {
    "low": 45,
    "medium": 67,
    "high": 32,
    "critical": 12
  }
}
```

#### `GET /v1/opportunities/search`
**NEW**: Basic search endpoint with filtering.

**Query Parameters:**
- `search`: Text search in title/description
- `skills`: Array of required skills
- `remote_allowed`: Boolean for remote work
- `limit`: Results limit (default: 20, max: 100)

## Applications API (`/v1/applications/`)

### Core Endpoints

#### `POST /v1/applications/` 🔒
Create a new application (volunteer role required).

**Request Body:**
```json
{
  "opp_id": 123,
  "cover_letter": "Why I'm interested in this opportunity...",
  "availability": {
    "start_date": "2024-02-01",
    "hours_per_week": 10
  }
}
```

#### `GET /v1/applications/{application_id}` 🔒
Get application details (applicant, organization, or admin only).

#### `PUT /v1/applications/{application_id}` 🔒
Update application (applicant only, if draft/submitted status).

#### `POST /v1/applications/{application_id}/submit` 🔒
Submit a draft application (volunteer only).

#### `POST /v1/applications/{application_id}/review` 🔒
Review an application (organization or admin only).

**Request Body:**
```json
{
  "status": "accepted",  // or "rejected", "interview"
  "feedback": "Great fit for our organization!"
}
```

## Profiles API (`/v1/profiles/`)

### Volunteer Profiles

#### `POST /v1/profiles/volunteer` 🔒
Create or update volunteer profile.

#### `GET /v1/profiles/volunteer/{volunteer_id}` 🔒
Get volunteer profile.

#### `GET /v1/profiles/volunteers/search` 🔒
Search volunteers with filters.

### Organization Profiles

#### `POST /v1/profiles/organization` 🔒
Create or update organization profile.

#### `GET /v1/profiles/organization/{org_id}` 🔒
Get organization profile.

#### `GET /v1/profiles/organizations/search` 🔒
Search organizations with filters.

## Data Models

### User Model
```python
class User(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    first_name: str
    last_name: str
    role: UserRole
    is_verified: bool = False
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
```

### Opportunity Model
```python
class Opportunity(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    org_id: int = Field(foreign_key="organisations.id")
    title: str = Field(index=True)
    description: str
    state: OpportunityState = Field(default="draft")
    skills_required: List[str] = Field(sa_column=Column(JSON))
    location: Optional[str]
    remote_allowed: bool = False
    urgency: UrgencyLevel = Field(default="medium")
    featured: bool = False
    view_count: int = 0
    created_at: datetime
    updated_at: datetime
```

### Application Model
```python
class Application(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    volunteer_id: int = Field(foreign_key="volunteers.id")
    opp_id: int = Field(foreign_key="opportunities.id")
    status: ApplicationStatus = Field(default="draft")
    cover_letter: Optional[str]
    application_data: Dict[str, Any] = Field(sa_column=Column(JSON))
    submitted_at: Optional[datetime]
    reviewed_at: Optional[datetime]
    created_at: datetime
```

## Error Handling

### Standard Error Response Format
```json
{
  "detail": "Error message",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-01-01T00:00:00Z",
  "path": "/v1/opportunities/",
  "suggestions": ["Check required fields", "Verify authentication"]
}
```

### HTTP Status Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (missing/invalid token)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found
- `422`: Unprocessable Entity (validation errors)
- `429`: Too Many Requests (rate limited)
- `500`: Internal Server Error

## Middleware Stack

### Request Processing Order
1. **Rate Limiting**: Request throttling per IP
2. **Response Timing**: Performance monitoring
3. **Error Handling**: Standardized error responses
4. **CORS**: Cross-origin request handling
5. **Authentication**: JWT token validation

### Response Formatting
All successful API responses are wrapped in a consistent format:

```json
{
  "success": true,
  "data": { /* actual response data */ },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Database Schema

### Key Relationships
- **User** → **Volunteer** (1:1)
- **User** → **Organisation** (1:1)
- **Organisation** → **Opportunity** (1:many)
- **Volunteer** → **Application** (1:many)
- **Opportunity** → **Application** (1:many)
- **User** → **Conversation** (many:many)
- **Conversation** → **Message** (1:many)

### Indexes
- `users.email` (unique)
- `opportunities.title`
- `opportunities.state`
- `opportunities.org_id`
- `applications.volunteer_id`
- `applications.opp_id`
- `applications.status`

## Testing

### Test Structure
- **Unit Tests**: Individual function testing
- **Integration Tests**: Full request/response testing
- **Performance Tests**: Load and stress testing
- **Authentication Tests**: JWT and permission testing

### Test Database
Tests use an isolated SQLite database that's created and destroyed for each test session.

### Running Tests
```bash
cd apps/api
pytest tests/ -v
```

---

*Last Updated: July 29, 2025*
*Version: v2.0*