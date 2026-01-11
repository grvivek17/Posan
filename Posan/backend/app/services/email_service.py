import os
import resend
from typing import Optional, List, Dict, Any

class EmailService:
    def __init__(self):
        # Initialize Resend with API key from environment
        api_key = os.getenv("RESEND_API_KEY")
        if not api_key:
            print("Warning: RESEND_API_KEY not found in environment variables")
        resend.api_key = api_key

    def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str, 
        from_email: str = "onboarding@resend.dev"
    ) -> Dict[str, Any]:
        """
        Send an email using Resend API
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            from_email: Sender email address (default: onboarding@resend.dev)
            
        Returns:
            Dictionary containing response from Resend API
        """
        try:
            params = {
                "from": from_email,
                "to": to_email,
                "subject": subject,
                "html": html_content
            }
            
            response = resend.Emails.send(params)
            return {"success": True, "data": response}
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return {"success": False, "error": str(e)}

    def send_welcome_email(self, to_email: str, name: str = "User"):
        """Send a standardized welcome email"""
        subject = "Welcome to Posan!"
        html_content = f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #4F46E5;">Welcome to Posan! 🚀</h1>
            <p>Hi {name},</p>
            <p>We're thrilled to have you onboard.</p>
            <p>With Posan, you can create amazing AI-powered content and track your learning journey.</p>
            <br>
            <p>Cheers,<br>The Posan Team</p>
        </div>
        """
        return self.send_email(to_email, subject, html_content)

# Create singleton instance
email_service = EmailService()
