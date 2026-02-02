import sys
from app.core.database import engine, SessionLocal
from app.models.user import User
from app.models.subscription import Subscription, SubscriptionTier, SubscriptionStatus
from datetime import datetime, timedelta

def upgrade_user_to_pro(username):
    db = SessionLocal()
    try:
        # Find user
        user = db.query(User).filter(User.username == username.lower()).first()
        
        if not user:
            print(f"❌ User '{username}' not found!")
            print("\nAvailable users:")
            users = db.query(User).all()
            for u in users:
                print(f"  - {u.username} ({u.email})")
            return
        
        print(f"✅ Found user: {user.username} (ID: {user.id})")
        
        # Check existing subscription
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user.id
        ).first()
        
        if subscription:
            print(f"📋 Current subscription: {subscription.tier.value} ({subscription.status.value})")
        else:
            print("📋 No subscription found, creating new one...")
            subscription = Subscription(user_id=user.id)
            db.add(subscription)
        
        # Upgrade to Pro
        subscription.tier = SubscriptionTier.PRO
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.ai_image_generation = True
        subscription.advanced_puzzles = True
        subscription.unlimited_content = True
        subscription.no_ads = True
        subscription.expires_at = datetime.utcnow() + timedelta(days=365)  # 1 year
        subscription.started_at = datetime.utcnow()
        
        db.commit()
        db.refresh(subscription)
        
        print(f"\n🎉 Successfully upgraded {user.username} to PRO!")
        print(f"   Tier: {subscription.tier.value}")
        print(f"   Status: {subscription.status.value}")
        print(f"   Expires: {subscription.expires_at}")
        print(f"   Features:")
        print(f"     - AI Image Generation: {subscription.ai_image_generation}")
        print(f"     - Advanced Puzzles: {subscription.advanced_puzzles}")
        print(f"     - Unlimited Content: {subscription.unlimited_content}")
        print(f"     - No Ads: {subscription.no_ads}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python upgrade_user_to_pro.py <username>")
        print("\nListing all users:")
        db = SessionLocal()
        users = db.query(User).all()
        for u in users:
            sub = db.query(Subscription).filter(Subscription.user_id == u.id).first()
            tier = sub.tier.value if sub else "none"
            print(f"  - {u.username} ({u.email}) - Tier: {tier}")
        db.close()
    else:
        upgrade_user_to_pro(sys.argv[1])
