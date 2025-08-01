# Seraaj v2 Architecture Documentation

## Overview

Seraaj v2 is a **two-sided volunteer marketplace** designed for under-resourced nonprofits in the MENA region. The platform connects volunteers with organizations through a modern, responsive web application built with performance and user experience as primary concerns.

## Project Vision

> "Turn goodwill into impact in two clicks."

**Core Mission**: Enable meaningful volunteer connections in the MENA region by reducing friction between willing volunteers and organizations that need help.

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Database      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (SQLite/PG)   │
│   Port: 3000    │    │   Port: 8000    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack

#### Frontend (`apps/web/`)
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS with custom "8-Bit Optimism" design system
- **State Management**: React Context (Auth, Language, Theme, WebSocket)
- **Package Manager**: PNPM

#### Backend (`apps/api/`)
- **Framework**: FastAPI (Python)
- **Database ORM**: SQLModel (built on SQLAlchemy)
- **Authentication**: JWT with refresh tokens
- **Validation**: Pydantic v2
- **Database**: SQLite (development) → PostgreSQL (production)

#### Deployment Architecture
- **Frontend**: Vercel
- **Backend**: AWS Fargate
- **Database**: Supabase PostgreSQL
- **Package Management**: PNPM Workspace (monorepo)

## Design System: "8-Bit Optimism"

### Color Palette
- **Primary**: Sun-Burst Yellow (`#FFD749`)
- **Secondary**: Ink (`#101028`)
- **Accent**: Pixel Coral (`#FF6B94`)
- **Additional**: Neon Cyan, Electric Teal, Deep Indigo, Pixel Lavender

### Typography
- **Headings**: Press Start 2P (pixel font)
- **Body Text**: Inter (clean, readable)

### Design Principles
- **Grid System**: 12 columns, 8px base unit
- **Corners**: Clipped corners with 8px offset
- **Motion**: Steps(8) easing, 240ms duration
- **Accessibility**: High contrast, keyboard navigation, screen reader support

## User Personas & Flows

### 1. Volunteers
**Goal**: Find and apply to relevant opportunities quickly

**Success Metric**: Complete application in ≤120 seconds

**Key Features**:
- Personalized discovery feed
- One-click application flow
- In-app messaging with organizations
- Profile management and skill tracking

### 2. NGO Administrators
**Goal**: Post roles and identify best-fit candidates efficiently

**Success Metric**: See "Recommended" candidate in ≤10 seconds

**Key Features**:
- Lean applicant-tracking board
- ML-driven candidate ranking
- Quick organization profile setup
- Application management dashboard

### 3. Platform Moderators
**Goal**: Maintain platform quality and support users

**Key Features**:
- User management tools
- Analytics dashboard
- Content moderation interface
- System health monitoring

## Directory Structure

```
seraaj/
├── apps/
│   ├── web/                    # Next.js frontend application
│   │   ├── app/               # App Router pages
│   │   ├── components/        # React components
│   │   ├── contexts/          # React contexts
│   │   ├── lib/              # Utilities and API client
│   │   └── package.json
│   └── api/                   # FastAPI backend application
│       ├── models/           # SQLModel database models
│       ├── routers/          # FastAPI route handlers
│       ├── middleware/       # Custom middleware
│       ├── services/         # Business logic services
│       ├── utils/           # Utility functions
│       ├── tests/           # Test suite
│       └── main.py          # FastAPI application entry
├── packages/
│   └── ui/                   # Shared UI components (planned)
├── docs/                     # Project documentation
├── docker-compose.yml        # Development containers
├── pnpm-workspace.yaml      # Monorepo configuration
└── turbo.json               # Build system configuration
```

## Core Data Models

### User Management
- **User**: Base user account (email, password, role)
- **Volunteer**: Extended volunteer profile (skills, availability, experience)
- **Organisation**: NGO/nonprofit organization profile

### Opportunity Management
- **Opportunity**: Volunteer positions posted by organizations
- **Application**: Volunteer applications to opportunities
- **Review**: Performance reviews and feedback

### Communication
- **Conversation**: Message threads between users
- **Message**: Individual messages with read receipts
- **Notification**: System and push notifications

### System Features
- **Analytics**: User activity and platform metrics
- **FileUpload**: Document and image management
- **Payment**: Donation and premium feature handling (future)

## Security Architecture

### Authentication Flow
1. **Registration**: Email/password with role selection
2. **Login**: JWT access token (15min) + refresh token (7 days)
3. **Authorization**: Role-based access control (RBAC)
4. **Token Refresh**: Automatic refresh on API calls

### Security Measures
- **Password Hashing**: Bcrypt with salt
- **JWT Validation**: Signature verification and expiration checks
- **CORS Configuration**: Restricted origins for API access
- **Rate Limiting**: Request throttling per IP
- **Input Validation**: Pydantic models for all API inputs

## Development Environment

### Prerequisites
- Node.js 18+
- Python 3.9+
- PNPM 8+
- Docker (for PostgreSQL)

### Local Development Ports
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432 (PostgreSQL) or local SQLite file

## Performance Targets

### Frontend Performance
- **First Contentful Paint**: <1.5s
- **Largest Contentful Paint**: <2.5s
- **Cumulative Layout Shift**: <0.1
- **Time to Interactive**: <3s

### Backend Performance
- **API Response Time**: <200ms (95th percentile)
- **Database Query Time**: <100ms average
- **Authentication**: <50ms token validation
- **Concurrent Users**: 1000+ supported

## Monitoring & Analytics

### Application Monitoring
- **Error Tracking**: Sentry integration
- **Performance Monitoring**: Real User Monitoring (RUM)
- **API Monitoring**: Response times and error rates
- **Database Monitoring**: Query performance and connection health

### Business Analytics
- **User Engagement**: Registration, login, application completion rates
- **Platform Health**: Opportunity posting rates, application success rates
- **Performance Metrics**: Time-to-application, time-to-recommendation

---

*Last Updated: July 29, 2025*
*Version: v2.0*