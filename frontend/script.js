// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Global state
let authToken = null;
let currentUser = null;
let tempToken = null; // For MFA verification during login
let mfaType = null; // Type of MFA required ("totp" or "email")

// Utility functions
function showMessage(elementId, message, type = 'info') {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.className = `message ${type}`;
    element.style.display = 'block';
    
    // Auto-hide success messages after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            element.style.display = 'none';
        }, 5000);
    }
}

function hideMessage(elementId) {
    const element = document.getElementById(elementId);
    element.style.display = 'none';
}

function showSection(sectionId) {
    document.getElementById(sectionId).style.display = 'block';
}

function hideSection(sectionId) {
    document.getElementById(sectionId).style.display = 'none';
}

function setLoading(button, isLoading) {
    if (isLoading) {
        button.disabled = true;
        button.textContent = 'Loading...';
    } else {
        button.disabled = false;
        button.textContent = button.getAttribute('data-original-text') || button.textContent;
    }
}

// Form validation functions
function validatePassword(password) {
    const minLength = password.length >= 8;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasDigit = /\d/.test(password);
    
    return minLength && hasUpperCase && hasLowerCase && hasDigit;
}

function validateRegistrationForm(formData) {
    const errors = [];
    
    // Check password requirements
    if (!validatePassword(formData.password)) {
        errors.push('Password must be at least 8 characters with uppercase, lowercase, and digit');
    }
    
    // Check password confirmation
    if (formData.password !== formData.confirm_password) {
        errors.push('Passwords do not match');
    }
    
    // Check email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
        errors.push('Please enter a valid email address');
    }
    
    // Check phone format (basic validation)
    const phoneRegex = /^\+?[\d\s\-\(\)]+$/;
    if (!phoneRegex.test(formData.phone)) {
        errors.push('Please enter a valid phone number');
    }
    
    // Check required fields
    if (!formData.full_name.trim()) {
        errors.push('Full name is required');
    }
    
    if (!formData.user_type) {
        errors.push('Please select a user type');
    }
    
    return errors;
}

// Tab switching functions
function switchToLogin() {
    document.getElementById('login-tab').classList.add('active');
    document.getElementById('register-tab').classList.remove('active');
    document.getElementById('login-form-container').style.display = 'block';
    document.getElementById('register-form-container').style.display = 'none';
    hideMessage('login-message');
    hideMessage('register-message');
}

function switchToRegister() {
    document.getElementById('register-tab').classList.add('active');
    document.getElementById('login-tab').classList.remove('active');
    document.getElementById('register-form-container').style.display = 'block';
    document.getElementById('login-form-container').style.display = 'none';
    hideMessage('login-message');
    hideMessage('register-message');
}

// API functions
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    };

    if (authToken) {
        config.headers['Authorization'] = `Bearer ${authToken}`;
    }

    try {
        const response = await fetch(url, config);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || `HTTP ${response.status}: ${response.statusText}`);
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Authentication functions
async function register(userData) {
    try {
        const response = await apiRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
        
        return response;
    } catch (error) {
        throw error;
    }
}

async function login(email, password) {
    try {
        // Check if we have a stored MFA session token
        const mfaSessionToken = localStorage.getItem('mfaSessionToken');
        
        const loginData = { email, password };
        if (mfaSessionToken) {
            loginData.mfa_session_token = mfaSessionToken;
        }
        
        const response = await apiRequest('/auth/login', {
            method: 'POST',
            body: JSON.stringify(loginData)
        });

        if (response.requires_mfa) {
            // MFA is required, store temporary token and show MFA verification
            tempToken = response.temp_token;
            mfaType = response.mfa_type;
            currentUser = { email };
            
            // Show MFA verification form
            showMFAVerification();
            return response;
        } else {
            // No MFA required, proceed with normal login
            authToken = response.access_token;
            currentUser = { email };
            
            // Store token in localStorage
            localStorage.setItem('authToken', authToken);
            
            return response;
        }
    } catch (error) {
        throw error;
    }
}

async function verifyMFALogin(code, rememberDevice = false) {
    try {
        const response = await apiRequest('/auth/mfa/verify', {
            method: 'POST',
            body: JSON.stringify({
                temp_token: tempToken,
                code: code,
                mfa_type: mfaType,
                remember_device: rememberDevice
            })
        });

        // MFA verification successful, store tokens
        authToken = response.access_token;
        localStorage.setItem('authToken', authToken);
        
        // Store MFA session token if provided
        if (response.mfa_session_token) {
            localStorage.setItem('mfaSessionToken', response.mfa_session_token);
        }
        
        // Clear temporary data
        tempToken = null;
        mfaType = null;
        
        return response;
    } catch (error) {
        throw error;
    }
}

function showMFAVerification() {
    // Hide login form, show MFA verification
    document.getElementById('login-form-container').style.display = 'none';
    document.getElementById('mfa-verification-container').style.display = 'block';
    
    // Update instruction based on MFA type
    const instruction = document.getElementById('mfa-verification-instruction');
    if (mfaType === 'totp') {
        instruction.textContent = 'Please enter the 6-digit code from your authenticator app.';
    } else if (mfaType === 'email') {
        instruction.textContent = 'Please enter the 6-digit code sent to your email.';
    }
    
    // Clear any previous messages
    hideMessage('mfa-verification-message');
}

function hideMFAVerification() {
    // Hide MFA verification, show login form
    document.getElementById('mfa-verification-container').style.display = 'none';
    document.getElementById('login-form-container').style.display = 'block';
    
    // Clear form
    document.getElementById('mfa-verification-code').value = '';
    hideMessage('mfa-verification-message');
    
    // Clear temporary data
    tempToken = null;
    mfaType = null;
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('mfaSessionToken');
    
    // Show auth section, hide others
    showSection('auth-section');
    hideSection('mfa-status-section');
    hideSection('totp-setup-section');
    hideSection('totp-management-section');
    hideSection('email-mfa-section');
    hideSection('backup-codes-section');
    hideSection('logout-section');
    
    // Clear forms
    document.getElementById('login-form').reset();
    document.getElementById('register-form').reset();
    
    // Switch to login tab
    switchToLogin();
}

// MFA functions
async function getMFAStatus() {
    try {
        const status = await apiRequest('/mfa/status');
        
        document.getElementById('totp-status').textContent = status.totp_enabled ? 'Yes' : 'No';
        document.getElementById('email-mfa-status').textContent = status.email_mfa_enabled ? 'Yes' : 'No';
        document.getElementById('mfa-required-status').textContent = status.mfa_required ? 'Yes' : 'No';
        document.getElementById('backup-codes-remaining').textContent = status.backup_codes_remaining || 0;
        
        return status;
    } catch (error) {
        console.error('Failed to get MFA status:', error);
        showMessage('login-message', `Failed to get MFA status: ${error.message}`, 'error');
        throw error;
    }
}

async function setupTOTP() {
    try {
        const response = await apiRequest('/mfa/totp/setup', {
            method: 'POST',
            body: JSON.stringify({})
        });

        // Display QR code (using a QR code generator service)
        const qrCodeUrl = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(response.qr_code_url)}`;
        
        const qrContainer = document.getElementById('qr-code-container');
        qrContainer.innerHTML = `<img src="${qrCodeUrl}" alt="QR Code">`;
        
        // Display secret and backup codes
        document.getElementById('totp-secret').textContent = response.secret;
        
        const backupCodesList = document.getElementById('backup-codes');
        backupCodesList.innerHTML = '';
        response.backup_codes.forEach(code => {
            const li = document.createElement('li');
            li.textContent = code;
            backupCodesList.appendChild(li);
        });

        // Show the setup result
        document.getElementById('totp-setup-result').style.display = 'block';
        
        showMessage('totp-setup-message', 'TOTP setup initiated. Scan the QR code with your authenticator app.', 'info');
        
        return response;
    } catch (error) {
        showMessage('totp-setup-message', `Failed to setup TOTP: ${error.message}`, 'error');
        throw error;
    }
}

async function verifyTOTPSetup(code) {
    try {
        const response = await apiRequest('/mfa/totp/verify', {
            method: 'POST',
            body: JSON.stringify({ code })
        });

        showMessage('totp-setup-message', 'TOTP enabled successfully!', 'success');
        
        // Hide setup result and refresh status
        document.getElementById('totp-setup-result').style.display = 'none';
        await getMFAStatus();
        
        return response;
    } catch (error) {
        showMessage('totp-setup-message', `Failed to verify TOTP: ${error.message}`, 'error');
        throw error;
    }
}

async function disableTOTP(code) {
    try {
        const response = await apiRequest('/mfa/totp/disable', {
            method: 'POST',
            body: JSON.stringify({ code })
        });

        showMessage('totp-management-message', 'TOTP disabled successfully!', 'success');
        
        // Clear the input and refresh status
        document.getElementById('totp-disable-code').value = '';
        await getMFAStatus();
        
        return response;
    } catch (error) {
        showMessage('totp-management-message', `Failed to disable TOTP: ${error.message}`, 'error');
        throw error;
    }
}

async function setupEmailMFA() {
    try {
        const response = await apiRequest('/mfa/email/setup', {
            method: 'POST',
            body: JSON.stringify({})
        });

        showMessage('email-mfa-message', 'Email MFA enabled successfully!', 'success');
        await getMFAStatus();
        
        return response;
    } catch (error) {
        showMessage('email-mfa-message', `Failed to setup email MFA: ${error.message}`, 'error');
        throw error;
    }
}

async function disableEmailMFA() {
    try {
        const response = await apiRequest('/mfa/email/disable', {
            method: 'POST',
            body: JSON.stringify({})
        });

        showMessage('email-mfa-message', 'Email MFA disabled successfully!', 'success');
        await getMFAStatus();
        
        return response;
    } catch (error) {
        showMessage('email-mfa-message', `Failed to disable email MFA: ${error.message}`, 'error');
        throw error;
    }
}

async function sendEmailCode(email) {
    try {
        const response = await apiRequest('/mfa/email/send-code', {
            method: 'POST',
            body: JSON.stringify({ email })
        });

        showMessage('email-mfa-message', response.message, 'info');
        
        return response;
    } catch (error) {
        showMessage('email-mfa-message', `Failed to send email code: ${error.message}`, 'error');
        throw error;
    }
}

async function verifyEmailCode(code) {
    try {
        const response = await apiRequest('/mfa/email/verify', {
            method: 'POST',
            body: JSON.stringify({ code })
        });

        showMessage('email-mfa-message', 'Email code verified successfully!', 'success');
        
        // Clear the input
        document.getElementById('email-verify-code').value = '';
        
        return response;
    } catch (error) {
        showMessage('email-mfa-message', `Failed to verify email code: ${error.message}`, 'error');
        throw error;
    }
}

async function verifyBackupCode(code) {
    try {
        const response = await apiRequest('/mfa/backup/verify', {
            method: 'POST',
            body: JSON.stringify({ code })
        });

        showMessage('backup-message', 'Backup code verified successfully!', 'success');
        
        // Clear the input
        document.getElementById('backup-code').value = '';
        
        return response;
    } catch (error) {
        showMessage('backup-message', `Failed to verify backup code: ${error.message}`, 'error');
        throw error;
    }
}

// OAuth functions
async function initiateGoogleOAuth() {
    try {
        // Get the OAuth URL from the backend
        const redirectUri = `${window.location.origin}/oauth-callback.html`;
        const response = await apiRequest('/auth/google/auth-url', {
            method: 'POST',
            body: JSON.stringify({ redirect_uri: redirectUri })
        });

        // Store the redirect URI for the callback
        localStorage.setItem('oauth_redirect_uri', redirectUri);
        
        // Redirect to Google OAuth
        window.location.href = response.auth_url;
        
    } catch (error) {
        throw error;
    }
}

async function handleGoogleOAuthCallback(code) {
    try {
        const redirectUri = localStorage.getItem('oauth_redirect_uri') || `${window.location.origin}/oauth-callback.html`;
        
        const response = await apiRequest('/auth/google/callback', {
            method: 'POST',
            body: JSON.stringify({ 
                code: code, 
                redirect_uri: redirectUri 
            })
        });

        // Clear the stored redirect URI
        localStorage.removeItem('oauth_redirect_uri');

        if (response.requires_mfa) {
            // MFA is required, store temporary token and show MFA verification
            tempToken = response.temp_token;
            mfaType = response.mfa_type;
            currentUser = response.user;
            
            // Show MFA verification form
            showMFAVerification();
            return response;
        } else {
            // No MFA required, proceed with normal login
            authToken = response.access_token;
            currentUser = response.user;
            
            // Store token in localStorage
            localStorage.setItem('authToken', authToken);
            
            // Complete login
            onLoginSuccess();
            return response;
        }
        
    } catch (error) {
        throw error;
    }
}

// Check for OAuth callback on page load
function checkForOAuthCallback() {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const error = urlParams.get('error');
    
    if (error) {
        showMessage('login-message', `OAuth error: ${error}`, 'error');
        return;
    }
    
    if (code) {
        // Handle OAuth callback
        handleGoogleOAuthCallback(code).catch(error => {
            console.error('OAuth callback failed:', error);
            showMessage('login-message', `OAuth callback failed: ${error.message}`, 'error');
        });
    }
}

// Event handlers
document.addEventListener('DOMContentLoaded', function() {
    // Check for OAuth callback first
    checkForOAuthCallback();
    
    // Check if user is already logged in
    const savedToken = localStorage.getItem('authToken');
    if (savedToken) {
        authToken = savedToken;
        onLoginSuccess();
    }

    // Tab switching
    document.getElementById('login-tab').addEventListener('click', switchToLogin);
    document.getElementById('register-tab').addEventListener('click', switchToRegister);

    // Registration form
    document.getElementById('register-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = {
            full_name: document.getElementById('register-full-name').value,
            email: document.getElementById('register-email').value,
            phone: document.getElementById('register-phone').value,
            user_type: document.getElementById('register-user-type').value,
            password: document.getElementById('register-password').value,
            confirm_password: document.getElementById('register-confirm-password').value,
            language_preference: 'en',
            currency_preference: 'USD'
        };
        
        const submitButton = this.querySelector('button[type="submit"]');
        
        setLoading(submitButton, true);
        hideMessage('register-message');
        
        try {
            // Validate form
            const errors = validateRegistrationForm(formData);
            if (errors.length > 0) {
                showMessage('register-message', errors.join('. '), 'error');
                return;
            }
            
            // Register user
            await register(formData);
            showMessage('register-message', 'Registration successful! You can now login.', 'success');
            
            // Clear form and switch to login
            this.reset();
            setTimeout(() => {
                switchToLogin();
            }, 2000);
            
        } catch (error) {
            showMessage('register-message', `Registration failed: ${error.message}`, 'error');
        } finally {
            setLoading(submitButton, false);
        }
    });

    // Login form
    document.getElementById('login-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        const submitButton = this.querySelector('button[type="submit"]');
        
        setLoading(submitButton, true);
        hideMessage('login-message');
        
        try {
            const response = await login(email, password);
            
            if (response.requires_mfa) {
                // MFA verification will be handled by showMFAVerification()
                showMessage('login-message', 'MFA verification required. Please enter your code.', 'info');
            } else {
                // Normal login success
                onLoginSuccess();
            }
        } catch (error) {
            showMessage('login-message', `Login failed: ${error.message}`, 'error');
        } finally {
            setLoading(submitButton, false);
        }
    });

    // MFA verification button
    document.getElementById('mfa-verify-btn').addEventListener('click', async function() {
        const code = document.getElementById('mfa-verification-code').value;
        if (!code || code.length !== 6) {
            showMessage('mfa-verification-message', 'Please enter a valid 6-digit code', 'error');
            return;
        }

        const rememberDevice = document.getElementById('remember-device-checkbox').checked;

        const button = this;
        setLoading(button, true);
        hideMessage('mfa-verification-message');
        
        try {
            await verifyMFALogin(code, rememberDevice);
            onLoginSuccess();
        } catch (error) {
            showMessage('mfa-verification-message', `MFA verification failed: ${error.message}`, 'error');
        } finally {
            setLoading(button, false);
        }
    });

    // Back to login button
    document.getElementById('mfa-back-to-login-btn').addEventListener('click', function() {
        hideMFAVerification();
        hideMessage('login-message');
    });

    // Google OAuth login button
    document.getElementById('google-login-btn').addEventListener('click', async function() {
        const button = this;
        setLoading(button, true);
        try {
            await initiateGoogleOAuth();
        } catch (error) {
            console.error('Failed to initiate Google OAuth:', error);
            showMessage('login-message', `Google OAuth failed: ${error.message}`, 'error');
        } finally {
            setLoading(button, false);
        }
    });

    // Logout button
    document.getElementById('logout-btn').addEventListener('click', logout);

    // Refresh status button
    document.getElementById('refresh-status-btn').addEventListener('click', async function() {
        const button = this;
        setLoading(button, true);
        try {
            await getMFAStatus();
        } catch (error) {
            console.error('Failed to refresh status:', error);
        } finally {
            setLoading(button, false);
        }
    });

    // TOTP setup button
    document.getElementById('setup-totp-btn').addEventListener('click', async function() {
        const button = this;
        setLoading(button, true);
        try {
            await setupTOTP();
        } catch (error) {
            console.error('Failed to setup TOTP:', error);
        } finally {
            setLoading(button, false);
        }
    });

    // TOTP verify button
    document.getElementById('verify-totp-btn').addEventListener('click', async function() {
        const code = document.getElementById('totp-verify-code').value;
        if (!code || code.length !== 6) {
            showMessage('totp-setup-message', 'Please enter a valid 6-digit code', 'error');
            return;
        }

        const button = this;
        setLoading(button, true);
        try {
            await verifyTOTPSetup(code);
        } catch (error) {
            console.error('Failed to verify TOTP:', error);
        } finally {
            setLoading(button, false);
        }
    });

    // TOTP disable button
    document.getElementById('disable-totp-btn').addEventListener('click', async function() {
        const code = document.getElementById('totp-disable-code').value;
        if (!code || code.length !== 6) {
            showMessage('totp-management-message', 'Please enter a valid 6-digit code', 'error');
            return;
        }

        const button = this;
        setLoading(button, true);
        try {
            await disableTOTP(code);
        } catch (error) {
            console.error('Failed to disable TOTP:', error);
        } finally {
            setLoading(button, false);
        }
    });

    // Email MFA setup button
    document.getElementById('setup-email-mfa-btn').addEventListener('click', async function() {
        const button = this;
        setLoading(button, true);
        try {
            await setupEmailMFA();
        } catch (error) {
            console.error('Failed to setup email MFA:', error);
        } finally {
            setLoading(button, false);
        }
    });

    // Email MFA disable button
    document.getElementById('disable-email-mfa-btn').addEventListener('click', async function() {
        const button = this;
        setLoading(button, true);
        try {
            await disableEmailMFA();
        } catch (error) {
            console.error('Failed to disable email MFA:', error);
        } finally {
            setLoading(button, false);
        }
    });

    // Send email code button
    document.getElementById('send-email-code-btn').addEventListener('click', async function() {
        const email = document.getElementById('email-mfa-email').value;
        if (!email) {
            showMessage('email-mfa-message', 'Please enter an email address', 'error');
            return;
        }

        const button = this;
        setLoading(button, true);
        try {
            await sendEmailCode(email);
        } catch (error) {
            console.error('Failed to send email code:', error);
        } finally {
            setLoading(button, false);
        }
    });

    // Verify email code button
    document.getElementById('verify-email-btn').addEventListener('click', async function() {
        const code = document.getElementById('email-verify-code').value;
        if (!code || code.length !== 6) {
            showMessage('email-mfa-message', 'Please enter a valid 6-digit code', 'error');
            return;
        }

        const button = this;
        setLoading(button, true);
        try {
            await verifyEmailCode(code);
        } catch (error) {
            console.error('Failed to verify email code:', error);
        } finally {
            setLoading(button, false);
        }
    });

    // Verify backup code button
    document.getElementById('verify-backup-btn').addEventListener('click', async function() {
        const code = document.getElementById('backup-code').value;
        if (!code || code.length !== 8) {
            showMessage('backup-message', 'Please enter a valid 8-digit backup code', 'error');
            return;
        }

        const button = this;
        setLoading(button, true);
        try {
            await verifyBackupCode(code);
        } catch (error) {
            console.error('Failed to verify backup code:', error);
        } finally {
            setLoading(button, false);
        }
    });

    // Store original button text for loading states
    document.querySelectorAll('button').forEach(button => {
        button.setAttribute('data-original-text', button.textContent);
    });
});

function onLoginSuccess() {
    // Hide auth section, show others
    hideSection('auth-section');
    showSection('mfa-status-section');
    showSection('totp-setup-section');
    showSection('totp-management-section');
    showSection('email-mfa-section');
    showSection('backup-codes-section');
    showSection('logout-section');
    
    // Get initial MFA status
    getMFAStatus();
} 