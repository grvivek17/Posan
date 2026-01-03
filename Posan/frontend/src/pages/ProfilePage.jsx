import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './ProfilePage.css';

function ProfilePage() {
    const navigate = useNavigate();
    const [username, setUsername] = useState('CaptainCool123');
    const [userLevel, setUserLevel] = useState(5);

    useEffect(() => {
        const storedUsername = localStorage.getItem('username');
        if (storedUsername) {
            setUsername(storedUsername);
        }
    }, []);

    const createdContent = [
        {
            id: 1,
            title: 'My Dragon',
            icon: '🐉',
            color: '#0B5563'
        },
        {
            id: 2,
            title: 'Space Puzzle',
            icon: '🪐',
            color: '#1A2332'
        },
        {
            id: 3,
            title: 'Magic Forest',
            icon: '🌲',
            color: '#10B981'
        }
    ];

    return (
        <div className="profile-page-new">
            {/* Header */}
            <div className="profile-header">
                <button className="back-btn" onClick={() => navigate(-1)}>
                    ←
                </button>
                <h1 className="profile-title">My Space</h1>
                <button className="settings-btn" onClick={() => alert('Settings coming soon!')}>
                    ⚙️
                </button>
            </div>

            <div className="container">
                {/* User Profile Card */}
                <div className="user-profile-card">
                    <button className="edit-btn">✏️</button>
                    <div className="profile-avatar-large">
                        <span className="avatar-icon">👨‍✈️</span>
                        <div className="level-badge">
                            <span className="level-icon">⚡</span>
                            <span className="level-text">Lvl {userLevel}</span>
                        </div>
                    </div>
                    <h2 className="profile-username">{username}</h2>
                    <p className="profile-role">Super Explorer</p>
                </div>

                {/* Action Buttons */}
                <div className="action-buttons">
                    <div className="action-card change-look">
                        <div className="action-icon">👗</div>
                        <h3>Change Look</h3>
                    </div>
                    <div className="action-card favorites">
                        <div className="action-icon">💗</div>
                        <h3>Favorites</h3>
                    </div>
                </div>

                {/* Achievements */}
                <div className="achievements-card">
                    <div className="achievements-icon">🏆</div>
                    <h3>My Achievements</h3>
                    <span className="achievements-badge">12 New!</span>
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
                        {createdContent.map((item) => (
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
