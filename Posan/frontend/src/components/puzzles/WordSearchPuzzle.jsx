import { useState } from 'react';
import './WordSearchPuzzle.css';

const WordSearchPuzzle = ({ words = [], grid = [], title = "Word Search" }) => {
    const [foundWords, setFoundWords] = useState([]);
    const [selectedCells, setSelectedCells] = useState([]);
    const [isSelecting, setIsSelecting] = useState(false);

    // Sample grid if none provided
    const defaultGrid = [
        ['C', 'A', 'T', 'S', 'P', 'L', 'A', 'Y'],
        ['O', 'D', 'O', 'G', 'M', 'O', 'V', 'E'],
        ['L', 'I', 'R', 'U', 'N', 'S', 'W', 'R'],
        ['O', 'S', 'K', 'I', 'P', 'E', 'I', 'B'],
        ['R', 'H', 'O', 'P', 'G', 'A', 'M', 'E'],
        ['S', 'J', 'U', 'M', 'P', 'L', 'E', 'A'],
        ['F', 'U', 'N', 'B', 'A', 'L', 'L', 'P'],
        ['D', 'A', 'N', 'C', 'E', 'T', 'O', 'Y']
    ];

    const defaultWords = ['CAT', 'DOG', 'RUN', 'JUMP', 'PLAY', 'FUN', 'GAME', 'TOY'];

    const currentGrid = grid.length > 0 ? grid : defaultGrid;
    const currentWords = words.length > 0 ? words : defaultWords;

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
            <h3 className="puzzle-title">{title}</h3>

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
