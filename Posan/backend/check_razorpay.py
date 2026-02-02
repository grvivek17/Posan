"""
Quick script to verify Razorpay configuration
"""
from app.services.payment_service import razorpay_service

print("=" * 60)
print("🔍 Checking Razorpay Configuration")
print("=" * 60)

if razorpay_service.client is None:
    print("❌ FAILED: Razorpay client is not initialized")
    print("   Reason: Missing credentials in .env file")
    print("")
    print("   Required in .env:")
    print("   RAZORPAY_KEY_ID=rzp_test_...")
    print("   RAZORPAY_KEY_SECRET=...")
else:
    print("✅ SUCCESS: Razorpay client is initialized!")
    print("")
    print("   Configuration:")
    key_id = razorpay_service.client.auth[0] if razorpay_service.client else "N/A"
    print(f"   Key ID: {key_id[:15]}..." if len(key_id) > 15 else f"   Key ID: {key_id}")
    print("   Secret: ********** (hidden)")
    print("")
    print("✅ Payment integration is ready!")
    print("")
    print("   You can now:")
    print("   1. Create payment orders")
    print("   2. Process subscriptions")
    print("   3. Test with Razorpay test cards")

print("=" * 60)
