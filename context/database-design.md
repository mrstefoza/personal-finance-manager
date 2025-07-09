# Database Design

## Overview
PostgreSQL database with raw SQL queries, UUID primary keys, and comprehensive audit trails.

## Database Schema

### Users Table
Main user table with authentication and profile information.

```sql
CREATE TABLE users (
    -- Core fields
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('individual', 'business')),
    language_preference VARCHAR(10) DEFAULT 'hy' NOT NULL,
    currency_preference VARCHAR(3) DEFAULT 'AMD' NOT NULL,
    profile_picture VARCHAR(500),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    profile_status VARCHAR(20) DEFAULT 'active' CHECK (profile_status IN ('active', 'inactive', 'suspended', 'pending_verification')),
    
    -- Authentication fields
    password_hash VARCHAR(255),
    email_verified BOOLEAN DEFAULT FALSE,
    email_verification_token VARCHAR(255),
    email_verification_expires TIMESTAMP,
    
    -- OAuth fields
    google_id VARCHAR(255) UNIQUE,
    oauth_provider VARCHAR(20),
    
    -- MFA fields
    mfa_enabled BOOLEAN DEFAULT FALSE,
    totp_secret_encrypted TEXT,
    totp_enabled BOOLEAN DEFAULT FALSE,
    email_mfa_enabled BOOLEAN DEFAULT FALSE,
    backup_codes_encrypted TEXT,
    
    -- Security fields
    failed_login_attempts INTEGER DEFAULT 0,
    account_locked_until TIMESTAMP,
    password_reset_token VARCHAR(255),
    password_reset_expires TIMESTAMP,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);
```

### User Sessions Table
Manages refresh tokens and active sessions.

```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token_hash VARCHAR(255) NOT NULL,
    device_info JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Email MFA Codes Table
Temporary storage for email MFA codes.

```sql
CREATE TABLE email_mfa_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    code_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### MFA Attempts Table
Tracks MFA login attempts for rate limiting.

```sql
CREATE TABLE mfa_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    method VARCHAR(20) NOT NULL CHECK (method IN ('totp', 'email', 'backup')),
    success BOOLEAN NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Indexes

### Performance Indexes
```sql
-- Users table indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_google_id ON users(google_id);
CREATE INDEX idx_users_user_type ON users(user_type);
CREATE INDEX idx_users_profile_status ON users(profile_status);
CREATE INDEX idx_users_created_at ON users(created_at);

-- User sessions indexes
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_refresh_token ON user_sessions(refresh_token_hash);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX idx_user_sessions_active ON user_sessions(is_active);

-- Email MFA codes indexes
CREATE INDEX idx_email_mfa_codes_user_id ON email_mfa_codes(user_id);
CREATE INDEX idx_email_mfa_codes_expires_at ON email_mfa_codes(expires_at);
CREATE INDEX idx_email_mfa_codes_used ON email_mfa_codes(used);

-- MFA attempts indexes
CREATE INDEX idx_mfa_attempts_user_id_created ON mfa_attempts(user_id, created_at);
CREATE INDEX idx_mfa_attempts_method_success ON mfa_attempts(method, success);
CREATE INDEX idx_mfa_attempts_ip_address ON mfa_attempts(ip_address);
```

## Data Types and Constraints

### UUID Primary Keys
- **Advantages**: Globally unique, no sequential guessing
- **Security**: Prevents enumeration attacks
- **Distribution**: Better for distributed systems

### Check Constraints
- **User Type**: Only 'individual' or 'business'
- **Profile Status**: Valid status values
- **MFA Method**: Valid MFA methods

### Foreign Key Constraints
- **Cascade Deletes**: Sessions and MFA data deleted with user
- **Referential Integrity**: Ensures data consistency

### JSONB Fields
- **Device Info**: Flexible storage for browser/OS information
- **Performance**: Better than JSON for querying

## Security Considerations

### Encrypted Fields
- **TOTP Secret**: Encrypted at rest
- **Backup Codes**: Encrypted JSON array
- **Password Hash**: bcrypt/argon2 hashing

### Token Management
- **Refresh Tokens**: Hashed storage
- **Verification Tokens**: Temporary, short-lived
- **Reset Tokens**: Time-limited access

### Audit Trail
- **Timestamps**: Created, updated, deleted
- **Login Tracking**: Last login, failed attempts
- **MFA Attempts**: Success/failure logging

## Migration Strategy

### Alembic Integration
- **Raw SQL Support**: Custom SQL in migrations
- **Version Control**: Track schema changes
- **Rollback Support**: Reversible migrations

### Migration Files
```sql
-- Example migration structure
-- alembic/versions/001_create_users_table.sql
-- alembic/versions/002_create_sessions_table.sql
-- alembic/versions/003_create_mfa_tables.sql
```

## Query Patterns

### Common Queries
```sql
-- User authentication
SELECT * FROM users WHERE email = $1 AND deleted_at IS NULL;

-- Active sessions
SELECT * FROM user_sessions WHERE user_id = $1 AND is_active = true;

-- Valid MFA codes
SELECT * FROM email_mfa_codes 
WHERE user_id = $1 AND expires_at > NOW() AND used = false;

-- Recent MFA attempts
SELECT COUNT(*) FROM mfa_attempts 
WHERE user_id = $1 AND created_at > NOW() - INTERVAL '1 hour';
```

### Performance Optimizations
- **Connection Pooling**: asyncpg built-in pooling
- **Prepared Statements**: Reusable query plans
- **Index Usage**: Optimized for common queries
- **Query Optimization**: Minimal data transfer

## Backup and Recovery

### Backup Strategy
- **Regular Backups**: Daily automated backups
- **Point-in-Time Recovery**: WAL archiving
- **Encrypted Backups**: Secure storage

### Data Retention
- **Soft Deletes**: Mark as deleted, retain for audit
- **Session Cleanup**: Remove expired sessions
- **MFA Code Cleanup**: Remove used/expired codes

## Future Considerations

### Scalability
- **Partitioning**: User data by user_type or date
- **Read Replicas**: Separate read/write operations
- **Caching**: Redis for frequently accessed data

### Extensibility
- **User Roles**: Additional permission system
- **Company Structure**: Business user hierarchies
- **Audit Logging**: Comprehensive activity tracking 