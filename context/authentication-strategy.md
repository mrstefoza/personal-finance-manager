# Authentication Strategy

## Overview
Comprehensive authentication system with JWT tokens, OAuth integration, and multi-factor authentication.

## JWT Token Strategy

### Token Types
1. **Access Token**
   - **Duration**: 15-30 minutes
   - **Purpose**: API authentication
   - **Storage**: Client-side (memory/cookies)
   - **Claims**: User ID, permissions, expiration

2. **Refresh Token**
   - **Duration**: 7-30 days
   - **Purpose**: Obtain new access tokens
   - **Storage**: Database (hashed)
   - **Claims**: User ID, session ID, expiration

### Token Structure
```json
{
  "sub": "user_id",
  "exp": 1640995200,
  "iat": 1640991600,
  "type": "access|refresh",
  "session_id": "session_uuid"
}
```

### Token Management
- **Issuance**: Login, token refresh
- **Validation**: Middleware on protected routes
- **Revocation**: Database lookup for refresh tokens
- **Rotation**: New refresh token on each use

## OAuth Integration

### Google OAuth Flow
1. **Authorization Request**
   ```
   GET https://accounts.google.com/oauth/authorize
   ?client_id=YOUR_CLIENT_ID
   &redirect_uri=YOUR_REDIRECT_URI
   &response_type=code
   &scope=email profile
   ```

2. **Token Exchange**
   ```
   POST https://oauth2.googleapis.com/token
   {
     "client_id": "YOUR_CLIENT_ID",
     "client_secret": "YOUR_CLIENT_SECRET",
     "code": "AUTHORIZATION_CODE",
     "grant_type": "authorization_code",
     "redirect_uri": "YOUR_REDIRECT_URI"
   }
   ```

3. **User Info Retrieval**
   ```
   GET https://www.googleapis.com/oauth2/v2/userinfo
   Authorization: Bearer ACCESS_TOKEN
   ```

### OAuth User Management
- **Account Linking**: Link OAuth to existing email account
- **Account Creation**: Create new account from OAuth data
- **Profile Sync**: Update profile from OAuth provider

## Multi-Factor Authentication (MFA)

### TOTP (Time-based One-Time Password)
- **Algorithm**: TOTP (RFC 6238)
- **Secret**: 32-character base32 encoded
- **Time Window**: 30 seconds
- **Digits**: 6 digits
- **Tolerance**: ±1 time window for clock skew

### Email MFA
- **Code Generation**: 6-8 digit random code
- **Expiration**: 5-10 minutes
- **Rate Limiting**: Max 3 attempts per code
- **Template**: Professional email with code

### Backup Codes
- **Generation**: 10 codes, 8 characters each
- **Storage**: Encrypted in database
- **Usage**: One-time use, marked as used
- **Regeneration**: User can generate new codes

## Authentication Flow

### Email/Password Registration
```
1. User submits registration form
2. Validate email uniqueness
3. Hash password with bcrypt
4. Generate email verification token
5. Send verification email
6. Create user with pending_verification status
7. Return success response
```

### Email/Password Login
```
1. User submits login credentials
2. Validate email and password
3. Check account status and lockout
4. If MFA enabled:
   a. Generate MFA challenge
   b. Return MFA required response
5. If MFA disabled or verified:
   a. Generate access and refresh tokens
   b. Create session record
   c. Update last_login
   d. Return tokens
```

### Google OAuth Login
```
1. User initiates OAuth flow
2. Redirect to Google authorization
3. Handle OAuth callback
4. Exchange code for tokens
5. Retrieve user info from Google
6. Find or create user account
7. Generate application tokens
8. Return tokens to client
```

### MFA Verification
```
1. User submits MFA code
2. Validate code based on method:
   a. TOTP: Verify with pyotp
   b. Email: Check database code
   c. Backup: Verify and mark used
3. Check rate limiting
4. Log attempt (success/failure)
5. If successful: Complete login
6. If failed: Increment failed attempts
```

## Security Measures

### Password Security
- **Hashing**: bcrypt with cost factor 12
- **Validation**: Minimum 8 characters, complexity rules
- **Rate Limiting**: Max 5 failed attempts per hour
- **Account Lockout**: 15-minute lockout after 5 failures

### Token Security
- **Signing**: HMAC-SHA256 with strong secret
- **Encryption**: Sensitive claims encrypted
- **Storage**: Refresh tokens hashed in database
- **Rotation**: Refresh tokens rotated on use

### MFA Security
- **Secret Storage**: TOTP secrets encrypted at rest
- **Rate Limiting**: Max 3 MFA attempts per 5 minutes
- **Code Expiration**: Short-lived codes
- **Backup Codes**: Encrypted storage

### Session Security
- **Device Tracking**: Store device information
- **Session Limits**: Max 5 active sessions per user
- **Automatic Cleanup**: Remove expired sessions
- **Revocation**: User can revoke individual sessions

## API Endpoints

### Authentication Endpoints
```
POST /api/v1/auth/register          # User registration
POST /api/v1/auth/login             # Email/password login
POST /api/v1/auth/refresh           # Refresh access token
POST /api/v1/auth/logout            # Logout and revoke tokens
POST /api/v1/auth/verify-email      # Email verification
POST /api/v1/auth/forgot-password   # Password reset request
POST /api/v1/auth/reset-password    # Password reset
```

### OAuth Endpoints
```
GET  /api/v1/auth/google/login      # Initiate Google OAuth
POST /api/v1/auth/google/callback   # Handle OAuth callback
POST /api/v1/auth/link-google       # Link Google to existing account
```

### MFA Endpoints
```
POST /api/v1/mfa/setup              # Initialize MFA setup
POST /api/v1/mfa/verify-totp        # Verify TOTP during setup
POST /api/v1/mfa/verify-email       # Verify email during setup
POST /api/v1/mfa/enable             # Enable MFA
POST /api/v1/mfa/disable            # Disable MFA
POST /api/v1/mfa/login/totp         # TOTP during login
POST /api/v1/mfa/login/email        # Email MFA during login
POST /api/v1/mfa/backup-codes       # Generate backup codes
POST /api/v1/mfa/verify-backup      # Use backup code
```

## Error Handling

### Authentication Errors
```json
{
  "error": "authentication_failed",
  "message": "Invalid email or password",
  "details": {
    "remaining_attempts": 3,
    "lockout_until": null
  }
}
```

### MFA Errors
```json
{
  "error": "mfa_required",
  "message": "Multi-factor authentication required",
  "details": {
    "methods": ["totp", "email"],
    "challenge_id": "challenge_uuid"
  }
}
```

### Rate Limiting Errors
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many attempts",
  "details": {
    "retry_after": 300,
    "attempts_remaining": 0
  }
}
```

## Implementation Considerations

### Performance
- **Token Validation**: JWT signature verification (fast)
- **Database Queries**: Minimal queries for authentication
- **Caching**: Cache user permissions and session data
- **Async Operations**: Non-blocking authentication flows

### Scalability
- **Stateless**: JWT tokens work across multiple servers
- **Database**: Efficient indexing for session lookups
- **Rate Limiting**: Distributed rate limiting with Redis
- **Session Management**: Centralized session storage

### Monitoring
- **Login Attempts**: Track success/failure rates
- **MFA Usage**: Monitor MFA adoption and success rates
- **Token Usage**: Monitor token refresh patterns
- **Security Events**: Alert on suspicious activities 