# Seraaj v2 Data Flow Documentation

## Overview

This document describes how data flows through the Seraaj application, from user interactions to database operations and real-time updates. Understanding these flows is essential for debugging, optimization, and feature development.

## System Data Flow Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Browser   │    │  Frontend   │    │  Backend    │    │  Database   │
│             │    │  (Next.js)  │    │  (FastAPI)  │    │ (SQLite/PG) │
├─────────────┤    ├─────────────┤    ├─────────────┤    ├─────────────┤
│ User Input  │───►│ React       │───►│ API         │───►│ SQLModel    │
│ UI Events   │    │ Components  │    │ Endpoints   │    │ Operations  │
│ Form Data   │    │ Contexts    │    │ Business    │    │ Queries     │
│             │◄───│ State Mgmt  │◄───│ Logic       │◄───│ Results     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Core Data Flows

### 1. Authentication Flow

#### User Registration Flow
```
User Input (Form) → Frontend Validation → API Request → Database Creation → JWT Response → Context Update → UI Redirect
```

**Detailed Steps**:

1. **User Interaction**:
   ```tsx
   // User fills registration form
   const [formData, setFormData] = useState({
     email: '',
     password: '',
     first_name: '',
     last_name: '',
     role: 'volunteer'
   });
   ```

2. **Frontend Validation**:
   ```tsx
   const validateForm = () => {
     if (!formData.email.includes('@')) return false;
     if (formData.password.length < 8) return false;
     return true;
   };
   ```

3. **API Request**:
   ```tsx
   const { register } = useAuth();
   const result = await register(formData);
   ```

4. **Backend Processing**:
   ```python
   # routers/auth.py
   @router.post("/register")
   async def register(user_data: UserCreate, session: Session):
       # Hash password
       hashed_password = get_password_hash(user_data.password)
       
       # Create user
       user = User(
           email=user_data.email,
           hashed_password=hashed_password,
           first_name=user_data.first_name,
           last_name=user_data.last_name,
           role=user_data.role
       )
       
       session.add(user)
       session.commit()
       
       # Generate tokens
       access_token = create_access_token(user.id)
       refresh_token = create_refresh_token(user.id)
       
       return {
           "access_token": access_token,
           "refresh_token": refresh_token,
           "user": user
       }
   ```

5. **Database Operations**:
   ```sql
   INSERT INTO users (email, hashed_password, first_name, last_name, role, created_at)
   VALUES (?, ?, ?, ?, ?, ?);
   ```

6. **Response Handling**:
   ```tsx
   // AuthContext.tsx
   const register = async (userData) => {
     const response = await apiClient.register(userData);
     if (response.success) {
       setUser(response.data.user);
       setIsAuthenticated(true);
       // Store tokens in localStorage
       localStorage.setItem('access_token', response.data.access_token);
       localStorage.setItem('refresh_token', response.data.refresh_token);
     }
     return response;
   };
   ```

7. **UI Update**:
   ```tsx
   // Registration page
   if (result.success) {
     router.push('/onboarding'); // Redirect to onboarding
   } else {
     setError(result.error); // Show error message
   }
   ```

#### Login Flow
```
Credentials Input → Validation → API Authentication → JWT Generation → Token Storage → User Context Update → Dashboard Redirect
```

#### Token Refresh Flow
```
API Request → 401 Response → Refresh Token Check → New Token Request → Token Update → Retry Original Request
```

### 2. Opportunity Discovery Flow

#### Feed Page Data Loading
```
Page Mount → Authentication Check → API Request → Database Query → Response Processing → UI Rendering
```

**Detailed Implementation**:

1. **Page Initialization**:
   ```tsx
   // app/feed/page.tsx
   useEffect(() => {
     if (isAuthenticated) {
       fetchOpportunities();
     }
   }, [isAuthenticated, filters]);
   ```

2. **API Request Construction**:
   ```tsx
   const fetchOpportunities = async () => {
     setLoading(true);
     const response = await opportunities.getAll({
       ...filters,
       limit: 20
     });
     
     if (response.success) {
       setCurrentOpportunities(response.data);
     } else {
       setError(response.error);
     }
     setLoading(false);
   };
   ```

3. **Backend Processing**:
   ```python
   # routers/opportunities.py
   @router.get("/", response_model=List[OpportunityRead])
   async def get_opportunities(
       session: Session,
       skip: int = 0,
       limit: int = 50,
       search: Optional[str] = None,
       remote_allowed: Optional[bool] = None
   ):
       query = select(Opportunity)
       
       # Apply filters
       if search:
           search_filter = or_(
               Opportunity.title.contains(search),
               Opportunity.description.contains(search)
           )
           query = query.where(search_filter)
       
       if remote_allowed is not None:
           query = query.where(Opportunity.remote_allowed == remote_allowed)
       
       # Order and paginate
       query = query.order_by(Opportunity.created_at.desc())
       query = query.offset(skip).limit(limit)
       
       opportunities = session.exec(query).all()
       return [OpportunityRead.model_validate(opp) for opp in opportunities]
   ```

4. **Database Query Execution**:
   ```sql
   SELECT opportunities.*
   FROM opportunities
   WHERE (title LIKE '%search%' OR description LIKE '%search%')
     AND remote_allowed = true
   ORDER BY created_at DESC
   LIMIT 20 OFFSET 0;
   ```

5. **Response Processing**:
   ```tsx
   // Frontend receives data
   const opportunities = [
     {
       id: 1,
       title: "Community Garden Project",
       description: "Help create and maintain...",
       skills_required: ["Gardening", "Physical Work"],
       is_remote: false,
       // ... other fields
     }
   ];
   ```

6. **UI Rendering**:
   ```tsx
   {currentOpportunities.map((opportunity) => (
     <PxCard key={opportunity.id}>
       <h3>{opportunity.title}</h3>
       <p>{opportunity.description}</p>
       <div className="skills">
         {opportunity.skills_required.map(skill => (
           <PxChip key={skill}>{skill}</PxChip>
         ))}
       </div>
     </PxCard>
   ))}
   ```

### 3. Application Submission Flow

#### User Applies to Opportunity
```
Apply Button Click → Form Validation → API Request → Database Insert → Email Notification → UI Feedback
```

**Implementation Details**:

1. **User Interaction**:
   ```tsx
   const handleApply = async (opportunityId) => {
     const response = await opportunities.apply(opportunityId, {
       cover_letter: coverLetter,
       availability: selectedAvailability
     });
     
     if (response.success) {
       showSuccessMessage("Application submitted!");
       handleSwipe('right'); // Move to next opportunity
     } else {
       setError(response.error);
     }
   };
   ```

2. **Backend Processing**:
   ```python
   @router.post("/", response_model=ApplicationRead)
   async def create_application(
       application_data: ApplicationCreate,
       current_user: User,
       session: Session
   ):
       # Verify volunteer profile exists
       volunteer = session.exec(
           select(Volunteer).where(Volunteer.user_id == current_user.id)
       ).first()
       
       if not volunteer:
           raise HTTPException(400, "Volunteer profile required")
       
       # Verify opportunity exists and is active
       opportunity = session.get(Opportunity, application_data.opp_id)
       if not opportunity or opportunity.state != "active":
           raise HTTPException(404, "Opportunity not available")
       
       # Create application
       application = Application(
           volunteer_id=volunteer.id,
           opp_id=opportunity.id,
           cover_letter=application_data.cover_letter,
           status="submitted",
           submitted_at=datetime.now(datetime.timezone.utc)
       )
       
       session.add(application)
       session.commit()
       session.refresh(application)
       
       # TODO: Send notification to organization
       
       return ApplicationRead.model_validate(application)
   ```

3. **Database Operations**:
   ```sql
   -- Insert application
   INSERT INTO applications (volunteer_id, opp_id, cover_letter, status, submitted_at, created_at)
   VALUES (?, ?, ?, 'submitted', ?, ?);
   
   -- Update opportunity stats (if needed)
   UPDATE opportunities 
   SET application_count = application_count + 1 
   WHERE id = ?;
   ```

### 4. Real-time Messaging Flow

#### WebSocket Connection & Message Handling
```
Connection Establishment → Authentication → Channel Subscription → Message Sending → Broadcast → UI Update
```

**WebSocket Flow**:

1. **Connection Setup**:
   ```tsx
   // WebSocketContext.tsx
   useEffect(() => {
     if (isAuthenticated && user) {
       const ws = new WebSocket(`ws://localhost:8000/ws/${user.id}`);
       
       ws.onopen = () => {
         setIsConnected(true);
         setSocket(ws);
       };
       
       ws.onmessage = (event) => {
         const message = JSON.parse(event.data);
         handleIncomingMessage(message);
       };
       
       ws.onclose = () => {
         setIsConnected(false);
         // Implement reconnection logic
       };
     }
   }, [isAuthenticated, user]);
   ```

2. **Message Sending**:
   ```tsx
   const sendMessage = async (conversationId, content) => {
     // Send via API for persistence
     const response = await messaging.sendMessage(conversationId, content);
     
     // Also send via WebSocket for real-time delivery
     if (socket && socket.readyState === WebSocket.OPEN) {
       socket.send(JSON.stringify({
         type: 'message',
         conversation_id: conversationId,
         content: content,
         timestamp: new Date().toISOString()
       }));
     }
     
     return response;
   };
   ```

3. **Backend WebSocket Handler**:
   ```python
   # websocket/connection_manager.py
   class ConnectionManager:
       def __init__(self):
           self.active_connections: Dict[int, WebSocket] = {}
       
       async def connect(self, websocket: WebSocket, user_id: int):
           await websocket.accept()
           self.active_connections[user_id] = websocket
       
       async def send_personal_message(self, message: str, user_id: int):
           if user_id in self.active_connections:
               websocket = self.active_connections[user_id]
               await websocket.send_text(message)
       
       async def broadcast_to_conversation(self, message: str, conversation_id: int):
           # Get all participants in conversation
           participants = await get_conversation_participants(conversation_id)
           for participant_id in participants:
               await self.send_personal_message(message, participant_id)
   ```

### 5. Profile Management Flow

#### Profile Update Process
```
Form Changes → Validation → API Request → Database Update → Cache Invalidation → UI Refresh
```

**Implementation**:

1. **Form State Management**:
   ```tsx
   const [profile, setProfile] = useState({
     first_name: user.first_name,
     last_name: user.last_name,
     bio: user.bio,
     skills: user.skills || [],
     availability: user.availability || {}
   });
   
   const [isDirty, setIsDirty] = useState(false);
   
   const handleChange = (field, value) => {
     setProfile(prev => ({ ...prev, [field]: value }));
     setIsDirty(true);
   };
   ```

2. **Save Process**:
   ```tsx
   const handleSave = async () => {
     const response = await profile.update(profile);
     
     if (response.success) {
       // Update user context
       setUser(prev => ({ ...prev, ...response.data }));
       setIsDirty(false);
       showSuccessMessage("Profile updated successfully!");
     } else {
       setError(response.error);
     }
   };
   ```

## Error Handling Data Flow

### API Error Propagation
```
Backend Error → HTTP Status Code → API Client Error Handling → Context Error State → UI Error Display
```

**Error Handling Implementation**:

1. **Backend Error Response**:
   ```python
   # middleware/error_handler.py
   async def error_handling_middleware(request: Request, call_next):
       try:
           response = await call_next(request)
           return response
       except ValidationError as e:
           return JSONResponse(
               status_code=422,
               content={
                   "detail": "Validation failed",
                   "errors": e.errors(),
                   "timestamp": datetime.now(datetime.timezone.utc).isoformat()
               }
           )
       except Exception as e:
           logger.error(f"Unhandled error: {e}")
           return JSONResponse(
               status_code=500,
               content={"detail": "Internal server error"}
           )
   ```

2. **Frontend Error Handling**:
   ```tsx
   // lib/api.ts
   private async request<T>(endpoint: string, options: RequestInit = {}) {
     try {
       const response = await fetch(url, config);
       
       if (!response.ok) {
         const errorData = await response.json();
         return {
           success: false,
           error: errorData.detail || `HTTP ${response.status}`,
           data: null
         };
       }
       
       const data = await response.json();
       return { success: true, data, error: null };
       
     } catch (error) {
       return {
         success: false,
         error: 'Network error occurred',
         data: null
       };
     }
   }
   ```

## Performance Optimization Data Flows

### Caching Strategy
```
Request → Cache Check → Cache Hit/Miss → API Request (if miss) → Cache Update → Response
```

### State Management Optimization
```
Context Change → Subscriber Check → Selective Re-render → DOM Update
```

## Data Validation Flow

### Frontend Validation
```
User Input → Client Validation → Visual Feedback → Server Validation → Error Handling
```

### Backend Validation
```
Request → Pydantic Model → Field Validation → Business Logic → Database Constraints → Response
```

## Security Data Flow

### Authentication Token Flow
```
Login → JWT Generation → Token Storage → Request Headers → Token Validation → Protected Resource Access
```

### Authorization Check Flow
```
Protected Route → Token Extraction → User Role Check → Permission Validation → Access Grant/Deny
```

---

## Data Flow Monitoring

### Logging Points
- API request/response logging
- Database query performance
- WebSocket connection events
- Error occurrences and stack traces
- User action tracking

### Metrics Collection
- Response times per endpoint
- Database query execution time
- WebSocket message throughput
- Error rates by component
- User engagement metrics

---

*Last Updated: July 29, 2025*
*Version: v2.0*