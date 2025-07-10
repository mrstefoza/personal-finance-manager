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
        "password": "Testpassword123",
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
        "password": "testpassword123",
        "full_name": "Test User",
        "phone": "+37412345678",
        "user_type": "individual",
        "language_preference": "en",
        "currency_preference": "USD"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_login_user(client):
    """Test user login"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    # First register a user
    user_data = {
        "email": f"test_{unique_id}@example.com",
        "password": "Testpassword123",
        "full_name": "Test User",
        "phone": "+37412345678",
        "user_type": "individual",
        "language_preference": "en",
        "currency_preference": "USD"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    
    # Login with the user
    login_data = {
        "email": f"test_{unique_id}@example.com",
        "password": "Testpassword123"
    }
    
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_user_invalid_credentials(client):
    """Test user login with invalid credentials"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    # First register a user
    user_data = {
        "email": f"test_{unique_id}@example.com",
        "password": "Testpassword123",
        "full_name": "Test User",
        "phone": "+37412345678",
        "user_type": "individual",
        "language_preference": "en",
        "currency_preference": "USD"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    
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