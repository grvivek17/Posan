from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRole(enum.Enum):
    """User role enumeration."""
    PARENT = "parent"
    CHILD = "child"
    ADMIN = "admin"


class User(Base):
    """User model for authentication."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    keycloak_id = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.CHILD)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    parent_account = relationship("ParentAccount", back_populates="user", uselist=False)
    child_profile = relationship("ChildProfile", back_populates="user", uselist=False)
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    puzzle_progress = relationship("UserPuzzleProgress", back_populates="user")
    achievements = relationship("UserAchievement", back_populates="user")


class ParentAccount(Base):
    """Parent account with additional information."""
    __tablename__ = "parent_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    full_name = Column(String, nullable=False)
    phone = Column(String)
    
    # Relationships
    user = relationship("User", back_populates="parent_account")
    children = relationship("ChildProfile", back_populates="parent")


class AgeGroup(enum.Enum):
    """Age group enumeration for content filtering."""
    TODDLER = "3-5"      # 3-5 years
    EARLY = "6-8"        # 6-8 years
    MIDDLE = "9-11"      # 9-11 years
    PRETEEN = "12-14"    # 12-14 years


class ChildProfile(Base):
    """Child profile linked to parent account."""
    __tablename__ = "child_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    parent_id = Column(Integer, ForeignKey("parent_accounts.id"))
    full_name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    age_group = Column(SQLEnum(AgeGroup))
    avatar_url = Column(String)
    total_points = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="child_profile")
    parent = relationship("ParentAccount", back_populates="children")
