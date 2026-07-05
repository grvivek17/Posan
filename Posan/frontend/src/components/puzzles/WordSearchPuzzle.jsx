import { useState, useEffect } from 'react';
import './WordSearchPuzzle.css';
import { getRandomWordSearch } from '../../data/puzzleData';
import { gamificationService } from '../../services/gamificationService';

const WordSearchPuzzle = ({ words = [], grid = [], title = "" }) => {
    const [foundWords, setFoundWords] = useState([]); // Array of found word strings (e.g., ['DOG'])
    const [foundCells, setFoundCells] = useState([]); // Array of "row-col" strings for highlighting
    const [selectedCells, setSelectedCells] = useState([]);
    const [currentPuzzle, setCurrentPuzzle] = useState(null);
    const [completed, setCompleted] = useState(false);

    // Initialize puzzle
    useEffect(() => {
        if (words.length > 0 && grid.length > 0) {
            // Use props if provided (AI mode)
            setCurrentPuzzle({ words, grid, title });
        } else {
            // Load random puzzle
            loadRandomPuzzle();
        }
    }, [words, grid, title]);

    const loadRandomPuzzle = () => {
        const randomPuzzle = getRandomWordSearch();
        setCurrentPuzzle(randomPuzzle);
        setFoundWords([]);
        setFoundCells([]);
        setSelectedCells([]);
        setCompleted(false);
    };

    // Determine current game state
    const currentGrid = currentPuzzle ? currentPuzzle.grid : [];
    const currentWordList = currentPuzzle ? currentPuzzle.words : [];
    const displayTitle = currentPuzzle ? currentPuzzle.title : "Word Search";

    // Validates if selected cells form a word
    const checkWord = () => {
        if (!currentGrid.length) return;

        const selectedLetters = selectedCells.map(key => {
            const [r, c] = key.split('-').map(Number);
            return currentGrid[r][c];
        }).join('');

        const reversedLetters = selectedLetters.split('').reverse().join('');

        const matchedWord = currentWordList.find(word =>
            (word === selectedLetters || word === reversedLetters) &&
            !foundWords.includes(word)
        );

        if (matchedWord) {
            // Valid word found!
            setFoundWords([...foundWords, matchedWord]);
            setFoundCells([...foundCells, ...selectedCells]);
            setSelectedCells([]);

            // Check for game completion
            // We use the new length + 1 because state updates are async
            if (foundWords.length + 1 === currentWordList.length) {
                handleCompletion();
            }
        } else {
            // Invalid - clear selection
            alert("Not a valid word! Try again.");
            setSelectedCells([]);
        }
    };

    const handleCompletion = () => {
        if (!completed) {
            setCompleted(true);

            // Allow state to update before showing alert
            setTimeout(async () => {
                try {
                    await gamificationService.addPoints(
                        'puzzle_solved',
                        { puzzle_type: 'word_search' }
                    );
                    alert('🎉 Congratulations! You found all the words! Points awarded!');
                } catch (error) {
                    console.error('Error awarding points:', error);
                    alert('🎉 Congratulations! You found all the words!');
                }
            }, 100);
        }
    };

    const handleCellClick = (row, col) => {
        if (completed) return;

        const cellKey = `${row}-${col}`;

        // Allow deselecting the last clicked cell (undo)
        if (selectedCells[selectedCells.length - 1] === cellKey) {
            setSelectedCells(selectedCells.slice(0, -1));
            return;
        }

        // Prevent selecting already found cells or adding duplicates
        if (foundCells.includes(cellKey) || selectedCells.includes(cellKey)) return;

        if (selectedCells.length === 0) {
            // First cell - always valid
            setSelectedCells([cellKey]);
        } else if (selectedCells.length === 1) {
            // Second cell - must be adjacent to first
            const [r0, c0] = selectedCells[0].split('-').map(Number);
            if (Math.abs(row - r0) <= 1 && Math.abs(col - c0) <= 1) {
                setSelectedCells([...selectedCells, cellKey]);
            }
        } else {
            // Subsequent cells - must continue in same direction and be adjacent to last
            const [r0, c0] = selectedCells[0].split('-').map(Number);
            const [r1, c1] = selectedCells[1].split('-').map(Number);
            const dr = Math.sign(r1 - r0);
            const dc = Math.sign(c1 - c0);

            const [rLast, cLast] = selectedCells[selectedCells.length - 1].split('-').map(Number);
            const expectedRow = rLast + dr;
            const expectedCol = cLast + dc;

            if (row === expectedRow && col === expectedCol) {
                setSelectedCells([...selectedCells, cellKey]);
            }
        }
    };

    if (!currentPuzzle) {
        return <div className="word-search-puzzle">Loading puzzle...</div>;
    }

    return (
        <div className="word-search-puzzle">
            <h3 className="puzzle-title">{displayTitle}</h3>

            <div className="puzzle-layout">
                <div className="word-grid">
                    {currentGrid.map((row, rowIndex) => (
                        <div key={rowIndex} className="grid-row">
                            {row.map((letter, colIndex) => {
                                const cellKey = `${rowIndex}-${colIndex}`;
                                const isSelected = selectedCells.includes(cellKey);
                                const isFound = foundCells.includes(cellKey);

                                let className = 'grid-cell';
                                if (isFound) className += ' found';
                                if (isSelected) className += ' selected';

                                return (
                                    <div
                                        key={colIndex}
                                        className={className}
                                        onClick={() => handleCellClick(rowIndex, colIndex)}
                                    >
                                        {letter}
                                    </div>
                                );
                            })}
                        </div>
                    ))}
                </div>

                <div className="word-list">
                    <h4>Find these words:</h4>
                    <ul>
                        {currentWordList.map((word, index) => (
                            <li
                                key={index}
                                className={foundWords.includes(word) ? 'found' : ''}
                            >
                                {word}
                            </li>
                        ))}
                    </ul>

                    <div className="puzzle-controls">
                        {selectedCells.length > 0 && (
                            <button className="check-btn" onClick={checkWord}>
                                ✓ Check Word
                            </button>
                        )}

                        {/* Only show refresh for non-AI puzzles */}
                        {grid.length === 0 && (
                            <button className="reset-btn" onClick={loadRandomPuzzle} style={{ marginTop: '10px' }}>
                                ↻ New Puzzle
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default WordSearchPuzzle;
