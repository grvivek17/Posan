"""
Gamification Service
Handles point awards, level calculations, and badge management.
"""
from sqlalchemy.orm import Session
from app.models.activity import UserActivity, UserLevel, ActivityType, ACTIVITY_POINTS, LEVEL_THRESHOLDS
from app.models.user import ChildProfile
from app.models.gamification import Badge, UserAchievement
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class GamificationService:
    """Service for managing gamification features."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def award_points(
        self,
        user_id: int,
        activity_type: ActivityType,
        reference_id: Optional[int] = None,
        reference_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Award points to a user for completing an activity.
        
        Args:
            user_id: The user's ID
            activity_type: Type of activity completed
            reference_id: Optional ID of the related entity (puzzle, article, etc.)
            reference_type: Optional type of the reference
            
        Returns:
            Dictionary with points awarded, new total, level info, and any new badges
        """
        # Get points for this activity
        points = ACTIVITY_POINTS.get(activity_type, 0)
        
        # Check for duplicate activities (prevent gaming the system)
        if reference_id and reference_type:
            existing = self.db.query(UserActivity).filter(
                UserActivity.user_id == user_id,
                UserActivity.activity_type == activity_type,
                UserActivity.reference_id == reference_id,
                UserActivity.reference_type == reference_type
            ).first()
            
            if existing:
                return {
                    "points_awarded": 0,
                    "message": "Points already awarded for this activity",
                    "duplicate": True
                }
        
        # Record the activity
        activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type,
            points_earned=points,
            reference_id=reference_id,
            reference_type=reference_type
        )
        self.db.add(activity)
        
        # Update user's total points
        child_profile = self.db.query(ChildProfile).filter(
            ChildProfile.user_id == user_id
        ).first()
        
        if not child_profile:
            self.db.rollback()
            return {
                "error": "Child profile not found",
                "points_awarded": 0
            }
        
        old_points = child_profile.total_points
        child_profile.total_points += points
        new_points = child_profile.total_points
        
        # Update level
        level_info = self.update_user_level(user_id, new_points)
        
        # Check for new badges
        new_badges = self.check_and_award_badges(user_id)
        
        self.db.commit()
        
        return {
            "points_awarded": points,
            "old_total": old_points,
            "new_total": new_points,
            "level": level_info,
            "new_badges": new_badges,
            "activity_type": activity_type.value,
            "duplicate": False
        }
    
    def update_user_level(self, user_id: int, total_points: int) -> Dict[str, Any]:
        """
        Update user's level based on total points.
        
        Args:
            user_id: The user's ID
            total_points: User's total points
            
        Returns:
            Dictionary with level information
        """
        # Determine current level
        current_level_data = None
        next_level_data = None
        level_number = 0
        
        for idx, level in enumerate(LEVEL_THRESHOLDS):
            if level["min_points"] <= total_points <= level["max_points"]:
                current_level_data = level
                level_number = idx + 1
                if idx + 1 < len(LEVEL_THRESHOLDS):
                    next_level_data = LEVEL_THRESHOLDS[idx + 1]
                break
        
        if not current_level_data:
            current_level_data = LEVEL_THRESHOLDS[-1]  # Max level
            level_number = len(LEVEL_THRESHOLDS)
        
        # Calculate points to next level
        if next_level_data:
            points_to_next = next_level_data["min_points"] - total_points
        else:
            points_to_next = 0  # Already at max level
        
        # Update or create user level record
        user_level = self.db.query(UserLevel).filter(
            UserLevel.user_id == user_id
        ).first()
        
        level_up = False
        if user_level:
            if user_level.current_level != current_level_data["name"]:
                level_up = True
            user_level.current_level = current_level_data["name"]
            user_level.level_number = level_number
            user_level.points_to_next_level = points_to_next
        else:
            user_level = UserLevel(
                user_id=user_id,
                current_level=current_level_data["name"],
                level_number=level_number,
                points_to_next_level=points_to_next
            )
            self.db.add(user_level)
        
        return {
            "current_level": current_level_data["name"],
            "level_number": level_number,
            "level_icon": current_level_data["icon"],
            "points_to_next_level": points_to_next,
            "next_level": next_level_data["name"] if next_level_data else None,
            "level_up": level_up,
            "progress_percentage": self._calculate_level_progress(total_points, current_level_data, next_level_data)
        }
    
    def _calculate_level_progress(self, total_points: int, current_level: Dict, next_level: Optional[Dict]) -> int:
        """Calculate percentage progress to next level."""
        if not next_level:
            return 100  # Max level reached
        
        level_range = next_level["min_points"] - current_level["min_points"]
        points_in_level = total_points - current_level["min_points"]
        
        if level_range == 0:
            return 100
        
        return int((points_in_level / level_range) * 100)
    
    def check_and_award_badges(self, user_id: int) -> list:
        """
        Check if user qualifies for any new badges and award them.
        
        Args:
            user_id: The user's ID
            
        Returns:
            List of newly awarded badges
        """
        child_profile = self.db.query(ChildProfile).filter(
            ChildProfile.user_id == user_id
        ).first()
        
        if not child_profile:
            return []
        
        # Get user's current badges
        earned_badge_ids = [
            ua.badge_id for ua in self.db.query(UserAchievement).filter(
                UserAchievement.user_id == user_id
            ).all()
        ]
        
        # Get activity counts
        puzzles_completed = self.db.query(UserActivity).filter(
            UserActivity.user_id == user_id,
            UserActivity.activity_type == ActivityType.PUZZLE_SOLVED
        ).count()
        
        articles_read = self.db.query(UserActivity).filter(
            UserActivity.user_id == user_id,
            UserActivity.activity_type == ActivityType.ARTICLE_READ
        ).count()
        
        # Check all badges
        badges = self.db.query(Badge).all()
        new_badges = []
        
        for badge in badges:
            if badge.id in earned_badge_ids:
                continue
            
            # Check if user qualifies
            if (child_profile.total_points >= badge.points_required and
                puzzles_completed >= badge.puzzles_required):
                # Award badge
                achievement = UserAchievement(user_id=user_id, badge_id=badge.id)
                self.db.add(achievement)
                new_badges.append({
                    "id": badge.id,
                    "name": badge.name,
                    "description": badge.description,
                    "icon_url": badge.icon_url
                })
        
        return new_badges
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get comprehensive user statistics.
        
        Args:
            user_id: The user's ID
            
        Returns:
            Dictionary with all user stats
        """
        child_profile = self.db.query(ChildProfile).filter(
            ChildProfile.user_id == user_id
        ).first()
        
        if not child_profile:
            return {"error": "Child profile not found"}
        
        # Get level info
        level_info = self.update_user_level(user_id, child_profile.total_points)
        
        # Get activity counts
        activity_counts = {}
        for activity_type in ActivityType:
            count = self.db.query(UserActivity).filter(
                UserActivity.user_id == user_id,
                UserActivity.activity_type == activity_type
            ).count()
            activity_counts[activity_type.value] = count
        
        # Get badges
        badges_earned = self.db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id
        ).count()
        
        # Get recent activities
        recent_activities = self.db.query(UserActivity).filter(
            UserActivity.user_id == user_id
        ).order_by(UserActivity.created_at.desc()).limit(10).all()
        
        return {
            "total_points": child_profile.total_points,
            "level": level_info,
            "activity_counts": activity_counts,
            "badges_earned": badges_earned,
            "recent_activities": [
                {
                    "activity_type": a.activity_type.value,
                    "points_earned": a.points_earned,
                    "created_at": a.created_at.isoformat()
                }
                for a in recent_activities
            ]
        }
    
    def get_daily_streak(self, user_id: int) -> int:
        """Calculate user's daily login streak."""
        activities = self.db.query(UserActivity).filter(
            UserActivity.user_id == user_id,
            UserActivity.activity_type == ActivityType.DAILY_LOGIN
        ).order_by(UserActivity.created_at.desc()).all()
        
        if not activities:
            return 0
        
        streak = 1
        current_date = activities[0].created_at.date()
        
        for activity in activities[1:]:
            activity_date = activity.created_at.date()
            if (current_date - activity_date).days == 1:
                streak += 1
                current_date = activity_date
            else:
                break
        
        return streak
