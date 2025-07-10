# Database Migrations Guide

## Overview

This project uses **Alembic** for database migrations, providing a robust way to manage database schema changes across different environments.

## How Migrations Work

### 1. **Migration Files**
- Located in `alembic/versions/`
- Each migration has a unique revision ID
- Contains `upgrade()` and `downgrade()` functions
- Uses raw SQL for maximum control

### 2. **Migration Tracking**
- Alembic tracks which migrations have been applied
- Stored in `alembic_version` table in the database
- Prevents duplicate migrations
- Enables rollback capabilities

### 3. **Deployment Process**
When you deploy new code:

```bash
# 1. Pull new code
git pull origin main

# 2. Run deployment script (automatically handles migrations)
./scripts/deploy.sh

# Or manually:
docker-compose down
docker-compose up -d
docker-compose exec app alembic upgrade head
```

## Migration Commands

### Development Commands
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

### Production Commands
```bash
# Full deployment with migrations
./scripts/deploy.sh

# Run migrations only
./scripts/deploy.sh migrate

# Check application health
./scripts/deploy.sh health
```

### Direct Alembic Commands
```bash
# Run all pending migrations
docker-compose exec app alembic upgrade head

# Run specific migration
docker-compose exec app alembic upgrade 0002

# Rollback one migration
docker-compose exec app alembic downgrade -1

# Check current version
docker-compose exec app alembic current

# View migration history
docker-compose exec app alembic history
```

## Migration Workflow

### 1. **Creating a New Migration**

When you need to change the database schema:

```bash
# 1. Make your code changes
# 2. Create migration
./scripts/dev.sh migrate-create "Add user preferences table"

# 3. Review the generated migration file
# 4. Test the migration
./scripts/dev.sh migrate

# 5. Commit both code and migration
git add .
git commit -m "Add user preferences table"
```

### 2. **Migration File Structure**

```python
"""Add user preferences table

Revision ID: 0003
Revises: 0002
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Your migration code here
    op.execute("""
        CREATE TABLE user_preferences (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            theme VARCHAR(20) DEFAULT 'light',
            notifications_enabled BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

def downgrade() -> None:
    # Rollback code here
    op.execute("DROP TABLE IF EXISTS user_preferences")
```

### 3. **Testing Migrations**

```bash
# Test upgrade
./scripts/dev.sh migrate

# Test downgrade
docker-compose exec app alembic downgrade -1

# Test upgrade again
./scripts/dev.sh migrate
```

## Deployment Scenarios

### **Fresh Server Setup**
```bash
# 1. Clone repository
git clone <repo-url>
cd pfm

# 2. Start containers
docker-compose up -d

# 3. Run migrations (creates all tables)
./scripts/deploy.sh
```

### **Existing Server - New Code**
```bash
# 1. Pull new code
git pull origin main

# 2. Deploy with migrations
./scripts/deploy.sh
```

### **Existing Server - Schema Changes Only**
```bash
# 1. Pull new code
git pull origin main

# 2. Run migrations only
./scripts/deploy.sh migrate
```

## Migration Best Practices

### 1. **Always Test Migrations**
- Test both upgrade and downgrade
- Use test data to verify functionality
- Test in staging environment first

### 2. **Backup Before Production**
```bash
# Create database backup
docker-compose exec postgres pg_dump -U pfm_user pfm_dev > backup.sql

# Run migrations
./scripts/deploy.sh migrate

# If issues occur, restore from backup
docker-compose exec postgres psql -U pfm_user pfm_dev < backup.sql
```

### 3. **Migration Naming**
- Use descriptive names: "Add user preferences table"
- Include the feature or change being made
- Avoid generic names like "Update schema"

### 4. **Data Migration**
For data changes, include both schema and data:

```python
def upgrade() -> None:
    # Add new column
    op.execute("ALTER TABLE users ADD COLUMN preferences JSONB")
    
    # Migrate existing data
    op.execute("""
        UPDATE users 
        SET preferences = '{"theme": "light", "notifications": true}'::jsonb
        WHERE preferences IS NULL
    """)

def downgrade() -> None:
    # Remove column (data will be lost)
    op.execute("ALTER TABLE users DROP COLUMN preferences")
```

## Troubleshooting

### **Migration Fails**
```bash
# Check migration status
./scripts/dev.sh migrate-status

# Check database logs
docker-compose logs postgres

# Manually run migration with verbose output
docker-compose exec app alembic upgrade head --verbose
```

### **Migration Already Applied**
```bash
# Check current version
docker-compose exec app alembic current

# If migration is stuck, mark as applied
docker-compose exec app alembic stamp head
```

### **Database Out of Sync**
```bash
# Reset database (WARNING: deletes all data)
./scripts/dev.sh reset-db

# Or manually sync
docker-compose exec app alembic stamp head
```

## Migration Files

### **Current Migrations**
- `0001_initial_schema.py` - Base schema (users, sessions, MFA tables)
- `0002_add_mfa_sessions.py` - MFA session tracking

### **Future Migrations**
When adding new features, create migrations for:
- New tables
- New columns
- New indexes
- Data migrations
- Schema changes

## Environment-Specific Considerations

### **Development**
- Use `./scripts/dev.sh` commands
- Reset database frequently for testing
- Test migrations thoroughly

### **Staging**
- Mirror production environment
- Test all migrations before production
- Use production-like data

### **Production**
- Always backup before migrations
- Use `./scripts/deploy.sh` for deployment
- Monitor migration logs
- Have rollback plan ready

## Security Considerations

### **Migration Permissions**
- Migrations run with database user permissions
- Ensure proper database user setup
- Use least privilege principle

### **Sensitive Data**
- Never include secrets in migrations
- Use environment variables for sensitive data
- Encrypt sensitive data in database

### **Audit Trail**
- Log all migration operations
- Track who ran migrations
- Keep migration history for compliance

## Integration with CI/CD

### **Automated Testing**
```yaml
# Example GitHub Actions step
- name: Test migrations
  run: |
    docker-compose up -d
    ./scripts/dev.sh migrate
    ./scripts/dev.sh test
```

### **Deployment Pipeline**
```yaml
# Example deployment step
- name: Deploy with migrations
  run: |
    ./scripts/deploy.sh
```

## Summary

The migration system provides:
- ✅ **Version Control**: Track all database changes
- ✅ **Rollback Support**: Revert changes if needed
- ✅ **Automated Deployment**: Migrations run automatically
- ✅ **Environment Consistency**: Same schema across environments
- ✅ **Testing Support**: Easy to test migrations
- ✅ **Documentation**: Migration history serves as documentation

For questions or issues with migrations, check the logs and use the troubleshooting commands above. 