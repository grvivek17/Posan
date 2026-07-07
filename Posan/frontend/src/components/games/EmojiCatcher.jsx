import { useState, useEffect, useRef, useCallback } from 'react';
import './EmojiCatcher.css';

const EMOJIS = ['🍎', '🌟', '🎈', '🦋', '🍕', '🎸', '🏀', '🎯', '💎', '🍩', '🚀', '🌈'];
const BAD_EMOJIS = ['💣', '🌵', '👻'];
const GAME_DURATION = 30;

const EmojiCatcher = () => {
  const [gameState, setGameState] = useState('idle');
  const [score, setScore] = useState(0);
  const [timeLeft, setTimeLeft] = useState(GAME_DURATION);
  const [fallingItems, setFallingItems] = useState([]);
  const [caught, setCaught] = useState([]);
  const [highScore, setHighScore] = useState(0);
  const [combo, setCombo] = useState(0);
  const [showEffect, setShowEffect] = useState(null);
  const areaRef = useRef(null);
  const itemIdRef = useRef(0);

  useEffect(() => {
    const saved = localStorage.getItem('emoji-catch-high');
    if (saved) setHighScore(parseInt(saved));
  }, []);

  const spawnItem = useCallback(() => {
    const isBad = Math.random() < 0.2;
    const pool = isBad ? BAD_EMOJIS : EMOJIS;
    const emoji = pool[Math.floor(Math.random() * pool.length)];
    const id = itemIdRef.current++;
    const left = 5 + Math.random() * 85;
    const speed = 2 + Math.random() * 3;
    const size = 1.5 + Math.random() * 1;

    return { id, emoji, left, speed, top: -10, isBad, size };
  }, []);

  useEffect(() => {
    if (gameState !== 'playing') return;
    if (timeLeft <= 0) {
      setGameState('finished');
      if (score > highScore) {
        localStorage.setItem('emoji-catch-high', score.toString());
        setHighScore(score);
      }
      return;
    }
    const timer = setTimeout(() => setTimeLeft(t => t - 1), 1000);
    return () => clearTimeout(timer);
  }, [timeLeft, gameState, score, highScore]);

  useEffect(() => {
    if (gameState !== 'playing') return;

    const spawnInterval = setInterval(() => {
      setFallingItems(prev => [...prev, spawnItem()]);
    }, 600 + Math.random() * 400);

    return () => clearInterval(spawnInterval);
  }, [gameState, spawnItem]);

  useEffect(() => {
    if (gameState !== 'playing') return;

    const moveInterval = setInterval(() => {
      setFallingItems(prev =>
        prev
          .map(item => ({ ...item, top: item.top + item.speed }))
          .filter(item => item.top < 110)
      );
    }, 50);

    return () => clearInterval(moveInterval);
  }, [gameState]);

  const catchItem = (item, e) => {
    e.stopPropagation();
    if (gameState !== 'playing') return;

    setFallingItems(prev => prev.filter(i => i.id !== item.id));

    if (item.isBad) {
      setScore(s => Math.max(0, s - 15));
      setCombo(0);
      setShowEffect({ x: e.clientX, y: e.clientY, text: '-15', type: 'bad' });
    } else {
      const points = 10 + combo * 3;
      setScore(s => s + points);
      setCombo(c => c + 1);
      setCaught(prev => [...prev.slice(-20), item.emoji]);
      setShowEffect({ x: e.clientX, y: e.clientY, text: `+${points}`, type: 'good' });
    }

    setTimeout(() => setShowEffect(null), 600);
  };

  const startGame = () => {
    setGameState('playing');
    setScore(0);
    setTimeLeft(GAME_DURATION);
    setFallingItems([]);
    setCaught([]);
    setCombo(0);
    itemIdRef.current = 0;
  };

  return (
    <div className="emoji-catcher">
      <div className="catcher-header">
        <h2>🎯 Emoji Catcher</h2>
        <p>Tap the good emojis, avoid the bad ones!</p>
      </div>

      {gameState === 'idle' && (
        <div className="catcher-setup">
          <div className="catcher-rules">
            <div className="rule-item good">
              <span className="rule-emojis">{EMOJIS.slice(0, 5).join(' ')}</span>
              <span className="rule-text">Catch these! +10 pts</span>
            </div>
            <div className="rule-item bad">
              <span className="rule-emojis">{BAD_EMOJIS.join(' ')}</span>
              <span className="rule-text">Avoid these! -15 pts</span>
            </div>
          </div>
          {highScore > 0 && <p className="catcher-high">🏆 Best: {highScore} pts</p>}
          <button className="catcher-start-btn" onClick={startGame}>Start Catching! 🎯</button>
        </div>
      )}

      {gameState === 'playing' && (
        <>
          <div className="catcher-top-bar">
            <div className="catcher-stat">🎯 {score}</div>
            <div className={`catcher-stat timer ${timeLeft <= 5 ? 'urgent' : ''}`}>⏱️ {timeLeft}s</div>
            {combo > 1 && <div className="catcher-stat combo">🔥 x{combo}</div>}
          </div>

          <div className="catch-area" ref={areaRef}>
            {fallingItems.map(item => (
              <div
                key={item.id}
                className={`falling-item ${item.isBad ? 'bad' : 'good'}`}
                style={{
                  left: `${item.left}%`,
                  top: `${item.top}%`,
                  fontSize: `${item.size}rem`,
                }}
                onClick={e => catchItem(item, e)}
              >
                {item.emoji}
              </div>
            ))}
            {showEffect && (
              <div
                className={`catch-effect ${showEffect.type}`}
                style={{ left: showEffect.x, top: showEffect.y }}
              >
                {showEffect.text}
              </div>
            )}
          </div>
        </>
      )}

      {gameState === 'finished' && (
        <div className="catcher-results">
          <h3>🎉 Great Catching!</h3>
          <div className="catcher-final-score">
            <span className="final-label">Final Score</span>
            <span className="final-value">{score}</span>
          </div>
          <div className="caught-display">
            <p>You caught:</p>
            <div className="caught-emojis">{caught.join(' ')}</div>
          </div>
          {score >= highScore && score > 0 && <p className="catcher-new-record">🏆 New Record!</p>}
          <button className="catcher-start-btn" onClick={startGame}>Play Again</button>
        </div>
      )}
    </div>
  );
};

export default EmojiCatcher;
