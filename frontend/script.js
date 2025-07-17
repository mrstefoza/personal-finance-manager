// Global variables
let currentUser = null;
const API_BASE = '/api/v1';

// At the top, after defining currentUser and API_BASE
const savedUser = localStorage.getItem('currentUser');
if (savedUser) {
    currentUser = JSON.parse(savedUser);
}

// Navigation state management
const NAV_SECTIONS = {
    'login': 'login-section',
    'register': 'register-section',
    'dashboard': 'dashboard-section',
    'mfa-setup': 'mfa-setup-section',
    'totp-setup': 'totp-setup-section',
    'totp-management': 'totp-management-section',
    'email-mfa': 'email-mfa-section',
    'backup-codes': 'backup-codes-section',
    'mfa': 'mfa-section',
    'email-verification': 'email-verification-section',
    'resend-verification': 'resend-verification-section'
};

// Authentication check function
function isUserAuthenticated() {
    // Check if user has a valid access token (not just temp_token for MFA)
    return currentUser && currentUser.access_token && !currentUser.temp_token;
}

// Token validation function (only for critical operations)
async function validateToken() {
    if (!currentUser || !currentUser.access_token) {
        return false;
    }
    
    try {
        const response = await fetch(`${API_BASE}/auth/validate-token`, {
            headers: {
                'Authorization': `Bearer ${currentUser.access_token}`,
                'Content-Type': 'application/json',
            }
        });
        
        return response.ok;
    } catch (error) {
        console.error('Token validation failed:', error);
        return false;
    }
}

// Check authentication before protected operations (simplified)
async function checkAuthentication() {
    if (!isUserAuthenticated()) {
        return false;
    }
    
    return true;
}

// Navigation functions
function navigateTo(section, updateHistory = true) {
    // Check if user is authenticated for protected sections
    const protectedSections = ['dashboard', 'mfa-setup', 'totp-setup', 'totp-management', 'email-mfa', 'backup-codes'];
    
    // Allow access to MFA section if user has temp_token (MFA verification in progress)
    if (section === 'mfa' && currentUser && currentUser.temp_token) {
        // Allow access to MFA section during verification
    } else if (protectedSections.includes(section) && !isUserAuthenticated()) {
        console.log('Redirecting to login - user not authenticated');
        section = 'login';
    }
    
    // Hide all sections
    document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
    
    // Show target section
    const targetSection = document.getElementById(NAV_SECTIONS[section]);
    if (targetSection) {
        targetSection.style.display = 'block';
    }
    
    // Update navigation links
    updateNavigationLinks(section);
    
    // Update browser history
    if (updateHistory) {
        const url = new URL(window.location);
        url.searchParams.set('section', section);
        window.history.pushState({ section }, '', url);
    }
}

function updateNavigationLinks(activeSection) {
    const navLinks = document.getElementById('nav-links');
    navLinks.innerHTML = '';
    
    if (!isUserAuthenticated()) {
        // Not logged in - show only login/register
        addNavLink('login', 'Login', activeSection);
        addNavLink('register', 'Register', activeSection);
        
        // Hide user section
        document.getElementById('nav-user').style.display = 'none';
    } else {
        // Logged in - show full navigation
        addNavLink('dashboard', 'Dashboard', activeSection);
        addNavLink('mfa-setup', 'Setup MFA', activeSection);
        addNavLink('totp-management', 'TOTP Management', activeSection);
        addNavLink('email-mfa', 'Email MFA', activeSection);
        addNavLink('backup-codes', 'Backup Codes', activeSection);
        
        // Show user info in nav
        const navUser = document.getElementById('nav-user');
        const userName = document.getElementById('user-name');
        if (currentUser && currentUser.user) {
            userName.textContent = `${currentUser.user.full_name} (${currentUser.user.email})`;
            navUser.style.display = 'flex';
        }
    }
}

function addNavLink(section, text, activeSection) {
    const navLinks = document.getElementById('nav-links');
    const link = document.createElement('a');
    link.href = '#';
    link.className = `nav-link ${section === activeSection ? 'active' : ''}`;
    link.textContent = text;
    link.addEventListener('click', (e) => {
        e.preventDefault();
        navigateTo(section);
    });
    navLinks.appendChild(link);
}

// Handle browser back/forward buttons
window.addEventListener('popstate', function(event) {
    if (event.state && event.state.section) {
        navigateTo(event.state.section, false);
    } else {
        // Default to login if no section in history
        navigateTo('login', false);
    }
});

// Initialize navigation on page load
function initializeNavigation() {
    const urlParams = new URLSearchParams(window.location.search);
    let section = urlParams.get('section') || 'login';
    
    // Check if user is authenticated for protected sections
    const protectedSections = ['dashboard', 'mfa-setup', 'totp-setup', 'totp-management', 'email-mfa', 'backup-codes'];
    
    // Allow access to MFA section if user has temp_token (MFA verification in progress)
    if (section === 'mfa' && currentUser && currentUser.temp_token) {
        // Allow access to MFA section during verification
    } else if (protectedSections.includes(section) && !isUserAuthenticated()) {
        console.log('Redirecting to login - user not authenticated for protected section');
        section = 'login';
        // Update URL to reflect the redirect
        const url = new URL(window.location);
        url.searchParams.set('section', section);
        window.history.replaceState({ section }, '', url);
    }
    
    navigateTo(section, false);
}

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
    navigateTo('login');
}

function switchToRegister() {
    navigateTo('register');
}

function switchToMFA() {
    navigateTo('mfa');
}

function switchToDashboard() {
    navigateTo('dashboard');
    updateDashboard();
}

function switchToEmailVerification() {
    navigateTo('email-verification');
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
    // Get stored MFA session token if available
    const mfaSessionToken = localStorage.getItem('mfaSessionToken');
    
    const loginData = { email, password };
    if (mfaSessionToken) {
        loginData.mfa_session_token = mfaSessionToken;
    }
    
    const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(loginData)
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
    // Update navigation first to show authenticated sections
    updateNavigationLinks('dashboard');
    
    // Navigate to dashboard
    navigateTo('dashboard');
    updateDashboard();
    
    // Show nav user section
    const navUser = document.getElementById('nav-user');
    const userName = document.getElementById('user-name');
    if (currentUser && currentUser.user) {
        userName.textContent = `${currentUser.user.full_name} (${currentUser.user.email})`;
        navUser.style.display = 'flex';
    }
    // Save to localStorage
    localStorage.setItem('currentUser', JSON.stringify(currentUser));
}

function updateDashboard() {
    if (currentUser && currentUser.user) {
        const userInfo = document.getElementById('user-info');
        userInfo.innerHTML = `
            <h3>Welcome, ${currentUser.user.full_name}!</h3>
            <p><strong>Email:</strong> ${currentUser.user.email}</p>
            <p><strong>User Type:</strong> ${currentUser.user.user_type}</p>
            <p><strong>Profile Status:</strong> ${currentUser.user.profile_status}</p>
            
            <div class="mfa-status-section">
                <h4>MFA Status</h4>
                <div id="mfa-status-display">
                    <p>Loading MFA status...</p>
                </div>
            </div>
        `;
        
        // Load and display MFA status
        loadMFAStatus();
    }
}

async function loadMFAStatus() {
    try {
        const status = await getMFAStatus();
        const statusDisplay = document.getElementById('mfa-status-display');
        
        if (status) {
            statusDisplay.innerHTML = `
                <div class="status-item">
                    <span class="status-label">TOTP:</span>
                    <span class="status-value ${status.totp_enabled ? 'enabled' : 'disabled'}">
                        ${status.totp_enabled ? '✅ Enabled' : '❌ Disabled'}
                    </span>
                </div>
                <div class="status-item">
                    <span class="status-label">Email MFA:</span>
                    <span class="status-value ${status.email_mfa_enabled ? 'enabled' : 'disabled'}">
                        ${status.email_mfa_enabled ? '✅ Enabled' : '❌ Disabled'}
                    </span>
                </div>
                <div class="status-item">
                    <span class="status-label">MFA Required:</span>
                    <span class="status-value ${status.mfa_required ? 'enabled' : 'disabled'}">
                        ${status.mfa_required ? '✅ Yes' : '❌ No'}
                    </span>
                </div>
                ${status.totp_enabled ? `
                <div class="status-item">
                    <span class="status-label">Backup Codes:</span>
                    <span class="status-value">
                        ${status.backup_codes_remaining} remaining
                    </span>
                </div>
                ` : ''}
            `;
        } else {
            statusDisplay.innerHTML = '<p class="error">Failed to load MFA status</p>';
        }
    } catch (error) {
        console.error('Failed to load MFA status:', error);
        const statusDisplay = document.getElementById('mfa-status-display');
        statusDisplay.innerHTML = '<p class="error">Failed to load MFA status</p>';
    }
}

function logout() {
    currentUser = null;
    localStorage.removeItem('currentUser');
    localStorage.removeItem('mfaSessionToken');
    
    // Also sign out from Firebase if user was signed in
    if (window.FirebaseAuth) {
        window.FirebaseAuth.signOut().catch(console.error);
    }
    
    // Hide nav user section
    document.getElementById('nav-user').style.display = 'none';
    
    // Navigate to login and reset navigation
    navigateTo('login');
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
    // Initialize navigation
    initializeNavigation();

    // Check for verification token in URL
    checkForVerificationToken();
    
    // Navigation buttons
    document.getElementById('show-login').addEventListener('click', switchToLogin);
    document.getElementById('show-register').addEventListener('click', switchToRegister);
    document.getElementById('logout-btn').addEventListener('click', logout);
    document.getElementById('nav-logout-btn').addEventListener('click', logout);
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
                currentUser = { temp_token: response.temp_token, mfa_type: response.mfa_type, user: response.user };
                switchToMFA();
                
                // Show appropriate message based on MFA type
                if (response.mfa_type === 'email') {
                    showMessage('mfa-message', `Please enter your EMAIL code. Check the browser console for the code (development mode).`, 'info');
                    console.log('Email MFA code should have been auto-sent. Check the backend console for the code.');
                } else if (response.mfa_type === 'totp') {
                    showMessage('mfa-message', `Please enter your TOTP code from your authenticator app. You can also use a backup code instead.`, 'info');
                } else {
                    showMessage('mfa-message', `Please enter your ${response.mfa_type.toUpperCase()} code.`, 'info');
                }
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
                currentUser = { temp_token: response.temp_token, mfa_type: response.mfa_type, user: response.user };
                switchToMFA();
                
                // Show appropriate message based on MFA type
                if (response.mfa_type === 'email') {
                    showMessage('mfa-message', `Please enter your EMAIL code. Check the browser console for the code (development mode).`, 'info');
                    console.log('Email MFA code should have been auto-sent. Check the backend console for the code.');
                } else if (response.mfa_type === 'totp') {
                    showMessage('mfa-message', `Please enter your TOTP code from your authenticator app. You can also use a backup code instead.`, 'info');
                } else {
                    showMessage('mfa-message', `Please enter your ${response.mfa_type.toUpperCase()} code.`, 'info');
                }
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
            
            // Store MFA session token if remember_device was checked
            if (rememberDevice && result.mfa_session_token) {
                localStorage.setItem('mfaSessionToken', result.mfa_session_token);
            }
            
            onLoginSuccess();
        } catch (error) {
            showMessage('mfa-message', `MFA verification failed: ${error.message}`, 'error');
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
            loadMFAStatus();
            
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
        navigateTo('mfa-setup');
    });

    document.getElementById('show-totp-management').addEventListener('click', function() {
        navigateTo('totp-management');
    });

    document.getElementById('show-email-mfa').addEventListener('click', function() {
        navigateTo('email-mfa');
    });

    document.getElementById('show-backup-codes').addEventListener('click', function() {
        navigateTo('backup-codes');
    });

    // TOTP setup button (main MFA setup section)
    document.getElementById('setup-totp-btn-main').addEventListener('click', async function() {
        try {
            setLoading(this, true);
            hideMessage('mfa-setup-message');
            
            const result = await setupTOTP();
            console.log('TOTP setup result:', result);
            
            // Show QR code and secret
            const qrCodeElement = document.getElementById('qr-code');
            console.log('QR code element:', qrCodeElement);
            console.log('QR code URL:', result.qr_code_url);
            
            qrCodeElement.src = result.qr_code_url;
            document.getElementById('totp-secret').textContent = result.secret;
            document.getElementById('backup-codes').textContent = result.backup_codes.join(', ');
            
            // Show verification step
            const step1 = document.getElementById('totp-setup-step1');
            const step2 = document.getElementById('totp-setup-step2');
            console.log('Step 1 element:', step1);
            console.log('Step 2 element:', step2);
            
            step1.style.display = 'none';
            step2.style.display = 'block';
            
            console.log('Step 1 display after hide:', step1.style.display);
            console.log('Step 2 display after show:', step2.style.display);
            
            // Check if image is visible
            setTimeout(() => {
                const rect = qrCodeElement.getBoundingClientRect();
                console.log('QR code element bounds:', rect);
                console.log('QR code element visible:', rect.width > 0 && rect.height > 0);
                console.log('QR code element computed style:', window.getComputedStyle(qrCodeElement));
            }, 100);
            
        } catch (error) {
            showMessage('mfa-setup-message', `TOTP setup failed: ${error.message}`, 'error');
        } finally {
            setLoading(this, false);
        }
    });

    // TOTP setup button (generate QR code)
    document.getElementById('setup-totp-btn-generate').addEventListener('click', async function() {
        try {
            setLoading(this, true);
            hideMessage('totp-verify-message');
            
            const result = await setupTOTP();
            console.log('TOTP setup result (generate):', result);
            
            // Show QR code and secret
            const qrCodeElement = document.getElementById('qr-code');
            console.log('QR code element (generate):', qrCodeElement);
            console.log('QR code URL (generate):', result.qr_code_url);
            
            qrCodeElement.src = result.qr_code_url;
            document.getElementById('totp-secret').textContent = result.secret;
            document.getElementById('backup-codes').textContent = result.backup_codes.join(', ');
            
            // Show verification step
            document.getElementById('totp-setup-step1').style.display = 'none';
            document.getElementById('totp-setup-step2').style.display = 'block';
            
        } catch (error) {
            showMessage('totp-verify-message', `TOTP setup failed: ${error.message}`, 'error');
        } finally {
            setLoading(this, false);
        }
    });

    // TOTP setup button (management section)
    document.getElementById('setup-totp-btn-manage').addEventListener('click', async function() {
        try {
            setLoading(this, true);
            hideMessage('totp-management-message');
            
            const result = await setupTOTP();
            console.log('TOTP setup result (manage):', result);
            
            // Show QR code and secret
            const qrCodeElement = document.getElementById('qr-code');
            console.log('QR code element (manage):', qrCodeElement);
            console.log('QR code URL (manage):', result.qr_code_url);
            
            qrCodeElement.src = result.qr_code_url;
            document.getElementById('totp-secret').textContent = result.secret;
            document.getElementById('backup-codes').textContent = result.backup_codes.join(', ');
            
            // Show verification step
            const step1 = document.getElementById('totp-setup-step1');
            const step2 = document.getElementById('totp-setup-step2');
            console.log('Step 1 element (manage):', step1);
            console.log('Step 2 element (manage):', step2);
            
            step1.style.display = 'none';
            step2.style.display = 'block';
            
            console.log('Step 1 display after hide (manage):', step1.style.display);
            console.log('Step 2 display after show (manage):', step2.style.display);
            
            // Navigate to TOTP setup section to show the QR code
            console.log('Navigating to TOTP setup section...');
            navigateTo('totp-setup');
            
            // Check if the section is visible
            setTimeout(() => {
                const totpSetupSection = document.getElementById('totp-setup-section');
                console.log('TOTP setup section element:', totpSetupSection);
                console.log('TOTP setup section display:', totpSetupSection.style.display);
                console.log('TOTP setup section visible:', totpSetupSection.offsetParent !== null);
            }, 100);
            
        } catch (error) {
            showMessage('totp-management-message', `TOTP setup failed: ${error.message}`, 'error');
        } finally {
            setLoading(this, false);
        }
    });

    // Email MFA setup button (main MFA setup section)
    document.getElementById('setup-email-mfa-btn-main').addEventListener('click', async function() {
        try {
            setLoading(this, true);
            hideMessage('mfa-setup-message');
            
            // Enable email MFA
            const response = await fetch(`${API_BASE}/mfa/email/setup`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${currentUser.access_token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            });

            if (!response.ok) {
                const error = await response.json();
                console.log('Email MFA setup error:', error);
                
                // Handle specific error cases
                if (response.status === 400) {
                    if (error.detail && error.detail.includes('already enabled')) {
                        // Treat "already enabled" as success since the goal is achieved
                        showMessage('mfa-setup-message', 'Email MFA is already enabled for your account. ✅', 'success');
                        // Update MFA status to reflect current state
                        loadMFAStatus();
                    } else if (error.detail && error.detail.includes('email')) {
                        showMessage('mfa-setup-message', 'Please ensure your email address is verified before enabling email MFA.', 'error');
                    } else {
                        showMessage('mfa-setup-message', `Email MFA setup failed: ${error.detail || 'Invalid request'}. Please try again.`, 'error');
                    }
                } else {
                    throw new Error(error.detail || 'Email MFA setup failed');
                }
                return;
            }

            showMessage('mfa-setup-message', 'Email MFA enabled successfully!', 'success');
            
            // Update MFA status
            loadMFAStatus();
            
        } catch (error) {
            console.error('Email MFA setup error:', error);
            showMessage('mfa-setup-message', `Email MFA setup failed: ${error.message}`, 'error');
        } finally {
            setLoading(this, false);
        }
    });

    // Email MFA setup button (enable)
    document.getElementById('setup-email-mfa-btn-enable').addEventListener('click', async function() {
        try {
            setLoading(this, true);
            hideMessage('email-mfa-message');
            
            // Enable email MFA
            const response = await fetch(`${API_BASE}/mfa/email/setup`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${currentUser.access_token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            });

            if (!response.ok) {
                const error = await response.json();
                console.log('Email MFA setup error (enable):', error);
                
                // Handle specific error cases
                if (response.status === 400) {
                    if (error.detail && error.detail.includes('already enabled')) {
                        // Treat "already enabled" as success since the goal is achieved
                        showMessage('email-mfa-message', 'Email MFA is already enabled for your account. ✅', 'success');
                        // Update MFA status to reflect current state
                        loadMFAStatus();
                    } else if (error.detail && error.detail.includes('email')) {
                        showMessage('email-mfa-message', 'Please ensure your email address is verified before enabling email MFA.', 'error');
                    } else {
                        showMessage('email-mfa-message', `Email MFA setup failed: ${error.detail || 'Invalid request'}. Please try again.`, 'error');
                    }
                } else {
                    throw new Error(error.detail || 'Email MFA setup failed');
                }
                return;
            }

            showMessage('email-mfa-message', 'Email MFA enabled successfully!', 'success');
            
            // Update MFA status
            loadMFAStatus();
            
        } catch (error) {
            console.error('Email MFA setup error (enable):', error);
            showMessage('email-mfa-message', `Email MFA setup failed: ${error.message}`, 'error');
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
                
                // Update MFA status
                loadMFAStatus();
                
            } catch (error) {
                showMessage('totp-management-message', `Failed to disable TOTP: ${error.message}`, 'error');
            } finally {
                setLoading(this, false);
            }
        }
    });

    // Send email MFA code button
    document.getElementById('send-email-code-btn').addEventListener('click', async function() {
        try {
            setLoading(this, true);
            hideMessage('email-mfa-message');
            
            const email = document.getElementById('email-mfa-email').value;
            if (!email) {
                showMessage('email-mfa-message', 'Please enter an email address for MFA codes.', 'error');
                return;
            }
            
            // Send email MFA code
            const response = await fetch(`${API_BASE}/mfa/email/send-code`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${currentUser.access_token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email: email })
            });

            if (!response.ok) {
                const error = await response.json();
                console.log('Send email MFA code error:', error);
                throw new Error(error.detail || 'Failed to send email MFA code');
            }

            showMessage('email-mfa-message', 'Email MFA code sent successfully! Check your email.', 'success');
            
        } catch (error) {
            console.error('Send email MFA code error:', error);
            showMessage('email-mfa-message', `Failed to send email MFA code: ${error.message}`, 'error');
        } finally {
            setLoading(this, false);
        }
    });

    // Verify email MFA code button
    document.getElementById('verify-email-btn').addEventListener('click', async function() {
        try {
            setLoading(this, true);
            hideMessage('email-mfa-message');
            
            const code = document.getElementById('email-verify-code').value;
            if (!code) {
                showMessage('email-mfa-message', 'Please enter the 6-digit code from your email.', 'error');
                return;
            }
            
            // Verify email MFA code
            const response = await fetch(`${API_BASE}/mfa/email/verify`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${currentUser.access_token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ code: code })
            });

            if (!response.ok) {
                const error = await response.json();
                console.log('Verify email MFA code error:', error);
                throw new Error(error.detail || 'Failed to verify email MFA code');
            }

            showMessage('email-mfa-message', 'Email MFA code verified successfully!', 'success');
            
            // Update MFA status
            loadMFAStatus();
            
        } catch (error) {
            console.error('Verify email MFA code error:', error);
            showMessage('email-mfa-message', `Failed to verify email MFA code: ${error.message}`, 'error');
        } finally {
            setLoading(this, false);
        }
    });

    // Disable email MFA button
    document.getElementById('disable-email-mfa-btn').addEventListener('click', async function() {
        if (confirm('Are you sure you want to disable Email MFA? This will make your account less secure.')) {
            try {
                setLoading(this, true);
                hideMessage('email-mfa-message');
                
                // Disable email MFA
                const response = await fetch(`${API_BASE}/mfa/email/disable`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${currentUser.access_token}`,
                        'Content-Type': 'application/json',
                    }
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Failed to disable email MFA');
                }

                showMessage('email-mfa-message', 'Email MFA disabled successfully!', 'success');
                
                // Update MFA status
                loadMFAStatus();
                
            } catch (error) {
                showMessage('email-mfa-message', `Failed to disable email MFA: ${error.message}`, 'error');
            } finally {
                setLoading(this, false);
            }
        }
    });

    // Verify backup code button
    document.getElementById('verify-backup-btn').addEventListener('click', async function() {
        try {
            setLoading(this, true);
            hideMessage('backup-message');
            
            const code = document.getElementById('backup-code').value;
            if (!code) {
                showMessage('backup-message', 'Please enter a backup code.', 'error');
                return;
            }
            
            // Verify backup code
            const response = await fetch(`${API_BASE}/mfa/backup/verify`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${currentUser.access_token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ code: code })
            });

            if (!response.ok) {
                const error = await response.json();
                console.log('Backup code verification error:', error);
                throw new Error(error.detail || 'Failed to verify backup code');
            }

            showMessage('backup-message', 'Backup code verified successfully!', 'success');
            
            // Clear the input
            document.getElementById('backup-code').value = '';
            
            // Update MFA status to show remaining backup codes
            loadMFAStatus();
            
        } catch (error) {
            console.error('Backup code verification error:', error);
            showMessage('backup-message', `Failed to verify backup code: ${error.message}`, 'error');
        } finally {
            setLoading(this, false);
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