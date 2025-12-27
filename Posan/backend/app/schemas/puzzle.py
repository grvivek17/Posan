from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.puzzle import PuzzleType, DifficultyLevel
from app.models.user import AgeGroup


# Puzzle Schemas
class PuzzleBase(BaseModel):
    """Base puzzle schema."""
    title: str
    description: Optional[str] = None
    puzzle_type: PuzzleType
    difficulty: DifficultyLevel = DifficultyLevel.EASY
    age_group: AgeGroup
    points_reward: int = 50
    time_limit_seconds: Optional[int] = None


class PuzzleCreate(PuzzleBase):
    """Schema for creating a puzzle."""
    puzzle_data: Dict[str, Any]
    solution_data: Dict[str, Any]
    image_url: Optional[str] = None
    is_daily_challenge: bool = False
    challenge_date: Optional[datetime] = None


class PuzzleResponse(PuzzleBase):
    """Schema for puzzle response."""
    id: int
    puzzle_data: Dict[str, Any]
    image_url: Optional[str]
    is_daily_challenge: bool
    challenge_date: Optional[datetime]
    created_at: datetime
    
    model_config = {"from_attributes": True}


class PuzzleSubmission(BaseModel):
    """Schema for submitting puzzle solution."""
    puzzle_id: int
    user_solution: Dict[str, Any]
    completion_time_seconds: Optional[int] = None


class PuzzleResult(BaseModel):
    """Schema for puzzle validation result."""
    is_correct: bool
    points_earned: int
    completion_time_seconds: Optional[int]
    message: str


# User Puzzle Progress Schemas
class UserPuzzleProgressResponse(BaseModel):
    """Schema for user puzzle progress response."""
    id: int
    user_id: int
    puzzle_id: int
    is_completed: bool
    completion_time_seconds: Optional[int]
    attempts: int
    points_earned: int
    started_at: datetime
    completed_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


class PuzzleStats(BaseModel):
    """Schema for puzzle statistics."""
    total_puzzles: int
    completed_puzzles: int
    total_points: int
    average_completion_time: Optional[float]
    by_type: Dict[str, int]
