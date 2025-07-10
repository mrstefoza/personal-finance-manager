from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional
from app.core.database import Database
from app.services.user_service import UserService
from app.schemas.user import UserProfile, UserUpdate, UserProfile as UserProfileSchema
from app.api.deps import get_database, get_current_user

router = APIRouter()


@router.get("/profile", response_model=UserProfileSchema)
async def get_profile(
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Get current user profile"""
    return UserProfileSchema(**current_user)


@router.put("/profile", response_model=UserProfileSchema)
async def update_profile(
    profile: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Update current user profile"""
    try:
        user_service = UserService(db)
        updated_user = await user_service.update_user_profile(current_user["id"], profile)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserProfileSchema(**updated_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/profile")
async def delete_profile(
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Delete current user profile"""
    try:
        user_service = UserService(db)
        success = await user_service.delete_user(current_user["id"])
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {"message": "User profile deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/sessions")
async def get_sessions(
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Get user active sessions"""
    # TODO: Implement session management
    # For now, return a placeholder response
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
async def revoke_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Revoke a specific session"""
    # TODO: Implement session revocation
    return {"message": f"Session {session_id} revoked successfully"} 