import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './PointsDisplay.css';

const PointsDisplay = ({ compact = false }) => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchStats();
        const interval = setInterval(fetchStats, 30000);
        return () => clearInterval(interval);
    }, []);

    const fetchStats = async () => {
        try {
            const token = localStorage.getItem('token');
            const userId = localStorage.getItem('user_id');

            if (!token || !userId) {
                setError('Please login');
                setLoading(false);
                return;
            }

            const response = await axios.get('http://localhost:8000/api/v1/gamification-v2/stats', {
                params: { user_id: parseInt(userId) },
                headers: { Authorization: `Bearer ${token}` }
            });

            setStats(response.data);
            setError(null);
            setLoading(false);
        } catch (err) {
            console.error('Error fetching stats:', err);
            setError(err.message);
            setLoading(false);
        }
    };

    if (loading) {
        return compact ? (
            <div className="points-display-compact">
                <span className="points-loading">...</span>
            </div>
        ) : <div>Loading...</div>;
    }

    if (error || !stats) {
        return compact ? (
            <div className="points-display-compact">
                <span className="points-value">0</span>
                <span className="points-label">pts</span>
            </div>
        ) : <div>Error loading stats</div>;
    }

    const { total_points = 0, level = {}, badges_earned = 0, activity_counts = {} } = stats;
    const {
        current_level = 'Bronze',
        level_icon = '🥉',
        level_number = 1,
        progress_percentage = 0,
        points_to_next_level = 100,
        next_level = 'Silver'
    } = level;

    if (compact) {
        return (
            <div className="points-display-compact">
                <span className="level-icon">{level_icon}</span>
                <span className="points-value">{total_points}</span>
                <span className="points-label">pts</span>
            </div>
        );
    }

    return (
        <div className="points-display-full">
            <div className="points-header">
                <div className="level-badge">
                    <span className="level-icon-large">{level_icon}</span>
                    <div className="level-info">
                        <span className="level-name">{current_level}</span>
                        <span className="level-subtitle">Level {level_number}</span>
                    </div>
                </div>
                <div className="points-total">
                    <span className="points-number">{total_points}</span>
                    <span className="points-text">Points</span>
                </div>
            </div>

            <div className="progress-section">
                <div className="progress-header">
                    <span className="progress-label">
                        {points_to_next_level > 0 ? `${points_to_next_level} to ${next_level}` : 'Max Level!'}
                    </span>
                    <span className="progress-percentage">{progress_percentage}%</span>
                </div>
                <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${progress_percentage}%` }}>
                        <div className="progress-shine"></div>
                    </div>
                </div>
            </div>

            <div className="stats-grid">
                <div className="stat-item">
                    <span className="stat-icon">🧩</span>
                    <span className="stat-value">{activity_counts.puzzle_solved || 0}</span>
                    <span className="stat-label">Puzzles</span>
                </div>
                <div className="stat-item">
                    <span className="stat-icon">📚</span>
                    <span className="stat-value">{activity_counts.article_read || 0}</span>
                    <span className="stat-label">Articles</span>
                </div>
                <div className="stat-item">
                    <span className="stat-icon">🏆</span>
                    <span className="stat-value">{badges_earned}</span>
                    <span className="stat-label">Badges</span>
                </div>
            </div>
        </div>
    );
};

export default PointsDisplay;
