from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


def generate_uuid():
    """Generate UUID as string"""
    return str(uuid.uuid4())


class StudyPlan(Base):
    """Tracks a high-level goal or exam study schedule"""
    __tablename__ = "study_plans"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    subject = Column(String)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    total_sessions = Column(Integer, default=0)
    completed_sessions = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sessions = relationship("StudySession", back_populates="plan", cascade="all, delete-orphan")


class StudySession(Base):
    """Granular study blocks belonging to a StudyPlan"""
    __tablename__ = "study_sessions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    plan_id = Column(String, ForeignKey("study_plans.id", ondelete="CASCADE"), nullable=False)
    date = Column(DateTime, nullable=False)
    topic = Column(String, nullable=False)
    duration_minutes = Column(Integer, default=30)
    is_completed = Column(Boolean, default=False)
    points_earned = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    plan = relationship("StudyPlan", back_populates="sessions")


class GamificationProfile(Base):
    """Tracks a user's overarching stats (streaks, points)"""
    __tablename__ = "gamification_profiles"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, unique=True, index=True)
    current_streak = Column(Integer, default=0)
    max_streak = Column(Integer, default=0)
    total_points = Column(Integer, default=0)
    last_activity_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
