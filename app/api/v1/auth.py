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
from datetime import datetime

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user: UserCreate,
    db: Database = Depends(get_database)
):
    """Register a new user with email verification"""
    try:
        user_service = UserService(db)
        new_user = await user_service.create_user(user)
        
        # Return user data but inform about email verification requirement
        return {
            **new_user.dict(),
            "message": "Registration successful! Please check your email to verify your account before logging in."
        }
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
        user = await user_service.authenticate_user(user_credentials.email, user_credentials.password)
        print(f"DEBUG: After authenticate_user, user is None: {user is None}")
        if not user:
            print("DEBUG: Raising 401 for invalid credentials")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        print(f"DEBUG: About to update last login for user id: {user['id']}")
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
            status_code=status.HTTP_401_UNAUTHORIZED,
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
    refresh_request: RefreshTokenRequest,
    db: Database = Depends(get_database)
):
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token
        payload = JWTManager.verify_token(refresh_request.refresh_token, "refresh")
        user_id = UUID(payload.get("sub"))
        email = payload.get("email")
        
        # Check if refresh token exists in database
        query = """
        SELECT * FROM user_sessions 
        WHERE user_id = $1 AND refresh_token_hash = $2 AND is_active = TRUE AND expires_at > $3
        """
        
        # Hash the refresh token for comparison
        import hashlib
        token_hash = hashlib.sha256(refresh_request.refresh_token.encode()).hexdigest()
        
        session = await db.fetchrow(query, user_id, token_hash, datetime.utcnow())
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Generate new tokens
        tokens = JWTManager.create_user_tokens(user_id, email)
        
        return tokens
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/verify-email")
async def verify_email(
    token: str,
    db: Database = Depends(get_database)
):
    """Verify user email with token"""
    try:
        user_service = UserService(db)
        success = await user_service.verify_email(token)
        
        if success:
            return {
                "message": "Email verified successfully! You can now log in to your account.",
                "verified": True
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email verification failed"
            )
            
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


@router.post("/resend-verification")
async def resend_verification_email(
    email: str,
    db: Database = Depends(get_database)
):
    """Resend verification email"""
    try:
        user_service = UserService(db)
        success = await user_service.resend_verification_email(email)
        
        if success:
            return {
                "message": "Verification email sent successfully! Please check your inbox.",
                "sent": True
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to send verification email"
            )
            
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


# OAuth endpoints (existing code)
@router.get("/google/login")
async def google_login():
    """Initiate Google OAuth login"""
    oauth_service = OAuthService()
    auth_url = oauth_service.get_google_auth_url()
    return {"auth_url": auth_url}


@router.post("/google/callback", response_model=OAuthLoginResponse)
async def google_callback(
    callback_data: GoogleCallbackRequest,
    db: Database = Depends(get_database)
):
    """Handle Google OAuth callback"""
    try:
        oauth_service = OAuthService(db)
        result = await oauth_service.handle_google_callback(callback_data.code)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/logout")
async def logout(
    refresh_token: str,
    db: Database = Depends(get_database)
):
    """Logout user and revoke refresh token"""
    try:
        # Hash the refresh token
        import hashlib
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        
        # Mark session as inactive
        query = """
        UPDATE user_sessions 
        SET is_active = FALSE, updated_at = $1
        WHERE refresh_token_hash = $2
        """
        await db.execute(query, datetime.utcnow(), token_hash)
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 