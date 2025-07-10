# MFA Demo Frontend

A simple HTML/CSS/JavaScript frontend to demonstrate the complete TOTP and Email MFA workflow for the Personal Finance Manager backend.

## Features

- **User Authentication**: Login with email/password
- **TOTP MFA**: Setup, verify, and disable TOTP (Google Authenticator)
- **Email MFA**: Setup, send codes, verify, and disable email MFA
- **Backup Codes**: Verify backup codes for account recovery
- **MFA Status**: View current MFA configuration and backup codes remaining
- **Responsive Design**: Works on desktop and mobile
- **Modern UI**: Clean, professional interface with helpful instructions

## Setup

1. **Start the backend server**:
   ```bash
   cd /path/to/your/backend
   ./scripts/dev.sh start
   ```

2. **Open the frontend**:
   - Open `frontend/index.html` in your web browser
   - Or serve it with a simple HTTP server:
     ```bash
     cd frontend
     python -m http.server 8080
     # Then visit http://localhost:8080
     ```

## Usage

### 1. Registration & Login
- **Register**: Create a new account with email, password, and user details
- **Login**: Enter your credentials to authenticate
- **MFA Login**: If MFA is enabled, you'll be prompted for a verification code

### 2. TOTP Setup & Management
1. **Setup TOTP**:
   - Click "Setup TOTP" button
   - Scan the QR code with your authenticator app (Google Authenticator, Authy, etc.)
   - Save the backup codes shown (important for account recovery)
   - Enter the 6-digit code from your app
   - Click "Verify & Enable TOTP"

2. **Disable TOTP**:
   - Enter a valid TOTP code from your authenticator app
   - Click "Disable TOTP"

### 3. Email MFA
1. **Enable Email MFA**:
   - Click "Enable Email MFA"
   - Enter your email address
   - Click "Send Code" to receive a verification code
   - Enter the 6-digit code from your email
   - Click "Verify Email Code"

2. **Disable Email MFA**:
   - Click "Disable Email MFA"

### 4. Backup Codes
- **Use Backup Codes**: Enter an 8-digit backup code to verify it works
- **Account Recovery**: Backup codes can be used if you lose access to TOTP/email MFA

### 5. MFA Status
- **View Status**: Check current MFA configuration
- **Refresh**: Click "Refresh Status" to update the display
- **Backup Codes**: See how many backup codes remain

## API Endpoints Used

The frontend demonstrates these backend endpoints:

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/mfa/verify` - MFA verification during login

### MFA Management
- `GET /api/v1/mfa/status` - Get MFA status
- `POST /api/v1/mfa/totp/setup` - Setup TOTP
- `POST /api/v1/mfa/totp/verify` - Verify TOTP setup
- `POST /api/v1/mfa/totp/disable` - Disable TOTP
- `POST /api/v1/mfa/email/setup` - Setup email MFA
- `POST /api/v1/mfa/email/send-code` - Send email code
- `POST /api/v1/mfa/email/verify` - Verify email code
- `POST /api/v1/mfa/email/disable` - Disable email MFA
- `POST /api/v1/mfa/backup/verify` - Verify backup code

## Demo Workflow

### Complete MFA Flow
1. **Register** a new account
2. **Login** with your credentials
3. **Setup TOTP** by scanning the QR code
4. **Logout** and login again
5. **Verify MFA** with your authenticator app
6. **Test Email MFA** as an alternative
7. **Try Backup Codes** for account recovery

### Testing Scenarios
- **Normal Login**: Users without MFA enabled
- **MFA Login**: Users with TOTP or email MFA enabled
- **MFA Setup**: First-time MFA configuration
- **MFA Management**: Enable/disable different MFA methods
- **Account Recovery**: Using backup codes

## Security Features

- **JWT Tokens**: Secure authentication with access and refresh tokens
- **MFA Verification**: Two-factor authentication for enhanced security
- **Backup Codes**: Account recovery mechanism
- **Rate Limiting**: Protection against brute force attacks
- **Encrypted Secrets**: TOTP secrets encrypted at rest

## Browser Compatibility

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Development

### File Structure
```
frontend/
├── index.html          # Main HTML file
├── styles.css          # CSS styles
├── script.js           # JavaScript functionality
├── README.md           # This file
└── test-workflow.md    # API testing guide
```

### Customization
- **Styling**: Modify `styles.css` for different themes
- **Functionality**: Update `script.js` for additional features
- **API Endpoints**: Change `API_BASE_URL` in `script.js` for different environments

## Troubleshooting

### Common Issues
1. **CORS Errors**: Ensure the backend is running and accessible
2. **API Errors**: Check browser console for detailed error messages
3. **MFA Setup Fails**: Verify the QR code is scanned correctly
4. **Email Codes**: Check spam folder for MFA codes

### Debug Mode
Open browser developer tools (F12) to see:
- Network requests and responses
- JavaScript console logs
- Error messages and stack traces

## Next Steps

Once you've verified everything works:

1. **Show your frontend developer** the complete workflow
2. **Explain the API integration** patterns
3. **Discuss production considerations** (security, styling, etc.)
4. **Move on to Google OAuth** implementation 