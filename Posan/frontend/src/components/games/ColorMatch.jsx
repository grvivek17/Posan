import { useState, useEffect, useCallback } from 'react';
import './ColorMatch.css';

const COLORS = [
  { name: 'Red', hex: '#EF4444' },
  { name: 'Blue', hex: '#3B82F6' },
  { name: 'Green', hex: '#10B981' },
  { name: 'Yellow', hex: '#EAB308' },
  { name: 'Purple', hex: '#8B5CF6' },
  { name: 'Orange', hex: '#F97316' },
  { name: 'Pink', hex: '#EC4899' },
  { name: 'Teal', hex: '#14B8A6' },
];

const GAME_ROUNDS = 15;
const TIME_PER_ROUND = 5;

const ColorMatch = () => {
  const [gameState, setGameState] = useState('idle');
  const [round, setRound] = useState(0);
  const [score, setScore] = useState(0);
  const [displayWord, setDisplayWord] = useState('');
  const [displayColor, setDisplayColor] = useState('');
  const [options, setOptions] = useState([]);
  const [feedback, setFeedback] = useState(null);
  const [timeLeft, setTimeLeft] = useState(TIME_PER_ROUND);
  const [streak, setStreak] = useState(0);
  const [highScore, setHighScore] = useState(0);
  const [correctAnswer, setCorrectAnswer] = useState('');
  const [totalTime, setTotalTime] = useState(0);

  useEffect(() => {
    const saved = localStorage.getItem('color-match-high');
    if (saved) setHighScore(parseInt(saved));
  }, []);

  const generateRound = useCallback(() => {
    // Pick a random color for the text
    const textColor = COLORS[Math.floor(Math.random() * COLORS.length)];
    // Pick a different color for the display color (the trap)
    let inkColor;
    do {
      inkColor = COLORS[Math.floor(Math.random() * COLORS.length)];
    } while (inkColor.name === textColor.name);

    // The correct answer is the INK color (the actual color shown), not the word
    const correct = inkColor;

    // Build 4 options including the correct one
    const optionSet = new Set([correct.name]);
    // Add the word as a distractor (this is the trap)
    optionSet.add(textColor.name);
    while (optionSet.size < 4) {
      const c = COLORS[Math.floor(Math.random() * COLORS.length)];
      optionSet.add(c.name);
    }

    const shuffled = [...optionSet].sort(() => Math.random() - 0.5);

    setDisplayWord(textColor.name);
    setDisplayColor(inkColor.hex);
    setCorrectAnswer(inkColor.name);
    setOptions(shuffled);
    setFeedback(null);
    setTimeLeft(TIME_PER_ROUND);
  }, []);

  const startGame = () => {
    setGameState('playing');
    setRound(1);
    setScore(0);
    setStreak(0);
    setTotalTime(0);
    generateRound();
  };

  useEffect(() => {
    if (gameState !== 'playing' || feedback) return;
    if (timeLeft <= 0) {
      handleAnswer(null);
      return;
    }
    const timer = setTimeout(() => setTimeLeft(t => t - 1), 1000);
    return () => clearTimeout(timer);
  }, [timeLeft, gameState, feedback]);

  const handleAnswer = (answer) => {
    if (feedback) return;
    const timeTaken = TIME_PER_ROUND - timeLeft;
    setTotalTime(t => t + timeTaken);

    if (answer === correctAnswer) {
      const timeBonus = Math.max(0, (TIME_PER_ROUND - timeTaken) * 5);
      const points = 20 + timeBonus + streak * 5;
      setScore(s => s + points);
      setStreak(s => s + 1);
      setFeedback({ correct: true, points });
    } else {
      setStreak(0);
      setFeedback({ correct: false, correctAnswer });
    }

    setTimeout(() => {
      if (round >= GAME_ROUNDS) {
        setGameState('finished');
        const finalScore = score + (feedback?.correct ? feedback.points : 0);
        if (finalScore > highScore) {
          localStorage.setItem('color-match-high', finalScore.toString());
          setHighScore(finalScore);
        }
      } else {
        setRound(r => r + 1);
        generateRound();
      }
    }, 1200);
  };

  return (
    <div className="color-match">
      <div className="color-header">
        <h2>🎨 Color Match</h2>
        <p>What COLOR is the text shown in? Don't read the word!</p>
      </div>

      {gameState === 'idle' && (
        <div className="color-setup">
          <div className="color-instructions">
            <div className="instruction-example">
              <span className="example-word" style={{ color: '#3B82F6' }}>Red</span>
              <span className="example-arrow">→</span>
              <span className="example-answer">Answer: Blue (the ink color!)</span>
            </div>
            <p className="instruction-text">
              The word says one color, but it's displayed in a DIFFERENT color. 
              Pick the color the text is SHOWN in, not what it says!
            </p>
          </div>
          {highScore > 0 && <p className="color-high">🏆 Best: {highScore} pts</p>}
          <button className="color-start-btn" onClick={startGame}>Start Game! 🎨</button>
        </div>
      )}

      {gameState === 'playing' && (
        <div className="color-playing">
          <div className="color-top-bar">
            <div className="color-stat">🎯 {score}</div>
            <div className="color-stat">Round {round}/{GAME_ROUNDS}</div>
            <div className={`color-stat ${timeLeft <= 2 ? 'urgent' : ''}`}>⏱️ {timeLeft}s</div>
            {streak > 1 && <div className="color-stat streak">🔥 x{streak}</div>}
          </div>

          <div className="color-display-card">
            <div className="color-word" style={{ color: displayColor }}>
              {displayWord}
            </div>
            <p className="color-prompt">What COLOR is this text shown in?</p>
          </div>

          <div className="color-options">
            {options.map((opt) => (
              <button
                key={opt}
                className={`color-option ${
                  feedback
                    ? opt === correctAnswer
                      ? 'correct'
                      : feedback && !feedback.correct && opt === feedback.correctAnswer
                        ? 'correct'
                        : 'disabled'
                    : ''
                }`}
                onClick={() => handleAnswer(opt)}
                disabled={!!feedback}
                style={{
                  borderColor: COLORS.find(c => c.name === opt)?.hex,
                }}
              >
                <span
                  className="option-dot"
                  style={{ backgroundColor: COLORS.find(c => c.name === opt)?.hex }}
                ></span>
                {opt}
              </button>
            ))}
          </div>

          {feedback && (
            <div className={`color-feedback ${feedback.correct ? 'correct' : 'wrong'}`}>
              {feedback.correct
                ? `✅ Correct! +${feedback.points} pts`
                : `❌ Wrong! It was ${correctAnswer}`
              }
            </div>
          )}

          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${(round / GAME_ROUNDS) * 100}%` }}></div>
          </div>
        </div>
      )}

      {gameState === 'finished' && (
        <div className="color-results">
          <h3>🎨 Game Over!</h3>
          <div className="color-final-score">
            <span className="cf-label">Final Score</span>
            <span className="cf-value">{score}</span>
          </div>
          <div className="color-stats-row">
            <div className="cs-item">
              <span className="cs-val">{GAME_ROUNDS}</span>
              <span className="cs-lbl">Rounds</span>
            </div>
            <div className="cs-item">
              <span className="cs-val">{Math.round(totalTime / GAME_ROUNDS * 10) / 10}s</span>
              <span className="cs-lbl">Avg Time</span>
            </div>
          </div>
          {score >= highScore && score > 0 && <p className="color-new-record">🏆 New Record!</p>}
          <button className="color-start-btn" onClick={startGame}>Play Again</button>
          <button className="color-back-btn" onClick={() => setGameState('idle')}>Back</button>
        </div>
      )}
    </div>
  );
};

export default ColorMatch;
