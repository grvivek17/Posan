from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
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
        
        # Update child profile points
        child_profile = db.query(ChildProfile).filter(ChildProfile.user_id == user_id).first()
        if child_profile:
            child_profile.total_points += points_earned
        
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
