# Project Structure

## Overview
Clean architecture with separation of concerns, dependency injection, and comprehensive testing.

## Directory Structure
```
pfm/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration management
│   │   ├── database.py         # Database connection and pool
│   │   ├── security.py         # JWT, password hashing, encryption
│   │   ├── oauth.py            # Google OAuth integration
│   │   └── mfa.py              # MFA utilities (TOTP, email codes)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py             # Dependency injection
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py         # Authentication endpoints
│   │       ├── users.py        # User management endpoints
│   │       └── mfa.py          # MFA endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # User data models
│   │   └── session.py          # Session/token models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication request/response schemas
│   │   ├── user.py             # User request/response schemas
│   │   └── mfa.py              # MFA request/response schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py     # Authentication business logic
│   │   ├── user_service.py     # User management business logic
│   │   ├── mfa_service.py      # MFA business logic
│   │   └── email_service.py    # Email sending service
│   └── utils/
│       ├── __init__.py
│       ├── encryption.py       # Data encryption utilities
│       └── validators.py       # Custom validation functions
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # pytest configuration and fixtures
│   ├── test_api/
│   │   ├── __init__.py
│   │   ├── test_auth.py        # Authentication API tests
│   │   ├── test_users.py       # User API tests
│   │   └── test_mfa.py         # MFA API tests
│   ├── test_services/
│   │   ├── __init__.py
│   │   ├── test_auth_service.py
│   │   ├── test_user_service.py
│   │   └── test_mfa_service.py
│   └── test_utils/
│       ├── __init__.py
│       └── test_encryption.py
├── alembic/
│   ├── versions/               # Migration files
│   ├── env.py                  # Alembic environment
│   └── alembic.ini             # Alembic configuration
├── sql/
│   ├── migrations/             # Raw SQL migration files
│   ├── queries/                # Reusable SQL queries
│   │   ├── users.sql
│   │   ├── sessions.sql
│   │   └── mfa.sql
│   └── indexes.sql             # Database indexes
├── docker/
│   ├── Dockerfile              # Application container
│   └── docker-compose.yml      # Development environment
├── scripts/
│   ├── setup.sh                # Development setup script
│   └── test.sh                 # Test execution script
├── .env.example                # Environment variables template
├── .gitignore
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── pyproject.toml              # Project configuration
└── README.md                   # Project documentation
```

## Architecture Principles

### 1. Separation of Concerns
- **API Layer**: HTTP endpoints, request/response handling
- **Service Layer**: Business logic, data processing
- **Data Layer**: Database operations, data models
- **Core Layer**: Configuration, utilities, shared functionality

### 2. Dependency Injection
- Services are injected into API endpoints
- Database connections are managed centrally
- Configuration is injected where needed
- Easy testing with mock dependencies

### 3. Clean Architecture
- **Dependencies flow inward**: API → Services → Data
- **No circular dependencies**
- **Testable components**
- **Framework independence**

### 4. File Organization
- **Feature-based**: Related functionality grouped together
- **Consistent naming**: Clear, descriptive file names
- **Modular structure**: Easy to add new features
- **Scalable design**: Supports team development

## Key Components

### Core Module
- **Configuration**: Environment-based settings
- **Database**: Connection pooling and utilities
- **Security**: JWT, encryption, password hashing
- **OAuth**: Google authentication integration
- **MFA**: TOTP and email MFA utilities

### API Module
- **Versioned endpoints**: `/api/v1/` structure
- **Dependency injection**: Shared dependencies
- **Request validation**: Pydantic schemas
- **Error handling**: Consistent error responses
- **Authentication**: JWT token validation

### Services Module
- **Business logic**: Core application functionality
- **Data processing**: Transform and validate data
- **External integrations**: Email, OAuth, etc.
- **Transaction management**: Database transaction handling

### Models & Schemas
- **Models**: Database data structures
- **Schemas**: API request/response structures
- **Validation**: Data validation rules
- **Serialization**: Data transformation

## Development Workflow

### Adding New Features
1. **Database**: Create migration files
2. **Models**: Define data structures
3. **Schemas**: Create API schemas
4. **Services**: Implement business logic
5. **API**: Add endpoints
6. **Tests**: Write comprehensive tests

### Testing Strategy
- **Unit tests**: Individual component testing
- **Integration tests**: API endpoint testing
- **Fixtures**: Reusable test data
- **Mocking**: External service simulation

### Code Quality
- **Type hints**: Full type annotation
- **Documentation**: Docstrings and comments
- **Formatting**: Black code formatter
- **Linting**: Flake8 and mypy
- **Pre-commit hooks**: Automated quality checks 