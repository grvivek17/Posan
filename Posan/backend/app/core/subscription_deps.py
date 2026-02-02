"""
Dependency for checking Pro subscription access
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.subscription import Subscription, SubscriptionTier


def require_pro_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dependency that requires user to have Pro or Premium subscription.
    
    Raises HTTPException if user doesn't have Pro/Premium subscription.
    """
    # Get user's subscription
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    # Check if subscription exists and is Pro or Premium
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Pro subscription required for AI Study Tools",
                "feature": "ai_study_tools",
                "current_tier": "free",
                "required_tier": "pro",
                "upgrade_url": "/subscription/upgrade"
            }
        )
    
    if subscription.tier not in [SubscriptionTier.PRO, SubscriptionTier.PREMIUM]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Pro subscription required for AI Study Tools",
                "feature": "ai_study_tools",
                "current_tier": subscription.tier.value,
                "required_tier": "pro",
                "upgrade_url": "/subscription/upgrade"
            }
        )
    
    # Check if subscription is active
    if not subscription.is_active():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Your Pro subscription has expired. Please renew to access AI Study Tools.",
                "feature": "ai_study_tools",
                "current_tier": subscription.tier.value,
                "is_expired": True,
                "upgrade_url": "/subscription/upgrade"
            }
        )
    
    return current_user
