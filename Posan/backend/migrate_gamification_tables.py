"""
Migration script to create gamification tables in PostgreSQL
Run this to add the new user_activities and user_levels tables
"""
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import Base, engine
from app.models.activity import UserActivity, UserLevel
from app.models.gamification import Badge, UserAchievement, Leaderboard

def create_gamification_tables():
    """Create the new gamification tables."""
    print("Creating gamification tables...")
    
    try:
        # Create all tables defined in models
        # This will only create tables that don't exist yet
        Base.metadata.create_all(bind=engine)
        
        print("✅ Successfully created gamification tables!")
        print("\nTables created/verified:")
        print("  - user_activities (tracks all user activities and points)")
        print("  - user_levels (stores user level progression)")
        print("  - badges (achievement definitions)")
        print("  - user_achievements (user's earned badges)")
        print("  - leaderboard (competitive rankings)")
        
        # Verify tables exist
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('user_activities', 'user_levels', 'badges', 'user_achievements', 'leaderboard')
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result]
            
            print("\n✅ Verified tables in database:")
            for table in tables:
                print(f"  ✓ {table}")
            
            if 'user_activities' not in tables:
                print("\n⚠️  Warning: user_activities table not found!")
            if 'user_levels' not in tables:
                print("\n⚠️  Warning: user_levels table not found!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating tables: {e}")
        return False


def show_table_schemas():
    """Display the schema of the new tables."""
    print("\n" + "="*60)
    print("TABLE SCHEMAS")
    print("="*60)
    
    print("\n1. USER_ACTIVITIES TABLE:")
    print("-" * 60)
    print("""
    Column              | Type          | Description
    --------------------|---------------|---------------------------
    id                  | INTEGER       | Primary key
    user_id             | INTEGER       | Foreign key to users
    activity_type       | ENUM          | Type of activity
    points_earned       | INTEGER       | Points awarded
    reference_id        | INTEGER       | Related entity ID (optional)
    reference_type      | VARCHAR       | Type of reference (optional)
    created_at          | TIMESTAMP     | When activity occurred
    
    Activity Types:
    - puzzle_solved (10 pts)
    - article_read (5 pts)
    - comment_posted (2 pts)
    - content_shared (3 pts)
    - quiz_completed (15 pts)
    - daily_login (1 pt)
    - profile_completed (20 pts)
    - homework_uploaded (8 pts)
    - study_plan_created (12 pts)
    """)
    
    print("\n2. USER_LEVELS TABLE:")
    print("-" * 60)
    print("""
    Column              | Type          | Description
    --------------------|---------------|---------------------------
    id                  | INTEGER       | Primary key
    user_id             | INTEGER       | Foreign key to users (unique)
    current_level       | VARCHAR       | Level name (Bronze, Silver, etc.)
    level_number        | INTEGER       | Numeric level (1-6)
    points_to_next_level| INTEGER       | Points needed for next level
    updated_at          | TIMESTAMP     | Last update time
    
    Levels:
    1. Bronze (0-99 pts)
    2. Silver (100-299 pts)
    3. Gold (300-599 pts)
    4. Platinum (600-999 pts)
    5. Diamond (1000-1999 pts)
    6. Master (2000+ pts)
    """)


if __name__ == "__main__":
    print("="*60)
    print("GAMIFICATION TABLES MIGRATION")
    print("="*60)
    print(f"\nDatabase: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'PostgreSQL'}")
    print("\nThis script will create the following tables:")
    print("  • user_activities")
    print("  • user_levels")
    print("\nExisting tables will not be modified.")
    print("-"*60)
    
    input("\nPress Enter to continue or Ctrl+C to cancel...")
    
    success = create_gamification_tables()
    
    if success:
        show_table_schemas()
        print("\n" + "="*60)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nNext steps:")
        print("  1. Run: python seed_badges.py")
        print("  2. Test the gamification system at /achievements")
        print("  3. Complete a puzzle to earn your first points!")
    else:
        print("\n" + "="*60)
        print("❌ MIGRATION FAILED")
        print("="*60)
        print("\nPlease check the error message above and try again.")
