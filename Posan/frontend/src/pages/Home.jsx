import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Home.css';

function Home() {
    const [username, setUsername] = useState('Explorer');
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('access_token');
        const storedUsername = localStorage.getItem('username');

        setIsAuthenticated(!!token);
        if (storedUsername) {
            setUsername(storedUsername);
        }
    }, []);

    const featuredContent = [
        {
            id: 1,
            title: "Space Adventure",
            subtitle: "Issue #42 · Science",
            image: "🚀",
            tag: "NEW",
            color: "#1A2332"
        },
        {
            id: 2,
            title: "Dino World",
            subtitle: "Issue #41 · History",
            image: "🦕",
            tag: "",
            color: "#0B5563"
        },
        {
            id: 3,
            title: "Ocean Mysteries",
            subtitle: "Issue #40 · Nature",
            image: "🌊",
            tag: "",
            color: "#4ECDC4"
        }
    ];

    const categories = ['All', 'Animals', 'Science', 'History', 'Space'];
    const [activeCategory, setActiveCategory] = useState('All');

    return (
        <div className="home">
            {/* Greeting Section */}
            <section className="greeting-section">
                <div className="container">
                    <div className="greeting-header">
                        <div className="greeting-info">
                            <div className="avatar">👋</div>
                            <div>
                                <h1 className="greeting-title">Hi, {username}! 👋</h1>
                                <p className="greeting-subtitle">Ready to explore?</p>
                            </div>
                        </div>
                        <div className="points-badge">
                            <span className="star-icon">⭐</span>
                            <span className="points">150 pts</span>
                        </div>
                    </div>

                    {/* Magic Story Maker Banner */}
                    <div className="magic-story-banner">
                        <div className="banner-content">
                            <span className="new-badge">NEW!</span>
                            <h2 className="banner-title">Magic Story Maker ✨</h2>
                            <p className="banner-subtitle">Create your own adventure!</p>
                        </div>
                        <button className="menu-icon" onClick={() => navigate('/ai-content')}>
                            <span className="icon-bars">☰</span>
                        </button>
                    </div>
                </div>
            </section>

            {/* Fresh Off the Press */}
            <section className="featured-section">
                <div className="container">
                    <div className="section-header">
                        <h2 className="section-title">Fresh Off the Press 📰</h2>
                        <Link to="/magazines" className="see-all-link">See All</Link>
                    </div>

                    <div className="featured-cards">
                        {featuredContent.map((item) => (
                            <div
                                key={item.id}
                                className="featured-card"
                                style={{ backgroundColor: item.color }}
                                onClick={() => navigate('/magazines')}
                            >
                                {item.tag && <span className="card-tag">{item.tag}</span>}
                                <div className="card-icon">{item.image}</div>
                                <h3 className="card-title">{item.title}</h3>
                                <p className="card-subtitle">{item.subtitle}</p>
                            </div>
                        ))}
                    </div>

                    {/* Category Filters */}
                    <div className="category-filters">
                        {categories.map((category) => (
                            <button
                                key={category}
                                className={`filter-btn ${activeCategory === category ? 'active' : ''}`}
                                onClick={() => setActiveCategory(category)}
                            >
                                {category}
                            </button>
                        ))}
                    </div>
                </div>
            </section>

            {/* What do you want to do? */}
            <section className="activities-section">
                <div className="container">
                    <h2 className="section-title">What do you want to do? 🎮</h2>

                    <div className="activities-grid">
                        <div className="activity-card purple-gradient" onClick={() => navigate('/puzzles')}>
                            <div className="activity-icon">🧩</div>
                            <h3 className="activity-title">Puzzles</h3>
                        </div>

                        <div className="activity-card blue-gradient" onClick={() => navigate('/homework')}>
                            <div className="activity-icon">📚</div>
                            <h3 className="activity-title">Homework</h3>
                        </div>

                        <div className="activity-card orange-gradient" onClick={() => navigate('/ai-content')}>
                            <div className="activity-icon">😄</div>
                            <h3 className="activity-title">Jokes</h3>
                        </div>

                        <div className="activity-card pink-gradient" onClick={() => navigate('/puzzle-zone')}>
                            <div className="activity-icon">🎮</div>
                            <h3 className="activity-title">Games</h3>
                        </div>
                    </div>

                    {!isAuthenticated && (
                        <div className="cta-section">
                            <div className="cta-content">
                                <h2>Ready to start your adventure?</h2>
                                <div className="cta-buttons">
                                    <Link to="/register" className="btn btn-primary btn-large">
                                        Join POSAN! 🌟
                                    </Link>
                                    <Link to="/login" className="btn btn-secondary btn-large">
                                        Login
                                    </Link>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </section>
        </div>
    );
}

export default Home;
