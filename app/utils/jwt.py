import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID
from fastapi import HTTPException, status
from app.core.config import settings


class JWTManager:
    """JWT token management utilities"""
    
    @staticmethod
    def create_access_token(
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a new access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a new refresh token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        # Add a unique identifier to make each refresh token unique
        import uuid
        to_encode.update({
            "exp": expire, 
            "type": "refresh",
            "jti": str(uuid.uuid4())  # JWT ID - unique identifier
        })
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")
        return encoded_jwt
    
    @staticmethod
    def create_mfa_session_token(user_id: UUID, email: str) -> str:
        """Create an MFA session token for 'Remember this device' functionality"""
        user_data = {
            "sub": str(user_id),
            "email": email,
            "mfa_verified": True
        }
        
        # MFA session token expires in MFA_SESSION_DAYS
        expire = datetime.utcnow() + timedelta(days=settings.MFA_SESSION_DAYS)
        user_data.update({"exp": expire, "type": "mfa_session"})
        
        encoded_jwt = jwt.encode(user_data, settings.JWT_SECRET_KEY, algorithm="HS256")
        return encoded_jwt
    
    @staticmethod
    def create_temp_token(user_id: UUID, email: str, mfa_type: str) -> str:
        """Create a temporary token for MFA verification (short-lived)"""
        user_data = {
            "sub": str(user_id),
            "email": email,
            "mfa_type": mfa_type,
            "mfa_pending": True
        }
        
        # Temporary token expires in 5 minutes
        expire = datetime.utcnow() + timedelta(minutes=5)
        user_data.update({"exp": expire, "type": "temp"})
        
        encoded_jwt = jwt.encode(user_data, settings.JWT_SECRET_KEY, algorithm="HS256")
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
            
            # Check token type
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.exceptions.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    @staticmethod
    def create_user_tokens(user_id: UUID, email: str) -> Dict[str, Any]:
        """Create both access and refresh tokens for a user"""
        user_data = {
            "sub": str(user_id),
            "email": email
        }
        
        access_token = JWTManager.create_access_token(user_data)
        refresh_token = JWTManager.create_refresh_token(user_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # seconds
        } 