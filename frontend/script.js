// Global variables
let currentUser = null;
let mfaSessionToken = null;

// API base URL
const API_BASE = 'http://localhost:8000/api/v1';

// Utility functions
function showMessage(elementId, message, type = 'info') {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
        element.className = `message ${type}`;
        element.style.display = 'block';
    }
}

function hideMessage(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = 'none';
    }
}

function setLoading(button, loading) {
    if (loading) {
        button.disabled = true;
        button.textContent = 'Loading...';
    } else {
        button.disabled = false;
        button.textContent = button.getAttribute('data-original-text') || 'Submit';
    }
}

function switchToLogin() {
    document.getElementById('login-section').style.display = 'block';
    document.getElementById('register-section').style.display = 'none';
    document.getElementById('mfa-section').style.display = 'none';
    document.getElementById('dashboard-section').style.display = 'none';
    document.getElementById('email-verification-section').style.display = 'none';
}

function switchToRegister() {
    document.getElementById('login-section').style.display = 'none';
    document.getElementById('register-section').style.display = 'block';
    document.getElementById('mfa-section').style.display = 'none';
    document.getElementById('dashboard-section').style.display = 'none';
    document.getElementById('email-verification-section').style.display = 'none';
}

function switchToMFA() {
    document.getElementById('login-section').style.display = 'none';
    document.getElementById('register-section').style.display = 'none';
    document.getElementById('mfa-section').style.display = 'block';
    document.getElementById('dashboard-section').style.display = 'none';
    document.getElementById('email-verification-section').style.display = 'none';
}

function switchToDashboard() {
    document.getElementById('login-section').style.display = 'none';
    document.getElementById('register-section').style.display = 'none';
    document.getElementById('mfa-section').style.display = 'none';
    document.getElementById('dashboard-section').style.display = 'block';
    document.getElementById('email-verification-section').style.display = 'none';
}

function switchToEmailVerification() {
    document.getElementById('login-section').style.display = 'none';
    document.getElementById('register-section').style.display = 'none';
    document.getElementById('mfa-section').style.display = 'none';
    document.getElementById('dashboard-section').style.display = 'none';
    document.getElementById('email-verification-section').style.display = 'block';
}

// API functions
async function register(userData) {
    const response = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Registration failed');
    }

    return await response.json();
}

async function login(email, password) {
    const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
    }

    return await response.json();
}

async function verifyMFA(tempToken, code, rememberDevice = false) {
    const response = await fetch(`${API_BASE}/auth/mfa/verify`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            temp_token: tempToken,
            code: code,
            remember_device: rememberDevice
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'MFA verification failed');
    }

    return await response.json();
}

async function verifyEmail(token) {
    const response = await fetch(`${API_BASE}/auth/verify-email`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token: token })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Email verification failed');
    }

    return await response.json();
}

async function resendVerificationEmail(email) {
    const response = await fetch(`${API_BASE}/auth/resend-verification`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: email })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to resend verification email');
    }

    return await response.json();
}

async function getMFAStatus() {
    const response = await fetch(`${API_BASE}/mfa/status`, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    });

    if (!response.ok) {
        throw new Error('Failed to get MFA status');
    }

    return await response.json();
}

async function setupTOTP() {
    const response = await fetch(`${API_BASE}/mfa/setup`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ method: 'totp' })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to setup TOTP');
    }

    return await response.json();
}

async function verifyTOTPSetup(code) {
    const response = await fetch(`${API_BASE}/mfa/verify-totp`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code: code })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'TOTP verification failed');
    }

    return await response.json();
}

async function disableTOTP() {
    const response = await fetch(`${API_BASE}/mfa/disable`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ method: 'totp' })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to disable TOTP');
    }

    return await response.json();
}

// Form validation
function validateRegistrationForm(data) {
    const errors = [];
    
    if (!data.full_name || data.full_name.trim().length < 2) {
        errors.push('Full name must be at least 2 characters long');
    }
    
    if (!data.email || !data.email.includes('@')) {
        errors.push('Please enter a valid email address');
    }
    
    if (!data.phone || data.phone.trim().length < 10) {
        errors.push('Please enter a valid phone number');
    }
    
    if (!data.password || data.password.length < 8) {
        errors.push('Password must be at least 8 characters long');
    }
    
    if (data.user_type && !['individual', 'business'].includes(data.user_type)) {
        errors.push('User type must be either individual or business');
    }
    
    return errors;
}

function validateLoginForm(data) {
    const errors = [];
    
    if (!data.email || !data.email.includes('@')) {
        errors.push('Please enter a valid email address');
    }
    
    if (!data.password || data.password.length < 1) {
        errors.push('Password is required');
    }
    
    return errors;
}

// Event handlers
function onLoginSuccess() {
    // Store tokens
    if (currentUser.access_token) {
        localStorage.setItem('access_token', currentUser.access_token);
    }
    if (currentUser.refresh_token) {
        localStorage.setItem('refresh_token', currentUser.refresh_token);
    }
    if (currentUser.mfa_session_token) {
        mfaSessionToken = currentUser.mfa_session_token;
        localStorage.setItem('mfa_session_token', currentUser.mfa_session_token);
    }
    
    // Switch to dashboard
    switchToDashboard();
    updateDashboard();
}

function updateDashboard() {
    // Update user info
    const userInfo = document.getElementById('user-info');
    if (userInfo && currentUser) {
        userInfo.innerHTML = `
            <h3>Welcome, ${currentUser.full_name || 'User'}!</h3>
            <p>Email: ${currentUser.email}</p>
            <p>Status: ${currentUser.profile_status}</p>
            <p>Email Verified: ${currentUser.email_verified ? 'Yes' : 'No'}</p>
        `;
    }
}

function logout() {
    // Clear tokens
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('mfa_session_token');
    
    // Clear user data
    currentUser = null;
    mfaSessionToken = null;
    
    // Switch to login
    switchToLogin();
    
    // Clear forms
    document.getElementById('login-form').reset();
    document.getElementById('register-form').reset();
}

// Check for email verification token in URL
function checkForVerificationToken() {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (token) {
        // Show email verification section
        switchToEmailVerification();
        
        // Auto-verify the email
        verifyEmailFromURL(token);
    }
}

async function verifyEmailFromURL(token) {
    try {
        const result = await verifyEmail(token);
        showMessage('email-verification-message', result.message, 'success');
        
        // Clear the token from URL
        window.history.replaceState({}, document.title, window.location.pathname);
        
        // Show login button
        document.getElementById('email-verification-login-btn').style.display = 'inline-block';
        
    } catch (error) {
        showMessage('email-verification-message', `Verification failed: ${error.message}`, 'error');
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Check for verification token in URL
    checkForVerificationToken();
    
    // Navigation buttons
    document.getElementById('show-login').addEventListener('click', switchToLogin);
    document.getElementById('show-register').addEventListener('click', switchToRegister);
    document.getElementById('logout-btn').addEventListener('click', logout);
    document.getElementById('email-verification-login-btn').addEventListener('click', switchToLogin);
    
    // Register form
    document.getElementById('register-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = {
            full_name: document.getElementById('register-full-name').value,
            email: document.getElementById('register-email').value,
            phone: document.getElementById('register-phone').value,
            password: document.getElementById('register-password').value,
            user_type: document.getElementById('register-user-type').value
        };
        
        const submitButton = this.querySelector('button[type="submit"]');
        submitButton.setAttribute('data-original-text', submitButton.textContent);
        
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
            const result = await register(formData);
            showMessage('register-message', result.message || 'Registration successful! Please check your email to verify your account before logging in.', 'success');
            
            // Clear form and switch to login
            this.reset();
            setTimeout(() => {
                switchToLogin();
            }, 3000);
            
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
                // Store temp token for MFA verification
                currentUser = { temp_token: response.temp_token, mfa_type: response.mfa_type };
                switchToMFA();
                showMessage('mfa-message', `Please enter your ${response.mfa_type.toUpperCase()} code.`, 'info');
            } else {
                // Normal login success
                currentUser = response;
                onLoginSuccess();
            }
        } catch (error) {
            showMessage('login-message', `Login failed: ${error.message}`, 'error');
        } finally {
            setLoading(submitButton, false);
        }
    });

    // MFA verification form
    document.getElementById('mfa-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const code = document.getElementById('mfa-code').value;
        const rememberDevice = document.getElementById('remember-device').checked;
        const submitButton = this.querySelector('button[type="submit"]');
        
        setLoading(submitButton, true);
        hideMessage('mfa-message');
        
        try {
            const result = await verifyMFA(currentUser.temp_token, code, rememberDevice);
            currentUser = result;
            onLoginSuccess();
        } catch (error) {
            showMessage('mfa-message', `MFA verification failed: ${error.message}`, 'error');
        } finally {
            setLoading(submitButton, false);
        }
    });

    // MFA setup form
    document.getElementById('mfa-setup-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const submitButton = this.querySelector('button[type="submit"]');
        setLoading(submitButton, true);
        hideMessage('mfa-setup-message');
        
        try {
            const result = await setupTOTP();
            
            // Show QR code and secret
            document.getElementById('qr-code').src = result.qr_code_url;
            document.getElementById('totp-secret').textContent = result.secret;
            document.getElementById('backup-codes').textContent = result.backup_codes.join(', ');
            
            // Show verification step
            document.getElementById('mfa-setup-step1').style.display = 'none';
            document.getElementById('mfa-setup-step2').style.display = 'block';
            
        } catch (error) {
            showMessage('mfa-setup-message', `TOTP setup failed: ${error.message}`, 'error');
        } finally {
            setLoading(submitButton, false);
        }
    });

    // TOTP verification form
    document.getElementById('totp-verify-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const code = document.getElementById('totp-verify-code').value;
        const submitButton = this.querySelector('button[type="submit"]');
        
        setLoading(submitButton, true);
        hideMessage('totp-verify-message');
        
        try {
            await verifyTOTPSetup(code);
            showMessage('totp-verify-message', 'TOTP enabled successfully!', 'success');
            
            // Update MFA status
            updateMFAStatus();
            
        } catch (error) {
            showMessage('totp-verify-message', `TOTP verification failed: ${error.message}`, 'error');
        } finally {
            setLoading(submitButton, false);
        }
    });

    // Resend verification email form
    document.getElementById('resend-verification-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('resend-email').value;
        const submitButton = this.querySelector('button[type="submit"]');
        
        setLoading(submitButton, true);
        hideMessage('resend-verification-message');
        
        try {
            const result = await resendVerificationEmail(email);
            showMessage('resend-verification-message', result.message, 'success');
        } catch (error) {
            showMessage('resend-verification-message', `Failed to resend verification email: ${error.message}`, 'error');
        } finally {
            setLoading(submitButton, false);
        }
    });

    // MFA status buttons
    document.getElementById('check-mfa-status').addEventListener('click', updateMFAStatus);
    document.getElementById('setup-totp-btn').addEventListener('click', () => {
        document.getElementById('mfa-setup-step1').style.display = 'block';
        document.getElementById('mfa-setup-step2').style.display = 'none';
        document.getElementById('mfa-setup-section').style.display = 'block';
    });
    document.getElementById('disable-totp-btn').addEventListener('click', async () => {
        try {
            await disableTOTP();
            showMessage('dashboard-message', 'TOTP disabled successfully!', 'success');
            updateMFAStatus();
        } catch (error) {
            showMessage('dashboard-message', `Failed to disable TOTP: ${error.message}`, 'error');
        }
    });
});

async function updateMFAStatus() {
    try {
        const status = await getMFAStatus();
        const statusElement = document.getElementById('mfa-status');
        
        if (statusElement) {
            statusElement.innerHTML = `
                <h4>MFA Status:</h4>
                <p>MFA Enabled: ${status.mfa_enabled ? 'Yes' : 'No'}</p>
                <p>TOTP Enabled: ${status.totp_enabled ? 'Yes' : 'No'}</p>
                <p>Email MFA Enabled: ${status.email_mfa_enabled ? 'Yes' : 'No'}</p>
            `;
        }
    } catch (error) {
        console.error('Failed to get MFA status:', error);
    }
} 