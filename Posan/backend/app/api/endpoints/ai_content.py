"""
AI Content Generation API Endpoints.
Provides endpoints for generating kid-friendly content using Hugging Face models.
"""
from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional, List
import tempfile
import os
from pathlib import Path
from app.services.ai_content import (
    content_generator,
    generate_story,
    generate_article,
    generate_quiz,
    generate_word_search,
    generate_crossword
)
from app.services.ocr_service import ocr_service

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


class TestAnalysisRequest(BaseModel):
    subject: str = Field(..., description="Subject of the test")
    score: int = Field(..., ge=0, description="Score achieved")
    total: int = Field(..., gt=0, description="Total possible score")
    weak_areas: Optional[List[str]] = Field(default=None, description="Areas where student struggled")
    strong_areas: Optional[List[str]] = Field(default=None, description="Areas where student excelled")
    age_group: str = Field(default="6-8", description="Student age group")
    student_name: str = Field(default="Student", description="Student name")


class TestAnalysisResponse(BaseModel):
    subject: str
    score: int
    total: int
    percentage: float
    performance_level: str
    analysis: str
    motivational_quote: str
    weak_areas: List[str]
    strong_areas: List[str]


@router.post("/analyze/test", response_model=TestAnalysisResponse, summary="Analyze test results and get AI recommendations")
async def api_analyze_test(request: TestAnalysisRequest):
    """
    Analyze student test results and provide personalized AI-powered recommendations.
    
    - **subject**: Subject of the test (Math, Science, English, etc.)
    - **score**: Score achieved by the student
    - **total**: Total possible score
    - **weak_areas**: Optional list of topics where student struggled
    - **strong_areas**: Optional list of topics where student excelled
    - **age_group**: Student's age group for age-appropriate feedback
    - **student_name**: Student's name for personalized feedback
    
    Returns detailed analysis, strengths, areas for growth, recommendations, and motivational quote.
    """
    try:
        test_scores = {
            "score": request.score,
            "total": request.total,
            "weak_areas": request.weak_areas or [],
            "strong_areas": request.strong_areas or []
        }
        
        result = content_generator.analyze_test_results(
            subject=request.subject,
            test_scores=test_scores,
            age_group=request.age_group,
            student_name=request.student_name
        )
        
        return TestAnalysisResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing test: {str(e)}")


@router.post("/analyze/test-upload", summary="Upload and analyze test paper with OCR")
async def api_analyze_test_upload(
    file: UploadFile = File(..., description="Test paper image or PDF"),
    student_name: str = Query(..., description="Student's name"),
    subject: str = Query(..., description="Subject of the test"),
    age_group: str = Query(default="6-8", description="Student age group")
):
    """
    Upload a test paper (image or PDF) and analyze it using OCR + AI.
    
    This endpoint:
    1. Accepts JPG, PNG, or PDF files
    2. Uses Tesseract OCR to extract text from the test paper
    3. Parses the text to identify scores and marks
    4. Sends the results to AI for personalized analysis
    
    - **file**: Test paper file (JPG, PNG, PDF, max 10MB)
    - **student_name**: Student's name for personalized feedback
    - **subject**: Subject of the test
    - **age_group**: Student age group for age-appropriate analysis
    
    Returns OCR extraction results and AI-powered recommendations.
    """
    # Validate file type
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB in bytes
    
    # Save uploaded file temporarily
    temp_file = None
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=file_extension
        ) as temp_file:
            # Read and save file content
            content = await file.read()
            
            if len(content) > max_size:
                raise HTTPException(
                    status_code=400,
                    detail="File size exceeds 10MB limit"
                )
            
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Process with OCR service
        ocr_result = ocr_service.analyze_test_paper(
            file_path=temp_file_path,
            file_extension=file_extension,
            student_name=student_name,
            subject=subject
        )
        
        if not ocr_result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"OCR processing failed: {ocr_result.get('error', 'Unknown error')}"
            )
        
        # Get question-answer pairs for content analysis
        question_answers = ocr_result.get("question_answers", [])
        extracted_text = ocr_result.get("extracted_text", "")
        
        # Use new content-based analysis if we have question-answer pairs
        if question_answers and len(question_answers) > 0:
            # Perform deep content analysis based on actual answers
            ai_result = content_generator.analyze_test_paper_content(
                subject=subject,
                question_answers=question_answers,
                extracted_text=extracted_text,
                age_group=age_group,
                student_name=student_name
            )
            
            # Combine OCR and AI results
            return {
                "ocr_success": True,
                "analysis_type": "content_based",
                "message": f"Analyzed {len(question_answers)} questions with detailed answer evaluation",
                "ocr_confidence": ocr_result.get("confidence", "medium"),
                "extracted_text_preview": extracted_text[:200] if extracted_text else "",
                **ai_result
            }
        
        # Fallback: If no questions extracted but score found, use score-based analysis
        elif ocr_result.get("score") is not None:
            score = ocr_result.get("score")
            total = ocr_result.get("total", 100)
            
            test_scores = {
                "score": score,
                "total": total,
                "weak_areas": [],
                "strong_areas": []
            }
            
            # Get AI analysis based on score only
            ai_result = content_generator.analyze_test_results(
                subject=subject,
                test_scores=test_scores,
                age_group=age_group,
                student_name=student_name
            )
            
            # Combine OCR and AI results
            return {
                "ocr_success": True,
                "analysis_type": "score_based",
                "message": "Score detected. For better analysis, ensure questions and answers are clearly visible.",
                "ocr_confidence": ocr_result.get("confidence", "medium"),
                "extracted_text_preview": extracted_text[:200] if extracted_text else "",
                **ai_result
            }
        
        # No score or questions found
        else:
            return {
                "ocr_success": True,
                "score_detected": False,
                "analysis_type": "none",
                "message": "Could not extract questions/answers or score from test paper. The text was extracted but needs manual review. Please ensure the test paper is clear and properly formatted.",
                "extracted_text_preview": extracted_text[:500] if extracted_text else "",
                "confidence": ocr_result.get("confidence", "low"),
                "questions_found": 0,
                "correct_count": ocr_result.get("correct_count", 0),
                "incorrect_count": ocr_result.get("incorrect_count", 0),
                "suggested_subject": ocr_result.get("subject", subject)
            }
        
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing test paper: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                # Log but don't fail if cleanup fails
                print(f"Warning: Could not delete temp file: {e}")



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


# ============= STUDY MATERIAL ANALYSIS ENDPOINTS =============

class StudyMaterialResponse(BaseModel):
    summary: str
    key_topics: List[str]
    age_group: str
    original_length: int


class PracticeQuestionsResponse(BaseModel):
    mcqs: List[dict]
    short_answers: List[dict]
    total_questions: int


class AnswerEvaluationRequest(BaseModel):
    question: str
    student_answer: str
    expected_answer: str


class AnswerEvaluationResponse(BaseModel):
    question: str
    score: int
    is_correct: str
    feedback: str


class StudyPlanRequest(BaseModel):
    topics: List[str]
    weak_areas: List[str] = []
    days: int = 7
    age_group: str = "9-11"


@router.post("/study-material/upload", summary="Upload PDF study material for analysis")
async def upload_study_material(
    file: UploadFile = File(..., description="PDF study material"),
    age_group: str = Query(default="9-11", description="Student age group")
):
    """
    Upload a PDF study material for AI-powered analysis.
    
    This endpoint:
    1. Extracts text from the PDF
    2. Summarizes the content into a study plan
    3. Identifies key topics and vocabulary
    4. Returns a structured learning guide
    
    - **file**: PDF file (max 10MB)
    - **age_group**: Student's age group for appropriate content
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted for study material"
        )
    
    temp_file_path = None
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            if len(content) > 10 * 1024 * 1024:  # 10MB limit
                raise HTTPException(status_code=400, detail="File too large (max 10MB)")
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Extract text using OCR service
        extracted_text = ocr_service.extract_text_from_pdf(temp_file_path)
        
        text_len = len(extracted_text.strip()) if extracted_text else 0
        print(f"📄 PDF Extraction Result: {text_len} characters found")

        if not extracted_text or text_len < 10:
            raise HTTPException(
                status_code=400,
                detail=f"Could not extract enough text from PDF (only {text_len} chars found). Please ensure the PDF contains readable text or high-quality images."
            )
        
        # Summarize and analyze
        result = content_generator.summarize_study_material(extracted_text, age_group)
        
        return {
            "success": True,
            "filename": file.filename,
            "characters_extracted": len(extracted_text),
            **result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@router.post("/study-material/generate-questions", summary="Generate practice questions from text")
async def generate_practice_questions(
    text: str = Query(..., description="Study material text (or summary)"),
    num_mcq: int = Query(default=5, ge=1, le=10),
    num_short: int = Query(default=3, ge=1, le=5),
    age_group: str = Query(default="9-11")
):
    """
    Generate practice questions from study material.
    
    - **text**: The study material text to generate questions from
    - **num_mcq**: Number of multiple choice questions (1-10)
    - **num_short**: Number of short answer questions (1-5)
    - **age_group**: Student's age group
    
    Returns MCQs with options and correct answers, plus short answer questions.
    """
    try:
        if len(text) < 100:
            raise HTTPException(
                status_code=400,
                detail="Text too short. Need at least 100 characters."
            )
        
        result = content_generator.generate_practice_questions(
            text=text,
            num_mcq=num_mcq,
            num_short=num_short,
            age_group=age_group
        )
        
        return {"success": True, **result}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating questions: {str(e)}")


@router.post("/study-material/evaluate-answer", summary="Evaluate a student's answer")
async def evaluate_student_answer(request: AnswerEvaluationRequest):
    """
    Evaluate a student's answer using AI.
    
    - **question**: The question asked
    - **student_answer**: Student's submitted answer
    - **expected_answer**: The correct/expected answer
    
    Returns score (0-100), correctness, and constructive feedback.
    """
    try:
        result = content_generator.evaluate_answer(
            question=request.question,
            student_answer=request.student_answer,
            expected_answer=request.expected_answer
        )
        
        return {"success": True, **result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating answer: {str(e)}")


@router.post("/study-material/analyze-performance", summary="Analyze weak topics from answers")
async def analyze_performance(answers: List[AnswerEvaluationRequest]):
    """
    Analyze a batch of student answers to identify weak topics.
    
    - **answers**: List of evaluated answers with scores
    
    Returns weak topics, strengths, and personalized recommendations.
    """
    try:
        # First evaluate all answers
        evaluated = []
        for answer in answers:
            result = content_generator.evaluate_answer(
                question=answer.question,
                student_answer=answer.student_answer,
                expected_answer=answer.expected_answer
            )
            evaluated.append(result)
        
        # Analyze weak topics
        analysis = content_generator.analyze_weak_topics(evaluated)
        
        return {
            "success": True,
            "individual_results": evaluated,
            **analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing performance: {str(e)}")


@router.post("/study-material/generate-plan", summary="Generate personalized study plan")
async def generate_study_plan(request: StudyPlanRequest):
    """
    Generate a personalized study plan based on topics and weak areas.
    
    - **topics**: All topics from study material
    - **weak_areas**: Topics the student struggles with
    - **days**: Number of days to plan (1-14)
    - **age_group**: Student's age group
    
    Returns a day-by-day study schedule with activities.
    """
    try:
        result = content_generator.generate_study_plan(
            topics=request.topics,
            weak_areas=request.weak_areas,
            days=request.days,
            age_group=request.age_group
        )
        
        return {"success": True, **result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating study plan: {str(e)}")

