import firebase_admin
from firebase_admin import auth, credentials
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.database import Database
from app.services.user_service import UserService
from app.utils.jwt import JWTManager
from app.services.mfa_service import MFAService
import uuid
from datetime import datetime


class FirebaseService:
    """Service for Firebase Authentication operations"""
    
    def __init__(self, db: Database):
        self.db = db
        self.user_service = UserService(db)
        self.mfa_service = MFAService(db)
        
        # Initialize Firebase Admin SDK if not already initialized
        if not firebase_admin._apps:
            try:
                # Try to load service account key from file
                cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH)
                firebase_admin.initialize_app(cred)
            except Exception as e:
                # If file not found, try to use environment variable
                try:
                    import json
                    service_account_info = json.loads(settings.FIREBASE_SERVICE_ACCOUNT_JSON)
                    cred = credentials.Certificate(service_account_info)
                    firebase_admin.initialize_app(cred)
                except Exception as e2:
                    raise Exception(f"Failed to initialize Firebase: {e2}")
    
    async def verify_firebase_token(self, id_token: str) -> Dict[str, Any]:
        """Verify Firebase ID token and return user info"""
        try:
            # Verify the Firebase ID token
            decoded_token = auth.verify_id_token(id_token)
            
            # Extract user information
            user_info = {
                "uid": decoded_token["uid"],
                "email": decoded_token.get("email"),
                "email_verified": decoded_token.get("email_verified", False),
                "name": decoded_token.get("name"),
                "picture": decoded_token.get("picture"),
                "provider": decoded_token.get("firebase", {}).get("sign_in_provider", "google")
            }
            
            return user_info
            
        except Exception as e:
            raise ValueError(f"Invalid Firebase token: {str(e)}")
    
    async def find_or_create_user(self, firebase_user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Find existing user or create new one from Firebase data"""
        firebase_uid = firebase_user_info["uid"]
        email = firebase_user_info["email"]
        
        # First, try to find user by Firebase UID
        user = await self.get_user_by_firebase_uid(firebase_uid)
        if user:
            return user
        
        # Then, try to find user by email
        user = await self.user_service.get_user_by_email(email)
        if user:
            # Link Firebase account to existing email account
            await self.link_firebase_account(user["id"], firebase_uid)
            # Fetch and return the updated user
            user = await self.user_service.get_user_by_email(email)
            return user
        
        # Create new user from Firebase data
        return await self.create_user_from_firebase(firebase_user_info)
    
    async def get_user_by_firebase_uid(self, firebase_uid: str) -> Optional[Dict[str, Any]]:
        """Get user by Firebase UID"""
        query = """
        SELECT * FROM users 
        WHERE firebase_uid = $1 AND deleted_at IS NULL
        """
        result = await self.db.fetchrow(query, firebase_uid)
        return dict(result) if result else None
    
    async def link_firebase_account(self, user_id: uuid.UUID, firebase_uid: str) -> None:
        """Link Firebase account to existing user"""
        query = """
        UPDATE users 
        SET firebase_uid = $1, oauth_provider = 'firebase', updated_at = $2
        WHERE id = $3
        """
        await self.db.execute(query, firebase_uid, datetime.utcnow(), user_id)
    
    async def create_user_from_firebase(self, firebase_user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user from Firebase data"""
        user_id = uuid.uuid4()
        firebase_uid = firebase_user_info["uid"]
        email = firebase_user_info["email"]
        full_name = firebase_user_info.get("name", "Unknown")
        picture = firebase_user_info.get("picture")
        
        # Create user with Firebase data
        query = """
        INSERT INTO users (
            id, full_name, email, phone, user_type, language_preference, 
            currency_preference, profile_picture, firebase_uid, oauth_provider,
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
            firebase_uid,
            "firebase",
            "active",      # OAuth users are automatically verified
            firebase_user_info.get("email_verified", True),  # Email is verified by Firebase
            datetime.utcnow()
        )
        
        return dict(result)
    
    async def handle_firebase_login(self, id_token: str) -> Dict[str, Any]:
        """Handle Firebase login and return appropriate response"""
        # Verify Firebase token
        firebase_user_info = await self.verify_firebase_token(id_token)
        
        # Find or create user
        user = await self.find_or_create_user(firebase_user_info)
        
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