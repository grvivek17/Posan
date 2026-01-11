"""
Check existing users in database
"""
from app.core.database import SessionLocal
from app.models.user import User

def list_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print("\n" + "=" * 60)
        print("EXISTING USERS IN DATABASE")
        print("=" * 60)
        
        if not users:
            print("\n❌ No users found in database")
            print("\nTo test password reset:")
            print("1. Register a new user first")
            print("2. Then use that email for password reset")
            return
        
        for user in users:
            print(f"\nID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Role: {user.role}")
            print("-" * 60)
        
        print(f"\nTotal users: {len(users)}")
        print("=" * 60)
        
    finally:
        db.close()

if __name__ == "__main__":
    list_users()
