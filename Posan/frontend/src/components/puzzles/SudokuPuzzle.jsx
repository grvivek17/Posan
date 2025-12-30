import { useState } from 'react';
import './SudokuPuzzle.css';

const SudokuPuzzle = ({ initialGrid = null, title = "Sudoku" }) => {
    // Easy 4x4 Sudoku for kids
    const defaultGrid = [
        [1, 0, 0, 4],
        [0, 4, 1, 0],
        [0, 1, 4, 0],
        [4, 0, 0, 1]
    ];

    const solution = [
        [1, 2, 3, 4],
        [3, 4, 1, 2],
        [2, 1, 4, 3],
        [4, 3, 2, 1]
    ];

    const [grid, setGrid] = useState(initialGrid || defaultGrid);
    const [selectedCell, setSelectedCell] = useState(null);

    const handleCellClick = (row, col) => {
        if (defaultGrid[row][col] === 0) {
            setSelectedCell({ row, col });
        }
    };

    const handleNumberClick = (num) => {
        if (selectedCell) {
            const newGrid = grid.map(row => [...row]);
            newGrid[selectedCell.row][selectedCell.col] = num;
            setGrid(newGrid);
            setSelectedCell(null);
        }
    };

    const checkSolution = () => {
        const isCorrect = grid.every((row, i) =>
            row.every((cell, j) => cell === solution[i][j])
        );
        if (isCorrect) {
            alert('🎉 Congratulations! You solved it!');
        } else {
            alert('Not quite right. Keep trying! 💪');
        }
    };

    const resetPuzzle = () => {
        setGrid(defaultGrid.map(row => [...row]));
        setSelectedCell(null);
    };

    return (
        <div className="sudoku-puzzle">
            <h3 className="puzzle-title">{title}</h3>
            <p className="puzzle-hint">Fill in numbers 1-4 (each row, column, and 2x2 box must have all numbers)</p>

            <div className="sudoku-grid">
                {grid.map((row, rowIndex) => (
                    <div key={rowIndex} className="sudoku-row">
                        {row.map((cell, colIndex) => {
                            const isInitial = defaultGrid[rowIndex][colIndex] !== 0;
                            const isSelected = selectedCell?.row === rowIndex && selectedCell?.col === colIndex;
                            return (
                                <div
                                    key={colIndex}
                                    className={`sudoku-cell ${isInitial ? 'initial' : 'editable'} ${isSelected ? 'selected' : ''} ${(colIndex === 1 || colIndex === 2) ? 'border-right' : ''} ${(rowIndex === 1 || rowIndex === 2) ? 'border-bottom' : ''}`}
                                    onClick={() => handleCellClick(rowIndex, colIndex)}
                                >
                                    {cell !== 0 ? cell : ''}
                                </div>
                            );
                        })}
                    </div>
                ))}
            </div>

            <div className="number-pad">
                {[1, 2, 3, 4].map(num => (
                    <button
                        key={num}
                        className="number-btn"
                        onClick={() => handleNumberClick(num)}
                        disabled={!selectedCell}
                    >
                        {num}
                    </button>
                ))}
                <button className="number-btn clear-btn" onClick={() => selectedCell && handleNumberClick(0)}>
                    Clear
                </button>
            </div>

            <div className="puzzle-actions">
                <button className="action-btn check-btn" onClick={checkSolution}>
                    ✓ Check Solution
                </button>
                <button className="action-btn reset-btn" onClick={resetPuzzle}>
                    ↻ Reset
                </button>
            </div>
        </div>
    );
};

export default SudokuPuzzle;
