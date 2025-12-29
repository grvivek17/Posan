from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.content import Magazine, Article, Quiz
from app.models.user import AgeGroup
from app.schemas.content import (
    MagazineCreate,
    MagazineResponse,
    ArticleCreate,
    ArticleResponse,
    QuizCreate,
    QuizResponse,
    QuizAnswer,
    QuizResult
)

router = APIRouter()


@router.post("/magazines", response_model=MagazineResponse, status_code=status.HTTP_201_CREATED)
def create_magazine(magazine_data: MagazineCreate, db: Session = Depends(get_db)):
    """Create a new magazine."""
    magazine = Magazine(**magazine_data.model_dump())
    db.add(magazine)
    db.commit()
    db.refresh(magazine)
    return magazine


@router.get("/magazines", response_model=List[MagazineResponse])
def get_magazines(
    age_group: Optional[AgeGroup] = None,
    published_only: bool = True,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get list of magazines with optional filtering."""
    query = db.query(Magazine)
    
    if published_only:
        query = query.filter(Magazine.is_published == True)
    
    if age_group:
        query = query.filter(Magazine.age_group == age_group)
    
    magazines = query.offset(skip).limit(limit).all()
    return magazines


@router.get("/magazines/{magazine_id}", response_model=MagazineResponse)
def get_magazine(magazine_id: int, db: Session = Depends(get_db)):
    """Get a specific magazine by ID."""
    magazine = db.query(Magazine).filter(Magazine.id == magazine_id).first()
    if not magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")
    return magazine


@router.post("/articles", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
def create_article(article_data: ArticleCreate, db: Session = Depends(get_db)):
    """Create a new article."""
    # Verify magazine exists
    magazine = db.query(Magazine).filter(Magazine.id == article_data.magazine_id).first()
    if not magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")
    
    article = Article(**article_data.model_dump())
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


@router.get("/articles", response_model=List[ArticleResponse])
def get_articles(
    magazine_id: Optional[int] = None,
    age_group: Optional[AgeGroup] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get list of articles with optional filtering."""
    query = db.query(Article)
    
    if magazine_id:
        query = query.filter(Article.magazine_id == magazine_id)
    
    if age_group:
        query = query.filter(Article.age_group == age_group)
    
    articles = query.order_by(Article.order_in_magazine).offset(skip).limit(limit).all()
    return articles


@router.get("/articles/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)):
    """Get a specific article by ID."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.post("/quizzes", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
def create_quiz(quiz_data: QuizCreate, db: Session = Depends(get_db)):
    """Create a new quiz."""
    # Verify article exists
    article = db.query(Article).filter(Article.id == quiz_data.article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    quiz = Quiz(**quiz_data.model_dump())
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz


@router.post("/quizzes/submit", response_model=QuizResult)
def submit_quiz_answer(answer: QuizAnswer, user_id: int, db: Session = Depends(get_db)):
    """Submit and validate a quiz answer."""
    quiz = db.query(Quiz).filter(Quiz.id == answer.quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    is_correct = answer.answer.strip().lower() == quiz.correct_answer.strip().lower()
    points_earned = quiz.points if is_correct else 0
    
    # Update user points if correct
    if is_correct:
        from app.models.user import ChildProfile
        child_profile = db.query(ChildProfile).filter(ChildProfile.user_id == user_id).first()
        if child_profile:
            child_profile.total_points += points_earned
            db.commit()
    
    return QuizResult(
        is_correct=is_correct,
        points_earned=points_earned,
        explanation=quiz.explanation if not is_correct else None
    )
