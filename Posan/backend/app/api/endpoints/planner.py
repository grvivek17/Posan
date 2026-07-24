from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.study_plan import StudyPlan, StudySession, GamificationProfile
from app.agents.planner_agent import planner_agent


router = APIRouter(prefix="/planner", tags=["planner"])


class GeneratePlanRequest(BaseModel):
    subject: str
    topics: List[str]
    start_date: str
    end_date: str


@router.post("/generate")
async def generate_study_plan(
    request: GeneratePlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a study plan using the Planner Agent and save it to the database.
    """
    try:
        # Call the planner agent
        output = planner_agent.execute(
            input_data={
                "subject": request.subject,
                "topics": request.topics,
                "start_date": request.start_date,
                "end_date": request.end_date
            },
            user_id=str(current_user.id),
            related_entity="study_plan"
        )
        
        if output.status != "success":
            raise HTTPException(status_code=500, detail=f"Planner agent failed: {output.error}")
            
        result = output.result
        
        # Save to DB
        new_plan = StudyPlan(
            user_id=str(current_user.id),
            title=result.get("title", f"{request.subject} Plan"),
            subject=result.get("subject"),
            start_date=datetime.strptime(result.get("start_date"), "%Y-%m-%d"),
            end_date=datetime.strptime(result.get("end_date"), "%Y-%m-%d"),
            total_sessions=result.get("total_sessions", 0)
        )
        db.add(new_plan)
        db.flush()
        
        for s in result.get("sessions", []):
            session = StudySession(
                plan_id=new_plan.id,
                date=datetime.strptime(s.get("date"), "%Y-%m-%d"),
                topic=s.get("topic"),
                duration_minutes=s.get("duration_minutes", 30)
            )
            db.add(session)
            
        db.commit()
        db.refresh(new_plan)
        
        return {
            "success": True,
            "message": "Study plan generated successfully",
            "plan_id": new_plan.id,
            "total_sessions": new_plan.total_sessions
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plans")
async def get_study_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all study plans for the current user."""
    plans = db.query(StudyPlan).filter(StudyPlan.user_id == str(current_user.id)).all()
    
    response = []
    for plan in plans:
        # Get sessions for this plan
        sessions = db.query(StudySession).filter(StudySession.plan_id == plan.id).order_by(StudySession.date).all()
        
        plan_data = {
            "id": plan.id,
            "title": plan.title,
            "subject": plan.subject,
            "start_date": plan.start_date.strftime("%Y-%m-%d"),
            "end_date": plan.end_date.strftime("%Y-%m-%d"),
            "total_sessions": plan.total_sessions,
            "completed_sessions": plan.completed_sessions,
            "sessions": [
                {
                    "id": s.id,
                    "date": s.date.strftime("%Y-%m-%d"),
                    "topic": s.topic,
                    "duration_minutes": s.duration_minutes,
                    "is_completed": s.is_completed,
                    "points_earned": s.points_earned
                } for s in sessions
            ]
        }
        response.append(plan_data)
        
    return {"plans": response}


@router.post("/sessions/{session_id}/complete")
async def complete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a session as complete and update gamification profile."""
    # Fetch session and verify ownership via plan
    session = db.query(StudySession).join(StudyPlan).filter(
        StudySession.id == session_id,
        StudyPlan.user_id == str(current_user.id)
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Study session not found")
        
    if session.is_completed:
        return {"success": True, "message": "Session already completed", "points_earned": 0}
        
    # Mark complete
    session.is_completed = True
    session.points_earned = 10  # Standard 10 points per session
    
    # Update plan completion count
    plan = session.plan
    plan.completed_sessions += 1
    
    # Gamification Logic
    profile = db.query(GamificationProfile).filter(GamificationProfile.user_id == str(current_user.id)).first()
    if not profile:
        profile = GamificationProfile(user_id=str(current_user.id))
        db.add(profile)
        db.flush()
        
    today = datetime.utcnow().date()
    
    # Check streak logic
    if profile.last_activity_date:
        last_date = profile.last_activity_date.date()
        diff = (today - last_date).days
        
        if diff == 1:
            # Maintained streak
            profile.current_streak += 1
        elif diff > 1:
            # Lost streak
            profile.current_streak = 1
        # If diff == 0, they already studied today, so streak doesn't increase, just points
    else:
        # First time studying
        profile.current_streak = 1
        
    if profile.current_streak > profile.max_streak:
        profile.max_streak = profile.current_streak
        
    profile.total_points += session.points_earned
    profile.last_activity_date = datetime.utcnow()
    
    db.commit()
    
    return {
        "success": True,
        "message": "Session completed!",
        "points_earned": session.points_earned,
        "current_streak": profile.current_streak,
        "total_points": profile.total_points
    }


@router.get("/gamification")
async def get_gamification_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's gamification stats"""
    profile = db.query(GamificationProfile).filter(GamificationProfile.user_id == str(current_user.id)).first()
    
    if not profile:
        return {
            "current_streak": 0,
            "max_streak": 0,
            "total_points": 0,
            "last_activity_date": None
        }
        
    return {
        "current_streak": profile.current_streak,
        "max_streak": profile.max_streak,
        "total_points": profile.total_points,
        "last_activity_date": profile.last_activity_date.isoformat() if profile.last_activity_date else None
    }
