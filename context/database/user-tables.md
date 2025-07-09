# User Database Tables

## Complete SQL Schema

### Users Table
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

## Field Descriptions

### Users Table Fields

#### Core Fields
- **id**: Unique identifier for the user (UUID)
- **full_name**: User's full name (required)
- **email**: User's email address (unique, required)
- **phone**: User's phone number (required)
- **user_type**: Type of user ('individual' or 'business')
- **language_preference**: Preferred language (default: 'hy' for Armenian)
- **currency_preference**: Preferred currency (default: 'AMD')
- **profile_picture**: URL to user's profile picture
- **registration_date**: When the user registered
- **last_login**: Last successful login timestamp
- **profile_status**: Current status of the user account

#### Authentication Fields
- **password_hash**: Hashed password (NULL for OAuth-only users)
- **email_verified**: Whether email has been verified
- **email_verification_token**: Token for email verification
- **email_verification_expires**: Expiration time for verification token

#### OAuth Fields
- **google_id**: Google OAuth user ID (unique)
- **oauth_provider**: Which OAuth provider is linked ('google', 'email', 'both')

#### MFA Fields
- **mfa_enabled**: Whether MFA is enabled for the account
- **totp_secret_encrypted**: Encrypted TOTP secret key
- **totp_enabled**: Whether TOTP MFA is enabled
- **email_mfa_enabled**: Whether email MFA is enabled
- **backup_codes_encrypted**: Encrypted JSON array of backup codes

#### Security Fields
- **failed_login_attempts**: Count of consecutive failed login attempts
- **account_locked_until**: Timestamp until account is locked
- **password_reset_token**: Token for password reset
- **password_reset_expires**: Expiration time for reset token

#### Audit Fields
- **created_at**: When the user record was created
- **updated_at**: When the user record was last updated
- **deleted_at**: Soft delete timestamp (NULL if not deleted)

### User Sessions Table Fields
- **id**: Unique session identifier
- **user_id**: Reference to the user
- **refresh_token_hash**: Hashed refresh token
- **device_info**: JSON object with device information (browser, OS, IP)
- **is_active**: Whether the session is active
- **expires_at**: When the session expires
- **created_at**: When the session was created
- **last_used_at**: When the session was last used

### Email MFA Codes Table Fields
- **id**: Unique code identifier
- **user_id**: Reference to the user
- **code_hash**: Hashed MFA code
- **expires_at**: When the code expires
- **used**: Whether the code has been used
- **created_at**: When the code was created

### MFA Attempts Table Fields
- **id**: Unique attempt identifier
- **user_id**: Reference to the user
- **method**: MFA method used ('totp', 'email', 'backup')
- **success**: Whether the attempt was successful
- **ip_address**: IP address of the attempt
- **user_agent**: User agent string
- **created_at**: When the attempt was made

## Constraints and Validations

### Check Constraints
```sql
-- User type validation
CHECK (user_type IN ('individual', 'business'))

-- Profile status validation
CHECK (profile_status IN ('active', 'inactive', 'suspended', 'pending_verification'))

-- MFA method validation
CHECK (method IN ('totp', 'email', 'backup'))
```

### Foreign Key Constraints
```sql
-- User sessions reference users
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE

-- Email MFA codes reference users
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE

-- MFA attempts reference users
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
```

### Unique Constraints
```sql
-- Email must be unique
UNIQUE (email)

-- Google ID must be unique
UNIQUE (google_id)
```

## Data Types and Sizes

### String Fields
- **VARCHAR(255)**: Names, emails, tokens
- **VARCHAR(20)**: User types, phone numbers
- **VARCHAR(10)**: Language codes
- **VARCHAR(3)**: Currency codes
- **VARCHAR(500)**: URLs (profile pictures)

### Timestamp Fields
- **TIMESTAMP**: All date/time fields
- **Default**: CURRENT_TIMESTAMP for created_at fields

### Boolean Fields
- **BOOLEAN**: True/false flags
- **Default**: FALSE for most boolean fields

### JSON Fields
- **JSONB**: Device information (better performance than JSON)

### Network Fields
- **INET**: IP addresses (supports IPv4 and IPv6)

## Indexes

### Primary Indexes
- All tables have UUID primary keys with gen_random_uuid() default

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

## Triggers

### Updated At Trigger
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
```

## Sample Data

### Sample User Record
```sql
INSERT INTO users (
    full_name,
    email,
    phone,
    user_type,
    language_preference,
    currency_preference,
    profile_status,
    email_verified
) VALUES (
    'John Doe',
    'john.doe@example.com',
    '+37412345678',
    'individual',
    'hy',
    'AMD',
    'active',
    true
);
```

### Sample Session Record
```sql
INSERT INTO user_sessions (
    user_id,
    refresh_token_hash,
    device_info,
    expires_at
) VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'hashed_refresh_token_here',
    '{"browser": "Chrome", "os": "Windows", "ip": "192.168.1.1"}',
    NOW() + INTERVAL '30 days'
);
``` 