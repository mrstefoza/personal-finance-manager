import httpx
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.database import Database
from app.services.user_service import UserService
from app.utils.jwt import JWTManager
from app.services.mfa_service import MFAService
from app.schemas.user import UserCreate
import uuid
from datetime import datetime


class OAuthService:
    """Service for OAuth operations"""
    
    def __init__(self, db: Database):
        self.db = db
        self.user_service = UserService(db)
        self.mfa_service = MFAService(db)
    
    def get_google_auth_url(self, redirect_uri: str) -> str:
        """Generate Google OAuth authorization URL"""
        base_url = "https://accounts.google.com/oauth/authorize"
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "email profile",
            "access_type": "offline",
            "prompt": "consent"
        }
        
        # Build query string
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"
    
    async def exchange_code_for_tokens(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for access tokens"""
        token_url = "https://oauth2.googleapis.com/token"
        
        data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            response.raise_for_status()
            return response.json()
    
    async def get_google_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Google"""
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(userinfo_url, headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def find_or_create_user(self, google_user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Find existing user or create new one from Google OAuth data"""
        google_id = google_user_info["id"]
        email = google_user_info["email"]
        
        # First, try to find user by Google ID
        user = await self.get_user_by_google_id(google_id)
        if user:
            return user
        
        # Then, try to find user by email
        user = await self.user_service.get_user_by_email(email)
        if user:
            # Link Google account to existing email account
            await self.link_google_account(user["id"], google_id)
            # Fetch and return the updated user
            user = await self.user_service.get_user_by_email(email)
            return user
        
        # Create new user from Google data
        return await self.create_user_from_google(google_user_info)
    
    async def get_user_by_google_id(self, google_id: str) -> Optional[Dict[str, Any]]:
        """Get user by Google ID"""
        query = """
        SELECT * FROM users 
        WHERE google_id = $1 AND deleted_at IS NULL
        """
        result = await self.db.fetchrow(query, google_id)
        return dict(result) if result else None
    
    async def link_google_account(self, user_id: uuid.UUID, google_id: str) -> None:
        """Link Google account to existing user"""
        query = """
        UPDATE users 
        SET google_id = $1, oauth_provider = 'both', updated_at = $2
        WHERE id = $3
        """
        await self.db.execute(query, google_id, datetime.utcnow(), user_id)
    
    async def create_user_from_google(self, google_user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user from Google OAuth data"""
        user_id = uuid.uuid4()
        google_id = google_user_info["id"]
        email = google_user_info["email"]
        full_name = google_user_info.get("name", "Unknown")
        picture = google_user_info.get("picture")
        
        # Create user with Google data
        query = """
        INSERT INTO users (
            id, full_name, email, phone, user_type, language_preference, 
            currency_preference, profile_picture, google_id, oauth_provider,
            profile_status, email_verified, registration_date
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
        RETURNING *
        """
        
        result = await self.db.fetchrow(
            query,
            user_id,
            full_name,
            email,
            "+0000000000",  # Default phone for OAuth users
            "individual",   # Default user type
            "en",          # Default language
            "USD",         # Default currency
            picture,
            google_id,
            "google",
            "active",      # OAuth users are automatically verified
            True,          # Email is verified by Google
            datetime.utcnow()
        )
        
        return dict(result)
    
    async def handle_oauth_login(self, google_user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Handle OAuth login and return appropriate response"""
        user = await self.find_or_create_user(google_user_info)
        
        # Update last login
        await self.user_service.update_last_login(user["id"])
        
        # Check MFA status
        mfa_status = await self.mfa_service.get_mfa_status(user["id"])
        
        if mfa_status["mfa_required"]:
            # User has MFA enabled, return temporary token
            mfa_type = "totp" if mfa_status["totp_enabled"] else "email"
            temp_token = JWTManager.create_temp_token(user["id"], user["email"], mfa_type)
            
            return {
                "requires_mfa": True,
                "mfa_type": mfa_type,
                "temp_token": temp_token,
                "user": user
            }
        else:
            # No MFA required, return full tokens
            tokens = JWTManager.create_user_tokens(user["id"], user["email"])
            
            return {
                "requires_mfa": False,
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "token_type": tokens["token_type"],
                "user": user
            } 