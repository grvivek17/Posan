import { useState, useEffect, useCallback, useRef } from 'react';
import './MathQuiz.css';

const DIFFICULTIES = {
  easy: { max: 10, ops: ['+', '-'], time: 60, label: 'Easy (1-10)' },
  medium: { max: 25, ops: ['+', '-', '*'], time: 45, label: 'Medium (1-25)' },
  hard: { max: 50, ops: ['+', '-', '*', '/'], time: 30, label: 'Hard (1-50)' },
};

function generateQuestion(config) {
  const op = config.ops[Math.floor(Math.random() * config.ops.length)];
  let a, b, answer;

  switch (op) {
    case '+':
      a = Math.floor(Math.random() * config.max) + 1;
      b = Math.floor(Math.random() * config.max) + 1;
      answer = a + b;
      break;
    case '-':
      a = Math.floor(Math.random() * config.max) + 1;
      b = Math.floor(Math.random() * a) + 1;
      answer = a - b;
      break;
    case '*':
      a = Math.floor(Math.random() * 12) + 1;
      b = Math.floor(Math.random() * 12) + 1;
      answer = a * b;
      break;
    case '/':
      b = Math.floor(Math.random() * 12) + 1;
      answer = Math.floor(Math.random() * 12) + 1;
      a = b * answer;
      break;
    default:
      a = 1; b = 1; answer = 2;
  }

  return { a, b, op, answer, display: `${a} ${op} ${b} = ?` };
}

const MathQuiz = () => {
  const [difficulty, setDifficulty] = useState('easy');
  const [gameState, setGameState] = useState('idle'); // idle, playing, finished
  const [question, setQuestion] = useState(null);
  const [userAnswer, setUserAnswer] = useState('');
  const [score, setScore] = useState(0);
  const [streak, setStreak] = useState(0);
  const [bestStreak, setBestStreak] = useState(0);
  const [timeLeft, setTimeLeft] = useState(0);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [feedback, setFeedback] = useState(null);
  const [highScore, setHighScore] = useState(0);
  const inputRef = useRef(null);

  useEffect(() => {
    const saved = localStorage.getItem(`math-high-${difficulty}`);
    setHighScore(saved ? parseInt(saved) : 0);
  }, [difficulty]);

  const nextQuestion = useCallback(() => {
    const config = DIFFICULTIES[difficulty];
    setQuestion(generateQuestion(config));
    setUserAnswer('');
    setFeedback(null);
    setTimeout(() => inputRef.current?.focus(), 50);
  }, [difficulty]);

  const startGame = () => {
    const config = DIFFICULTIES[difficulty];
    setGameState('playing');
    setScore(0);
    setStreak(0);
    setBestStreak(0);
    setTotalQuestions(0);
    setTimeLeft(config.time);
    nextQuestion();
  };

  useEffect(() => {
    if (gameState !== 'playing') return;
    if (timeLeft <= 0) {
      setGameState('finished');
      if (score > highScore) {
        localStorage.setItem(`math-high-${difficulty}`, score.toString());
        setHighScore(score);
      }
      return;
    }
    const timer = setTimeout(() => setTimeLeft(t => t - 1), 1000);
    return () => clearTimeout(timer);
  }, [timeLeft, gameState, score, highScore, difficulty]);

  const submitAnswer = () => {
    if (!userAnswer.trim()) return;
    const parsed = parseInt(userAnswer);
    setTotalQuestions(t => t + 1);

    if (parsed === question.answer) {
      const points = 10 + streak * 2;
      setScore(s => s + points);
      setStreak(s => s + 1);
      setBestStreak(prev => Math.max(prev, streak + 1));
      setFeedback({ correct: true, points, message: getCorrectMessage() });
    } else {
      setStreak(0);
      setFeedback({ correct: false, answer: question.answer, message: 'Not quite!' });
    }

    setTimeout(nextQuestion, 1000);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') submitAnswer();
  };

  const getCorrectMessage = () => {
    const msgs = ['Awesome!', 'Great job!', 'Perfect!', 'You rock!', 'Amazing!', 'Brilliant!'];
    return msgs[Math.floor(Math.random() * msgs.length)];
  };

  const accuracy = totalQuestions > 0 ? Math.round((score > 0 ? (totalQuestions - (totalQuestions - Math.floor(score / 10))) : 0) / totalQuestions * 100) : 0;

  return (
    <div className="math-quiz">
      <div className="math-header">
        <h2>🧮 Math Quiz</h2>
        <p>Solve as many problems as you can!</p>
      </div>

      {gameState === 'idle' && (
        <div className="math-setup">
          <div className="difficulty-selector">
            {Object.entries(DIFFICULTIES).map(([key, val]) => (
              <button
                key={key}
                className={`diff-btn ${difficulty === key ? 'active' : ''}`}
                onClick={() => setDifficulty(key)}
              >
                {val.label}
                <span className="diff-time">{val.time}s</span>
              </button>
            ))}
          </div>
          {highScore > 0 && (
            <p className="high-score-display">🏆 Best Score: {highScore} points</p>
          )}
          <button className="math-start-btn" onClick={startGame}>
            Start Quiz! 🚀
          </button>
        </div>
      )}

      {gameState === 'playing' && (
        <div className="math-playing">
          <div className="math-top-bar">
            <div className="math-stat">
              <span className="math-stat-label">Score</span>
              <span className="math-stat-value">{score}</span>
            </div>
            <div className={`math-stat timer ${timeLeft <= 10 ? 'urgent' : ''}`}>
              <span className="math-stat-label">Time</span>
              <span className="math-stat-value">{timeLeft}s</span>
            </div>
            <div className="math-stat">
              <span className="math-stat-label">Streak</span>
              <span className="math-stat-value">🔥 {streak}</span>
            </div>
          </div>

          <div className={`math-question-card ${feedback ? (feedback.correct ? 'correct-flash' : 'wrong-flash') : ''}`}>
            <div className="question-text">{question?.display}</div>
            <div className="answer-row">
              <input
                ref={inputRef}
                type="number"
                className="math-input"
                value={userAnswer}
                onChange={e => setUserAnswer(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="?"
                autoFocus
              />
              <button className="math-submit-btn" onClick={submitAnswer}>Go!</button>
            </div>
          </div>

          {feedback && (
            <div className={`math-feedback ${feedback.correct ? 'correct' : 'wrong'}`}>
              {feedback.correct
                ? `✅ ${feedback.message} +${feedback.points} pts`
                : `❌ ${feedback.message} Answer: ${feedback.answer}`
              }
            </div>
          )}
        </div>
      )}

      {gameState === 'finished' && (
        <div className="math-results">
          <h3>⏱️ Time's Up!</h3>
          <div className="results-grid">
            <div className="result-item">
              <span className="result-emoji">🎯</span>
              <span className="result-val">{score}</span>
              <span className="result-lbl">Points</span>
            </div>
            <div className="result-item">
              <span className="result-emoji">📝</span>
              <span className="result-val">{totalQuestions}</span>
              <span className="result-lbl">Questions</span>
            </div>
            <div className="result-item">
              <span className="result-emoji">🔥</span>
              <span className="result-val">{bestStreak}</span>
              <span className="result-lbl">Best Streak</span>
            </div>
          </div>
          {score >= highScore && score > 0 && (
            <p className="new-high-score">🏆 New High Score!</p>
          )}
          <button className="math-start-btn" onClick={startGame}>Play Again</button>
          <button className="math-back-btn" onClick={() => setGameState('idle')}>Change Difficulty</button>
        </div>
      )}
    </div>
  );
};

export default MathQuiz;
