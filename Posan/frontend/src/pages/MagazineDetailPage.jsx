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
    const [currentPage, setCurrentPage] = useState(0);

    const getPaginatedContent = (content, articleId) => {
        const paragraphs = content.split('\n').filter(p => p.trim());
        const emojis = ['🚀', '🦕', '🌟', '🎨', '🦁', '🔍', '🌈', '🧩', '⚡', '🦉', '✨', '🌍', '🦖', '🔭', '🎭'];
        
        const blocks = [];
        paragraphs.forEach((paragraph, idx) => {
            // Handle markdown images
            if (paragraph.startsWith('![') && paragraph.includes('](')) {
                const match = paragraph.match(/!\[(.*?)\]\((.*?)\)/);
                if (match) {
                    blocks.push(
                        <div key={idx} className="book-image-container">
                            <img src={match[2]} alt={match[1]} className="book-image" />
                        </div>
                    );
                    return;
                }
            }

            // Did you know block
            if (paragraph.toLowerCase().includes('did you know') || paragraph.toLowerCase().includes('fun fact')) {
                blocks.push(
                    <div key={idx} className="did-you-know">
                        💡 {paragraph}
                    </div>
                );
                return;
            }

            // Drop cap for the first paragraph
            let textElement = <p key={idx}>{paragraph}</p>;
            if (idx === 0 && paragraph.length > 0 && !paragraph.startsWith('![')) {
                const firstChar = paragraph.charAt(0);
                const rest = paragraph.slice(1);
                textElement = (
                    <p key={idx}>
                        <span className="drop-cap">{firstChar}</span>
                        {rest}
                    </p>
                );
            }

            // Insert illustration occasionally
            if (idx > 0 && idx % 3 === 0) {
                const pseudoRandomIndex = (articleId * 7 + idx * 13) % emojis.length;
                const randomEmoji = emojis[pseudoRandomIndex];
                blocks.push(
                    <div key={`ill-${idx}`} className="illustration-box">
                        {randomEmoji}
                        <div className="illustration-caption">Imagine this!</div>
                    </div>
                );
            }

            blocks.push(textElement);
        });

        // Split into pages (4 blocks per page)
        const BLOCKS_PER_PAGE = 4;
        const pages = [];
        for (let i = 0; i < blocks.length; i += BLOCKS_PER_PAGE) {
            pages.push(blocks.slice(i, i + BLOCKS_PER_PAGE));
        }
        return pages;
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
            {/* Article Reader View (Book UI) */}
            {selectedArticle && (() => {
                const pages = getPaginatedContent(selectedArticle.content, selectedArticle.id);
                return (
                <div className="article-reader-overlay" onClick={() => setSelectedArticle(null)}>
                    <div className="book-reader-container" onClick={(e) => e.stopPropagation()}>
                        <button className="book-close" onClick={() => setSelectedArticle(null)}>&times;</button>
                        
                        <div className="book-layout">
                            {/* Previous Button */}
                            <button 
                                className="book-nav-btn prev" 
                                disabled={currentPage === 0}
                                onClick={() => setCurrentPage(prev => Math.max(0, prev - 2))}
                            >
                                &#8249;
                            </button>
                            
                            {/* Book Spine (Visual) */}
                            <div className="book-spine-center"></div>

                            {/* Left Page */}
                            <div className="book-page left-page">
                                {currentPage === 0 && (
                                    <div className="book-cover-page">
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
                                        </div>
                                        <h1 className="article-reader-title">{selectedArticle.title}</h1>
                                        {selectedArticle.author && <p className="article-reader-author">By {selectedArticle.author}</p>}
                                        <button 
                                            className="read-aloud-btn"
                                            onClick={() => setIsReadingAloud(!isReadingAloud)}
                                        >
                                            {isReadingAloud ? '⏸️ Pause Reading' : '🔊 Read Aloud'}
                                        </button>
                                    </div>
                                )}
                                <div className="book-page-content">
                                    {pages[currentPage]}
                                </div>
                                <div className="page-number">{currentPage + 1}</div>
                            </div>
                            
                            {/* Right Page */}
                            <div className="book-page right-page">
                                <div className="book-page-content">
                                    {pages[currentPage + 1]}
                                </div>
                                {currentPage + 1 < pages.length && (
                                    <div className="page-number">{currentPage + 2}</div>
                                )}
                            </div>

                            {/* Next Button */}
                            <button 
                                className="book-nav-btn next" 
                                disabled={currentPage + 2 >= pages.length}
                                onClick={() => setCurrentPage(prev => prev + 2)}
                            >
                                &#8250;
                            </button>
                        </div>
                    </div>
                </div>
                );
            })()}

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
                                        onClick={() => {
                                            setSelectedArticle(article);
                                            setCurrentPage(0);
                                        }}
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
