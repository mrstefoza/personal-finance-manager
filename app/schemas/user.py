from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for user registration"""
    full_name: str
    email: EmailStr
    phone: str
    password: str
    user_type: str = "individual"
    language_preference: str = "hy"
    currency_preference: str = "AMD"
    profile_picture: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "John Doe",
                "email": "john@example.com",
                "phone": "+37412345678",
                "password": "securepassword123",
                "user_type": "individual",
                "language_preference": "hy",
                "currency_preference": "AMD"
            }
        }
    )


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str
    mfa_session_token: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john@example.com",
                "password": "securepassword123"
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