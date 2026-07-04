import React, { useState, useEffect } from 'react';
import axios from 'axios';
import AudioPlayer from '../components/podcasts/AudioPlayer';
import './PodcastsPage.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const PodcastsPage = () => {
    const [activeTab, setActiveTab] = useState('request'); // request, weekly, library
    const [topic, setTopic] = useState('');
    const [ageGroup, setAgeGroup] = useState('8-12');
    const [duration, setDuration] = useState('short');
    const [style, setStyle] = useState('fun');
    const [loading, setLoading] = useState(false);
    const [currentPodcast, setCurrentPodcast] = useState(null);
    const [suggestions, setSuggestions] = useState([]);
    const [examples, setExamples] = useState([]);
    const [savedPodcasts, setSavedPodcasts] = useState([]);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchSuggestions();
        fetchExamples();
        loadSavedPodcasts();
    }, []);

    const fetchSuggestions = async () => {
        try {
            const response = await axios.get(`${API_BASE}/podcasts/suggestions`);
            setSuggestions(response.data.suggestions);
        } catch (err) {
            console.error('Error fetching suggestions:', err);
        }
    };

    const fetchExamples = async () => {
        try {
            const response = await axios.get(`${API_BASE}/podcasts/examples`);
            setExamples(response.data.examples);
        } catch (err) {
            console.error('Error fetching examples:', err);
        }
    };

    const loadSavedPodcasts = () => {
        const saved = localStorage.getItem('saved_podcasts');
        if (saved) {
            setSavedPodcasts(JSON.parse(saved));
        }
    };

    const savePodcast = (podcast) => {
        const updated = [podcast, ...savedPodcasts.slice(0, 9)]; // Keep last 10
        setSavedPodcasts(updated);
        localStorage.setItem('saved_podcasts', JSON.stringify(updated));
    };

    const generatePodcast = async () => {
        if (!topic.trim()) {
            setError('Please enter a topic!');
            return;
        }

        setLoading(true);
        setError('');

        try {
            const response = await axios.post(`${API_BASE}/podcasts/generate`, {
                topic,
                age_group: ageGroup,
                duration,
                style
            });

            const podcast = {
                ...response.data,
                id: Date.now(),
                createdAt: new Date().toISOString()
            };

            setCurrentPodcast(podcast);
            savePodcast(podcast);
            setActiveTab('player');
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to generate podcast. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const generateWeeklyHighlights = async () => {
        setLoading(true);
        setError('');

        try {
            const response = await axios.post(`${API_BASE}/podcasts/weekly-highlights`, {
                topics: null // Will use default topics
            });

            const podcast = {
                ...response.data,
                id: Date.now(),
                createdAt: new Date().toISOString()
            };

            setCurrentPodcast(podcast);
            savePodcast(podcast);
            setActiveTab('player');
        } catch (err) {
            setError('Failed to generate weekly highlights. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const useSuggestion = (suggestion) => {
        setTopic(suggestion);
        setActiveTab('request');
    };

    const useExample = (example) => {
        setTopic(example.request);
        setStyle(example.style);
        setDuration(example.duration);
        setActiveTab('request');
    };

    return (
        <div className="podcasts-page">
            <div className="podcasts-header">
                <h1 className="podcasts-title">🎙️ AI Mini-Podcasts</h1>
                <p className="podcasts-subtitle">
                    Request personalized audio stories on any topic you're curious about!
                </p>
            </div>

            <div className="podcasts-tabs">
                <button
                    className={`tab-btn ${activeTab === 'request' ? 'active' : ''}`}
                    onClick={() => setActiveTab('request')}
                >
                    ✨ Request Podcast
                </button>
                <button
                    className={`tab-btn ${activeTab === 'weekly' ? 'active' : ''}`}
                    onClick={() => setActiveTab('weekly')}
                >
                    📅 Weekly Highlights
                </button>
                <button
                    className={`tab-btn ${activeTab === 'library' ? 'active' : ''}`}
                    onClick={() => setActiveTab('library')}
                >
                    📚 My Library
                </button>
                {currentPodcast && (
                    <button
                        className={`tab-btn ${activeTab === 'player' ? 'active' : ''}`}
                        onClick={() => setActiveTab('player')}
                    >
                        ▶️ Now Playing
                    </button>
                )}
            </div>

            <div className="podcasts-content">
                {/* Request Tab */}
                {activeTab === 'request' && (
                    <div className="request-section">
                        <div className="request-card card">
                            <h2>🎤 What do you want to learn about?</h2>

                            <div className="form-group">
                                <label>Your Topic or Question:</label>
                                <input
                                    type="text"
                                    value={topic}
                                    onChange={(e) => setTopic(e.target.value)}
                                    placeholder="e.g., Tell me a fun fact about dinosaurs"
                                    className="topic-input"
                                />
                            </div>

                            <div className="options-grid">
                                <div className="form-group">
                                    <label>Age Group:</label>
                                    <select value={ageGroup} onChange={(e) => setAgeGroup(e.target.value)}>
                                        <option value="6-8">6-8 years</option>
                                        <option value="8-12">8-12 years</option>
                                        <option value="12-14">12-14 years</option>
                                    </select>
                                </div>

                                <div className="form-group">
                                    <label>Duration:</label>
                                    <select value={duration} onChange={(e) => setDuration(e.target.value)}>
                                        <option value="short">Short (2-3 min)</option>
                                        <option value="medium">Medium (5 min)</option>
                                        <option value="long">Long (10 min)</option>
                                    </select>
                                </div>

                                <div className="form-group">
                                    <label>Style:</label>
                                    <select value={style} onChange={(e) => setStyle(e.target.value)}>
                                        <option value="fun">🎉 Fun & Exciting</option>
                                        <option value="educational">📚 Educational</option>
                                        <option value="story">📖 Story-based</option>
                                    </select>
                                </div>
                            </div>

                            {error && <div className="error-message">{error}</div>}

                            <button
                                className="generate-btn btn-primary"
                                onClick={generatePodcast}
                                disabled={loading}
                            >
                                {loading ? '🎙️ Creating Your Podcast...' : '✨ Generate Podcast'}
                            </button>
                        </div>

                        {/* Examples */}
                        <div className="examples-section">
                            <h3>💡 Need Ideas? Try These:</h3>
                            <div className="examples-grid">
                                {examples.map((example, index) => (
                                    <div
                                        key={index}
                                        className="example-card"
                                        onClick={() => useExample(example)}
                                    >
                                        <div className="example-request">{example.request}</div>
                                        <div className="example-desc">{example.description}</div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Suggestions */}
                        {suggestions.popular && (
                            <div className="suggestions-section">
                                <h3>🔥 Popular Topics:</h3>
                                <div className="suggestions-grid">
                                    {suggestions.popular.slice(0, 8).map((suggestion, index) => (
                                        <button
                                            key={index}
                                            className="suggestion-chip"
                                            onClick={() => useSuggestion(suggestion)}
                                        >
                                            {suggestion}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Weekly Highlights Tab */}
                {activeTab === 'weekly' && (
                    <div className="weekly-section">
                        <div className="weekly-card card">
                            <div className="weekly-icon">📅</div>
                            <h2>Weekly Highlights Podcast</h2>
                            <p>Get a summary of this week's most interesting topics!</p>

                            <button
                                className="generate-btn btn-primary"
                                onClick={generateWeeklyHighlights}
                                disabled={loading}
                            >
                                {loading ? '🎙️ Creating Highlights...' : '🎧 Generate This Week\'s Highlights'}
                            </button>
                        </div>
                    </div>
                )}

                {/* Library Tab */}
                {activeTab === 'library' && (
                    <div className="library-section">
                        <h2>📚 Your Podcast Library</h2>
                        {savedPodcasts.length === 0 ? (
                            <div className="empty-library">
                                <div className="empty-icon">🎙️</div>
                                <p>No podcasts yet!</p>
                                <p>Generate your first podcast to start your library.</p>
                            </div>
                        ) : (
                            <div className="library-grid">
                                {savedPodcasts.map((podcast) => (
                                    <div
                                        key={podcast.id}
                                        className="library-item"
                                        onClick={() => {
                                            setCurrentPodcast(podcast);
                                            setActiveTab('player');
                                        }}
                                    >
                                        <div className="library-icon">🎧</div>
                                        <div className="library-info">
                                            <h4>{podcast.topic || podcast.title}</h4>
                                            <div className="library-meta">
                                                <span>{podcast.metadata?.estimated_minutes || 3} min</span>
                                                <span>•</span>
                                                <span>{podcast.metadata?.style || 'fun'}</span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* Player Tab */}
                {activeTab === 'player' && currentPodcast && (
                    <div className="player-section">
                        <div className="player-card card">
                            <div className="player-header">
                                <h2>🎧 {currentPodcast.topic || currentPodcast.title}</h2>
                                <div className="player-meta">
                                    <span className="meta-badge">{currentPodcast.metadata?.style || 'fun'}</span>
                                    <span className="meta-badge">{currentPodcast.metadata?.estimated_minutes || 3} min</span>
                                    <span className="meta-badge">{currentPodcast.metadata?.age_group || '8-12'}</span>
                                </div>
                            </div>

                            {/* Audio Player */}
                            <AudioPlayer
                                script={currentPodcast.script}
                                podcastId={currentPodcast.id?.toString()}
                                topic={currentPodcast.topic || currentPodcast.title}
                            />

                            <div className="podcast-script">
                                {currentPodcast.script ? (
                                    <div className="script-content">
                                        {currentPodcast.script.split('\n').map((line, index) => {
                                            if (line.trim().startsWith('[') && line.trim().endsWith(']')) {
                                                return (
                                                    <h3 key={index} className="script-section-title">
                                                        {line.trim()}
                                                    </h3>
                                                );
                                            } else if (line.trim()) {
                                                return <p key={index} className="script-line">{line}</p>;
                                            }
                                            return null;
                                        })}
                                    </div>
                                ) : (
                                    <p>No script available</p>
                                )}
                            </div>

                            <div className="player-actions">
                                <button
                                    className="btn-secondary"
                                    onClick={() => setActiveTab('request')}
                                >
                                    ✨ Create Another
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default PodcastsPage;
