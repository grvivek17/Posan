from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# Badge Schemas
class BadgeBase(BaseModel):
    """Base badge schema."""
    name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    points_required: int = 0
    puzzles_required: int = 0
    is_special: bool = False


class BadgeCreate(BadgeBase):
    """Schema for creating a badge."""
    pass


class BadgeResponse(BadgeBase):
    """Schema for badge response."""
    id: int
    created_at: datetime
    
    model_config = {"from_attributes": True}


# User Achievement Schemas
class UserAchievementResponse(BaseModel):
    """Schema for user achievement response."""
    id: int
    user_id: int
    badge_id: int
    earned_at: datetime
    badge: BadgeResponse
    
    model_config = {"from_attributes": True}


# Leaderboard Schemas
class LeaderboardEntry(BaseModel):
    """Schema for leaderboard entry."""
    user_id: int
    username: str
    total_points: int
    puzzles_completed: int
    badges_earned: int
    rank: int


class LeaderboardResponse(BaseModel):
    """Schema for leaderboard response."""
    entries: List[LeaderboardEntry]
    user_rank: Optional[int] = None
    total_users: int


# Gamification Stats
class UserStats(BaseModel):
    """Schema for user gamification statistics."""
    total_points: int
    puzzles_completed: int
    badges_earned: int
    current_rank: Optional[int]
    recent_achievements: List[UserAchievementResponse]
