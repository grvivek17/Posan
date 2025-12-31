import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { contentAPI } from '../services/api';
import SearchBar from '../components/magazine/SearchBar';
import CategoryFilter from '../components/magazine/CategoryFilter';
import Card from '../components/common/Card';
import './MagazinePage.css';

function MagazinePage() {
    const navigate = useNavigate();
    const [magazines, setMagazines] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [searchQuery, setSearchQuery] = useState('');
    const [activeCategory, setActiveCategory] = useState('all');

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

    const handleReadMagazine = (magazineId) => {
        navigate(`/magazines/${magazineId}`);
    };

    // Filter magazines based on search and category
    const filteredMagazines = magazines.filter(magazine => {
        const matchesSearch = magazine.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
            magazine.description.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesCategory = activeCategory === 'all' ||
            magazine.title.toLowerCase().includes(activeCategory);
        return matchesSearch && matchesCategory;
    });

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
                <div className="page-header">
                    <div className="header-content">
                        <h1 className="page-title">📚 Library</h1>
                        <p className="page-subtitle">Discover amazing stories and adventures!</p>
                    </div>
                </div>

                <SearchBar
                    value={searchQuery}
                    onChange={setSearchQuery}
                    placeholder="Search magazines, stories..."
                />

                <CategoryFilter
                    activeCategory={activeCategory}
                    onCategoryChange={setActiveCategory}
                />

                {error && <div className="error-message">{error}</div>}

                {filteredMagazines.length === 0 ? (
                    <div className="empty-state">
                        <p>🎨 No magazines found. Try a different search or category!</p>
                    </div>
                ) : (
                    <>
                        <div className="section-header">
                            <h2>Explore All</h2>
                            <span className="result-count">{filteredMagazines.length} magazines</span>
                        </div>

                        <div className="magazines-grid">
                            {filteredMagazines.map((magazine) => (
                                <div key={magazine.id} className="magazine-card-wrapper">
                                    <div className="magazine-card" onClick={() => handleReadMagazine(magazine.id)}>
                                        <div className="card-image-container">
                                            {magazine.cover_image_url ? (
                                                <img
                                                    src={magazine.cover_image_url}
                                                    alt={magazine.title}
                                                    className="magazine-cover"
                                                />
                                            ) : (
                                                <div className="placeholder-cover">
                                                    <span className="placeholder-icon">📖</span>
                                                </div>
                                            )}
                                            {magazine.issue_number && (
                                                <div className="card-badge">Issue #{magazine.issue_number}</div>
                                            )}
                                        </div>
                                        <div className="card-content">
                                            <h3 className="card-title">{magazine.title}</h3>
                                            <p className="card-description">{magazine.description}</p>
                                            <div className="card-footer">
                                                <span className="age-badge">{magazine.age_group}</span>
                                                <button className="read-btn">
                                                    Read Now
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}

export default MagazinePage;
