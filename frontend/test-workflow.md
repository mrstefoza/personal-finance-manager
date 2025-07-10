# MFA Test Workflow

This guide will help you test the complete TOTP MFA system step by step, including user registration.

## Prerequisites

1. **Backend is running**: `./scripts/dev.sh start`
2. **Frontend is accessible**: Open `frontend/index.html` in your browser
3. **Authenticator app**: Install Google Authenticator, Authy, or similar on your phone

## Step 1: Test User Registration

1. **Open the frontend**: Open `frontend/index.html` in your browser
2. **Click "Register" tab**: Switch to the registration form
3. **Fill out the form**:
   - Full Name: `Test User`
   - Email: `test@example.com`
   - Phone: `+1234567890`
   - User Type: `Individual`
   - Password: `TestPass123!`
   - Confirm Password: `TestPass123!`
4. **Click "Register"**: You should see a success message
5. **Auto-switch to login**: The form should automatically switch to the login tab after 2 seconds

## Step 2: Test Login

1. **Login with registered credentials**:
   - Email: `test@example.com`
   - Password: `TestPass123!`
2. **Click "Login"**: You should be authenticated and see the MFA sections
3. **Check MFA Status**: You should see all MFA methods are disabled

## Step 3: Test TOTP Setup

1. **Click "Setup TOTP"**
2. **Scan QR Code**: Use your authenticator app to scan the displayed QR code
3. **Enter Code**: Enter the 6-digit code from your app
4. **Verify**: Click "Verify & Enable TOTP"
5. **Check Status**: The MFA status should now show TOTP as enabled

## Step 4: Test TOTP Verification

1. **Enter TOTP Code**: In the TOTP Management section, enter a code from your app
2. **Disable TOTP**: Click "Disable TOTP" to test the verification
3. **Check Status**: TOTP should now be disabled

## Step 5: Test Email MFA

1. **Enable Email MFA**: Click "Enable Email MFA"
2. **Send Code**: Enter your email and click "Send Code"
3. **Check Response**: The code will be shown in the response (for demo purposes)
4. **Verify Code**: Enter the code and click "Verify Email Code"

## Step 6: Test Backup Codes

1. **Setup TOTP again**: Follow step 3 to re-enable TOTP
2. **Use Backup Code**: In the backup codes section, enter one of the backup codes shown during TOTP setup
3. **Verify**: Click "Verify Backup Code"

## Step 7: Test Logout and Re-login

1. **Click "Logout"**: You should be returned to the login form
2. **Login again**: Use the same credentials to verify persistence
3. **Check MFA Status**: Your MFA settings should still be active

## Expected Results

- ✅ Registration works with form validation
- ✅ Login works with JWT tokens
- ✅ TOTP setup generates QR code and secret
- ✅ TOTP verification works with authenticator app
- ✅ Email MFA sends and verifies codes
- ✅ Backup codes work for recovery
- ✅ MFA status updates correctly
- ✅ All operations require authentication
- ✅ Logout clears session and returns to login

## Form Validation Tests

### Registration Validation
- **Password requirements**: Try passwords without uppercase, lowercase, or digits
- **Password confirmation**: Try mismatched passwords
- **Email format**: Try invalid email addresses
- **Required fields**: Try submitting with empty fields
- **Phone format**: Try invalid phone numbers

### Login Validation
- **Invalid credentials**: Try wrong email/password combinations
- **Empty fields**: Try submitting with empty email or password

## Troubleshooting

### Common Issues

1. **CORS Errors**: Make sure the backend is running on `localhost:8000`
2. **QR Code Not Working**: Try manually entering the secret in your authenticator app
3. **API Errors**: Check the browser console for detailed error messages
4. **Token Expired**: Logout and login again
5. **Registration Errors**: Check that the email isn't already registered

### Manual Testing with curl

You can also test the API directly:

```bash
# Register a user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "email": "test@example.com",
    "phone": "+1234567890",
    "user_type": "individual",
    "password": "TestPass123!"
  }'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123!"}'

# Get MFA status (use the access_token from login)
curl -X GET "http://localhost:8000/api/v1/mfa/status" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Setup TOTP
curl -X POST "http://localhost:8000/api/v1/mfa/totp/setup" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Next Steps

Once you've verified everything works:

1. **Show your frontend developer** the complete workflow
2. **Explain the API integration** patterns
3. **Discuss production considerations** (security, styling, etc.)
4. **Move on to Google OAuth** implementation 