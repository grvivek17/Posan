import { useState, useEffect, useCallback, useRef } from 'react';
import './BubblePop.css';

const PASTEL_COLORS = [
  '#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF',
  '#E8BAFF', '#FFC4E1', '#C4F0FF', '#D4BAFF', '#FFE0B2',
];

const BUBBLE_EMOJIS = ['', '', '', '', '', '', '', '', '', ''];

const SPARKLE_CHARS = ['', '', '', '', '', ''];

let bubbleIdCounter = 0;

const BubblePop = () => {
  const [bubbles, setBubbles] = useState([]);
  const [sparkles, setSparkles] = useState([]);
  const [poppedCount, setPoppedCount] = useState(0);
  const [badges, setBadges] = useState([]);
  const [showBadge, setShowBadge] = useState(null);
  const containerRef = useRef(null);
  const animFrameRef = useRef(null);

  const BADGE_THRESHOLDS = [
    { count: 5, emoji: '', label: 'Star Popper!' },
    { count: 15, emoji: '', label: 'Bubble Friend!' },
    { count: 30, emoji: '', label: 'Rainbow Catcher!' },
    { count: 50, emoji: '', label: 'Sparkle Master!' },
  ];

  const createBubble = useCallback(() => {
    const id = ++bubbleIdCounter;
    const size = 40 + Math.random() * 50;
    const x = 10 + Math.random() * 80;
    const color = PASTEL_COLORS[Math.floor(Math.random() * PASTEL_COLORS.length)];
    const emoji = Math.random() > 0.5 ? BUBBLE_EMOJIS[Math.floor(Math.random() * BUBBLE_EMOJIS.length)] : '';
    const duration = 6 + Math.random() * 6;
    const wobble = -15 + Math.random() * 30;

    return { id, size, x, color, emoji, duration, wobble, popping: false, createdAt: Date.now() };
  }, []);

  useEffect(() => {
    const initial = Array.from({ length: 6 }, () => createBubble());
    setBubbles(initial);
  }, [createBubble]);

  useEffect(() => {
    const interval = setInterval(() => {
      setBubbles(prev => {
        const now = Date.now();
        const filtered = prev.filter(b => now - b.createdAt < b.duration * 1000 && !b.popping);
        if (filtered.length < 10) {
          return [...filtered, createBubble()];
        }
        return filtered;
      });
    }, 800);

    return () => clearInterval(interval);
  }, [createBubble]);

  const createSparkles = (x, y, color) => {
    const newSparkles = Array.from({ length: 6 }, (_, i) => ({
      id: Date.now() + i,
      x: x + (Math.random() - 0.5) * 60,
      y: y + (Math.random() - 0.5) * 60,
      char: SPARKLE_CHARS[Math.floor(Math.random() * SPARKLE_CHARS.length)],
      color,
    }));
    setSparkles(prev => [...prev, ...newSparkles]);
    setTimeout(() => {
      setSparkles(prev => prev.filter(s => !newSparkles.find(ns => ns.id === s.id)));
    }, 800);
  };

  const popBubble = (e, bubbleId) => {
    e.stopPropagation();
    const bubble = bubbles.find(b => b.id === bubbleId);
    if (!bubble || bubble.popping) return;

    const rect = e.currentTarget.getBoundingClientRect();
    const containerRect = containerRef.current?.getBoundingClientRect();
    if (containerRect) {
      createSparkles(
        rect.left - containerRect.left + rect.width / 2,
        rect.top - containerRect.top + rect.height / 2,
        bubble.color
      );
    }

    setBubbles(prev => prev.filter(b => b.id !== bubbleId));
    const newCount = poppedCount + 1;
    setPoppedCount(newCount);

    const earned = BADGE_THRESHOLDS.find(b => b.count === newCount && !badges.includes(b.count));
    if (earned) {
      setBadges(prev => [...prev, earned.count]);
      setShowBadge(earned);
      setTimeout(() => setShowBadge(null), 2500);
    }
  };

  return (
    <div className="bubble-pop-game" ref={containerRef}>
      <div className="bubble-pop-header">
        <h2>Bubble Pop</h2>
        <p className="bubble-pop-hint">Tap the bubbles to pop them!</p>
      </div>

      <div className="bubble-pop-badges">
        {BADGE_THRESHOLDS.map(b => (
          <div key={b.count} className={`bp-badge ${badges.includes(b.count) ? 'earned' : 'locked'}`} title={b.label}>
            <span className="bp-badge-emoji">{badges.includes(b.count) ? b.emoji : ''}</span>
          </div>
        ))}
      </div>

      <div className="bubble-pop-area">
        {bubbles.map(bubble => (
          <div
            key={bubble.id}
            className="bubble"
            style={{
              width: bubble.size,
              height: bubble.size,
              left: `${bubble.x}%`,
              background: `radial-gradient(circle at 30% 30%, white, ${bubble.color})`,
              animationDuration: `${bubble.duration}s`,
              '--wobble': `${bubble.wobble}px`,
            }}
            onClick={(e) => popBubble(e, bubble.id)}
          >
            {bubble.emoji && <span className="bubble-emoji">{bubble.emoji}</span>}
            <div className="bubble-shine" />
          </div>
        ))}

        {sparkles.map(s => (
          <div
            key={s.id}
            className="pop-sparkle"
            style={{ left: s.x, top: s.y, color: s.color }}
          >
            {s.char}
          </div>
        ))}
      </div>

      {showBadge && (
        <div className="bubble-badge-popup">
          <div className="badge-popup-inner">
            <span className="badge-popup-emoji">{showBadge.emoji}</span>
            <span className="badge-popup-text">{showBadge.label}</span>
          </div>
        </div>
      )}

      <div className="bubble-pop-footer">
        <span className="bubble-smile">{poppedCount > 0 ? '' : ''}</span>
        <span className="bubble-count">{poppedCount} bubbles popped</span>
      </div>
    </div>
  );
};

export default BubblePop;
