"""
Razorpay Payment Integration Service
Handles payment processing for subscriptions
"""
import razorpay
from app.core.config import settings
from typing import Dict, Any, Optional
from datetime import datetime


class RazorpayService:
    """Service for handling Razorpay payments"""
    
    def __init__(self):
        """Initialize Razorpay client"""
        if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
            print("⚠️  WARNING: Razorpay credentials not configured")
            self.client = None
        else:
            self.client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )
            print("[OK] Razorpay client initialized")
    
    def create_order(
        self, 
        amount: float, 
        currency: str = "INR",
        receipt: Optional[str] = None,
        notes: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a Razorpay order
        
        Args:
            amount: Amount in base currency (will be converted to paise/cents)
            currency: Currency code (INR, USD, etc.)
            receipt: Receipt ID for your reference
            notes: Additional notes/metadata
        
        Returns:
            Order details including order_id
        """
        if not self.client:
            raise Exception("Razorpay not configured")
        
        # Convert amount to smallest currency unit (paise for INR)
        amount_in_paise = int(amount * 100)
        
        if not receipt:
            receipt = f"rcpt_{int(datetime.now().timestamp())}"
        
        order_data = {
            "amount": amount_in_paise,
            "currency": currency,
            "receipt": receipt,
            "notes": notes or {}
        }
        
        order = self.client.order.create(data=order_data)
        return order
    
    def verify_payment(
        self, 
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str
    ) -> bool:
        """
        Verify payment signature
        
        Args:
            razorpay_order_id: Order ID from Razorpay
            razorpay_payment_id: Payment ID from Razorpay
            razorpay_signature: Signature to verify
        
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.client:
            raise Exception("Razorpay not configured")
        
        try:
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            self.client.utility.verify_payment_signature(params_dict)
            return True
        except razorpay.errors.SignatureVerificationError:
            return False
    
    def get_payment_details(self, payment_id: str) -> Dict[str, Any]:
        """
        Get payment details
        
        Args:
            payment_id: Razorpay payment ID
        
        Returns:
            Payment details
        """
        if not self.client:
            raise Exception("Razorpay not configured")
        
        return self.client.payment.fetch(payment_id)
    
    def create_subscription_order(
        self,
        tier: str,
        user_id: int,
        user_email: str
    ) -> Dict[str, Any]:
        """
        Create order for subscription
        
        Args:
            tier: Subscription tier (pro, premium)
            user_id: User ID
            user_email: User email
        
        Returns:
            Order details
        """
        # Define pricing
        pricing = {
            "pro": {"amount": 99, "currency": "INR", "description": "Pro Monthly"},
            "premium": {"amount": 999, "currency": "INR", "description": "Premium Yearly"}
        }
        
        if tier.lower() not in pricing:
            raise ValueError(f"Invalid tier: {tier}")
        
        plan = pricing[tier.lower()]
        
        return self.create_order(
            amount=plan["amount"],
            currency=plan["currency"],
            receipt=f"sub_{tier}_{user_id}_{int(datetime.now().timestamp())}",
            notes={
                "user_id": str(user_id),
                "user_email": user_email,
                "tier": tier,
                "type": "subscription"
            }
        )


# Global instance
razorpay_service = RazorpayService()
