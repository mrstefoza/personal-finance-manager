import pyotp
import qrcode
import base64
import secrets
from io import BytesIO
from typing import List
from cryptography.fernet import Fernet
from app.core.config import settings


class TOTPManager:
    """TOTP (Time-based One-Time Password) management utilities"""
    
    @staticmethod
    def generate_secret() -> str:
        """Generate a new TOTP secret"""
        return pyotp.random_base32()
    
    @staticmethod
    def generate_backup_codes(count: int = 10) -> List[str]:
        """Generate backup codes for account recovery"""
        codes = []
        for _ in range(count):
            # Generate 8-digit backup codes
            code = ''.join(secrets.choice('0123456789') for _ in range(8))
            codes.append(code)
        return codes
    
    @staticmethod
    def generate_qr_code(secret: str, email: str, app_name: str = "Personal Finance Manager") -> str:
        """Generate QR code URL for TOTP setup"""
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=email,
            issuer_name=app_name
        )
        return provisioning_uri
    
    @staticmethod
    def generate_qr_code_image(secret: str, email: str, app_name: str = "Personal Finance Manager") -> str:
        """Generate QR code image as base64 string"""
        qr_url = TOTPManager.generate_qr_code(secret, email, app_name)
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    @staticmethod
    def verify_code(secret: str, code: str, window: int = 1) -> bool:
        """Verify a TOTP code"""
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=window)
    
    @staticmethod
    def get_current_code(secret: str) -> str:
        """Get the current TOTP code for a secret"""
        totp = pyotp.TOTP(secret)
        return totp.now()


class TOTPEncryption:
    """Encryption utilities for TOTP secrets and backup codes"""
    
    def __init__(self, key: str = None):
        if key:
            self.fernet = Fernet(key.encode())
        else:
            # Use the key from settings for consistency
            self.fernet = Fernet(settings.FERNET_KEY.encode())
    
    def encrypt(self, data: str) -> str:
        """Encrypt data"""
        return self.fernet.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data"""
        return self.fernet.decrypt(encrypted_data.encode()).decode()
    
    def encrypt_backup_codes(self, codes: List[str]) -> str:
        """Encrypt backup codes"""
        codes_str = ','.join(codes)
        return self.encrypt(codes_str)
    
    def decrypt_backup_codes(self, encrypted_codes: str) -> List[str]:
        """Decrypt backup codes"""
        codes_str = self.decrypt(encrypted_codes)
        return codes_str.split(',') 