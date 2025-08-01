# Seraaj v2 Documentation

Welcome to the comprehensive documentation for Seraaj v2, a volunteer marketplace platform for the MENA region.

## 📚 Documentation Index

### 🏗️ [Architecture Overview](./ARCHITECTURE.md)
- System architecture and technology stack
- Design system ("8-Bit Optimism") specifications
- User personas and success metrics
- Project structure and directory organization
- Security architecture and performance targets

### 🔌 [API Documentation](./API.md)
- Complete API endpoint reference
- Authentication and authorization
- Data models and database schema
- Request/response formats
- Error handling and status codes
- Testing strategies

### 💻 [Frontend Documentation](./FRONTEND.md)
- Next.js application architecture
- React component structure
- State management with contexts
- API integration patterns
- Design system implementation
- Performance optimizations

### 🔄 [Data Flow Documentation](./DATA_FLOW.md)
- Authentication and user registration flows
- Opportunity discovery and application processes
- Real-time messaging architecture
- Profile management workflows
- Error handling and validation flows
- Performance optimization strategies

### 🛠️ [Development Guide](./DEVELOPMENT.md)
- Local development setup
- Environment configuration
- Database setup and seeding
- Development workflows
- Testing strategies
- Troubleshooting common issues
- Production deployment processes

### ⚠️ [API Issues & Inconsistencies](./API_ISSUES.md)
- Known API problems and conflicts
- Endpoint mapping inconsistencies
- Missing implementations
- Recommended fixes and prioritization
- Workarounds for current issues

## 🚀 Quick Start

If you're new to the project, follow this recommended reading order:

1. **[Architecture Overview](./ARCHITECTURE.md)** - Understand the big picture
2. **[Development Guide](./DEVELOPMENT.md)** - Set up your local environment
3. **[API Issues](./API_ISSUES.md)** - Be aware of current limitations
4. **[Frontend Documentation](./FRONTEND.md)** - Learn the UI architecture
5. **[Data Flow Documentation](./DATA_FLOW.md)** - Understand how data moves through the system

## 🎯 Key Insights from Documentation

### Current Status
- **Frontend**: Well-structured Next.js app with custom design system
- **Backend**: FastAPI with comprehensive models, but many routers disabled
- **Integration**: API endpoint mismatches prevent full functionality
- **Database**: SQLModel setup with good relationships, needs better seeding

### Critical Issues Identified
1. **Phantom API Endpoints**: OpenAPI spec shows endpoints that don't exist
2. **Router Architecture Conflicts**: Two different URL patterns causing confusion
3. **Missing Search Implementation**: Core opportunity discovery is broken
4. **Disabled Router Dependencies**: 80% of planned functionality unavailable

### Immediate Action Items
1. Fix `/v1/opportunities/search` endpoint
2. Update frontend API client to use correct endpoints
3. Enable core routers (websocket, files, admin)
4. Implement basic database seeding

### Architecture Strengths
- **Monorepo Structure**: Clean separation of concerns
- **Type Safety**: Full TypeScript integration
- **Design System**: Consistent "8-Bit Optimism" theme
- **Authentication**: Complete JWT-based auth system
- **Database Design**: Well-structured SQLModel relationships

## 🔧 Development Workflow

### For New Developers
```bash
# 1. Clone and setup
git clone <repo-url>
cd seraaj
pnpm install

# 2. Setup backend
cd apps/api
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# 3. Start servers
# Terminal 1
cd apps/api && uvicorn main:app --reload

# Terminal 2  
cd apps/web && pnpm dev

# 4. Access application
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### For Feature Development
1. **Plan**: Check API Issues doc for known limitations
2. **Backend**: Create/update routers, models, tests
3. **Frontend**: Create components, update API client
4. **Integration**: Test full user flow
5. **Document**: Update relevant documentation

## 📊 Project Metrics

### Codebase Statistics
- **Backend**: ~50 Python files, 15 routers (3 enabled)
- **Frontend**: ~40 TypeScript files, 25+ components
- **Database**: 15+ models with relationships
- **Tests**: Comprehensive test suites for both frontend and backend

### Documentation Coverage
- **Architecture**: ✅ Complete
- **API Reference**: ✅ Complete
- **Frontend Guide**: ✅ Complete
- **Development Setup**: ✅ Complete
- **Data Flows**: ✅ Complete
- **Issue Tracking**: ✅ Complete

## 🤝 Contributing

### Documentation Updates
- Keep documentation in sync with code changes
- Use clear, concise language
- Include code examples where helpful  
- Update the "Last Updated" date

### Code Contributions
- Follow existing patterns and conventions
- Add tests for new functionality
- Update documentation for changes
- Consider impact on existing API contracts

## 📞 Support

### Getting Help
1. **Check Documentation**: Start with relevant doc sections
2. **Review Issues**: Check API_ISSUES.md for known problems
3. **Development Setup**: Follow DEVELOPMENT.md step-by-step
4. **Architecture Questions**: Refer to ARCHITECTURE.md

### Reporting Issues
- **API Problems**: Add to API_ISSUES.md
- **Documentation Gaps**: Create documentation pull requests
- **Bug Reports**: Include steps to reproduce and environment details

---

## 📁 File Organization

```
docs/
├── README.md           # This file - documentation index
├── ARCHITECTURE.md     # System architecture and design
├── API.md             # Complete API reference
├── API_ISSUES.md      # Known issues and inconsistencies
├── FRONTEND.md        # Frontend architecture guide
├── DATA_FLOW.md       # Data flow documentation
└── DEVELOPMENT.md     # Development setup and workflow
```

---

*This documentation was created July 29, 2025 to provide comprehensive understanding of the Seraaj v2 codebase architecture, current status, and development guidelines.*

**Version**: v2.0  
**Last Updated**: July 29, 2025  
**Maintainers**: Development Team