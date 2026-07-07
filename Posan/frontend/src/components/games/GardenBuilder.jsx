import { useState, useCallback } from 'react';
import './GardenBuilder.css';

const GARDEN_ITEMS = [
  { category: 'Flowers', items: [
    { id: 'tulip', emoji: '', label: 'Tulip' },
    { id: 'sunflower', emoji: '', label: 'Sunflower' },
    { id: 'rose', emoji: '', label: 'Rose' },
    { id: 'cherry_blossom', emoji: '', label: 'Cherry Blossom' },
    { id: 'hibiscus', emoji: '', label: 'Hibiscus' },
    { id: 'bouquet', emoji: '', label: 'Bouquet' },
  ]},
  { category: 'Trees', items: [
    { id: 'tree', emoji: '', label: 'Tree' },
    { id: 'palm', emoji: '', label: 'Palm' },
    { id: 'evergreen', emoji: '', label: 'Pine' },
    { id: 'cactus', emoji: '', label: 'Cactus' },
    { id: 'herb', emoji: '', label: 'Herb' },
    { id: 'clover', emoji: '', label: 'Clover' },
  ]},
  { category: 'Friends', items: [
    { id: 'butterfly', emoji: '', label: 'Butterfly' },
    { id: 'ladybug', emoji: '', label: 'Ladybug' },
    { id: 'bee', emoji: '', label: 'Bee' },
    { id: 'bird', emoji: '', label: 'Bird' },
    { id: 'snail', emoji: '', label: 'Snail' },
    { id: 'rabbit', emoji: '', label: 'Rabbit' },
  ]},
  { category: 'Decor', items: [
    { id: 'mushroom', emoji: '', label: 'Mushroom' },
    { id: 'rainbow', emoji: '', label: 'Rainbow' },
    { id: 'star', emoji: '', label: 'Star' },
    { id: 'sparkle', emoji: '', label: 'Sparkle' },
    { id: 'droplet', emoji: '', label: 'Water' },
    { id: 'rock', emoji: '', label: 'Rock' },
  ]},
];

const BACKGROUNDS = [
  { id: 'meadow', label: 'Meadow', gradient: 'linear-gradient(180deg, #87CEEB 0%, #87CEEB 40%, #90EE90 40%, #228B22 100%)' },
  { id: 'sunset', label: 'Sunset', gradient: 'linear-gradient(180deg, #FFB347 0%, #FFCC80 30%, #C8E6C9 50%, #66BB6A 100%)' },
  { id: 'night', label: 'Night', gradient: 'linear-gradient(180deg, #1A237E 0%, #283593 30%, #2E7D32 60%, #1B5E20 100%)' },
  { id: 'spring', label: 'Spring', gradient: 'linear-gradient(180deg, #B3E5FC 0%, #E1F5FE 35%, #C8E6C9 50%, #A5D6A7 100%)' },
];

let placedIdCounter = 0;

const GardenBuilder = () => {
  const [placedItems, setPlacedItems] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);
  const [activeCategory, setActiveCategory] = useState('Flowers');
  const [background, setBackground] = useState(BACKGROUNDS[0]);
  const [showCelebration, setShowCelebration] = useState(false);
  const [gardenName, setGardenName] = useState('My Garden');

  const handleGardenClick = (e) => {
    if (!selectedItem) return;

    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;

    if (y < 10) return;

    const newItem = {
      placedId: ++placedIdCounter,
      ...selectedItem,
      x,
      y,
      scale: 0.8 + Math.random() * 0.5,
      rotation: -10 + Math.random() * 20,
    };

    setPlacedItems(prev => [...prev, newItem]);

    if ((placedItems.length + 1) % 10 === 0) {
      setShowCelebration(true);
      setTimeout(() => setShowCelebration(false), 2000);
    }
  };

  const removeItem = (placedId) => {
    setPlacedItems(prev => prev.filter(i => i.placedId !== placedId));
  };

  const clearGarden = () => {
    setPlacedItems([]);
    placedIdCounter = 0;
  };

  const currentItems = GARDEN_ITEMS.find(c => c.category === activeCategory)?.items || [];

  return (
    <div className="garden-builder-game">
      <div className="garden-header">
        <h2>My Garden</h2>
        <input
          className="garden-name-input"
          value={gardenName}
          onChange={(e) => setGardenName(e.target.value)}
          maxLength={20}
          placeholder="Name your garden..."
        />
      </div>

      <div className="garden-bg-picker">
        {BACKGROUNDS.map(bg => (
          <button
            key={bg.id}
            className={`bg-option ${background.id === bg.id ? 'active' : ''}`}
            style={{ background: bg.gradient }}
            onClick={() => setBackground(bg)}
            title={bg.label}
          />
        ))}
      </div>

      <div className="garden-canvas-wrapper">
        <div
          className="garden-canvas"
          style={{ background: background.gradient }}
          onClick={handleGardenClick}
        >
          {placedItems.map(item => (
            <div
              key={item.placedId}
              className="garden-placed-item"
              style={{
                left: `${item.x}%`,
                top: `${item.y}%`,
                transform: `translate(-50%, -50%) scale(${item.scale}) rotate(${item.rotation}deg)`,
              }}
              onDoubleClick={(e) => { e.stopPropagation(); removeItem(item.placedId); }}
            >
              <span className="placed-emoji">{item.emoji}</span>
            </div>
          ))}

          {placedItems.length === 0 && (
            <div className="garden-empty-hint">
              <p>Pick something below, then tap here to plant it!</p>
            </div>
          )}

          {showCelebration && (
            <div className="garden-celebration">
              <span>Your garden is beautiful!</span>
            </div>
          )}
        </div>
      </div>

      <div className="garden-toolbar">
        <div className="garden-categories">
          {GARDEN_ITEMS.map(cat => (
            <button
              key={cat.category}
              className={`garden-cat-btn ${activeCategory === cat.category ? 'active' : ''}`}
              onClick={() => setActiveCategory(cat.category)}
            >
              {cat.category}
            </button>
          ))}
        </div>

        <div className="garden-items-row">
          {currentItems.map(item => (
            <button
              key={item.id}
              className={`garden-item-btn ${selectedItem?.id === item.id ? 'selected' : ''}`}
              onClick={() => setSelectedItem(selectedItem?.id === item.id ? null : item)}
              title={item.label}
            >
              <span className="gi-emoji">{item.emoji}</span>
              <span className="gi-label">{item.label}</span>
            </button>
          ))}
        </div>

        <div className="garden-actions">
          <button className="garden-clear-btn" onClick={clearGarden}>Start Fresh</button>
          <span className="garden-item-count">{placedItems.length} items planted</span>
        </div>
      </div>
    </div>
  );
};

export default GardenBuilder;
