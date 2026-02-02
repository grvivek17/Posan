"""
Admin API endpoints for user management and monitoring
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.subscription import Subscription, SubscriptionTier, SubscriptionStatus
from app.models.puzzle_generation import DailyPuzzleGeneration

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(current_user: User = Depends(get_current_user)):
    """Dependency to check if user is admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/users")
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    search: Optional[str] = None,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get all users with pagination and search
    
    Admin only - requires is_admin = True
    """
    query = db.query(User)
    
    # Search filter
    if search:
        query = query.filter(
            (User.username.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%"))
        )
    
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "is_admin": user.is_admin,
                "created_at": user.created_at,
                "last_login": user.last_login
            }
            for user in users
        ]
    }


@router.get("/users/{user_id}")
async def get_user_details(
    user_id: int,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific user"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get subscription
    subscription = db.query(Subscription).filter(
        Subscription.user_id == user_id
    ).first()
    
    # Get puzzle generation stats
    puzzle_stats = db.query(
        func.count(DailyPuzzleGeneration.id).label('total'),
        func.count(func.distinct(DailyPuzzleGeneration.generation_date)).label('unique_days')
    ).filter(
        DailyPuzzleGeneration.user_id == user_id
    ).first()
    
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_admin": user.is_admin,
            "created_at": user.created_at,
            "last_login": user.last_login
        },
        "subscription": {
            "tier": subscription.tier.value if subscription else "free",
            "status": subscription.status.value if subscription else "active",
            "is_active": subscription.is_active() if subscription else False,
            "expires_at": subscription.expires_at if subscription else None,
            "payment_provider": subscription.payment_provider if subscription else None,
            "created_at": subscription.created_at if subscription else None
        } if subscription else None,
        "activity": {
            "total_puzzle_generations": puzzle_stats.total if puzzle_stats else 0,
            "active_days": puzzle_stats.unique_days if puzzle_stats else 0
        }
    }


@router.get("/subscriptions")
async def get_all_subscriptions(
    tier: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all subscriptions with filters"""
    query = db.query(Subscription).join(User)
    
    # Filters
    if tier:
        query = query.filter(Subscription.tier == SubscriptionTier(tier))
    if status:
        query = query.filter(Subscription.status == SubscriptionStatus(status))
    
    total = query.count()
    subscriptions = query.order_by(desc(Subscription.created_at)).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "subscriptions": [
            {
                "id": sub.id,
                "user_id": sub.user_id,
                "username": sub.user.username,
                "email": sub.user.email,
                "tier": sub.tier.value,
                "status": sub.status.value,
                "is_active": sub.is_active(),
                "created_at": sub.created_at,
                "expires_at": sub.expires_at,
                "payment_provider": sub.payment_provider,
                "payment_id": sub.payment_id
            }
            for sub in subscriptions
        ]
    }


@router.get("/stats/overview")
async def get_overview_stats(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get overview statistics for admin dashboard"""
    
    # Total users
    total_users = db.query(func.count(User.id)).scalar()
    
    # Users by subscription tier
    tier_stats = db.query(
        Subscription.tier,
        func.count(Subscription.id)
    ).group_by(Subscription.tier).all()
    
    # Active subscriptions (Pro + Premium + Active)
    active_subs = db.query(func.count(Subscription.id)).filter(
        Subscription.tier.in_([SubscriptionTier.PRO, SubscriptionTier.PREMIUM]),
        Subscription.status == SubscriptionStatus.ACTIVE
    ).scalar()
    
    # Revenue (mock calculation - you'd pull from payment provider)
    pro_count = db.query(func.count(Subscription.id)).filter(
        Subscription.tier == SubscriptionTier.PRO,
        Subscription.status == SubscriptionStatus.ACTIVE
    ).scalar() or 0
    
    premium_count = db.query(func.count(Subscription.id)).filter(
        Subscription.tier == SubscriptionTier.PREMIUM,
        Subscription.status == SubscriptionStatus.ACTIVE
    ).scalar() or 0
    
    estimated_mrr = (pro_count * 99) + (premium_count * 83.25)  # ₹999/year = ₹83.25/month
    
    # Recent signups (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_signups = db.query(func.count(User.id)).filter(
        User.created_at >= seven_days_ago
    ).scalar()
    
    # Puzzle generation stats
    total_puzzles = db.query(func.count(DailyPuzzleGeneration.id)).scalar()
    today_puzzles = db.query(func.count(DailyPuzzleGeneration.id)).filter(
        func.date(DailyPuzzleGeneration.created_at) == func.current_date()
    ).scalar()
    
    return {
        "users": {
            "total": total_users,
            "recent_signups": recent_signups,
            "growth_rate": "+12%"  # Mock data - calculate from real data
        },
        "subscriptions": {
            "total_active": active_subs,
            "pro": pro_count,
            "premium": premium_count,
            "free": total_users - active_subs
        },
        "revenue": {
            "mrr": round(estimated_mrr, 2),
            "currency": "INR"
        },
        "activity": {
            "total_puzzles_generated": total_puzzles,
            "puzzles_today": today_puzzles
        }
    }


@router.get("/activity/recent")
async def get_recent_activity(
    limit: int = Query(50, le=100),
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get recent user activity (puzzle generations, subscriptions)"""
    
    # Recent puzzle generations
    recent = recent_puzzles = db.query(DailyPuzzleGeneration).join(User).order_by(
        desc(DailyPuzzleGeneration.created_at)
    ).limit(limit).all()
    
    return {
        "recent_activity": [
            {
                "id": gen.id,
                "user_id": gen.user_id,
                "username": gen.user.username,
                "activity_type": "puzzle_generation",
                "puzzle_type": gen.puzzle_type,
                "topic": gen.topic,
                "difficulty": gen.difficulty,
                "timestamp": gen.created_at
            }
            for gen in recent_puzzles
        ]
    }


@router.post("/users/{user_id}/upgrade")
async def admin_upgrade_user(
    user_id: int,
    tier: str,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin can manually upgrade any user"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get or create subscription
    subscription = db.query(Subscription).filter(
        Subscription.user_id == user_id
    ).first()
    
    if not subscription:
        subscription = Subscription(user_id=user_id)
        db.add(subscription)
    
    # Upgrade based on tier
    if tier.lower() == "pro":
        subscription.upgrade_to_pro()
        subscription.expires_at = datetime.utcnow() + timedelta(days=30)
    elif tier.lower() == "premium":
        subscription.upgrade_to_premium()
        subscription.expires_at = datetime.utcnow() + timedelta(days=365)
    else:
        raise HTTPException(status_code=400, detail="Invalid tier")
    
    subscription.payment_provider = "admin_manual"
    subscription.payment_id = f"admin_{admin_user.id}_{datetime.utcnow().timestamp()}"
    
    db.commit()
    db.refresh(subscription)
    
    return {
        "message": f"User {user.username} upgraded to {tier}",
        "subscription": {
            "tier": subscription.tier.value,
            "expires_at": subscription.expires_at
        }
    }


@router.delete("/users/{user_id}")
async def admin_delete_user(
    user_id: int,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin can delete a user (use with caution!)"""
    if user_id == admin_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete related records
    db.query(Subscription).filter(Subscription.user_id == user_id).delete()
    db.query(DailyPuzzleGeneration).filter(DailyPuzzleGeneration.user_id == user_id).delete()
    
    # Delete user
    db.delete(user)
    db.commit()
    
    return {"message": f"User {user.username} deleted successfully"}


@router.put("/users/{user_id}")
async def admin_update_user(
    user_id: int,
    user_data: dict,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin can update user attributes (username, email, full_name, is_admin)"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update allowed fields
    allowed_fields = ['username', 'email', 'full_name', 'is_admin']
    
    for field in allowed_fields:
        if field in user_data and user_data[field] is not None:
            # Check for unique username/email if being changed
            if field == 'username' and user_data[field] != user.username:
                existing = db.query(User).filter(User.username == user_data[field]).first()
                if existing:
                    raise HTTPException(status_code=400, detail="Username already taken")
            if field == 'email' and user_data[field] != user.email:
                existing = db.query(User).filter(User.email == user_data[field]).first()
                if existing:
                    raise HTTPException(status_code=400, detail="Email already taken")
            
            setattr(user, field, user_data[field])
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": f"User {user.username} updated successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_admin": user.is_admin
        }
    }


@router.post("/users/{user_id}/reset-password")
async def admin_reset_password(
    user_id: int,
    password_data: dict,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin can reset a user's password"""
    from app.core.security import get_password_hash
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_password = password_data.get('new_password')
    if not new_password or len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    # Hash and update password
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    return {"message": f"Password reset successfully for {user.username}"}
