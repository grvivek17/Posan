import { useState, useEffect, useRef } from 'react';
import './SolarSystem.css';

const PLANETS = [
  {
    id: 'sun',
    name: 'The Sun',
    emoji: '☀️',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/The_Sun_by_the_Atmospheric_Imaging_Assembly_of_NASA%27s_Solar_Dynamics_Observatory_-_20100819.jpg/480px-The_Sun_by_the_Atmospheric_Imaging_Assembly_of_NASA%27s_Solar_Dynamics_Observatory_-_20100819.jpg',
    color: '#FDB813',
    glowColor: 'rgba(253, 184, 19, 0.6)',
    size: 90,
    orbitRadius: 0,
    period: 0,
    facts: [
      '🌟 The Sun contains 99.86% of all mass in our Solar System!',
      '🔥 Surface temperature is about 5,500°C (9,932°F)',
      '⚡ Light from the Sun takes 8 minutes to reach Earth',
      '🌊 1.3 million Earths could fit inside the Sun',
    ],
    description: 'Our star — a giant ball of hot plasma at the center of our solar system.',
    type: 'Star',
    diameter: '1,391,000 km',
    distance: 'Center',
    moons: 0,
  },
  {
    id: 'mercury',
    name: 'Mercury',
    emoji: '☿',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Mercury_in_true_color.jpg/480px-Mercury_in_true_color.jpg',
    color: '#B5B5B5',
    glowColor: 'rgba(181,181,181,0.5)',
    size: 18,
    orbitRadius: 110,
    period: 8,
    facts: [
      '🥵 Days can reach 430°C (800°F), but nights drop to -180°C!',
      '🏃 Mercury zips around the Sun in just 88 Earth days',
      '🌑 No moons, no rings, no atmosphere to speak of',
      '🪨 Covered in craters like our Moon',
    ],
    description: 'The smallest planet and closest to the Sun, with extreme temperature swings.',
    type: 'Terrestrial Planet',
    diameter: '4,879 km',
    distance: '57.9M km from Sun',
    moons: 0,
  },
  {
    id: 'venus',
    name: 'Venus',
    emoji: '♀',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Venus-real_color.jpg/480px-Venus-real_color.jpg',
    color: '#E8C975',
    glowColor: 'rgba(232,201,117,0.5)',
    size: 26,
    orbitRadius: 160,
    period: 12,
    facts: [
      '🔥 Hottest planet! Surface is 465°C — hotter than Mercury!',
      '🔄 Venus spins backwards compared to most planets',
      '☁️ Thick clouds of sulfuric acid cover the planet',
      '📅 A day on Venus is longer than its year!',
    ],
    description: 'The hottest planet, wrapped in thick toxic clouds — a hostile twin of Earth.',
    type: 'Terrestrial Planet',
    diameter: '12,104 km',
    distance: '108.2M km from Sun',
    moons: 0,
  },
  {
    id: 'earth',
    name: 'Earth',
    emoji: '🌍',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/The_Earth_seen_from_Apollo_17.jpg/480px-The_Earth_seen_from_Apollo_17.jpg',
    color: '#4A90D9',
    glowColor: 'rgba(74,144,217,0.5)',
    size: 28,
    orbitRadius: 215,
    period: 16,
    facts: [
      '🌊 71% of Earth\'s surface is covered by water',
      '🧬 The only known planet with life in the universe',
      '🛡️ Our magnetic field protects us from solar winds',
      '🌙 Earth has the largest moon relative to its size',
    ],
    description: 'Our home — the only planet known to harbor life, with liquid water and oxygen.',
    type: 'Terrestrial Planet',
    diameter: '12,742 km',
    distance: '149.6M km from Sun',
    moons: 1,
  },
  {
    id: 'mars',
    name: 'Mars',
    emoji: '♂',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/OSIRIS_Mars_true_color.jpg/480px-OSIRIS_Mars_true_color.jpg',
    color: '#C1440E',
    glowColor: 'rgba(193,68,14,0.5)',
    size: 22,
    orbitRadius: 275,
    period: 22,
    facts: [
      '🌋 Home to Olympus Mons — the tallest volcano in the solar system!',
      '❄️ Mars has polar ice caps made of water and CO₂',
      '🤖 Several rovers explore its surface right now',
      '🌪️ Massive dust storms can cover the entire planet',
    ],
    description: 'The Red Planet — dusty, cold, and a future target for human exploration.',
    type: 'Terrestrial Planet',
    diameter: '6,779 km',
    distance: '227.9M km from Sun',
    moons: 2,
  },
  {
    id: 'jupiter',
    name: 'Jupiter',
    emoji: '♃',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2b/Jupiter_and_its_shrunken_Great_Red_Spot.jpg/480px-Jupiter_and_its_shrunken_Great_Red_Spot.jpg',
    color: '#C88B3A',
    glowColor: 'rgba(200,139,58,0.5)',
    size: 58,
    orbitRadius: 345,
    period: 30,
    facts: [
      '🌀 The Great Red Spot is a storm bigger than Earth!',
      '🏆 Largest planet — over 1,300 Earths could fit inside',
      '🛡️ Jupiter protects Earth by catching asteroids',
      '🌙 Has 95 known moons, including the moon Europa!',
    ],
    description: 'The king of planets — a gas giant with the iconic Great Red Spot storm.',
    type: 'Gas Giant',
    diameter: '139,820 km',
    distance: '778.5M km from Sun',
    moons: 95,
  },
  {
    id: 'saturn',
    name: 'Saturn',
    emoji: '♄',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Saturn_during_Equinox.jpg/480px-Saturn_during_Equinox.jpg',
    color: '#E4D191',
    glowColor: 'rgba(228,209,145,0.5)',
    size: 50,
    orbitRadius: 415,
    period: 38,
    facts: [
      '💍 Its rings are made of ice and rock — some as big as houses!',
      '🪐 Saturn is so light it could float on water!',
      '🌙 Has 146 known moons — the most of any planet',
      '💨 Wind speeds can reach 1,800 km/h (1,118 mph)!',
    ],
    description: 'The ringed jewel of the solar system — a beautiful gas giant with iconic rings.',
    type: 'Gas Giant',
    diameter: '116,460 km',
    distance: '1,432M km from Sun',
    moons: 146,
    hasRings: true,
  },
  {
    id: 'uranus',
    name: 'Uranus',
    emoji: '♅',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Uranus2.jpg/480px-Uranus2.jpg',
    color: '#7DE8E8',
    glowColor: 'rgba(125,232,232,0.5)',
    size: 36,
    orbitRadius: 480,
    period: 46,
    facts: [
      '🔄 Uranus spins on its side — 98° tilt!',
      '❄️ The coldest planet — temperatures reach -224°C',
      '💍 Has 13 faint rings invisible to the naked eye',
      '🌊 Made of a slush of water, methane and ammonia',
    ],
    description: 'An ice giant that rolls around the Sun on its side, with a pale blue-green hue.',
    type: 'Ice Giant',
    diameter: '50,724 km',
    distance: '2,867M km from Sun',
    moons: 27,
  },
  {
    id: 'neptune',
    name: 'Neptune',
    emoji: '♆',
    image: 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/Neptune_-_Voyager_2_%2829347980845%29_flatten_crop.jpg/480px-Neptune_-_Voyager_2_%2829347980845%29_flatten_crop.jpg',
    color: '#4B70DD',
    glowColor: 'rgba(75,112,221,0.5)',
    size: 34,
    orbitRadius: 540,
    period: 54,
    facts: [
      '💨 Fastest winds in the solar system — 2,100 km/h!',
      '📅 One year on Neptune = 165 Earth years!',
      '🔵 Its blue color comes from methane in its atmosphere',
      '🌑 Its moon Triton orbits backwards — a captured object!',
    ],
    description: 'The windiest planet, a deep blue ice giant at the edge of our solar system.',
    type: 'Ice Giant',
    diameter: '49,244 km',
    distance: '4,495M km from Sun',
    moons: 16,
  },
];

const SolarSystem = () => {
  const [selectedPlanet, setSelectedPlanet] = useState(null);
  const [viewMode, setViewMode] = useState('orbit'); // 'orbit' | 'explore'
  const [animating, setAnimating] = useState(true);
  const [currentFact, setCurrentFact] = useState(0);
  const [imageError, setImageError] = useState({});
  const factTimerRef = useRef(null);

  useEffect(() => {
    if (selectedPlanet) {
      setCurrentFact(0);
      if (factTimerRef.current) clearInterval(factTimerRef.current);
      factTimerRef.current = setInterval(() => {
        setCurrentFact(f => (f + 1) % selectedPlanet.facts.length);
      }, 3500);
    }
    return () => { if (factTimerRef.current) clearInterval(factTimerRef.current); };
  }, [selectedPlanet]);

  const handlePlanetClick = (planet) => {
    setSelectedPlanet(planet);
  };

  const handleImageError = (id) => {
    setImageError(prev => ({ ...prev, [id]: true }));
  };

  const planets = PLANETS.slice(1); // exclude Sun for orbit view

  return (
    <div className="ss-container">
      {/* Header */}
      <div className="ss-header">
        <h1 className="ss-title">🚀 Solar System Explorer</h1>
        <p className="ss-subtitle">Click any planet to discover amazing facts!</p>
        <div className="ss-view-toggle">
          <button
            className={`ss-toggle-btn ${viewMode === 'orbit' ? 'active' : ''}`}
            onClick={() => setViewMode('orbit')}
          >
            🌌 Orbit View
          </button>
          <button
            className={`ss-toggle-btn ${viewMode === 'explore' ? 'active' : ''}`}
            onClick={() => setViewMode('explore')}
          >
            🔭 Explore View
          </button>
        </div>
      </div>

      {/* Main Content */}
      {viewMode === 'orbit' ? (
        <div className="ss-orbit-view">
          {/* Solar System Orrery */}
          <div className="ss-orrery-wrapper">
            <div className={`ss-orrery ${animating ? 'animating' : 'paused'}`}>
              {/* Sun */}
              <div
                className="ss-sun"
                onClick={() => handlePlanetClick(PLANETS[0])}
                title="The Sun"
              >
                {!imageError['sun'] ? (
                  <img
                    src={PLANETS[0].image}
                    alt="Sun"
                    className="ss-planet-img"
                    onError={() => handleImageError('sun')}
                  />
                ) : (
                  <div className="ss-planet-fallback" style={{ background: 'radial-gradient(circle at 35% 35%, #FFF176, #FDB813, #E65100)' }}>☀️</div>
                )}
                <div className="ss-sun-glow" />
                <div className="ss-planet-label">Sun</div>
              </div>

              {/* Orbits & Planets */}
              {planets.map((planet, i) => (
                <div
                  key={planet.id}
                  className="ss-orbit-ring"
                  style={{ '--orbit-r': `${planet.orbitRadius}px` }}
                >
                  <div
                    className="ss-orbiting-planet"
                    style={{
                      '--period': `${planet.period}s`,
                      '--planet-size': `${planet.size}px`,
                      '--glow': planet.glowColor,
                      '--start-angle': `${(i * 43) % 360}deg`,
                    }}
                    onClick={() => handlePlanetClick(planet)}
                    title={planet.name}
                  >
                    <div className="ss-planet-sphere">
                      {!imageError[planet.id] ? (
                        <img
                          src={planet.image}
                          alt={planet.name}
                          className="ss-planet-img"
                          onError={() => handleImageError(planet.id)}
                        />
                      ) : (
                        <div
                          className="ss-planet-fallback"
                          style={{ background: planet.color }}
                        >
                          {planet.emoji}
                        </div>
                      )}
                      {planet.hasRings && (
                        <div className="ss-saturn-rings">
                          <div className="ss-ring ss-ring-1" />
                          <div className="ss-ring ss-ring-2" />
                          <div className="ss-ring ss-ring-3" />
                        </div>
                      )}
                    </div>
                    <div className="ss-planet-label">{planet.name}</div>
                  </div>
                </div>
              ))}
            </div>

            {/* Controls */}
            <div className="ss-controls">
              <button
                className="ss-control-btn"
                onClick={() => setAnimating(a => !a)}
                title={animating ? 'Pause' : 'Play'}
              >
                {animating ? '⏸' : '▶️'}
              </button>
            </div>
          </div>

          {/* Mini planet list */}
          <div className="ss-mini-list">
            {PLANETS.map(p => (
              <button
                key={p.id}
                className={`ss-mini-btn ${selectedPlanet?.id === p.id ? 'active' : ''}`}
                style={{ '--p-color': p.color }}
                onClick={() => handlePlanetClick(p)}
              >
                <div className="ss-mini-img-wrap">
                  {(p.id === 'sun' || p.id === 'earth') && !imageError[p.id] ? (
                    <img src={p.image} alt={p.name} className="ss-mini-img" onError={() => handleImageError(p.id)} />
                  ) : (
                    <span>{p.emoji}</span>
                  )}
                </div>
                <span className="ss-mini-name">{p.name}</span>
              </button>
            ))}
          </div>
        </div>
      ) : (
        /* Explore View — Grid of Planet Cards */
        <div className="ss-explore-grid">
          {PLANETS.map((planet) => (
            <div
              key={planet.id}
              className={`ss-planet-card ${selectedPlanet?.id === planet.id ? 'selected' : ''}`}
              style={{ '--p-glow': planet.glowColor, '--p-color': planet.color }}
              onClick={() => handlePlanetClick(planet)}
            >
              <div className="ss-card-img-wrap">
                {!imageError[planet.id] ? (
                  <img
                    src={planet.image}
                    alt={planet.name}
                    className="ss-card-img"
                    onError={() => handleImageError(planet.id)}
                  />
                ) : (
                  <div className="ss-card-img-fallback">{planet.emoji}</div>
                )}
                {planet.hasRings && (
                  <div className="ss-card-rings">
                    <div className="ss-card-ring" />
                    <div className="ss-card-ring ss-card-ring-2" />
                  </div>
                )}
                {planet.id === 'sun' && <div className="ss-card-sun-pulse" />}
              </div>
              <div className="ss-card-info">
                <h3 className="ss-card-name" style={{ color: planet.color }}>{planet.name}</h3>
                <span className="ss-card-type">{planet.type}</span>
                <p className="ss-card-desc">{planet.description}</p>
                <div className="ss-card-stats">
                  <div className="ss-stat">
                    <span className="ss-stat-label">⬛ Diameter</span>
                    <span className="ss-stat-value">{planet.diameter}</span>
                  </div>
                  <div className="ss-stat">
                    <span className="ss-stat-label">🌙 Moons</span>
                    <span className="ss-stat-value">{planet.moons}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Detail Panel */}
      {selectedPlanet && (
        <div className="ss-detail-overlay" onClick={() => setSelectedPlanet(null)}>
          <div
            className="ss-detail-panel"
            onClick={(e) => e.stopPropagation()}
            style={{ '--p-glow': selectedPlanet.glowColor, '--p-color': selectedPlanet.color }}
          >
            <button className="ss-detail-close" onClick={() => setSelectedPlanet(null)}>✕</button>

            <div className="ss-detail-hero">
              <div className="ss-detail-img-wrap">
                {!imageError[selectedPlanet.id] ? (
                  <img
                    src={selectedPlanet.image}
                    alt={selectedPlanet.name}
                    className="ss-detail-img"
                    onError={() => handleImageError(selectedPlanet.id)}
                  />
                ) : (
                  <div className="ss-detail-img-fallback">{selectedPlanet.emoji}</div>
                )}
                {selectedPlanet.hasRings && (
                  <div className="ss-detail-rings">
                    <div className="ss-detail-ring ss-detail-ring-1" />
                    <div className="ss-detail-ring ss-detail-ring-2" />
                    <div className="ss-detail-ring ss-detail-ring-3" />
                  </div>
                )}
                {selectedPlanet.id === 'sun' && <div className="ss-detail-sun-glow" />}
              </div>

              <div className="ss-detail-header">
                <h2 className="ss-detail-name" style={{ color: selectedPlanet.color }}>
                  {selectedPlanet.name}
                </h2>
                <span className="ss-detail-type">{selectedPlanet.type}</span>
                <p className="ss-detail-desc">{selectedPlanet.description}</p>
              </div>
            </div>

            {/* Stats */}
            <div className="ss-detail-stats">
              <div className="ss-detail-stat">
                <span className="ss-dstat-icon">⬛</span>
                <span className="ss-dstat-label">Diameter</span>
                <span className="ss-dstat-val">{selectedPlanet.diameter}</span>
              </div>
              <div className="ss-detail-stat">
                <span className="ss-dstat-icon">📍</span>
                <span className="ss-dstat-label">Distance</span>
                <span className="ss-dstat-val">{selectedPlanet.distance}</span>
              </div>
              <div className="ss-detail-stat">
                <span className="ss-dstat-icon">🌙</span>
                <span className="ss-dstat-label">Moons</span>
                <span className="ss-dstat-val">{selectedPlanet.moons}</span>
              </div>
            </div>

            {/* Fun Fact Carousel */}
            <div className="ss-fact-box">
              <div className="ss-fact-header">💡 Did You Know?</div>
              <div className="ss-fact-text" key={currentFact}>
                {selectedPlanet.facts[currentFact]}
              </div>
              <div className="ss-fact-dots">
                {selectedPlanet.facts.map((_, i) => (
                  <button
                    key={i}
                    className={`ss-fact-dot ${i === currentFact ? 'active' : ''}`}
                    onClick={() => { setCurrentFact(i); }}
                    style={{ '--p-color': selectedPlanet.color }}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SolarSystem;
