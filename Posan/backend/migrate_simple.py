"""
Simple database migration - Create tables with raw SQL

This avoids SQLAlchemy relationship issues.
"""

import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "posan.db"

def run_migration():
    """Create tables using raw SQL"""
    print("="*60)
    print("Multi-Agent Homework System - Database Migration")
    print("="*60)
    print(f"\nDatabase: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Create materials table
        print("\n📊 Creating 'materials' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS materials (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                subject TEXT,
                topic TEXT,
                grade INTEGER,
                storage_url TEXT NOT NULL,
                file_extension TEXT NOT NULL,
                is_ocr BOOLEAN DEFAULT 0,
                total_chunks INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                topics_json TEXT,
                metadata_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✅ materials table created")
        
        # Create material_chunks table
        print("\n📊 Creating 'material_chunks' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS material_chunks (
                id TEXT PRIMARY KEY,
                material_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                text TEXT NOT NULL,
                tokens INTEGER NOT NULL,
                heading TEXT,
                topic TEXT,
                embedding_vector TEXT,
                metadata_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE CASCADE
            )
        """)
        print("   ✅ material_chunks table created")
        
        # Create agent_runs table
        print("\n📊 Creating 'agent_runs' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_runs (
                id TEXT PRIMARY KEY,
                agent_name TEXT NOT NULL,
                task_id TEXT NOT NULL UNIQUE,
                input_json TEXT NOT NULL,
                output_json TEXT,
                status TEXT NOT NULL,
                error TEXT,
                user_id TEXT,
                related_entity TEXT,
                related_id TEXT,
                execution_time_ms REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✅ agent_runs table created")
        
        # Create indices
        print("\n📊 Creating indices...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_runs_agent_name ON agent_runs(agent_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_runs_task_id ON agent_runs(task_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_runs_created_at ON agent_runs(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_material_chunks_material_id ON material_chunks(material_id)")
        print("   ✅ Indices created")
        
        conn.commit()
        
        # Verify tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('materials', 'material_chunks', 'agent_runs')")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"\n📋 Verified tables:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   ✓ {table} ({count} rows)")
        
        if len(tables) == 3:
            print("\n✅ Migration completed successfully!")
        else:
            print(f"\n⚠️  Warning: Expected 3 tables, found {len(tables)}")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()
    
    print("\n" + "="*60)
    print("Next steps:")
    print("1. Restart the backend server (it will auto-reload)")
    print("2. Test the new endpoints")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_migration()
