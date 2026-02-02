from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, ChildProfile, ParentAccount, AgeGroup
from app.schemas.user import UserResponse, ChildProfileCreate, ChildProfileUpdate, ChildProfileResponse

router = APIRouter()


def get_age_group(age: int) -> AgeGroup:
    """Determine age group based on age."""
    if 3 <= age <= 5:
        return AgeGroup.TODDLER
    elif 6 <= age <= 8:
        return AgeGroup.EARLY
    elif 9 <= age <= 11:
        return AgeGroup.MIDDLE
    elif 12 <= age <= 14:
        return AgeGroup.PRETEEN
    else:
        raise ValueError("Age must be between 3 and 14")


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information from JWT token."""
    return current_user


@router.post("/child-profile", response_model=ChildProfileResponse, status_code=status.HTTP_201_CREATED)
def create_child_profile(
    child_data: ChildProfileCreate,
    parent_user_id: int,
    child_user_id: int,
    db: Session = Depends(get_db)
):
    """Create a child profile linked to parent account."""
    # Get parent account
    parent_account = db.query(ParentAccount).filter(ParentAccount.user_id == parent_user_id).first()
    if not parent_account:
        raise HTTPException(status_code=404, detail="Parent account not found")
    
    # Check if child user exists
    child_user = db.query(User).filter(User.id == child_user_id).first()
    if not child_user:
        raise HTTPException(status_code=404, detail="Child user not found")
    
    # Check if child profile already exists
    existing_profile = db.query(ChildProfile).filter(ChildProfile.user_id == child_user_id).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="Child profile already exists")
    
    # Determine age group
    age_group = get_age_group(child_data.age)
    
    # Create child profile
    child_profile = ChildProfile(
        user_id=child_user_id,
        parent_id=parent_account.id,
        full_name=child_data.full_name,
        age=child_data.age,
        age_group=age_group,
        avatar_url=child_data.avatar_url
    )
    
    db.add(child_profile)
    db.commit()
    db.refresh(child_profile)
    
    return child_profile


@router.get("/child-profiles", response_model=List[ChildProfileResponse])
def get_child_profiles(parent_user_id: int, db: Session = Depends(get_db)):
    """Get all child profiles for a parent."""
    parent_account = db.query(ParentAccount).filter(ParentAccount.user_id == parent_user_id).first()
    if not parent_account:
        raise HTTPException(status_code=404, detail="Parent account not found")
    
    children = db.query(ChildProfile).filter(ChildProfile.parent_id == parent_account.id).all()
    return children


@router.get("/child-profile/{child_id}", response_model=ChildProfileResponse)
def get_child_profile(child_id: int, db: Session = Depends(get_db)):
    """Get a specific child profile."""
    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child profile not found")
    return child


@router.put("/child-profile/{child_id}", response_model=ChildProfileResponse)
def update_child_profile(
    child_id: int,
    child_data: ChildProfileUpdate,
    db: Session = Depends(get_db)
):
    """Update a child profile."""
    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child profile not found")
    
    # Update fields if provided
    if child_data.full_name is not None:
        child.full_name = child_data.full_name
    
    if child_data.age is not None:
        child.age = child_data.age
        child.age_group = get_age_group(child_data.age)
    
    if child_data.avatar_url is not None:
        child.avatar_url = child_data.avatar_url
    
    db.commit()
    db.refresh(child)
    
    return child
