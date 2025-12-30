import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { contentAPI } from '../services/api';
import Card from '../components/common/Card';
import './MagazinePage.css';

function MagazinePage() {
    const navigate = useNavigate();
    const [magazines, setMagazines] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

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
                <h1 className="page-title">📚 Digital Magazines</h1>
                <p className="page-subtitle">Explore amazing stories, comics, and articles!</p>

                {error && <div className="error-message">{error}</div>}

                <div className="magazines-grid">
                    {magazines.length === 0 ? (
                        <div className="empty-state">
                            <p>🎨 No magazines available yet. Check back soon!</p>
                        </div>
                    ) : (
                        magazines.map((magazine) => (
                            <Card key={magazine.id} className="magazine-card">
                                {magazine.cover_image_url && (
                                    <img
                                        src={magazine.cover_image_url}
                                        alt={magazine.title}
                                        className="magazine-cover"
                                    />
                                )}
                                <div className="magazine-info">
                                    <h3>{magazine.title}</h3>
                                    <p className="magazine-description">{magazine.description}</p>
                                    <div className="magazine-meta">
                                        <span className="age-badge">{magazine.age_group}</span>
                                        {magazine.issue_number && (
                                            <span className="issue-badge">Issue #{magazine.issue_number}</span>
                                        )}
                                    </div>
                                    <button
                                        className="btn btn-primary"
                                        onClick={() => handleReadMagazine(magazine.id)}
                                    >
                                        Read Now 📖
                                    </button>
                                </div>
                            </Card>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}

export default MagazinePage;
