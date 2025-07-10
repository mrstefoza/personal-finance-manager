import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.main import app
from app.services.oauth_service import OAuthService
from app.core.database import Database
import uuid


@pytest_asyncio.fixture
async def oauth_service(db_session):
    return OAuthService(db_session)


@pytest.mark.asyncio
async def test_get_google_auth_url(oauth_service):
    """Test Google OAuth URL generation"""
    redirect_uri = "http://localhost:8000/callback"
    auth_url = oauth_service.get_google_auth_url(redirect_uri)
    
    assert "accounts.google.com/oauth/authorize" in auth_url
    assert "client_id=" in auth_url
    assert "redirect_uri=" in auth_url
    assert "response_type=code" in auth_url
    assert "scope=email profile" in auth_url


@pytest.mark.asyncio
async def test_oauth_endpoints(client):
    """Test OAuth API endpoints"""
    # Test auth URL endpoint
    response = await client.post("/api/v1/auth/google/auth-url", json={
        "redirect_uri": "http://localhost:8000/callback"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "auth_url" in data
    assert "accounts.google.com" in data["auth_url"]


@pytest.mark.asyncio
async def test_oauth_service_user_creation(oauth_service, db_session):
    """Test OAuth user creation and linking"""
    # Mock Google user info
    unique_email = f"test_oauth_creation_{uuid.uuid4()}@example.com"
    google_user_info = {
        "id": str(uuid.uuid4()),
        "email": unique_email,
        "name": "Test User",
        "picture": "https://example.com/picture.jpg"
    }
    
    # Test creating user from Google data
    user = await oauth_service.create_user_from_google(google_user_info)
    
    assert user["email"] == unique_email
    assert user["full_name"] == "Test User"
    assert user["google_id"] == google_user_info["id"]
    assert user["oauth_provider"] == "google"
    assert user["profile_status"] == "active"
    assert user["email_verified"] is True
    
    # Test finding user by Google ID
    found_user = await oauth_service.get_user_by_google_id(google_user_info["id"])
    assert found_user is not None
    assert found_user["id"] == user["id"]


@pytest.mark.asyncio
async def test_oauth_account_linking(oauth_service, db_session):
    """Test linking Google account to existing email account"""
    from app.services.user_service import UserService
    user_service = UserService(db_session)
    unique_email = f"existing_oauth_{uuid.uuid4()}@example.com"
    user_data = {
        "full_name": "Existing User",
        "email": unique_email,
        "password": "TestPass123",
        "phone": "+1234567890",
        "user_type": "individual"
    }
    existing_user = await user_service.create_user(user_data)
    # Mock Google user info with same email
    google_user_info = {
        "id": str(uuid.uuid4()),
        "email": unique_email,
        "name": "Google User",
        "picture": "https://example.com/picture.jpg"
    }
    # Test finding/linking user
    user = await oauth_service.find_or_create_user(google_user_info)
    assert user["id"] == existing_user.id
    assert user["google_id"] == google_user_info["id"]
    assert user["oauth_provider"] == "both" 