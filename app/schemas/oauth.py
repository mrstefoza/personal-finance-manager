from pydantic import BaseModel, ConfigDict
from typing import Optional


class FirebaseLoginRequest(BaseModel):
    """Request for Firebase authentication"""
    id_token: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMzQ1Njc4OTAiLCJ0eXAiOiJKV1QifQ..."
            }
        }
    )


class OAuthLoginResponse(BaseModel):
    """Response for OAuth login"""
    requires_mfa: bool
    mfa_type: Optional[str] = None
    temp_token: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: Optional[str] = None
    user: Optional[dict] = None 