"""Test SMTP email sending"""
import os
import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

from app.services.smtp_email_service import smtp_email_service

with open('smtp_result.txt', 'w') as f:
    f.write("SMTP Configuration Test\n")
    f.write("=" * 50 + "\n")
    f.write(f"Host: {smtp_email_service.smtp_host}\n")
    f.write(f"Port: {smtp_email_service.smtp_port}\n")
    f.write(f"User: {smtp_email_service.smtp_user}\n")
    f.write(f"Password Set: {bool(smtp_email_service.smtp_password)}\n")
    f.write("=" * 50 + "\n\n")
    
    f.write("Sending test email...\n")
    
    result = smtp_email_service.send_email(
        to_emails=['rvposhika26@gmail.com'],
        subject='Test Email from POSAN Admin',
        html_content='''
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #667eea;">Test Successful!</h1>
            <p>Your SMTP configuration is working correctly.</p>
            <p>You can now send promotional emails from the POSAN Admin Dashboard.</p>
        </div>
        '''
    )
    
    f.write(f"\nResult: {result}\n")
    
print("Test completed! Check smtp_result.txt for results.")
