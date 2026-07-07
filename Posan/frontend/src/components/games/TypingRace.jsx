import { useState, useEffect, useRef } from 'react';
import './TypingRace.css';

const WORD_LISTS = {
  easy: ['cat', 'dog', 'sun', 'hat', 'cup', 'red', 'big', 'run', 'fun', 'map', 'top', 'box', 'pen', 'bed', 'hot', 'ice', 'egg', 'bus', 'ant', 'owl'],
  medium: ['apple', 'house', 'water', 'happy', 'cloud', 'music', 'tiger', 'ocean', 'pizza', 'robot', 'sugar', 'green', 'story', 'light', 'plant', 'train', 'river', 'dance', 'brave', 'smile'],
  hard: ['elephant', 'dinosaur', 'rainbow', 'computer', 'mushroom', 'butterfly', 'treasure', 'calendar', 'sandwich', 'mountain', 'champion', 'princess', 'umbrella', 'firework', 'kangaroo', 'chocolate', 'adventure', 'beautiful'],
};

const GAME_DURATION = 30;

const TypingRace = () => {
  const [difficulty, setDifficulty] = useState('easy');
  const [gameState, setGameState] = useState('idle');
  const [currentWord, setCurrentWord] = useState('');
  const [typedText, setTypedText] = useState('');
  const [score, setScore] = useState(0);
  const [wordsTyped, setWordsTyped] = useState(0);
  const [timeLeft, setTimeLeft] = useState(GAME_DURATION);
  const [mistakes, setMistakes] = useState(0);
  const [highScore, setHighScore] = useState(0);
  const [wordQueue, setWordQueue] = useState([]);
  const [completedWords, setCompletedWords] = useState([]);
  const inputRef = useRef(null);

  useEffect(() => {
    const saved = localStorage.getItem(`typing-high-${difficulty}`);
    if (saved) setHighScore(parseInt(saved));
  }, [difficulty]);

  const getShuffledWords = (diff) => {
    const words = [...WORD_LISTS[diff]];
    for (let i = words.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [words[i], words[j]] = [words[j], words[i]];
    }
    return words;
  };

  const startGame = () => {
    const words = getShuffledWords(difficulty);
    setWordQueue(words);
    setCurrentWord(words[0]);
    setTypedText('');
    setScore(0);
    setWordsTyped(0);
    setTimeLeft(GAME_DURATION);
    setMistakes(0);
    setCompletedWords([]);
    setGameState('playing');
    setTimeout(() => inputRef.current?.focus(), 100);
  };

  useEffect(() => {
    if (gameState !== 'playing') return;
    if (timeLeft <= 0) {
      setGameState('finished');
      if (score > highScore) {
        localStorage.setItem(`typing-high-${difficulty}`, score.toString());
        setHighScore(score);
      }
      return;
    }
    const timer = setTimeout(() => setTimeLeft(t => t - 1), 1000);
    return () => clearTimeout(timer);
  }, [timeLeft, gameState, score, highScore, difficulty]);

  const handleInput = (e) => {
    if (gameState !== 'playing') return;
    const val = e.target.value.toLowerCase();
    setTypedText(val);

    if (val === currentWord) {
      const points = currentWord.length * 5;
      setScore(s => s + points);
      setWordsTyped(w => w + 1);
      setCompletedWords(prev => [...prev, currentWord]);
      setTypedText('');

      const nextIndex = (wordQueue.indexOf(currentWord) + 1) % wordQueue.length;
      if (nextIndex === 0) {
        const newWords = getShuffledWords(difficulty);
        setWordQueue(newWords);
        setCurrentWord(newWords[0]);
      } else {
        setCurrentWord(wordQueue[nextIndex]);
      }
    } else if (val.length > 0 && !currentWord.startsWith(val)) {
      setMistakes(m => m + 1);
    }
  };

  const getCharStatus = (index) => {
    if (index >= typedText.length) return 'pending';
    if (typedText[index] === currentWord[index]) return 'correct';
    return 'wrong';
  };

  const wpm = timeLeft < GAME_DURATION
    ? Math.round(wordsTyped / ((GAME_DURATION - timeLeft) / 60))
    : 0;

  const accuracy = wordsTyped + mistakes > 0
    ? Math.round((wordsTyped / (wordsTyped + mistakes)) * 100)
    : 100;

  return (
    <div className="typing-race">
      <div className="typing-header">
        <h2>⌨️ Typing Race</h2>
        <p>Type the words as fast as you can!</p>
      </div>

      {gameState === 'idle' && (
        <div className="typing-setup">
          <div className="typing-diff-options">
            {Object.entries(WORD_LISTS).map(([key]) => (
              <button
                key={key}
                className={`typing-diff-btn ${difficulty === key ? 'active' : ''}`}
                onClick={() => setDifficulty(key)}
              >
                {key.charAt(0).toUpperCase() + key.slice(1)}
                <span className="word-preview">
                  {WORD_LISTS[key].slice(0, 3).join(', ')}...
                </span>
              </button>
            ))}
          </div>
          {highScore > 0 && <p className="typing-high">🏆 Best: {highScore} pts</p>}
          <button className="typing-start-btn" onClick={startGame}>Start Typing! ⌨️</button>
        </div>
      )}

      {gameState === 'playing' && (
        <div className="typing-playing">
          <div className="typing-stats-bar">
            <div className="typing-stat">
              <span className="typing-stat-lbl">Score</span>
              <span className="typing-stat-val">{score}</span>
            </div>
            <div className={`typing-stat ${timeLeft <= 5 ? 'urgent' : ''}`}>
              <span className="typing-stat-lbl">Time</span>
              <span className="typing-stat-val">{timeLeft}s</span>
            </div>
            <div className="typing-stat">
              <span className="typing-stat-lbl">WPM</span>
              <span className="typing-stat-val">{wpm}</span>
            </div>
            <div className="typing-stat">
              <span className="typing-stat-lbl">Words</span>
              <span className="typing-stat-val">{wordsTyped}</span>
            </div>
          </div>

          <div className="word-display">
            {currentWord.split('').map((char, i) => (
              <span key={i} className={`word-char ${getCharStatus(i)}`}>{char}</span>
            ))}
          </div>

          <input
            ref={inputRef}
            type="text"
            className="typing-input"
            value={typedText}
            onChange={handleInput}
            placeholder="Type here..."
            autoFocus
            autoComplete="off"
            autoCapitalize="off"
          />

          {completedWords.length > 0 && (
            <div className="completed-words">
              {completedWords.slice(-8).map((w, i) => (
                <span key={i} className="completed-word">{w}</span>
              ))}
            </div>
          )}
        </div>
      )}

      {gameState === 'finished' && (
        <div className="typing-results">
          <h3>⏱️ Time's Up!</h3>
          <div className="typing-result-grid">
            <div className="typing-result-item">
              <span className="tr-emoji">🎯</span>
              <span className="tr-val">{score}</span>
              <span className="tr-lbl">Points</span>
            </div>
            <div className="typing-result-item">
              <span className="tr-emoji">📝</span>
              <span className="tr-val">{wordsTyped}</span>
              <span className="tr-lbl">Words</span>
            </div>
            <div className="typing-result-item">
              <span className="tr-emoji">⚡</span>
              <span className="tr-val">{wpm}</span>
              <span className="tr-lbl">WPM</span>
            </div>
            <div className="typing-result-item">
              <span className="tr-emoji">🎯</span>
              <span className="tr-val">{accuracy}%</span>
              <span className="tr-lbl">Accuracy</span>
            </div>
          </div>
          {score >= highScore && score > 0 && <p className="typing-new-record">🏆 New High Score!</p>}
          <button className="typing-start-btn" onClick={startGame}>Play Again</button>
          <button className="typing-back-btn" onClick={() => setGameState('idle')}>Change Difficulty</button>
        </div>
      )}
    </div>
  );
};

export default TypingRace;
