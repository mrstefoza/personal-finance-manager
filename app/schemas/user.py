from pydantic import BaseModel, EmailStr, field_validator
from pydantic import ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    """Base user schema with common fields"""
    full_name: str
    email: EmailStr
    phone: str
    user_type: str
    language_preference: str = "hy"
    currency_preference: str = "AMD"


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

    @field_validator('user_type')
    @classmethod
    def validate_user_type(cls, v):
        if v not in ['individual', 'business']:
            raise ValueError('User type must be either "individual" or "business"')
        return v


class UserUpdate(BaseModel):
    """Schema for user profile updates"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    language_preference: Optional[str] = None
    currency_preference: Optional[str] = None
    profile_picture: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user responses"""
    id: UUID
    profile_status: str
    email_verified: bool
    registration_date: datetime
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str
    mfa_session_token: Optional[str] = None


class TokenResponse(BaseModel):
    """Schema for authentication tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    mfa_session_token: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str


class UserProfile(BaseModel):
    """Schema for user profile"""
    id: UUID
    full_name: str
    email: str
    phone: str
    user_type: str
    language_preference: str
    currency_preference: str
    profile_picture: Optional[str] = None
    profile_status: str
    email_verified: bool
    registration_date: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True) 