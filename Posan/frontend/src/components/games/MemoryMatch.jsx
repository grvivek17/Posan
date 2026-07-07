import { useState, useEffect, useCallback } from 'react';
import './MemoryMatch.css';

const EMOJI_SETS = {
  animals: ['🐶', '🐱', '🐼', '🦁', '🐸', '🐵', '🐰', '🦊'],
  food: ['🍕', '🍔', '🍦', '🍩', '🍎', '🍪', '🧁', '🌮'],
  space: ['🚀', '🌟', '🌙', '🪐', '👽', '🛸', '☄️', '🌍'],
  nature: ['🌸', '🌻', '🍀', '🌈', '🦋', '🌊', '⛰️', '🔥'],
};

const DIFFICULTIES = {
  easy: { pairs: 4, label: 'Easy (4 pairs)' },
  medium: { pairs: 6, label: 'Medium (6 pairs)' },
  hard: { pairs: 8, label: 'Hard (8 pairs)' },
};

function shuffleArray(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

const MemoryMatch = () => {
  const [difficulty, setDifficulty] = useState('easy');
  const [theme, setTheme] = useState('animals');
  const [cards, setCards] = useState([]);
  const [flipped, setFlipped] = useState([]);
  const [matched, setMatched] = useState([]);
  const [moves, setMoves] = useState(0);
  const [gameWon, setGameWon] = useState(false);
  const [timer, setTimer] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [bestScore, setBestScore] = useState(null);

  const initGame = useCallback(() => {
    const numPairs = DIFFICULTIES[difficulty].pairs;
    const emojis = EMOJI_SETS[theme].slice(0, numPairs);
    const deck = shuffleArray([...emojis, ...emojis]).map((emoji, i) => ({
      id: i,
      emoji,
      isFlipped: false,
    }));
    setCards(deck);
    setFlipped([]);
    setMatched([]);
    setMoves(0);
    setGameWon(false);
    setTimer(0);
    setIsRunning(false);
  }, [difficulty, theme]);

  useEffect(() => {
    initGame();
  }, [initGame]);

  useEffect(() => {
    let interval;
    if (isRunning && !gameWon) {
      interval = setInterval(() => setTimer(t => t + 1), 1000);
    }
    return () => clearInterval(interval);
  }, [isRunning, gameWon]);

  useEffect(() => {
    if (matched.length > 0 && matched.length === cards.length) {
      setGameWon(true);
      setIsRunning(false);
      const key = `memory-best-${difficulty}`;
      const prev = localStorage.getItem(key);
      if (!prev || moves < parseInt(prev)) {
        localStorage.setItem(key, moves.toString());
        setBestScore(moves);
      }
    }
  }, [matched, cards.length, moves, difficulty]);

  useEffect(() => {
    const key = `memory-best-${difficulty}`;
    const prev = localStorage.getItem(key);
    setBestScore(prev ? parseInt(prev) : null);
  }, [difficulty]);

  const handleCardClick = (id) => {
    if (flipped.length === 2 || flipped.includes(id) || matched.includes(id)) return;

    if (!isRunning) setIsRunning(true);

    const newFlipped = [...flipped, id];
    setFlipped(newFlipped);

    if (newFlipped.length === 2) {
      setMoves(m => m + 1);
      const [first, second] = newFlipped;
      if (cards[first].emoji === cards[second].emoji) {
        setMatched(prev => [...prev, first, second]);
        setFlipped([]);
      } else {
        setTimeout(() => setFlipped([]), 800);
      }
    }
  };

  const formatTime = (s) => {
    const mins = Math.floor(s / 60);
    const secs = s % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const numPairs = DIFFICULTIES[difficulty].pairs;
  const cols = numPairs <= 4 ? 4 : numPairs <= 6 ? 4 : 4;

  return (
    <div className="memory-game">
      <div className="memory-header">
        <h2>🃏 Memory Match</h2>
        <p>Find all the matching pairs!</p>
      </div>

      <div className="memory-controls">
        <div className="control-group">
          <label>Difficulty:</label>
          <select value={difficulty} onChange={e => setDifficulty(e.target.value)}>
            {Object.entries(DIFFICULTIES).map(([k, v]) => (
              <option key={k} value={k}>{v.label}</option>
            ))}
          </select>
        </div>
        <div className="control-group">
          <label>Theme:</label>
          <select value={theme} onChange={e => setTheme(e.target.value)}>
            {Object.keys(EMOJI_SETS).map(t => (
              <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>
            ))}
          </select>
        </div>
        <button className="memory-reset-btn" onClick={initGame}>🔄 New Game</button>
      </div>

      <div className="memory-stats">
        <div className="stat-item">
          <span className="stat-label">Moves</span>
          <span className="stat-value">{moves}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Time</span>
          <span className="stat-value">{formatTime(timer)}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Pairs</span>
          <span className="stat-value">{matched.length / 2}/{numPairs}</span>
        </div>
        {bestScore !== null && (
          <div className="stat-item best">
            <span className="stat-label">Best</span>
            <span className="stat-value">{bestScore} moves</span>
          </div>
        )}
      </div>

      <div className="memory-grid" style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}>
        {cards.map(card => {
          const isFlippedCard = flipped.includes(card.id) || matched.includes(card.id);
          const isMatched = matched.includes(card.id);
          return (
            <div
              key={card.id}
              className={`memory-card ${isFlippedCard ? 'flipped' : ''} ${isMatched ? 'matched' : ''}`}
              onClick={() => handleCardClick(card.id)}
            >
              <div className="card-inner">
                <div className="card-front">❓</div>
                <div className="card-back">{card.emoji}</div>
              </div>
            </div>
          );
        })}
      </div>

      {gameWon && (
        <div className="memory-win-overlay">
          <div className="win-modal">
            <h2>🎉 You Won!</h2>
            <p>You matched all pairs in <strong>{moves} moves</strong> and <strong>{formatTime(timer)}</strong>!</p>
            {bestScore === moves && <p className="new-record">🏆 New Best Score!</p>}
            <button className="memory-reset-btn" onClick={initGame}>Play Again</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default MemoryMatch;
