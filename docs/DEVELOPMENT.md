# Seraaj v2 Development Guide

## Quick Start

### Prerequisites

- **Node.js**: 18+ (LTS recommended)
- **Python**: 3.9+
- **PNPM**: 8+ (`npm install -g pnpm`)
- **Git**: Latest version
- **Docker**: Optional, for PostgreSQL in production mode

### Initial Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd seraaj
   ```

2. **Install dependencies**:
   ```bash
   pnpm install
   ```

3. **Set up Python environment**:
   ```bash
   cd apps/api
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   
   pip install -r requirements.txt
   cd ../..
   ```

4. **Environment configuration**:
   ```bash
   # Backend environment
   cp apps/api/.env.example apps/api/.env
   
   # Frontend environment  
   cp apps/web/.env.local.example apps/web/.env.local
   ```

5. **Start development servers**:
   ```bash
   # Terminal 1: Backend API
   cd apps/api
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   
   # Terminal 2: Frontend Web App
   cd apps/web
   pnpm dev
   ```

6. **Access the application**:
   - **Frontend**: http://localhost:3000
   - **API Documentation**: http://localhost:8000/docs
   - **API Health**: http://localhost:8000/health

## Environment Configuration

### Backend Environment (`.env`)

```bash
# Database
DATABASE_URL=sqlite:///./seraaj_dev.db
# For PostgreSQL: postgresql://user:password@localhost:5432/seraaj

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# API Configuration
API_TITLE=Seraaj API
API_VERSION=2.0.0
DEBUG=true

# CORS Settings
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# Email Configuration (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# File Upload
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_DIR=./uploads

# External Services
OPENAI_API_KEY=your-openai-key  # For ML features
STRIPE_SECRET_KEY=your-stripe-key  # For payments
```

### Frontend Environment (`.env.local`)

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_MESSAGING=true
NEXT_PUBLIC_ENABLE_PAYMENTS=false

# External Services
NEXT_PUBLIC_GOOGLE_ANALYTICS_ID=GA-XXXXXXXXX
NEXT_PUBLIC_SENTRY_DSN=your-sentry-dsn

# WebSocket Configuration
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

## Database Setup

### SQLite (Development)

The application uses SQLite by default for development. The database file is automatically created when you start the API server.

**Database location**: `apps/api/seraaj_dev.db`

### PostgreSQL (Production)

For production or testing with PostgreSQL:

1. **Start PostgreSQL with Docker**:
   ```bash
   docker-compose up -d postgres
   ```

2. **Update DATABASE_URL in `.env`**:
   ```bash
   DATABASE_URL=postgresql://seraaj:password@localhost:5432/seraaj_dev
   ```

3. **Run migrations**:
   ```bash
   cd apps/api
   python -c "from database import create_db_and_tables; create_db_and_tables()"
   ```

### Database Seeding

To populate the database with test data:

```bash
cd apps/api

# Basic test opportunities
python create_test_opportunities.py

# Comprehensive seed data
python seed_database.py

# Simple user accounts
python simple_seed.py
```

## Development Workflow

### Backend Development

#### Project Structure
```
apps/api/
├── main.py              # FastAPI application entry point
├── database.py          # Database configuration and connection
├── models/              # SQLModel database models
│   ├── __init__.py     # Model exports
│   ├── user.py         # User and authentication models
│   ├── opportunity.py  # Opportunity-related models
│   ├── application.py  # Application models
│   └── ...             # Other domain models
├── routers/            # API route handlers
│   ├── auth.py         # Authentication endpoints
│   ├── opportunities.py # Opportunity CRUD
│   ├── applications.py # Application management
│   └── ...             # Other feature routers
├── middleware/         # Custom middleware
├── services/           # Business logic services
├── utils/              # Utility functions
└── tests/              # Test suite
```

#### Adding New Endpoints

1. **Create or update router**:
   ```python
   # routers/new_feature.py
   from fastapi import APIRouter, Depends
   from sqlmodel import Session
   
   router = APIRouter(prefix="/v1/new-feature", tags=["new-feature"])
   
   @router.get("/")
   async def list_items(session: Annotated[Session, Depends(get_session)]):
       # Implementation
       pass
   ```

2. **Add router to main application**:
   ```python
   # main.py
   from routers import new_feature
   
   app.include_router(new_feature.router)
   ```

3. **Create database models**:
   ```python
   # models/new_feature.py
   from sqlmodel import SQLModel, Field
   from typing import Optional
   
   class NewFeatureBase(SQLModel):
       name: str
       description: str
   
   class NewFeature(NewFeatureBase, table=True):
       id: Optional[int] = Field(primary_key=True)
   
   class NewFeatureCreate(NewFeatureBase):
       pass
   
   class NewFeatureRead(NewFeatureBase):
       id: int
   ```

4. **Add tests**:
   ```python
   # tests/test_new_feature.py
   def test_create_new_feature(client, auth_headers):
       response = client.post("/v1/new-feature/", 
                            json={"name": "test", "description": "test"},
                            headers=auth_headers)
       assert response.status_code == 201
   ```

#### Running Tests

```bash
cd apps/api

# Run all tests
pytest

# Run specific test file
pytest tests/test_opportunities.py

# Run with coverage
pytest --cov=.

# Run tests with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_auth"
```

#### Database Migrations

For model changes:

1. **Update model definition**
2. **Delete existing database** (development only):
   ```bash
   rm seraaj_dev.db
   ```
3. **Restart server** (auto-creates tables)

For production, implement proper migration system.

### Frontend Development

#### Project Structure
```
apps/web/
├── app/                # Next.js App Router
│   ├── layout.tsx     # Root layout
│   ├── page.tsx       # Landing page
│   ├── globals.css    # Global styles
│   └── [routes]/      # Page routes
├── components/         # React components
│   ├── ui/            # Design system components  
│   ├── layout/        # Layout components
│   └── [features]/    # Feature-specific components
├── contexts/          # React contexts
├── lib/               # Utilities and API client
└── public/            # Static assets
```

#### Creating New Components

1. **Create component file**:
   ```tsx
   // components/ui/PxNewComponent.tsx
   interface PxNewComponentProps {
     variant?: 'primary' | 'secondary';
     children: React.ReactNode;
   }
   
   export function PxNewComponent({ variant = 'primary', children }: PxNewComponentProps) {
     return (
       <div className={`px-component ${variant}`}>
         {children}
       </div>
     );
   }
   ```

2. **Add to design system exports**:
   ```tsx
   // components/ui/index.ts
   export { PxNewComponent } from './PxNewComponent';
   ```

3. **Create stories (if using Storybook)**:
   ```tsx
   // components/ui/PxNewComponent.stories.tsx
   export default {
     title: 'UI/PxNewComponent',
     component: PxNewComponent,
   };
   
   export const Primary = {
     args: {
       variant: 'primary',
       children: 'Example content',
     },
   };
   ```

#### Adding New Pages

1. **Create page file**:
   ```tsx
   // app/new-page/page.tsx
   'use client';
   
   import { AppLayout } from '../../components/layout/AppLayout';
   import { useAuth } from '../../contexts/AuthContext';
   
   export default function NewPage() {
     const { user, isAuthenticated } = useAuth();
     
     if (!isAuthenticated) {
       return <div>Please log in</div>;
     }
     
     return (
       <AppLayout userType={user.role.toLowerCase()}>
         <h1>New Page</h1>
       </AppLayout>
     );
   }
   ```

2. **Add navigation links** (if needed):
   ```tsx
   // components/layout/MobileNav.tsx or AppLayout.tsx
   <Link href="/new-page">New Page</Link>
   ```

#### Styling Guidelines

1. **Use Tailwind classes**:
   ```tsx
   <div className="bg-sun-burst text-ink p-4 rounded-lg">
     Content
   </div>
   ```

2. **Custom CSS for complex styles**:
   ```css
   /* globals.css */
   .custom-animation {
     animation: px-glow 2s infinite;
   }
   ```

3. **Follow design system patterns**:
   ```tsx
   // Good: Using design system
   <PxButton variant="primary" size="lg">Click Me</PxButton>
   
   // Avoid: Custom styling
   <button className="bg-yellow-400 px-8 py-4 text-black">Click Me</button>
   ```

### Testing Strategy

#### Backend Testing

**Unit Tests**: Test individual functions and classes
```python
def test_password_hashing():
    password = "testpassword"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) is True
```

**Integration Tests**: Test API endpoints
```python
def test_create_opportunity(client, auth_headers):
    data = {
        "title": "Test Opportunity",
        "description": "Test description"
    }
    response = client.post("/v1/opportunities/", json=data, headers=auth_headers)
    assert response.status_code == 201
```

**Database Tests**: Test model relationships
```python
def test_user_volunteer_relationship():
    user = User(email="test@example.com")
    volunteer = Volunteer(user=user, bio="Test bio")
    assert volunteer.user.email == "test@example.com"
```

#### Frontend Testing

**Component Tests** (Jest + Testing Library):
```tsx
import { render, screen } from '@testing-library/react';
import { PxButton } from './PxButton';

test('renders button with text', () => {
  render(<PxButton>Click me</PxButton>);
  expect(screen.getByText('Click me')).toBeInTheDocument();
});
```

**Integration Tests** (Cypress):
```tsx
describe('Authentication Flow', () => {
  it('should login user and redirect to feed', () => {
    cy.visit('/auth/login');
    cy.get('[data-testid=email]').type('test@example.com');
    cy.get('[data-testid=password]').type('password');
    cy.get('[data-testid=submit]').click();
    cy.url().should('include', '/feed');
  });
});
```

### Common Development Tasks

#### Adding Authentication to New Page

```tsx
// In page component
const { user, isAuthenticated } = useAuth();

if (!isAuthenticated) {
  return <LoginRequired />;
}
```

#### Making API Calls

```tsx
// Using the API client
const { data, error } = await opportunities.getAll({
  search: searchTerm,
  limit: 20
});

if (error) {
  setError(error);
} else {
  setOpportunities(data);
}
```

#### Adding Real-time Features

```tsx
// Using WebSocket context
const { socket, isConnected, subscribe } = useWebSocket();

useEffect(() => {
  const handleNewMessage = (message) => {
    setMessages(prev => [...prev, message]);
  };
  
  subscribe('new_message', handleNewMessage);
  
  return () => unsubscribe('new_message', handleNewMessage);
}, []);
```

## Troubleshooting

### Common Issues

#### Backend Issues

**ImportError: No module named 'X'**
```bash
cd apps/api
pip install -r requirements.txt
```

**Database connection errors**
- Check DATABASE_URL in .env
- Ensure database file permissions
- Verify PostgreSQL is running (if using)

**JWT token errors**
- Verify SECRET_KEY in .env
- Check token expiration settings
- Clear localStorage in browser

#### Frontend Issues

**Module not found errors**
```bash
pnpm install
# or
rm -rf node_modules package-lock.json
pnpm install
```

**API connection errors**
- Verify NEXT_PUBLIC_API_URL in .env.local
- Check if backend server is running
- Inspect network tab in browser dev tools

**Build errors**
```bash
pnpm build
# Check for TypeScript errors
pnpm type-check
```

### Debug Tools

#### API Debugging
- FastAPI automatic docs: http://localhost:8000/docs
- Database browser for SQLite
- API client tools (Postman, Insomnia)

#### Frontend Debugging
- React Developer Tools browser extension
- Next.js built-in debugging
- Browser network and console tabs

### Performance Optimization

#### Backend Optimization
- Use database indexes for frequent queries
- Implement caching for expensive operations
- Optimize SQLModel queries
- Use async/await properly

#### Frontend Optimization
- Implement proper loading states
- Use React.memo for expensive components
- Optimize image loading with Next.js Image
- Implement code splitting for large features

---

## Production Deployment

### Backend Deployment (AWS Fargate)
1. Build Docker image
2. Push to ECR
3. Update Fargate service
4. Run database migrations

### Frontend Deployment (Vercel)
1. Connect GitHub repository
2. Configure environment variables
3. Deploy automatically on push

### Database Migration (Supabase)
1. Export local data
2. Run migration scripts
3. Import data to production
4. Update connection strings

---

*Last Updated: July 29, 2025*
*Version: v2.0*