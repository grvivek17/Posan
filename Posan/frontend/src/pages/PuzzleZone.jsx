import { useState } from 'react';
import WordSearchPuzzle from '../components/puzzles/WordSearchPuzzle';
import CrosswordPuzzle from '../components/puzzles/CrosswordPuzzle';
import JigsawPuzzle from '../components/puzzles/JigsawPuzzle';
import SudokuPuzzle from '../components/puzzles/SudokuPuzzle';
import './PuzzleZone.css';

const PuzzleZone = () => {
    const [activePuzzle, setActivePuzzle] = useState('word-search');

    const puzzles = [
        { id: 'word-search', name: 'Word Search', icon: '🔍', component: WordSearchPuzzle },
        { id: 'crossword', name: 'Crossword', icon: '📝', component: CrosswordPuzzle },
        { id: 'jigsaw', name: 'Jigsaw', icon: '🧩', component: JigsawPuzzle },
        { id: 'sudoku', name: 'Sudoku', icon: '🔢', component: SudokuPuzzle }
    ];

    const ActiveComponent = puzzles.find(p => p.id === activePuzzle)?.component;

    return (
        <div className="puzzle-zone-page">
            <div className="puzzle-zone-header">
                <h1 className="main-title">🎮 Puzzle Zone</h1>
                <p className="subtitle">Challenge your brain with fun interactive puzzles!</p>
            </div>

            <div className="puzzle-tabs">
                {puzzles.map(puzzle => (
                    <button
                        key={puzzle.id}
                        className={`puzzle-tab ${activePuzzle === puzzle.id ? 'active' : ''}`}
                        onClick={() => setActivePuzzle(puzzle.id)}
                    >
                        <span className="tab-icon">{puzzle.icon}</span>
                        <span className="tab-name">{puzzle.name}</span>
                    </button>
                ))}
            </div>

            <div className="puzzle-container">
                {ActiveComponent && <ActiveComponent />}
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
