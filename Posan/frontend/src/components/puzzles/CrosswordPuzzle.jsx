import { useState } from 'react';
import './CrosswordPuzzle.css';

const CrosswordPuzzle = ({ title = "Crossword" }) => {
    // Simple 5x5 crossword grid
    const grid = [
        [{ num: 1, letter: 'C' }, { letter: 'A' }, { letter: 'T' }, null, null],
        [{ letter: 'O' }, null, null, { num: 2, letter: 'D' }, { letter: 'O' }],
        [{ letter: 'W' }, null, { num: 3, letter: 'R' }, { letter: 'U' }, { letter: 'N' }],
        [null, { num: 4, letter: 'F' }, { letter: 'U' }, { letter: 'N' }, null],
        [null, null, null, null, null]
    ];

    const clues = {
        across: [
            { num: 1, clue: "A pet that says meow" },
            { num: 2, clue: "A pet that barks" },
            { num: 3, clue: "Move quickly on foot" },
            { num: 4, clue: "Something enjoyable, not boring" }
        ],
        down: [
            { num: 1, clue: "Farm animal that gives milk" }
        ]
    };

    const [userGrid, setUserGrid] = useState(
        grid.map(row => row.map(cell => cell ? { ...cell, userLetter: '' } : null))
    );

    const handleCellChange = (rowIndex, colIndex, value) => {
        const newGrid = userGrid.map(row => [...row]);
        if (newGrid[rowIndex][colIndex]) {
            newGrid[rowIndex][colIndex].userLetter = value.toUpperCase();
        }
        setUserGrid(newGrid);
    };

    const checkAnswers = () => {
        let correct = 0;
        let total = 0;

        userGrid.forEach((row, i) => {
            row.forEach((cell, j) => {
                if (cell) {
                    total++;
                    if (cell.userLetter === cell.letter) {
                        correct++;
                    }
                }
            });
        });

        alert(`You got ${correct} out of ${total} letters correct! ${correct === total ? '🎉 Perfect!' : 'Keep trying! 💪'}`);
    };

    return (
        <div className="crossword-puzzle">
            <h3 className="puzzle-title">{title}</h3>

            <div className="crossword-layout">
                <div className="crossword-grid">
                    {userGrid.map((row, rowIndex) => (
                        <div key={rowIndex} className="crossword-row">
                            {row.map((cell, colIndex) => {
                                if (!cell) {
                                    return <div key={colIndex} className="crossword-cell blocked"></div>;
                                }
                                return (
                                    <div key={colIndex} className="crossword-cell">
                                        {cell.num && <span className="cell-number">{cell.num}</span>}
                                        <input
                                            type="text"
                                            maxLength="1"
                                            value={cell.userLetter}
                                            onChange={(e) => handleCellChange(rowIndex, colIndex, e.target.value)}
                                            className="cell-input"
                                        />
                                    </div>
                                );
                            })}
                        </div>
                    ))}
                </div>

                <div className="clues-section">
                    <div className="clues-group">
                        <h4>Across</h4>
                        <ul>
                            {clues.across.map(clue => (
                                <li key={clue.num}>
                                    <strong>{clue.num}.</strong> {clue.clue}
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div className="clues-group">
                        <h4>Down</h4>
                        <ul>
                            {clues.down.map(clue => (
                                <li key={clue.num}>
                                    <strong>{clue.num}.</strong> {clue.clue}
                                </li>
                            ))}
                        </ul>
                    </div>
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
