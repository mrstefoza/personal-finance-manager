from fastapi import APIRouter, HTTPException, status, Depends, Request
from app.core.database import Database
from app.services.mfa_service import MFAService
from app.schemas.mfa import (
    TOTPSetupRequest, TOTPSetupResponse, TOTPVerifyRequest, TOTPDisableRequest,
    EmailMFASetupRequest, EmailMFASendCodeRequest, EmailMFAVerifyRequest,
    MFAResponse, MFAStatusResponse, BackupCodeVerifyRequest
)
from app.api.deps import get_database, get_current_user
from app.core.config import settings
from fastapi.security import HTTPBearer

router = APIRouter()
security = HTTPBearer()


@router.get("/status", response_model=MFAStatusResponse)
async def get_mfa_status(
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database),
    token: str = Depends(security)
):
    """Get MFA status for current user"""
    mfa_service = MFAService(db)
    status = await mfa_service.get_mfa_status(current_user["id"])
    return MFAStatusResponse(**status)


# TOTP MFA Endpoints

@router.post("/totp/setup", response_model=TOTPSetupResponse)
async def setup_totp(
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Setup TOTP MFA for current user"""
    try:
        mfa_service = MFAService(db)
        
        # Check if TOTP is already enabled
        status = await mfa_service.get_mfa_status(current_user["id"])
        if status["totp_enabled"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="TOTP is already enabled"
            )
        
        # Setup TOTP
        result = await mfa_service.setup_totp(current_user["id"], current_user["email"])
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to setup TOTP"
        )


@router.post("/totp/verify", response_model=MFAResponse)
async def verify_totp_setup(
    request: TOTPVerifyRequest,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Verify TOTP code during setup and enable TOTP"""
    try:
        mfa_service = MFAService(db)
        
        # Verify and enable TOTP
        success = await mfa_service.verify_totp_setup(current_user["id"], request.code)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid TOTP code"
            )
        
        # Log successful attempt
        await mfa_service.log_mfa_attempt(
            current_user["id"], "totp", True
        )
        
        return MFAResponse(
            message="TOTP enabled successfully",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify TOTP"
        )


@router.post("/totp/disable", response_model=MFAResponse)
async def disable_totp(
    request: TOTPDisableRequest,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Disable TOTP MFA for current user"""
    try:
        mfa_service = MFAService(db)
        
        # Verify code and disable TOTP
        success = await mfa_service.disable_totp(current_user["id"], request.code)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid TOTP code"
            )
        
        return MFAResponse(
            message="TOTP disabled successfully",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disable TOTP"
        )


@router.post("/totp/verify-login", response_model=MFAResponse)
async def verify_totp_login(
    request: TOTPVerifyRequest,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database),
    http_request: Request = None
):
    """Verify TOTP code during login"""
    try:
        mfa_service = MFAService(db)
        
        # Verify TOTP code
        success = await mfa_service.verify_totp_login(current_user["id"], request.code)
        
        if not success:
            # Log failed attempt
            await mfa_service.log_mfa_attempt(
                current_user["id"], "totp", False,
                ip_address=http_request.client.host if http_request else None,
                user_agent=http_request.headers.get("user-agent") if http_request else None
            )
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid TOTP code"
            )
        
        # Log successful attempt
        await mfa_service.log_mfa_attempt(
            current_user["id"], "totp", True,
            ip_address=http_request.client.host if http_request else None,
            user_agent=http_request.headers.get("user-agent") if http_request else None
        )
        
        return MFAResponse(
            message="TOTP verification successful",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify TOTP"
        )


# Email MFA Endpoints

@router.post("/email/setup", response_model=MFAResponse)
async def setup_email_mfa(
    request: EmailMFASetupRequest,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Setup email MFA for current user"""
    try:
        mfa_service = MFAService(db)
        
        # Check if email MFA is already enabled
        status = await mfa_service.get_mfa_status(current_user["id"])
        if status["email_mfa_enabled"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email MFA is already enabled"
            )
        
        # Enable email MFA
        await mfa_service.enable_email_mfa(current_user["id"])
        
        return MFAResponse(
            message="Email MFA enabled successfully",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to setup email MFA"
        )


@router.post("/email/send-code", response_model=MFAResponse)
async def send_email_mfa_code(
    request: EmailMFASendCodeRequest,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database),
    token: str = Depends(security)
):
    """Send email MFA code"""
    try:
        mfa_service = MFAService(db)
        
        # Check if email MFA is enabled
        mfa_status = await mfa_service.get_mfa_status(current_user["id"])
        if not mfa_status["email_mfa_enabled"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email MFA is not enabled"
            )
        
        # Send code
        code = await mfa_service.send_email_mfa_code(current_user["id"], request.email)
        
        # In development mode, return the code for testing
        # In production, this should be removed
        if settings.ENVIRONMENT == "development":
            return MFAResponse(
                message=f"Email MFA code sent: {code}",
                success=True
            )
        else:
            return MFAResponse(
                message="Email MFA code sent successfully",
                success=True
            )
        
    except HTTPException:
        raise
    except ValueError as e:
        # Handle ValueError from MFA service (e.g., "Email MFA is not enabled")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email MFA code"
        )


@router.post("/email/verify", response_model=MFAResponse)
async def verify_email_mfa(
    request: EmailMFAVerifyRequest,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database),
    http_request: Request = None
):
    """Verify email MFA code"""
    try:
        mfa_service = MFAService(db)
        
        # Verify email MFA code
        success = await mfa_service.verify_email_mfa_code(current_user["id"], request.code)
        
        if not success:
            # Log failed attempt
            await mfa_service.log_mfa_attempt(
                current_user["id"], "email", False,
                ip_address=http_request.client.host if http_request else None,
                user_agent=http_request.headers.get("user-agent") if http_request else None
            )
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired email MFA code"
            )
        
        # Log successful attempt
        await mfa_service.log_mfa_attempt(
            current_user["id"], "email", True,
            ip_address=http_request.client.host if http_request else None,
            user_agent=http_request.headers.get("user-agent") if http_request else None
        )
        
        return MFAResponse(
            message="Email MFA verification successful",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify email MFA"
        )


@router.post("/email/disable", response_model=MFAResponse)
async def disable_email_mfa(
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Disable email MFA for current user"""
    try:
        mfa_service = MFAService(db)
        
        # Disable email MFA
        await mfa_service.disable_email_mfa(current_user["id"])
        
        return MFAResponse(
            message="Email MFA disabled successfully",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disable email MFA"
        )


# Backup Codes Endpoints

@router.post("/backup/verify", response_model=MFAResponse)
async def verify_backup_code(
    request: BackupCodeVerifyRequest,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database),
    http_request: Request = None
):
    """Verify backup code during login"""
    try:
        mfa_service = MFAService(db)
        
        # Verify backup code
        success = await mfa_service.verify_backup_code(current_user["id"], request.code)
        
        if not success:
            # Log failed attempt
            await mfa_service.log_mfa_attempt(
                current_user["id"], "backup", False,
                ip_address=http_request.client.host if http_request else None,
                user_agent=http_request.headers.get("user-agent") if http_request else None
            )
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid backup code"
            )
        
        # Log successful attempt
        await mfa_service.log_mfa_attempt(
            current_user["id"], "backup", True,
            ip_address=http_request.client.host if http_request else None,
            user_agent=http_request.headers.get("user-agent") if http_request else None
        )
        
        return MFAResponse(
            message="Backup code verification successful",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify backup code"
        ) 