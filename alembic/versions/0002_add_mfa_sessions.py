"""Add MFA session tracking

Revision ID: 0002
Revises: 0001
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add MFA session fields to user_sessions table
    op.execute("""
        ALTER TABLE user_sessions 
        ADD COLUMN mfa_verified_at TIMESTAMP WITHOUT TIME ZONE,
        ADD COLUMN mfa_session_expires_at TIMESTAMP WITHOUT TIME ZONE
    """)

    # Add index for efficient MFA session lookups
    op.execute("""
        CREATE INDEX idx_user_sessions_mfa_verified 
        ON user_sessions (user_id, mfa_verified_at, mfa_session_expires_at)
    """)

    # Add comment for documentation
    op.execute("""
        COMMENT ON COLUMN user_sessions.mfa_verified_at 
        IS 'Timestamp when MFA was last verified for this session'
    """)
    op.execute("""
        COMMENT ON COLUMN user_sessions.mfa_session_expires_at 
        IS 'Timestamp when MFA session expires and requires re-verification'
    """)


def downgrade() -> None:
    # Drop index
    op.execute("DROP INDEX IF EXISTS idx_user_sessions_mfa_verified")
    
    # Drop columns
    op.execute("""
        ALTER TABLE user_sessions 
        DROP COLUMN IF EXISTS mfa_verified_at,
        DROP COLUMN IF EXISTS mfa_session_expires_at
    """) 