import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from app.core.database import Database
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.email_service import EmailService


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """Service for user management operations"""
    
    def __init__(self, db: Database):
        self.db = db
        self.email_service = EmailService()
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def generate_verification_token(self) -> str:
        """Generate a secure verification token"""
        return str(uuid.uuid4())
    
    async def create_user(self, user_data) -> UserResponse:
        """Create a new user in the database with email verification"""
        # Convert dict to UserCreate if needed
        if isinstance(user_data, dict):
            user_data = UserCreate(**user_data)
        
        # Check if user already exists
        existing_user = await self.db.fetchrow(
            "SELECT id FROM users WHERE email = $1 AND deleted_at IS NULL",
            user_data.email
        )
        
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Hash password
        hashed_password = self.hash_password(user_data.password)
        
        # Generate email verification token
        verification_token = self.generate_verification_token()
        verification_expires = datetime.utcnow() + timedelta(hours=24)  # 24 hours expiry
        
        # Create user with pending verification status
        user_id = uuid.uuid4()
        query = """
        INSERT INTO users (
            id, full_name, email, phone, user_type, language_preference, 
            currency_preference, password_hash, profile_status, email_verified,
            email_verification_token, email_verification_expires
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
        RETURNING *
        """
        
        result = await self.db.fetchrow(
            query,
            user_id,
            user_data.full_name,
            user_data.email,
            user_data.phone,
            user_data.user_type,
            user_data.language_preference,
            user_data.currency_preference,
            hashed_password,
            "pending_verification",  # Set to pending verification
            False,                   # Email not verified yet
            verification_token,
            verification_expires
        )
        
        # Send verification email
        await self.email_service.send_verification_email(
            user_data.email, 
            user_data.full_name, 
            verification_token
        )
        
        return UserResponse(**dict(result))
    
    async def verify_email(self, token: str) -> bool:
        """Verify user email with token"""
        # Find user with this verification token
        query = """
        SELECT id, email_verification_expires, email_verified 
        FROM users 
        WHERE email_verification_token = $1 AND deleted_at IS NULL
        """
        user = await self.db.fetchrow(query, token)
        
        if not user:
            raise ValueError("Invalid verification token")
        
        # Check if already verified
        if user["email_verified"]:
            raise ValueError("Email is already verified")
        
        # Check if token is expired
        if user["email_verification_expires"] < datetime.utcnow():
            raise ValueError("Verification token has expired")
        
        # Update user to verified status
        update_query = """
        UPDATE users 
        SET email_verified = TRUE, 
            profile_status = 'active',
            email_verification_token = NULL,
            email_verification_expires = NULL,
            updated_at = $1
        WHERE id = $2
        """
        await self.db.execute(update_query, datetime.utcnow(), user["id"])
        
        return True
    
    async def resend_verification_email(self, email: str) -> bool:
        """Resend verification email for existing user"""
        # Find user by email
        user = await self.get_user_by_email(email)
        
        if not user:
            raise ValueError("User not found")
        
        if user["email_verified"]:
            raise ValueError("Email is already verified")
        
        # Generate new verification token
        verification_token = self.generate_verification_token()
        verification_expires = datetime.utcnow() + timedelta(hours=24)
        
        # Update user with new token
        update_query = """
        UPDATE users 
        SET email_verification_token = $1,
            email_verification_expires = $2,
            updated_at = $3
        WHERE id = $4
        """
        await self.db.execute(update_query, verification_token, verification_expires, datetime.utcnow(), user["id"])
        
        # Send verification email
        await self.email_service.send_verification_email(
            user["email"], 
            user["full_name"], 
            verification_token
        )
        
        return True
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        query = """
        SELECT * FROM users 
        WHERE email = $1 AND deleted_at IS NULL
        """
        result = await self.db.fetchrow(query, email)
        return dict(result) if result else None
    
    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        query = """
        SELECT * FROM users 
        WHERE id = $1 AND deleted_at IS NULL
        """
        result = await self.db.fetchrow(query, user_id)
        return dict(result) if result else None
    
    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password"""
        print(f"DEBUG: authenticate_user called for email: {email}")
        user = await self.get_user_by_email(email)
        
        if not user:
            print(f"DEBUG: User not found for email: {email}")
            return None
        
        print(f"DEBUG: User found, password_hash exists: {user.get('password_hash') is not None}")
        print(f"DEBUG: User profile_status: {user.get('profile_status')}")
        print(f"DEBUG: User email_verified: {user.get('email_verified')}")
        
        try:
            if not self.verify_password(password, user["password_hash"]):
                print(f"DEBUG: Password verification failed")
                return None
            print(f"DEBUG: Password verification succeeded")
        except Exception as e:
            print(f"Password verification exception: {e}")
            return None
        
        # Check if account is locked
        if user["account_locked_until"] and user["account_locked_until"] > datetime.utcnow():
            raise ValueError("Account is temporarily locked")
        
        # Check if email is verified
        if not user["email_verified"]:
            raise ValueError("Please verify your email address before logging in")
        
        # Check if account is active
        if user["profile_status"] != "active":
            raise ValueError("Account is not active")
        
        return user
    
    async def update_last_login(self, user_id: uuid.UUID) -> None:
        """Update user's last login timestamp"""
        query = """
        UPDATE users 
        SET last_login = $1, updated_at = $1
        WHERE id = $2
        """
        await self.db.execute(query, datetime.utcnow(), user_id)
    
    async def update_user(self, user_id: uuid.UUID, user_data: UserUpdate) -> Optional[UserResponse]:
        """Update user information"""
        # Build dynamic update query
        update_fields = []
        values = []
        param_count = 1
        
        if user_data.full_name is not None:
            update_fields.append(f"full_name = ${param_count}")
            values.append(user_data.full_name)
            param_count += 1
        
        if user_data.phone is not None:
            update_fields.append(f"phone = ${param_count}")
            values.append(user_data.phone)
            param_count += 1
        
        if user_data.language_preference is not None:
            update_fields.append(f"language_preference = ${param_count}")
            values.append(user_data.language_preference)
            param_count += 1
        
        if user_data.currency_preference is not None:
            update_fields.append(f"currency_preference = ${param_count}")
            values.append(user_data.currency_preference)
            param_count += 1
        
        if user_data.profile_picture is not None:
            update_fields.append(f"profile_picture = ${param_count}")
            values.append(user_data.profile_picture)
            param_count += 1
        
        if not update_fields:
            return None
        
        # Add updated_at and user_id
        update_fields.append(f"updated_at = ${param_count}")
        values.append(datetime.utcnow())
        param_count += 1
        
        values.append(user_id)
        
        query = f"""
        UPDATE users 
        SET {', '.join(update_fields)}
        WHERE id = ${param_count} AND deleted_at IS NULL
        RETURNING *
        """
        
        result = await self.db.fetchrow(query, *values)
        return UserResponse(**dict(result)) if result else None
    
    async def increment_failed_login_attempts(self, user_id: uuid.UUID) -> None:
        """Increment failed login attempts and lock account if needed"""
        # Get current failed attempts
        user = await self.get_user_by_id(user_id)
        if not user:
            return
        
        failed_attempts = user["failed_login_attempts"] + 1
        
        if failed_attempts >= 5:
            # Lock account for 15 minutes
            lock_until = datetime.utcnow().replace(second=0, microsecond=0)
            lock_until = lock_until.replace(minute=lock_until.minute + 15)
            
            query = """
            UPDATE users 
            SET failed_login_attempts = $1, account_locked_until = $2
            WHERE id = $3
            """
            await self.db.execute(query, failed_attempts, lock_until, user_id)
        else:
            query = """
            UPDATE users 
            SET failed_login_attempts = $1
            WHERE id = $2
            """
            await self.db.execute(query, failed_attempts, user_id)
    
    async def update_user_profile(self, user_id: uuid.UUID, update_data: UserUpdate) -> Optional[Dict[str, Any]]:
        """Update user profile"""
        # Build update query dynamically
        update_fields = []
        values = []
        param_count = 1
        
        for field, value in update_data.model_dump(exclude_unset=True).items():
            if value is not None:
                update_fields.append(f"{field} = ${param_count}")
                values.append(value)
                param_count += 1
        
        if not update_fields:
            return await self.get_user_by_id(user_id)
        
        # Add updated_at timestamp with correct parameter number
        update_fields.append(f"updated_at = ${param_count}")
        values.append(datetime.utcnow())
        param_count += 1
        
        query = f"""
        UPDATE users 
        SET {', '.join(update_fields)}
        WHERE id = ${param_count} AND deleted_at IS NULL
        RETURNING *
        """
        
        values.append(user_id)
        
        result = await self.db.fetchrow(query, *values)
        return dict(result) if result else None
    
    async def delete_user(self, user_id: uuid.UUID) -> bool:
        """Delete a user (soft delete)"""
        query = """
        UPDATE users 
        SET deleted_at = $1 
        WHERE id = $2 AND deleted_at IS NULL
        """
        result = await self.db.execute(query, datetime.utcnow(), user_id)
        return result == "DELETE 1"
    
    async def store_refresh_token(self, user_id: uuid.UUID, refresh_token: str) -> None:
        """Store refresh token hash in user_sessions table"""
        import hashlib
        from datetime import datetime, timedelta
        from app.core.config import settings
        
        # Hash the refresh token
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        
        # Calculate expiration time
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        # Store in user_sessions table
        query = """
        INSERT INTO user_sessions (user_id, refresh_token_hash, expires_at, is_active)
        VALUES ($1, $2, $3, TRUE)
        """
        
        await self.db.execute(query, user_id, token_hash, expires_at) 