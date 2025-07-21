import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_complete_auth_flow(client, db_session):
    """Test complete authentication flow: register -> login -> get profile"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    # Step 1: Register a new user
    user_data = {
        "email": f"integration_{unique_id}@example.com",
        "password": "Integrationpass123!",
        "full_name": "Integration Test",
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
    
    registered_user = response.json()
    assert registered_user["email"] == user_data["email"]
    
    # Step 2: Login with the registered user
    login_data = {
        "email": f"integration_{unique_id}@example.com",
        "password": "Integrationpass123!"
    }
    
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    
    login_response = response.json()
    assert "access_token" in login_response
    assert "refresh_token" in login_response
    
    # Step 3: Get user profile using the access token
    headers = {"Authorization": f"Bearer {login_response['access_token']}"}
    response = await client.get("/api/v1/users/profile", headers=headers)
    assert response.status_code == 200
    
    profile = response.json()
    assert profile["email"] == user_data["email"]
    assert profile["full_name"] == user_data["full_name"]

@pytest.mark.asyncio
async def test_complete_mfa_flow(client, db_session):
    """Test complete MFA flow: register -> login -> setup TOTP -> verify -> disable"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    # Step 1: Register and login
    user_data = {
        "email": f"mfa_{unique_id}@example.com",
        "password": "Mfapass123!",
        "full_name": "MFA Test",
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

    login_data = {
        "email": f"mfa_{unique_id}@example.com",
        "password": "Mfapass123!"
    }

    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200

    login_response = response.json()
    headers = {"Authorization": f"Bearer {login_response['access_token']}"}

    # Step 2: Check initial MFA status
    response = await client.get("/api/v1/mfa/status", headers=headers)
    assert response.status_code == 200

    status = response.json()
    assert status["totp_enabled"] is False
    assert status["email_mfa_enabled"] is False
    assert status["backup_codes_remaining"] == 0

    # Step 3: Setup TOTP
    response = await client.post("/api/v1/mfa/totp/setup", headers=headers)
    assert response.status_code == 200

    setup_data = response.json()
    assert "secret" in setup_data
    assert "qr_code_url" in setup_data
    assert "backup_codes" in setup_data

    # Step 4: Verify and enable TOTP
    from app.utils.totp import TOTPManager
    totp_code = TOTPManager.get_current_code(setup_data["secret"])
    
    verify_data = {"code": totp_code}
    response = await client.post("/api/v1/mfa/totp/verify", json=verify_data, headers=headers)
    assert response.status_code == 200

    # Step 5: Check MFA status after enabling
    response = await client.get("/api/v1/mfa/status", headers=headers)
    assert response.status_code == 200

    status = response.json()
    assert status["totp_enabled"] is True
    assert status["backup_codes_remaining"] == 10

    # Step 6: Disable TOTP
    disable_data = {"code": totp_code}
    response = await client.post("/api/v1/mfa/totp/disable", json=disable_data, headers=headers)
    assert response.status_code == 200

    # Step 7: Check MFA status after disabling
    response = await client.get("/api/v1/mfa/status", headers=headers)
    assert response.status_code == 200

    status = response.json()
    assert status["totp_enabled"] is False
    assert status["backup_codes_remaining"] == 0

@pytest.mark.asyncio
async def test_backup_codes_flow(client, db_session):
    """Test backup codes flow: setup TOTP -> use backup code -> verify remaining"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    # Step 1: Register, login, and setup TOTP
    user_data = {
        "email": f"backup_{unique_id}@example.com",
        "password": "Backuppass123!",
        "full_name": "Backup Test",
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

    login_data = {
        "email": f"backup_{unique_id}@example.com",
        "password": "Backuppass123!"
    }

    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200

    login_response = response.json()
    headers = {"Authorization": f"Bearer {login_response['access_token']}"}

    # Setup TOTP to get backup codes
    response = await client.post("/api/v1/mfa/totp/setup", headers=headers)
    assert response.status_code == 200

    setup_data = response.json()
    backup_codes = setup_data["backup_codes"]

    # Enable TOTP by verifying the setup code
    from app.utils.totp import TOTPManager
    totp_code = TOTPManager.get_current_code(setup_data["secret"])
    verify_data = {"code": totp_code}
    response = await client.post("/api/v1/mfa/totp/verify", json=verify_data, headers=headers)
    assert response.status_code == 200

    # Step 2: Use a backup code
    verify_data = {"code": backup_codes[0]}
    response = await client.post("/api/v1/mfa/backup/verify", json=verify_data, headers=headers)
    assert response.status_code == 200

    # Step 3: Check remaining backup codes
    response = await client.get("/api/v1/mfa/status", headers=headers)
    assert response.status_code == 200

    status = response.json()
    assert status["backup_codes_remaining"] == 9

    # Step 4: Try to use the same backup code again (should fail)
    response = await client.post("/api/v1/mfa/backup/verify", json=verify_data, headers=headers)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_mfa_login_flow(client, db_session):
    """Test MFA login flow: register -> setup TOTP -> login with MFA"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    # Step 1: Register and setup TOTP
    user_data = {
        "email": f"mfa_login_{unique_id}@example.com",
        "password": "Mfaloginpass123!",
        "full_name": "MFALogin Test",
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

    login_data = {
        "email": f"mfa_login_{unique_id}@example.com",
        "password": "Mfaloginpass123!"
    }

    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200

    login_response = response.json()
    headers = {"Authorization": f"Bearer {login_response['access_token']}"}

    # Setup TOTP
    response = await client.post("/api/v1/mfa/totp/setup", headers=headers)
    assert response.status_code == 200

    setup_data = response.json()

    # Enable TOTP
    from app.utils.totp import TOTPManager
    totp_code = TOTPManager.get_current_code(setup_data["secret"])
    verify_data = {"code": totp_code}
    response = await client.post("/api/v1/mfa/totp/verify", json=verify_data, headers=headers)
    assert response.status_code == 200
    
    # Step 2: Login again (should require MFA)
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    login_response = response.json()
    assert "temp_token" in login_response
    assert "requires_mfa" in login_response
    assert login_response["requires_mfa"] is True

    # Step 3: Verify MFA to get full access
    # Use the correct endpoint and request body for TOTP verification during login
    mfa_verify_data = {"temp_token": login_response["temp_token"], "code": TOTPManager.get_current_code(setup_data["secret"]), "mfa_type": "totp"}
    response = await client.post("/api/v1/auth/mfa/verify", json=mfa_verify_data)
    assert response.status_code == 200
    mfa_response = response.json()
    assert "access_token" in mfa_response
    assert "refresh_token" in mfa_response

    # Step 4: Use the full access token
    full_headers = {"Authorization": f"Bearer {mfa_response['access_token']}"}
    response = await client.get("/api/v1/users/profile", headers=full_headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_error_handling(client):
    """Test error handling for various scenarios"""
    # Test 404 for non-existent endpoint
    response = await client.get("/api/v1/nonexistent")
    assert response.status_code == 404
    
    # Test 422 for invalid JSON
    response = await client.post("/api/v1/auth/register", data="invalid json")
    assert response.status_code == 422
    
    # Test 401 for protected endpoint without auth
    response = await client.get("/api/v1/users/profile")
    assert response.status_code == 401
    
    # Test 401 for invalid token
    headers = {"Authorization": "Bearer invalid_token"}
    response = await client.get("/api/v1/users/profile", headers=headers)
    assert response.status_code == 401 