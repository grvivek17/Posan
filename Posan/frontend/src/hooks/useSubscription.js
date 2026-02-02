import { useState, useEffect } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const useSubscription = () => {
    const [subscription, setSubscription] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchSubscription = async () => {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                setLoading(false);
                return;
            }

            const response = await fetch(`${API_BASE}/subscription/status`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                setSubscription(data);
            } else {
                setError('Failed to fetch subscription');
            }
        } catch (err) {
            console.error('Subscription fetch error:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchSubscription();
    }, []);

    const hasFeature = (featureName) => {
        if (!subscription || !subscription.is_active) {
            return false;
        }
        return subscription.features?.[featureName] === true;
    };

    const isPro = () => {
        return subscription?.tier === 'pro' || subscription?.tier === 'premium';
    };

    const refresh = () => {
        fetchSubscription();
    };

    return {
        subscription,
        loading,
        error,
        hasFeature,
        isPro,
        refresh
    };
};
