import { useState, useEffect } from 'react';
import './WordSearchPuzzle.css';
import { getRandomWordSearch } from '../../data/puzzleData';

const WordSearchPuzzle = ({ words = [], grid = [], title = "" }) => {
    const [foundWords, setFoundWords] = useState([]);
    const [selectedCells, setSelectedCells] = useState([]);
    const [isSelecting, setIsSelecting] = useState(false);
    const [currentPuzzle, setCurrentPuzzle] = useState(null);

    // Load a random puzzle on component mount
    useEffect(() => {
        const randomPuzzle = getRandomWordSearch();
        setCurrentPuzzle(randomPuzzle);
    }, []);

    // Use provided props or random puzzle data
    const puzzleToUse = currentPuzzle || { grid: [[]], words: [], title: "Word Search" };
    const currentGrid = grid.length > 0 ? grid : puzzleToUse.grid;
    const currentWords = words.length > 0 ? words : puzzleToUse.words;
    const puzzleTitle = title || puzzleToUse.title;

    // Return loading state if puzzle not loaded
    if (!currentPuzzle && grid.length === 0) {
        return <div className="word-search-puzzle">Loading puzzle...</div>;
    }

    const handleCellClick = (row, col) => {
        const cellKey = `${row}-${col}`;
        if (selectedCells.includes(cellKey)) {
            setSelectedCells(selectedCells.filter(c => c !== cellKey));
        } else {
            setSelectedCells([...selectedCells, cellKey]);
        }
    };

    const checkWord = () => {
        // Simple check - in a real app, you'd validate the selection
        if (selectedCells.length >= 3) {
            setFoundWords([...foundWords, selectedCells.join(',')]);
            setSelectedCells([]);
        }
    };

    return (
        <div className="word-search-puzzle">
            <h3 className="puzzle-title">{puzzleTitle}</h3>

            <div className="puzzle-layout">
                <div className="word-grid">
                    {currentGrid.map((row, rowIndex) => (
                        <div key={rowIndex} className="grid-row">
                            {row.map((letter, colIndex) => {
                                const cellKey = `${rowIndex}-${colIndex}`;
                                const isSelected = selectedCells.includes(cellKey);
                                return (
                                    <div
                                        key={colIndex}
                                        className={`grid-cell ${isSelected ? 'selected' : ''}`}
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
                        {currentWords.map((word, index) => (
                            <li
                                key={index}
                                className={foundWords.some(fw => fw.includes(word)) ? 'found' : ''}
                            >
                                {word}
                            </li>
                        ))}
                    </ul>
                    {selectedCells.length > 0 && (
                        <button className="check-btn" onClick={checkWord}>
                            ✓ Check Word
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default WordSearchPuzzle;
