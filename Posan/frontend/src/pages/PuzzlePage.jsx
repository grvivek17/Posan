import React, { useState, useEffect } from 'react';
import { puzzlesAPI } from '../services/api';
import Card from '../components/common/Card';
import './PuzzlePage.css';

function PuzzlePage() {
    const [puzzles, setPuzzles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [filter, setFilter] = useState('all');
    const [generating, setGenerating] = useState(false);
    const [selectedTopic, setSelectedTopic] = useState('animals');

    const topics = [
        'animals', 'space', 'ocean', 'dinosaurs', 'sports',
        'food', 'science', 'history', 'nature', 'vehicles'
    ];

    useEffect(() => {
        fetchPuzzles();
    }, [filter]);

    const fetchPuzzles = async () => {
        try {
            const params = filter !== 'all' ? { puzzle_type: filter } : {};
            const response = await puzzlesAPI.getPuzzles(params);
            setPuzzles(response.data);
        } catch (err) {
            setError('Failed to load puzzles');
        } finally {
            setLoading(false);
        }
    };

    const generateAIPuzzle = async () => {
        if (!filter || filter === 'all') {
            alert('Please select a puzzle type first!');
            return;
        }

        setGenerating(true);
        setError('');

        try {
            const response = await puzzlesAPI.generateAIPuzzle({
                puzzle_type: filter,
                topic: selectedTopic,
                difficulty: 'medium',
                age_group: '6-8',
                save_to_db: false  // Don't save, just generate for instant play
            });

            // Add generated puzzle to the list
            setPuzzles([response.data, ...puzzles]);
            alert(`✨ Generated a new ${filter} puzzle about ${selectedTopic}!`);
        } catch (err) {
            setError('Failed to generate puzzle. Please try again.');
            console.error('Puzzle generation error:', err);
        } finally {
            setGenerating(false);
        }
    };

    const getPuzzleIcon = (type) => {
        const icons = {
            word_search: '🔍',
            crossword: '📝',
            jigsaw: '🧩',
            sudoku: '🔢',
        };
        return icons[type] || '🎯';
    };

    if (loading) {
        return (
            <div className="loading-container">
                <div className="spinner"></div>
                <p>Loading puzzles...</p>
            </div>
        );
    }

    return (
        <div className="puzzle-page">
            <div className="container">
                <h1 className="page-title">🧩 Puzzle Zone</h1>
                <p className="page-subtitle">Challenge your brain with fun puzzles!</p>

                {/* AI Puzzle Generator */}
                <div className="ai-generator-section">
                    <h3>🤖 Generate AI Puzzle</h3>
                    <div className="generator-controls">
                        <select
                            value={selectedTopic}
                            onChange={(e) => setSelectedTopic(e.target.value)}
                            className="topic-selector"
                        >
                            {topics.map(topic => (
                                <option key={topic} value={topic}>
                                    {topic.charAt(0).toUpperCase() + topic.slice(1)}
                                </option>
                            ))}
                        </select>
                        <button
                            onClick={generateAIPuzzle}
                            disabled={generating || filter === 'all'}
                            className="btn btn-primary generate-btn"
                        >
                            {generating ? '✨ Generating...' : '✨ Generate Random Puzzle'}
                        </button>
                    </div>
                    {filter === 'all' && (
                        <p className="hint-text">💡 Select a puzzle type above to generate!</p>
                    )}
                </div>

                <div className="puzzle-filters">
                    <button
                        className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
                        onClick={() => setFilter('all')}
                    >
                        All Puzzles
                    </button>
                    <button
                        className={`filter-btn ${filter === 'word_search' ? 'active' : ''}`}
                        onClick={() => setFilter('word_search')}
                    >
                        🔍 Word Search
                    </button>
                    <button
                        className={`filter-btn ${filter === 'crossword' ? 'active' : ''}`}
                        onClick={() => setFilter('crossword')}
                    >
                        📝 Crossword
                    </button>
                    <button
                        className={`filter-btn ${filter === 'jigsaw' ? 'active' : ''}`}
                        onClick={() => setFilter('jigsaw')}
                    >
                        🧩 Jigsaw
                    </button>
                    <button
                        className={`filter-btn ${filter === 'sudoku' ? 'active' : ''}`}
                        onClick={() => setFilter('sudoku')}
                    >
                        🔢 Sudoku
                    </button>
                </div>

                {error && <div className="error-message">{error}</div>}

                <div className="puzzles-grid">
                    {puzzles.length === 0 ? (
                        <div className="empty-state">
                            <p>🎨 No puzzles available yet. Check back soon!</p>
                        </div>
                    ) : (
                        puzzles.map((puzzle) => (
                            <Card key={puzzle.id} className="puzzle-card">
                                <div className="puzzle-icon-large">{getPuzzleIcon(puzzle.puzzle_type)}</div>
                                <h3>{puzzle.title}</h3>
                                <p className="puzzle-description">{puzzle.description}</p>
                                <div className="puzzle-meta">
                                    <span className={`difficulty-badge difficulty-${puzzle.difficulty}`}>
                                        {puzzle.difficulty}
                                    </span>
                                    <span className="points-badge">⭐ {puzzle.points_reward} pts</span>
                                </div>
                                {puzzle.is_daily_challenge && (
                                    <div className="daily-badge">🌟 Daily Challenge</div>
                                )}
                                <button className="btn btn-primary">Play Now 🎮</button>
                            </Card>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}

export default PuzzlePage;
