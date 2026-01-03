"""
Database migration script for Multi-Agent Homework System

Creates tables:
- materials
- material_chunks
- agent_runs

Run this script to create the new tables.
"""

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import Base
from app.models.homework_agents import Material, MaterialChunk, AgentRunLog

def run_migration():
    """Create new tables for multi-agent system"""
    print("="*60)
    print("Multi-Agent Homework System - Database Migration")
    print("="*60)
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    print("\n📊 Creating tables...")
    
    try:
        # Create tables
        Base.metadata.create_all(bind=engine, tables=[
            Material.__table__,
            MaterialChunk.__table__,
            AgentRunLog.__table__
        ])
        
        print("✅ Tables created successfully!")
        
        # Verify tables
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name IN ('materials', 'material_chunks', 'agent_runs')"
            ))
            tables = [row[0] for row in result]
            
            print(f"\n📋 Verified tables:")
            for table in tables:
                print(f"   ✓ {table}")
            
            if len(tables) == 3:
                print("\n✅ Migration completed successfully!")
            else:
                print(f"\n⚠️  Warning: Expected 3 tables, found {len(tables)}")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        raise
    
    print("\n" + "="*60)
    print("Next steps:")
    print("1. Restart the backend server")
    print("2. Check API docs: http://localhost:8000/docs")
    print("3. Test material upload: python test_agent_system.py")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_migration()
