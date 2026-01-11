from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.core.database import get_db
from app.models.puzzle import Puzzle, UserPuzzleProgress, PuzzleType, DifficultyLevel
from app.models.user import AgeGroup, ChildProfile
from app.schemas.puzzle import (
    PuzzleCreate,
    PuzzleResponse,
    PuzzleSubmission,
    PuzzleResult,
    UserPuzzleProgressResponse,
    PuzzleStats
)

router = APIRouter()


def validate_puzzle_solution(puzzle: Puzzle, user_solution: dict) -> bool:
    """Validate user's puzzle solution against the correct solution."""
    solution = puzzle.solution_data
    
    if puzzle.puzzle_type == PuzzleType.WORD_SEARCH:
        # Check if all words are found
        return set(user_solution.get("found_words", [])) == set(solution.get("words", []))
    
    elif puzzle.puzzle_type == PuzzleType.CROSSWORD:
        # Check if all answers match
        user_answers = user_solution.get("answers", {})
        correct_answers = solution.get("answers", {})
        return user_answers == correct_answers
    
    elif puzzle.puzzle_type == PuzzleType.JIGSAW:
        # Check if puzzle is completed (all pieces in correct positions)
        return user_solution.get("completed", False)
    
    elif puzzle.puzzle_type == PuzzleType.SUDOKU:
        # Check if grid matches solution
        user_grid = user_solution.get("grid", [])
        correct_grid = solution.get("grid", [])
        return user_grid == correct_grid
    
    return False


@router.post("/puzzles", response_model=PuzzleResponse, status_code=status.HTTP_201_CREATED)
def create_puzzle(puzzle_data: PuzzleCreate, db: Session = Depends(get_db)):
    """Create a new puzzle."""
    puzzle = Puzzle(**puzzle_data.model_dump())
    db.add(puzzle)
    db.commit()
    db.refresh(puzzle)
    return puzzle


@router.get("/puzzles", response_model=List[PuzzleResponse])
def get_puzzles(
    puzzle_type: Optional[PuzzleType] = None,
    difficulty: Optional[DifficultyLevel] = None,
    age_group: Optional[AgeGroup] = None,
    daily_only: bool = False,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get list of puzzles with optional filtering."""
    query = db.query(Puzzle)
    
    if puzzle_type:
        query = query.filter(Puzzle.puzzle_type == puzzle_type)
    
    if difficulty:
        query = query.filter(Puzzle.difficulty == difficulty)
    
    if age_group:
        query = query.filter(Puzzle.age_group == age_group)
    
    if daily_only:
        query = query.filter(Puzzle.is_daily_challenge == True)
    
    puzzles = query.offset(skip).limit(limit).all()
    return puzzles


@router.get("/puzzles/{puzzle_id}", response_model=PuzzleResponse)
def get_puzzle(puzzle_id: int, db: Session = Depends(get_db)):
    """Get a specific puzzle by ID."""
    puzzle = db.query(Puzzle).filter(Puzzle.id == puzzle_id).first()
    if not puzzle:
        raise HTTPException(status_code=404, detail="Puzzle not found")
    return puzzle


@router.post("/puzzles/submit", response_model=PuzzleResult)
def submit_puzzle(submission: PuzzleSubmission, user_id: int, db: Session = Depends(get_db)):
    """Submit and validate a puzzle solution."""
    # Get puzzle
    puzzle = db.query(Puzzle).filter(Puzzle.id == submission.puzzle_id).first()
    if not puzzle:
        raise HTTPException(status_code=404, detail="Puzzle not found")
    
    # Validate solution
    is_correct = validate_puzzle_solution(puzzle, submission.user_solution)
    
    # Get or create user progress
    progress = db.query(UserPuzzleProgress).filter(
        UserPuzzleProgress.user_id == user_id,
        UserPuzzleProgress.puzzle_id == submission.puzzle_id
    ).first()
    
    if not progress:
        progress = UserPuzzleProgress(
            user_id=user_id,
            puzzle_id=submission.puzzle_id,
            attempts=0
        )
        db.add(progress)
    
    # Update progress
    progress.attempts += 1
    
    points_earned = 0
    message = "Incorrect solution. Try again!"
    
    if is_correct and not progress.is_completed:
        progress.is_completed = True
        progress.completed_at = datetime.utcnow()
        progress.completion_time_seconds = submission.completion_time_seconds
        points_earned = puzzle.points_reward
        progress.points_earned = points_earned
        
        # Update child profile points (legacy)
        child_profile = db.query(ChildProfile).filter(ChildProfile.user_id == user_id).first()
        if child_profile:
            child_profile.total_points += points_earned
        
        # Award points using gamification service
        from app.services.gamification_service import GamificationService
        from app.models.activity import ActivityType
        
        gamification_service = GamificationService(db)
        gamification_service.award_points(
            user_id=user_id,
            activity_type=ActivityType.PUZZLE_SOLVED,
            reference_id=puzzle.id,
            reference_type="puzzle"
        )
        
        message = f"Congratulations! You earned {points_earned} points!"
    elif is_correct and progress.is_completed:
        message = "You've already completed this puzzle!"
    
    db.commit()
    
    return PuzzleResult(
        is_correct=is_correct,
        points_earned=points_earned,
        completion_time_seconds=submission.completion_time_seconds,
        message=message
    )


@router.get("/puzzles/progress/{user_id}", response_model=List[UserPuzzleProgressResponse])
def get_user_puzzle_progress(user_id: int, db: Session = Depends(get_db)):
    """Get user's puzzle progress."""
    progress = db.query(UserPuzzleProgress).filter(
        UserPuzzleProgress.user_id == user_id
    ).all()
    return progress


@router.get("/puzzles/stats/{user_id}", response_model=PuzzleStats)
def get_puzzle_stats(user_id: int, db: Session = Depends(get_db)):
    """Get user's puzzle statistics."""
    # Get total puzzles
    total_puzzles = db.query(Puzzle).count()
    
    # Get completed puzzles
    completed_count = db.query(UserPuzzleProgress).filter(
        UserPuzzleProgress.user_id == user_id,
        UserPuzzleProgress.is_completed == True
    ).count()
    
    # Get total points
    total_points = db.query(func.sum(UserPuzzleProgress.points_earned)).filter(
        UserPuzzleProgress.user_id == user_id
    ).scalar() or 0
    
    # Get average completion time
    avg_time = db.query(func.avg(UserPuzzleProgress.completion_time_seconds)).filter(
        UserPuzzleProgress.user_id == user_id,
        UserPuzzleProgress.is_completed == True
    ).scalar()
    
    # Get stats by puzzle type
    by_type = {}
    for puzzle_type in PuzzleType:
        count = db.query(UserPuzzleProgress).join(Puzzle).filter(
            UserPuzzleProgress.user_id == user_id,
            UserPuzzleProgress.is_completed == True,
            Puzzle.puzzle_type == puzzle_type
        ).count()
        by_type[puzzle_type.value] = count
    
    return PuzzleStats(
        total_puzzles=total_puzzles,
        completed_puzzles=completed_count,
        total_points=int(total_points),
        average_completion_time=float(avg_time) if avg_time else None,
        by_type=by_type
    )


@router.post("/generate", status_code=status.HTTP_201_CREATED)
def generate_ai_puzzle(
    puzzle_type: Optional[str] = "word_search",
    topic: Optional[str] = "animals",
    difficulty: Optional[str] = "easy",
    age_group: Optional[str] = "6-8",
    save_to_db: bool = False,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate a random puzzle using AI (Hugging Face models).
    
    Args:
        puzzle_type: word_search, crossword, sudoku
        topic: Theme for the puzzle (e.g., animals, space, ocean)
        difficulty: easy, medium, hard
        age_group: 3-5, 6-8, 9-11, 12-14
        save_to_db: Whether to save the generated puzzle to database
    
    Returns:
        Generated puzzle with all data
    """
    try:
        from app.services.ai_content import generate_complete_puzzle
        
        # Generate puzzle using AI
        puzzle_data = generate_complete_puzzle(
            puzzle_type=puzzle_type,
            topic=topic,
            difficulty=difficulty,
            age_group=age_group
        )
        
        # Map difficulty string to enum
        difficulty_map = {
            "easy": DifficultyLevel.EASY,
            "medium": DifficultyLevel.MEDIUM,
            "hard": DifficultyLevel.HARD
        }
        
        # Map puzzle type string to enum
        type_map = {
            "word_search": PuzzleType.WORD_SEARCH,
            "crossword": PuzzleType.CROSSWORD,
            "sudoku": PuzzleType.SUDOKU,
            "jigsaw": PuzzleType.JIGSAW
        }
        
        # Map age group string to enum
        age_map = {
            "3-5": AgeGroup.TODDLER,
            "6-8": AgeGroup.EARLY,
            "9-11": AgeGroup.MIDDLE,
            "12-14": AgeGroup.PRETEEN
        }
        
        # Points based on difficulty
        points_map = {"easy": 50, "medium": 75, "hard": 100}
        
        if save_to_db:
            # Create database record
            puzzle = Puzzle(
                title=puzzle_data.get("title", f"{topic.title()} Puzzle"),
                description=puzzle_data.get("description", "AI-generated puzzle"),
                puzzle_type=type_map.get(puzzle_type, PuzzleType.WORD_SEARCH),
                difficulty=difficulty_map.get(difficulty, DifficultyLevel.EASY),
                age_group=age_map.get(age_group, AgeGroup.AGE_6_8),
                puzzle_data=puzzle_data.get("puzzle_data", {}),
                solution_data=puzzle_data.get("solution_data", {}),
                points_reward=points_map.get(difficulty, 50),
                is_daily_challenge=False
            )
            
            db.add(puzzle)
            db.commit()
            db.refresh(puzzle)
            
            # Convert to dict for response
            return {
                "id": puzzle.id,
                "title": puzzle.title,
                "description": puzzle.description,
                "puzzle_type": puzzle_type,
                "difficulty": difficulty,
                "age_group": age_group,
                "puzzle_data": puzzle.puzzle_data,
                "solution_data": puzzle.solution_data,
                "points_reward": puzzle.points_reward
            }
        else:
            # Return generated puzzle data directly
            return {
                "id": 0,
                "title": puzzle_data.get("title", f"{topic.title()} Puzzle"),
                "description": puzzle_data.get("description", "AI-generated puzzle"),
                "puzzle_type": puzzle_type,
                "difficulty": difficulty,
                "age_group": age_group,
                "puzzle_data": puzzle_data.get("puzzle_data", {}),
                "solution_data": puzzle_data.get("solution_data", {}),
                "points_reward": points_map.get(difficulty, 50)
            }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate puzzle: {str(e)}"
        )


