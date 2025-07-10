-- Migration: Add MFA session tracking
-- This allows users to skip MFA for a configurable time period after successful verification

-- Add MFA session fields to user_sessions table
ALTER TABLE user_sessions 
ADD COLUMN mfa_verified_at TIMESTAMP WITHOUT TIME ZONE,
ADD COLUMN mfa_session_expires_at TIMESTAMP WITHOUT TIME ZONE;

-- Add index for efficient MFA session lookups
CREATE INDEX idx_user_sessions_mfa_verified ON user_sessions (user_id, mfa_verified_at, mfa_session_expires_at);

-- Add comment for documentation
COMMENT ON COLUMN user_sessions.mfa_verified_at IS 'Timestamp when MFA was last verified for this session';
COMMENT ON COLUMN user_sessions.mfa_session_expires_at IS 'Timestamp when MFA session expires and requires re-verification'; 