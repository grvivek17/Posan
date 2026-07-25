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
    const [successMsg, setSuccessMsg] = useState('');
    const [searchQuery, setSearchQuery] = useState('');
    const [activeCategory, setActiveCategory] = useState('All');
    const [weeklyLoading, setWeeklyLoading] = useState(false);
    const [refreshing, setRefreshing] = useState(false);

    useEffect(() => {
        fetchMagazines();
    }, []);

    const fetchMagazines = async () => {
        try {
            const response = await contentAPI.getMagazines({ published_only: true });
            const allMagazines = response.data;
            setMagazines(allMagazines);
            setLoading(false);

            // Auto-check: if no magazines exist for the current month, trigger a background refresh
            const now = new Date();
            const currentMonth = now.getMonth() + 1;
            const currentYear = now.getFullYear();
            const hasCurrentMonth = allMagazines.some(mag => {
                if (!mag.publication_date) return false;
                const pubDate = new Date(mag.publication_date);
                return pubDate.getMonth() + 1 === currentMonth && pubDate.getFullYear() === currentYear;
            });

            // Throttle auto-refresh: only try once per hour to avoid repeated slow loads
            const lastRefresh = localStorage.getItem('magazine_last_auto_refresh');
            const oneHourAgo = Date.now() - 60 * 60 * 1000;
            const shouldAutoRefresh = !lastRefresh || Number(lastRefresh) < oneHourAgo;

            if (shouldAutoRefresh && (!hasCurrentMonth || allMagazines.length === 0)) {
                console.log('[Magazines] Triggering background auto-refresh...');
                // Run in background - don't block the UI
                autoRefreshMagazines();
            }
        } catch (err) {
            setError('Failed to load magazines');
            setLoading(false);
        }
    };

    const autoRefreshMagazines = async () => {
        setRefreshing(true);
        localStorage.setItem('magazine_last_auto_refresh', String(Date.now()));
        try {
            // Use force=false so existing magazines are kept if they exist
            const result = await contentAPI.refreshMonthlyMagazines(false);
            console.log('[Magazines] Auto-refresh result:', result.data);
            // Re-fetch magazines after refresh
            const response = await contentAPI.getMagazines({ published_only: true });
            setMagazines(response.data);
        } catch (err) {
            console.warn('[Magazines] Auto-refresh failed:', err);
        } finally {
            setRefreshing(false);
        }
    };

    const handleForceRefresh = async () => {
        setRefreshing(true);
        setError('');
        setSuccessMsg('');
        try {
            const result = await contentAPI.refreshMonthlyMagazines(true);
            console.log('[Magazines] Force refresh result:', result.data);
            // Re-fetch magazines after refresh
            const response = await contentAPI.getMagazines({ published_only: true });
            setMagazines(response.data);
            const count = result.data?.magazines?.length || response.data?.length || 0;
            if (result.data?.status === 'success' && count > 0) {
                setSuccessMsg(`Refreshed! ${count} magazines loaded with latest content.`);
            } else if (response.data?.length > 0) {
                setSuccessMsg('Magazines updated successfully!');
            }
            // Auto-dismiss success message after 4 seconds
            setTimeout(() => setSuccessMsg(''), 4000);
        } catch (err) {
            setError('Failed to refresh magazines. Please try again later.');
        } finally {
            setRefreshing(false);
        }
    };

    const generateWeeklyHighlights = async () => {
        setWeeklyLoading(true);
        try {
            const magazineApiBase = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
            const response = await axios.post(`${magazineApiBase}/podcasts/weekly-highlights`, {
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

    // Featured magazine (first one or with special flag) only on default view
    const featuredMagazine = (searchQuery === '' && activeCategory === 'All' && magazines.length > 0) ? magazines[0] : null;
    
    const remainingMagazines = featuredMagazine 
        ? filteredMagazines.filter(m => m.id !== featuredMagazine.id) 
        : filteredMagazines;
        
    const newArrivals = remainingMagazines.slice(0, 3);
    const exploreAll = remainingMagazines.slice(3);

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
                            onClick={handleForceRefresh}
                            disabled={refreshing}
                        >
                            {refreshing ? '🔄 Refreshing...' : '🔄 Get Latest'}
                        </button>
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

                {/* Refreshing indicator */}
                {refreshing && (
                    <div className="refresh-banner">
                        <div className="spinner-small"></div>
                        <span>Fetching latest magazines from the web...</span>
                    </div>
                )}

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
                {successMsg && <div className="success-message">{successMsg}</div>}

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
                                                loading="lazy"
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
                {exploreAll.length > 0 && (
                    <section className="explore-section">
                        <h2 className="section-title-lib">Explore All</h2>
                        <div className="explore-grid">
                            {exploreAll.map((magazine, index) => (
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
                                                loading="lazy"
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
