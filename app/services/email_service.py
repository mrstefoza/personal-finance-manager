import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.core.config import settings


class EmailService:
    """Service for sending emails"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_USER or "noreply@personalfinancemanager.com"
    
    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: str) -> bool:
        """Send an email using SMTP"""
        try:
            print(f"DEBUG: Attempting to send email to {to_email}")
            print(f"DEBUG: SMTP_HOST={self.smtp_host}, SMTP_PORT={self.smtp_port}")
            print(f"DEBUG: SMTP_USER={self.smtp_user}, SMTP_PASSWORD={'***' if self.smtp_password else 'None'}")
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Attach parts
            text_part = MIMEText(text_content, 'plain')
            html_part = MIMEText(html_content, 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            if self.smtp_host:
                print(f"DEBUG: Using SMTP server {self.smtp_host}:{self.smtp_port}")
                # Use configured SMTP (with or without authentication)
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    # Only use authentication if credentials are provided
                    if self.smtp_user and self.smtp_password:
                        print(f"DEBUG: Using SMTP authentication")
                        server.starttls()
                        server.login(self.smtp_user, self.smtp_password)
                    else:
                        print(f"DEBUG: No SMTP authentication required")
                    print(f"DEBUG: Sending email...")
                    server.send_message(msg)
                    print(f"DEBUG: Email sent successfully!")
            else:
                print(f"DEBUG: No SMTP_HOST configured, logging email instead")
                # In development, just log the email
                print(f"=== EMAIL WOULD BE SENT ===")
                print(f"To: {to_email}")
                print(f"Subject: {subject}")
                print(f"Text: {text_content}")
                print(f"HTML: {html_content}")
                print(f"=== END EMAIL ===")
            
            return True
            
        except Exception as e:
            print(f"DEBUG: Failed to send email: {str(e)}")
            print(f"DEBUG: Exception type: {type(e)}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            return False
    
    async def send_verification_email(self, to_email: str, user_name: str, verification_token: str) -> bool:
        """Send email verification email"""
        subject = "Verify Your Email - Personal Finance Manager"
        
        # Create verification URL using configured frontend hostname
        verification_url = f"{settings.FRONTEND_HOSTNAME}/verify-email?token={verification_token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Verify Your Email</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; border-radius: 5px; }}
                .button {{ display: inline-block; background-color: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; font-size: 14px; color: #6c757d; }}
                .code {{ background-color: #f8f9fa; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 16px; text-align: center; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Verify Your Email Address</h1>
                </div>
                
                <p>Hello {user_name},</p>
                
                <p>Thank you for registering with Personal Finance Manager! To complete your registration, please verify your email address by clicking the button below:</p>
                
                <div style="text-align: center;">
                    <a href="{verification_url}" class="button">Verify Email Address</a>
                </div>
                
                <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                <div class="code">{verification_url}</div>
                
                <p><strong>Important:</strong></p>
                <ul>
                    <li>This verification link will expire in 24 hours</li>
                    <li>You won't be able to log in until you verify your email</li>
                    <li>If you didn't create this account, please ignore this email</li>
                </ul>
                
                <p>If you have any questions, please contact our support team.</p>
                
                <div class="footer">
                    <p>This is an automated message from Personal Finance Manager. Please do not reply to this email.</p>
                    <p>If you're having trouble, you can also verify your email by visiting our website and entering the verification code manually.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Text content
        text_content = f"""
Verify Your Email Address

Hello {user_name},

Thank you for registering with Personal Finance Manager! To complete your registration, please verify your email address.

Verification Link: {verification_url}

Important:
- This verification link will expire in 24 hours
- You won't be able to log in until you verify your email
- If you didn't create this account, please ignore this email

If you have any questions, please contact our support team.

This is an automated message from Personal Finance Manager. Please do not reply to this email.
        """
        
        return await self.send_email(to_email, subject, html_content, text_content)
    
    async def send_mfa_code(self, to_email: str, code: str, user_name: str = None) -> bool:
        """Send MFA verification code email"""
        subject = "MFA Verification Code - Personal Finance Manager"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>MFA Verification Code</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #ffc107; color: #333; padding: 20px; text-align: center; border-radius: 5px; }}
                .code {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; font-family: monospace; font-size: 24px; text-align: center; margin: 20px 0; letter-spacing: 5px; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; font-size: 14px; color: #6c757d; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 MFA Verification Code</h1>
                </div>
                
                <p>Hello{user_name if user_name else ""},</p>
                
                <p>You requested a verification code for your Personal Finance Manager account.</p>
                
                <p>Your verification code is:</p>
                <div class="code">{code}</div>
                
                <p><strong>Important:</strong></p>
                <ul>
                    <li>This code will expire in 5 minutes</li>
                    <li>Never share this code with anyone</li>
                    <li>If you didn't request this code, please change your password immediately</li>
                </ul>
                
                <div class="footer">
                    <p>This is an automated message from Personal Finance Manager. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Text content
        text_content = f"""
MFA Verification Code

Hello{user_name if user_name else ""},

You requested a verification code for your Personal Finance Manager account.

Your verification code is: {code}

This code will expire in 5 minutes.

If you didn't request this code, please ignore this email and consider changing your password.

This is an automated message from Personal Finance Manager. Please do not reply to this email.
        """
        
        return await self.send_email(to_email, subject, html_content, text_content)
    
    async def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """Send welcome email to new users"""
        subject = "Welcome to Personal Finance Manager!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Welcome to Personal Finance Manager</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #28a745; color: white; padding: 20px; text-align: center; border-radius: 5px; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; font-size: 14px; color: #6c757d; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Welcome to Personal Finance Manager!</h1>
                </div>
                
                <p>Hello {user_name},</p>
                
                <p>Welcome to Personal Finance Manager! Your account has been successfully created and verified.</p>
                
                <p>You can now:</p>
                <ul>
                    <li>Log in to your account</li>
                    <li>Set up multi-factor authentication for enhanced security</li>
                    <li>Start managing your personal finances</li>
                    <li>Explore our features and tools</li>
                </ul>
                
                <p>If you have any questions or need help getting started, please don't hesitate to contact our support team.</p>
                
                <p>Thank you for choosing Personal Finance Manager!</p>
                
                <div class="footer">
                    <p>This is an automated message from Personal Finance Manager. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Text content
        text_content = f"""
Welcome to Personal Finance Manager!

Hello {user_name},

Welcome to Personal Finance Manager! Your account has been successfully created and verified.

You can now:
- Log in to your account
- Set up multi-factor authentication for enhanced security
- Start managing your personal finances
- Explore our features and tools

If you have any questions or need help getting started, please don't hesitate to contact our support team.

Thank you for choosing Personal Finance Manager!

This is an automated message from Personal Finance Manager. Please do not reply to this email.
        """
        
        return await self.send_email(to_email, subject, html_content, text_content) 