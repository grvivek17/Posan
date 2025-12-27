import React from 'react';
import { Link } from 'react-router-dom';
import './Home.css';

function Home() {
    return (
        <div className="home">
            <section className="hero">
                <div className="container">
                    <div className="hero-content animate-fade-in">
                        <h1 className="hero-title">Welcome to POSAN! 🎨</h1>
                        <p className="hero-subtitle">
                            Your magical world of stories, puzzles, and adventures!
                        </p>
                        <div className="hero-buttons">
                            <Link to="/register" className="btn btn-primary btn-large">
                                Start Your Adventure! 🚀
                            </Link>
                            <Link to="/login" className="btn btn-secondary btn-large">
                                Login
                            </Link>
                        </div>
                    </div>
                </div>
            </section>

            <section className="features">
                <div className="container">
                    <h2 className="section-title text-center">What's Inside?</h2>

                    <div className="features-grid">
                        <div className="feature-card card animate-scale-in">
                            <div className="feature-icon">📚</div>
                            <h3>Digital Magazines</h3>
                            <p>Read amazing stories, comics, and articles with beautiful illustrations!</p>
                        </div>

                        <div className="feature-card card animate-scale-in">
                            <div className="feature-icon">🧩</div>
                            <h3>Fun Puzzles</h3>
                            <p>Challenge yourself with word searches, crosswords, jigsaws, and sudoku!</p>
                        </div>

                        <div className="feature-card card animate-scale-in">
                            <div className="feature-icon">🏆</div>
                            <h3>Earn Rewards</h3>
                            <p>Collect points, unlock badges, and climb the leaderboard!</p>
                        </div>

                        <div className="feature-card card animate-scale-in">
                            <div className="feature-icon">🎧</div>
                            <h3>Audio Stories</h3>
                            <p>Listen to stories being read aloud - perfect for bedtime!</p>
                        </div>
                    </div>
                </div>
            </section>

            <section className="cta">
                <div className="container">
                    <div className="cta-content">
                        <h2>Ready to Start Learning and Having Fun?</h2>
                        <Link to="/register" className="btn btn-accent btn-large">
                            Join POSAN Today! 🌟
                        </Link>
                    </div>
                </div>
            </section>
        </div>
    );
}

export default Home;
