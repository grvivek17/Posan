import { useState, useEffect, useCallback } from 'react';
import { puzzlesAPI } from '../services/api';
import WordSearchPuzzle from '../components/puzzles/WordSearchPuzzle';
import CrosswordPuzzle from '../components/puzzles/CrosswordPuzzle';
import JigsawPuzzle from '../components/puzzles/JigsawPuzzle';
import SudokuPuzzle from '../components/puzzles/SudokuPuzzle';
import SolarSystemPuzzle from '../components/puzzles/SolarSystemPuzzle';
import './PuzzleZone.css';

const PuzzleZone = () => {
    const [activePuzzle, setActivePuzzle] = useState('word-search');
    const [generating, setGenerating] = useState(false);
    const [selectedTopic, setSelectedTopic] = useState('animals');
    const [selectedDifficulty, setSelectedDifficulty] = useState('medium');
    const [selectedAgeGroup, setSelectedAgeGroup] = useState('6-8');
    const [aiPuzzleData, setAiPuzzleData] = useState(null);

    const topics = [
        'animals', 'space', 'ocean', 'dinosaurs', 'sports',
        'food', 'science', 'history', 'nature', 'vehicles'
    ];
    const difficulties = ['easy', 'medium', 'hard'];
    const ageGroups = ['4-5', '6-8', '9-12', '13+'];

    const puzzles = [
        { id: 'word-search', name: 'Word Search', icon: '🔍', component: WordSearchPuzzle },
        { id: 'crossword', name: 'Crossword', icon: '📝', component: CrosswordPuzzle },
        { id: 'jigsaw', name: 'Jigsaw', icon: '🧩', component: JigsawPuzzle },
        { id: 'sudoku', name: 'Sudoku', icon: '🔢', component: SudokuPuzzle },
        { id: 'solar', name: 'Solar System', icon: '🪐', component: SolarSystemPuzzle }
    ];

    const generateAIPuzzle = useCallback(async () => {
        if (activePuzzle === 'solar') {
            setAiPuzzleData(null);
            return;
        }
        
        setGenerating(true);
        setAiPuzzleData(null); // Clear old puzzle immediately so user sees fresh state
        try {
            const puzzleTypeMap = {
                'word-search': 'word_search',
                'crossword': 'crossword',
                'sudoku': 'sudoku',
                'jigsaw': 'jigsaw'
            };

            const response = await puzzlesAPI.generateAIPuzzle({
                puzzle_type: puzzleTypeMap[activePuzzle],
                topic: selectedTopic,
                difficulty: selectedDifficulty,
                age_group: selectedAgeGroup,
                save_to_db: false
            });

            setAiPuzzleData(response.data);
            // Puzzle will automatically display in the container
        } catch (err) {
            console.error('Puzzle generation error:', err);
            alert('Failed to generate puzzle. Please try again.');
        } finally {
            setGenerating(false);
        }
    }, [activePuzzle, selectedTopic, selectedDifficulty, selectedAgeGroup]);

    // Auto-generate puzzle on page load and when puzzle type or topic changes
    useEffect(() => {
        generateAIPuzzle();
    }, [generateAIPuzzle]); // Auto-regenerates when puzzle type or topic changes

    const clearAIPuzzle = () => {
        setAiPuzzleData(null);
    };

    const handleTabClick = (puzzleId) => {
        setActivePuzzle(puzzleId);
        setAiPuzzleData(null); // Clear AI puzzle when switching tabs
    };

    const ActiveComponent = puzzles.find(p => p.id === activePuzzle)?.component;

    return (
        <div className="puzzle-zone-page">
            <div className="puzzle-zone-header">
                <h1 className="main-title">🎮 Puzzle Zone</h1>
                <p className="subtitle">Challenge your brain with fun interactive puzzles!</p>
            </div>

            {/* AI Puzzle Generator - Auto Mode */}
            <div className="ai-generator-section">
                <h3>🤖 AI Puzzle Generator</h3>
                <div className="generator-controls">
                    <select
                        value={selectedTopic}
                        onChange={(e) => setSelectedTopic(e.target.value)}
                        className="topic-selector"
                        disabled={generating}
                    >
                        {topics.map(topic => (
                            <option key={topic} value={topic}>
                                {topic.charAt(0).toUpperCase() + topic.slice(1)}
                            </option>
                        ))}
                    </select>
                    <select
                        value={selectedDifficulty}
                        onChange={(e) => setSelectedDifficulty(e.target.value)}
                        className="topic-selector"
                        disabled={generating}
                    >
                        {difficulties.map(diff => (
                            <option key={diff} value={diff}>
                                {diff.charAt(0).toUpperCase() + diff.slice(1)}
                            </option>
                        ))}
                    </select>
                    <select
                        value={selectedAgeGroup}
                        onChange={(e) => setSelectedAgeGroup(e.target.value)}
                        className="topic-selector"
                        disabled={generating}
                    >
                        {ageGroups.map(age => (
                            <option key={age} value={age}>
                                Age {age}
                            </option>
                        ))}
                    </select>
                    <button
                        onClick={generateAIPuzzle}
                        disabled={generating}
                        className="btn btn-secondary generate-btn"
                    >
                        {generating ? '✨ Generating...' : '🔄 Regenerate Puzzle'}
                    </button>
                </div>
                <p className="hint-text">
                    {generating ? '⏳ Creating your puzzle...' : '💡 Puzzle auto-generates! Switch tabs or topics for new puzzles.'}
                </p>
                {aiPuzzleData && (
                    <div className="ai-puzzle-status">
                        <span>✨ AI Puzzle: {aiPuzzleData.title}</span>
                        <button onClick={clearAIPuzzle} className="clear-btn">✕ Clear</button>
                    </div>
                )}
            </div>

            <div className="puzzle-tabs">
                {puzzles.map(puzzle => (
                    <button
                        key={puzzle.id}
                        className={`puzzle-tab ${activePuzzle === puzzle.id ? 'active' : ''}`}
                        onClick={() => handleTabClick(puzzle.id)}
                    >
                        <span className="tab-icon">{puzzle.icon}</span>
                        <span className="tab-name">{puzzle.name}</span>
                    </button>
                ))}
            </div>

            <div className="puzzle-container">
                {aiPuzzleData && activePuzzle === 'word-search' && (
                    <WordSearchPuzzle
                        key={`ai-ws-${selectedTopic}`}
                        words={aiPuzzleData.puzzle_data?.words || []}
                        grid={aiPuzzleData.puzzle_data?.grid || []}
                        title={aiPuzzleData.title || 'AI Word Search'}
                    />
                )}
                {aiPuzzleData && activePuzzle === 'crossword' && (
                    <CrosswordPuzzle
                        key={`ai-cw-${selectedTopic}`}
                        clues={aiPuzzleData.puzzle_data?.clues || []}
                        title={aiPuzzleData.title || 'AI Crossword'}
                    />
                )}
                {aiPuzzleData && activePuzzle === 'sudoku' && (
                    <SudokuPuzzle
                        key={`ai-su-${selectedTopic}`}
                        puzzle={aiPuzzleData.puzzle_data?.puzzle || null}
                        solution={aiPuzzleData.puzzle_data?.solution || null}
                    />
                )}
                {aiPuzzleData && activePuzzle === 'jigsaw' && (
                    <JigsawPuzzle key={`ai-jig-${selectedTopic}`} />
                )}
                {!aiPuzzleData && ActiveComponent && <ActiveComponent key={`fallback-${activePuzzle}-${selectedTopic}`} />}
            </div>

            <div className="puzzle-zone-footer">
                <div className="tips-section">
                    <h3>💡 Puzzle Tips</h3>
                    <div className="tips-grid">
                        {activePuzzle === 'word-search' && (
                            <>
                                <div className="tip-card">
                                    <span className="tip-icon">👀</span>
                                    <p>Look in all directions - horizontal, vertical, and diagonal!</p>
                                </div>
                                <div className="tip-card">
                                    <span className="tip-icon">🎯</span>
                                    <p>Start with shorter words to make it easier</p>
                                </div>
                            </>
                        )}
                        {activePuzzle === 'crossword' && (
                            <>
                                <div className="tip-card">
                                    <span className="tip-icon">📖</span>
                                    <p>Read all clues first to get an overview</p>
                                </div>
                                <div className="tip-card">
                                    <span className="tip-icon">✏️</span>
                                    <p>Fill in the answers you're most confident about first</p>
                                </div>
                            </>
                        )}
                        {activePuzzle === 'jigsaw' && (
                            <>
                                <div className="tip-card">
                                    <span className="tip-icon">🔢</span>
                                    <p>Drag pieces to rearrange them in order</p>
                                </div>
                                <div className="tip-card">
                                    <span className="tip-icon">✨</span>
                                    <p>Pieces turn green when in the correct position!</p>
                                </div>
                            </>
                        )}
                        {activePuzzle === 'sudoku' && (
                            <>
                                <div className="tip-card">
                                    <span className="tip-icon">🎲</span>
                                    <p>Each number 1-4 must appear once in each row and column</p>
                                </div>
                                <div className="tip-card">
                                    <span className="tip-icon">📦</span>
                                    <p>Each 2x2 box must also have all numbers 1-4</p>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PuzzleZone;
