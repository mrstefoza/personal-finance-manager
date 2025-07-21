from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional
from app.core.database import Database
from app.services.user_service import UserService
from app.schemas.user import UserResponse, UserUpdate
from app.api.deps import get_database, get_current_user
from fastapi.security import HTTPBearer

router = APIRouter()
security = HTTPBearer()


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database),
    token: str = Depends(security)
):
    """Get current user profile"""
    return UserResponse(**current_user)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database),
    token: str = Depends(security)
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
        
        return UserResponse(**updated_user)
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
    db: Database = Depends(get_database),
    token: str = Depends(security)
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
        
        return {"message": "Profile deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 