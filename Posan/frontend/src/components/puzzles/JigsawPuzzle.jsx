import { useState, useEffect } from 'react';
import './JigsawPuzzle.css';

const JigsawPuzzle = ({ title = "Jigsaw Puzzle" }) => {
    // Simple 3x3 jigsaw (9 pieces)
    const totalPieces = 9;
    const gridSize = 3;

    const [pieces, setPieces] = useState([]);
    const [solvedPieces, setSolvedPieces] = useState(Array(totalPieces).fill(false));
    const [draggedPiece, setDraggedPiece] = useState(null);

    useEffect(() => {
        // Initialize shuffled pieces
        const initialPieces = Array.from({ length: totalPieces }, (_, i) => i);
        const shuffled = [...initialPieces].sort(() => Math.random() - 0.5);
        setPieces(shuffled);
    }, []);

    const handleDragStart = (e, piece) => {
        setDraggedPiece(piece);
        e.dataTransfer.effectAllowed = 'move';
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    };

    const handleDrop = (e, targetIndex) => {
        e.preventDefault();

        if (draggedPiece === null) return;

        const newPieces = [...pieces];
        const draggedIndex = pieces.indexOf(draggedPiece);

        // Swap pieces
        [newPieces[draggedIndex], newPieces[targetIndex]] =
            [newPieces[targetIndex], newPieces[draggedIndex]];

        setPieces(newPieces);

        // Check if piece is in correct position
        const newSolved = [...solvedPieces];
        newSolved[targetIndex] = newPieces[targetIndex] === targetIndex;
        newSolved[draggedIndex] = newPieces[draggedIndex] === draggedIndex;
        setSolvedPieces(newSolved);

        setDraggedPiece(null);

        // Check if puzzle is complete
        if (newPieces.every((piece, index) => piece === index)) {
            setTimeout(() => alert('🎉 Congratulations! Puzzle completed!'), 100);
        }
    };

    const getPieceColor = (pieceNum) => {
        const colors = [
            '#ff6b6b', '#4ecdc4', '#45b7d1', '#f7a400',
            '#95e1d3', '#ffc93c', '#ff85a2', '#91c4f2', '#b88ed1'
        ];
        return colors[pieceNum];
    };

    const resetPuzzle = () => {
        const shuffled = Array.from({ length: totalPieces }, (_, i) => i)
            .sort(() => Math.random() - 0.5);
        setPieces(shuffled);
        setSolvedPieces(Array(totalPieces).fill(false));
    };

    if (pieces.length === 0) return <div>Loading...</div>;

    return (
        <div className="jigsaw-puzzle">
            <h3 className="puzzle-title">{title}</h3>
            <p className="puzzle-hint">Drag and drop pieces to complete the puzzle!</p>

            <div className="jigsaw-grid">
                {pieces.map((piece, index) => {
                    const row = Math.floor(piece / gridSize);
                    const col = piece % gridSize;

                    return (
                        <div
                            key={index}
                            className={`jigsaw-piece ${solvedPieces[index] ? 'solved' : ''}`}
                            style={{ backgroundColor: getPieceColor(piece) }}
                            draggable
                            onDragStart={(e) => handleDragStart(e, piece)}
                            onDragOver={handleDragOver}
                            onDrop={(e) => handleDrop(e, index)}
                        >
                            <div className="piece-number">{piece + 1}</div>
                            <div className="piece-pattern">
                                <div className="pattern-dot" style={{
                                    top: `${row * 33}%`,
                                    left: `${col * 33}%`
                                }}></div>
                            </div>
                        </div>
                    );
                })}
            </div>

            <div className="completion-status">
                <div className="status-bar">
                    <div
                        className="status-progress"
                        style={{ width: `${(solvedPieces.filter(Boolean).length / totalPieces) * 100}%` }}
                    ></div>
                </div>
                <p>{solvedPieces.filter(Boolean).length} / {totalPieces} pieces correct</p>
            </div>

            <div className="puzzle-actions">
                <button className="action-btn reset-btn" onClick={resetPuzzle}>
                    ↻ Shuffle Again
                </button>
            </div>
        </div>
    );
};

export default JigsawPuzzle;
