"""
Initialize subscriptions table and create default subscriptions for existing users
Run this script once to set up the subscription system
"""
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine,  Base
from app.models.user import User
from app.models.subscription import Subscription, SubscriptionTier, SubscriptionStatus

def init_subscriptions():
    """Initialize subscriptions table and create default subscriptions"""
    
    print("Creating subscriptions table...")
    # Create all tables (including subscription)
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")
    
    db = SessionLocal()
    try:
        # Get all users without subscriptions
        users = db.query(User).all()
        
        print(f"\nFound {len(users)} users")
        
        for user in users:
            # Check if user already has a subscription
            existing = db.query(Subscription).filter(
                Subscription.user_id == user.id
            ).first()
            
            if not existing:
                # Create free tier subscription
                subscription = Subscription(
                    user_id=user.id,
                    tier=SubscriptionTier.FREE,
                    status=SubscriptionStatus.ACTIVE,
                    ai_image_generation=False,
                    advanced_puzzles=False,
                    unlimited_content=False,
                    no_ads=False
                )
                db.add(subscription)
                print(f"✓ Created FREE subscription for user {user.username}")
            else:
                print(f"- User {user.username} already has subscription ({existing.tier.value})")
        
        db.commit()
        print("\n✅ Subscription initialization complete!")
        print("\nNext steps:")
        print("1. Restart your backend server")
        print("2. Test the subscription API at /docs")
        print("3. Try upgrading a user to PRO")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 50)
    print("Subscription System Initialization")
    print("=" * 50)
    init_subscriptions()
