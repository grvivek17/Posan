"""Models package initialization."""
from app.models.user import User, ParentAccount, ChildProfile, UserRole, AgeGroup
from app.models.content import Magazine, Article, Quiz, ContentType
from app.models.puzzle import Puzzle, UserPuzzleProgress, PuzzleType, DifficultyLevel
from app.models.gamification import Badge, UserAchievement, Leaderboard
from app.models.activity import UserActivity, UserLevel, ActivityType, ACTIVITY_POINTS

__all__ = [
    "User",
    "ParentAccount",
    "ChildProfile",
    "UserRole",
    "AgeGroup",
    "Magazine",
    "Article",
    "Quiz",
    "ContentType",
    "Puzzle",
    "UserPuzzleProgress",
    "PuzzleType",
    "DifficultyLevel",
    "Badge",
    "UserAchievement",
    "Leaderboard",
    "UserActivity",
    "UserLevel",
    "ActivityType",
    "ACTIVITY_POINTS",
]
