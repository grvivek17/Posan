import React, { useEffect, useState } from 'react';
import PointsDisplay from '../components/common/PointsDisplay';
import BadgesDisplay from '../components/common/BadgesDisplay';
import GamificationService from '../services/gamificationService';
import './GamificationPage.css';

const GamificationPage = () => {
    const [activityPoints, setActivityPoints] = useState([]);
    const [levels, setLevels] = useState([]);
    const [streak, setStreak] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const userId = localStorage.getItem('user_id');
            if (!userId) {
                setError('Please login to view achievements');
                setLoading(false);
                return;
            }

            const [pointsData, levelsData, streakData] = await Promise.all([
                GamificationService.getActivityPoints(),
                GamificationService.getAllLevels(),
                GamificationService.getDailyStreak()
            ]);

            setActivityPoints(pointsData || []);
            setLevels(levelsData || []);
            setStreak(streakData);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching gamification data:', error);
            setError('Failed to load achievements. Please try again.');
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="gamification-page">
                <div className="gamification-loading">
                    <div className="spinner"></div>
                    <p>Loading your achievements...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="gamification-page">
                <div className="gamification-container">
                    <div style={{
                        background: '#fee',
                        padding: '20px',
                        borderRadius: '8px',
                        margin: '20px',
                        textAlign: 'center'
                    }}>
                        <h2>⚠️ {error}</h2>
                        <button
                            onClick={() => window.location.reload()}
                            style={{
                                padding: '10px 20px',
                                background: '#667eea',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                marginTop: '10px'
                            }}
                        >
                            Retry
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="gamification-page">
            <div className="gamification-container">
                <header className="gamification-header">
                    <h1>🎮 Your Progress</h1>
                    <p className="subtitle">Track your achievements and level up!</p>
                </header>

                {/* Points and Level Display */}
                <section className="points-section">
                    <PointsDisplay />
                </section>

                {/* Daily Streak */}
                {streak && streak.streak > 0 && (
                    <section className="streak-section">
                        <div className="streak-card">
                            <div className="streak-icon">🔥</div>
                            <div className="streak-info">
                                <h3>{streak.streak} Day Streak!</h3>
                                <p>{streak.message}</p>
                            </div>
                        </div>
                    </section>
                )}

                {/* How to Earn Points */}
                <section className="earn-points-section">
                    <h2>💰 How to Earn Points</h2>
                    <div className="activities-grid">
                        {activityPoints.map((activity, index) => (
                            <div key={index} className="activity-card">
                                <div className="activity-icon">
                                    {getActivityIcon(activity.activity_type)}
                                </div>
                                <div className="activity-info">
                                    <h4>{activity.description}</h4>
                                    <div className="activity-points">
                                        <span className="points-value">+{activity.points}</span>
                                        <span className="points-label">points</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

                {/* Level System */}
                <section className="levels-section">
                    <h2>🏅 Level System</h2>
                    <div className="levels-grid">
                        {levels.map((level, index) => {
                            const minPoints = level.min_points ?? 0;
                            const maxPoints = level.max_points;

                            return (
                                <div key={index} className="level-card">
                                    <div className="level-icon-large">{level.icon || '🏅'}</div>
                                    <h3>{level.name || 'Level'}</h3>
                                    <p className="level-range">
                                        {minPoints === 0 ? '0' : minPoints.toLocaleString()}
                                        {' - '}
                                        {maxPoints === null || maxPoints === undefined || maxPoints === Infinity
                                            ? '∞'
                                            : maxPoints.toLocaleString()}
                                        {' points'}
                                    </p>
                                </div>
                            );
                        })}
                    </div>
                </section>

                {/* Badges */}
                <section className="badges-section">
                    <BadgesDisplay />
                </section>

                {/* Tips */}
                <section className="tips-section">
                    <h2>💡 Pro Tips</h2>
                    <div className="tips-grid">
                        <div className="tip-card">
                            <div className="tip-icon">🎯</div>
                            <h4>Stay Consistent</h4>
                            <p>Log in daily to maintain your streak and earn bonus points!</p>
                        </div>
                        <div className="tip-card">
                            <div className="tip-icon">🧩</div>
                            <h4>Complete Puzzles</h4>
                            <p>Puzzles give the most points. Challenge yourself daily!</p>
                        </div>
                        <div className="tip-card">
                            <div className="tip-icon">📚</div>
                            <h4>Read Articles</h4>
                            <p>Learn something new and earn points at the same time!</p>
                        </div>
                        <div className="tip-card">
                            <div className="tip-icon">🏆</div>
                            <h4>Collect Badges</h4>
                            <p>Complete challenges to unlock special badges and achievements!</p>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    );
};

// Helper function to get activity icons
const getActivityIcon = (activityType) => {
    const icons = {
        puzzle_solved: '🧩',
        article_read: '📚',
        comment_posted: '💬',
        content_shared: '🔗',
        quiz_completed: '📝',
        daily_login: '📅',
        profile_completed: '👤',
        homework_uploaded: '📤',
        study_plan_created: '📋'
    };
    return icons[activityType] || '⭐';
};

export default GamificationPage;
