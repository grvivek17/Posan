"""
Seed default badges for the gamification system
"""
from app.core.database import SessionLocal
from app.models.gamification import Badge

def seed_badges():
    """Create default badges for the gamification system."""
    db = SessionLocal()
    
    try:
        # Check if badges already exist
        existing_badges = db.query(Badge).count()
        if existing_badges > 0:
            print(f"Badges already exist ({existing_badges} badges found). Skipping seed.")
            return
        
        badges = [
            # Beginner Badges
            Badge(
                name="First Steps",
                description="Welcome to POSAN! Complete your first activity.",
                points_required=0,
                puzzles_required=0,
                is_special=False
            ),
            Badge(
                name="Puzzle Novice",
                description="Solve your first puzzle!",
                points_required=0,
                puzzles_required=1,
                is_special=False
            ),
            Badge(
                name="Point Collector",
                description="Earn your first 50 points.",
                points_required=50,
                puzzles_required=0,
                is_special=False
            ),
            
            # Intermediate Badges
            Badge(
                name="Puzzle Enthusiast",
                description="Solve 10 puzzles.",
                points_required=0,
                puzzles_required=10,
                is_special=False
            ),
            Badge(
                name="Century Club",
                description="Reach 100 points!",
                points_required=100,
                puzzles_required=0,
                is_special=False
            ),
            Badge(
                name="Dedicated Learner",
                description="Reach 250 points.",
                points_required=250,
                puzzles_required=0,
                is_special=False
            ),
            Badge(
                name="Puzzle Master",
                description="Solve 25 puzzles.",
                points_required=0,
                puzzles_required=25,
                is_special=False
            ),
            
            # Advanced Badges
            Badge(
                name="Half Century",
                description="Solve 50 puzzles!",
                points_required=0,
                puzzles_required=50,
                is_special=False
            ),
            Badge(
                name="Point Champion",
                description="Reach 500 points!",
                points_required=500,
                puzzles_required=0,
                is_special=False
            ),
            Badge(
                name="Elite Solver",
                description="Solve 100 puzzles.",
                points_required=0,
                puzzles_required=100,
                is_special=True
            ),
            
            # Expert Badges
            Badge(
                name="Thousand Club",
                description="Reach 1000 points!",
                points_required=1000,
                puzzles_required=0,
                is_special=True
            ),
            Badge(
                name="Puzzle Legend",
                description="Solve 200 puzzles!",
                points_required=0,
                puzzles_required=200,
                is_special=True
            ),
            Badge(
                name="Ultimate Champion",
                description="Reach 2000 points and solve 100 puzzles!",
                points_required=2000,
                puzzles_required=100,
                is_special=True
            ),
            
            # Special Event Badges
            Badge(
                name="Early Adopter",
                description="One of the first users of POSAN!",
                points_required=10,
                puzzles_required=0,
                is_special=True
            ),
            Badge(
                name="Weekend Warrior",
                description="Complete 20 activities on weekends.",
                points_required=100,
                puzzles_required=0,
                is_special=True
            ),
        ]
        
        # Add all badges to database
        for badge in badges:
            db.add(badge)
        
        db.commit()
        print(f"Successfully created {len(badges)} badges!")
        
        # Print summary
        print("\nBadges created:")
        for badge in badges:
            special = " ⭐ SPECIAL" if badge.is_special else ""
            print(f"  - {badge.name}{special}")
            print(f"    {badge.description}")
            if badge.points_required > 0:
                print(f"    Requires: {badge.points_required} points")
            if badge.puzzles_required > 0:
                print(f"    Requires: {badge.puzzles_required} puzzles")
            print()
        
    except Exception as e:
        print(f"Error seeding badges: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Seeding badges...")
    seed_badges()
    print("Done!")
