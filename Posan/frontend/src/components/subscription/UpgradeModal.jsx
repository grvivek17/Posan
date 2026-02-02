import { useState } from 'react';
import ProBadge from './ProBadge';
import './UpgradeModal.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const UpgradeModal = ({ isOpen, onClose, featureName = "this feature" }) => {
    const [selectedPlan, setSelectedPlan] = useState('pro');
    const [isProcessing, setIsProcessing] = useState(false);

    if (!isOpen) return null;

    const loadRazorpayScript = () => {
        return new Promise((resolve) => {
            const script = document.createElement('script');
            script.src = 'https://checkout.razorpay.com/v1/checkout.js';
            script.onload = () => resolve(true);
            script.onerror = () => resolve(false);
            document.body.appendChild(script);
        });
    };

    const handleRazorpayPayment = async () => {
        setIsProcessing(true);

        try {
            // Load Razorpay script
            const scriptLoaded = await loadRazorpayScript();
            if (!scriptLoaded) {
                alert('Failed to load Razorpay. Please check your internet connection.');
                setIsProcessing(false);
                return;
            }

            // Create order
            const token = localStorage.getItem('token');
            const orderResponse = await fetch(`${API_BASE}/subscription/razorpay/create-order`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ tier: selectedPlan })
            });

            const orderData = await orderResponse.json();

            if (!orderData.success) {
                throw new Error('Failed to create order');
            }

            // Razorpay options
            const options = {
                key: orderData.key_id,
                amount: orderData.amount,
                currency: orderData.currency,
                name: 'POSAN Pro',
                description: `${selectedPlan.toUpperCase()} Subscription`,
                order_id: orderData.order_id,
                handler: async function (response) {
                    // Verify payment
                    try {
                        const verifyResponse = await fetch(`${API_BASE}/subscription/razorpay/verify-payment`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'Authorization': `Bearer ${token}`
                            },
                            body: JSON.stringify({
                                razorpay_order_id: response.razorpay_order_id,
                                razorpay_payment_id: response.razorpay_payment_id,
                                razorpay_signature: response.razorpay_signature,
                                tier: selectedPlan
                            })
                        });

                        const verifyData = await verifyResponse.json();

                        if (verifyData.success) {
                            alert('🎉 Payment successful! You are now a PRO member!');
                            window.location.reload();
                        } else {
                            alert('Payment verification failed. Please contact support.');
                        }
                    } catch (error) {
                        console.error('Verification error:', error);
                        alert('Payment verification failed. Please contact support.');
                    }
                },
                prefill: {
                    email: localStorage.getItem('email') || '',
                    contact: ''
                },
                theme: {
                    color: '#667eea'
                },
                modal: {
                    ondismiss: function () {
                        setIsProcessing(false);
                    }
                }
            };

            const razorpay = new window.Razorpay(options);
            razorpay.open();

        } catch (error) {
            console.error('Payment error:', error);
            alert('Failed to initiate payment. Please try again.');
        } finally {
            setIsProcessing(false);
        }
    };

    const handleTestUpgrade = async () => {
        // Test mode (for development without Razorpay)
        setIsProcessing(true);

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_BASE}/subscription/upgrade`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    tier: selectedPlan,
                    payment_provider: 'test',
                    payment_id: `test_${Date.now()}`
                })
            });

            if (response.ok) {
                const data = await response.json();
                console.log('✅ Upgrade successful:', data);
                alert('✅ Successfully upgraded in TEST mode! Refresh the page.');
                window.location.reload();
            } else {
                const errorData = await response.json();
                console.error('❌ Upgrade failed:', errorData);

                // Extract error message
                const errorMessage = typeof errorData.detail === 'string'
                    ? errorData.detail
                    : JSON.stringify(errorData.detail || errorData);

                alert(`Upgrade failed: ${errorMessage}`);
            }
        } catch (error) {
            console.error('Upgrade error:', error);
            alert(`Error during upgrade: ${error.message || 'Please try again.'}`);
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <div className="upgrade-modal-overlay" onClick={onClose}>
            <div className="upgrade-modal" onClick={(e) => e.stopPropagation()}>
                <button className="close-modal-btn" onClick={onClose}>×</button>

                <div className="modal-header">
                    <ProBadge variant="large" showLabel={false} />
                    <h2>Unlock {featureName}</h2>
                    <p>Upgrade to PRO to access premium features!</p>
                </div>

                <div className="plans-container">
                    {/* Pro Plan */}
                    <div
                        className={`plan-card ${selectedPlan === 'pro' ? 'selected' : ''}`}
                        onClick={() => setSelectedPlan('pro')}
                    >
                        <div className="plan-badge">POPULAR</div>
                        <h3>PRO</h3>
                        <div className="plan-price">
                            <span className="price">₹99</span>
                            <span className="period">/month</span>
                        </div>
                        <ul className="plan-features">
                            <li>✨ AI Image Generation</li>
                            <li>🧩 Advanced Puzzles</li>
                            <li>📚 Unlimited Content</li>
                            <li>🚫 No Ads</li>
                        </ul>
                    </div>

                    {/* Premium Plan */}
                    <div
                        className={`plan-card ${selectedPlan === 'premium' ? 'selected' : ''}`}
                        onClick={() => setSelectedPlan('premium')}
                    >
                        <div className="plan-badge best-value">BEST VALUE</div>
                        <h3>PREMIUM</h3>
                        <div className="plan-price">
                            <span className="price">₹999</span>
                            <span className="period">/year</span>
                        </div>
                        <div className="savings">Save 92%</div>
                        <ul className="plan-features">
                            <li>✨ AI Image Generation</li>
                            <li>🧩 Advanced Puzzles</li>
                            <li>📚 Unlimited Content</li>
                            <li>🚫 No Ads</li>
                            <li>🎁 Exclusive Content</li>
                            <li>⭐ Priority Support</li>
                        </ul>
                    </div>
                </div>

                <div className="payment-buttons">
                    <button
                        className="upgrade-btn primary"
                        onClick={handleRazorpayPayment}
                        disabled={isProcessing}
                    >
                        {isProcessing ? '⏳ Processing...' : `🔐 Pay with Razorpay`}
                    </button>

                    <button
                        className="upgrade-btn secondary"
                        onClick={handleTestUpgrade}
                        disabled={isProcessing}
                    >
                        {isProcessing ? '⏳ Processing...' : `🧪 Test Upgrade (Dev Only)`}
                    </button>
                </div>

                <p className="terms-text">
                    Secure payment powered by Razorpay
                </p>
            </div>
        </div>
    );
};

export default UpgradeModal;
