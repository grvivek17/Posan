"""
Subscription API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.subscription import Subscription, SubscriptionTier, SubscriptionStatus
from app.services.payment_service import razorpay_service

router = APIRouter(prefix="/subscription", tags=["subscription"])


class SubscriptionResponse(BaseModel):
    """Subscription status response"""
    tier: str
    status: str
    is_active: bool
    features: dict
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UpgradeRequest(BaseModel):
    """Request to upgrade subscription"""
    tier: str
    payment_provider: Optional[str] = None
    payment_id: Optional[str] = None


@router.get("/status", response_model=SubscriptionResponse)
async def get_subscription_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's subscription status
    """
    # Get or create subscription
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        # Create free tier subscription for new users
        subscription = Subscription(
            user_id=current_user.id,
            tier=SubscriptionTier.FREE,
            status=SubscriptionStatus.ACTIVE
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
    
    return SubscriptionResponse(
        tier=subscription.tier.value,
        status=subscription.status.value,
        is_active=subscription.is_active(),
        features={
            "ai_image_generation": subscription.ai_image_generation,
            "advanced_puzzles": subscription.advanced_puzzles,
            "unlimited_content": subscription.unlimited_content,
            "no_ads": subscription.no_ads
        },
        expires_at=subscription.expires_at
    )


@router.post("/upgrade")
async def upgrade_subscription(
    request: UpgradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upgrade user subscription to Pro or Premium
    
    In production, this would integrate with payment providers (Stripe, Razorpay, etc.)
    For now, we'll allow direct upgrades for testing
    """
    # Get or create subscription
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        subscription = Subscription(user_id=current_user.id)
        db.add(subscription)
    
    # Update subscription based on tier
    if request.tier.lower() == "pro":
        subscription.upgrade_to_pro()
        subscription.expires_at = datetime.utcnow() + timedelta(days=30)  # 30-day subscription
    elif request.tier.lower() == "premium":
        subscription.upgrade_to_premium()
        subscription.expires_at = datetime.utcnow() + timedelta(days=365)  # 1-year subscription
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subscription tier"
        )
    
    # Store payment info if provided
    if request.payment_provider:
        subscription.payment_provider = request.payment_provider
    if request.payment_id:
        subscription.payment_id = request.payment_id
    
    db.commit()
    db.refresh(subscription)
    
    return {
        "message": f"Successfully upgraded to {request.tier}",
        "tier": subscription.tier.value,
        "expires_at": subscription.expires_at
    }


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel user subscription"""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    subscription.status = SubscriptionStatus.CANCELLED
    subscription.cancelled_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Subscription cancelled successfully"}


@router.get("/features/{feature}")
async def check_feature_access(
    feature: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if user has access to a specific feature
    """
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        return {"has_access": False, "tier": "free"}
    
    has_access = subscription.has_feature(feature)
    
    return {
        "has_access": has_access,
        "tier": subscription.tier.value,
        "active": subscription.is_active()
    }


@router.get("/plans")
async def get_subscription_plans():
    """
    Get available subscription plans
    """
    return {
        "plans": [
            {
                "tier": "free",
                "price": 0,
                "currency": "USD",
                "features": {
                    "ai_image_generation": False,
                    "advanced_puzzles": False,
                    "unlimited_content": False,
                    "no_ads": False
                },
                "limits": {
                    "daily_content": 5,
                    "puzzles_per_day": 10
                }
            },
            {
                "tier": "pro",
                "price": 99,
                "currency": "INR",
                "billing": "monthly",
                "features": {
                    "ai_image_generation": True,
                    "advanced_puzzles": True,
                    "unlimited_content": True,
                    "no_ads": True
                },
                "limits": {
                    "daily_content": -1,  # unlimited
                    "puzzles_per_day": -1  # unlimited
                }
            },
            {
                "tier": "premium",
                "price": 999,
                "currency": "INR",
                "billing": "yearly",
                "features": {
                    "ai_image_generation": True,
                    "advanced_puzzles": True,
                    "unlimited_content": True,
                    "no_ads": True
                },
                "limits": {
                    "daily_content": -1,
                    "puzzles_per_day": -1
                },
                "savings": "Save 92% vs monthly (₹99 x 12 = ₹1188)"
            }
        ]
    }


# Razorpay Payment Integration

class RazorpayOrderRequest(BaseModel):
    """Request to create Razorpay order"""
    tier: str


class RazorpayVerifyRequest(BaseModel):
    """Request to verify Razorpay payment"""
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    tier: str


@router.post("/razorpay/create-order")
async def create_razorpay_order(
    request: RazorpayOrderRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create a Razorpay order for subscription
    """
    try:
        order = razorpay_service.create_subscription_order(
            tier=request.tier,
            user_id=current_user.id,
            user_email=current_user.email
        )
        
        return {
            "success": True,
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "key_id": razorpay_service.client.auth[0] if razorpay_service.client else None
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}"
        )


@router.post("/razorpay/verify-payment")
async def verify_razorpay_payment(
    request: RazorpayVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify Razorpay payment and activate subscription
    """
    try:
        # Verify payment signature
        is_valid = razorpay_service.verify_payment(
            razorpay_order_id=request.razorpay_order_id,
            razorpay_payment_id=request.razorpay_payment_id,
            razorpay_signature=request.razorpay_signature
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payment signature"
            )
        
        # Get payment details
        payment_details = razorpay_service.get_payment_details(request.razorpay_payment_id)
        
        # Update subscription
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).first()
        
        if not subscription:
            subscription = Subscription(user_id=current_user.id)
            db.add(subscription)
        
        # Activate based on tier
        if request.tier.lower() == "pro":
            subscription.upgrade_to_pro()
            subscription.expires_at = datetime.utcnow() + timedelta(days=30)
        elif request.tier.lower() == "premium":
            subscription.upgrade_to_premium()
            subscription.expires_at = datetime.utcnow() + timedelta(days=365)
        
        # Store payment info
        subscription.payment_provider = "razorpay"
        subscription.payment_id = request.razorpay_payment_id
        
        db.commit()
        db.refresh(subscription)
        
        return {
            "success": True,
            "message": f"Successfully upgraded to {request.tier}",
            "tier": subscription.tier.value,
            "expires_at": subscription.expires_at,
            "payment_id": request.razorpay_payment_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment verification failed: {str(e)}"
        )
