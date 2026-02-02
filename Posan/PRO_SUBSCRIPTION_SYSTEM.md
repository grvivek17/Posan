# 💎 Pro/Premium Subscription System

## Overview
Complete subscription system with Pro and Premium tiers that gate access to premium features like AI image generation, advanced puzzles, and unlimited content.

## Architecture

### Database Schema

#### Subscription Model
```python
class Subscription:
    - user_id: ForeignKey to User
    - tier: enum (FREE, PRO, PREMIUM)
    - status: enum (ACTIVE, EXPIRED, CANCELLED, TRIAL)
    - started_at, expires_at, cancelled_at
    - payment_provider, payment_id
    - Feature flags:
        * ai_image_generation
        * advanced_puzzles
        * unlimited_content  
        * no_ads
```

## API Endpoints

### GET `/api/v1/subscription/status`
Get current user's subscription status and features.

**Response:**
```json
{
  "tier": "pro",
  "status": "active",
  "is_active": true,
  "features": {
    "ai_image_generation": true,
    "advanced_puzzles": true,
    "unlimited_content": true,
    "no_ads": true
  },
  "expires_at": "2026-02-18T00:00:00Z"
}
```

### POST `/api/v1/subscription/upgrade`
Upgrade to Pro or Premium tier.

**Request:**
```json
{
  "tier": "pro",
  "payment_provider": "stripe",
  "payment_id": "pi_123456"
}
```

### GET `/api/v1/subscription/plans`
Get available subscription plans with pricing.

### GET `/api/v1/subscription/features/{feature}`
Check if user has access to specific feature.

### POST `/api/v1/subscription/cancel`
Cancel current subscription.

## Frontend Components

### 1. ProBadge Component
Visual indicator for pro features.

**Variants:**
- `small`: Compact badge for feature labels
- `large`: Full badge for locked features
- `inline`: Inline badge for buttons

**Usage:**
```jsx
import ProBadge from './components/subscription/ProBadge';

<ProBadge variant="small" showLabel={true} />
```

### 2. UpgradeModal Component
Modal for plan selection and upgrade.

**Usage:**
```jsx
import UpgradeModal from './components/subscription/UpgradeModal';

const [showUpgrade, setShowUpgrade] = useState(false);

<UpgradeModal 
  isOpen={showUpgrade}
  onClose={() => setShowUpgrade(false)}
  featureName="AI Image Generation"
/>
```

## Subscription Tiers

### FREE (Default)
- ❌ No AI Image Generation
- ❌ Limited Puzzles
- ❌ Daily Content Limits (5/day)
- ❌ Ads Enabled

### PRO - $9.99/month
- ✅ AI Image Generation
- ✅ Advanced Puzzles
- ✅ Unlimited Content
- ✅ No Ads

### PREMIUM - $99.99/year (Save 17%)
- ✅ Everything in PRO
- ✅ Exclusive Content
- ✅ Priority Support
- ✅ Early Access to Features

## Feature Gating

### Backend Example
```python
from app.models.subscription import Subscription

def check_feature_access(user_id: int, feature: str):
    subscription = get_user_subscription(user_id)
    if not subscription.has_feature(feature):
        raise HTTPException(403, "Upgrade to Pro to access this feature")
```

### Frontend Example
```jsx
const [subscription, setSubscription] = useState(null);

useEffect(() => {
  fetchSubscriptionStatus();
}, []);

const handleProFeature = () => {
  if (!subscription?.features?.ai_image_generation) {
    setShowUpgradeModal(true);
    return;
  }
  // Execute pro feature
};
```

## Integration Steps

### 1. Update Database
Run migration to create `subscriptions` table.

### 2. Add Pro Badges to Features
```jsx
import ProBadge from './components/subscription/ProBadge';

<button onClick={handleImageGeneration}>
  Generate Image
  {!subscription?.features?.ai_image_generation && (
    <ProBadge variant="inline" />
  )}
</button>
```

### 3. Gate Feature Access
```jsx
const handleFeature = async () => {
  // Check subscription
  const response = await fetch(`${API_BASE}/subscription/features/ai_image_generation`);
  const data = await response.json();
  
  if (!data.has_access) {
    setShowUpgradeModal(true);
    return;
  }
  
  // Execute feature
};
```

## Payment Integration (Future)

### Stripe Integration
```javascript
// In production, integrate with Stripe
import { loadStripe } from '@stripe/stripe-js';

const handleCheckout = async (plan) => {
  const stripe = await loadStripe('pk_live_...');
  const { error } = await stripe.redirectToCheckout({
    lineItems: [{ price: plan.priceId, quantity: 1 }],
    mode: 'subscription',
    successUrl: `${window.location.origin}/success`,
    cancelUrl: `${window.location.origin}/cancel`,
  });
};
```

### Razorpay Integration (India)
```javascript
const handleRazorpay = (plan) => {
  const options = {
    key: 'rzp_live_...',
    amount: plan.price * 100, // in paise
    currency: 'INR',
    name: 'POSAN PRO',
    description: `${plan.tier} Subscription`,
    handler: function(response) {
      upgradeSubscription(plan.tier, 'razorpay', response.razorpay_payment_id);
    }
  };
  
  const rzp = new Razorpay(options);
  rzp.open();
};
```

## File Structure

```
backend/
├── app/
│   ├── models/
│   │   └── subscription.py          # Subscription model
│   └── api/
│       └── endpoints/
│           └── subscription.py      # Subscription API

frontend/
├── src/
│   └── components/
│       └── subscription/
│           ├── ProBadge.jsx         # Pro badge component
│           ├── ProBadge.css
│           ├── UpgradeModal.jsx     # Upgrade modal
│           └── UpgradeModal.css
```

## Testing

### Test Subscription Endpoints
```bash
# Get status
curl -X GET http://localhost:8000/api/v1/subscription/status \
  -H "Authorization: Bearer YOUR_TOKEN"

# Upgrade to Pro
curl -X POST http://localhost:8000/api/v1/subscription/upgrade \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tier": "pro"}'

# Check feature access
curl -X GET http://localhost:8000/api/v1/subscription/features/ai_image_generation \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Best Practices

1. **Feature Gating**: Always check both frontend and backend
2. **User Experience**: Show upgrade prompts, not hard blocks
3. **Clear Value**: Communicate benefits clearly
4. **Trial Periods**: Consider offering trials
5. **Analytics**: Track conversion rates

## Next Steps

1. ✅ Database migration for subscriptions table
2. ✅ Backend API implementation
3. ✅ Frontend components (ProBadge, UpgradeModal)
4. ⏳ Payment provider integration (Stripe/Razorpay)
5. ⏳ Add pro features to existing pages
6. ⏳ Analytics and conversion tracking

---

**Status**: Core system implemented, payment integration pending
**Version**: 1.0.0
**Created**: January 2026
