import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from passlib.context import CryptContext
from app.core.database import Database
from app.utils.totp import TOTPManager, TOTPEncryption
from app.schemas.mfa import TOTPSetupResponse
from app.services.email_service import EmailService


# Password hashing context for email MFA codes
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class MFAService:
    """Service for MFA operations"""
    
    def __init__(self, db: Database):
        self.db = db
        self.totp_encryption = TOTPEncryption()
        self.email_service = EmailService()
    
    # TOTP MFA Methods
    
    async def setup_totp(self, user_id: uuid.UUID, email: str) -> TOTPSetupResponse:
        """Setup TOTP MFA for a user"""
        # Generate TOTP secret and backup codes
        secret = TOTPManager.generate_secret()
        backup_codes = TOTPManager.generate_backup_codes()
        
        # Encrypt secret and backup codes
        encrypted_secret = self.totp_encryption.encrypt(secret)
        encrypted_backup_codes = self.totp_encryption.encrypt_backup_codes(backup_codes)
        
        # Store encrypted secret and backup codes (but don't enable yet)
        query = """
        UPDATE users 
        SET totp_secret_encrypted = $1, backup_codes_encrypted = $2, updated_at = $3
        WHERE id = $4
        """
        await self.db.execute(query, encrypted_secret, encrypted_backup_codes, datetime.utcnow(), user_id)
        
        # Generate QR code
        qr_code_url = TOTPManager.generate_qr_code_image(secret, email)
        
        return TOTPSetupResponse(
            qr_code_url=qr_code_url,
            secret=secret,  # Only shown during setup
            backup_codes=backup_codes
        )
    
    async def verify_totp_setup(self, user_id: uuid.UUID, code: str) -> bool:
        """Verify TOTP code during setup and enable TOTP"""
        # Get encrypted secret
        user = await self.get_user_by_id(user_id)
        if not user or not user.get("totp_secret_encrypted"):
            return False
        
        # Decrypt secret
        secret = self.totp_encryption.decrypt(user["totp_secret_encrypted"])
        
        # Verify code
        if not TOTPManager.verify_code(secret, code):
            return False
        
        # Enable TOTP
        query = """
        UPDATE users 
        SET totp_enabled = TRUE, updated_at = $1
        WHERE id = $2
        """
        await self.db.execute(query, datetime.utcnow(), user_id)
        
        return True
    
    async def verify_totp_login(self, user_id: uuid.UUID, code: str) -> bool:
        """Verify TOTP code during login"""
        user = await self.get_user_by_id(user_id)
        if not user or not user.get("totp_enabled") or not user.get("totp_secret_encrypted"):
            return False
        
        # Decrypt secret
        secret = self.totp_encryption.decrypt(user["totp_secret_encrypted"])
        
        # Verify code
        return TOTPManager.verify_code(secret, code)
    
    async def disable_totp(self, user_id: uuid.UUID, code: str) -> bool:
        """Disable TOTP MFA"""
        # First verify the code
        if not await self.verify_totp_login(user_id, code):
            return False
        
        # Disable TOTP and clear secrets
        query = """
        UPDATE users 
        SET totp_enabled = FALSE, totp_secret_encrypted = NULL, 
            backup_codes_encrypted = NULL, updated_at = $1
        WHERE id = $2
        """
        await self.db.execute(query, datetime.utcnow(), user_id)
        
        return True
    
    async def verify_backup_code(self, user_id: uuid.UUID, code: str) -> bool:
        """Verify a backup code and mark it as used"""
        user = await self.get_user_by_id(user_id)
        if not user or not user.get("backup_codes_encrypted"):
            return False
        
        # Decrypt backup codes
        backup_codes = self.totp_encryption.decrypt_backup_codes(user["backup_codes_encrypted"])
        
        # Check if code exists
        if code not in backup_codes:
            return False
        
        # Remove the used code and update
        backup_codes.remove(code)
        encrypted_backup_codes = self.totp_encryption.encrypt_backup_codes(backup_codes)
        
        query = """
        UPDATE users 
        SET backup_codes_encrypted = $1, updated_at = $2
        WHERE id = $3
        """
        await self.db.execute(query, encrypted_backup_codes, datetime.utcnow(), user_id)
        
        return True
    
    # Email MFA Methods
    
    async def send_email_mfa_code(self, user_id: uuid.UUID, email: str) -> str:
        """Send email MFA code and store it"""
        print(f"DEBUG: send_email_mfa_code called for user_id: {user_id}, email: {email}")
        
        # Check if email MFA is enabled for this user
        user = await self.get_user_by_id(user_id)
        if not user:
            print(f"DEBUG: User not found: {user_id}")
            raise ValueError("User not found")
        
        print(f"DEBUG: User email_mfa_enabled: {user.get('email_mfa_enabled')}")
        
        if not user.get("email_mfa_enabled"):
            print(f"DEBUG: Email MFA not enabled for user: {user_id}")
            raise ValueError("Email MFA is not enabled for this user")
        
        # Generate 6-digit code
        code = ''.join([str(uuid.uuid4().int % 10) for _ in range(6)])
        code_hash = pwd_context.hash(code)
        
        print(f"DEBUG: Generated code: {code}")
        
        # Store code with expiration (5 minutes)
        expires_at = datetime.utcnow() + timedelta(minutes=5)
        
        query = """
        INSERT INTO email_mfa_codes (user_id, code_hash, expires_at)
        VALUES ($1, $2, $3)
        """
        await self.db.execute(query, user_id, code_hash, expires_at)
        
        # Get user name for email
        user_name = user.get("full_name") if user else None
        
        # Send email with code
        email_sent = await self.email_service.send_mfa_code(email, code, user_name)
        
        if not email_sent:
            # If email fails, still return code for testing in development
            print(f"Failed to send email, returning code for testing: {code}")
        
        # In development mode, always return the code for testing
        # In production, you might want to return a success message instead
        return code
    
    async def verify_email_mfa_code(self, user_id: uuid.UUID, code: str) -> bool:
        """Verify email MFA code"""
        # Get the most recent unused code
        query = """
        SELECT code_hash, expires_at, used
        FROM email_mfa_codes 
        WHERE user_id = $1 AND used = FALSE AND expires_at > $2
        ORDER BY created_at DESC 
        LIMIT 1
        """
        result = await self.db.fetchrow(query, user_id, datetime.utcnow())
        
        if not result:
            return False
        
        # Verify code
        if not pwd_context.verify(code, result["code_hash"]):
            return False
        
        # Mark code as used
        update_query = """
        UPDATE email_mfa_codes 
        SET used = TRUE 
        WHERE user_id = $1 AND code_hash = $2
        """
        await self.db.execute(update_query, user_id, result["code_hash"])
        
        return True
    
    async def enable_email_mfa(self, user_id: uuid.UUID) -> bool:
        """Enable email MFA for a user"""
        query = """
        UPDATE users 
        SET email_mfa_enabled = TRUE, updated_at = $1
        WHERE id = $2
        """
        await self.db.execute(query, datetime.utcnow(), user_id)
        return True
    
    async def disable_email_mfa(self, user_id: uuid.UUID) -> bool:
        """Disable email MFA for a user"""
        query = """
        UPDATE users 
        SET email_mfa_enabled = FALSE, updated_at = $1
        WHERE id = $2
        """
        await self.db.execute(query, datetime.utcnow(), user_id)
        return True
    
    async def verify_totp(self, user_id: uuid.UUID, code: str) -> bool:
        """Verify TOTP code (alias for verify_totp_login)"""
        return await self.verify_totp_login(user_id, code)
    
    async def setup_email_mfa(self, user_id: uuid.UUID) -> bool:
        """Setup email MFA for a user (alias for enable_email_mfa)"""
        return await self.enable_email_mfa(user_id)
    
    async def verify_email_mfa(self, user_id: uuid.UUID, code: str) -> bool:
        """Verify email MFA code (alias for verify_email_mfa_code)"""
        return await self.verify_email_mfa_code(user_id, code)

    # Utility Methods
    
    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        query = """
        SELECT * FROM users 
        WHERE id = $1 AND deleted_at IS NULL
        """
        result = await self.db.fetchrow(query, user_id)
        return dict(result) if result else None
    
    async def get_mfa_status(self, user_id: uuid.UUID) -> Dict[str, bool]:
        """Get MFA status for a user"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return {"totp_enabled": False, "email_mfa_enabled": False, "mfa_required": False, "backup_codes_remaining": 0}
        
        # Count backup codes if TOTP is enabled
        backup_codes_remaining = 0
        if user.get("totp_enabled") and user.get("backup_codes_encrypted"):
            try:
                backup_codes = self.totp_encryption.decrypt_backup_codes(user["backup_codes_encrypted"])
                backup_codes_remaining = len(backup_codes)
            except:
                backup_codes_remaining = 0
        
        return {
            "totp_enabled": user.get("totp_enabled", False),
            "email_mfa_enabled": user.get("email_mfa_enabled", False),
            "mfa_required": user.get("totp_enabled", False) or user.get("email_mfa_enabled", False),
            "backup_codes_remaining": backup_codes_remaining
        }
    
    async def log_mfa_attempt(self, user_id: uuid.UUID, method: str, success: bool, ip_address: str = None, user_agent: str = None) -> None:
        """Log MFA attempt for security monitoring"""
        query = """
        INSERT INTO mfa_attempts (user_id, method, success, ip_address, user_agent)
        VALUES ($1, $2, $3, $4, $5)
        """
        await self.db.execute(query, user_id, method, success, ip_address, user_agent) 