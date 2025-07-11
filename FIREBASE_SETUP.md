# Firebase Authentication Setup Guide

This guide will help you set up Firebase Authentication for Google login in your Personal Finance Manager app.

## Step 1: Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project" or "Add project"
3. Enter a project name (e.g., "personal-finance-manager")
4. Choose whether to enable Google Analytics (optional)
5. Click "Create project"

## Step 2: Enable Authentication

1. In your Firebase project, go to "Authentication" in the left sidebar
2. Click "Get started"
3. Go to the "Sign-in method" tab
4. Click on "Google" provider
5. Enable it and configure:
   - **Project support email**: Your email address
   - **Web SDK configuration**: Add your domain (localhost for development)
6. Click "Save"

## Step 3: Get Firebase Configuration

1. In Firebase Console, go to "Project settings" (gear icon)
2. Scroll down to "Your apps" section
3. Click "Add app" and select "Web" (</>)
4. Register your app with a nickname (e.g., "PFM Web App")
5. Copy the Firebase configuration object

## Step 4: Update Frontend Configuration

1. Open `frontend/firebase-config.js`
2. Replace the placeholder configuration with your actual Firebase config:

```javascript
const firebaseConfig = {
    apiKey: "your-actual-api-key",
    authDomain: "your-project.firebaseapp.com",
    projectId: "your-project-id",
    storageBucket: "your-project.appspot.com",
    messagingSenderId: "123456789",
    appId: "your-app-id"
};
```

## Step 5: Get Service Account Key

1. In Firebase Console, go to "Project settings"
2. Go to "Service accounts" tab
3. Click "Generate new private key"
4. Download the JSON file
5. **IMPORTANT**: Keep this file secure and never commit it to version control

## Step 6: Configure Backend

You have two options for providing the service account key to your backend:

### Option A: Environment Variable (Recommended for Production)

1. Convert the service account JSON to a single line:
   ```bash
   cat your-service-account-key.json | jq -c '.' | tr -d '\n'
   ```

2. Add to your `.env` file:
   ```
   FIREBASE_SERVICE_ACCOUNT_JSON='{"type":"service_account","project_id":"...","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"...","client_id":"...","auth_uri":"...","token_uri":"...","auth_provider_x509_cert_url":"...","client_x509_cert_url":"..."}'
   ```

### Option B: File Path (Good for Development)

1. Save the service account JSON file in your project (e.g., `firebase-service-account.json`)
2. Add to your `.env` file:
   ```
   FIREBASE_SERVICE_ACCOUNT_KEY_PATH=./firebase-service-account.json
   ```

## Step 7: Update Database Schema

The database schema has been updated to include Firebase UID support. If you're running this on an existing database, you'll need to add the column:

```sql
ALTER TABLE users ADD COLUMN firebase_uid VARCHAR(255) UNIQUE;
CREATE INDEX idx_users_firebase_uid ON users(firebase_uid);
```

## Step 8: Install Dependencies

Make sure you have the Firebase Admin SDK installed:

```bash
pip install firebase-admin==6.2.0
```

## Step 9: Test the Implementation

1. Start your backend server
2. Open the frontend in your browser
3. Click "Sign in with Google"
4. Complete the Google authentication flow
5. Verify that the user is created in your database

## Troubleshooting

### Common Issues:

1. **"Firebase App named '[DEFAULT]' already exists"**
   - This is normal if Firebase is already initialized
   - The code handles this automatically

2. **"Invalid Firebase token"**
   - Check that your service account key is correct
   - Verify the Firebase project ID matches

3. **"Google sign-in error"**
   - Make sure Google provider is enabled in Firebase Console
   - Check that your domain is authorized

4. **CORS errors**
   - Add your frontend domain to Firebase authorized domains
   - For development: `localhost`, `127.0.0.1`

### Security Best Practices:

1. **Never commit service account keys** to version control
2. **Use environment variables** for sensitive configuration
3. **Restrict Firebase rules** to only necessary permissions
4. **Monitor authentication logs** in Firebase Console
5. **Set up proper CORS** for production domains

## Production Deployment

For production deployment:

1. **Update authorized domains** in Firebase Console
2. **Use environment variables** for all sensitive data
3. **Set up proper CORS** configuration
4. **Monitor authentication** in Firebase Console
5. **Set up Firebase App Check** for additional security

## Additional Features

Once Firebase Authentication is working, you can easily add:

- **Facebook Login**: Enable Facebook provider in Firebase Console
- **Apple Sign-In**: Enable Apple provider (requires Apple Developer account)
- **Phone Authentication**: Enable phone number sign-in
- **Email Link Authentication**: Passwordless email sign-in

## Support

If you encounter issues:

1. Check Firebase Console logs
2. Verify your configuration matches this guide
3. Check browser console for JavaScript errors
4. Review backend logs for authentication errors
5. Ensure all environment variables are set correctly 