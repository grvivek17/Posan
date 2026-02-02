from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date
from sqlalchemy.sql import func
from app.core.database import Base


class DailyPuzzleGeneration(Base):
    """Track daily puzzle generation per user to limit abuse"""
    __tablename__ = "daily_puzzle_generations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    generation_date = Column(Date, nullable=False, server_default=func.current_date())
    puzzle_type = Column(String, nullable=False)  # word_search, crossword, etc.
    topic = Column(String)
    difficulty = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Index for quick lookups
    __table_args__ = (
        # Ensure we can quickly query user's generations for a specific date
        {'mysql_engine': 'InnoDB'}
    )
