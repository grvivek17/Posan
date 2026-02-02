"""
Migration script to add daily_puzzle_generations table
This table tracks puzzle generation limits (one per user per day)
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import engine, Base
from app.models.puzzle_generation import DailyPuzzleGeneration

def create_puzzle_generation_table():
    """Create the daily_puzzle_generations table"""
    print("📊 Creating daily_puzzle_generations table...")
    
    try:
        # Create the table
        Base.metadata.create_all(bind=engine, tables=[DailyPuzzleGeneration.__table__])
        print("✅ Table created successfully!")
        print("\nℹ️  This table will track:")
        print("   - User ID")
        print("   - Generation date")  
        print("   - Puzzle type")
        print("   - Topic and difficulty")
        print("\n🎯 Limit: One puzzle generation per user per day")
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        raise

if __name__ == "__main__":
    create_puzzle_generation_table()
