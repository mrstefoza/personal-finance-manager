"""Add Firebase UID support

Revision ID: 0003
Revises: 0002
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add firebase_uid column to users table
    op.execute("""
        ALTER TABLE users 
        ADD COLUMN firebase_uid VARCHAR(255) UNIQUE
    """)
    
    # Create index for firebase_uid
    op.execute("""
        CREATE INDEX idx_users_firebase_uid ON users(firebase_uid)
    """)


def downgrade() -> None:
    # Drop index first
    op.execute("""
        DROP INDEX IF EXISTS idx_users_firebase_uid
    """)
    
    # Drop firebase_uid column
    op.execute("""
        ALTER TABLE users 
        DROP COLUMN IF EXISTS firebase_uid
    """) 