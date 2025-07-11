// Global variables
let currentUser = null;
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
        button.setAttribute('data-original-text', button.textContent);
        button.textContent = 'Loading...';
        button.disabled = true;
    } else {
        const originalText = button.getAttribute('data-original-text');
        if (originalText) {
            button.textContent = originalText;
        }
        button.disabled = false;
    }
}

// Navigation functions
function switchToLogin() {
    document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
    document.getElementById('login-section').style.display = 'block';
}

function switchToRegister() {
    document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
    document.getElementById('register-section').style.display = 'block';
}

function switchToMFA() {
    document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
    document.getElementById('mfa-section').style.display = 'block';
}

function switchToDashboard() {
    document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
    document.getElementById('dashboard-section').style.display = 'block';
    updateDashboard();
}

function switchToEmailVerification() {
    document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
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
            mfa_type: currentUser.mfa_type,
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
            'Authorization': `Bearer ${currentUser.access_token}`,
            'Content-Type': 'application/json',
        }
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get MFA status');
    }

    return await response.json();
}

async function setupTOTP() {
    const response = await fetch(`${API_BASE}/mfa/totp/setup`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${currentUser.access_token}`,
            'Content-Type': 'application/json',
        }
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'TOTP setup failed');
    }

    return await response.json();
}

async function verifyTOTPSetup(code) {
    const response = await fetch(`${API_BASE}/mfa/totp/verify`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${currentUser.access_token}`,
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
    const response = await fetch(`${API_BASE}/mfa/totp/disable`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${currentUser.access_token}`,
            'Content-Type': 'application/json',
        }
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to disable TOTP');
    }

    return await response.json();
}

// Firebase authentication functions
async function firebaseLogin(idToken) {
    const response = await fetch(`${API_BASE}/auth/firebase/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id_token: idToken })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Firebase login failed');
    }

    return await response.json();
}

// Form validation
function validateRegistrationForm(data) {
    const errors = [];
    
    if (!data.full_name || data.full_name.trim().length < 2) {
        errors.push('Full name must be at least 2 characters');
    }
    
    if (!data.email || !data.email.includes('@')) {
        errors.push('Valid email is required');
    }
    
    if (!data.phone || data.phone.length < 10) {
        errors.push('Valid phone number is required');
    }
    
    if (!data.password || data.password.length < 8) {
        errors.push('Password must be at least 8 characters');
    }
    
    if (!data.user_type) {
        errors.push('User type is required');
    }
    
    return errors;
}

function validateLoginForm(data) {
    const errors = [];
    
    if (!data.email || !data.email.includes('@')) {
        errors.push('Valid email is required');
    }
    
    if (!data.password || data.password.length < 1) {
        errors.push('Password is required');
    }
    
    return errors;
}

// Dashboard functions
function onLoginSuccess() {
    switchToDashboard();
    updateDashboard();
}

function updateDashboard() {
    if (currentUser && currentUser.user) {
        const userInfo = document.getElementById('user-info');
        userInfo.innerHTML = `
            <h3>Welcome, ${currentUser.user.full_name}!</h3>
            <p><strong>Email:</strong> ${currentUser.user.email}</p>
            <p><strong>User Type:</strong> ${currentUser.user.user_type}</p>
            <p><strong>Profile Status:</strong> ${currentUser.user.profile_status}</p>
        `;
    }
}

function logout() {
    currentUser = null;
    switchToLogin();
    // Also sign out from Firebase if user was signed in
    if (window.FirebaseAuth) {
        window.FirebaseAuth.signOut().catch(console.error);
    }
}

// URL token handling
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
    
    // Google login button
    document.getElementById('google-login-btn').addEventListener('click', async function() {
        try {
            setLoading(this, true);
            hideMessage('login-message');
            
            // Sign in with Google using Firebase
            const user = await window.FirebaseAuth.signInWithGoogle();
            
            // Get the ID token
            const idToken = await user.getIdToken();
            
            // Send token to our backend
            const response = await firebaseLogin(idToken);
            
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
            showMessage('login-message', `Google login failed: ${error.message}`, 'error');
        } finally {
            setLoading(this, false);
        }
    });
    
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

    // Dashboard navigation
    document.getElementById('show-mfa-setup').addEventListener('click', function() {
        document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
        document.getElementById('mfa-setup-section').style.display = 'block';
    });

    document.getElementById('show-totp-management').addEventListener('click', function() {
        document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
        document.getElementById('totp-management-section').style.display = 'block';
    });

    document.getElementById('show-email-mfa').addEventListener('click', function() {
        document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
        document.getElementById('email-mfa-section').style.display = 'block';
    });

    document.getElementById('show-backup-codes').addEventListener('click', function() {
        document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
        document.getElementById('backup-codes-section').style.display = 'block';
    });

    // TOTP setup button
    document.getElementById('setup-totp-btn').addEventListener('click', async function() {
        try {
            setLoading(this, true);
            hideMessage('mfa-setup-message');
            
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
            setLoading(this, false);
        }
    });

    // Disable TOTP button
    document.getElementById('disable-totp-btn').addEventListener('click', async function() {
        if (confirm('Are you sure you want to disable TOTP? This will make your account less secure.')) {
            try {
                setLoading(this, true);
                hideMessage('totp-management-message');
                
                await disableTOTP();
                showMessage('totp-management-message', 'TOTP disabled successfully!', 'success');
                
            } catch (error) {
                showMessage('totp-management-message', `Failed to disable TOTP: ${error.message}`, 'error');
            } finally {
                setLoading(this, false);
            }
        }
    });
});

async function updateMFAStatus() {
    try {
        const status = await getMFAStatus();
        // Update UI with MFA status if needed
        console.log('MFA Status:', status);
    } catch (error) {
        console.error('Failed to update MFA status:', error);
    }
} 