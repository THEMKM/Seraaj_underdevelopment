# Seraaj v2 Frontend Documentation

## Overview

The Seraaj frontend is a **Next.js 14** application built with TypeScript, Tailwind CSS, and the custom "8-Bit Optimism" design system. It provides a responsive, accessible, and performant user experience for volunteers and organizations.

## Technology Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript 5+
- **Styling**: Tailwind CSS + Custom CSS
- **State Management**: React Context API
- **HTTP Client**: Native Fetch API with custom wrapper
- **Build Tool**: Next.js built-in bundler
- **Package Manager**: PNPM

## Project Structure

```
apps/web/
├── app/                          # Next.js App Router
│   ├── globals.css              # Global styles + Tailwind
│   ├── layout.tsx               # Root layout with providers
│   ├── page.tsx                 # Landing page
│   ├── auth/
│   │   ├── login/page.tsx       # Login page
│   │   └── register/page.tsx    # Registration page
│   ├── feed/page.tsx            # Main opportunity feed
│   ├── profile/page.tsx         # User profile management
│   ├── messages/page.tsx        # Messaging interface
│   ├── search/page.tsx          # Advanced search
│   ├── analytics/page.tsx       # Analytics dashboard
│   ├── admin/page.tsx           # Admin console
│   ├── demo/page.tsx            # Demo/seed data page
│   ├── onboarding/page.tsx      # User onboarding flow
│   └── org/
│       └── dashboard/page.tsx   # Organization dashboard
├── components/                   # React components
│   ├── ui/                      # Design system components
│   ├── layout/                  # Layout components
│   ├── auth/                    # Authentication components
│   ├── feed/                    # Feed-related components
│   ├── messaging/               # Chat/messaging components
│   ├── profile/                 # Profile management
│   ├── analytics/               # Dashboard components
│   ├── admin/                   # Admin interface
│   ├── demo/                    # Demo/development tools
│   ├── onboarding/              # User onboarding
│   └── landing/                 # Landing page components
├── contexts/                     # React contexts
│   ├── AuthContext.tsx          # Authentication state
│   ├── LanguageContext.tsx      # i18n/localization
│   ├── ThemeContext.tsx         # Dark/light theme
│   └── WebSocketContext.tsx     # Real-time connections
├── lib/                         # Utilities and libraries
│   ├── api.ts                   # API client
│   └── seedData.ts              # Development seed data
└── [config files]
```

## Design System: "8-Bit Optimism"

### Core Components (`components/ui/`)

#### **PxButton**
Pixel-styled button with multiple variants:
```tsx
<PxButton variant="primary" size="lg" onClick={handleClick}>
  Click Me
</PxButton>
```

**Variants**: `primary`, `secondary`, `outline`, `ghost`
**Sizes**: `sm`, `md`, `lg`

#### **PxCard**
Container component with pixel-perfect borders:
```tsx
<PxCard className="p-6" variant="highlighted">
  <h3>Card Title</h3>
  <p>Card content</p>
</PxCard>
```

#### **PxSwipeCard**
Interactive card component for the opportunity feed:
```tsx
<PxSwipeCard onSwipe={handleSwipe}>
  <OpportunityDetails />
</PxSwipeCard>
```

#### **PxChip**
Small tags for skills, categories, etc.:
```tsx
<PxChip size="sm" variant="primary">
  JavaScript
</PxChip>
```

#### **Additional Components**
- `PxInput`: Form input with pixel styling
- `PxModal`: Modal dialog with overlay
- `PxBadge`: Status indicators
- `PxProgress`: Progress bars and loading states
- `PxSkeleton`: Loading placeholders
- `PxToast`: Notification system
- `PxTimeline`: Step-by-step progress
- `PxThemeToggle`: Dark/light mode switcher
- `PxLanguageToggle`: Language selection

### Color System

```css
:root {
  /* Primary Colors */
  --sun-burst: #FFD749;
  --ink: #101028;
  --pixel-coral: #FF6B94;
  
  /* Secondary Colors */
  --neon-cyan: #00FFFF;
  --electric-teal: #00CCAA;
  --deep-indigo: #1A1B3A;
  --pixel-lavender: #B794F6;
  
  /* Semantic Colors */
  --success: #10B981;
  --warning: #F59E0B;
  --error: #EF4444;
  --info: #3B82F6;
}
```

### Typography

```css
/* Headings - Pixel Font */
.font-pixel {
  font-family: 'Press Start 2P', monospace;
  line-height: 1.6;
}

/* Body Text - Clean Font */
.font-body {
  font-family: 'Inter', sans-serif;
}
```

### Custom Animations

```css
@keyframes px-glow {
  0%, 100% { box-shadow: 0 0 5px var(--sun-burst); }
  50% { box-shadow: 0 0 20px var(--sun-burst), 0 0 30px var(--sun-burst); }
}

@keyframes px-fade-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
```

## State Management

### Authentication Context (`AuthContext.tsx`)

Manages user authentication state and provides auth-related functions:

```tsx
interface AuthContextType {
  user: User | null;
  login: (credentials: LoginCredentials) => Promise<ApiResponse<AuthResponse>>;
  logout: () => void;
  register: (userData: RegisterData) => Promise<ApiResponse<AuthResponse>>;
  isAuthenticated: boolean;
  loading: boolean;
}
```

**Key Features**:
- JWT token management
- Automatic token refresh
- Persistent login state
- Role-based access control

**Usage**:
```tsx
const { user, login, logout, isAuthenticated } = useAuth();

// Login flow
const handleLogin = async (credentials) => {
  const result = await login(credentials);
  if (result.success) {
    router.push('/feed');
  }
};
```

### Language Context (`LanguageContext.tsx`)

Provides internationalization (i18n) support:

```tsx
interface LanguageContextType {
  language: 'en' | 'ar';
  setLanguage: (lang: 'en' | 'ar') => void;
  t: (key: string) => string;
  direction: 'ltr' | 'rtl';
}
```

**Features**:
- English/Arabic language switching
- RTL support for Arabic
- Translation function with fallbacks
- Persistent language preference

### Theme Context (`ThemeContext.tsx`)

Manages dark/light theme switching:

```tsx
interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
}
```

### WebSocket Context (`WebSocketContext.tsx`)

Handles real-time connections for messaging:

```tsx
interface WebSocketContextType {
  socket: WebSocket | null;
  isConnected: boolean;
  sendMessage: (message: any) => void;
  subscribe: (event: string, callback: Function) => void;
  unsubscribe: (event: string, callback: Function) => void;
}
```

## API Integration

### API Client (`lib/api.ts`)

Centralized HTTP client with authentication and error handling:

```tsx
class ApiClient {
  private baseURL: string;
  private accessToken: string | null;
  private refreshToken: string | null;

  // Authentication methods
  async login(credentials: LoginCredentials): Promise<ApiResponse<AuthResponse>>
  async register(userData: RegisterData): Promise<ApiResponse<AuthResponse>>
  async logout(): Promise<ApiResponse<any>>
  async getCurrentUser(): Promise<ApiResponse<User>>

  // Opportunity methods
  async getOpportunities(params?: SearchParams): Promise<ApiResponse<Opportunity[]>>
  async getOpportunity(id: string): Promise<ApiResponse<Opportunity>>
  async applyToOpportunity(id: string, data?: any): Promise<ApiResponse<any>>

  // Profile methods
  async updateProfile(data: any): Promise<ApiResponse<any>>
  async getMyApplications(): Promise<ApiResponse<Application[]>>

  // Organization methods
  async getMyOrganization(): Promise<ApiResponse<Organization>>
  async createOpportunity(data: any): Promise<ApiResponse<Opportunity>>

  // Messaging methods
  async getConversations(): Promise<ApiResponse<Conversation[]>>
  async sendMessage(conversationId: string, content: string): Promise<ApiResponse<Message>>
}
```

**Key Features**:
- Automatic JWT token refresh
- Request/response interceptors
- Standardized error handling
- TypeScript type safety
- Retry logic for failed requests

### API Response Types

```tsx
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'VOLUNTEER' | 'ORG_ADMIN' | 'SUPERADMIN';
  is_verified: boolean;
  created_at: string;
}

interface Opportunity {
  id: string;
  title: string;
  description: string;
  skills_required: string[];
  location: string;
  is_remote: boolean;
  status: string;
  org_id: string;
  created_at: string;
  start_date: string;
  end_date: string;
  min_hours: number;
}
```

## Page Architecture

### Landing Page (`app/page.tsx`)

**Purpose**: Marketing page and entry point
**Features**:
- Hero section with search
- Feature highlights
- Authentication status awareness
- Theme/language toggles

### Authentication Pages

#### Login (`app/auth/login/page.tsx`)
```tsx
export default function LoginPage() {
  const { login } = useAuth();
  const [credentials, setCredentials] = useState({});
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await login(credentials);
    if (result.success) {
      router.push('/feed');
    } else {
      setError(result.error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Login form */}
    </form>
  );
}
```

#### Register (`app/auth/register/page.tsx`)
Similar structure with additional fields for user registration.

### Main Application Pages

#### Opportunity Feed (`app/feed/page.tsx`)

**Purpose**: Main application interface for discovering opportunities

**Key Features**:
- Swipe-based opportunity discovery
- List view alternative  
- Real-time filters (remote, skills, search)
- Authentication-required access
- Loading states and error handling

**State Management**:
```tsx
const [currentOpportunities, setCurrentOpportunities] = useState<Opportunity[]>([]);
const [currentIndex, setCurrentIndex] = useState(0);
const [viewMode, setViewMode] = useState<'swipe' | 'list'>('swipe');
const [loading, setLoading] = useState(true);
const [filters, setFilters] = useState({
  remote: false,
  skills: [],
  search: ''
});
```

**API Integration**:
```tsx
const fetchOpportunities = async () => {
  setLoading(true);
  const response = await opportunities.getAll(filters);
  if (response.success) {
    setCurrentOpportunities(response.data);
  } else {
    setError(response.error);
  }
  setLoading(false);
};
```

#### Profile Management (`app/profile/page.tsx`)

**Purpose**: User profile editing and management
**Features**:
- Profile form with validation
- Skill management
- Availability settings
- Profile completion tracking

#### Messaging Interface (`app/messages/page.tsx`)

**Purpose**: Real-time messaging between users
**Features**:
- Conversation list
- Message threads
- WebSocket integration
- File attachments (planned)

### Layout Components

#### App Layout (`components/layout/AppLayout.tsx`)

Main application shell with navigation:

```tsx
interface AppLayoutProps {
  children: React.ReactNode;
  userType: 'volunteer' | 'organization' | 'admin';
}

export function AppLayout({ children, userType }: AppLayoutProps) {
  return (
    <div className="min-h-screen bg-white dark:bg-dark-bg">
      <Header userType={userType} />
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
      <MobileNav userType={userType} />
    </div>
  );
}
```

#### Mobile Navigation (`components/layout/MobileNav.tsx`)

Bottom navigation bar for mobile devices with role-based menu items.

## Performance Optimizations

### Code Splitting
- Automatic route-based code splitting via Next.js
- Dynamic imports for heavy components
- Lazy loading for non-critical features

### Image Optimization
- Next.js Image component for automatic optimization
- WebP format support
- Responsive image sizing

### State Management Optimization
- Context splitting to prevent unnecessary re-renders
- useMemo and useCallback for expensive operations
- Debounced search inputs

### Bundle Optimization
- Tree shaking for unused code
- Dynamic imports for feature flags
- Compressed assets in production

## Accessibility Features

### Keyboard Navigation
- Tab order for all interactive elements
- Focus management in modals
- Keyboard shortcuts for power users

### Screen Reader Support
- Semantic HTML structure
- ARIA labels and descriptions
- Live regions for dynamic content

### Visual Accessibility
- High contrast color combinations
- Scalable font sizes
- Color-blind friendly palette

## Development Workflow

### Local Development
```bash
cd apps/web
pnpm dev          # Start development server
pnpm build        # Production build
pnpm lint         # ESLint check
pnpm type-check   # TypeScript check
```

### Component Development
1. Create component in appropriate directory
2. Add TypeScript interfaces
3. Implement with proper styling
4. Add to design system exports
5. Document usage examples

### State Management Pattern
1. Create context for domain-specific state
2. Provide context at appropriate level
3. Use custom hooks for context consumption
4. Implement error boundaries

---

*Last Updated: July 29, 2025*
*Version: v2.0*