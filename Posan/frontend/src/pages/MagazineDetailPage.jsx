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
                        </div>
                        <div className="article-reader-body">
                            {selectedArticle.content.split('\n').map((paragraph, idx) => (
                                paragraph.trim() ? (
                                    <p key={idx}>{paragraph}</p>
                                ) : null
                            ))}
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
