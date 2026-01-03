import React, { useState } from 'react';
import './About.css';

function About() {
    const [selectedImage, setSelectedImage] = useState(null);

    const galleryItems = [
        {
            id: 1,
            image: '/gallery/ai-teacher-drawing.jpg',
            title: 'AI is my Teacher',
            artist: 'Poshika V',
            description: 'A beautiful illustration showing how AI can be a helpful teacher, teaching students math and making learning fun! The drawing features a friendly robot teacher on a screen, explaining math equations (1+2=3) to happy students sitting at their desks.',
            date: 'December 2025'
        },
        {
            id: 2,
            image: '/gallery/new-year-2026.jpg',
            title: 'Happy New Year 2026',
            artist: 'Poshika V',
            description: 'A vibrant and colorful New Year greeting card featuring purple flowers, decorative hearts, and an inspiring message: "Happy New Year! May this new year all your dreams turn into reality and all your efforts into great achievements." Created with love and creativity.',
            date: 'January 2026'
        },
        {
            id: 3,
            image: '/gallery/healthy-burger-project.jpg',
            title: 'How to Make a Healthy Burger and Sandwich',
            artist: 'Poshika V',
            description: 'An educational project showcasing the process of making healthy burgers and sandwiches. Features colorful diagrams showing the ingredients, cooking process, and final output. Complete with decorative stars and a creative layout demonstrating culinary skills and presentation.',
            date: 'January 2026'
        }
    ];

    const openModal = (item) => {
        setSelectedImage(item);
    };

    const closeModal = () => {
        setSelectedImage(null);
    };

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
                            <h2>Created By</h2>
                            <div className="creator-info">
                                <h3 className="creator-name">Poshika V</h3>
                                <div className="creator-photo-wrapper">
                                    <img
                                        src="/poshika-photo.jpg"
                                        alt="Poshika V"
                                        className="creator-photo"
                                    />
                                </div>
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

                    <section className="about-section gallery-section">
                        <div className="section-icon">🎨</div>
                        <h2>Gallery Collection</h2>
                        <p className="gallery-intro">
                            Click on any artwork to view it in detail!
                        </p>
                        <div className="gallery-grid">
                            {galleryItems.map((item) => (
                                <div
                                    key={item.id}
                                    className="gallery-thumbnail"
                                    onClick={() => openModal(item)}
                                >
                                    <div className="thumbnail-wrapper">
                                        <img
                                            src={item.image}
                                            alt={item.title}
                                            className="thumbnail-image"
                                        />
                                        <div className="thumbnail-overlay">
                                            <span className="view-icon">👁️ View</span>
                                        </div>
                                    </div>
                                    <div className="thumbnail-info">
                                        <h4>{item.title}</h4>
                                        <p>{item.artist}</p>
                                    </div>
                                </div>
                            ))}
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

                    {/* Modal for expanded view */}
                    {selectedImage && (
                        <div className="gallery-modal" onClick={closeModal}>
                            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                                <button className="modal-close" onClick={closeModal}>✕</button>
                                <div className="modal-image-container">
                                    <img
                                        src={selectedImage.image}
                                        alt={selectedImage.title}
                                        className="modal-image"
                                    />
                                </div>
                                <div className="modal-info">
                                    <h2>{selectedImage.title}</h2>
                                    <p className="modal-artist">By: {selectedImage.artist}</p>
                                    <p className="modal-date">📅 {selectedImage.date}</p>
                                    <p className="modal-description">{selectedImage.description}</p>
                                </div>
                            </div>
                        </div>
                    )}

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
