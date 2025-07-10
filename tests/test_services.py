import pytest
import pytest_asyncio
from app.services.user_service import UserService
from app.services.mfa_service import MFAService
# from app.core.security import verify_password  # Remove this import

@pytest.mark.asyncio
async def test_create_user(user_service, test_user_data):
    """Test user creation"""
    user = await user_service.create_user(test_user_data)
    
    assert user.email == test_user_data["email"]
    assert user.full_name == test_user_data["full_name"]
    assert user.user_type == test_user_data["user_type"]
    assert hasattr(user, 'id')
    assert not hasattr(user, 'password')

@pytest.mark.asyncio
async def test_get_user_by_email(user_service, test_user_data, db_session):
    """Test getting user by email"""
    # Create user first
    user = await user_service.create_user(test_user_data)
    # Activate user
    user_dict = user.model_dump()
    await db_session.execute(
        "UPDATE users SET profile_status = 'active', email_verified = TRUE WHERE id = $1",
        user_dict["id"]
    )
    # Get user by email
    retrieved_user = await user_service.get_user_by_email(test_user_data["email"])
    assert retrieved_user["email"] == user.email
    assert retrieved_user["id"] == user.id

@pytest.mark.asyncio
async def test_get_user_by_email_not_found(user_service):
    """Test getting user by email when not found"""
    user = await user_service.get_user_by_email("nonexistent@example.com")
    assert user is None

@pytest.mark.asyncio
async def test_authenticate_user(user_service, test_user_data, db_session):
    """Test user authentication"""
    # Create user first
    user = await user_service.create_user(test_user_data)
    # Activate user
    user_dict = user.model_dump()
    await db_session.execute(
        "UPDATE users SET profile_status = 'active', email_verified = TRUE WHERE id = $1",
        user_dict["id"]
    )
    
    # Authenticate with correct password
    authenticated_user = await user_service.authenticate_user(
        test_user_data["email"], 
        test_user_data["password"]
    )
    
    assert authenticated_user["email"] == user.email
    assert authenticated_user["id"] == user.id

@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(user_service, test_user_data, db_session):
    """Test user authentication with wrong password"""
    # Create user first
    user = await user_service.create_user(test_user_data)
    # Activate user
    user_dict = user.model_dump()
    await db_session.execute(
        "UPDATE users SET profile_status = 'active', email_verified = TRUE WHERE id = $1",
        user_dict["id"]
    )
    
    # Try to authenticate with wrong password
    authenticated_user = await user_service.authenticate_user(
        test_user_data["email"], 
        "wrongpassword"
    )
    
    assert authenticated_user is None

@pytest.mark.asyncio
async def test_totp_setup(mfa_service, test_user, db_session):
    """Test TOTP setup"""
    await db_session.execute(
        "UPDATE users SET profile_status = 'active', email_verified = TRUE WHERE id = $1",
        test_user["id"]
    )
    response = await mfa_service.setup_totp(test_user["id"], test_user["email"])
    
    assert response.secret is not None
    assert response.qr_code_url is not None
    assert len(response.backup_codes) == 10
    assert all(len(code) == 8 for code in response.backup_codes)

@pytest.mark.asyncio
async def test_totp_verify_valid_code(mfa_service, test_user, db_session):
    """Test TOTP verification with valid code"""
    await db_session.execute(
        "UPDATE users SET profile_status = 'active', email_verified = TRUE WHERE id = $1",
        test_user["id"]
    )
    # Setup TOTP first
    setup_response = await mfa_service.setup_totp(test_user["id"], test_user["email"])
    
    # Generate a valid TOTP code using the actual secret from setup
    from app.utils.totp import TOTPManager
    totp_code = TOTPManager.get_current_code(setup_response.secret)
    
    # First enable TOTP by verifying the setup
    await mfa_service.verify_totp_setup(test_user["id"], totp_code)
    
    # Now verify the code for login
    result = await mfa_service.verify_totp(test_user["id"], totp_code)
    assert result is True

@pytest.mark.asyncio
async def test_totp_verify_invalid_code(mfa_service, test_user, db_session):
    """Test TOTP verification with invalid code"""
    await db_session.execute(
        "UPDATE users SET profile_status = 'active', email_verified = TRUE WHERE id = $1",
        test_user["id"]
    )
    # Setup TOTP first
    await mfa_service.setup_totp(test_user["id"], test_user["email"])
    
    # Try to verify with invalid code
    result = await mfa_service.verify_totp(test_user["id"], "123456")
    assert result is False

@pytest.mark.asyncio
async def test_totp_disable(mfa_service, test_user, db_session):
    """Test TOTP disable"""
    await db_session.execute(
        "UPDATE users SET profile_status = 'active', email_verified = TRUE WHERE id = $1",
        test_user["id"]
    )
    # Setup and enable TOTP first
    setup_response = await mfa_service.setup_totp(test_user["id"], test_user["email"])
    
    # Generate a valid TOTP code using the actual secret from setup
    from app.utils.totp import TOTPManager
    totp_code = TOTPManager.get_current_code(setup_response.secret)
    
    # First enable TOTP by verifying the setup
    await mfa_service.verify_totp_setup(test_user["id"], totp_code)
    
    # Now disable TOTP
    result = await mfa_service.disable_totp(test_user["id"], totp_code)
    assert result is True

@pytest.mark.asyncio
async def test_backup_codes_verify_valid_code(mfa_service, test_user_with_totp, db_session):
    """Test backup codes verification with valid code"""
    await db_session.execute(
        "UPDATE users SET profile_status = 'active', email_verified = TRUE WHERE id = $1",
        test_user_with_totp["id"]
    )
    # Get backup codes from the setup
    backup_codes = test_user_with_totp["backup_codes"]
    
    # Use a backup code
    result = await mfa_service.verify_backup_code(test_user_with_totp["id"], backup_codes[0])
    assert result is True

@pytest.mark.asyncio
async def test_backup_codes_verify_invalid_code(mfa_service, test_user_with_totp, db_session):
    """Test backup codes verification with invalid code"""
    await db_session.execute(
        "UPDATE users SET profile_status = 'active', email_verified = TRUE WHERE id = $1",
        test_user_with_totp["id"]
    )
    # Try to use invalid backup code
    result = await mfa_service.verify_backup_code(test_user_with_totp["id"], "invalid-code")
    assert result is False

@pytest.mark.asyncio
async def test_backup_codes_verify_used_code(mfa_service, test_user_with_totp, db_session):
    """Test backup codes verification with already used code"""
    await db_session.execute(
        "UPDATE users SET profile_status = 'active', email_verified = TRUE WHERE id = $1",
        test_user_with_totp["id"]
    )
    # Get backup codes from the setup
    backup_codes = test_user_with_totp["backup_codes"]
    
    # Use a backup code first time
    result = await mfa_service.verify_backup_code(test_user_with_totp["id"], backup_codes[0])
    assert result is True
    
    # Try to use the same code again
    result = await mfa_service.verify_backup_code(test_user_with_totp["id"], backup_codes[0])
    assert result is False

@pytest.mark.asyncio
async def test_email_mfa_setup(mfa_service, test_user, db_session):
    """Test email MFA setup"""
    await db_session.execute(
        "UPDATE users SET profile_status = 'active', email_verified = TRUE WHERE id = $1",
        test_user["id"]
    )
    result = await mfa_service.setup_email_mfa(test_user["id"])
    assert result is True

@pytest.mark.asyncio
async def test_email_mfa_verify(mfa_service, test_user, db_session):
    """Test email MFA verification"""
    await db_session.execute(
        "UPDATE users SET profile_status = 'active', email_verified = TRUE WHERE id = $1",
        test_user["id"]
    )
    # Setup email MFA first
    await mfa_service.setup_email_mfa(test_user["id"])
    
    # Send an email MFA code
    code = await mfa_service.send_email_mfa_code(test_user["id"], test_user["email"])
    
    # Verify with the sent code
    result = await mfa_service.verify_email_mfa(test_user["id"], code)
    assert result is True

@pytest.mark.asyncio
async def test_email_mfa_disable(mfa_service, test_user, db_session):
    """Test email MFA disable"""
    await db_session.execute(
        "UPDATE users SET profile_status = 'active', email_verified = TRUE WHERE id = $1",
        test_user["id"]
    )
    # Setup email MFA first
    await mfa_service.setup_email_mfa(test_user["id"])
    
    # Disable email MFA
    result = await mfa_service.disable_email_mfa(test_user["id"])
    assert result is True 