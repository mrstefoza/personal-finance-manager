# Technical Stack

## Backend Framework
**FastAPI** - Modern, fast Python web framework
- **Performance**: One of the fastest Python frameworks, comparable to Node.js
- **Type Safety**: Built-in Pydantic models for automatic validation
- **Documentation**: Auto-generated OpenAPI/Swagger docs
- **Async Support**: Native async/await for concurrent requests
- **Developer Experience**: Excellent IDE support with type hints

## Database
**PostgreSQL** - Relational database
- **ACID Compliance**: Full transactional support for data integrity
- **Rich Features**: JSON support, full-text search, advanced indexing
- **Scalability**: Handles complex queries and large datasets
- **Production Ready**: Battle-tested in production environments

## Database Access
**Raw SQL with asyncpg** - Direct SQL queries with async PostgreSQL driver
- **Performance**: Maximum performance without ORM overhead
- **Control**: Full control over SQL queries and optimization
- **Async Support**: Native async database operations
- **Simplicity**: No ORM complexity for simple queries

## Authentication & Security
**JWT (JSON Web Tokens)** - Stateless authentication
- **Access Tokens**: 15-30 minutes validity
- **Refresh Tokens**: 7-30 days validity, stored in database
- **Stateless**: No server-side session storage needed
- **Scalable**: Works well with multiple server instances

**OAuth Integration**
- **Google OAuth**: Social login integration
- **Hybrid Approach**: Support both OAuth and email/password

**Multi-Factor Authentication (MFA)**
- **TOTP**: Time-based One-Time Password (Google Authenticator/Authy)
- **Email MFA**: One-time codes sent via email
- **Backup Codes**: Recovery mechanism for account access

## Development Tools
**Docker** - Containerization
- **Consistency**: Same environment across development and production
- **Isolation**: Clean separation of services
- **Deployment**: Easy deployment and scaling

**Alembic** - Database migrations
- **Version Control**: Track database schema changes
- **Rollback**: Ability to rollback migrations
- **Raw SQL**: Support for custom SQL in migrations

**python-dotenv** - Environment management
- **Security**: Keep sensitive data out of code
- **Flexibility**: Different configurations per environment
- **Best Practice**: Industry standard for configuration

## Testing
**pytest** - Testing framework
- **Comprehensive**: Unit, integration, and e2e testing
- **Fixtures**: Reusable test data and setup
- **Async Support**: Built-in async testing capabilities
- **Plugins**: Rich ecosystem of testing plugins

## Logging & Monitoring
**Structured Logging** - JSON-formatted logs
- **Searchable**: Easy to search and filter logs
- **Integration**: Works well with log aggregation services
- **Performance**: Minimal overhead

## Dependencies
### Core Dependencies
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `asyncpg` - Async PostgreSQL driver
- `alembic` - Database migrations
- `python-dotenv` - Environment variables

### Authentication Dependencies
- `python-jose[cryptography]` - JWT handling
- `passlib[bcrypt]` - Password hashing
- `pyotp` - TOTP generation/validation
- `qrcode` - QR code generation for MFA setup
- `httpx` - HTTP client for OAuth

### Development Dependencies
- `pytest` - Testing framework
- `pytest-asyncio` - Async testing support
- `black` - Code formatting
- `flake8` - Linting
- `mypy` - Type checking

## Why This Stack?

### Performance
- FastAPI provides excellent performance for API endpoints
- Raw SQL with asyncpg gives maximum database performance
- Async operations handle concurrent requests efficiently

### Security
- JWT with refresh tokens provides secure authentication
- MFA adds additional security layer
- PostgreSQL offers robust data integrity

### Developer Experience
- FastAPI's auto-documentation saves development time
- Type hints improve code quality and IDE support
- Docker ensures consistent development environment

### Scalability
- Stateless JWT authentication scales horizontally
- PostgreSQL handles complex queries and large datasets
- Async operations support high concurrency

### Maintenance
- Raw SQL is easier to debug and optimize
- Alembic provides reliable database migrations
- Comprehensive testing ensures code quality 