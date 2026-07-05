import { useState, useEffect } from 'react';
import './CrosswordPuzzle.css';
import { getRandomCrossword } from '../../data/puzzleData';
import { gamificationService } from '../../services/gamificationService';

const CrosswordPuzzle = ({ clues: aiClues = [], title = "Crossword" }) => {
    const [currentPuzzle, setCurrentPuzzle] = useState(null);
    const [userAnswers, setUserAnswers] = useState({});
    const [grid, setGrid] = useState([]);
    const [gridSize, setGridSize] = useState({ rows: 0, cols: 0 });
    const [completed, setCompleted] = useState(false);

    // Load a random puzzle on component mount if no AI clues provided
    useEffect(() => {
        if (!aiClues || aiClues.length === 0) {
            const randomPuzzle = getRandomCrossword();
            setCurrentPuzzle(randomPuzzle);
        }
    }, [aiClues]);

    // Use AI clues if provided, otherwise use random puzzle
    const displayClues = aiClues && aiClues.length > 0 ? aiClues : (currentPuzzle?.clues || []);
    const puzzleTitle = title || currentPuzzle?.title || "Crossword";

    // Generate grid from clues
    useEffect(() => {
        if (displayClues && displayClues.length > 0) {
            generateGrid(displayClues);
        }
    }, [displayClues]);

    // Reset user answers when clues change
    useEffect(() => {
        setUserAnswers({});
    }, [displayClues]);

    const generateGrid = (clues) => {
        // Calculate grid size based on longest word and number of words
        const maxLength = Math.max(...clues.map(c => (c.answer || '').length), 8);
        const size = Math.max(maxLength + 2, Math.min(clues.length + 3, 15));

        // Initialize empty grid
        const newGrid = Array(size).fill(null).map(() =>
            Array(size).fill(null).map(() => ({
                type: 'blocked',
                letter: null,
                number: null,
                clueIndex: null,
                letterIndex: null,
                direction: null
            }))
        );

        let currentRow = 1;
        let currentCol = 1;

        // Place words in grid (simplified placement - alternate horizontal)
        clues.forEach((clue, clueIndex) => {
            const word = (clue.answer || '').toUpperCase();
            const isHorizontal = clueIndex % 2 === 0;

            // Place word
            for (let i = 0; i < word.length; i++) {
                if (isHorizontal) {
                    if (currentCol + i < size) {
                        newGrid[currentRow][currentCol + i] = {
                            type: 'cell',
                            letter: word[i],
                            number: i === 0 ? clueIndex + 1 : null,
                            clueIndex,
                            letterIndex: i,
                            direction: 'across'
                        };
                    }
                } else {
                    if (currentRow + i < size) {
                        newGrid[currentRow + i][currentCol] = {
                            type: 'cell',
                            letter: word[i],
                            number: i === 0 ? clueIndex + 1 : null,
                            clueIndex,
                            letterIndex: i,
                            direction: 'down'
                        };
                    }
                }
            }

            // Move to next position
            if (isHorizontal) {
                currentRow += 2;
                if (currentRow >= size - 1) {
                    currentRow = 1;
                    currentCol += 3;
                }
            } else {
                currentCol += 2;
                if (currentCol >= size - 1) {
                    currentCol = 1;
                    currentRow += 3;
                }
            }
        });

        setGrid(newGrid);
        setGridSize({ rows: size, cols: size });
    };

    const handleCellChange = (row, col, value) => {
        const cell = grid[row][col];
        if (cell.type === 'cell') {
            const key = `${cell.clueIndex}-${cell.letterIndex}`;
            setUserAnswers({
                ...userAnswers,
                [key]: value.toUpperCase()
            });
        }
    };

    const checkAnswers = async () => {
        let correct = 0;
        let total = 0;

        displayClues.forEach((clue, clueIndex) => {
            const word = (clue.answer || '').toUpperCase();

            for (let i = 0; i < word.length; i++) {
                const key = `${clueIndex}-${i}`;
                const userLetter = userAnswers[key] || '';
                total++;

                if (userLetter === word[i]) {
                    correct++;
                }
            }
        });

        if (correct === total && !completed) {
            setCompleted(true);
            try {
                await gamificationService.addPoints('puzzle_solved', {
                    puzzle_type: 'crossword'
                });
            } catch (error) {
                console.error('Error awarding points:', error);
            }
        }

        alert(`You got ${correct} out of ${total} letters correct! ${correct === total ? '🎉 Perfect! Points awarded!' : 'Keep trying! 💪'}`);
    };

    const getCellValue = (row, col) => {
        const cell = grid[row][col];
        if (cell.type === 'cell') {
            const key = `${cell.clueIndex}-${cell.letterIndex}`;
            return userAnswers[key] || '';
        }
        return '';
    };

    // Separate clues into across and down
    const acrossClues = displayClues.filter((_, index) => index % 2 === 0);
    const downClues = displayClues.filter((_, index) => index % 2 !== 0);

    // Show loading state
    if (!displayClues || displayClues.length === 0) {
        return <div className="crossword-puzzle">Loading puzzle...</div>;
    }

    return (
        <div className="crossword-puzzle">
            <h3 className="puzzle-title">{puzzleTitle}</h3>

            {aiClues && aiClues.length > 0 && (
                <div className="ai-badge">🤖 AI Generated</div>
            )}

            <div className="crossword-layout">
                {/* Crossword Grid */}
                <div className="crossword-grid">
                    {grid.map((row, rowIndex) => (
                        <div key={rowIndex} className="crossword-row">
                            {row.map((cell, colIndex) => (
                                <div
                                    key={colIndex}
                                    className={`crossword-cell ${cell.type === 'blocked' ? 'blocked' : ''}`}
                                >
                                    {cell.type === 'cell' && (
                                        <>
                                            {cell.number && (
                                                <span className="cell-number">{cell.number}</span>
                                            )}
                                            <input
                                                type="text"
                                                className="cell-input"
                                                maxLength="1"
                                                value={getCellValue(rowIndex, colIndex)}
                                                onChange={(e) => handleCellChange(rowIndex, colIndex, e.target.value)}
                                            />
                                        </>
                                    )}
                                </div>
                            ))}
                        </div>
                    ))}
                </div>

                {/* Clues Section */}
                <div className="clues-section">
                    {acrossClues.length > 0 && (
                        <div className="clues-group">
                            <h4>Across</h4>
                            <ul>
                                {acrossClues.map((clue, index) => {
                                    const clueIndex = index * 2;
                                    return (
                                        <li key={clueIndex}>
                                            <strong>{clueIndex + 1}.</strong> {clue.clue || clue}
                                        </li>
                                    );
                                })}
                            </ul>
                        </div>
                    )}

                    {downClues.length > 0 && (
                        <div className="clues-group">
                            <h4>Down</h4>
                            <ul>
                                {downClues.map((clue, index) => {
                                    const clueIndex = index * 2 + 1;
                                    return (
                                        <li key={clueIndex}>
                                            <strong>{clueIndex + 1}.</strong> {clue.clue || clue}
                                        </li>
                                    );
                                })}
                            </ul>
                        </div>
                    )}
                </div>
            </div>

            <div className="puzzle-actions">
                <button className="action-btn check-btn" onClick={checkAnswers}>
                    ✓ Check Answers
                </button>
            </div>
        </div>
    );
};

export default CrosswordPuzzle;
