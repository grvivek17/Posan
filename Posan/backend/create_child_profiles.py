"""
Create child profile for user if missing
This ensures gamification works for all users
"""
from app.core.database import SessionLocal
from app.models.user import User, ChildProfile, AgeGroup

def create_child_profile_for_user(user_id: int):
    """Create a default child profile for a user if they don't have one."""
    db = SessionLocal()
    
    try:
        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"❌ User with ID {user_id} not found")
            return False
        
        # Check if child profile already exists
        existing_profile = db.query(ChildProfile).filter(
            ChildProfile.user_id == user_id
        ).first()
        
        if existing_profile:
            print(f"✅ Child profile already exists for user {user.username}")
            print(f"   Total points: {existing_profile.total_points}")
            return True
        
        # Create child profile
        child_profile = ChildProfile(
            user_id=user_id,
            parent_id=None,  # No parent for now
            full_name=user.username.title(),
            age=10,  # Default age
            age_group=AgeGroup.MIDDLE,  # 9-11 years
            total_points=0
        )
        
        db.add(child_profile)
        db.commit()
        db.refresh(child_profile)
        
        print(f"✅ Created child profile for user: {user.username}")
        print(f"   User ID: {user_id}")
        print(f"   Profile ID: {child_profile.id}")
        print(f"   Age: {child_profile.age}")
        print(f"   Age Group: {child_profile.age_group.value}")
        print(f"   Total Points: {child_profile.total_points}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating child profile: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def create_profiles_for_all_users():
    """Create child profiles for all users who don't have one."""
    db = SessionLocal()
    
    try:
        users = db.query(User).all()
        print(f"Found {len(users)} users")
        print("-" * 60)
        
        created = 0
        existing = 0
        
        for user in users:
            print(f"\nChecking user: {user.username} (ID: {user.id})")
            
            profile = db.query(ChildProfile).filter(
                ChildProfile.user_id == user.id
            ).first()
            
            if profile:
                print(f"  ✓ Already has profile (Points: {profile.total_points})")
                existing += 1
            else:
                # Create profile
                child_profile = ChildProfile(
                    user_id=user.id,
                    parent_id=None,
                    full_name=user.username.title(),
                    age=10,
                    age_group=AgeGroup.MIDDLE,
                    total_points=0
                )
                db.add(child_profile)
                print(f"  ✓ Created new profile")
                created += 1
        
        db.commit()
        
        print("\n" + "=" * 60)
        print(f"Summary:")
        print(f"  Existing profiles: {existing}")
        print(f"  New profiles created: {created}")
        print(f"  Total users: {len(users)}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("CREATE CHILD PROFILES FOR GAMIFICATION")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # Create for specific user
        user_id = int(sys.argv[1])
        print(f"\nCreating profile for user ID: {user_id}\n")
        create_child_profile_for_user(user_id)
    else:
        # Create for all users
        print("\nCreating profiles for all users without one...\n")
        create_profiles_for_all_users()
    
    print("\n✅ Done!")
