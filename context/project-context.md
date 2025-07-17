# Personal Finance Manager - Project Context

This folder contains all the architectural decisions, database schemas, and technical specifications for the Personal Finance Manager backend project.

## 🤖 AI Assistant Reminder
**IMPORTANT**: When working on this project, always update this context file when:
- Adding new features or functionality
- Changing deployment procedures
- Encountering and solving new issues
- Updating dependencies or configurations
- Adding new scripts or tools
- Changing database schema or migration procedures
- Updating security measures or authentication flows

**Keep this context current and comprehensive for future reference and troubleshooting.**

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
- ✅ Email/password + Firebase Authentication (Google OAuth)
- ✅ MFA: TOTP + Email (no SMS due to cost)
- ✅ Token revocation via database storage
- ✅ Firebase Admin SDK for secure token verification

### Database
- ✅ Raw SQL with asyncpg (no ORM)
- ✅ Alembic for migrations
- ✅ UUID primary keys
- ✅ User types: individual, business
- ✅ Firebase UID support for OAuth users

### Security
- ✅ Rate limiting for MFA and login attempts
- ✅ Account lockout after failed attempts
- ✅ Encrypted sensitive data (TOTP secrets, backup codes)
- ✅ Audit trails for all actions
- ✅ Firebase token verification on backend

### Development & Deployment
- ✅ Docker Compose for development and production
- ✅ Hot reload for development
- ✅ Automated migration system with Alembic
- ✅ Helper scripts for common tasks

## Database Migration System

### Overview
The project uses **Alembic** for database migrations with a hybrid approach:
- **Initial setup**: SQL scripts in `sql/init/` create base schema on fresh database
- **Schema changes**: Alembic migrations handle all subsequent schema changes
- **Version tracking**: Alembic tracks applied migrations in `alembic_version` table

### Migration Files
- **Location**: `alembic/versions/`
- **Current migrations**:
  - `0001_initial_schema.py` - Base schema (users, sessions, MFA tables)
  - `0002_add_mfa_sessions.py` - MFA session tracking
  - `0003_add_firebase_uid.py` - Firebase UID support for OAuth
- **Format**: Raw SQL with upgrade/downgrade functions

### Deployment Workflow

#### Fresh Server Setup
```bash
# 1. Clone and setup
git clone <repo-url>
cd personal-finance-manager
docker compose up -d

# 2. Run migrations (creates all tables)
./scripts/deploy.sh
```

#### Existing Server - New Code
```bash
# 1. Pull latest code
git pull origin main

# 2. Rebuild if new dependencies
docker compose build app

# 3. Start containers
docker compose up -d

# 4. Deploy with migrations
./scripts/deploy.sh
```

#### Existing Server - First Time with Alembic
```bash
# 1. Pull latest code
git pull origin main

# 2. Rebuild container
docker compose build app
docker compose up -d

# 3. Mark existing schema as up-to-date (IMPORTANT!)
docker compose exec app alembic stamp head

# 4. Deploy
./scripts/deploy.sh
```

### Migration Commands

#### Development
```bash
# Run migrations
./scripts/dev.sh migrate

# Create new migration
./scripts/dev.sh migrate-create "Add user preferences table"

# Check migration status
./scripts/dev.sh migrate-status

# Reset database (WARNING: deletes all data)
./scripts/dev.sh reset-db
```

#### Production
```bash
# Full deployment with migrations
./scripts/deploy.sh

# Run migrations only
./scripts/deploy.sh migrate

# Check application health
./scripts/deploy.sh health
```

### Common Issues & Solutions

#### "DuplicateTable: relation already exists"
**Cause**: Database was initialized with SQL scripts, but Alembic doesn't know about existing tables.

**Solution**:
```bash
# Mark current schema as up-to-date
docker compose exec app alembic stamp head
```

#### "No module named 'psycopg2'"
**Cause**: New dependency not installed in container.

**Solution**:
```bash
# Rebuild container with new requirements
docker compose build app
docker compose up -d
```

#### Migration fails
**Troubleshooting**:
```bash
# Check migration status
./scripts/dev.sh migrate-status

# Check database logs
docker compose logs postgres

# Manual migration with verbose output
docker compose exec app alembic upgrade head --verbose
```

## Development Status

### ✅ Completed Features
- Basic infrastructure implemented
- User registration and authentication
- JWT token management
- TOTP MFA setup and verification
- Email confirmation system
- Firebase Authentication integration
- Frontend demo with MFA flows
- Database migration system
- Deployment automation

### ⚠️ Current Issues
- Limited test coverage (only 4 basic tests)
- Missing integration tests for MFA flows
- No automated test execution on code changes
- Manual debugging required for production issues

### 🔄 Next Priorities
1. Implement comprehensive test suite according to testing strategy
2. Add automated test execution on code changes
3. Complete Firebase setup and testing
4. Implement email MFA with actual email sending
5. Add proper error handling and validation

## Quick Reference Commands

### Development
```bash
./scripts/dev.sh start      # Start development environment
./scripts/dev.sh test       # Run tests
./scripts/dev.sh logs       # View logs
./scripts/dev.sh restart    # Restart containers
./scripts/dev.sh migrate    # Run migrations
```

### Production
```bash
./scripts/deploy.sh         # Full deployment with migrations
./scripts/deploy.sh migrate # Run migrations only
./scripts/deploy.sh health  # Check application health
```

### Database Management
```bash
# Access database
docker compose exec postgres psql -U pfm_user -d pfm_dev

# Run migrations
docker compose exec app alembic upgrade head

# Create new migration
docker compose exec app alembic revision --autogenerate -m "description"

# Mark schema as up-to-date (for existing databases)
docker compose exec app alembic stamp head
```

## Environment Variables

### Required for Production
```bash
SECRET_KEY=your_secure_secret_key
JWT_SECRET_KEY=your_secure_jwt_secret
DATABASE_URL=your_production_database_url
FIREBASE_SERVICE_ACCOUNT_JSON=your_firebase_service_account_json
FRONTEND_HOSTNAME=https://your-domain.com
```

### Development Defaults
```bash
ENVIRONMENT=development
SECRET_KEY=pfm_dev_secret_key_2024_xyz789_abcdefghijklmnopqrstuvwxyz123456789
JWT_SECRET_KEY=pfm_dev_jwt_secret_2024_xyz789_abcdefghijklmnopqrstuvwxyz123456789
DATABASE_URL=postgresql://pfm_user:pfm_dev_secure_2024_xyz789@postgres:5432/pfm_dev
FRONTEND_HOSTNAME=http://localhost:3000
```

## Security Considerations

### Migration Security
- Migrations run with database user permissions
- Ensure proper database user setup
- Use least privilege principle
- Never include secrets in migrations

### Data Protection
- Encrypt sensitive data (TOTP secrets, backup codes)
- Use environment variables for configuration
- Implement audit trails
- Regular security updates
- Firebase token verification on backend

## Troubleshooting Guide

### Deployment Issues
1. **Check container status**: `docker compose ps`
2. **View logs**: `docker compose logs -f app`
3. **Check database**: `docker compose exec postgres pg_isready -U pfm_user -d pfm_dev`
4. **Verify migrations**: `docker compose exec app alembic current`

### Common Error Solutions
- **Container won't start**: Check Docker and disk space
- **Database connection failed**: Verify DATABASE_URL and network
- **Migration conflicts**: Use `alembic stamp head` for existing databases
- **Missing dependencies**: Rebuild container with `docker compose build app`
- **Firebase errors**: Check service account configuration and environment variables

## Future Enhancements

### Planned Features
- [ ] Complete authentication implementation
- [ ] Add financial management features
- [ ] Implement reporting and analytics
- [ ] Add mobile app support
- [ ] Enhanced security features
- [ ] Performance optimizations

### Infrastructure Improvements
- [ ] CI/CD pipeline with automated testing
- [ ] Production monitoring and alerting
- [ ] Database backup and recovery procedures
- [ ] Load balancing and scaling
- [ ] Security audit and penetration testing 