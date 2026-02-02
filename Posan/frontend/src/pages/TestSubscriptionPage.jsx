import React, { useState, useEffect } from 'react';
import { useSubscription } from '../hooks/useSubscription';
import ProBadge from '../components/subscription/ProBadge';
import UpgradeModal from '../components/subscription/UpgradeModal';
import './TestSubscriptionPage.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const TestSubscriptionPage = () => {
    const { subscription, loading, error, hasFeature, isPro, refresh } = useSubscription();
    const [showUpgradeModal, setShowUpgradeModal] = useState(false);
    const [debugInfo, setDebugInfo] = useState(null);

    useEffect(() => {
        // Get debug info
        const token = localStorage.getItem('token');
        setDebugInfo({
            hasToken: !!token,
            token: token ? `${token.substring(0, 20)}...` : 'none',
            apiBase: API_BASE
        });
    }, []);

    const handleTestUpgrade = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_BASE}/subscription/upgrade`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    tier: 'pro'
                })
            });

            if (response.ok) {
                alert('✅ Upgraded to Pro!');
                refresh();
            } else {
                const data = await response.json();
                alert(`❌ Error: ${data.detail}`);
            }
        } catch (err) {
            alert(`❌ Error: ${err.message}`);
        }
    };

    return (
        <div className="test-subscription-page">
            <h1>🧪 Subscription Test Page</h1>

            <div className="debug-section">
                <h2>Debug Information</h2>
                <div className="debug-box">
                    <p><strong>API Base:</strong> {debugInfo?.apiBase}</p>
                    <p><strong>Has Token:</strong> {debugInfo?.hasToken ? '✅ Yes' : '❌ No'}</p>
                    {debugInfo?.hasToken && (
                        <p><strong>Token:</strong> <code>{debugInfo?.token}</code></p>
                    )}
                    <p><strong>Loading:</strong> {loading ? '⏳ Yes' : '✅ No'}</p>
                    <p><strong>Error:</strong> {error || '✅ None'}</p>
                </div>
            </div>

            <div className="subscription-section">
                <h2>Subscription Status</h2>
                {loading && <p>⏳ Loading subscription data...</p>}
                {error && <p className="error">❌ Error: {error}</p>}

                {subscription ? (
                    <div className="subscription-box">
                        <p><strong>Tier:</strong> {subscription.tier} <ProBadge variant="inline" /></p>
                        <p><strong>Status:</strong> {subscription.status}</p>
                        <p><strong>Is Active:</strong> {subscription.is_active ? '✅ Yes' : '❌ No'}</p>
                        <p><strong>Is Pro:</strong> {isPro() ? '✅ Yes' : '❌ No'}</p>
                        {subscription.expires_at && (
                            <p><strong>Expires:</strong> {new Date(subscription.expires_at).toLocaleDateString()}</p>
                        )}

                        <h3>Features:</h3>
                        <ul>
                            <li>AI Image Generation: {hasFeature('ai_image_generation') ? '✅' : '❌'}</li>
                            <li>Advanced Puzzles: {hasFeature('advanced_puzzles') ? '✅' : '❌'}</li>
                            <li>Unlimited Content: {hasFeature('unlimited_content') ? '✅' : '❌'}</li>
                            <li>No Ads: {hasFeature('no_ads') ? '✅' : '❌'}</li>
                        </ul>
                    </div>
                ) : (
                    !loading && <p>No subscription data loaded yet</p>
                )}
            </div>

            <div className="actions-section">
                <h2>Actions</h2>
                <button onClick={refresh} className="btn-primary">
                    🔄 Refresh Subscription
                </button>
                <button onClick={handleTestUpgrade} className="btn-success">
                    ⬆️ Test Upgrade to Pro
                </button>
                <button onClick={() => setShowUpgradeModal(true)} className="btn-info">
                    💎 Show Upgrade Modal
                </button>
            </div>

            <div className="raw-data-section">
                <h2>Raw Subscription Data</h2>
                <pre>{JSON.stringify(subscription, null, 2)}</pre>
            </div>

            <UpgradeModal
                isOpen={showUpgradeModal}
                onClose={() => setShowUpgradeModal(false)}
                featureName="Pro Features"
            />
        </div>
    );
};

export default TestSubscriptionPage;
