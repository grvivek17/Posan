import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { contentAPI } from '../services/api';
import SearchBar from '../components/magazine/SearchBar';
import CategoryFilter from '../components/magazine/CategoryFilter';
import axios from 'axios';
import './MagazinePage.css';

function MagazinePage() {
    const navigate = useNavigate();
    const [magazines, setMagazines] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [searchQuery, setSearchQuery] = useState('');
    const [activeCategory, setActiveCategory] = useState('All');
    const [weeklyLoading, setWeeklyLoading] = useState(false);

    useEffect(() => {
        fetchMagazines();
    }, []);

    const fetchMagazines = async () => {
        try {
            const response = await contentAPI.getMagazines({ published_only: true });
            setMagazines(response.data);
        } catch (err) {
            setError('Failed to load magazines');
        } finally {
            setLoading(false);
        }
    };

    const generateWeeklyHighlights = async () => {
        setWeeklyLoading(true);
        try {
            const response = await axios.post('http://localhost:8000/api/v1/podcasts/weekly-highlights', {
                topics: null
            });

            // Navigate to AI Creator with the podcast result
            navigate('/ai-content', {
                state: {
                    podcastData: response.data,
                    showPodcast: true
                }
            });
        } catch (err) {
            setError('Failed to generate weekly highlights');
        } finally {
            setWeeklyLoading(false);
        }
    };

    const handleReadMagazine = (magazineId) => {
        navigate(`/magazines/${magazineId}`);
    };

    // Filter magazines based on search and category
    const filteredMagazines = magazines.filter(magazine => {
        const matchesSearch = magazine.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
            magazine.description.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesCategory = activeCategory === 'All' ||
            magazine.title.toLowerCase().includes(activeCategory.toLowerCase());
        return matchesSearch && matchesCategory;
    });

    // Featured magazine (first one or with special flag)
    const featuredMagazine = magazines[0];
    const newArrivals = filteredMagazines.slice(0, 3);
    const exploreAll = filteredMagazines.slice(3);

    if (loading) {
        return (
            <div className="loading-container">
                <div className="spinner"></div>
                <p>Loading magazines...</p>
            </div>
        );
    }

    return (
        <div className="magazine-page">
            <div className="container">
                {/* Header */}
                <div className="page-header-lib">
                    <div className="header-icon">📚</div>
                    <h1 className="page-title-lib">Library</h1>
                    <div className="header-buttons">
                        <button
                            className="store-btn"
                            onClick={() => navigate('/store')}
                        >
                            🛒 Shop Activity Books
                        </button>
                        <button
                            className="weekly-highlights-btn"
                            onClick={generateWeeklyHighlights}
                            disabled={weeklyLoading}
                        >
                            {weeklyLoading ? '🎙️ Creating...' : '🎧 Weekly Highlights Podcast'}
                        </button>
                    </div>
                </div>

                {/* Search Bar */}
                <SearchBar
                    value={searchQuery}
                    onChange={setSearchQuery}
                    placeholder="Search stories, games..."
                />

                {/* Category Filter */}
                <CategoryFilter
                    activeCategory={activeCategory}
                    onCategoryChange={setActiveCategory}
                />

                {error && <div className="error-message">{error}</div>}

                {/* Issue of the Month */}
                {featuredMagazine && (
                    <section className="featured-section-lib">
                        <div
                            className="featured-card-lib"
                            onClick={() => handleReadMagazine(featuredMagazine.id)}
                        >
                            <div className="featured-badge">ISSUE OF THE MONTH</div>
                            <div className="featured-content-lib">
                                <h3 className="featured-title">{featuredMagazine.title}</h3>
                                <p className="featured-subtitle">{featuredMagazine.description}</p>
                                <div className="featured-footer">
                                    <span className="reading-time">🕐 15 min read</span>
                                    <button className="read-now-btn">Read Now</button>
                                </div>
                            </div>
                        </div>
                    </section>
                )}

                {/* New Arrivals */}
                {newArrivals.length > 0 && (
                    <section className="arrivals-section">
                        <div className="section-header-lib">
                            <h2>New Arrivals</h2>
                            <button className="view-all-link" onClick={() => setActiveCategory('All')}>
                                View All
                            </button>
                        </div>
                        <div className="arrivals-grid">
                            {newArrivals.map((magazine, index) => (
                                <div
                                    key={magazine.id}
                                    className="arrival-card"
                                    onClick={() => handleReadMagazine(magazine.id)}
                                >
                                    {index < 2 && <span className="new-tag">NEW</span>}
                                    <div className="arrival-image">
                                        {magazine.cover_image_url ? (
                                            <img
                                                src={magazine.cover_image_url}
                                                alt={magazine.title}
                                            />
                                        ) : (
                                            <div className="placeholder-icon-lib">
                                                {index === 0 ? '🤖' : index === 1 ? '🦒' : '🎨'}
                                            </div>
                                        )}
                                    </div>
                                    <div className="arrival-info">
                                        <h3>{magazine.title}</h3>
                                        <p>Vol. {magazine.issue_number || (index + 1)} · 12 min</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>
                )}

                {/* Explore All */}
                {filteredMagazines.length > 0 && (
                    <section className="explore-section">
                        <h2 className="section-title-lib">Explore All</h2>
                        <div className="explore-grid">
                            {filteredMagazines.map((magazine, index) => (
                                <div
                                    key={magazine.id}
                                    className="explore-card"
                                    onClick={() => handleReadMagazine(magazine.id)}
                                >
                                    <div className="explore-image">
                                        {magazine.cover_image_url ? (
                                            <img
                                                src={magazine.cover_image_url}
                                                alt={magazine.title}
                                            />
                                        ) : (
                                            <div className="explore-placeholder">
                                                {['📖', '🌍', '🐸', '⚽', '🎭', '🔬'][index % 6]}
                                            </div>
                                        )}
                                    </div>
                                    <div className="explore-info">
                                        <h3>{magazine.title}</h3>
                                        <div className="explore-footer">
                                            <span className="issue-number">#{magazine.issue_number || (index + 1)}</span>
                                            <span className="star-rating">⭐</span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>
                )}

                {filteredMagazines.length === 0 && (
                    <div className="empty-state">
                        <p>🎨 No magazines found. Try a different search or category!</p>
                    </div>
                )}
            </div>
        </div>
    );
}

export default MagazinePage;
