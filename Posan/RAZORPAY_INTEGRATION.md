# 💳 Razorpay Payment Integration Guide

## Overview
Complete Razorpay payment gateway integration for POSAN Pro subscription system, supporting secure payment processing for Indian users.

## Setup

### 1. Get Razorpay Credentials

1. Sign up at https://razorpay.com
2. Go to Dashboard → Settings → API Keys
3. Generate Test/Live API keys

### 2. Configure Environment Variables

Add to `backend/.env`:
```bash
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxx
```

### 3. Install Dependencies

Backend:
```bash
cd backend
pip install razorpay
```

Frontend: No additional packages needed (uses Razorpay Checkout.js CDN)

## Architecture

### Payment Flow

```
1. User clicks "Pay with Razorpay"
   ↓
2. Frontend calls /subscription/razorpay/create-order
   ↓
3. Backend creates Razorpay order
   ↓
4. Frontend loads Razorpay Checkout modal
   ↓
5. User completes payment
   ↓
6. Frontend calls /subscription/razorpay/verify-payment
   ↓
7. Backend verifies signature & activates subscription
   ↓
8. User becomes PRO member!
```

## API Endpoints

### POST `/api/v1/subscription/razorpay/create-order`

Create a Razorpay order for subscription payment.

**Request:**
```json
{
  "tier": "pro"  // or "premium"
}
```

**Response:**
```json
{
  "success": true,
  "order_id": "order_xxxxxxxxxxxxx",
  "amount": 99900,  // in paise (999 INR)
  "currency": "INR",
  "key_id": "rzp_test_xxxxxxxxxxxxx"
}
```

### POST `/api/v1/subscription/razorpay/verify-payment`

Verify payment and activate subscription.

**Request:**
```json
{
  "razorpay_order_id": "order_xxxxxxxxxxxxx",
  "razorpay_payment_id": "pay_xxxxxxxxxxxxx",
  "razorpay_signature": "xxxxxxxxxxxxxxxxxxxxxx",
  "tier": "pro"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully upgraded to pro",
  "tier": "pro",
  "expires_at": "2026-02-18T00:00:00Z",
  "payment_id": "pay_xxxxxxxxxxxxx"
}
```

## Frontend Integration

### UpgradeModal Component

The modal now has two payment options:

1. **🔐 Pay with Razorpay** (Production)
   - Opens Razorpay Checkout
   - Handles payment completion
   - Verifies and activates subscription

2. **🧪 Test Upgrade** (Development)
   - Bypasses payment
   - Instantly activates subscription
   - For testing only

### Usage Example

```jsx
import UpgradeModal from './components/subscription/UpgradeModal';

const [showUpgrade, setShowUpgrade] = useState(false);

<UpgradeModal 
  isOpen={showUpgrade}
  onClose={() => setShowUpgrade(false)}
  featureName="AI Image Generation"
/>
```

## Pricing

### India (INR)

| Plan | Price | Duration |
|------|-------|----------|
| PRO | ₹999 | Monthly |
| PREMIUM | ₹9,999 | Yearly (Save 17%) |

### Conversion to USD (approx)

| Plan | INR | USD (approx) |
|------|-----|--------------|
| PRO | ₹999 | $12 |
| PREMIUM | ₹9,999 | $120 |

## Security

### Payment Signature Verification

All payments are verified using Razorpay's signature verification:

```python
razorpay_service.verify_payment(
    razorpay_order_id=order_id,
    razorpay_payment_id=payment_id,
    razorpay_signature=signature
)
```

This ensures:
- Payment authenticity
- No tampering with amounts
- Secure transaction completion

### SSL/HTTPS

- Always use HTTPS in production
- Razorpay Checkout is PCI-DSS compliant
- No sensitive card details touch your server

## Testing

### Test Mode

1. Use Test API keys from Razorpay Dashboard
2. Use test cards:
   - **Success**: 4111 1111 1111 1111
   - **Failure**: 4000 0000 0000 0002
   - CVV: Any 3 digits
   - Expiry: Any future date

### Test Flow

```bash
# 1. Create order
curl -X POST http://localhost:8000/api/v1/subscription/razorpay/create-order \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tier": "pro"}'

# 2. Frontend handles Razorpay Checkout

# 3. Verify payment
curl -X POST http://localhost:8000/api/v1/subscription/razorpay/verify-payment \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "razorpay_order_id": "order_xxx",
    "razorpay_payment_id": "pay_xxx",
    "razorpay_signature": "xxx",
    "tier": "pro"
  }'
```

## Webhooks (Optional)

For production, set up Razorpay webhooks to handle:
- Payment failures
- Subscription renewals
- Refunds

Configure at: Dashboard → Settings → Webhooks

Webhook URL: `https://yourdomain.com/api/v1/subscription/razorpay/webhook`

## Error Handling

### Common Errors

1. **Razorpay not configured**
   - Ensure environment variables are set
   - Restart backend server

2. **Invalid signature**
   - Payment tampered or invalid
   - User should retry payment

3. **Payment failed**
   - Card declined or insufficient funds
   - User can retry with different card

### Frontend Error Messages

```javascript
try {
  // Payment logic
} catch (error) {
  if (error.message.includes('signature')) {
    alert('Payment verification failed. Please contact support.');
  } else {
    alert('Payment failed. Please try again.');
  }
}
```

## Going Live

### Checklist

1. ✅ Get Live API keys from Razorpay
2. ✅ Update `.env` with live keys
3. ✅ Enable HTTPS on your domain
4. ✅ Test with real small amount
5. ✅ Set up webhooks for automated handling
6. ✅ Configure email notifications
7. ✅ Add refund policy page
8. ✅ Set up customer support

### Environment Variables (Production)

```bash
RAZORPAY_KEY_ID=rzp_live_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxx
```

## Files Created/Modified

### Backend
- `backend/app/core/config.py` - Added Razorpay config
- `backend/app/services/payment_service.py` - Razorpay service
- `backend/app/api/endpoints/subscription.py` - Payment endpoints
- `backend/requirements.txt` - Added razorpay package

### Frontend
- `frontend/src/components/subscription/UpgradeModal.jsx` - Razorpay integration
- `frontend/src/components/subscription/UpgradeModal.css` - Updated styles

## Support

- **Razorpay Docs**: https://razorpay.com/docs
- **API Reference**: https://razorpay.com/docs/api
- **Test Cards**: https://razorpay.com/docs/payments/payments/test-card-details

---

**Status**: ✅ Fully Integrated
**Version**: 1.0.0
**Last Updated**: January 2026
