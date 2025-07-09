from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class UserProfile(BaseModel):
    full_name: str
    email: str
    phone: str
    user_type: str
    language_preference: str = "hy"
    currency_preference: str = "AMD"
    profile_picture: Optional[str] = None


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    language_preference: Optional[str] = None
    currency_preference: Optional[str] = None
    profile_picture: Optional[str] = None


@router.get("/profile", response_model=UserProfile)
async def get_profile():
    """Get current user profile"""
    # TODO: Implement get user profile
    return {
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+37412345678",
        "user_type": "individual",
        "language_preference": "hy",
        "currency_preference": "AMD",
        "profile_picture": None
    }


@router.put("/profile", response_model=UserProfile)
async def update_profile(profile: UserProfileUpdate):
    """Update current user profile"""
    # TODO: Implement update user profile
    return {
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+37412345678",
        "user_type": "individual",
        "language_preference": "hy",
        "currency_preference": "AMD",
        "profile_picture": None
    }


@router.delete("/profile")
async def delete_profile():
    """Delete current user profile"""
    # TODO: Implement delete user profile
    return {"message": "User profile deleted successfully"}


@router.get("/sessions")
async def get_sessions():
    """Get user active sessions"""
    # TODO: Implement get user sessions
    return {
        "sessions": [
            {
                "id": "session_id_1",
                "device_info": {"browser": "Chrome", "os": "Windows"},
                "created_at": "2024-01-01T00:00:00Z",
                "last_used_at": "2024-01-01T12:00:00Z"
            }
        ]
    }


@router.delete("/sessions/{session_id}")
async def revoke_session(session_id: str):
    """Revoke a specific session"""
    # TODO: Implement revoke session
    return {"message": f"Session {session_id} revoked successfully"} 