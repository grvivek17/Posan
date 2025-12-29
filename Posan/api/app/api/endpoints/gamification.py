from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from app.core.database import get_db
from app.models.gamification import Badge, UserAchievement, Leaderboard
from app.models.user import User, ChildProfile
from app.models.puzzle import UserPuzzleProgress
from app.schemas.gamification import (
    BadgeCreate,
    BadgeResponse,
    UserAchievementResponse,
    LeaderboardResponse,
    LeaderboardEntry,
    UserStats
)

router = APIRouter()


def check_and_award_badges(user_id: int, db: Session):
    """Check if user qualifies for any new badges and award them."""
    child_profile = db.query(ChildProfile).filter(ChildProfile.user_id == user_id).first()
    if not child_profile:
        return
    
    # Get user's current badges
    earned_badge_ids = [ua.badge_id for ua in db.query(UserAchievement).filter(
        UserAchievement.user_id == user_id
    ).all()]
    
    # Get puzzles completed count
    puzzles_completed = db.query(UserPuzzleProgress).filter(
        UserPuzzleProgress.user_id == user_id,
        UserPuzzleProgress.is_completed == True
    ).count()
    
    # Check all badges
    badges = db.query(Badge).all()
    for badge in badges:
        if badge.id in earned_badge_ids:
            continue
        
        # Check if user qualifies
        if (child_profile.total_points >= badge.points_required and
            puzzles_completed >= badge.puzzles_required):
            # Award badge
            achievement = UserAchievement(user_id=user_id, badge_id=badge.id)
            db.add(achievement)
    
    db.commit()


@router.post("/badges", response_model=BadgeResponse, status_code=status.HTTP_201_CREATED)
def create_badge(badge_data: BadgeCreate, db: Session = Depends(get_db)):
    """Create a new badge (admin only)."""
    badge = Badge(**badge_data.model_dump())
    db.add(badge)
    db.commit()
    db.refresh(badge)
    return badge


@router.get("/badges", response_model=List[BadgeResponse])
def get_badges(db: Session = Depends(get_db)):
    """Get all available badges."""
    badges = db.query(Badge).all()
    return badges


@router.get("/achievements/{user_id}", response_model=List[UserAchievementResponse])
def get_user_achievements(user_id: int, db: Session = Depends(get_db)):
    """Get user's earned achievements."""
    achievements = db.query(UserAchievement).filter(
        UserAchievement.user_id == user_id
    ).all()
    return achievements


@router.get("/leaderboard", response_model=LeaderboardResponse)
def get_leaderboard(
    limit: int = 100,
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """Get global leaderboard."""
    # Update leaderboard entries
    update_leaderboard(db)
    
    # Get top entries
    entries = db.query(Leaderboard).order_by(desc(Leaderboard.total_points)).limit(limit).all()
    
    # Convert to response format
    leaderboard_entries = []
    for entry in entries:
        user = db.query(User).filter(User.id == entry.user_id).first()
        if user:
            leaderboard_entries.append(LeaderboardEntry(
                user_id=entry.user_id,
                username=user.username,
                total_points=entry.total_points,
                puzzles_completed=entry.puzzles_completed,
                badges_earned=entry.badges_earned,
                rank=entry.rank
            ))
    
    # Get user's rank if user_id provided
    user_rank = None
    if user_id:
        user_entry = db.query(Leaderboard).filter(Leaderboard.user_id == user_id).first()
        if user_entry:
            user_rank = user_entry.rank
    
    return LeaderboardResponse(
        entries=leaderboard_entries,
        user_rank=user_rank,
        total_users=len(leaderboard_entries)
    )


@router.get("/stats/{user_id}", response_model=UserStats)
def get_user_stats(user_id: int, db: Session = Depends(get_db)):
    """Get comprehensive user statistics."""
    # Check for new badges
    check_and_award_badges(user_id, db)
    
    # Get child profile
    child_profile = db.query(ChildProfile).filter(ChildProfile.user_id == user_id).first()
    if not child_profile:
        raise HTTPException(status_code=404, detail="Child profile not found")
    
    # Get puzzles completed
    puzzles_completed = db.query(UserPuzzleProgress).filter(
        UserPuzzleProgress.user_id == user_id,
        UserPuzzleProgress.is_completed == True
    ).count()
    
    # Get badges earned
    badges_earned = db.query(UserAchievement).filter(
        UserAchievement.user_id == user_id
    ).count()
    
    # Get current rank
    leaderboard_entry = db.query(Leaderboard).filter(Leaderboard.user_id == user_id).first()
    current_rank = leaderboard_entry.rank if leaderboard_entry else None
    
    # Get recent achievements (last 5)
    recent_achievements = db.query(UserAchievement).filter(
        UserAchievement.user_id == user_id
    ).order_by(desc(UserAchievement.earned_at)).limit(5).all()
    
    return UserStats(
        total_points=child_profile.total_points,
        puzzles_completed=puzzles_completed,
        badges_earned=badges_earned,
        current_rank=current_rank,
        recent_achievements=recent_achievements
    )


def update_leaderboard(db: Session):
    """Update leaderboard rankings."""
    # Get all child profiles with their stats
    children = db.query(ChildProfile).all()
    
    for child in children:
        # Get puzzles completed
        puzzles_completed = db.query(UserPuzzleProgress).filter(
            UserPuzzleProgress.user_id == child.user_id,
            UserPuzzleProgress.is_completed == True
        ).count()
        
        # Get badges earned
        badges_earned = db.query(UserAchievement).filter(
            UserAchievement.user_id == child.user_id
        ).count()
        
        # Update or create leaderboard entry
        entry = db.query(Leaderboard).filter(Leaderboard.user_id == child.user_id).first()
        if entry:
            entry.total_points = child.total_points
            entry.puzzles_completed = puzzles_completed
            entry.badges_earned = badges_earned
        else:
            entry = Leaderboard(
                user_id=child.user_id,
                total_points=child.total_points,
                puzzles_completed=puzzles_completed,
                badges_earned=badges_earned
            )
            db.add(entry)
    
    db.commit()
    
    # Update ranks
    entries = db.query(Leaderboard).order_by(desc(Leaderboard.total_points)).all()
    for idx, entry in enumerate(entries, start=1):
        entry.rank = idx
    
    db.commit()
