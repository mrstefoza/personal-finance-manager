from fastapi import APIRouter, HTTPException, status, Depends
from app.core.database import Database
from app.services.user_service import UserService
from app.services.mfa_service import MFAService
from app.services.oauth_service import OAuthService
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, RefreshTokenRequest
from app.schemas.mfa import LoginResponse, MFALoginVerifyRequest
from app.schemas.oauth import GoogleAuthRequest, GoogleAuthResponse, GoogleCallbackRequest, OAuthLoginResponse
from app.api.deps import get_database, get_current_user
from app.utils.jwt import JWTManager
from uuid import UUID

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user: UserCreate,
    db: Database = Depends(get_database)
):
    """Register a new user"""
    try:
        user_service = UserService(db)
        new_user = await user_service.create_user(user)
        return new_user
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


@router.post("/login", response_model=LoginResponse)
async def login(
    user_credentials: UserLogin,
    db: Database = Depends(get_database)
):
    """Login user and return tokens or MFA requirement"""
    try:
        user_service = UserService(db)
        mfa_service = MFAService(db)
        
        # Authenticate user
        user = await user_service.authenticate_user(
            user_credentials.email, 
            user_credentials.password
        )
        
        if not user:
            # Increment failed attempts for the user
            user_by_email = await user_service.get_user_by_email(user_credentials.email)
            if user_by_email:
                await user_service.increment_failed_login_attempts(user_by_email["id"])
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Update last login
        await user_service.update_last_login(user["id"])
        
        # Check if user provided an MFA session token
        if user_credentials.mfa_session_token:
            try:
                # Verify MFA session token
                mfa_payload = JWTManager.verify_token(user_credentials.mfa_session_token, "mfa_session")
                mfa_user_id = mfa_payload.get("sub")
                
                # Check if token belongs to this user
                if mfa_user_id == str(user["id"]):
                    # Valid MFA session token, skip MFA and return full tokens
                    tokens = JWTManager.create_user_tokens(user["id"], user["email"])
                    
                    return LoginResponse(
                        requires_mfa=False,
                        access_token=tokens["access_token"],
                        refresh_token=tokens["refresh_token"],
                        token_type=tokens["token_type"]
                    )
            except HTTPException:
                # Invalid MFA session token, continue with normal MFA flow
                pass
        
        # Check MFA status
        mfa_status = await mfa_service.get_mfa_status(user["id"])
        
        if mfa_status["mfa_required"]:
            # User has MFA enabled, return temporary token
            mfa_type = "totp" if mfa_status["totp_enabled"] else "email"
            temp_token = JWTManager.create_temp_token(user["id"], user["email"], mfa_type)
            
            return LoginResponse(
                requires_mfa=True,
                mfa_type=mfa_type,
                temp_token=temp_token
            )
        else:
            # No MFA required, return full tokens
            tokens = JWTManager.create_user_tokens(user["id"], user["email"])
            
            return LoginResponse(
                requires_mfa=False,
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                token_type=tokens["token_type"]
            )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/mfa/verify", response_model=TokenResponse)
async def verify_mfa_login(
    mfa_request: MFALoginVerifyRequest,
    db: Database = Depends(get_database)
):
    """Verify MFA code during login and return full tokens"""
    try:
        print(f"DEBUG: Starting MFA verification for temp_token: {mfa_request.temp_token[:20]}...")
        
        # Verify temporary token
        payload = JWTManager.verify_token(mfa_request.temp_token, "temp")
        print(f"DEBUG: Token payload: {payload}")
        
        user_id = UUID(payload.get("sub"))
        email = payload.get("email")
        mfa_type = payload.get("mfa_type")
        
        print(f"DEBUG: Extracted user_id: {user_id}, email: {email}, mfa_type: {mfa_type}")
        
        if not user_id or not email or not mfa_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid temporary token"
            )
        
        # Verify user still exists and is active
        user_service = UserService(db)
        user = await user_service.get_user_by_id(user_id)
        
        print(f"DEBUG: User lookup result: {user is not None}")
        if user:
            print(f"DEBUG: User profile_status: {user.get('profile_status')}")
            print(f"DEBUG: User totp_enabled: {user.get('totp_enabled')}")
            print(f"DEBUG: User has totp_secret_encrypted: {user.get('totp_secret_encrypted') is not None}")
        
        if not user or user["profile_status"] != "active":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Verify MFA code
        mfa_service = MFAService(db)
        mfa_verified = False
        
        print(f"DEBUG: About to verify MFA code for type: {mfa_type}")
        
        if mfa_type == "totp":
            mfa_verified = await mfa_service.verify_totp_login(user_id, mfa_request.code)
        elif mfa_type == "email":
            mfa_verified = await mfa_service.verify_email_mfa_code(user_id, mfa_request.code)
        
        print(f"DEBUG: MFA verification result: {mfa_verified}")
        
        if not mfa_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA code"
            )
        
        # Generate full tokens
        tokens = JWTManager.create_user_tokens(user_id, email)
        
        # If user wants to remember this device, also create an MFA session token
        if mfa_request.remember_device:
            mfa_session_token = JWTManager.create_mfa_session_token(user_id, email)
            tokens["mfa_session_token"] = mfa_session_token
        
        print(f"DEBUG: Generated tokens successfully")
        
        return tokens
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Exception in MFA verification: {str(e)}")
        print(f"DEBUG: Exception type: {type(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_request: RefreshTokenRequest,
    db: Database = Depends(get_database)
):
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token
        payload = JWTManager.verify_token(token_request.refresh_token, "refresh")
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Verify user still exists and is active
        user_service = UserService(db)
        user = await user_service.get_user_by_id(UUID(user_id))
        
        if not user or user["profile_status"] != "active":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Generate new tokens
        tokens = JWTManager.create_user_tokens(user["id"], user["email"])
        
        return tokens
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/logout")
async def logout(
    db: Database = Depends(get_database)
):
    """Logout user and revoke tokens"""
    # TODO: Implement logout logic (revoke refresh tokens)
    # For now, just return success - client should delete tokens
    return {"message": "User logged out successfully"}


@router.post("/verify-email")
async def verify_email(
    db: Database = Depends(get_database)
):
    """Verify user email"""
    # TODO: Implement email verification
    return {"message": "Email verification endpoint - to be implemented"}


@router.post("/forgot-password")
async def forgot_password(
    db: Database = Depends(get_database)
):
    """Request password reset"""
    # TODO: Implement password reset request
    return {"message": "Password reset request endpoint - to be implemented"}


@router.post("/reset-password")
async def reset_password(
    db: Database = Depends(get_database)
):
    """Reset password with token"""
    # TODO: Implement password reset
    return {"message": "Password reset endpoint - to be implemented"} 

# Google OAuth Endpoints

@router.post("/google/auth-url", response_model=GoogleAuthResponse)
async def get_google_auth_url(
    request: GoogleAuthRequest,
    db: Database = Depends(get_database)
):
    """Get Google OAuth authorization URL"""
    try:
        oauth_service = OAuthService(db)
        auth_url = oauth_service.get_google_auth_url(request.redirect_uri)
        
        return GoogleAuthResponse(auth_url=auth_url)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Google OAuth URL"
        )


@router.post("/google/callback", response_model=OAuthLoginResponse)
async def google_oauth_callback(
    request: GoogleCallbackRequest,
    db: Database = Depends(get_database)
):
    """Handle Google OAuth callback"""
    try:
        oauth_service = OAuthService(db)
        
        # Exchange code for tokens
        token_data = await oauth_service.exchange_code_for_tokens(
            request.code, 
            request.redirect_uri
        )
        
        # Get user info from Google
        google_user_info = await oauth_service.get_google_user_info(
            token_data["access_token"]
        )
        
        # Handle OAuth login (find/create user, check MFA, etc.)
        result = await oauth_service.handle_oauth_login(google_user_info)
        
        return OAuthLoginResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete Google OAuth login"
        )


@router.post("/google/link", response_model=dict)
async def link_google_account(
    request: GoogleCallbackRequest,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Link Google account to existing user"""
    try:
        oauth_service = OAuthService(db)
        
        # Exchange code for tokens
        token_data = await oauth_service.exchange_code_for_tokens(
            request.code, 
            request.redirect_uri
        )
        
        # Get user info from Google
        google_user_info = await oauth_service.get_google_user_info(
            token_data["access_token"]
        )
        
        # Link Google account to current user
        await oauth_service.link_google_account(
            current_user["id"], 
            google_user_info["id"]
        )
        
        return {"message": "Google account linked successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to link Google account"
        ) 