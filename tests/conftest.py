import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient
from app.main import app
from app.core.database import Database, get_db
from app.services.user_service import UserService
from app.services.mfa_service import MFAService
from app.utils.jwt import JWTManager
import uuid

@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def test_db():
    """Create test database instance"""
    database = Database()
    await database.connect()
    yield database
    await database.disconnect()

@pytest_asyncio.fixture
async def db_session(test_db):
    """Create a fresh database session for each test."""
    # For raw SQL, we just return the database instance
    yield test_db

@pytest_asyncio.fixture
async def client(db_session):
    """Create a test client with database dependency overridden."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def user_service(db_session):
    """User service fixture"""
    return UserService(db_session)

@pytest_asyncio.fixture
async def mfa_service(db_session):
    """MFA service fixture"""
    return MFAService(db_session)

@pytest.fixture
def test_user_data():
    """Test user data fixture"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"test_{unique_id}@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User",
        "phone": "+37412345678",
        "user_type": "individual",
        "language_preference": "en",
        "currency_preference": "USD"
    }

@pytest_asyncio.fixture
async def test_user(db_session, user_service, test_user_data):
    """Create a test user and return user data"""
    # Create test user
    user = await user_service.create_user(test_user_data)
    
    # Convert UserResponse to dict for database operations
    user_dict = user.model_dump()
    
    # Activate the user (set profile_status to active and email_verified to true)
    await db_session.execute(
        "UPDATE users SET profile_status = 'active', email_verified = TRUE WHERE id = $1",
        user_dict["id"]
    )
    
    # Get the updated user
    updated_user = await user_service.get_user_by_id(user_dict["id"])
    
    yield updated_user
    
    # Cleanup - delete test user
    await db_session.execute("DELETE FROM users WHERE id = $1", user_dict["id"])

@pytest_asyncio.fixture
async def auth_headers(client, db_session):
    """Create authenticated headers for testing."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    # Register a test user
    user_data = {
        "email": f"auth_test_{unique_id}@example.com",
        "password": "Testpassword123",
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
    
    # Login to get token
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture
async def admin_headers(client, db_session):
    """Create admin authenticated headers for testing."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    # Register an admin user
    user_data = {
        "email": f"admin_test_{unique_id}@example.com",
        "password": "Adminpassword123",
        "full_name": "Admin User",
        "phone": "+37412345678",
        "user_type": "business",
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
    
    # Login to get token
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture
async def temp_token(test_user):
    """Generate temporary token for MFA verification"""
    return JWTManager.create_temp_token(test_user["id"], test_user["email"], "totp")

@pytest.fixture
def test_totp_secret():
    """Test TOTP secret for testing"""
    return "JBSWY3DPEHPK3PXP"  # Standard test secret

@pytest.fixture
def test_backup_codes():
    """Test backup codes"""
    return ["12345678", "87654321", "11111111", "22222222", "33333333"]

@pytest_asyncio.fixture
async def test_user_with_totp(db_session, test_user, mfa_service, test_totp_secret):
    """Create a test user with TOTP enabled"""
    # Setup TOTP for the user
    totp_response = await mfa_service.setup_totp(test_user["id"], test_user["email"])
    
    # Verify and enable TOTP (we'll use the test secret directly)
    encrypted_secret = mfa_service.totp_encryption.encrypt(test_totp_secret)
    encrypted_backup_codes = mfa_service.totp_encryption.encrypt_backup_codes(totp_response.backup_codes)
    
    await db_session.execute(
        """
        UPDATE users 
        SET totp_secret_encrypted = $1, totp_enabled = TRUE, backup_codes_encrypted = $2
        WHERE id = $3
        """,
        encrypted_secret, encrypted_backup_codes, test_user["id"]
    )
    
    # Return user with backup codes for testing
    user_with_totp = test_user.copy()
    user_with_totp["backup_codes"] = totp_response.backup_codes
    user_with_totp["totp_secret"] = test_totp_secret
    
    yield user_with_totp
    
    # Cleanup - disable TOTP
    await db_session.execute(
        "UPDATE users SET totp_secret_encrypted = NULL, totp_enabled = FALSE, backup_codes_encrypted = NULL WHERE id = $1",
        test_user["id"]
    ) 