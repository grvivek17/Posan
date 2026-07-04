import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './BadgesDisplay.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const BadgesDisplay = () => {
    const [badges, setBadges] = useState([]);
    const [userBadges, setUserBadges] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedBadge, setSelectedBadge] = useState(null);

    useEffect(() => {
        fetchBadges();
    }, []);

    const fetchBadges = async () => {
        try {
            const token = localStorage.getItem('token');
            const userId = localStorage.getItem('user_id');

            if (!token || !userId) {
                setLoading(false);
                return;
            }

            // Fetch all available badges
            const badgesResponse = await axios.get(`${API_BASE}/gamification/badges`);

            // Fetch user's earned badges
            const userBadgesResponse = await axios.get(
                `${API_BASE}/gamification/achievements/${userId}`
            );

            setBadges(badgesResponse.data || []);
            setUserBadges(userBadgesResponse.data || []);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching badges:', error);
            setBadges([]);
            setUserBadges([]);
            setLoading(false);
        }
    };

    const isBadgeEarned = (badgeId) => {
        return userBadges.some(ub => ub.badge_id === badgeId);
    };

    const getBadgeEarnedDate = (badgeId) => {
        const earned = userBadges.find(ub => ub.badge_id === badgeId);
        return earned ? new Date(earned.earned_at).toLocaleDateString() : null;
    };

    if (loading) {
        return (
            <div className="badges-loading">
                <div className="spinner"></div>
                <p>Loading badges...</p>
            </div>
        );
    }

    return (
        <div className="badges-container">
            <div className="badges-header">
                <h2>🏆 Achievements</h2>
                <div className="badges-count">
                    <span className="earned">{userBadges.length}</span>
                    <span className="separator">/</span>
                    <span className="total">{badges.length}</span>
                </div>
            </div>

            <div className="badges-grid">
                {badges.map((badge) => {
                    const earned = isBadgeEarned(badge.id);
                    const earnedDate = getBadgeEarnedDate(badge.id);

                    return (
                        <div
                            key={badge.id}
                            className={`badge-card ${earned ? 'earned' : 'locked'} ${badge.is_special ? 'special' : ''}`}
                            onClick={() => setSelectedBadge(badge)}
                        >
                            <div className="badge-icon-container">
                                {badge.icon_url ? (
                                    <img src={badge.icon_url} alt={badge.name} className="badge-icon" />
                                ) : (
                                    <span className="badge-emoji">
                                        {earned ? '🏆' : '🔒'}
                                    </span>
                                )}
                                {earned && <div className="badge-shine"></div>}
                                {badge.is_special && <div className="special-glow"></div>}
                            </div>

                            <div className="badge-info">
                                <h3 className="badge-name">{badge.name}</h3>
                                <p className="badge-description">{badge.description}</p>

                                <div className="badge-requirements">
                                    {badge.points_required > 0 && (
                                        <span className="requirement">
                                            ⭐ {badge.points_required} points
                                        </span>
                                    )}
                                    {badge.puzzles_required > 0 && (
                                        <span className="requirement">
                                            🧩 {badge.puzzles_required} puzzles
                                        </span>
                                    )}
                                </div>

                                {earned && earnedDate && (
                                    <div className="earned-date">
                                        Earned on {earnedDate}
                                    </div>
                                )}
                            </div>

                            {earned && (
                                <div className="earned-checkmark">✓</div>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Badge Detail Modal */}
            {selectedBadge && (
                <div className="badge-modal" onClick={() => setSelectedBadge(null)}>
                    <div className="badge-modal-content" onClick={(e) => e.stopPropagation()}>
                        <button className="modal-close" onClick={() => setSelectedBadge(null)}>×</button>

                        <div className="modal-icon">
                            {selectedBadge.icon_url ? (
                                <img src={selectedBadge.icon_url} alt={selectedBadge.name} />
                            ) : (
                                <span className="modal-emoji">
                                    {isBadgeEarned(selectedBadge.id) ? '🏆' : '🔒'}
                                </span>
                            )}
                        </div>

                        <h2>{selectedBadge.name}</h2>
                        <p className="modal-description">{selectedBadge.description}</p>

                        <div className="modal-requirements">
                            <h3>Requirements:</h3>
                            <ul>
                                {selectedBadge.points_required > 0 && (
                                    <li>⭐ Earn {selectedBadge.points_required} points</li>
                                )}
                                {selectedBadge.puzzles_required > 0 && (
                                    <li>🧩 Complete {selectedBadge.puzzles_required} puzzles</li>
                                )}
                            </ul>
                        </div>

                        {isBadgeEarned(selectedBadge.id) ? (
                            <div className="modal-earned">
                                <div className="earned-badge">✓ Earned</div>
                                <p>Earned on {getBadgeEarnedDate(selectedBadge.id)}</p>
                            </div>
                        ) : (
                            <div className="modal-locked">
                                <div className="locked-badge">🔒 Locked</div>
                                <p>Keep going to unlock this badge!</p>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default BadgesDisplay;
