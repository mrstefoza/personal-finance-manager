import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from app.core.database import Database
from app.schemas.user import UserCreate, UserUpdate, UserResponse


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """Service for user management operations"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    async def create_user(self, user_data) -> UserResponse:
        """Create a new user in the database"""
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
        
        # Create user
        user_id = uuid.uuid4()
        query = """
        INSERT INTO users (
            id, full_name, email, phone, user_type, language_preference, 
            currency_preference, password_hash, profile_status, email_verified
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
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
            "active",  # Set to active for testing
            True       # Set to True for testing
        )
        
        return UserResponse(**dict(result))
    
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
        user = await self.get_user_by_email(email)
        
        if not user:
            return None
        
        if not self.verify_password(password, user["password_hash"]):
            return None
        
        # Check if account is locked
        if user["account_locked_until"] and user["account_locked_until"] > datetime.utcnow():
            raise ValueError("Account is temporarily locked")
        
        # Check if account is active
        if user["profile_status"] != "active":
            raise ValueError("Account is not active")
        
        return user
    
    async def update_last_login(self, user_id: uuid.UUID) -> None:
        """Update user's last login timestamp"""
        query = """
        UPDATE users 
        SET last_login = $1, failed_login_attempts = 0
        WHERE id = $2
        """
        await self.db.execute(query, datetime.utcnow(), user_id)
    
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
        
        for field, value in update_data.dict(exclude_unset=True).items():
            if value is not None:
                update_fields.append(f"{field} = ${param_count}")
                values.append(value)
                param_count += 1
        
        if not update_fields:
            return await self.get_user_by_id(user_id)
        
        # Add updated_at timestamp
        update_fields.append("updated_at = $1")
        values.insert(0, datetime.utcnow())
        
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
        """Soft delete a user"""
        query = """
        UPDATE users 
        SET deleted_at = $1, profile_status = 'inactive'
        WHERE id = $2 AND deleted_at IS NULL
        """
        result = await self.db.execute(query, datetime.utcnow(), user_id)
        return result == "UPDATE 1" 