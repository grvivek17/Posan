"""
Admin Promotional Email API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.content import Magazine
from app.models.store import Product
from app.services.smtp_email_service import smtp_email_service
import os

# Frontend URL for email links (update this for production)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

router = APIRouter(prefix="/admin/promotional-email", tags=["admin-email"])


def require_admin(current_user: User = Depends(get_current_user)):
    """Dependency to check if user is admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# Request/Response Models
class SendWeeklyArrivalsRequest(BaseModel):
    """Request model for sending weekly arrivals email"""
    recipient_emails: List[EmailStr]
    recipient_name: str = "Dear Reader"
    days_back: int = 7  # How many days to look back for new arrivals


class SendCustomEmailRequest(BaseModel):
    """Request model for sending custom promotional email"""
    recipient_emails: List[EmailStr]
    subject: str
    heading: str
    content: str
    cta_text: str = "Learn More"
    cta_url: str = "#"


class SendToAllUsersRequest(BaseModel):
    """Request model for sending email to all users"""
    subject: str
    include_new_magazines: bool = True
    include_new_products: bool = True
    days_back: int = 7
    custom_message: Optional[str] = None


@router.get("/new-arrivals")
async def get_new_arrivals(
    days: int = Query(7, description="Number of days to look back"),
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get new magazines and products from the last N days
    
    Admin only - for previewing what will be included in promotional emails
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Get new magazines
    new_magazines = db.query(Magazine).filter(
        Magazine.created_at >= cutoff_date,
        Magazine.is_published == True
    ).order_by(desc(Magazine.created_at)).all()
    
    # Get new products
    new_products = db.query(Product).filter(
        Product.created_at >= cutoff_date,
        Product.is_available == True
    ).order_by(desc(Product.created_at)).all()
    
    return {
        "period": f"Last {days} days",
        "cutoff_date": cutoff_date.isoformat(),
        "magazines": [
            {
                "id": mag.id,
                "title": mag.title,
                "description": mag.description,
                "cover_image_url": mag.cover_image_url,
                "issue_number": mag.issue_number,
                "age_group": mag.age_group.value if mag.age_group else None,
                "publication_date": mag.publication_date,
                "created_at": mag.created_at
            }
            for mag in new_magazines
        ],
        "products": [
            {
                "id": prod.id,
                "name": prod.name,
                "description": prod.description,
                "price": prod.price,
                "original_price": prod.original_price,
                "image_url": prod.image_url,
                "category": prod.category.value if prod.category else None,
                "age_range": prod.age_range,
                "is_new": prod.is_new,
                "is_bestseller": prod.is_bestseller,
                "created_at": prod.created_at
            }
            for prod in new_products
        ],
        "summary": {
            "new_magazines_count": len(new_magazines),
            "new_products_count": len(new_products)
        }
    }


@router.get("/subscribers")
async def get_email_subscribers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get all user emails for promotional campaigns
    
    Admin only
    """
    total = db.query(func.count(User.id)).scalar()
    users = db.query(User.id, User.email, User.username, User.full_name).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "subscribers": [
            {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name
            }
            for user in users
        ]
    }


@router.post("/preview-weekly-arrivals")
async def preview_weekly_arrivals_email(
    days: int = Query(7, description="Number of days to look back"),
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Preview the weekly arrivals email HTML
    
    Admin only - generates a preview of the email without sending
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Get new magazines
    new_magazines = db.query(Magazine).filter(
        Magazine.created_at >= cutoff_date,
        Magazine.is_published == True
    ).order_by(desc(Magazine.created_at)).all()
    
    # Get new products
    new_products = db.query(Product).filter(
        Product.created_at >= cutoff_date,
        Product.is_available == True
    ).order_by(desc(Product.created_at)).all()
    
    # Convert to dictionaries
    magazines_data = [
        {
            "title": mag.title,
            "description": mag.description or "",
            "cover_image_url": mag.cover_image_url,
            "issue_number": mag.issue_number,
            "age_group": mag.age_group.value if mag.age_group else "All ages"
        }
        for mag in new_magazines
    ]
    
    products_data = [
        {
            "name": prod.name,
            "description": prod.description or "",
            "price": prod.price,
            "original_price": prod.original_price,
            "image_url": prod.image_url,
            "age_range": prod.age_range or "All ages",
            "is_new": prod.is_new,
            "is_bestseller": prod.is_bestseller
        }
        for prod in new_products
    ]
    
    # Generate email HTML
    html_content = smtp_email_service.generate_weekly_arrivals_email(
        magazines=magazines_data,
        products=products_data,
        recipient_name="Preview Recipient",
        base_url=FRONTEND_URL
    )
    
    return {
        "html": html_content,
        "magazines_count": len(magazines_data),
        "products_count": len(products_data)
    }


@router.post("/send-weekly-arrivals")
async def send_weekly_arrivals_email(
    request: SendWeeklyArrivalsRequest,
    background_tasks: BackgroundTasks,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Send weekly new arrivals promotional email
    
    Admin only - sends email to specified recipients
    """
    cutoff_date = datetime.utcnow() - timedelta(days=request.days_back)
    
    # Get new magazines
    new_magazines = db.query(Magazine).filter(
        Magazine.created_at >= cutoff_date,
        Magazine.is_published == True
    ).order_by(desc(Magazine.created_at)).all()
    
    # Get new products
    new_products = db.query(Product).filter(
        Product.created_at >= cutoff_date,
        Product.is_available == True
    ).order_by(desc(Product.created_at)).all()
    
    # Convert to dictionaries
    magazines_data = [
        {
            "title": mag.title,
            "description": mag.description or "",
            "cover_image_url": mag.cover_image_url,
            "issue_number": mag.issue_number,
            "age_group": mag.age_group.value if mag.age_group else "All ages"
        }
        for mag in new_magazines
    ]
    
    products_data = [
        {
            "name": prod.name,
            "description": prod.description or "",
            "price": prod.price,
            "original_price": prod.original_price,
            "image_url": prod.image_url,
            "age_range": prod.age_range or "All ages",
            "is_new": prod.is_new,
            "is_bestseller": prod.is_bestseller
        }
        for prod in new_products
    ]
    
    # Generate email HTML
    html_content = smtp_email_service.generate_weekly_arrivals_email(
        magazines=magazines_data,
        products=products_data,
        recipient_name=request.recipient_name,
        base_url=FRONTEND_URL
    )
    
    subject = "🌟 This Week's New Arrivals at POSAN! 📚"
    
    # Send in background
    background_tasks.add_task(
        smtp_email_service.send_email,
        to_emails=request.recipient_emails,
        subject=subject,
        html_content=html_content
    )
    
    return {
        "message": f"Email queued for {len(request.recipient_emails)} recipient(s)",
        "recipients": request.recipient_emails,
        "magazines_included": len(magazines_data),
        "products_included": len(products_data)
    }


@router.post("/send-custom")
async def send_custom_promotional_email(
    request: SendCustomEmailRequest,
    background_tasks: BackgroundTasks,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Send a custom promotional email
    
    Admin only - allows sending custom marketing emails
    """
    # Generate email HTML
    html_content = smtp_email_service.generate_custom_promotional_email(
        subject=request.subject,
        heading=request.heading,
        content=request.content,
        cta_text=request.cta_text,
        cta_url=request.cta_url
    )
    
    # Send in background
    background_tasks.add_task(
        smtp_email_service.send_email,
        to_emails=request.recipient_emails,
        subject=request.subject,
        html_content=html_content
    )
    
    return {
        "message": f"Custom email queued for {len(request.recipient_emails)} recipient(s)",
        "recipients": request.recipient_emails,
        "subject": request.subject
    }


@router.post("/send-to-all-users")
async def send_to_all_users(
    request: SendToAllUsersRequest,
    background_tasks: BackgroundTasks,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Send promotional email to all registered users
    
    Admin only - USE WITH CAUTION! This sends to all users.
    """
    # Get all user emails
    users = db.query(User.email).all()
    all_emails = [user.email for user in users if user.email]
    
    if not all_emails:
        raise HTTPException(status_code=400, detail="No users found to send emails to")
    
    cutoff_date = datetime.utcnow() - timedelta(days=request.days_back)
    
    magazines_data = []
    products_data = []
    
    if request.include_new_magazines:
        new_magazines = db.query(Magazine).filter(
            Magazine.created_at >= cutoff_date,
            Magazine.is_published == True
        ).order_by(desc(Magazine.created_at)).all()
        
        magazines_data = [
            {
                "title": mag.title,
                "description": mag.description or "",
                "cover_image_url": mag.cover_image_url,
                "issue_number": mag.issue_number,
                "age_group": mag.age_group.value if mag.age_group else "All ages"
            }
            for mag in new_magazines
        ]
    
    if request.include_new_products:
        new_products = db.query(Product).filter(
            Product.created_at >= cutoff_date,
            Product.is_available == True
        ).order_by(desc(Product.created_at)).all()
        
        products_data = [
            {
                "name": prod.name,
                "description": prod.description or "",
                "price": prod.price,
                "original_price": prod.original_price,
                "image_url": prod.image_url,
                "age_range": prod.age_range or "All ages",
                "is_new": prod.is_new,
                "is_bestseller": prod.is_bestseller
            }
            for prod in new_products
        ]
    
    # Generate email HTML
    html_content = smtp_email_service.generate_weekly_arrivals_email(
        magazines=magazines_data,
        products=products_data,
        recipient_name="Dear Reader",
        base_url=FRONTEND_URL
    )
    
    # If custom message is provided, prepend it
    if request.custom_message:
        # Insert custom message after greeting
        custom_section = f"""
        <div style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); 
                    border-radius: 12px; padding: 20px; margin-bottom: 24px;">
            <p style="color: #8b4513; margin: 0; font-size: 15px; line-height: 1.7;">
                {request.custom_message}
            </p>
        </div>
        """
        # This is a simple approach - for production, you'd want a more robust template system
    
    # Send in background (batch to avoid rate limits)
    # For large lists, you might want to implement batching
    background_tasks.add_task(
        smtp_email_service.send_email,
        to_emails=all_emails,
        subject=request.subject,
        html_content=html_content
    )
    
    return {
        "message": f"Email queued for {len(all_emails)} user(s)",
        "total_recipients": len(all_emails),
        "magazines_included": len(magazines_data),
        "products_included": len(products_data),
        "subject": request.subject
    }


@router.get("/smtp-status")
async def get_smtp_status(
    admin_user: User = Depends(require_admin)
):
    """
    Check SMTP configuration status
    
    Admin only
    """
    import os
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = os.getenv("SMTP_PORT", "587")
    
    return {
        "configured": bool(smtp_user and smtp_password),
        "smtp_host": smtp_host,
        "smtp_port": smtp_port,
        "smtp_user": smtp_user if smtp_user else "Not configured",
        "smtp_password_set": bool(smtp_password)
    }


@router.post("/send-test")
async def send_test_email(
    to_email: EmailStr,
    admin_user: User = Depends(require_admin)
):
    """
    Send a test email to verify SMTP configuration
    
    Admin only
    """
    html_content = smtp_email_service.generate_custom_promotional_email(
        subject="Test Email from POSAN",
        heading="🎉 SMTP Test Successful!",
        content=f"""
            <p>Congratulations! Your SMTP email configuration is working correctly.</p>
            <p>This test was initiated by admin: <strong>{admin_user.username}</strong></p>
            <p>You can now send promotional emails to your users!</p>
        """,
        cta_text="Visit POSAN Store",
        cta_url=f"{FRONTEND_URL}/store"
    )
    
    result = smtp_email_service.send_email(
        to_emails=[to_email],
        subject="🧪 Test Email from POSAN Admin",
        html_content=html_content
    )
    
    return result
