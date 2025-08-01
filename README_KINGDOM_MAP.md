# Kingdom Map of Seraaj v2

This scroll describes the structure of the repository and the purpose of each major component. The file tree below omits `node_modules` directories for brevity.

## File Tree

```text
.
├── CLAUDE.md
├── CONTRIBUTING.md
├── DEMO_ACCOUNTS.md
├── README.md
├── SERVER_STATUS_REPORT.md
├── START_BOTH_SERVERS.md
├── START_SERVERS.bat
├── TECHNICAL_ASSESSMENT_REPORT.md
├── apps
│   ├── api
│   │   ├── README_TESTING.md
│   │   ├── __init__.py
│   │   ├── auth
│   │   │   ├── jwt.py
│   │   │   ├── models.py
│   │   │   └── password_utils.py
│   │   ├── calendar_module
│   │   │   ├── __init__.py
│   │   │   ├── calendar_router.py
│   │   │   └── scheduler.py
│   │   ├── collaboration
│   │   │   ├── __init__.py
│   │   │   └── team_manager.py
│   │   ├── config
│   │   │   ├── __init__.py
│   │   │   └── settings.py
│   │   ├── data
│   │   │   ├── demo_templates.py
│   │   │   └── tour_templates.py
│   │   ├── database
│   │   │   ├── __init__.py
│   │   │   └── optimization.py
│   │   ├── database.py
│   │   ├── debug_api.py
│   │   ├── file_management
│   │   │   ├── __init__.py
│   │   │   └── upload_handler.py
│   │   ├── main.py
│   │   ├── middleware
│   │   │   ├── __init__.py
│   │   │   ├── error_handler.py
│   │   │   ├── loading_states.py
│   │   │   ├── rate_limiter.py
│   │   │   └── request_logging.py
│   │   ├── ml
│   │   │   ├── __init__.py
│   │   │   └── matching_engine.py
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── analytics.py
│   │   │   ├── application.py
│   │   │   ├── base
│   │   │   │   ├── __init__.py
│   │   │   │   ├── enums.py
│   │   │   │   ├── relationships.py
│   │   │   │   └── timestamps.py
│   │   │   ├── base.py
│   │   │   ├── conversation.py
│   │   │   ├── demo_scenario.py
│   │   │   ├── file_upload.py
│   │   │   ├── guided_tour.py
│   │   │   ├── message.py
│   │   │   ├── opportunity.py
│   │   │   ├── organisation.py
│   │   │   ├── push_notification.py
│   │   │   ├── registry.py
│   │   │   ├── review.py
│   │   │   ├── skill_verification.py
│   │   │   ├── types.py
│   │   │   ├── user.py
│   │   │   └── volunteer.py
│   │   ├── monitoring
│   │   │   ├── __init__.py
│   │   │   └── health_checker.py
│   │   ├── package.json
│   │   ├── pwa
│   │   │   ├── __init__.py
│   │   │   ├── manifest_generator.py
│   │   │   ├── offline_storage.py
│   │   │   └── service_worker.py
│   │   ├── pytest.ini
│   │   ├── requirements.txt
│   │   ├── routers
│   │   │   ├── admin.py
│   │   │   ├── applications.py
│   │   │   ├── auth.py
│   │   │   ├── calendar.py
│   │   │   ├── collaboration.py
│   │   │   ├── demo_scenarios.py
│   │   │   ├── files.py
│   │   │   ├── guided_tours.py
│   │   │   ├── match.py
│   │   │   ├── operations.py
│   │   │   ├── opportunities.py
│   │   │   ├── organizations.py
│   │   │   ├── profiles.py
│   │   │   ├── push_notifications.py
│   │   │   ├── pwa.py
│   │   │   ├── reviews.py
│   │   │   ├── system.py
│   │   │   ├── verification.py
│   │   │   └── websocket.py
│   │   ├── seed_data
│   │   │   └── personas.py
│   │   ├── seraaj_dev.db-shm
│   │   ├── seraaj_dev.db-wal
│   │   ├── services
│   │   │   ├── demo_scenario_service.py
│   │   │   ├── guided_tour_service.py
│   │   │   ├── push_notification_service.py
│   │   │   └── unified_seeding_service.py
│   │   ├── simple_server.py
│   │   ├── start_server.py
│   │   ├── startup_sequence.py
│   │   ├── tasks
│   │   │   └── notification_scheduler.py
│   │   ├── test_runner.py
│   │   ├── tests
│   │   │   ├── __init__.py
│   │   │   ├── conftest.py
│   │   │   ├── test_applications.py
│   │   │   ├── test_auth.py
│   │   │   ├── test_demo_scenarios.py
│   │   │   ├── test_guided_tours.py
│   │   │   ├── test_integration.py
│   │   │   ├── test_opportunities.py
│   │   │   ├── test_performance.py
│   │   │   ├── test_push_notifications.py
│   │   │   ├── test_pwa.py
│   │   │   ├── test_search_debug.py
│   │   │   ├── test_server.py
│   │   │   ├── test_verification.py
│   │   │   └── test_websocket.py
│   │   ├── utils
│   │   │   ├── __init__.py
│   │   │   ├── encoding_config.py
│   │   │   ├── response_formatter.py
│   │   │   ├── template_renderer.py
│   │   │   └── validation.py
│   │   ├── verification
│   │   │   ├── __init__.py
│   │   │   ├── skill_verifier.py
│   │   │   └── trust_system.py
│   │   ├── verify_accounts_workflow.py
│   │   └── websocket
│   │       ├── __init__.py
│   │       ├── connection_manager.py
│   │       └── message_handler.py
│   └── web
│       ├── README.md
│       ├── app
│       │   ├── admin
│       │   │   └── page.tsx
│       │   ├── analytics
│       │   │   └── page.tsx
│       │   ├── auth
│       │   │   ├── login
│       │   │   │   └── page.tsx
│       │   │   └── register
│       │   │       └── page.tsx
│       │   ├── demo
│       │   │   └── page.tsx
│       │   ├── favicon.ico
│       │   ├── feed
│       │   │   ├── page-old.tsx
│       │   │   └── page.tsx
│       │   ├── fonts
│       │   │   ├── GeistMonoVF.woff
│       │   │   └── GeistVF.woff
│       │   ├── globals.css
│       │   ├── layout.tsx
│       │   ├── messages
│       │   │   └── page.tsx
│       │   ├── onboarding
│       │   │   └── page.tsx
│       │   ├── org
│       │   │   └── dashboard
│       │   │       └── page.tsx
│       │   ├── page.tsx
│       │   ├── profile
│       │   │   └── page.tsx
│       │   └── search
│       │       └── page.tsx
│       ├── components
│       │   ├── admin
│       │   │   └── AdminConsole.tsx
│       │   ├── analytics
│       │   │   └── AnalyticsDashboard.tsx
│       │   ├── demo
│       │   │   └── SeedDataLoader.tsx
│       │   ├── feed
│       │   │   └── LiveActivityFeed.tsx
│       │   ├── landing
│       │   │   └── HeroSearch.tsx
│       │   ├── layout
│       │   │   ├── AppLayout.tsx
│       │   │   └── MobileNav.tsx
│       │   ├── messaging
│       │   │   └── MessageInterface.tsx
│       │   ├── notifications
│       │   │   └── NotificationCenter.tsx
│       │   ├── onboarding
│       │   │   ├── OnboardingFlow.tsx
│       │   │   └── steps
│       │   │       ├── CompletionStep.tsx
│       │   │       ├── PreferencesStep.tsx
│       │   │       ├── ProfileStep.tsx
│       │   │       ├── UserTypeStep.tsx
│       │   │       └── WelcomeStep.tsx
│       │   ├── profile
│       │   │   ├── ProfileEditor.tsx
│       │   │   ├── ProfileManagement.tsx
│       │   │   ├── ProfilePreview.tsx
│       │   │   └── ProfileVersionHistory.tsx
│       │   ├── search
│       │   │   ├── AdvancedSearch.tsx
│       │   │   ├── SavedSearches.tsx
│       │   │   └── SearchResults.tsx
│       │   └── ui
│       │       ├── PxBadge.tsx
│       │       ├── PxButton.tsx
│       │       ├── PxCard.tsx
│       │       ├── PxChip.tsx
│       │       ├── PxInput.tsx
│       │       ├── PxLanguageToggle.tsx
│       │       ├── PxModal.tsx
│       │       ├── PxProgress.tsx
│       │       ├── PxSkeleton.tsx
│       │       ├── PxSwipeCard.tsx
│       │       ├── PxThemeToggle.tsx
│       │       ├── PxTimeline.tsx
│       │       ├── PxToast.tsx
│       │       └── index.ts
│       ├── contexts
│       │   ├── AuthContext.tsx
│       │   ├── LanguageContext.tsx
│       │   ├── ThemeContext.tsx
│       │   └── WebSocketContext.tsx
│       ├── next.config.mjs
│       ├── package.json
│       ├── postcss.config.mjs
│       ├── tailwind.config.ts
│       └── tsconfig.json
├── demo.md
├── docker-compose.yml
├── docs
│   ├── API.md
│   ├── API_ISSUES.md
│   ├── ARCHITECTURE.md
│   ├── CROSS_PLATFORM_SETUP.md
│   ├── CURRENT_SYSTEM_STATE.md
│   ├── DATA_FLOW.md
│   ├── DEVELOPMENT.md
│   ├── FRONTEND.md
│   └── README.md
├── kingdom_map.txt
├── package-lock.json
├── package.json
├── packages
│   └── ui
│       ├── package.json
│       ├── src
│       │   ├── components
│       │   │   ├── PxButton.tsx
│       │   │   ├── PxCard.tsx
│       │   │   ├── PxChip.tsx
│       │   │   ├── PxInput.tsx
│       │   │   └── PxProgress.tsx
│       │   └── index.ts
│       ├── tailwind.config.js
│       └── tsconfig.json
├── pnpm-workspace.yaml
├── pyproject.toml
├── seraaj_dev.db-shm
├── seraaj_dev.db-wal
├── setup-database.py
├── start-dev-servers.bat
├── start-dev-servers.sh
├── start-dev.bat
├── start-dev.sh
├── start-seraaj.bat
├── start-servers.py
├── start-servers.sh
├── start_seraaj.py
├── test_auth.py
└── turbo.json

60 directories, 230 files
```

## Strongholds and their Dependencies

### `apps/api` – FastAPI backend
- **Purpose**: Implements the API server with routes for authentication, opportunities, messaging, notifications and more. Contains models, services, and tests.
- **Key dependencies** (from `requirements.txt`):
  - `fastapi`, `uvicorn[standard]`, `sqlmodel`, `psycopg2-binary`, `alembic`, `pydantic[email]`, `python-jose[cryptography]`, `passlib[bcrypt]`, `python-multipart`, `aiofiles`, `Pillow`, `redis`, `pytest`, `pytest-asyncio`, `ruff`, `mypy`

### `apps/web` – Next.js frontend
- **Purpose**: Provides the user-facing web application using React, Tailwind CSS and the 8-Bit Optimism design system.
- **Key dependencies** (from `package.json`):
  - Runtime: `next`, `react`, `react-dom`, `clsx`
  - Dev: `@tailwindcss/forms`, `@types/node`, `@types/react`, `@types/react-dom`, `eslint`, `eslint-config-next`, `postcss`, `tailwindcss`, `typescript`

### `packages/ui` – 8‑Bit Optimism design system
- **Purpose**: Shared React component library with Tailwind styling used across the project.
- **Key dependencies** (from `package.json`):
  - Runtime: `react`, `tailwindcss`, `clsx`
  - Dev: `@types/react`, `tsup`, `typescript`, `eslint`

### `docs`
- **Purpose**: Documentation for architecture, API, frontend, development workflow and more.

### Root scripts and configuration
- **Purpose**: Shell/Bat scripts and Python utilities to start development servers (`start-servers.py`, `start-dev.sh`), manage the database (`setup-database.py`), and configure the monorepo (`package.json`, `pyproject.toml`, `pnpm-workspace.yaml`). The `Makefile` includes helper targets (`seed`, `lint`, `test`, `makemigrations`, `migrate`).
- **Dependencies**: Node.js 18+, Python 3.11+, PNPM, Docker for local PostgreSQL.

---

This map provides an overview of the lands within the repository and the forces that power each fortress.
