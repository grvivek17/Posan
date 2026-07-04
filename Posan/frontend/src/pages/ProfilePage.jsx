import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './ProfilePage.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

function ProfilePage() {
    const navigate = useNavigate();
    const [username, setUsername] = useState('Explorer');
    const [userLevel, setUserLevel] = useState(1);
    const [levelName, setLevelName] = useState('Super Explorer');
    const [levelIcon, setLevelIcon] = useState(null);
    const [badgesEarned, setBadgesEarned] = useState(0);
    const [activityCounts, setActivityCounts] = useState(null);
    const [totalPoints, setTotalPoints] = useState(0);
    const [showSettings, setShowSettings] = useState(false);
    const [showEditInfo, setShowEditInfo] = useState(false);
    const [loading, setLoading] = useState(true);

    // Settings state - loaded from localStorage
    const [settings, setSettings] = useState(() => {
        const saved = localStorage.getItem('profile_settings');
        if (saved) {
            try {
                return JSON.parse(saved);
            } catch {
                // ignore parse errors
            }
        }
        return {
            notifications: true,
            ageGroup: '8-12',
            theme: 'light',
        };
    });

    const getAuthHeaders = useCallback(() => {
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        return token ? { Authorization: `Bearer ${token}` } : {};
    }, []);

    const getUserId = useCallback(() => {
        return localStorage.getItem('user_id');
    }, []);

    // Fetch gamification stats
    useEffect(() => {
        const fetchStats = async () => {
            const userId = getUserId();
            if (!userId) {
                setLoading(false);
                return;
            }

            try {
                const [statsRes, achievementsRes] = await Promise.allSettled([
                    axios.get(`${API_BASE}/gamification-v2/stats`, {
                        params: { user_id: userId },
                        headers: getAuthHeaders(),
                    }),
                    axios.get(`${API_BASE}/gamification/achievements/${userId}`, {
                        headers: getAuthHeaders(),
                    }),
                ]);

                // Process gamification stats
                if (statsRes.status === 'fulfilled' && statsRes.value.data) {
                    const data = statsRes.value.data;
                    setTotalPoints(data.total_points || 0);

                    if (data.level) {
                        setUserLevel(data.level.level_number || data.level.current_level || 1);
                        setLevelName(data.level.current_level || 'Super Explorer');
                        setLevelIcon(data.level.level_icon || null);
                    }

                    if (data.badges_earned !== undefined) {
                        setBadgesEarned(data.badges_earned);
                    }

                    if (data.activity_counts) {
                        setActivityCounts(data.activity_counts);
                    }
                }

                // Process achievements for badge count (fallback)
                if (achievementsRes.status === 'fulfilled' && achievementsRes.value.data) {
                    const achData = achievementsRes.value.data;
                    const count = Array.isArray(achData)
                        ? achData.length
                        : achData.badges_earned || achData.total || 0;
                    setBadgesEarned((prev) => prev > 0 ? prev : count);
                }
            } catch (error) {
                console.error('Error fetching profile stats:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, [getAuthHeaders, getUserId]);

    // Load username
    useEffect(() => {
        const storedUsername = localStorage.getItem('username');
        if (storedUsername) {
            setUsername(storedUsername);
        }
    }, []);

    // Save settings to localStorage whenever they change
    useEffect(() => {
        localStorage.setItem('profile_settings', JSON.stringify(settings));
    }, [settings]);

    const handleSettingChange = (key, value) => {
        setSettings((prev) => ({ ...prev, [key]: value }));
    };

    // Build activity-based content for "What I Made" section
    const getActivityContent = () => {
        if (!activityCounts) return [];

        const activityMap = [
            { key: 'puzzle_solved', title: 'Puzzles Solved', icon: '🧩', color: '#0B5563' },
            { key: 'article_read', title: 'Articles Read', icon: '📖', color: '#1A2332' },
            { key: 'story_created', title: 'Stories Created', icon: '🌲', color: '#10B981' },
            { key: 'quiz_completed', title: 'Quizzes Done', icon: '🏅', color: '#7C3AED' },
            { key: 'magazine_read', title: 'Magazines Read', icon: '📰', color: '#D97706' },
            { key: 'lesson_completed', title: 'Lessons Done', icon: '📚', color: '#2563EB' },
            { key: 'daily_login', title: 'Daily Logins', icon: '📅', color: '#059669' },
        ];

        return activityMap
            .filter((item) => activityCounts[item.key] && activityCounts[item.key] > 0)
            .map((item, index) => ({
                id: index + 1,
                title: `${activityCounts[item.key]} ${item.title}`,
                icon: item.icon,
                color: item.color,
            }));
    };

    const createdContent = getActivityContent();

    // Fallback content when no activity data is available
    const fallbackContent = [
        { id: 1, title: 'Start Exploring!', icon: '🚀', color: '#0B5563' },
        { id: 2, title: 'Try a Puzzle', icon: '🧩', color: '#1A2332' },
        { id: 3, title: 'Read an Article', icon: '📖', color: '#10B981' },
    ];

    const displayContent = createdContent.length > 0 ? createdContent : fallbackContent;

    return (
        <div className="profile-page-new">
            {/* Header */}
            <div className="profile-header">
                <button className="back-btn" onClick={() => navigate(-1)}>
                    ←
                </button>
                <h1 className="profile-title">My Space</h1>
                <button
                    className="settings-btn"
                    onClick={() => {
                        setShowSettings((prev) => !prev);
                        setShowEditInfo(false);
                    }}
                >
                    ⚙️
                </button>
            </div>

            <div className="container">
                {/* Inline Settings Panel */}
                {showSettings && (
                    <div className="settings-panel" style={{
                        background: 'var(--bg-secondary, #fff)',
                        borderRadius: '16px',
                        padding: '1.5rem',
                        marginBottom: '1.5rem',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                    }}>
                        <div style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            marginBottom: '1.25rem',
                        }}>
                            <h3 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 700 }}>Settings</h3>
                            <button
                                onClick={() => setShowSettings(false)}
                                style={{
                                    background: 'none',
                                    border: 'none',
                                    fontSize: '1.5rem',
                                    cursor: 'pointer',
                                    padding: '0.25rem',
                                }}
                            >
                                ✕
                            </button>
                        </div>

                        {/* Notifications Toggle */}
                        <div style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            padding: '0.75rem 0',
                            borderBottom: '1px solid #eee',
                        }}>
                            <span style={{ fontWeight: 600 }}>Notifications</span>
                            <label style={{
                                position: 'relative',
                                display: 'inline-block',
                                width: '48px',
                                height: '26px',
                            }}>
                                <input
                                    type="checkbox"
                                    checked={settings.notifications}
                                    onChange={(e) => handleSettingChange('notifications', e.target.checked)}
                                    style={{ opacity: 0, width: 0, height: 0 }}
                                />
                                <span style={{
                                    position: 'absolute',
                                    cursor: 'pointer',
                                    top: 0, left: 0, right: 0, bottom: 0,
                                    backgroundColor: settings.notifications ? '#10B981' : '#ccc',
                                    borderRadius: '26px',
                                    transition: '0.3s',
                                }}>
                                    <span style={{
                                        position: 'absolute',
                                        height: '20px',
                                        width: '20px',
                                        left: settings.notifications ? '25px' : '3px',
                                        bottom: '3px',
                                        backgroundColor: 'white',
                                        borderRadius: '50%',
                                        transition: '0.3s',
                                    }} />
                                </span>
                            </label>
                        </div>

                        {/* Age Group Selector */}
                        <div style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            padding: '0.75rem 0',
                            borderBottom: '1px solid #eee',
                        }}>
                            <span style={{ fontWeight: 600 }}>Age Group</span>
                            <select
                                value={settings.ageGroup}
                                onChange={(e) => handleSettingChange('ageGroup', e.target.value)}
                                style={{
                                    padding: '0.4rem 0.75rem',
                                    borderRadius: '8px',
                                    border: '1px solid #ddd',
                                    fontSize: '0.9rem',
                                    cursor: 'pointer',
                                    background: 'white',
                                }}
                            >
                                <option value="4-7">4-7 years</option>
                                <option value="8-12">8-12 years</option>
                                <option value="13-17">13-17 years</option>
                            </select>
                        </div>

                        {/* Theme Preference */}
                        <div style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            padding: '0.75rem 0',
                        }}>
                            <span style={{ fontWeight: 600 }}>Theme</span>
                            <select
                                value={settings.theme}
                                onChange={(e) => handleSettingChange('theme', e.target.value)}
                                style={{
                                    padding: '0.4rem 0.75rem',
                                    borderRadius: '8px',
                                    border: '1px solid #ddd',
                                    fontSize: '0.9rem',
                                    cursor: 'pointer',
                                    background: 'white',
                                }}
                            >
                                <option value="light">Light</option>
                                <option value="dark">Dark</option>
                                <option value="auto">Auto</option>
                            </select>
                        </div>
                    </div>
                )}

                {/* User Profile Card */}
                <div className="user-profile-card">
                    <button
                        className="edit-btn"
                        onClick={() => {
                            setShowEditInfo((prev) => !prev);
                            setShowSettings(false);
                        }}
                    >
                        ✏️
                    </button>
                    <div className="profile-avatar-large">
                        <span className="avatar-icon">👨‍✈️</span>
                        <div className="level-badge">
                            <span className="level-icon">{levelIcon || '⚡'}</span>
                            <span className="level-text">Lvl {userLevel}</span>
                        </div>
                    </div>
                    <h2 className="profile-username">{username}</h2>
                    <p className="profile-role">{levelName}</p>

                    {/* Edit Info Panel (inline under profile card) */}
                    {showEditInfo && (
                        <div style={{
                            marginTop: '1rem',
                            padding: '1rem',
                            background: 'rgba(255,255,255,0.9)',
                            borderRadius: '12px',
                            textAlign: 'left',
                        }}>
                            <p style={{ margin: '0.4rem 0', fontSize: '0.95rem' }}>
                                <strong>Username:</strong> {username}
                            </p>
                            <p style={{ margin: '0.4rem 0', fontSize: '0.95rem' }}>
                                <strong>Level:</strong> {userLevel} - {levelName}
                            </p>
                            <p style={{ margin: '0.4rem 0', fontSize: '0.95rem' }}>
                                <strong>Total Points:</strong> {totalPoints}
                            </p>
                            <p style={{ margin: '0.4rem 0', fontSize: '0.95rem' }}>
                                <strong>Badges Earned:</strong> {badgesEarned}
                            </p>
                        </div>
                    )}
                </div>

                {/* Action Buttons */}
                <div className="action-buttons">
                    <div
                        className="action-card change-look"
                        onClick={() => navigate('/achievements')}
                    >
                        <div className="action-icon">👗</div>
                        <h3>Change Look</h3>
                    </div>
                    <div
                        className="action-card favorites"
                        onClick={() => navigate('/magazines')}
                    >
                        <div className="action-icon">💗</div>
                        <h3>Favorites</h3>
                    </div>
                </div>

                {/* Achievements */}
                <div className="achievements-card" onClick={() => navigate('/achievements')}>
                    <div className="achievements-icon">🏆</div>
                    <h3>My Achievements</h3>
                    {badgesEarned > 0 ? (
                        <span className="achievements-badge">{badgesEarned} Earned</span>
                    ) : (
                        <span className="achievements-badge">View All</span>
                    )}
                </div>

                {/* What I Made */}
                <section className="created-content-section">
                    <div className="section-header-profile">
                        <h2>What I Made</h2>
                        <button className="see-all-btn" onClick={() => navigate('/ai-content')}>
                            See All
                        </button>
                    </div>

                    <div className="created-grid">
                        {displayContent.map((item) => (
                            <div
                                key={item.id}
                                className="created-card"
                                style={{ backgroundColor: item.color }}
                            >
                                <div className="created-icon">{item.icon}</div>
                                <h4 className="created-title">{item.title}</h4>
                                <button className="created-action">✏️</button>
                            </div>
                        ))}
                    </div>
                </section>
            </div>
        </div>
    );
}

export default ProfilePage;
