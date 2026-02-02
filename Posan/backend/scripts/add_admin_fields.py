"""
Migration script to add is_admin, full_name, and last_login fields to users table
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import engine
from sqlalchemy import text

def add_user_fields():
    """Add new fields to users table"""
    print("=" * 60)
    print("📊 Adding new fields to users table")
    print("=" * 60)
    
    with engine.connect() as conn:
        try:
            # Add is_admin field
            print("\n1️⃣  Adding is_admin field...")
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE"))
            conn.commit()
            print("   ✅ is_admin added")
            
            # Add full_name field
            print("\n2️⃣  Adding full_name field...")
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR"))
            conn.commit()
            print("   ✅ full_name added")
            
            # Add last_login field
            print("\n3️⃣  Adding last_login field...")
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE"))
            conn.commit()
            print("   ✅ last_login added")
            
            print("\n" + "=" * 60)
            print("✅ Migration completed successfully!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Error during migration: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    add_user_fields()
