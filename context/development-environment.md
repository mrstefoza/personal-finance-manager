# Development Environment

## Overview
Docker-based development environment with hot reload and comprehensive API documentation.

## Docker Setup

### Container Architecture
Two-container setup for optimal development experience:

1. **PostgreSQL Database Container**
2. **FastAPI Application Container**

### Docker Compose Configuration

#### **docker-compose.yml**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: pfm_postgres
    environment:
      POSTGRES_DB: pfm_dev
      POSTGRES_USER: pfm_user
      POSTGRES_PASSWORD: pfm_password
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./sql/init:/docker-entrypoint-initdb.d
    networks:
      - pfm_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U pfm_user -d pfm_dev"]
      interval: 10s
      timeout: 5s
      retries: 5

  app:
    build: .
    container_name: pfm_app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://pfm_user:pfm_password@postgres:5432/pfm_dev
      - ENVIRONMENT=development
      - SECRET_KEY=dev_secret_key_change_in_production
      - JWT_SECRET_KEY=dev_jwt_secret_change_in_production
      - GOOGLE_CLIENT_ID=your_google_client_id
      - GOOGLE_CLIENT_SECRET=your_google_client_secret
    volumes:
      - .:/app
      - ./logs:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - pfm_network
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:

networks:
  pfm_network:
    driver: bridge
```

#### **Dockerfile**
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Hot Reload (Live Code Reloading)

### How It Works
```bash
# Hot reload command
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Monitored Files
- **Python files**: `.py` files in your project
- **Template files**: `.html`, `.jinja` files
- **Configuration**: `.env`, `.yaml`, `.json` files

### Hot Reload Process
```
1. You save a file (e.g., app/api/v1/auth.py)
2. uvicorn detects the file change
3. Server automatically restarts
4. New code is loaded
5. Server is ready in ~1-2 seconds
```

### Docker Hot Reload Setup
```yaml
# docker-compose.yml
app:
  volumes:
    - .:/app  # Mounts your local code into container
  command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Example: Code Changes
```python
# Before: app/api/v1/auth.py
@app.post("/login")
async def login():
    return {"message": "old code"}

# After: You change it to
@app.post("/login")
async def login():
    return {"message": "new code"}

# Result: Server restarts automatically, new endpoint works immediately
```

### Hot Reload Configuration

#### Custom Watch Directories
```bash
# Watch specific directories
uvicorn app.main:app --reload --reload-dir app --reload-dir tests
```

#### Exclude Files
```bash
# Ignore certain files
uvicorn app.main:app --reload --reload-exclude "*.pyc" --reload-exclude "*.log"
```

#### Environment Variables
```bash
# Development environment
ENVIRONMENT=development uvicorn app.main:app --reload

# Or in docker-compose
environment:
  - ENVIRONMENT=development
```

## API Documentation (Swagger/OpenAPI)

### FastAPI Auto-Generated Documentation
FastAPI automatically generates interactive API documentation using **OpenAPI 3.0** (formerly Swagger):

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Documentation Features
```python
# FastAPI automatically generates this from your code
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Personal Finance Manager",
    description="API for managing personal finances",
    version="1.0.0"
)

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

@app.post("/api/v1/auth/register", response_model=UserResponse)
async def register(user: UserCreate):
    """Register a new user account"""
    # Your code here
    pass
```

### What You Get in Swagger UI
- ✅ **Try-it-out functionality**: Test APIs directly in browser
- ✅ **Request/response schemas**: Exact data formats
- ✅ **Authentication examples**: JWT token integration
- ✅ **Error responses**: All possible error codes
- ✅ **Data validation rules**: Pydantic model constraints
- ✅ **Always up-to-date**: Generated from actual code

## Development Workflow

### Starting the Environment
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Access database
docker-compose exec postgres psql -U pfm_user -d pfm_dev
```

### Database Management
```bash
# Run migrations
docker-compose exec app alembic upgrade head

# Create new migration
docker-compose exec app alembic revision --autogenerate -m "description"

# Reset database
docker-compose down -v
docker-compose up -d
```

### Development Commands
```bash
# Run tests
docker-compose exec app pytest

# Format code
docker-compose exec app black .

# Lint code
docker-compose exec app flake8

# Type checking
docker-compose exec app mypy .
```

### Complete Development Example
```bash
# 1. Start environment
docker-compose up -d

# 2. Access documentation
# Open http://localhost:8000/docs

# 3. Edit code (hot reload works)
# Edit app/api/v1/auth.py

# 4. Test in Swagger UI
# Go to /api/v1/auth/register endpoint
# Click "Try it out"
# Test with your new validation

# 5. Run tests
docker-compose exec app pytest

# 6. Check logs
docker-compose logs -f app
```

## Access Points

### Development URLs
- **FastAPI App**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

### Database Access
- **PostgreSQL**: localhost:5432
- **Database**: pfm_dev
- **Username**: pfm_user
- **Password**: pfm_password
- **Admin Tools**: pgAdmin, DBeaver, or psql

## Benefits

### Development Experience
- **Hot Reload**: Code changes reflect immediately
- **Isolated Environment**: No conflicts with local Python/PostgreSQL
- **Consistent Setup**: Same environment for all developers
- **Easy Reset**: `docker-compose down -v` to start fresh

### API Documentation
- **Always Up-to-Date**: Generated from your actual code
- **Interactive Testing**: Test APIs directly in browser
- **Schema Validation**: Shows exact request/response formats
- **Authentication**: Test with real tokens
- **Error Examples**: See all possible error responses

### Database Management
- **Persistent Data**: Volume mounts preserve data between restarts
- **Initial Schema**: SQL files automatically loaded on first run
- **Easy Backup**: Simple volume backup/restore
- **Health Checks**: Ensures database is ready before app starts

### Production Parity
- **Same Dependencies**: Identical Python packages
- **Similar Environment**: Close to production setup
- **Easy Testing**: Test against same database version

## Troubleshooting

### Common Issues

#### Container Won't Start
```bash
# Check logs
docker-compose logs

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### Hot Reload Not Working
```bash
# Check volume mounts
docker-compose exec app ls -la /app

# Restart with explicit reload
docker-compose exec app uvicorn app.main:app --reload
```

#### Database Connection Issues
```bash
# Check database health
docker-compose exec postgres pg_isready -U pfm_user -d pfm_dev

# Check network connectivity
docker-compose exec app ping postgres
```

#### Port Conflicts
```bash
# Check what's using the ports
lsof -i :8000
lsof -i :5432

# Use different ports in docker-compose.yml
ports:
  - "8001:8000"  # Different host port
```

### Performance Optimization

#### Development vs Production
```yaml
# Development: Hot reload enabled
command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Production: No reload, multiple workers
command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Resource Limits
```yaml
# Add resource limits for production-like testing
app:
  deploy:
    resources:
      limits:
        memory: 512M
        cpus: '0.5'
``` 