import resend
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

# Get API key from env
api_key = os.getenv("RESEND_API_KEY")

if not api_key:
    print("❌ Error: RESEND_API_KEY not found in backend/.env")
    print("Please add RESEND_API_KEY=re_... to your .env file")
    exit(1)

resend.api_key = api_key

print(f"📧 Sending email using key: {api_key[:5]}...{api_key[-5:]}")

try:
    r = resend.Emails.send({
      "from": "onboarding@resend.dev",
      "to": "grvivek17@gmail.com",
      "subject": "Hello World from Posan",
      "html": "<p>Congrats on sending your <strong>first email</strong>!</p>"
    })
    
    print("✅ Email sent successfully!")
    print(r)

except Exception as e:
    print("❌ Failed to send email:")
    print(e)
