"""
Script to make a user an admin
Usage: python make_admin.py <username>
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models.user import User
from app.core.database import SessionLocal

def make_admin(username):
    """Make a user an admin"""
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            print(f"❌ User '{username}' not found")
            print("\nAvailable users:")
            users = db.query(User).all()
            for u in users[:10]:
                print(f"  - {u.username} ({u.email})")
            return
        
        if user.is_admin:
            print(f"ℹ️  User '{username}' is already an admin")
            return
        
        user.is_admin = True
        db.commit()
        
        print("=" * 60)
        print(f"✅ SUCCESS! {username} is now an admin!")
        print("=" * 60)
        print(f"\nUser Details:")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Is Admin: {user.is_admin}")
        print(f"\n🎉 {username} can now access /api/v1/admin/* endpoints!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python make_admin.py <username>")
        print("\nExample:")
        print("  python make_admin.py john_doe")
        sys.exit(1)
    
    username = sys.argv[1]
    make_admin(username)
