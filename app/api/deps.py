from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Header
from app.core.database import get_db, Database
from app.services.user_service import UserService
from app.utils.jwt import JWTManager
from uuid import UUID


async def get_database() -> Database:
    """Dependency to get database instance"""
    return await get_db()


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Database = Depends(get_database)
) -> dict:
    """Get current authenticated user from JWT token"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required"
        )
    
    try:
        # Extract token from "Bearer <token>"
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    # Verify token
    payload = JWTManager.verify_token(token, "access")
    user_id = payload.get("sub")
    email = payload.get("email")
    
    if not user_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get user from database
    user_service = UserService(db)
    user = await user_service.get_user_by_id(UUID(user_id))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Check if account is active
    if user["profile_status"] != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is not active"
        )
    
    return user


async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: Database = Depends(get_database)
) -> Optional[dict]:
    """Get current user if authenticated, otherwise return None"""
    if not authorization:
        return None
    
    try:
        return await get_current_user(authorization, db)
    except HTTPException:
        return None 