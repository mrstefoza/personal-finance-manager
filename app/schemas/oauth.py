from pydantic import BaseModel, ConfigDict
from typing import Optional


class GoogleAuthRequest(BaseModel):
    """Request to initiate Google OAuth"""
    redirect_uri: str


class GoogleAuthResponse(BaseModel):
    """Response with Google OAuth URL"""
    auth_url: str


class GoogleCallbackRequest(BaseModel):
    """Request for Google OAuth callback"""
    code: str
    redirect_uri: str


class OAuthLoginResponse(BaseModel):
    """Response for OAuth login"""
    requires_mfa: bool
    mfa_type: Optional[str] = None
    temp_token: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: Optional[str] = None
    user: Optional[dict] = None


class LinkGoogleRequest(BaseModel):
    """Request to link Google account to existing user"""
    google_token: str
    redirect_uri: str 