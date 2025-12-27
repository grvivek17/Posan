from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Badge(Base):
    """Badge/Achievement definition."""
    __tablename__ = "badges"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    icon_url = Column(String)
    points_required = Column(Integer, default=0)
    puzzles_required = Column(Integer, default=0)
    is_special = Column(Boolean, default=False)  # Special event badges
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user_achievements = relationship("UserAchievement", back_populates="badge")


class UserAchievement(Base):
    """Track user achievements and badges."""
    __tablename__ = "user_achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    badge_id = Column(Integer, ForeignKey("badges.id"))
    earned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="achievements")
    badge = relationship("Badge", back_populates="user_achievements")


class Leaderboard(Base):
    """Leaderboard entries for competitive ranking."""
    __tablename__ = "leaderboard"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_points = Column(Integer, default=0)
    puzzles_completed = Column(Integer, default=0)
    badges_earned = Column(Integer, default=0)
    rank = Column(Integer)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
