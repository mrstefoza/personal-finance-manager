"""Initial database schema

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.execute("""
        CREATE TABLE users (
            -- Core fields
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            full_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            phone VARCHAR(20) NOT NULL,
            user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('individual', 'business')),
            language_preference VARCHAR(10) DEFAULT 'hy' NOT NULL,
            currency_preference VARCHAR(3) DEFAULT 'AMD' NOT NULL,
            profile_picture VARCHAR(500),
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            profile_status VARCHAR(20) DEFAULT 'active' CHECK (profile_status IN ('active', 'inactive', 'suspended', 'pending_verification')),
            
            -- Authentication fields
            password_hash VARCHAR(255),
            email_verified BOOLEAN DEFAULT FALSE,
            email_verification_token VARCHAR(255),
            email_verification_expires TIMESTAMP,
            
            -- OAuth fields
            google_id VARCHAR(255) UNIQUE,
            oauth_provider VARCHAR(20),
            
            -- MFA fields
            mfa_enabled BOOLEAN DEFAULT FALSE,
            totp_secret_encrypted TEXT,
            totp_enabled BOOLEAN DEFAULT FALSE,
            email_mfa_enabled BOOLEAN DEFAULT FALSE,
            backup_codes_encrypted TEXT,
            
            -- Security fields
            failed_login_attempts INTEGER DEFAULT 0,
            account_locked_until TIMESTAMP,
            password_reset_token VARCHAR(255),
            password_reset_expires TIMESTAMP,
            
            -- Audit fields
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP
        )
    """)

    # Create user_sessions table
    op.execute("""
        CREATE TABLE user_sessions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            refresh_token_hash VARCHAR(255) NOT NULL,
            device_info JSONB,
            is_active BOOLEAN DEFAULT TRUE,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create email_mfa_codes table
    op.execute("""
        CREATE TABLE email_mfa_codes (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            code_hash VARCHAR(255) NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            used BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create mfa_attempts table
    op.execute("""
        CREATE TABLE mfa_attempts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            method VARCHAR(20) NOT NULL CHECK (method IN ('totp', 'email', 'backup')),
            success BOOLEAN NOT NULL,
            ip_address INET,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create indexes
    op.execute("CREATE INDEX idx_users_email ON users(email)")
    op.execute("CREATE INDEX idx_users_google_id ON users(google_id)")
    op.execute("CREATE INDEX idx_users_user_type ON users(user_type)")
    op.execute("CREATE INDEX idx_users_profile_status ON users(profile_status)")
    op.execute("CREATE INDEX idx_users_created_at ON users(created_at)")
    
    op.execute("CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id)")
    op.execute("CREATE INDEX idx_user_sessions_refresh_token ON user_sessions(refresh_token_hash)")
    op.execute("CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at)")
    op.execute("CREATE INDEX idx_user_sessions_active ON user_sessions(is_active)")
    
    op.execute("CREATE INDEX idx_email_mfa_codes_user_id ON email_mfa_codes(user_id)")
    op.execute("CREATE INDEX idx_email_mfa_codes_expires_at ON email_mfa_codes(expires_at)")
    op.execute("CREATE INDEX idx_email_mfa_codes_used ON email_mfa_codes(used)")
    
    op.execute("CREATE INDEX idx_mfa_attempts_user_id_created ON mfa_attempts(user_id, created_at)")
    op.execute("CREATE INDEX idx_mfa_attempts_method_success ON mfa_attempts(method, success)")
    op.execute("CREATE INDEX idx_mfa_attempts_ip_address ON mfa_attempts(ip_address)")

    # Create updated_at trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql'
    """)

    # Create trigger for users table
    op.execute("""
        CREATE TRIGGER update_users_updated_at 
        BEFORE UPDATE ON users 
        FOR EACH ROW 
        EXECUTE FUNCTION update_updated_at_column()
    """)


def downgrade() -> None:
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS update_users_updated_at ON users")
    
    # Drop function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")
    
    # Drop tables (in reverse order due to foreign keys)
    op.execute("DROP TABLE IF EXISTS mfa_attempts")
    op.execute("DROP TABLE IF EXISTS email_mfa_codes")
    op.execute("DROP TABLE IF EXISTS user_sessions")
    op.execute("DROP TABLE IF EXISTS users") 