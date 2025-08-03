import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "app" in data
    assert "version" in data
    assert "environment" in data

@pytest.mark.asyncio
async def test_register_user(client):
    """Test user registration"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    user_data = {
        "email": f"test_{unique_id}@example.com",
        "password": "Testpassword123!",
        "full_name": "Test User",
        "phone": "+37412345678",
        "user_type": "individual",
        "language_preference": "en",
        "currency_preference": "USD"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert data["user_type"] == user_data["user_type"]
    assert "id" in data
    assert "password" not in data

@pytest.mark.asyncio
async def test_register_user_invalid_data(client):
    """Test user registration with invalid data"""
    # Test with invalid email
    user_data = {
        "email": "invalid-email",
        "password": "Testpassword123!",
        "full_name": "Test User",
        "phone": "+37412345678",
        "user_type": "individual",
        "language_preference": "en",
        "currency_preference": "USD"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_login_user(client, db_session):
    """Test user login"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    # First register a user
    user_data = {
        "email": f"test_{unique_id}@example.com",
        "password": "Testpassword123!",
        "full_name": "Test User",
        "phone": "+37412345678",
        "user_type": "individual",
        "language_preference": "en",
        "currency_preference": "USD"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    user_id = response.json()["id"]
    # Verify the user
    await db_session.execute(
        "UPDATE users SET profile_status = 'active', email_verified = TRUE WHERE id = $1",
        user_id
    )
    
    # Login with the user
    login_data = {
        "email": f"test_{unique_id}@example.com",
        "password": "Testpassword123!"
    }
    
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_user_invalid_credentials(client, db_session):
    """Test user login with invalid credentials"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    # First register a user
    user_data = {
        "email": f"test_{unique_id}@example.com",
        "password": "Testpassword123!",
        "full_name": "Test User",
        "phone": "+37412345678",
        "user_type": "individual",
        "language_preference": "en",
        "currency_preference": "USD"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    user_id = response.json()["id"]
    # Verify the user
    await db_session.execute(
        "UPDATE users SET profile_status = 'active', email_verified = TRUE WHERE id = $1",
        user_id
    )
    
    # Then try to login with wrong password
    login_data = {
        "email": f"test_{unique_id}@example.com",
        "password": "wrongpassword"
    }
    
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_current_user(client, auth_headers):
    """Test getting current user information"""
    response = await client.get("/api/v1/users/profile", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "id" in data
    assert "email" in data
    assert "full_name" in data
    assert "user_type" in data

@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client):
    """Test getting current user without authentication"""
    response = await client.get("/api/v1/users/profile")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_mfa_status(client, auth_headers):
    """Test MFA status endpoint"""
    response = await client.get("/api/v1/mfa/status", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "totp_enabled" in data
    assert "email_mfa_enabled" in data
    assert "backup_codes_remaining" in data

@pytest.mark.asyncio
async def test_mfa_status_unauthorized(client):
    """Test MFA status without authentication"""
    response = await client.get("/api/v1/mfa/status")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_totp_setup(client, auth_headers):
    """Test TOTP setup endpoint"""
    response = await client.post("/api/v1/mfa/totp/setup", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert "secret" in data
    assert "qr_code_url" in data
    assert "backup_codes" in data
    assert len(data["backup_codes"]) == 10

@pytest.mark.asyncio
async def test_totp_verify(client, auth_headers):
    """Test TOTP verification endpoint"""
    # First setup TOTP
    response = await client.post("/api/v1/mfa/totp/setup", headers=auth_headers)
    assert response.status_code == 200

    setup_data = response.json()
    secret = setup_data["secret"]

    # Generate a valid TOTP code
    from app.utils.totp import TOTPManager
    totp_code = TOTPManager.get_current_code(secret)

    # Verify the code
    verify_data = {"code": totp_code}
    response = await client.post("/api/v1/mfa/totp/verify", json=verify_data, headers=auth_headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_totp_verify_invalid_code(client, auth_headers):
    """Test TOTP verification with invalid code"""
    # First setup TOTP
    response = await client.post("/api/v1/mfa/totp/setup", headers=auth_headers)
    assert response.status_code == 200
    
    # Try to verify with invalid code
    verify_data = {"code": "123456"}
    response = await client.post("/api/v1/mfa/totp/verify", json=verify_data, headers=auth_headers)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_totp_disable(client, auth_headers):
    """Test TOTP disable endpoint"""
    # First setup and enable TOTP
    response = await client.post("/api/v1/mfa/totp/setup", headers=auth_headers)
    assert response.status_code == 200

    setup_data = response.json()
    secret = setup_data["secret"]

    # Generate a valid TOTP code and enable
    from app.utils.totp import TOTPManager
    totp_code = TOTPManager.get_current_code(secret)

    # First verify to enable TOTP
    verify_data = {"code": totp_code}
    response = await client.post("/api/v1/mfa/totp/verify", json=verify_data, headers=auth_headers)
    assert response.status_code == 200

    # Then disable TOTP
    disable_data = {"code": totp_code}
    response = await client.post("/api/v1/mfa/totp/disable", json=disable_data, headers=auth_headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_backup_codes_verify(client, auth_headers):
    """Test backup codes verification endpoint"""
    # First setup TOTP to get backup codes
    response = await client.post("/api/v1/mfa/totp/setup", headers=auth_headers)
    assert response.status_code == 200

    setup_data = response.json()
    backup_codes = setup_data["backup_codes"]

    # Use a backup code
    verify_data = {"code": backup_codes[0]}
    response = await client.post("/api/v1/mfa/backup/verify", json=verify_data, headers=auth_headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_backup_codes_verify_invalid_code(client, auth_headers):
    """Test backup codes verification with invalid code"""
    # Try to verify with invalid backup code
    verify_data = {"code": "invalid-code"}
    response = await client.post("/api/v1/mfa/backup/verify", json=verify_data, headers=auth_headers)
    assert response.status_code == 422  # Validation error for invalid format 

@pytest.mark.asyncio
async def test_send_email_mfa_code_when_not_enabled(client, auth_headers):
    """Test sending email MFA code when not enabled returns 400 error"""
    response = await client.post(
        "/api/v1/mfa/email/send-code",
        headers=auth_headers,
        json={"email": "test@example.com"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email MFA is not enabled" 

@pytest.mark.asyncio
async def test_update_profile(client, auth_headers):
    """Test updating user profile"""
    # Test data for profile update
    update_data = {
        "full_name": "Updated Name",
        "phone": "+37498765432",
        "language_preference": "en",
        "currency_preference": "USD"
    }
    
    response = await client.put("/api/v1/users/profile", json=update_data, headers=auth_headers)
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["full_name"] == update_data["full_name"]
    assert data["phone"] == update_data["phone"]
    assert data["language_preference"] == update_data["language_preference"]
    assert data["currency_preference"] == update_data["currency_preference"] 

@pytest.mark.asyncio
async def test_refresh_token(client, db_session):
    """Test refreshing access token"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    # Register a test user
    user_data = {
        "email": f"refresh_test_{unique_id}@example.com",
        "password": "Testpassword123!",
        "full_name": "Test User",
        "phone": "+37412345678",
        "user_type": "individual",
        "language_preference": "en",
        "currency_preference": "USD"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    user_id = response.json()["id"]
    
    # Verify the user
    await db_session.execute(
        "UPDATE users SET profile_status = 'active', email_verified = TRUE WHERE id = $1",
        user_id
    )
    
    # Login to get refresh token
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    login_response = await client.post("/api/v1/auth/login", json=login_data)
    assert login_response.status_code == 200
    
    login_response_data = login_response.json()
    assert "refresh_token" in login_response_data
    
    refresh_token = login_response_data["refresh_token"]
    
    # Now test the refresh endpoint
    refresh_data = {
        "refresh_token": refresh_token
    }
    
    refresh_response = await client.post("/api/v1/auth/refresh", json=refresh_data)
    print(f"Refresh response status: {refresh_response.status_code}")
    print(f"Refresh response body: {refresh_response.text}")
    
    assert refresh_response.status_code == 200
    
    refresh_response_data = refresh_response.json()
    assert "access_token" in refresh_response_data
    assert "refresh_token" in refresh_response_data
    assert "token_type" in refresh_response_data
    assert refresh_response_data["token_type"] == "bearer"
    
    # Cleanup
    await db_session.execute("DELETE FROM users WHERE id = $1", user_id) 

@pytest.mark.asyncio
async def test_refresh_token_complete_flow(client, db_session):
    """Test complete refresh token flow including using new tokens"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    # Register a test user
    user_data = {
        "email": f"refresh_flow_{unique_id}@example.com",
        "password": "Testpassword123!",
        "full_name": "Test User",
        "phone": "+37412345678",
        "user_type": "individual",
        "language_preference": "en",
        "currency_preference": "USD"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    user_id = response.json()["id"]
    
    # Verify the user
    await db_session.execute(
        "UPDATE users SET profile_status = 'active', email_verified = TRUE WHERE id = $1",
        user_id
    )
    
    # Login to get initial tokens
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    login_response = await client.post("/api/v1/auth/login", json=login_data)
    assert login_response.status_code == 200
    
    login_response_data = login_response.json()
    initial_access_token = login_response_data["access_token"]
    initial_refresh_token = login_response_data["refresh_token"]
    
    # Use initial access token to access protected endpoint
    initial_headers = {"Authorization": f"Bearer {initial_access_token}"}
    profile_response = await client.get("/api/v1/users/profile", headers=initial_headers)
    assert profile_response.status_code == 200
    
    # Now refresh the tokens
    refresh_data = {"refresh_token": initial_refresh_token}
    refresh_response = await client.post("/api/v1/auth/refresh", json=refresh_data)
    assert refresh_response.status_code == 200
    
    refresh_response_data = refresh_response.json()
    new_access_token = refresh_response_data["access_token"]
    new_refresh_token = refresh_response_data["refresh_token"]
    
    # Verify new tokens are different from initial tokens
    # Access tokens might be the same if they're still valid, but refresh tokens should be different
    assert new_refresh_token != initial_refresh_token
    
    # Use new access token to access protected endpoint
    new_headers = {"Authorization": f"Bearer {new_access_token}"}
    profile_response2 = await client.get("/api/v1/users/profile", headers=new_headers)
    assert profile_response2.status_code == 200
    
    # Verify old access token still works (until it expires)
    profile_response3 = await client.get("/api/v1/users/profile", headers=initial_headers)
    assert profile_response3.status_code == 200
    
    # Test that old refresh token is invalidated (should fail)
    old_refresh_data = {"refresh_token": initial_refresh_token}
    old_refresh_response = await client.post("/api/v1/auth/refresh", json=old_refresh_data)
    assert old_refresh_response.status_code == 401
    
    # Cleanup
    await db_session.execute("DELETE FROM users WHERE id = $1", user_id) 

@pytest.mark.asyncio
async def test_registration_password_validation(client, db_session):
    """Test that registration properly validates passwords"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    # Test 1: Empty password
    user_data_empty = {
        "email": f"test_empty_{unique_id}@example.com",
        "password": "",
        "full_name": "Test User",
        "phone": "+37412345678"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data_empty)
    assert response.status_code == 422  # Validation error
    
    # Test 2: Whitespace-only password
    user_data_whitespace = {
        "email": f"test_whitespace_{unique_id}@example.com",
        "password": "   ",
        "full_name": "Test User",
        "phone": "+37412345678"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data_whitespace)
    assert response.status_code == 422  # Validation error
    
    # Test 3: Too short password
    user_data_short = {
        "email": f"test_short_{unique_id}@example.com",
        "password": "Abc1!",
        "full_name": "Test User",
        "phone": "+37412345678"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data_short)
    assert response.status_code == 422  # Validation error
    
    # Test 4: Missing uppercase letter
    user_data_no_upper = {
        "email": f"test_noupper_{unique_id}@example.com",
        "password": "securepass123!",
        "full_name": "Test User",
        "phone": "+37412345678"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data_no_upper)
    assert response.status_code == 422  # Validation error
    
    # Test 5: Missing lowercase letter
    user_data_no_lower = {
        "email": f"test_nolower_{unique_id}@example.com",
        "password": "SECUREPASS123!",
        "full_name": "Test User",
        "phone": "+37412345678"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data_no_lower)
    assert response.status_code == 422  # Validation error
    
    # Test 6: Missing digit
    user_data_no_digit = {
        "email": f"test_nodigit_{unique_id}@example.com",
        "password": "SecurePass!",
        "full_name": "Test User",
        "phone": "+37412345678"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data_no_digit)
    assert response.status_code == 422  # Validation error
    
    # Test 7: Missing special character
    user_data_no_special = {
        "email": f"test_nospecial_{unique_id}@example.com",
        "password": "SecurePass123",
        "full_name": "Test User",
        "phone": "+37412345678"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data_no_special)
    assert response.status_code == 422  # Validation error
    
    # Test 8: Valid password (should succeed)
    user_data_valid = {
        "email": f"test_valid_{unique_id}@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User",
        "phone": "+37412345678"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data_valid)
    assert response.status_code == 201  # Success
    
    # Cleanup
    user_id = response.json()["id"]
    await db_session.execute("DELETE FROM users WHERE id = $1", user_id)


@pytest.mark.asyncio
async def test_login_password_validation(client, db_session):
    """Test that login properly validates passwords"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    # Create a test user first
    user_data = {
        "email": f"test_login_{unique_id}@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User",
        "phone": "+37412345678"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    user_id = response.json()["id"]
    
    # Verify the user
    await db_session.execute(
        "UPDATE users SET profile_status = 'active', email_verified = TRUE WHERE id = $1",
        user_id
    )
    
    # Test 1: Empty password
    login_data_empty = {
        "email": user_data["email"],
        "password": ""
    }
    
    response = await client.post("/api/v1/auth/login", json=login_data_empty)
    assert response.status_code == 422  # Validation error
    
    # Test 2: Whitespace-only password
    login_data_whitespace = {
        "email": user_data["email"],
        "password": "   "
    }
    
    response = await client.post("/api/v1/auth/login", json=login_data_whitespace)
    assert response.status_code == 422  # Validation error
    
    # Test 3: Valid password (should succeed)
    login_data_valid = {
        "email": user_data["email"],
        "password": "SecurePass123!"
    }
    
    response = await client.post("/api/v1/auth/login", json=login_data_valid)
    assert response.status_code == 200  # Success
    
    # Cleanup
    await db_session.execute("DELETE FROM users WHERE id = $1", user_id) 

@pytest.mark.asyncio
async def test_refresh_token_debug(client, db_session):
    """Debug test to check refresh token flow manually"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    # Register a test user
    user_data = {
        "email": f"debug_refresh_{unique_id}@example.com",
        "password": "Testpassword123!",
        "full_name": "Test User",
        "phone": "+37412345678",
        "user_type": "individual",
        "language_preference": "en",
        "currency_preference": "USD"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    user_id = response.json()["id"]
    
    # Verify the user
    await db_session.execute(
        "UPDATE users SET profile_status = 'active', email_verified = TRUE WHERE id = $1",
        user_id
    )
    
    # Login to get refresh token
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    login_response = await client.post("/api/v1/auth/login", json=login_data)
    assert login_response.status_code == 200
    
    login_response_data = login_response.json()
    print(f"Login response: {login_response_data}")
    
    refresh_token = login_response_data["refresh_token"]
    print(f"Refresh token: {refresh_token[:50]}...")
    
    # Check if refresh token is stored in database
    import hashlib
    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    
    session_query = """
    SELECT * FROM user_sessions 
    WHERE user_id = $1 AND refresh_token_hash = $2 AND is_active = TRUE
    """
    
    session = await db_session.fetchrow(session_query, user_id, token_hash)
    print(f"Session found in DB: {session is not None}")
    if session:
        print(f"Session data: {dict(session)}")
    
    # Now test the refresh endpoint
    refresh_data = {
        "refresh_token": refresh_token
    }
    
    refresh_response = await client.post("/api/v1/auth/refresh", json=refresh_data)
    print(f"Refresh response status: {refresh_response.status_code}")
    print(f"Refresh response body: {refresh_response.text}")
    
    assert refresh_response.status_code == 200
    
    # Cleanup
    await db_session.execute("DELETE FROM users WHERE id = $1", user_id) 