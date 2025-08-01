# Seraaj v2 🌅

> Turn goodwill into impact in two clicks.

A two-sided volunteer marketplace for under-resourced nonprofits in the MENA region.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- PNPM 8+
- Docker (for PostgreSQL)

### Development Setup

1. **Clone and install dependencies**
   ```bash
   git clone <repo-url>
   cd seraaj
   pnpm install
   ```

2. **Start PostgreSQL**
   ```bash
   docker-compose up -d postgres
   ```

3. **Set up environment files**
   ```bash
   cp apps/api/.env.example apps/api/.env
   cp apps/web/.env.local.example apps/web/.env.local
   ```

4. **Install Python dependencies**
   ```bash
   cd apps/api
   pip install -r requirements.txt
   cd ../..
   ```

5. **Start development servers**
   ```bash
   # Terminal 1: Start API
   cd apps/api
   uvicorn main:app --reload --host 0.0.0.0 --port 8000

   # Terminal 2: Start Web App
   cd apps/web
   pnpm dev
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/v1/docs

## 🏗️ Architecture

```
seraaj/
├── apps/
│   ├── web/           # Next.js 14 frontend
│   └── api/           # FastAPI backend
├── packages/
│   └── ui/            # 8-Bit Optimism design system
└── docs/              # Documentation
```

## 🎨 Design System: "8-Bit Optimism"

- **Colors**: Sun-Burst yellow (#FFD749), Ink (#101028), Pixel Coral (#FF6B94)
- **Typography**: Press Start 2P (headings), Inter (body)
- **Grid**: 12 columns, 8px base unit
- **Corners**: Clipped corners with 8px offset
- **Motion**: Steps(8) easing, 240ms duration

## 🔑 Key Features

### For Volunteers
- Personalized discovery feed
- One-click application flow
- In-app messaging

### For NGO Admins
- Lean applicant-tracking board
- ML-driven candidate ranking
- "Recommended" volunteer in <10s

### For Platform Moderators
- User management tools
- Analytics dashboard
- Content moderation

## 📊 Success Metrics

- **Volunteer**: Find and apply to relevant opportunity in ≤120s
- **NGO**: Post role and see "Recommended" candidate in ≤10s

## 📚 Documentation

Comprehensive documentation is available in the [`docs/`](./docs/) directory:

- **[Architecture Overview](./docs/ARCHITECTURE.md)** - System design and technology stack
- **[API Reference](./docs/API.md)** - Complete API endpoint documentation
- **[Frontend Guide](./docs/FRONTEND.md)** - React/Next.js architecture
- **[Development Setup](./docs/DEVELOPMENT.md)** - Local development guide
- **[Data Flow](./docs/DATA_FLOW.md)** - How data moves through the system
- **[API Issues](./docs/API_ISSUES.md)** - Known issues and workarounds

## 🧪 Testing

```bash
# Run all tests
pnpm test

# Run specific app tests
pnpm --filter @seraaj/web test
pnpm --filter @seraaj/api test

# Backend tests
cd apps/api && pytest

# Frontend tests
cd apps/web && pnpm test
```

## 🚢 Deployment

- **Frontend**: Vercel
- **Backend**: AWS Fargate
- **Database**: Supabase PostgreSQL

See [Development Guide](./docs/DEVELOPMENT.md#production-deployment) for detailed deployment instructions.

## 📝 Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development guidelines.

For development setup and workflow, refer to the [Development Guide](./docs/DEVELOPMENT.md).

---

**Seraaj v2.0** • Built with 8-Bit Optimism ✨