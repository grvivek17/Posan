"""
Subscription model for Pro/Premium features
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class SubscriptionTier(str, enum.Enum):
    """Subscription tier levels"""
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"


class SubscriptionStatus(str, enum.Enum):
    """Subscription status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    TRIAL = "trial"


class Subscription(Base):
    """User subscription model"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Subscription details
    tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False)
    status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False)
    
    # Dates
    started_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    
    # Payment info (for future integration)
    payment_provider = Column(String, nullable=True)  # e.g., "stripe", "razorpay"
    payment_id = Column(String, nullable=True)
    
    # Features enabled
    ai_image_generation = Column(Boolean, default=False)
    advanced_puzzles = Column(Boolean, default=False)
    unlimited_content = Column(Boolean, default=False)
    no_ads = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="subscription")
    
    def is_active(self) -> bool:
        """Check if subscription is currently active"""
        if self.status != SubscriptionStatus.ACTIVE:
            return False
        
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        
        return True
    
    def has_feature(self, feature: str) -> bool:
        """Check if subscription has a specific feature"""
        if not self.is_active():
            return False
        
        return getattr(self, feature, False)
    
    def upgrade_to_pro(self):
        """Upgrade to Pro tier"""
        self.tier = SubscriptionTier.PRO
        self.status = SubscriptionStatus.ACTIVE
        self.ai_image_generation = True
        self.advanced_puzzles = True
        self.unlimited_content = True
        self.no_ads = True
    
    def upgrade_to_premium(self):
        """Upgrade to Premium tier"""
        self.tier = SubscriptionTier.PREMIUM
        self.status = SubscriptionStatus.ACTIVE
        self.ai_image_generation = True
        self.advanced_puzzles = True
        self.unlimited_content = True
        self.no_ads = True
