"""
SMTP Email Service for sending promotional emails via Gmail
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


class SMTPEmailService:
    """Service for sending emails via SMTP (Gmail)"""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_name = os.getenv("SMTP_FROM_NAME", "POSAN Kids Magazine")
        
        if not self.smtp_user or not self.smtp_password:
            print("Warning: SMTP_USER or SMTP_PASSWORD not configured")
    
    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send an email using SMTP
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (optional)
            
        Returns:
            Dictionary containing success status and details
        """
        try:
            if not self.smtp_user or not self.smtp_password:
                return {"success": False, "error": "SMTP not configured"}
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.smtp_user}>"
            msg['To'] = ", ".join(to_emails)
            
            # Add plain text version
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)
            
            # Add HTML version
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)
            
            # Connect and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, to_emails, msg.as_string())
            
            return {
                "success": True,
                "message": f"Email sent to {len(to_emails)} recipient(s)",
                "recipients": to_emails
            }
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"SMTP Authentication Error: {str(e)}")
            return {"success": False, "error": "Authentication failed. Check SMTP credentials."}
        except smtplib.SMTPException as e:
            print(f"SMTP Error: {str(e)}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def generate_weekly_arrivals_email(
        self,
        magazines: List[Dict[str, Any]],
        products: List[Dict[str, Any]],
        recipient_name: str = "Dear Reader",
        base_url: str = "http://localhost:5173"
    ) -> str:
        """
        Generate beautiful HTML email for weekly new arrivals
        
        Args:
            magazines: List of new magazine dictionaries
            products: List of new product dictionaries
            recipient_name: Name of the recipient
            base_url: Base URL of the frontend application
            
        Returns:
            HTML email content
        """
        current_date = datetime.now().strftime("%B %d, %Y")
        store_url = f"{base_url}/store"
        magazines_url = f"{base_url}/magazines"
        
        # Generate magazine cards
        magazine_html = ""
        for mag in magazines:
            magazine_html += f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        border-radius: 16px; padding: 24px; margin-bottom: 20px;
                        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);">
                <div style="display: flex; align-items: center;">
                    {'<img src="' + mag.get("cover_image_url", "") + '" style="width: 120px; height: 160px; border-radius: 12px; object-fit: cover; margin-right: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.3);" />' if mag.get("cover_image_url") else ''}
                    <div style="flex: 1;">
                        <h3 style="color: white; margin: 0 0 8px 0; font-size: 20px; font-weight: 700;">📚 {mag.get("title", "New Magazine")}</h3>
                        <p style="color: rgba(255,255,255,0.9); margin: 0 0 12px 0; font-size: 14px; line-height: 1.6;">
                            {mag.get("description", "")[:150]}{'...' if len(mag.get("description", "")) > 150 else ''}
                        </p>
                        <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                            <span style="background: rgba(255,255,255,0.2); padding: 6px 12px; border-radius: 20px; color: white; font-size: 12px;">
                                🎂 Ages: {mag.get("age_group", "All ages")}
                            </span>
                            <span style="background: rgba(255,255,255,0.2); padding: 6px 12px; border-radius: 20px; color: white; font-size: 12px;">
                                📖 Issue #{mag.get("issue_number", "N/A")}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            """
        
        # Generate product cards
        product_html = ""
        for prod in products:
            discount = ""
            if prod.get("original_price") and prod.get("price"):
                discount_pct = int(((prod["original_price"] - prod["price"]) / prod["original_price"]) * 100)
                if discount_pct > 0:
                    discount = f'<span style="background: #ff4757; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">{discount_pct}% OFF</span>'
            
            product_html += f"""
            <div style="background: white; border-radius: 16px; padding: 20px; margin-bottom: 16px;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.08); border: 1px solid #eee;">
                <div style="display: flex; align-items: center;">
                    {'<img src="' + prod.get("image_url", "") + '" style="width: 80px; height: 100px; border-radius: 8px; object-fit: cover; margin-right: 16px;" />' if prod.get("image_url") else ''}
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                            <h4 style="color: #1a1a2e; margin: 0; font-size: 16px; font-weight: 600;">
                                {'✨ ' if prod.get("is_new") else ''}{'🔥 ' if prod.get("is_bestseller") else ''}{prod.get("name", "New Product")}
                            </h4>
                            {discount}
                        </div>
                        <p style="color: #666; margin: 0 0 8px 0; font-size: 13px;">
                            {prod.get("description", "")[:100]}{'...' if len(prod.get("description", "")) > 100 else ''}
                        </p>
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <span style="color: #4F46E5; font-weight: 700; font-size: 18px;">₹{prod.get("price", 0)}</span>
                            {'<span style="color: #999; text-decoration: line-through; font-size: 14px;">₹' + str(prod.get("original_price", "")) + '</span>' if prod.get("original_price") and prod.get("original_price") > prod.get("price", 0) else ""}
                            <span style="color: #888; font-size: 12px;">Ages: {prod.get("age_range", "All")}</span>
                        </div>
                    </div>
                </div>
            </div>
            """
        
        # Complete email template
        # Add zero-width space and unique content to prevent Gmail from hiding as "quoted text"
        unique_id = datetime.now().strftime("%Y%m%d%H%M%S")
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Weekly New Arrivals at POSAN</title>
        </head>
        <body style="margin: 0; padding: 0; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
            <!-- Prevent Gmail from hiding content -->
            <div style="display:none;font-size:1px;color:#ffffff;line-height:1px;max-height:0px;max-width:0px;opacity:0;overflow:hidden;">
                &#8204;&#847; &#8204;&#847; &#8204;&#847; &#8204;&#847; New arrivals just for you! {unique_id}
            </div>
            <div style="max-width: 640px; margin: 0 auto; padding: 40px 20px;">
                
                <!-- Header -->
                <div style="text-align: center; margin-bottom: 40px;">
                    <div style="background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%); 
                                display: inline-block; padding: 16px 40px; border-radius: 50px;
                                box-shadow: 0 10px 40px rgba(79, 70, 229, 0.4);">
                        <h1 style="color: white; margin: 0; font-size: 28px; font-weight: 800; letter-spacing: 1px;">
                            🌟 POSAN 🌟
                        </h1>
                        <p style="color: rgba(255,255,255,0.9); margin: 8px 0 0 0; font-size: 13px; letter-spacing: 2px;">
                            KIDS MAGAZINE & STORE
                        </p>
                    </div>
                </div>
                
                <!-- Main Card -->
                <div style="background: white; border-radius: 24px; padding: 40px; 
                            box-shadow: 0 20px 60px rgba(0,0,0,0.1);">
                    
                    <!-- Greeting -->
                    <div style="text-align: center; margin-bottom: 32px;">
                        <h2 style="color: #1a1a2e; margin: 0 0 12px 0; font-size: 24px; font-weight: 700;">
                            🎉 This Week's New Arrivals! 🎉
                        </h2>
                        <p style="color: #666; margin: 0; font-size: 15px;">
                            {current_date}
                        </p>
                    </div>
                    
                    <p style="color: #444; font-size: 16px; line-height: 1.8; margin-bottom: 32px;">
                        {recipient_name},<br><br>
                        We're excited to share the latest additions to POSAN! Check out our fresh new magazines filled with 
                        amazing stories, puzzles, and activities, plus exciting new activity books for endless fun and learning! 📚✨
                    </p>
                    
                    <!-- New Magazines Section -->
                    {f'''
                    <div style="margin-bottom: 40px;">
                        <h3 style="color: #1a1a2e; font-size: 18px; margin: 0 0 20px 0; 
                                   padding-bottom: 12px; border-bottom: 2px solid #4F46E5;">
                            📰 New Magazines This Week
                        </h3>
                        {magazine_html if magazine_html else '<p style="color: #888; font-style: italic;">No new magazines this week - check back soon!</p>'}
                    </div>
                    ''' if magazine_html else ''}
                    
                    <!-- New Products Section -->
                    {f'''
                    <div style="margin-bottom: 40px;">
                        <h3 style="color: #1a1a2e; font-size: 18px; margin: 0 0 20px 0;
                                   padding-bottom: 12px; border-bottom: 2px solid #7C3AED;">
                            🛒 New in Store
                        </h3>
                        {product_html if product_html else '<p style="color: #888; font-style: italic;">No new products this week - check back soon!</p>'}
                    </div>
                    ''' if product_html else ''}
                    
                    <!-- CTA Button -->
                    <div style="text-align: center; margin-top: 40px;">
                        <a href="{store_url}" style="display: inline-block; background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
                                          color: white; text-decoration: none; padding: 16px 48px; border-radius: 50px;
                                          font-weight: 700; font-size: 16px; letter-spacing: 0.5px;
                                          box-shadow: 0 10px 30px rgba(79, 70, 229, 0.4);
                                          transition: transform 0.3s ease;">
                            🚀 Explore Store
                        </a>
                        <a href="{magazines_url}" style="display: inline-block; background: linear-gradient(135deg, #FF6B9D 0%, #FF9F1C 100%);
                                          color: white; text-decoration: none; padding: 16px 48px; border-radius: 50px;
                                          font-weight: 700; font-size: 16px; letter-spacing: 0.5px;
                                          box-shadow: 0 10px 30px rgba(255, 107, 157, 0.4);
                                          margin-left: 16px;">
                            📚 Read Magazines
                        </a>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="text-align: center; margin-top: 40px; padding: 20px;">
                    <p style="color: #888; font-size: 13px; margin: 0 0 12px 0;">
                        Thank you for being part of the POSAN family! 💜
                    </p>
                    <p style="color: #aaa; font-size: 11px; margin: 0;">
                        If you no longer wish to receive these emails, please contact us.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def generate_custom_promotional_email(
        self,
        subject: str,
        heading: str,
        content: str,
        cta_text: str = "Learn More",
        cta_url: str = "#"
    ) -> str:
        """
        Generate a custom promotional email
        
        Args:
            subject: Email subject
            heading: Email heading
            content: Main email content (HTML supported)
            cta_text: Call-to-action button text
            cta_url: Call-to-action button URL
            
        Returns:
            HTML email content
        """
        current_date = datetime.now().strftime("%B %d, %Y")
        unique_id = datetime.now().strftime("%Y%m%d%H%M%S")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{subject}</title>
        </head>
        <body style="margin: 0; padding: 0; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
            <!-- Prevent Gmail from hiding content -->
            <div style="display:none;font-size:1px;color:#ffffff;line-height:1px;max-height:0px;max-width:0px;opacity:0;overflow:hidden;">
                &#8204;&#847; &#8204;&#847; &#8204;&#847; &#8204;&#847; {heading} {unique_id}
            </div>
            <div style="max-width: 640px; margin: 0 auto; padding: 40px 20px;">
                
                <!-- Header -->
                <div style="text-align: center; margin-bottom: 40px;">
                    <div style="background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%); 
                                display: inline-block; padding: 16px 40px; border-radius: 50px;
                                box-shadow: 0 10px 40px rgba(79, 70, 229, 0.4);">
                        <h1 style="color: white; margin: 0; font-size: 28px; font-weight: 800; letter-spacing: 1px;">
                            🌟 POSAN 🌟
                        </h1>
                        <p style="color: rgba(255,255,255,0.9); margin: 8px 0 0 0; font-size: 13px; letter-spacing: 2px;">
                            KIDS MAGAZINE & STORE
                        </p>
                    </div>
                </div>
                
                <!-- Main Card -->
                <div style="background: white; border-radius: 24px; padding: 40px; 
                            box-shadow: 0 20px 60px rgba(0,0,0,0.1);">
                    
                    <!-- Heading -->
                    <div style="text-align: center; margin-bottom: 32px;">
                        <h2 style="color: #1a1a2e; margin: 0 0 12px 0; font-size: 24px; font-weight: 700;">
                            {heading}
                        </h2>
                        <p style="color: #666; margin: 0; font-size: 14px;">
                            {current_date}
                        </p>
                    </div>
                    
                    <!-- Content -->
                    <div style="color: #444; font-size: 16px; line-height: 1.8; margin-bottom: 32px;">
                        {content}
                    </div>
                    
                    <!-- CTA Button -->
                    <div style="text-align: center; margin-top: 40px;">
                        <a href="{cta_url}" style="display: inline-block; background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
                                          color: white; text-decoration: none; padding: 16px 48px; border-radius: 50px;
                                          font-weight: 700; font-size: 16px; letter-spacing: 0.5px;
                                          box-shadow: 0 10px 30px rgba(79, 70, 229, 0.4);">
                            {cta_text}
                        </a>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="text-align: center; margin-top: 40px; padding: 20px;">
                    <p style="color: #888; font-size: 13px; margin: 0 0 12px 0;">
                        Thank you for being part of the POSAN family! 💜
                    </p>
                    <p style="color: #aaa; font-size: 11px; margin: 0;">
                        If you no longer wish to receive these emails, please contact us.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html


# Create singleton instance
smtp_email_service = SMTPEmailService()
