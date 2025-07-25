from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime
import re


class UserCreate(BaseModel):
    """Schema for user registration"""
    full_name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    phone: str = Field(..., min_length=1, max_length=20, description="User's phone number")
    password: str = Field(..., min_length=8, max_length=128, description="User's password")
    user_type: str = Field(default="individual", pattern="^(individual|business)$", description="User type")
    language_preference: str = Field(default="hy", pattern="^(hy|en|ru)$", description="Language preference")
    currency_preference: str = Field(default="AMD", pattern="^(AMD|USD|EUR|RUB)$", description="Currency preference")
    profile_picture: Optional[str] = None
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength"""
        if not v or v.strip() == "":
            raise ValueError("Password cannot be empty")
        
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if len(v) > 128:
            raise ValueError("Password must be no more than 128 characters long")
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must contain at least one uppercase letter")
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', v):
            raise ValueError("Password must contain at least one lowercase letter")
        
        # Check for at least one digit
        if not re.search(r'\d', v):
            raise ValueError("Password must contain at least one digit")
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)")
        
        return v
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        """Validate full name"""
        if not v or v.strip() == "":
            raise ValueError("Full name cannot be empty")
        
        if len(v.strip()) < 2:
            raise ValueError("Full name must be at least 2 characters long")
        
        return v.strip()
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number"""
        if not v or v.strip() == "":
            raise ValueError("Phone number cannot be empty")
        
        # Basic phone validation - allows + and digits
        if not re.match(r'^\+?[\d\s\-\(\)]+$', v):
            raise ValueError("Phone number contains invalid characters")
        
        return v.strip()
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "John Doe",
                "email": "john@example.com",
                "phone": "+37412345678",
                "password": "SecurePass123!",
                "user_type": "individual",
                "language_preference": "hy",
                "currency_preference": "AMD"
            }
        }
    )


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=1, description="User's password")
    mfa_session_token: Optional[str] = None
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password is not empty"""
        if not v or v.strip() == "":
            raise ValueError("Password cannot be empty")
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john@example.com",
                "password": "SecurePass123!"
            }
        }
    )


class UserUpdate(BaseModel):
    """Schema for user profile updates"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    language_preference: Optional[str] = None
    currency_preference: Optional[str] = None
    profile_picture: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user response"""
    id: UUID
    full_name: str
    email: str
    phone: str
    user_type: str
    language_preference: str
    currency_preference: str
    profile_picture: Optional[str] = None
    registration_date: datetime
    last_login: Optional[datetime] = None
    profile_status: str
    email_verified: bool
    mfa_enabled: bool
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    mfa_session_token: Optional[str] = None
    user: Optional[dict] = None  # User data when authentication is successful


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str


class EmailVerificationRequest(BaseModel):
    """Schema for email verification request"""
    token: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "550e8400-e29b-41d4-a716-446655440000"
            }
        }
    )


class EmailVerificationResponse(BaseModel):
    """Schema for email verification response"""
    message: str
    verified: bool


class ResendVerificationRequest(BaseModel):
    """Schema for resend verification email request"""
    email: EmailStr
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john@example.com"
            }
        }
    )


class ResendVerificationResponse(BaseModel):
    """Schema for resend verification email response"""
    message: str
    sent: bool 

# Firebase Authentication Schemas
class FirebaseLoginRequest(BaseModel):
    id_token: str = Field(..., description="Firebase ID token from frontend")

class OAuthLoginResponse(BaseModel):
    requires_mfa: bool = Field(..., description="Whether MFA is required")
    mfa_type: Optional[str] = Field(None, description="Type of MFA required (totp, email)")
    temp_token: Optional[str] = Field(None, description="Temporary token for MFA verification")
    access_token: Optional[str] = Field(None, description="JWT access token")
    refresh_token: Optional[str] = Field(None, description="JWT refresh token")
    token_type: Optional[str] = Field(None, description="Token type (Bearer)")
    user: Optional[UserResponse] = Field(None, description="User information") 