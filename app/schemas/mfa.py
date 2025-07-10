from pydantic import BaseModel, field_validator
from typing import Optional
from uuid import UUID


class TOTPSetupRequest(BaseModel):
    """Request to enable TOTP MFA"""
    pass


class TOTPSetupResponse(BaseModel):
    """Response for TOTP setup with QR code and secret"""
    qr_code_url: str
    secret: str
    backup_codes: list[str]


class TOTPVerifyRequest(BaseModel):
    """Request to verify TOTP code during setup"""
    code: str
    
    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        if not v.isdigit() or len(v) != 6:
            raise ValueError('TOTP code must be a 6-digit number')
        return v


class TOTPDisableRequest(BaseModel):
    """Request to disable TOTP MFA"""
    code: str
    
    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        if not v.isdigit() or len(v) != 6:
            raise ValueError('TOTP code must be a 6-digit number')
        return v


class EmailMFASetupRequest(BaseModel):
    """Request to enable email MFA"""
    pass


class EmailMFASendCodeRequest(BaseModel):
    """Request to send email MFA code"""
    email: str


class EmailMFAVerifyRequest(BaseModel):
    """Request to verify email MFA code"""
    code: str
    
    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        if not v.isdigit() or len(v) != 6:
            raise ValueError('Email MFA code must be a 6-digit number')
        return v


class MFAResponse(BaseModel):
    """Generic MFA response"""
    message: str
    success: bool


class MFAStatusResponse(BaseModel):
    """Response showing MFA status for a user"""
    totp_enabled: bool
    email_mfa_enabled: bool
    mfa_required: bool
    backup_codes_remaining: int = 0


# MFA Login Flow Schemas
class LoginResponse(BaseModel):
    """Response for login - either tokens or MFA required"""
    requires_mfa: bool
    mfa_type: Optional[str] = None  # "totp" or "email"
    temp_token: Optional[str] = None  # Temporary token for MFA verification
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class MFALoginVerifyRequest(BaseModel):
    """Request to verify MFA during login"""
    temp_token: str
    code: str
    mfa_type: str  # "totp" or "email"
    remember_device: Optional[bool] = False
    
    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        if not v.isdigit() or len(v) != 6:
            raise ValueError('MFA code must be a 6-digit number')
        return v
    
    @field_validator('mfa_type')
    @classmethod
    def validate_mfa_type(cls, v):
        if v not in ['totp', 'email']:
            raise ValueError('MFA type must be "totp" or "email"')
        return v


class BackupCodeVerifyRequest(BaseModel):
    """Request to verify backup code"""
    code: str
    
    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        if not v.isdigit() or len(v) != 8:
            raise ValueError('Backup code must be an 8-digit number')
        return v 