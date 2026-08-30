import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import MemoryMatch from '../components/games/MemoryMatch';
import MathQuiz from '../components/games/MathQuiz';
import EmojiCatcher from '../components/games/EmojiCatcher';
import TypingRace from '../components/games/TypingRace';
import ColorMatch from '../components/games/ColorMatch';
import BubblePop from '../components/games/BubblePop';
import GardenBuilder from '../components/games/GardenBuilder';
import AnimalCare from '../components/games/AnimalCare';
import ColoringCanvas from '../components/games/ColoringCanvas';
import TicTacToe from '../components/games/TicTacToe';
import './GamesPage.css';

const RELAXING_GAMES = [
  {
    id: 'bubbles',
    name: 'Bubble Pop',
    icon: '',
    description: 'Pop gentle floating bubbles and collect sparkles!',
    color: '#BAE1FF',
    gradient: 'linear-gradient(135deg, #BAE1FF, #E8BAFF)',
    component: BubblePop,
  },
  {
    id: 'garden',
    name: 'My Garden',
    icon: '',
    description: 'Plant flowers and build your own beautiful garden!',
    color: '#BAFFC9',
    gradient: 'linear-gradient(135deg, #BAFFC9, #FFFFBA)',
    component: GardenBuilder,
  },
  {
    id: 'petcare',
    name: 'Pet Care',
    icon: '',
    description: 'Feed, pet, and care for adorable animals!',
    color: '#FFB3BA',
    gradient: 'linear-gradient(135deg, #FFB3BA, #FFDFBA)',
    component: AnimalCare,
  },
  {
    id: 'coloring',
    name: 'Coloring Canvas',
    icon: '',
    description: 'Draw and color with soft pastel colors and fun stamps!',
    color: '#E8BAFF',
    gradient: 'linear-gradient(135deg, #E8BAFF, #FFC4E1)',
    component: ColoringCanvas,
  },
];

const GAMES = [
  {
    id: 'tictactoe',
    name: 'Tic-Tac-Toe',
    icon: '❌⭕',
    description: 'Play 3x3 or 4x4 vs Computer or with friends!',
    color: '#6366F1',
    gradient: 'linear-gradient(135deg, #6366F1, #8B5CF6)',
    component: TicTacToe,
  },
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

const ALL_GAMES = [...RELAXING_GAMES, ...GAMES];

const GamesPage = () => {
  const [activeGame, setActiveGame] = useState(null);
  const navigate = useNavigate();

  const activeGameData = activeGame ? ALL_GAMES.find(g => g.id === activeGame) : null;
  const ActiveComponent = activeGameData?.component || null;

  return (
    <div className="games-page">
      <div className="games-header">
        <h1 className="games-title">Game Zone</h1>
        <p className="games-subtitle">Pick a game and have fun!</p>
      </div>

      {!activeGame ? (
        <div className="games-grid-container">
          <div className="relaxing-zone-section">
            <div className="relaxing-zone-header">
              <h2 className="relaxing-zone-title">Relaxing Zone</h2>
              <p className="relaxing-zone-subtitle">Calm, creative games just for you</p>
            </div>
            <div className="games-grid relaxing-grid">
              {RELAXING_GAMES.map((game) => (
                <div
                  key={game.id}
                  className="game-card relaxing-card"
                  style={{ background: game.gradient }}
                  onClick={() => setActiveGame(game.id)}
                >
                  <div className="game-card-icon">{game.icon}</div>
                  <h3 className="game-card-name">{game.name}</h3>
                  <p className="game-card-desc">{game.description}</p>
                  <div className="game-card-play relaxing-play">Let's Play</div>
                </div>
              ))}
            </div>
          </div>

          <div className="challenge-zone-section">
            <div className="challenge-zone-header">
              <h2 className="challenge-zone-title">Challenge Zone</h2>
              <p className="challenge-zone-subtitle">Test your skills with fun challenges!</p>
            </div>
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
                  <div className="game-card-play">Play Now</div>
                </div>
              ))}
            </div>
          </div>

          <div className="games-puzzle-link">
            <p>Looking for puzzles?</p>
            <button className="puzzle-zone-btn" onClick={() => navigate('/puzzle-zone')}>
              Go to Puzzle Zone
            </button>
          </div>
        </div>
      ) : (
        <div className="active-game-container">
          <button
            className="back-to-games-btn"
            onClick={() => setActiveGame(null)}
          >
            Back to Games
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
