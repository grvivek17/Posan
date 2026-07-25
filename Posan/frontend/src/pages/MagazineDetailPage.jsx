import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { contentAPI } from '../services/api';
import Card from '../components/common/Card';
import './MagazineDetailPage.css';

function MagazineDetailPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [magazine, setMagazine] = useState(null);
    const [articles, setArticles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [selectedArticle, setSelectedArticle] = useState(null);
    const [isReadingAloud, setIsReadingAloud] = useState(false);

    const renderEnrichedContent = (content) => {
        const paragraphs = content.split('\n').filter(p => p.trim());
        const emojis = ['🚀', '🦕', '🌟', '🎨', '🦁', '🔍', '🌈', '🧩', '⚡', '🦉'];
        
        return paragraphs.map((paragraph, idx) => {
            // Did you know block
            if (paragraph.toLowerCase().includes('did you know') || paragraph.toLowerCase().includes('fun fact')) {
                return (
                    <div key={idx} className="did-you-know">
                        💡 {paragraph}
                    </div>
                );
            }

            // Drop cap for the first paragraph
            let textElement = <p key={idx}>{paragraph}</p>;
            if (idx === 0 && paragraph.length > 0) {
                const firstChar = paragraph.charAt(0);
                const rest = paragraph.slice(1);
                textElement = (
                    <p key={idx}>
                        <span className="drop-cap">{firstChar}</span>
                        {rest}
                    </p>
                );
            }

            // Insert illustration every 3 paragraphs
            if (idx > 0 && idx % 3 === 0) {
                const randomEmoji = emojis[idx % emojis.length];
                return (
                    <React.Fragment key={idx}>
                        <div className="illustration-box">
                            {randomEmoji}
                            <div className="illustration-caption">Imagine this!</div>
                        </div>
                        {textElement}
                    </React.Fragment>
                );
            }

            return textElement;
        });
    };

    useEffect(() => {
        fetchMagazineAndArticles();
    }, [id]);

    const fetchMagazineAndArticles = async () => {
        try {
            // Fetch magazine details
            const magResponse = await contentAPI.getMagazine(id);
            setMagazine(magResponse.data);

            // Fetch articles for this magazine
            const articlesResponse = await contentAPI.getArticles({ magazine_id: id });
            setArticles(articlesResponse.data);
        } catch (err) {
            setError('Failed to load magazine content');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="loading-container">
                <div className="spinner"></div>
                <p>Loading magazine...</p>
            </div>
        );
    }

    if (error || !magazine) {
        return (
            <div className="error-container">
                <p>{error || 'Magazine not found'}</p>
                <button onClick={() => navigate('/magazines')} className="btn btn-primary">
                    Back to Magazines
                </button>
            </div>
        );
    }

    return (
        <div className="magazine-detail-page">
            {/* Article Reader View */}
            {selectedArticle && (
                <div className="article-reader-overlay" onClick={() => setSelectedArticle(null)}>
                    <div className="article-reader" onClick={(e) => e.stopPropagation()}>
                        <div className="article-reader-header">
                            <button
                                className="article-reader-close"
                                onClick={() => setSelectedArticle(null)}
                            >
                                &times;
                            </button>
                            <div className="article-reader-meta">
                                {selectedArticle.content_type && (
                                    <span className="article-reader-type">
                                        {selectedArticle.content_type === 'ARTICLE' && '📰'}
                                        {selectedArticle.content_type === 'STORY' && '📖'}
                                        {selectedArticle.content_type === 'ACTIVITY' && '🎨'}
                                        {selectedArticle.content_type === 'COMIC' && '💭'}
                                        {' '}{selectedArticle.content_type}
                                    </span>
                                )}
                                {selectedArticle.reading_time_minutes && (
                                    <span className="article-reader-time">
                                        ⏱️ {selectedArticle.reading_time_minutes} min read
                                    </span>
                                )}
                            </div>
                            <h1 className="article-reader-title">{selectedArticle.title}</h1>
                            {selectedArticle.author && (
                                <p className="article-reader-author">By {selectedArticle.author}</p>
                            )}
                            <button 
                                className="read-aloud-btn"
                                onClick={() => setIsReadingAloud(!isReadingAloud)}
                            >
                                {isReadingAloud ? '⏸️ Pause Reading' : '🔊 Read Aloud'}
                            </button>
                        </div>
                        <div className="article-reader-body enriched">
                            {renderEnrichedContent(selectedArticle.content)}
                        </div>
                        <div className="article-reader-footer">
                            <button
                                className="btn btn-primary"
                                onClick={() => setSelectedArticle(null)}
                            >
                                Back to Magazine
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Magazine Header */}
            <div className="magazine-header" style={{ backgroundImage: `url(${magazine.cover_image_url})` }}>
                <div className="magazine-header-overlay">
                    <button onClick={() => navigate('/magazines')} className="back-button">
                        ← Back to Magazines
                    </button>
                    <div className="magazine-header-content">
                        <h1>{magazine.title}</h1>
                        <p className="magazine-subtitle">{magazine.description}</p>
                        <div className="magazine-badges">
                            <span className="badge">{magazine.age_group}</span>
                            <span className="badge">Issue #{magazine.issue_number}</span>
                            <span className="badge">{articles.length} Articles</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Articles Section */}
            <div className="container">
                <div className="articles-section">
                    <h2>📖 Articles in this Issue</h2>

                    {articles.length === 0 ? (
                        <div className="empty-state">
                            <p>📝 No articles available yet in this magazine.</p>
                            <p>Check back soon for exciting content!</p>
                        </div>
                    ) : (
                        <div className="articles-grid">
                            {articles.map((article, index) => (
                                <Card key={article.id} className="article-card">
                                    <div className="article-number">Article {index + 1}</div>
                                    <h3>{article.title}</h3>
                                    <div className="article-meta">
                                        {article.content_type && (
                                            <span className="content-type-badge">
                                                {article.content_type === 'ARTICLE' && '📰'}
                                                {article.content_type === 'STORY' && '📖'}
                                                {article.content_type === 'ACTIVITY' && '🎨'}
                                                {article.content_type === 'COMIC' && '💭'}
                                                {' '}{article.content_type}
                                            </span>
                                        )}
                                        {article.reading_time_minutes && (
                                            <span className="reading-time">⏱️ {article.reading_time_minutes} min</span>
                                        )}
                                    </div>
                                    <p className="article-preview">
                                        {article.content.substring(0, 150)}...
                                    </p>
                                    <button
                                        className="btn btn-secondary"
                                        onClick={() => setSelectedArticle(article)}
                                    >
                                        Read Article →
                                    </button>
                                </Card>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default MagazineDetailPage;
