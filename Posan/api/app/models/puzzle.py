from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.user import AgeGroup
import enum


class PuzzleType(enum.Enum):
    """Puzzle type enumeration."""
    WORD_SEARCH = "word_search"
    CROSSWORD = "crossword"
    JIGSAW = "jigsaw"
    SUDOKU = "sudoku"


class DifficultyLevel(enum.Enum):
    """Difficulty level enumeration."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Puzzle(Base):
    """Puzzle model."""
    __tablename__ = "puzzles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    puzzle_type = Column(SQLEnum(PuzzleType), nullable=False)
    difficulty = Column(SQLEnum(DifficultyLevel), default=DifficultyLevel.EASY)
    age_group = Column(SQLEnum(AgeGroup))
    puzzle_data = Column(JSON, nullable=False)  # Stores puzzle configuration
    solution_data = Column(JSON, nullable=False)  # Stores solution
    image_url = Column(String)  # For jigsaw puzzles
    points_reward = Column(Integer, default=50)
    time_limit_seconds = Column(Integer)  # Optional time limit
    is_daily_challenge = Column(Boolean, default=False)
    challenge_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user_progress = relationship("UserPuzzleProgress", back_populates="puzzle")


class UserPuzzleProgress(Base):
    """Track user progress on puzzles."""
    __tablename__ = "user_puzzle_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    puzzle_id = Column(Integer, ForeignKey("puzzles.id"))
    is_completed = Column(Boolean, default=False)
    completion_time_seconds = Column(Integer)
    attempts = Column(Integer, default=0)
    points_earned = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="puzzle_progress")
    puzzle = relationship("Puzzle", back_populates="user_progress")
