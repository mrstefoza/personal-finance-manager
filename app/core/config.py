from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional
from cryptography.fernet import Fernet


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Personal Finance Manager"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Encryption
    FERNET_KEY: Optional[str] = None
    
    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    
    # Firebase
    FIREBASE_SERVICE_ACCOUNT_KEY_PATH: Optional[str] = None
    FIREBASE_SERVICE_ACCOUNT_JSON: Optional[str] = None
    
    # Email (for MFA)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # MFA Session
    MFA_SESSION_DAYS: int = 7
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Generate Fernet key if not provided
        if not self.FERNET_KEY:
            self.FERNET_KEY = Fernet.generate_key().decode()


# Create settings instance
settings = Settings() 