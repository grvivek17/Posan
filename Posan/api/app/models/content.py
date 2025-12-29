from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.user import AgeGroup
import enum


class ContentType(enum.Enum):
    """Content type enumeration."""
    STORY = "story"
    ARTICLE = "article"
    COMIC = "comic"
    ACTIVITY = "activity"


class Magazine(Base):
    """Magazine model."""
    __tablename__ = "magazines"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    cover_image_url = Column(String)
    issue_number = Column(Integer)
    publication_date = Column(DateTime(timezone=True))
    age_group = Column(SQLEnum(AgeGroup))
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    articles = relationship("Article", back_populates="magazine")


class Article(Base):
    """Article/Story model within a magazine."""
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    magazine_id = Column(Integer, ForeignKey("magazines.id"))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(SQLEnum(ContentType), default=ContentType.ARTICLE)
    author = Column(String)
    illustration_url = Column(String)
    audio_url = Column(String)  # URL to audio narration
    reading_time_minutes = Column(Integer)
    age_group = Column(SQLEnum(AgeGroup))
    order_in_magazine = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    magazine = relationship("Magazine", back_populates="articles")
    quizzes = relationship("Quiz", back_populates="article")


class Quiz(Base):
    """Interactive quiz embedded in articles."""
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"))
    question = Column(Text, nullable=False)
    options = Column(Text, nullable=False)  # JSON string of options
    correct_answer = Column(String, nullable=False)
    explanation = Column(Text)
    points = Column(Integer, default=10)
    
    # Relationships
    article = relationship("Article", back_populates="quizzes")
