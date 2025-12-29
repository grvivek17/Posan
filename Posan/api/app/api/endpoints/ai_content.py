"""
AI Content Generation API Endpoints.
Provides endpoints for generating kid-friendly content using Hugging Face models.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from app.services.ai_content import (
    content_generator,
    generate_story,
    generate_article,
    generate_quiz,
    generate_word_search,
    generate_crossword
)

router = APIRouter()


# Request/Response Schemas
class StoryRequest(BaseModel):
    topic: str = Field(..., description="Main theme of the story")
    age_group: str = Field(default="6-8", description="Target age group: 3-5, 6-8, 9-11, 12-14")
    word_count: int = Field(default=300, ge=100, le=1000)
    characters: Optional[List[str]] = Field(default=None, description="Character names")


class StoryResponse(BaseModel):
    title: str
    content: str
    topic: str
    age_group: str
    word_count: int


class ArticleRequest(BaseModel):
    topic: str = Field(..., description="Subject of the article")
    age_group: str = Field(default="6-8")
    article_type: str = Field(default="educational", description="educational, fun_facts, how_to, science")


class ArticleResponse(BaseModel):
    title: str
    content: str
    topic: str
    age_group: str
    article_type: str


class QuizRequest(BaseModel):
    topic: str = Field(..., description="Subject of the quiz")
    num_questions: int = Field(default=5, ge=1, le=10)
    age_group: str = Field(default="6-8")


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None


class WordSearchRequest(BaseModel):
    topic: str = Field(..., description="Theme for word search")
    num_words: int = Field(default=10, ge=5, le=20)
    age_group: str = Field(default="6-8")


class CrosswordRequest(BaseModel):
    topic: str = Field(..., description="Theme for crossword")
    num_clues: int = Field(default=8, ge=4, le=15)
    age_group: str = Field(default="6-8")


class CrosswordClue(BaseModel):
    clue: str
    answer: str


class RiddleResponse(BaseModel):
    riddle: str
    answer: str


# API Endpoints
@router.post("/generate/story", response_model=StoryResponse, summary="Generate a kid-friendly story")
async def api_generate_story(request: StoryRequest):
    """
    Generate a kid-friendly story using AI.
    
    - **topic**: Main theme (e.g., "space adventure", "friendship", "animals")
    - **age_group**: Target age (3-5, 6-8, 9-11, 12-14)
    - **word_count**: Approximate story length
    - **characters**: Optional character names to include
    """
    try:
        result = generate_story(
            topic=request.topic,
            age_group=request.age_group,
            word_count=request.word_count,
            characters=request.characters
        )
        return StoryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating story: {str(e)}")


@router.post("/generate/article", response_model=ArticleResponse, summary="Generate an educational article")
async def api_generate_article(request: ArticleRequest):
    """
    Generate an educational article for kids.
    
    - **topic**: Subject matter (e.g., "dinosaurs", "the ocean", "planets")
    - **age_group**: Target age group
    - **article_type**: Type of content (educational, fun_facts, how_to, science)
    """
    try:
        result = generate_article(
            topic=request.topic,
            age_group=request.age_group,
            article_type=request.article_type
        )
        return ArticleResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating article: {str(e)}")


@router.post("/generate/quiz", response_model=List[QuizQuestion], summary="Generate quiz questions")
async def api_generate_quiz(request: QuizRequest):
    """
    Generate multiple-choice quiz questions for kids.
    
    - **topic**: Subject of the quiz
    - **num_questions**: How many questions (1-10)
    - **age_group**: Target age group
    """
    try:
        questions = generate_quiz(
            topic=request.topic,
            num_questions=request.num_questions,
            age_group=request.age_group
        )
        return [QuizQuestion(**q) for q in questions if q.get("question")]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(e)}")


@router.post("/generate/word-search", summary="Generate word search words")
async def api_generate_word_search(request: WordSearchRequest):
    """
    Generate words for a word search puzzle.
    
    - **topic**: Theme for the puzzle (e.g., "animals", "food", "sports")
    - **num_words**: Number of words to find (5-20)
    - **age_group**: Target age group
    """
    try:
        words = generate_word_search(
            topic=request.topic,
            num_words=request.num_words,
            age_group=request.age_group
        )
        return {"topic": request.topic, "words": words, "age_group": request.age_group}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating word search: {str(e)}")


@router.post("/generate/crossword", response_model=List[CrosswordClue], summary="Generate crossword clues")
async def api_generate_crossword(request: CrosswordRequest):
    """
    Generate crossword clues and answers.
    
    - **topic**: Theme for the crossword
    - **num_clues**: Number of clues (4-15)
    - **age_group**: Target age group
    """
    try:
        clues = generate_crossword(
            topic=request.topic,
            num_clues=request.num_clues,
            age_group=request.age_group
        )
        return [CrosswordClue(**c) for c in clues if c.get("clue") and c.get("answer")]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating crossword: {str(e)}")


@router.get("/generate/fun-fact", summary="Generate a fun fact")
async def api_generate_fun_fact(
    topic: str = Query(..., description="Subject for the fun fact"),
    age_group: str = Query(default="6-8", description="Target age group")
):
    """Generate an amazing fun fact for kids."""
    try:
        fact = content_generator.generate_fun_fact(topic, age_group)
        return {"topic": topic, "fun_fact": fact, "age_group": age_group}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating fun fact: {str(e)}")


@router.get("/generate/riddle", response_model=RiddleResponse, summary="Generate a riddle")
async def api_generate_riddle(
    topic: str = Query(..., description="Subject for the riddle"),
    age_group: str = Query(default="6-8", description="Target age group")
):
    """Generate a fun riddle for kids."""
    try:
        riddle = content_generator.generate_riddle(topic, age_group)
        return RiddleResponse(**riddle)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating riddle: {str(e)}")


@router.get("/topics/suggestions", summary="Get suggested content topics")
async def get_topic_suggestions(age_group: str = Query(default="6-8")):
    """Get suggested topics for content generation based on age group."""
    topics = {
        "3-5": {
            "stories": ["farm animals", "colors", "shapes", "family", "seasons"],
            "articles": ["baby animals", "rainbows", "the moon", "butterflies"],
            "puzzles": ["animals", "fruits", "toys", "vehicles"]
        },
        "6-8": {
            "stories": ["space adventure", "underwater kingdom", "dinosaurs", "friendship", "magic forest"],
            "articles": ["solar system", "ocean creatures", "how airplanes fly", "volcanoes"],
            "puzzles": ["animals", "sports", "food", "nature", "countries"]
        },
        "9-11": {
            "stories": ["time travel", "mystery detective", "superhero origin", "fantasy quest"],
            "articles": ["ancient civilizations", "human body", "weather patterns", "inventions"],
            "puzzles": ["science", "geography", "history", "technology"]
        },
        "12-14": {
            "stories": ["dystopian adventure", "coming of age", "historical fiction", "sci-fi"],
            "articles": ["space exploration", "climate change", "coding", "psychology"],
            "puzzles": ["vocabulary", "world capitals", "science terms", "literature"]
        }
    }
    
    return topics.get(age_group, topics["6-8"])
