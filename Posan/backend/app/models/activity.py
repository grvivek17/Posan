from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ActivityType(enum.Enum):
    """Types of activities that earn points."""
    PUZZLE_SOLVED = "puzzle_solved"
    ARTICLE_READ = "article_read"
    COMMENT_POSTED = "comment_posted"
    CONTENT_SHARED = "content_shared"
    QUIZ_COMPLETED = "quiz_completed"
    DAILY_LOGIN = "daily_login"
    PROFILE_COMPLETED = "profile_completed"
    HOMEWORK_UPLOADED = "homework_uploaded"
    STUDY_PLAN_CREATED = "study_plan_created"


# Point values for each activity type
ACTIVITY_POINTS = {
    ActivityType.PUZZLE_SOLVED: 10,
    ActivityType.ARTICLE_READ: 5,
    ActivityType.COMMENT_POSTED: 2,
    ActivityType.CONTENT_SHARED: 3,
    ActivityType.QUIZ_COMPLETED: 15,
    ActivityType.DAILY_LOGIN: 1,
    ActivityType.PROFILE_COMPLETED: 20,
    ActivityType.HOMEWORK_UPLOADED: 8,
    ActivityType.STUDY_PLAN_CREATED: 12,
}


class UserActivity(Base):
    """Track user activities for points and analytics."""
    __tablename__ = "user_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_type = Column(SQLEnum(ActivityType), nullable=False)
    points_earned = Column(Integer, default=0)
    reference_id = Column(Integer)  # ID of puzzle, article, etc.
    reference_type = Column(String)  # Type of reference (puzzle, article, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="activities")


class UserLevel(Base):
    """User level/tier based on total points."""
    __tablename__ = "user_levels"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    current_level = Column(String, default="Bronze")  # Bronze, Silver, Gold, Platinum, Diamond
    level_number = Column(Integer, default=1)
    points_to_next_level = Column(Integer, default=100)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="level")


# Level thresholds
LEVEL_THRESHOLDS = [
    {"name": "Bronze", "min_points": 0, "max_points": 99, "icon": "🥉"},
    {"name": "Silver", "min_points": 100, "max_points": 299, "icon": "🥈"},
    {"name": "Gold", "min_points": 300, "max_points": 599, "icon": "🥇"},
    {"name": "Platinum", "min_points": 600, "max_points": 999, "icon": "💎"},
    {"name": "Diamond", "min_points": 1000, "max_points": 1999, "icon": "💠"},
    {"name": "Master", "min_points": 2000, "max_points": float('inf'), "icon": "👑"},
]
