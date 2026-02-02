import { useState, useEffect } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const useAdmin = () => {
    const [stats, setStats] = useState(null);
    const [users, setUsers] = useState([]);
    const [subscriptions, setSubscriptions] = useState([]);
    const [recentActivity, setRecentActivity] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const getAuthHeaders = () => {
        const token = localStorage.getItem('token');
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };
    };

    const fetchStats = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE}/admin/stats/overview`, {
                headers: getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error('Failed to fetch stats');
            }

            const data = await response.json();
            setStats(data);
        } catch (err) {
            setError(err.message);
            console.error('Error fetching stats:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchUsers = async (search = '', skip = 0, limit = 50) => {
        setLoading(true);
        try {
            const url = `${API_BASE}/admin/users?search=${search}&skip=${skip}&limit=${limit}`;
            const response = await fetch(url, {
                headers: getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error('Failed to fetch users');
            }

            const data = await response.json();
            setUsers(data);
        } catch (err) {
            setError(err.message);
            console.error('Error fetching users:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchUserDetails = async (userId) => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE}/admin/users/${userId}`, {
                headers: getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error('Failed to fetch user details');
            }

            return await response.json();
        } catch (err) {
            setError(err.message);
            console.error('Error fetching user details:', err);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const fetchSubscriptions = async (tier = '', status = '', skip = 0, limit = 50) => {
        setLoading(true);
        try {
            const params = new URLSearchParams();
            if (tier) params.append('tier', tier);
            if (status) params.append('status', status);
            params.append('skip', skip);
            params.append('limit', limit);

            const response = await fetch(`${API_BASE}/admin/subscriptions?${params}`, {
                headers: getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error('Failed to fetch subscriptions');
            }

            const data = await response.json();
            setSubscriptions(data);
        } catch (err) {
            setError(err.message);
            console.error('Error fetching subscriptions:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchRecentActivity = async (limit = 50) => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE}/admin/activity/recent?limit=${limit}`, {
                headers: getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error('Failed to fetch activity');
            }

            const data = await response.json();
            setRecentActivity(data.recent_activity || []);
        } catch (err) {
            setError(err.message);
            console.error('Error fetching activity:', err);
        } finally {
            setLoading(false);
        }
    };

    const upgradeUser = async (userId, tier) => {
        try {
            const response = await fetch(`${API_BASE}/admin/users/${userId}/upgrade`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({ tier })
            });

            if (!response.ok) {
                throw new Error('Failed to upgrade user');
            }

            return await response.json();
        } catch (err) {
            setError(err.message);
            console.error('Error upgrading user:', err);
            throw err;
        }
    };

    const deleteUser = async (userId) => {
        try {
            const response = await fetch(`${API_BASE}/admin/users/${userId}`, {
                method: 'DELETE',
                headers: getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error('Failed to delete user');
            }

            return await response.json();
        } catch (err) {
            setError(err.message);
            console.error('Error deleting user:', err);
            throw err;
        }
    };

    const updateUser = async (userId, userData) => {
        try {
            const response = await fetch(`${API_BASE}/admin/users/${userId}`, {
                method: 'PUT',
                headers: getAuthHeaders(),
                body: JSON.stringify(userData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to update user');
            }

            return await response.json();
        } catch (err) {
            setError(err.message);
            console.error('Error updating user:', err);
            throw err;
        }
    };

    const resetPassword = async (userId, newPassword) => {
        try {
            const response = await fetch(`${API_BASE}/admin/users/${userId}/reset-password`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({ new_password: newPassword })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to reset password');
            }

            return await response.json();
        } catch (err) {
            setError(err.message);
            console.error('Error resetting password:', err);
            throw err;
        }
    };

    return {
        stats,
        users,
        subscriptions,
        recentActivity,
        loading,
        error,
        fetchStats,
        fetchUsers,
        fetchUserDetails,
        fetchSubscriptions,
        fetchRecentActivity,
        upgradeUser,
        deleteUser,
        updateUser,
        resetPassword
    };
};
