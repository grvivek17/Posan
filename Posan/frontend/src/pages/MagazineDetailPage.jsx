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
                                        onClick={() => openArticle(article.id)}
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

    function openArticle(articleId) {
        // For now, scroll to article or open modal
        // You can enhance this to navigate to a full article view
        const article = articles.find(a => a.id === articleId);
        if (article) {
            alert(`Opening: ${article.title}\n\n${article.content}`);
            // TODO: Navigate to article detail page or open in modal
        }
    }
}

export default MagazineDetailPage;
