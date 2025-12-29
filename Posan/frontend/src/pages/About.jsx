import React from 'react';
import './About.css';

function About() {
    return (
        <div className="about-page">
            <div className="about-container">
                <div className="about-header">
                    <h1 className="about-title">About POSAN</h1>
                    <div className="title-underline"></div>
                </div>

                <div className="about-content">
                    <section className="about-section intro-section">
                        <div className="section-icon">🌟</div>
                        <h2>Welcome to POSAN</h2>
                        <p className="intro-text">
                            POSAN is an interactive educational platform designed to make learning
                            fun and engaging for kids through magazines, puzzles, and AI-powered content.
                        </p>
                    </section>

                    <section className="about-section creator-section">
                        <div className="creator-card">
                            <div className="creator-icon">👧</div>
                            <h2>Created By</h2>
                            <div className="creator-info">
                                <h3 className="creator-name">Poshika V</h3>
                                <p className="creator-details">
                                    <span className="detail-icon">🎓</span>
                                    Currently studying in 3rd Standard
                                </p>
                                <p className="creator-details">
                                    <span className="detail-icon">🏫</span>
                                    KRM Public School
                                </p>
                            </div>
                        </div>
                    </section>

                    <section className="about-section features-section">
                        <h2>What We Offer</h2>
                        <div className="features-grid">
                            <div className="feature-card">
                                <div className="feature-icon">📚</div>
                                <h3>Magazines</h3>
                                <p>Interactive digital magazines with engaging stories and articles</p>
                            </div>
                            <div className="feature-card">
                                <div className="feature-icon">🧩</div>
                                <h3>Puzzles</h3>
                                <p>Fun puzzles including crosswords, word searches, and more</p>
                            </div>
                            <div className="feature-card">
                                <div className="feature-icon">🤖</div>
                                <h3>AI Content</h3>
                                <p>AI-generated stories, quizzes, and educational content</p>
                            </div>
                            <div className="feature-card">
                                <div className="feature-icon">🏆</div>
                                <h3>Gamification</h3>
                                <p>Earn points, badges, and climb the leaderboard</p>
                            </div>
                        </div>
                    </section>

                    <section className="about-section contact-section">
                        <div className="contact-card">
                            <div className="contact-icon">📧</div>
                            <h2>Get in Touch</h2>
                            <p className="contact-text">
                                Have questions or suggestions? We'd love to hear from you!
                            </p>
                            <a
                                href="mailto:rvposhika26@gmail.com"
                                className="contact-email"
                            >
                                rvposhika26@gmail.com
                            </a>
                            <p className="contact-subtext">
                                Feel free to reach out for any questions, feedback, or collaboration opportunities.
                            </p>
                        </div>
                    </section>
                </div>

                <div className="about-footer">
                    <p>✨ Making learning fun, one puzzle at a time! ✨</p>
                </div>
            </div>
        </div>
    );
}

export default About;
