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
        self.from_email = settings.SMTP_USER or "noreply@pfm.com"
    
    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """Send an email"""
        if not self.smtp_host:
            # In development, just log the email instead of sending
            print(f"EMAIL (DEV MODE) - To: {to_email}")
            print(f"EMAIL (DEV MODE) - Subject: {subject}")
            print(f"EMAIL (DEV MODE) - Content: {html_content}")
            return True
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Add text and HTML parts
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                # Only use TLS and authentication if credentials are provided
                if self.smtp_user and self.smtp_password:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    async def send_mfa_code(self, to_email: str, code: str, user_name: str = None) -> bool:
        """Send MFA verification code email"""
        subject = "Your MFA Verification Code"
        
        # HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>MFA Verification Code</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 5px; }}
                .code {{ font-size: 32px; font-weight: bold; text-align: center; padding: 20px; background-color: #e9ecef; border-radius: 5px; margin: 20px 0; letter-spacing: 5px; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; font-size: 14px; color: #6c757d; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 MFA Verification Code</h1>
                </div>
                
                <p>Hello{f" {user_name}" if user_name else ""},</p>
                
                <p>You requested a verification code for your Personal Finance Manager account.</p>
                
                <div class="code">{code}</div>
                
                <p><strong>This code will expire in 5 minutes.</strong></p>
                
                <p>If you didn't request this code, please ignore this email and consider changing your password.</p>
                
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
                
                <p>Thank you for joining Personal Finance Manager! We're excited to help you take control of your finances.</p>
                
                <h3>What you can do now:</h3>
                <ul>
                    <li>Set up your profile and preferences</li>
                    <li>Enable two-factor authentication for enhanced security</li>
                    <li>Start tracking your income and expenses</li>
                    <li>Create budgets and financial goals</li>
                </ul>
                
                <p>If you have any questions, feel free to reach out to our support team.</p>
                
                <p>Best regards,<br>The Personal Finance Manager Team</p>
                
                <div class="footer">
                    <p>This is an automated message from Personal Finance Manager. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
Welcome to Personal Finance Manager!

Hello {user_name},

Thank you for joining Personal Finance Manager! We're excited to help you take control of your finances.

What you can do now:
- Set up your profile and preferences
- Enable two-factor authentication for enhanced security
- Start tracking your income and expenses
- Create budgets and financial goals

If you have any questions, feel free to reach out to our support team.

Best regards,
The Personal Finance Manager Team

This is an automated message from Personal Finance Manager. Please do not reply to this email.
        """
        
        return await self.send_email(to_email, subject, html_content, text_content) 