"""
Enhanced Gamification API Endpoints
Handles points, levels, badges, and activity tracking.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.services.gamification_service import GamificationService
from app.models.activity import ActivityType, ACTIVITY_POINTS, LEVEL_THRESHOLDS
from app.models.user import User

router = APIRouter()


# Request/Response Schemas
class AwardPointsRequest(BaseModel):
    """Request schema for awarding points."""
    activity_type: str
    reference_id: Optional[int] = None
    reference_type: Optional[str] = None


class AwardPointsResponse(BaseModel):
    """Response schema for point awards."""
    points_awarded: int
    old_total: int
    new_total: int
    level: dict
    new_badges: List[dict]
    activity_type: str
    duplicate: bool
    message: Optional[str] = None


class UserStatsResponse(BaseModel):
    """Response schema for user stats."""
    total_points: int
    level: dict
    activity_counts: dict
    badges_earned: int
    recent_activities: List[dict]


class LevelInfoResponse(BaseModel):
    """Response schema for level information."""
    current_level: str
    level_number: int
    level_icon: str
    points_to_next_level: int
    next_level: Optional[str]
    progress_percentage: int


class ActivityPointsResponse(BaseModel):
    """Response schema for activity points configuration."""
    activity_type: str
    points: int
    description: str


# Activity descriptions
ACTIVITY_DESCRIPTIONS = {
    "puzzle_solved": "Complete a puzzle",
    "article_read": "Read an article",
    "comment_posted": "Post a comment",
    "content_shared": "Share content",
    "quiz_completed": "Complete a quiz",
    "daily_login": "Daily login bonus",
    "profile_completed": "Complete your profile",
    "homework_uploaded": "Upload homework",
    "study_plan_created": "Create a study plan",
}


@router.post("/award-points", response_model=AwardPointsResponse)
async def award_points(
    request: AwardPointsRequest,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Award points to a user for completing an activity.
    """
    try:
        # Convert string to ActivityType enum
        activity_type = ActivityType(request.activity_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid activity type: {request.activity_type}"
        )
    
    service = GamificationService(db)
    result = service.award_points(
        user_id=user_id,
        activity_type=activity_type,
        reference_id=request.reference_id,
        reference_type=request.reference_type
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"]
        )
    
    return result


@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive statistics for a user.
    """
    service = GamificationService(db)
    stats = service.get_user_stats(user_id)
    
    if "error" in stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=stats["error"]
        )
    
    return stats


@router.get("/stats/{user_id}", response_model=UserStatsResponse)
async def get_user_stats_by_id(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive statistics for a specific user (public view).
    """
    service = GamificationService(db)
    stats = service.get_user_stats(user_id)
    
    if "error" in stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=stats["error"]
        )
    
    return stats


@router.get("/level", response_model=LevelInfoResponse)
async def get_user_level(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get current level information for a user.
    """
    from app.models.user import ChildProfile
    
    child_profile = db.query(ChildProfile).filter(
        ChildProfile.user_id == user_id
    ).first()
    
    if not child_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found"
        )
    
    service = GamificationService(db)
    level_info = service.update_user_level(user_id, child_profile.total_points)
    
    return level_info


@router.get("/activity-points", response_model=List[ActivityPointsResponse])
async def get_activity_points():
    """
    Get the points configuration for all activity types.
    """
    return [
        ActivityPointsResponse(
            activity_type=activity_type.value,
            points=points,
            description=ACTIVITY_DESCRIPTIONS.get(activity_type.value, "")
        )
        for activity_type, points in ACTIVITY_POINTS.items()
    ]


@router.get("/levels", response_model=List[dict])
async def get_all_levels():
    """
    Get information about all available levels.
    """
    return LEVEL_THRESHOLDS


@router.get("/streak")
async def get_daily_streak(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the user's daily login streak.
    """
    service = GamificationService(db)
    streak = service.get_daily_streak(user_id)
    
    return {
        "user_id": user_id,
        "streak": streak,
        "message": f"You're on a {streak}-day streak!" if streak > 0 else "Start your streak today!"
    }


@router.post("/daily-login")
async def record_daily_login(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Record a daily login and award points if it's the first login today.
    """
    from app.models.activity import UserActivity
    from datetime import date
    
    # Check if user already logged in today
    today = date.today()
    existing_login = db.query(UserActivity).filter(
        UserActivity.user_id == user_id,
        UserActivity.activity_type == ActivityType.DAILY_LOGIN,
        func.date(UserActivity.created_at) == today
    ).first()
    
    if existing_login:
        return {
            "message": "Daily login already recorded",
            "points_awarded": 0
        }
    
    # Award points for daily login
    service = GamificationService(db)
    result = service.award_points(
        user_id=user_id,
        activity_type=ActivityType.DAILY_LOGIN
    )
    
    # Get updated streak
    streak = service.get_daily_streak(user_id)
    result["streak"] = streak
    
    return result
