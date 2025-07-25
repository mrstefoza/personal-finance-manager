from fastapi import APIRouter, HTTPException, status, Depends
from app.core.database import Database
from app.services.user_service import UserService
from app.services.mfa_service import MFAService
from app.services.firebase_service import FirebaseService
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, RefreshTokenRequest, FirebaseLoginRequest, OAuthLoginResponse, ResendVerificationRequest, ResendVerificationResponse, EmailVerificationRequest, EmailVerificationResponse
from app.schemas.mfa import LoginResponse, MFALoginVerifyRequest
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
            **new_user.model_dump(),
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
                    
                    # Store refresh token in database
                    await user_service.store_refresh_token(user["id"], tokens["refresh_token"])
                    
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
            
            # If email MFA is required, automatically send the code
            if mfa_type == "email":
                try:
                    # Send email MFA code automatically
                    code = await mfa_service.send_email_mfa_code(user["id"], user["email"])
                    print(f"DEBUG: Auto-sent email MFA code: {code}")
                except Exception as e:
                    print(f"DEBUG: Failed to auto-send email MFA code: {str(e)}")
                    # Don't fail the login, just log the error
            
            return LoginResponse(
                requires_mfa=True,
                mfa_type=mfa_type,
                temp_token=temp_token,
                user={
                    "id": str(user["id"]),
                    "email": user["email"],
                    "full_name": user["full_name"],
                    "user_type": user["user_type"],
                    "profile_status": user["profile_status"]
                }
            )
        else:
            # No MFA required, return full tokens
            tokens = JWTManager.create_user_tokens(user["id"], user["email"])
            
            # Store refresh token in database
            await user_service.store_refresh_token(user["id"], tokens["refresh_token"])
            
            return LoginResponse(
                requires_mfa=False,
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                token_type=tokens["token_type"],
                user={
                    "id": str(user["id"]),
                    "email": user["email"],
                    "full_name": user["full_name"],
                    "user_type": user["user_type"],
                    "profile_status": user["profile_status"]
                }
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
            # First try TOTP verification
            mfa_verified = await mfa_service.verify_totp_login(user_id, mfa_request.code)
            
            # If TOTP fails, try backup code as fallback
            if not mfa_verified:
                print(f"DEBUG: TOTP verification failed, trying backup code")
                mfa_verified = await mfa_service.verify_backup_code(user_id, mfa_request.code)
                if mfa_verified:
                    print(f"DEBUG: Backup code verification successful")
                else:
                    print(f"DEBUG: Both TOTP and backup code verification failed")
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
        
        # Store refresh token in database
        await user_service.store_refresh_token(user_id, tokens["refresh_token"])
        
        # If user wants to remember this device, also create an MFA session token
        if mfa_request.remember_device:
            mfa_session_token = JWTManager.create_mfa_session_token(user_id, email)
            tokens["mfa_session_token"] = mfa_session_token
        
        print(f"DEBUG: Generated tokens successfully")
        
        # Add user data to response
        tokens["user"] = {
            "id": str(user["id"]),
            "email": user["email"],
            "full_name": user["full_name"],
            "user_type": user["user_type"],
            "profile_status": user["profile_status"]
        }
        
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
        
        # Store new refresh token in database
        user_service = UserService(db)
        await user_service.store_refresh_token(user_id, tokens["refresh_token"])
        
        # Invalidate the old refresh token
        await db.execute(
            "UPDATE user_sessions SET is_active = FALSE WHERE refresh_token_hash = $1",
            token_hash
        )
        
        return tokens
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/verify-email", response_model=EmailVerificationResponse)
async def verify_email(
    request: EmailVerificationRequest,
    db: Database = Depends(get_database)
):
    """Verify user email with token"""
    try:
        token = request.token
        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token is required"
            )
            
        user_service = UserService(db)
        success = await user_service.verify_email(token)
        
        if success:
            return EmailVerificationResponse(
                message="Email verified successfully! You can now log in to your account.",
                verified=True
            )
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


@router.post("/resend-verification", response_model=ResendVerificationResponse)
async def resend_verification_email(
    request: ResendVerificationRequest,
    db: Database = Depends(get_database)
):
    """Resend verification email"""
    try:
        user_service = UserService(db)
        success = await user_service.resend_verification_email(request.email)
        
        if success:
            return ResendVerificationResponse(
                message="Verification email sent successfully! Please check your inbox.",
                sent=True
            )
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


@router.post("/firebase/login", response_model=OAuthLoginResponse)
async def firebase_login(
    login_request: FirebaseLoginRequest,
    db: Database = Depends(get_database)
):
    """Handle Firebase authentication"""
    try:
        firebase_service = FirebaseService(db)
        result = await firebase_service.handle_firebase_login(login_request.id_token)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/logout")
async def logout(
    refresh_request: RefreshTokenRequest,
    db: Database = Depends(get_database)
):
    """Logout user and revoke refresh token"""
    try:
        # Hash the refresh token
        import hashlib
        token_hash = hashlib.sha256(refresh_request.refresh_token.encode()).hexdigest()
        
        # Mark session as inactive
        query = """
        UPDATE user_sessions 
        SET is_active = FALSE, last_used_at = $1
        WHERE refresh_token_hash = $2
        """
        await db.execute(query, datetime.utcnow(), token_hash)
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/validate-token")
async def validate_token(
    current_user: dict = Depends(get_current_user)
):
    """Validate current JWT token"""
    return {
        "valid": True,
        "user_id": str(current_user["id"]),
        "email": current_user["email"]
    } 