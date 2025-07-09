-- Create email MFA codes table
CREATE TABLE email_mfa_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    code_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create MFA attempts table
CREATE TABLE mfa_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    method VARCHAR(20) NOT NULL CHECK (method IN ('totp', 'email', 'backup')),
    success BOOLEAN NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for MFA tables
CREATE INDEX idx_email_mfa_codes_user_id ON email_mfa_codes(user_id);
CREATE INDEX idx_email_mfa_codes_expires_at ON email_mfa_codes(expires_at);
CREATE INDEX idx_email_mfa_codes_used ON email_mfa_codes(used);

CREATE INDEX idx_mfa_attempts_user_id_created ON mfa_attempts(user_id, created_at);
CREATE INDEX idx_mfa_attempts_method_success ON mfa_attempts(method, success);
CREATE INDEX idx_mfa_attempts_ip_address ON mfa_attempts(ip_address); 