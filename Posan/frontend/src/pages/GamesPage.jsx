import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import MemoryMatch from '../components/games/MemoryMatch';
import MathQuiz from '../components/games/MathQuiz';
import EmojiCatcher from '../components/games/EmojiCatcher';
import TypingRace from '../components/games/TypingRace';
import ColorMatch from '../components/games/ColorMatch';
import './GamesPage.css';

const GAMES = [
  {
    id: 'memory',
    name: 'Memory Match',
    icon: '🃏',
    description: 'Flip cards and find matching pairs!',
    color: '#8B5CF6',
    gradient: 'linear-gradient(135deg, #8B5CF6, #6D28D9)',
    component: MemoryMatch,
  },
  {
    id: 'math',
    name: 'Math Quiz',
    icon: '🧮',
    description: 'Solve math problems against the clock!',
    color: '#FF9F1C',
    gradient: 'linear-gradient(135deg, #FF9F1C, #F59E0B)',
    component: MathQuiz,
  },
  {
    id: 'emoji',
    name: 'Emoji Catcher',
    icon: '🎯',
    description: 'Catch falling emojis before they escape!',
    color: '#EC4899',
    gradient: 'linear-gradient(135deg, #EC4899, #BE185D)',
    component: EmojiCatcher,
  },
  {
    id: 'typing',
    name: 'Typing Race',
    icon: '⌨️',
    description: 'Type words as fast as you can!',
    color: '#10B981',
    gradient: 'linear-gradient(135deg, #10B981, #059669)',
    component: TypingRace,
  },
  {
    id: 'color',
    name: 'Color Match',
    icon: '🎨',
    description: 'Match colors - don\'t get tricked by the words!',
    color: '#4ECDC4',
    gradient: 'linear-gradient(135deg, #4ECDC4, #0D9488)',
    component: ColorMatch,
  },
];

const GamesPage = () => {
  const [activeGame, setActiveGame] = useState(null);
  const navigate = useNavigate();

  const ActiveComponent = activeGame ? GAMES.find(g => g.id === activeGame)?.component : null;
  const activeGameData = activeGame ? GAMES.find(g => g.id === activeGame) : null;

  return (
    <div className="games-page">
      <div className="games-header">
        <h1 className="games-title">🎮 Game Zone</h1>
        <p className="games-subtitle">Pick a game and have fun learning!</p>
      </div>

      {!activeGame ? (
        <div className="games-grid-container">
          <div className="games-grid">
            {GAMES.map((game) => (
              <div
                key={game.id}
                className="game-card"
                style={{ background: game.gradient }}
                onClick={() => setActiveGame(game.id)}
              >
                <div className="game-card-icon">{game.icon}</div>
                <h3 className="game-card-name">{game.name}</h3>
                <p className="game-card-desc">{game.description}</p>
                <div className="game-card-play">Play Now →</div>
              </div>
            ))}
          </div>

          <div className="games-puzzle-link">
            <p>Looking for puzzles?</p>
            <button className="puzzle-zone-btn" onClick={() => navigate('/puzzle-zone')}>
              🧩 Go to Puzzle Zone
            </button>
          </div>
        </div>
      ) : (
        <div className="active-game-container">
          <button
            className="back-to-games-btn"
            onClick={() => setActiveGame(null)}
          >
            ← Back to Games
          </button>
          <div className="active-game-wrapper">
            {ActiveComponent && <ActiveComponent />}
          </div>
        </div>
      )}
    </div>
  );
};

export default GamesPage;
