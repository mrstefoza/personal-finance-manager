# Personal Finance Manager - Project Context

## Overview
This document serves as a central reference for all project context files. Each file contains detailed information about specific aspects of the Personal Finance Manager application.

## Context Files Index

### 📋 [README.md](README.md)
**Purpose**: Project overview and getting started guide
**Contents**: 
- Project description and features
- Quick start instructions
- Technology stack overview
- Development setup guide

### 🏗️ [project-structure.md](project-structure.md)
**Purpose**: Detailed project organization and file structure
**Contents**:
- Directory layout and organization
- Module structure and responsibilities
- Code organization principles
- File naming conventions

### ⚙️ [technical-stack.md](technical-stack.md)
**Purpose**: Technology choices and architecture decisions
**Contents**:
- Backend framework (FastAPI)
- Database (PostgreSQL)
- Authentication (JWT, OAuth)
- Frontend technologies
- Development tools and libraries

### 🗄️ [database-design.md](database-design.md)
**Purpose**: Database schema and data modeling
**Contents**:
- Table structures and relationships
- Indexes and constraints
- Data types and validations
- Migration strategies

### 🔐 [authentication-strategy.md](authentication-strategy.md)
**Purpose**: Authentication and security implementation
**Contents**:
- JWT token strategy
- OAuth integration (Google)
- Multi-factor authentication (TOTP, Email)
- Security measures and best practices
- API endpoint specifications

### 🧪 [testing-strategy.md](testing-strategy.md)
**Purpose**: Comprehensive testing approach and guidelines
**Contents**:
- Testing philosophy and workflow
- Test categories (Unit, Integration, E2E, Security)
- Test structure and organization
- Coverage requirements (90%+)
- Automated test execution
- Quality gates and best practices

### 🛠️ [development-environment.md](development-environment.md)
**Purpose**: Development setup and workflow
**Contents**:
- Docker environment configuration
- Development tools and scripts
- Hot reload setup
- Database management
- Debugging and logging

### 📁 [database/](database/)
**Purpose**: Database-related files and scripts
**Contents**:
- SQL migration files
- Database initialization scripts
- Schema definitions
- Seed data

## Key Project Information

### Application Type
Personal Finance Manager supporting both individual and business users with comprehensive authentication, MFA, and financial management features.

### Core Features
- **User Management**: Registration, login, profile management
- **Authentication**: JWT tokens, Google OAuth, Multi-factor authentication
- **MFA Support**: TOTP (Google Authenticator), Email codes, Backup codes
- **Security**: Password hashing, rate limiting, account lockout
- **Database**: PostgreSQL with encrypted sensitive data

### Development Status
- ✅ Basic infrastructure implemented
- ✅ User registration and authentication
- ✅ JWT token management
- ✅ TOTP MFA setup and verification
- ✅ Frontend demo with MFA flows
- ⚠️ Testing coverage needs improvement
- 🔄 Google OAuth implementation pending
- 🔄 Email MFA implementation pending

### Current Issues
- Limited test coverage (only 4 basic tests)
- Missing integration tests for MFA flows
- No automated test execution on code changes
- Manual debugging required for production issues

### Next Priorities
1. Implement comprehensive test suite according to testing strategy
2. Add automated test execution on code changes
3. Complete Google OAuth integration
4. Implement email MFA with actual email sending
5. Add proper error handling and validation

## Quick Reference Commands

### Development
```bash
./scripts/dev.sh start      # Start development environment
./scripts/dev.sh test       # Run tests
./scripts/dev.sh logs       # View logs
./scripts/dev.sh restart    # Restart containers
```

### Testing
```bash
./scripts/dev.sh test -v                    # Verbose test output
./scripts/dev.sh test --cov=app             # With coverage
./scripts/dev.sh test tests/test_api/       # API tests only
```

### Database
```bash
./scripts/dev.sh db                         # Access database
docker-compose exec postgres psql -U pfm_user -d pfm_dev  # Direct DB access
```

## Architecture Overview

```
Frontend (Vanilla JS) ←→ FastAPI Backend ←→ PostgreSQL Database
                              ↓
                        Redis (Future: Caching)
                              ↓
                        External Services (Google OAuth, Email)
```

## Security Features

- **Password Security**: bcrypt hashing with cost factor 12
- **Token Security**: JWT with HMAC-SHA256 signing
- **MFA Security**: TOTP secrets encrypted at rest
- **Rate Limiting**: Failed login attempts and MFA attempts
- **Session Management**: Device tracking and session limits

## Testing Requirements

- **Coverage Target**: 90%+ overall coverage
- **Test Categories**: Unit, Integration, E2E, Security
- **Automation**: Tests run on every code change
- **Quality Gates**: All tests pass, coverage threshold met

---

*This context file serves as the single reference point for all project documentation. When working on the project, refer to the specific context files for detailed information about each aspect.* 