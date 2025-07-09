# Personal Finance Manager API

A modern, secure backend API for personal finance management built with FastAPI, PostgreSQL, and comprehensive authentication features.

## 🚀 Features

- **User Management**: Individual and business user accounts
- **Authentication**: JWT tokens with refresh mechanism
- **OAuth Integration**: Google OAuth support
- **Multi-Factor Authentication**: TOTP and Email MFA
- **Security**: Rate limiting, account lockout, audit trails
- **API Documentation**: Auto-generated Swagger/OpenAPI docs

## 🛠 Tech Stack

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with asyncpg
- **Authentication**: JWT + OAuth
- **MFA**: TOTP (Google Authenticator) + Email codes
- **Containerization**: Docker + Docker Compose
- **Testing**: pytest
- **Code Quality**: Black, Flake8, MyPy

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

## 🚀 Quick Start

### 1. Start Development Environment
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app
```

### 2. Access the Application
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📁 Project Structure

```
pfm/
├── app/                    # Application code
│   ├── api/               # API endpoints
│   │   └── v1/           # API version 1
│   ├── core/             # Core functionality
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── utils/            # Utility functions
├── sql/                  # Database scripts
│   └── init/            # Initialization scripts
├── tests/               # Test suite
├── context/             # Project documentation
├── docker-compose.yml   # Docker services
├── Dockerfile          # Application container
└── requirements.txt    # Dependencies
```

## 🔧 Development

### Environment Variables
Copy the example environment file and configure:
```bash
cp .env.example .env
```

### Database Management
```bash
# Access database
docker-compose exec postgres psql -U pfm_user -d pfm_dev

# Run migrations (when implemented)
docker-compose exec app alembic upgrade head
```

### Testing
```bash
# Run tests
docker-compose exec app pytest

# Run with coverage
docker-compose exec app pytest --cov=app
```

### Code Quality
```bash
# Format code
docker-compose exec app black .

# Lint code
docker-compose exec app flake8

# Type checking
docker-compose exec app mypy .
```

## 🔐 Security Features

### Authentication
- JWT access tokens (30 minutes)
- JWT refresh tokens (7 days)
- Password hashing with bcrypt
- Account lockout after failed attempts

### Multi-Factor Authentication
- TOTP (Time-based One-Time Password)
- Email verification codes
- Backup codes for account recovery
- Rate limiting on MFA attempts

### OAuth Integration
- Google OAuth 2.0
- Account linking capabilities
- Secure token handling

## 📊 Database Schema

### Core Tables
- **users**: User accounts and profiles
- **user_sessions**: JWT refresh tokens
- **email_mfa_codes**: Email MFA codes
- **mfa_attempts**: MFA attempt tracking

### Security Features
- UUID primary keys
- Encrypted sensitive data
- Audit trails
- Soft deletes

## 🧪 Testing

### Test Structure
```
tests/
├── test_api/           # API endpoint tests
├── test_services/      # Business logic tests
└── test_utils/         # Utility function tests
```

### Running Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/test_api/test_auth.py

# With coverage
pytest --cov=app --cov-report=html
```

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Key Endpoints
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh tokens
- `GET /api/v1/users/profile` - Get user profile
- `POST /api/v1/mfa/setup` - Setup MFA

## 🔄 Development Workflow

### Hot Reload
The development environment includes hot reload:
- Code changes are automatically detected
- Server restarts automatically
- No manual restart required

### Database Changes
1. Create migration files
2. Update schema documentation
3. Test migrations
4. Deploy changes

## 🚀 Deployment

### Production Considerations
- Change default secrets
- Configure proper CORS origins
- Set up SSL/TLS
- Configure email service
- Set up monitoring and logging

### Environment Variables
```bash
# Required for production
SECRET_KEY=your_secure_secret_key
JWT_SECRET_KEY=your_secure_jwt_secret
DATABASE_URL=your_production_database_url
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run code quality checks
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the documentation in `/context/`
- Review API documentation at `/docs`
- Open an issue for bugs or feature requests

## 🔄 Roadmap

- [ ] Complete authentication implementation
- [ ] Add financial management features
- [ ] Implement reporting and analytics
- [ ] Add mobile app support
- [ ] Enhanced security features
- [ ] Performance optimizations 