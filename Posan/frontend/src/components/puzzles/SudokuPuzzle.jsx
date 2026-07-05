import { useState, useEffect } from 'react';
import './SudokuPuzzle.css';
import { gamificationService } from '../../services/gamificationService';

const SudokuPuzzle = ({ initialGrid = null, title = "Sudoku" }) => {
    // Generate a random 4x4 Sudoku puzzle
    const generateSudokuPuzzle = () => {
        const puzzles = [
            {
                grid: [
                    [1, 0, 0, 4],
                    [0, 4, 1, 0],
                    [0, 1, 4, 0],
                    [4, 0, 0, 1]
                ],
                solution: [
                    [1, 2, 3, 4],
                    [3, 4, 1, 2],
                    [2, 1, 4, 3],
                    [4, 3, 2, 1]
                ]
            },
            {
                grid: [
                    [0, 3, 0, 2],
                    [2, 0, 3, 0],
                    [0, 2, 0, 3],
                    [3, 0, 2, 0]
                ],
                solution: [
                    [1, 3, 4, 2],
                    [2, 4, 3, 1],
                    [4, 2, 1, 3],
                    [3, 1, 2, 4]
                ]
            },
            {
                grid: [
                    [0, 0, 3, 1],
                    [3, 1, 0, 0],
                    [0, 0, 1, 3],
                    [1, 3, 0, 0]
                ],
                solution: [
                    [4, 2, 3, 1],
                    [3, 1, 4, 2],
                    [2, 4, 1, 3],
                    [1, 3, 2, 4]
                ]
            },
            {
                grid: [
                    [4, 0, 0, 3],
                    [0, 2, 4, 0],
                    [0, 4, 2, 0],
                    [3, 0, 0, 4]
                ],
                solution: [
                    [4, 1, 2, 3],
                    [3, 2, 4, 1],
                    [1, 4, 3, 2],
                    [2, 3, 1, 4]
                ]
            }
        ];

        return puzzles[Math.floor(Math.random() * puzzles.length)];
    };

    const [currentPuzzle, setCurrentPuzzle] = useState(null);
    const [grid, setGrid] = useState(null);
    const [selectedCell, setSelectedCell] = useState(null);
    const [completed, setCompleted] = useState(false);

    // Generate new puzzle on mount
    useEffect(() => {
        const newPuzzle = generateSudokuPuzzle();
        setCurrentPuzzle(newPuzzle);
        setGrid(newPuzzle.grid.map(row => [...row]));
    }, []);

    const handleCellClick = (row, col) => {
        if (currentPuzzle && currentPuzzle.grid[row][col] === 0) {
            setSelectedCell({ row, col });
        }
    };

    const handleNumberClick = (num) => {
        if (selectedCell && grid) {
            const newGrid = grid.map(row => [...row]);
            newGrid[selectedCell.row][selectedCell.col] = num;
            setGrid(newGrid);
            setSelectedCell(null);

            // Check if puzzle is complete
            const isComplete = newGrid.every((row, i) =>
                row.every((cell, j) => cell === currentPuzzle.solution[i][j])
            );

            if (isComplete && !completed) {
                setCompleted(true);
                setTimeout(async () => {
                    // Award points
                    try {
                        await gamificationService.addPoints('puzzle_solved', {
                            puzzle_type: 'sudoku'
                        });
                        alert('🎉 Congratulations! You solved the Sudoku! Points awarded!');
                    } catch (error) {
                        alert('🎉 Congratulations! You solved the Sudoku!');
                    }
                }, 100);
            }
        }
    };

    const checkSolution = () => {
        if (!grid || !currentPuzzle) return;

        const isCorrect = grid.every((row, i) =>
            row.every((cell, j) => cell === currentPuzzle.solution[i][j])
        );
        if (isCorrect) {
            if (!completed) {
                setCompleted(true);
                gamificationService.addPoints('puzzle_solved', {
                    puzzle_type: 'sudoku'
                }).then(() => {
                    alert('🎉 Congratulations! You solved it! Points awarded!');
                }).catch(() => {
                    alert('🎉 Congratulations! You solved it!');
                });
            } else {
                alert('🎉 Already completed!');
            }
        } else {
            alert('Not quite right. Keep trying! 💪');
        }
    };

    const resetPuzzle = () => {
        const newPuzzle = generateSudokuPuzzle();
        setCurrentPuzzle(newPuzzle);
        setGrid(newPuzzle.grid.map(row => [...row]));
        setSelectedCell(null);
        setCompleted(false);
    };

    if (!grid || !currentPuzzle) {
        return <div className="sudoku-puzzle">Loading puzzle...</div>;
    }

    return (
        <div className="sudoku-puzzle">
            <h3 className="puzzle-title">{title}</h3>
            <p className="puzzle-hint">Fill in numbers 1-4 (each row, column, and 2x2 box must have all numbers)</p>

            <div className="sudoku-grid">
                {grid.map((row, rowIndex) => (
                    <div key={rowIndex} className="sudoku-row">
                        {row.map((cell, colIndex) => {
                            const isInitial = currentPuzzle.grid[rowIndex][colIndex] !== 0;
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
