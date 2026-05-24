from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.models.content import Magazine, Article, Quiz, ContentType
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


@router.get("/magazines/current-month", response_model=List[MagazineResponse])
def get_current_month_magazines(db: Session = Depends(get_db)):
    """Get magazines published in the current month."""
    now = datetime.now()
    magazines = db.query(Magazine).filter(
        Magazine.is_published == True,
        extract("month", Magazine.publication_date) == now.month,
        extract("year", Magazine.publication_date) == now.year
    ).all()
    return magazines


@router.post("/magazines/refresh-monthly")
def refresh_monthly_magazines(
    force: bool = Query(False, description="Force refresh: delete existing magazines for this month and regenerate"),
    db: Session = Depends(get_db),
):
    """
    Generate and load fresh magazines for the current month.
    Fetches content from educational RSS feeds and web sources,
    then creates kid-friendly magazines with articles.

    - By default, skips if magazines already exist for the current month.
    - Pass ?force=true to delete existing magazines and regenerate with fresh content.
    """
    now = datetime.now()
    month_name = now.strftime("%B")
    year = now.year

    # Check if magazines already exist for this month
    existing_magazines = db.query(Magazine).filter(
        extract("month", Magazine.publication_date) == now.month,
        extract("year", Magazine.publication_date) == now.year
    ).all()

    if existing_magazines and not force:
        return {
            "status": "skipped",
            "message": f"Magazines for {month_name} {year} already exist ({len(existing_magazines)} found). Use ?force=true to regenerate.",
            "count": len(existing_magazines),
        }

    # If force refresh, delete existing magazines and their articles for this month
    if existing_magazines and force:
        for mag in existing_magazines:
            # Delete articles belonging to this magazine (and their quizzes)
            articles = db.query(Article).filter(Article.magazine_id == mag.id).all()
            for art in articles:
                db.query(Quiz).filter(Quiz.article_id == art.id).delete()
                db.delete(art)
            db.delete(mag)
        db.flush()
        print(f"[INFO] Force refresh: deleted {len(existing_magazines)} old magazines for {month_name} {year}")

    # Try to initialize the AI content generator (optional)
    ai_generator = None
    try:
        from app.services.ai_content import ContentGenerator
        ai_generator = ContentGenerator()
    except Exception as e:
        print(f"[WARN] AI generator not available: {e}. Using fallback content.")

    # Initialize the fetcher
    from app.services.magazine_fetcher import MagazineFetcher
    fetcher = MagazineFetcher(ai_generator=ai_generator)

    # Try web fetching first, fall back to curated content
    try:
        magazines_data = fetcher.generate_monthly_magazines()
    except Exception as e:
        print(f"[WARN] Web fetching failed: {e}. Using fallback content.")
        magazines_data = fetcher.generate_fallback_magazines()

    # If web fetching returned empty results, use fallback
    if not magazines_data:
        magazines_data = fetcher.generate_fallback_magazines()

    # Insert into database
    created_magazines = []
    for mag_data in magazines_data:
        # Map age_group string to AgeGroup enum
        age_str = mag_data["magazine"]["age_group"]
        age_group_map = {"3-5": AgeGroup.TODDLER, "6-8": AgeGroup.EARLY, "9-11": AgeGroup.MIDDLE, "12-14": AgeGroup.PRETEEN}
        age_group_enum = age_group_map.get(age_str, AgeGroup.EARLY)

        magazine = Magazine(
            title=mag_data["magazine"]["title"],
            description=mag_data["magazine"]["description"],
            age_group=age_group_enum,
            issue_number=mag_data["magazine"]["issue_number"],
            cover_image_url=mag_data["magazine"]["cover_image_url"],
            is_published=mag_data["magazine"]["is_published"],
            publication_date=mag_data["magazine"]["publication_date"],
        )
        db.add(magazine)
        db.flush()

        for article_data in mag_data["articles"]:
            art_age = age_group_map.get(article_data["age_group"], AgeGroup.EARLY)
            content_type_map = {"article": ContentType.ARTICLE, "story": ContentType.STORY, "activity": ContentType.ACTIVITY, "comic": ContentType.COMIC}
            content_type = content_type_map.get(article_data.get("content_type", "article"), ContentType.ARTICLE)

            article = Article(
                magazine_id=magazine.id,
                title=article_data["title"],
                content=article_data["content"],
                content_type=content_type,
                author=article_data.get("author", "Poshan Team"),
                reading_time_minutes=article_data.get("reading_time_minutes", 5),
                age_group=art_age,
                order_in_magazine=article_data.get("order_in_magazine", 1),
            )
            db.add(article)

        created_magazines.append({
            "title": magazine.title,
            "age_group": age_str,
            "articles_count": len(mag_data["articles"]),
        })

    db.commit()

    return {
        "status": "success",
        "message": f"Created {len(created_magazines)} magazines for {month_name} {year}",
        "month": month_name,
        "year": year,
        "magazines": created_magazines,
    }


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
