-- Clear TOTP data that was encrypted with the old Fernet key
-- This will allow users to re-setup TOTP with the new consistent key

UPDATE users 
SET 
    totp_enabled = false,
    totp_secret_encrypted = NULL,
    backup_codes_encrypted = NULL
WHERE totp_enabled = true;

-- Also clear any MFA attempts for TOTP
DELETE FROM mfa_attempts WHERE method = 'totp';

-- Clear backup code attempts
DELETE FROM mfa_attempts WHERE method = 'backup'; 