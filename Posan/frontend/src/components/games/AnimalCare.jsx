import { useState, useEffect, useCallback } from 'react';
import './AnimalCare.css';

const ANIMALS = [
  { id: 'puppy', emoji: '', name: 'Buddy', color: '#FFE0B2' },
  { id: 'kitten', emoji: '', name: 'Whiskers', color: '#F8BBD0' },
  { id: 'bunny', emoji: '', name: 'Flopsy', color: '#E1BEE7' },
  { id: 'panda', emoji: '', name: 'Bamboo', color: '#C8E6C9' },
  { id: 'fox', emoji: '', name: 'Rusty', color: '#FFCCBC' },
  { id: 'hamster', emoji: '', name: 'Peanut', color: '#FFF9C4' },
];

const ACTIONS = [
  { id: 'feed', emoji: '', label: 'Feed', effect: 'Yummy! Thank you!' },
  { id: 'pet', emoji: '', label: 'Pet', effect: 'So gentle and kind!' },
  { id: 'play', emoji: '', label: 'Play', effect: 'Wheee! So fun!' },
  { id: 'clean', emoji: '', label: 'Bath', effect: 'Squeaky clean!' },
  { id: 'sleep', emoji: '', label: 'Nap', effect: 'Zzz... sweet dreams!' },
  { id: 'treat', emoji: '', label: 'Treat', effect: 'What a special treat!' },
];

const MOOD_EMOJIS = {
  happy: '',
  love: '',
  sleepy: '',
  playful: '',
  content: '',
};

const AnimalCare = () => {
  const [currentAnimal, setCurrentAnimal] = useState(ANIMALS[0]);
  const [happiness, setHappiness] = useState(50);
  const [mood, setMood] = useState('content');
  const [actionFeedback, setActionFeedback] = useState(null);
  const [sparkles, setSparkles] = useState([]);
  const [hearts, setHearts] = useState([]);
  const [badges, setBadges] = useState([]);
  const [totalActions, setTotalActions] = useState(0);
  const [animalBounce, setAnimalBounce] = useState(false);

  const CARE_BADGES = [
    { count: 5, emoji: '', label: 'Kind Heart' },
    { count: 15, emoji: '', label: 'Best Friend' },
    { count: 30, emoji: '', label: 'Super Carer' },
    { count: 50, emoji: '', label: 'Animal Whisperer' },
  ];

  const createHearts = useCallback(() => {
    const newHearts = Array.from({ length: 4 }, (_, i) => ({
      id: Date.now() + i,
      x: 40 + Math.random() * 20,
      y: 30 + Math.random() * 20,
      delay: i * 0.15,
    }));
    setHearts(prev => [...prev, ...newHearts]);
    setTimeout(() => {
      setHearts(prev => prev.filter(h => !newHearts.find(nh => nh.id === h.id)));
    }, 1200);
  }, []);

  const doAction = (action) => {
    setActionFeedback(action);
    setAnimalBounce(true);
    createHearts();

    const newHappiness = Math.min(100, happiness + 8 + Math.floor(Math.random() * 8));
    setHappiness(newHappiness);

    const newTotal = totalActions + 1;
    setTotalActions(newTotal);

    if (action.id === 'sleep') setMood('sleepy');
    else if (action.id === 'pet') setMood('love');
    else if (action.id === 'play') setMood('playful');
    else if (newHappiness > 80) setMood('happy');
    else setMood('content');

    const earned = CARE_BADGES.find(b => b.count === newTotal && !badges.includes(b.count));
    if (earned) {
      setBadges(prev => [...prev, earned.count]);
    }

    setTimeout(() => {
      setActionFeedback(null);
      setAnimalBounce(false);
    }, 1500);
  };

  const switchAnimal = (animal) => {
    setCurrentAnimal(animal);
    setHappiness(50);
    setMood('content');
    setActionFeedback(null);
  };

  useEffect(() => {
    const interval = setInterval(() => {
      setHappiness(prev => Math.max(20, prev - 1));
    }, 8000);
    return () => clearInterval(interval);
  }, []);

  const happinessColor = happiness > 70 ? '#81C784' : happiness > 40 ? '#FFD54F' : '#FFAB91';

  return (
    <div className="animal-care-game" style={{ '--animal-bg': currentAnimal.color }}>
      <div className="ac-header">
        <h2>Pet Care</h2>
        <p className="ac-hint">Take care of your furry friend!</p>
      </div>

      <div className="ac-animal-picker">
        {ANIMALS.map(animal => (
          <button
            key={animal.id}
            className={`ac-animal-option ${currentAnimal.id === animal.id ? 'active' : ''}`}
            onClick={() => switchAnimal(animal)}
            style={{ '--option-color': animal.color }}
          >
            <span>{animal.emoji}</span>
          </button>
        ))}
      </div>

      <div className="ac-main-area">
        <div className="ac-pet-display">
          <div className={`ac-pet ${animalBounce ? 'bouncing' : ''}`}>
            <span className="ac-pet-emoji">{currentAnimal.emoji}</span>
            <span className="ac-pet-mood">{MOOD_EMOJIS[mood]}</span>
          </div>

          <div className="ac-pet-name">{currentAnimal.name}</div>

          {hearts.map(h => (
            <div
              key={h.id}
              className="ac-floating-heart"
              style={{ left: `${h.x}%`, top: `${h.y}%`, animationDelay: `${h.delay}s` }}
            >
              
            </div>
          ))}

          {actionFeedback && (
            <div className="ac-action-bubble">
              <span className="ac-ab-emoji">{actionFeedback.emoji}</span>
              <span className="ac-ab-text">{actionFeedback.effect}</span>
            </div>
          )}
        </div>

        <div className="ac-happiness-bar">
          <span className="ac-hb-label">Happiness</span>
          <div className="ac-hb-track">
            <div
              className="ac-hb-fill"
              style={{ width: `${happiness}%`, background: happinessColor }}
            />
          </div>
          <span className="ac-hb-emoji">{happiness > 70 ? '' : happiness > 40 ? '' : ''}</span>
        </div>
      </div>

      <div className="ac-actions">
        {ACTIONS.map(action => (
          <button
            key={action.id}
            className="ac-action-btn"
            onClick={() => doAction(action)}
            disabled={!!actionFeedback}
          >
            <span className="ac-act-emoji">{action.emoji}</span>
            <span className="ac-act-label">{action.label}</span>
          </button>
        ))}
      </div>

      <div className="ac-badges-row">
        {CARE_BADGES.map(b => (
          <div key={b.count} className={`ac-badge ${badges.includes(b.count) ? 'earned' : 'locked'}`} title={b.label}>
            <span>{badges.includes(b.count) ? b.emoji : ''}</span>
            {badges.includes(b.count) && <span className="ac-badge-label">{b.label}</span>}
          </div>
        ))}
      </div>
    </div>
  );
};

export default AnimalCare;
