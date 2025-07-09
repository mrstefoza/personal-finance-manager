# Personal Finance Manager - Project Context

This folder contains all the architectural decisions, database schemas, and technical specifications for the Personal Finance Manager backend project.

## Project Overview
- **Backend**: Python + FastAPI + PostgreSQL
- **Purpose**: Personal finance management application for individuals and businesses
- **Focus**: User management and authentication system

## Documentation Index

### Architecture & Design
- [Technical Stack](technical-stack.md) - Technology choices and rationale
- [Project Structure](project-structure.md) - Folder organization and architecture
- [Database Design](database-design.md) - Schema and relationships
- [API Design](api-design.md) - Endpoint structure and patterns

### Authentication & Security
- [Authentication Strategy](authentication-strategy.md) - JWT, OAuth, MFA implementation
- [Security Features](security-features.md) - Security measures and best practices
- [User Management](user-management.md) - User types, roles, and permissions

### Development & Operations
- [Development Environment](development-environment.md) - Docker setup, hot reload, API documentation
- [Development Workflow](development-workflow.md) - Coding standards and processes
- [Testing Strategy](testing-strategy.md) - Testing approach and tools
- [Error Handling](error-handling.md) - Error management and logging

### Database Schemas
- [User Tables](database/user-tables.md) - Complete user-related table definitions
- [Indexes](database/indexes.md) - Database performance optimizations

## Key Decisions Made

### Authentication
- ✅ JWT with refresh tokens (15-30 min access, 7-30 days refresh)
- ✅ Email/password + Google OAuth
- ✅ MFA: TOTP + Email (no SMS due to cost)
- ✅ Token revocation via database storage

### Database
- ✅ Raw SQL with asyncpg (no ORM)
- ✅ Alembic for migrations
- ✅ UUID primary keys
- ✅ User types: individual, business

### Security
- ✅ Rate limiting for MFA and login attempts
- ✅ Account lockout after failed attempts
- ✅ Encrypted storage for sensitive data
- ✅ Audit logging for security events

### Development
- ✅ Docker for containerization (2 containers: app + postgres)
- ✅ Environment variables with python-dotenv
- ✅ Hot reload for development
- ✅ Auto-generated Swagger/OpenAPI documentation
- ✅ Structured logging
- ✅ Comprehensive testing with pytest
- ✅ **Automated test execution on every code change**

## Development Environment

### Quick Start
```bash
# Start development environment
docker-compose up -d

# Access API documentation
open http://localhost:8000/docs

# View logs
docker-compose logs -f app
```

### Key Features
- **Hot Reload**: Code changes reflect immediately
- **Swagger UI**: Interactive API documentation at `/docs`
- **Isolated Environment**: No conflicts with local setup
- **Database Persistence**: Data preserved between restarts
- **Automated Testing**: Tests run automatically on code changes

## Testing Strategy

### Automated Test Execution
- **On Every Code Change**: Tests run automatically when files are modified
- **Immediate Feedback**: Get test results within seconds
- **Quality Gate**: Code changes are validated by tests
- **Comprehensive Coverage**: 90%+ coverage target

### Test Categories
- **Unit Tests**: Individual functions and components
- **Integration Tests**: Component interactions
- **End-to-End Tests**: Complete user workflows
- **Security Tests**: Authentication and authorization

### Test Execution
```bash
# Manual test execution
./scripts/dev.sh test

# Automated execution (on code changes)
# Tests run automatically when you save files
```

## Next Steps
1. Set up project structure and dependencies
2. Implement database schema and migrations
3. Build authentication system
4. Add user management features
5. Implement MFA functionality
6. Add Google OAuth integration
7. Create comprehensive test suite
8. **Implement automated test execution on code changes** 