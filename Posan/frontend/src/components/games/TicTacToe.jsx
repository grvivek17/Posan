import React, { useState, useEffect, useCallback, useRef } from 'react';
import './TicTacToe.css';

const THEMES = {
  classic: { name: 'Classic', x: '❌', o: '⭕', xLabel: 'X', oLabel: 'O' },
  animals: { name: 'Jungle Pets', x: '🦁', o: '🐯', xLabel: 'Lion', oLabel: 'Tiger' },
  space: { name: 'Galaxy Space', x: '🚀', o: '🛸', xLabel: 'Rocket', oLabel: 'UFO' },
  food: { name: 'Yummy Treats', x: '🍕', o: '🍔', xLabel: 'Pizza', oLabel: 'Burger' },
  magic: { name: 'Magic Stars', x: '⚡', o: '🌟', xLabel: 'Bolt', oLabel: 'Star' },
};

// Web Audio API Sound generator
const playTone = (freq, type = 'sine', duration = 0.15) => {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, ctx.currentTime);
    gain.gain.setValueAtTime(0.15, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + duration);
  } catch (e) {
    // Audio might be blocked if user hasn't interacted
  }
};

const playMoveSound = (isX) => {
  playTone(isX ? 520 : 440, 'sine', 0.12);
};

const playWinSound = () => {
  [440, 554, 659, 880].forEach((freq, i) => {
    setTimeout(() => playTone(freq, 'triangle', 0.25), i * 120);
  });
};

const playDrawSound = () => {
  [400, 350, 300].forEach((freq, i) => {
    setTimeout(() => playTone(freq, 'sawtooth', 0.2), i * 150);
  });
};

// Check Winner helper
const checkWinner = (squares, size = 3) => {
  const winLines = [];

  // Rows
  for (let r = 0; r < size; r++) {
    winLines.push(Array.from({ length: size }, (_, c) => r * size + c));
  }
  // Columns
  for (let c = 0; c < size; c++) {
    winLines.push(Array.from({ length: size }, (_, r) => r * size + c));
  }
  // Main diagonal
  winLines.push(Array.from({ length: size }, (_, i) => i * size + i));
  // Anti diagonal
  winLines.push(Array.from({ length: size }, (_, i) => i * size + (size - 1 - i)));

  for (let line of winLines) {
    const first = squares[line[0]];
    if (first && line.every(idx => squares[idx] === first)) {
      return { winner: first, line };
    }
  }

  if (squares.every(sq => sq !== null)) {
    return { winner: 'Draw', line: [] };
  }

  return null;
};

// Minimax for unbeatable 3x3 AI
const minimax = (board, depth, isMaximizing, aiSymbol, humanSymbol) => {
  const result = checkWinner(board, 3);
  if (result) {
    if (result.winner === aiSymbol) return 10 - depth;
    if (result.winner === humanSymbol) return depth - 10;
    if (result.winner === 'Draw') return 0;
  }
  if (depth >= 5) return 0; // limit depth for responsiveness

  const emptyIndices = board.map((val, idx) => (val === null ? idx : null)).filter(v => v !== null);

  if (isMaximizing) {
    let bestScore = -Infinity;
    for (let idx of emptyIndices) {
      board[idx] = aiSymbol;
      const score = minimax(board, depth + 1, false, aiSymbol, humanSymbol);
      board[idx] = null;
      bestScore = Math.max(score, bestScore);
    }
    return bestScore;
  } else {
    let bestScore = Infinity;
    for (let idx of emptyIndices) {
      board[idx] = humanSymbol;
      const score = minimax(board, depth + 1, true, aiSymbol, humanSymbol);
      board[idx] = null;
      bestScore = Math.min(score, bestScore);
    }
    return bestScore;
  }
};

const getAIMove = (board, difficulty, size, aiSymbol, humanSymbol) => {
  const emptyIndices = board.map((val, idx) => (val === null ? idx : null)).filter(v => v !== null);
  if (emptyIndices.length === 0) return null;

  // Easy: Random move
  if (difficulty === 'easy') {
    return emptyIndices[Math.floor(Math.random() * emptyIndices.length)];
  }

  // Medium: Block immediate opponent win or take immediate win, otherwise random
  if (difficulty === 'medium') {
    // 1. Can AI win immediately?
    for (let idx of emptyIndices) {
      board[idx] = aiSymbol;
      if (checkWinner(board, size)?.winner === aiSymbol) {
        board[idx] = null;
        return idx;
      }
      board[idx] = null;
    }
    // 2. Can Human win immediately? Block them!
    for (let idx of emptyIndices) {
      board[idx] = humanSymbol;
      if (checkWinner(board, size)?.winner === humanSymbol) {
        board[idx] = null;
        return idx;
      }
      board[idx] = null;
    }
    // 3. Take center if available
    const center = Math.floor((size * size) / 2);
    if (board[center] === null) return center;

    return emptyIndices[Math.floor(Math.random() * emptyIndices.length)];
  }

  // Hard / Unbeatable (for 3x3 use Minimax; for 4x4 use smart heuristic)
  if (difficulty === 'hard') {
    if (size === 3) {
      let bestScore = -Infinity;
      let move = emptyIndices[0];
      for (let idx of emptyIndices) {
        board[idx] = aiSymbol;
        const score = minimax(board, 0, false, aiSymbol, humanSymbol);
        board[idx] = null;
        if (score > bestScore) {
          bestScore = score;
          move = idx;
        }
      }
      return move;
    } else {
      // 4x4 Smart Heuristic
      for (let idx of emptyIndices) {
        board[idx] = aiSymbol;
        if (checkWinner(board, size)?.winner === aiSymbol) {
          board[idx] = null;
          return idx;
        }
        board[idx] = null;
      }
      for (let idx of emptyIndices) {
        board[idx] = humanSymbol;
        if (checkWinner(board, size)?.winner === humanSymbol) {
          board[idx] = null;
          return idx;
        }
        board[idx] = null;
      }
      return emptyIndices[Math.floor(Math.random() * emptyIndices.length)];
    }
  }

  return emptyIndices[0];
};

const TicTacToe = () => {
  const [gridSize, setGridSize] = useState(3); // 3 or 4
  const [themeKey, setThemeKey] = useState('classic');
  const [gameMode, setGameMode] = useState('ai'); // 'ai' or 'pvp'
  const [aiDifficulty, setAiDifficulty] = useState('medium'); // 'easy', 'medium', 'hard'

  const [board, setBoard] = useState(Array(9).fill(null));
  const [isXNext, setIsXNext] = useState(true);
  const [gameState, setGameState] = useState(null); // null, { winner: 'X'|'O'|'Draw', line: [] }
  const [scores, setScores] = useState({ x: 0, o: 0, ties: 0 });
  const [isAiThinking, setIsAiThinking] = useState(false);

  const theme = THEMES[themeKey];
  const totalCells = gridSize * gridSize;

  // Initialize/Reset Board
  const resetGame = useCallback(() => {
    setBoard(Array(gridSize * gridSize).fill(null));
    setIsXNext(true);
    setGameState(null);
    setIsAiThinking(false);
  }, [gridSize]);

  // When grid size changes, re-init
  useEffect(() => {
    resetGame();
  }, [gridSize, resetGame]);

  // AI turn trigger
  useEffect(() => {
    if (gameMode === 'ai' && !isXNext && !gameState && !isAiThinking) {
      setIsAiThinking(true);
      const timer = setTimeout(() => {
        const aiMove = getAIMove(board, aiDifficulty, gridSize, 'O', 'X');
        if (aiMove !== null) {
          makeMove(aiMove, 'O');
        }
        setIsAiThinking(false);
      }, 50);
      return () => clearTimeout(timer);
    }
  }, [isXNext, gameMode, gameState, board, aiDifficulty, gridSize, isAiThinking]);

  const makeMove = (index, symbol) => {
    if (board[index] || gameState) return;

    const newBoard = [...board];
    newBoard[index] = symbol;
    setBoard(newBoard);
    playMoveSound(symbol === 'X');

    const result = checkWinner(newBoard, gridSize);
    if (result) {
      setGameState(result);
      if (result.winner === 'X') {
        playWinSound();
        setScores(prev => ({ ...prev, x: prev.x + 1 }));
      } else if (result.winner === 'O') {
        playWinSound();
        setScores(prev => ({ ...prev, o: prev.o + 1 }));
      } else {
        playDrawSound();
        setScores(prev => ({ ...prev, ties: prev.ties + 1 }));
      }
    } else {
      setIsXNext(symbol !== 'X');
    }
  };

  const handleCellClick = (index) => {
    if (board[index] || gameState || isAiThinking) return;
    if (gameMode === 'ai' && !isXNext) return;

    const currentSymbol = isXNext ? 'X' : 'O';
    makeMove(index, currentSymbol);
  };

  const getCellDisplay = (val) => {
    if (val === 'X') return theme.x;
    if (val === 'O') return theme.o;
    return '';
  };

  const getStatusText = () => {
    if (gameState) {
      if (gameState.winner === 'Draw') return "🤝 It's a Tie / Draw!";
      if (gameState.winner === 'X') {
        return gameMode === 'ai' ? `🎉 You Won as ${theme.xLabel}!` : `🎉 Player 1 (${theme.xLabel}) Wins!`;
      }
      return gameMode === 'ai' ? `🤖 Computer (${theme.oLabel}) Wins!` : `🎉 Player 2 (${theme.oLabel}) Wins!`;
    }
    if (isAiThinking) return '🤖 Computer is thinking...';
    if (isXNext) {
      return gameMode === 'ai' ? `Your Turn (${theme.x})` : `Player 1's Turn (${theme.x})`;
    }
    return gameMode === 'ai' ? `Computer's Turn (${theme.o})` : `Player 2's Turn (${theme.o})`;
  };

  return (
    <div className="tictactoe-container">
      <div className="tictactoe-header">
        <h2 className="tictactoe-title">❌ Tic-Tac-Toe ⭕</h2>
        <p className="tictactoe-subtitle">Play against the Smart Computer or pass & play with a friend!</p>
      </div>

      {/* Control Bar */}
      <div className="tictactoe-controls">
        <div className="ttt-control-item">
          <label>Mode:</label>
          <div className="ttt-btn-group">
            <button
              className={`ttt-opt-btn ${gameMode === 'ai' ? 'active' : ''}`}
              onClick={() => { setGameMode('ai'); resetGame(); }}
            >
              🤖 vs Computer
            </button>
            <button
              className={`ttt-opt-btn ${gameMode === 'pvp' ? 'active' : ''}`}
              onClick={() => { setGameMode('pvp'); resetGame(); }}
            >
              👥 2 Players
            </button>
          </div>
        </div>

        {gameMode === 'ai' && (
          <div className="ttt-control-item">
            <label>Difficulty:</label>
            <select
              value={aiDifficulty}
              onChange={(e) => { setAiDifficulty(e.target.value); resetGame(); }}
              className="ttt-select"
            >
              <option value="easy">⭐ Easy (Friendly)</option>
              <option value="medium">⭐⭐ Medium (Clever)</option>
              <option value="hard">⭐⭐⭐ Hard (Champion)</option>
            </select>
          </div>
        )}

        <div className="ttt-control-item">
          <label>Grid Size:</label>
          <select
            value={gridSize}
            onChange={(e) => setGridSize(Number(e.target.value))}
            className="ttt-select"
          >
            <option value={3}>3 x 3 (Classic 3-in-a-row)</option>
            <option value={4}>4 x 4 (4-in-a-row Challenge)</option>
          </select>
        </div>

        <div className="ttt-control-item">
          <label>Theme:</label>
          <select
            value={themeKey}
            onChange={(e) => setThemeKey(e.target.value)}
            className="ttt-select"
          >
            {Object.entries(THEMES).map(([k, t]) => (
              <option key={k} value={k}>
                {t.x} {t.o} {t.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Scoreboard */}
      <div className="tictactoe-scoreboard">
        <div className={`score-card x-card ${isXNext && !gameState ? 'active-turn' : ''}`}>
          <div className="score-icon">{theme.x}</div>
          <div className="score-name">{gameMode === 'ai' ? 'Player (You)' : 'Player 1'}</div>
          <div className="score-number">{scores.x}</div>
        </div>

        <div className="score-card tie-card">
          <div className="score-icon">🤝</div>
          <div className="score-name">Ties</div>
          <div className="score-number">{scores.ties}</div>
        </div>

        <div className={`score-card o-card ${!isXNext && !gameState ? 'active-turn' : ''}`}>
          <div className="score-icon">{theme.o}</div>
          <div className="score-name">{gameMode === 'ai' ? 'Computer' : 'Player 2'}</div>
          <div className="score-number">{scores.o}</div>
        </div>
      </div>

      {/* Status Turn Indicator */}
      <div className={`tictactoe-status ${gameState ? (gameState.winner === 'Draw' ? 'status-draw' : 'status-win') : ''}`}>
        <span className="status-badge">{getStatusText()}</span>
      </div>

      {/* Game Board */}
      <div
        className={`tictactoe-grid grid-${gridSize}`}
        style={{
          gridTemplateColumns: `repeat(${gridSize}, 1fr)`,
          gridTemplateRows: `repeat(${gridSize}, 1fr)`
        }}
      >
        {board.map((cell, idx) => {
          const isWinningCell = gameState?.line?.includes(idx);
          return (
            <button
              key={idx}
              className={`tictactoe-cell ${cell ? 'filled' : ''} ${isWinningCell ? 'winning-cell' : ''}`}
              onClick={() => handleCellClick(idx)}
              disabled={!!cell || !!gameState || isAiThinking}
              aria-label={`Cell ${idx + 1}`}
            >
              <span className={`cell-content ${cell ? `symbol-${cell.toLowerCase()}` : ''}`}>
                {getCellDisplay(cell)}
              </span>
            </button>
          );
        })}
      </div>

      {/* Actions */}
      <div className="tictactoe-actions">
        <button className="ttt-action-btn reset-btn" onClick={resetGame}>
          🔄 Next Round
        </button>
        <button
          className="ttt-action-btn clear-score-btn"
          onClick={() => {
            setScores({ x: 0, o: 0, ties: 0 });
            resetGame();
          }}
        >
          🗑️ Reset Scores
        </button>
      </div>

      {/* Win Celebration Modal Overlay */}
      {gameState && (
        <div className="ttt-overlay">
          <div className="ttt-modal animate-pop">
            <div className="ttt-modal-icon">
              {gameState.winner === 'Draw' ? '🤝' : (gameState.winner === 'X' ? '🏆' : '🤖')}
            </div>
            <h3>
              {gameState.winner === 'Draw'
                ? "It's a Tie!"
                : `${gameState.winner === 'X' ? (gameMode === 'ai' ? 'Victory!' : 'Player 1 Wins!') : (gameMode === 'ai' ? 'Computer Wins!' : 'Player 2 Wins!')}`}
            </h3>
            <p>
              {gameState.winner === 'Draw'
                ? 'Well played by both sides! Ready for a rematch?'
                : `Awesome job making ${gridSize} in a row with ${gameState.winner === 'X' ? theme.x : theme.o}!`}
            </p>
            <div className="ttt-modal-btns">
              <button className="ttt-modal-play-btn" onClick={resetGame}>
                Play Again 🎮
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TicTacToe;
