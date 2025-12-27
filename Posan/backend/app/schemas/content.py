from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.content import ContentType
from app.models.user import AgeGroup


# Magazine Schemas
class MagazineBase(BaseModel):
    """Base magazine schema."""
    title: str
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    issue_number: Optional[int] = None
    age_group: AgeGroup


class MagazineCreate(MagazineBase):
    """Schema for creating a magazine."""
    publication_date: Optional[datetime] = None


class MagazineResponse(MagazineBase):
    """Schema for magazine response."""
    id: int
    publication_date: Optional[datetime]
    is_published: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}


# Article Schemas
class ArticleBase(BaseModel):
    """Base article schema."""
    title: str
    content: str
    content_type: ContentType = ContentType.ARTICLE
    author: Optional[str] = None
    illustration_url: Optional[str] = None
    audio_url: Optional[str] = None
    reading_time_minutes: Optional[int] = None
    age_group: AgeGroup


class ArticleCreate(ArticleBase):
    """Schema for creating an article."""
    magazine_id: int
    order_in_magazine: int = 0


class ArticleResponse(ArticleBase):
    """Schema for article response."""
    id: int
    magazine_id: int
    order_in_magazine: int
    created_at: datetime
    
    model_config = {"from_attributes": True}


# Quiz Schemas
class QuizBase(BaseModel):
    """Base quiz schema."""
    question: str
    options: str  # JSON string
    correct_answer: str
    explanation: Optional[str] = None
    points: int = 10


class QuizCreate(QuizBase):
    """Schema for creating a quiz."""
    article_id: int


class QuizResponse(QuizBase):
    """Schema for quiz response."""
    id: int
    article_id: int
    
    model_config = {"from_attributes": True}


class QuizAnswer(BaseModel):
    """Schema for submitting quiz answer."""
    quiz_id: int
    answer: str


class QuizResult(BaseModel):
    """Schema for quiz result."""
    is_correct: bool
    points_earned: int
    explanation: Optional[str] = None
