# Database Indexes

## Overview
Comprehensive indexing strategy for optimal query performance and security.

## Index Strategy

### Primary Indexes
All tables use UUID primary keys with `gen_random_uuid()` default for security and distribution.

### Performance Indexes
Optimized for common query patterns and security requirements.

## Users Table Indexes

### Core Indexes
```sql
-- Email lookup (most common query)
CREATE INDEX idx_users_email ON users(email);

-- Google OAuth lookup
CREATE INDEX idx_users_google_id ON users(google_id);

-- User type filtering
CREATE INDEX idx_users_user_type ON users(user_type);

-- Profile status filtering
CREATE INDEX idx_users_profile_status ON users(profile_status);

-- Registration date sorting
CREATE INDEX idx_users_created_at ON users(created_at);
```

### Composite Indexes
```sql
-- User type and status for business queries
CREATE INDEX idx_users_type_status ON users(user_type, profile_status);

-- Email and verification status
CREATE INDEX idx_users_email_verified ON users(email, email_verified);

-- User type and creation date
CREATE INDEX idx_users_type_created ON users(user_type, created_at);
```

### Partial Indexes
```sql
-- Active users only
CREATE INDEX idx_users_active ON users(id) WHERE profile_status = 'active';

-- Unverified users
CREATE INDEX idx_users_unverified ON users(email) WHERE email_verified = false;

-- Non-deleted users
CREATE INDEX idx_users_not_deleted ON users(id) WHERE deleted_at IS NULL;
```

## User Sessions Table Indexes

### Core Indexes
```sql
-- User sessions lookup
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);

-- Refresh token validation
CREATE INDEX idx_user_sessions_refresh_token ON user_sessions(refresh_token_hash);

-- Expired sessions cleanup
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);

-- Active sessions filtering
CREATE INDEX idx_user_sessions_active ON user_sessions(is_active);
```

### Composite Indexes
```sql
-- User active sessions
CREATE INDEX idx_user_sessions_user_active ON user_sessions(user_id, is_active);

-- Expired active sessions (for cleanup)
CREATE INDEX idx_user_sessions_expired_active ON user_sessions(expires_at, is_active) 
WHERE is_active = true;
```

### Partial Indexes
```sql
-- Active sessions only
CREATE INDEX idx_user_sessions_active_only ON user_sessions(user_id, expires_at) 
WHERE is_active = true;

-- Expired sessions for cleanup
CREATE INDEX idx_user_sessions_expired ON user_sessions(id) 
WHERE expires_at < NOW();
```

## Email MFA Codes Table Indexes

### Core Indexes
```sql
-- User MFA codes
CREATE INDEX idx_email_mfa_codes_user_id ON email_mfa_codes(user_id);

-- Expired codes cleanup
CREATE INDEX idx_email_mfa_codes_expires_at ON email_mfa_codes(expires_at);

-- Used codes filtering
CREATE INDEX idx_email_mfa_codes_used ON email_mfa_codes(used);
```

### Composite Indexes
```sql
-- Valid codes for user
CREATE INDEX idx_email_mfa_codes_valid ON email_mfa_codes(user_id, expires_at, used);

-- Unused expired codes (for cleanup)
CREATE INDEX idx_email_mfa_codes_unused_expired ON email_mfa_codes(expires_at, used) 
WHERE used = false;
```

### Partial Indexes
```sql
-- Valid codes only
CREATE INDEX idx_email_mfa_codes_valid_only ON email_mfa_codes(user_id, expires_at) 
WHERE used = false AND expires_at > NOW();

-- Expired unused codes for cleanup
CREATE INDEX idx_email_mfa_codes_cleanup ON email_mfa_codes(id) 
WHERE used = false AND expires_at < NOW();
```

## MFA Attempts Table Indexes

### Core Indexes
```sql
-- User MFA attempts
CREATE INDEX idx_mfa_attempts_user_id_created ON mfa_attempts(user_id, created_at);

-- Method and success filtering
CREATE INDEX idx_mfa_attempts_method_success ON mfa_attempts(method, success);

-- IP address tracking
CREATE INDEX idx_mfa_attempts_ip_address ON mfa_attempts(ip_address);
```

### Composite Indexes
```sql
-- Recent failed attempts for rate limiting
CREATE INDEX idx_mfa_attempts_recent_failed ON mfa_attempts(user_id, method, success, created_at);

-- IP-based rate limiting
CREATE INDEX idx_mfa_attempts_ip_recent ON mfa_attempts(ip_address, created_at);

-- Method-based statistics
CREATE INDEX idx_mfa_attempts_method_stats ON mfa_attempts(method, success, created_at);
```

### Partial Indexes
```sql
-- Recent attempts (last 24 hours)
CREATE INDEX idx_mfa_attempts_recent ON mfa_attempts(user_id, created_at) 
WHERE created_at > NOW() - INTERVAL '24 hours';

-- Failed attempts for security monitoring
CREATE INDEX idx_mfa_attempts_failed ON mfa_attempts(user_id, ip_address, created_at) 
WHERE success = false;
```

## Index Maintenance

### Regular Maintenance
```sql
-- Analyze tables for query planner
ANALYZE users;
ANALYZE user_sessions;
ANALYZE email_mfa_codes;
ANALYZE mfa_attempts;

-- Reindex if needed
REINDEX INDEX idx_users_email;
```

### Cleanup Queries
```sql
-- Remove expired sessions
DELETE FROM user_sessions WHERE expires_at < NOW();

-- Remove expired MFA codes
DELETE FROM email_mfa_codes WHERE expires_at < NOW() OR used = true;

-- Archive old MFA attempts (older than 90 days)
DELETE FROM mfa_attempts WHERE created_at < NOW() - INTERVAL '90 days';
```

## Performance Monitoring

### Index Usage Statistics
```sql
-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

### Slow Query Analysis
```sql
-- Enable query logging
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_min_duration_statement = 1000; -- 1 second
SELECT pg_reload_conf();
```

### Index Size Monitoring
```sql
-- Check index sizes
SELECT 
    t.tablename,
    indexname,
    c.reltuples AS num_rows,
    pg_size_pretty(pg_relation_size(quote_ident(t.schemaname)||'.'||quote_ident(t.tablename)::regclass)) AS table_size,
    pg_size_pretty(pg_relation_size(quote_ident(t.schemaname)||'.'||quote_ident(t.indexname)::regclass)) AS index_size
FROM pg_tables t
LEFT JOIN pg_class c ON c.relname=t.tablename
LEFT JOIN (
    SELECT 
        schemaname,
        tablename,
        indexname
    FROM pg_indexes
    WHERE schemaname = 'public'
) i ON i.tablename = t.tablename
WHERE t.schemaname = 'public'
ORDER BY t.tablename, indexname;
```

## Security Considerations

### Index Security
- **No sensitive data**: Indexes don't contain sensitive information
- **Hash-based**: Tokens and codes are hashed before indexing
- **UUID primary keys**: Prevent enumeration attacks

### Access Control
```sql
-- Grant minimal permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON users TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON user_sessions TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON email_mfa_codes TO app_user;
GRANT SELECT, INSERT ON mfa_attempts TO app_user;

-- Grant index usage
GRANT USAGE ON SCHEMA public TO app_user;
```

## Optimization Tips

### Query Optimization
- **Use prepared statements**: Reuse query plans
- **Limit result sets**: Use LIMIT and OFFSET
- **Avoid SELECT ***: Select only needed columns
- **Use appropriate data types**: UUID for IDs, TIMESTAMP for dates

### Index Optimization
- **Monitor usage**: Remove unused indexes
- **Consider composite indexes**: For multi-column queries
- **Use partial indexes**: For filtered queries
- **Regular maintenance**: ANALYZE and REINDEX as needed

### Connection Pooling
```sql
-- Configure connection pool settings
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
SELECT pg_reload_conf();
``` 