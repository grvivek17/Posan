import React, { useState, useEffect, useRef } from 'react';
// Mocks for missing files
const puzzleAudio = {
  playSelect: () => {},
  playWinFanfare: () => {},
  playMatch: () => {},
  playError: () => {},
  playHint: () => {}
};

const PuzzleWinModal = ({ isOpen, onClose, title, message, points, onPlayAgain }) => {
  if (!isOpen) return null;
  return (
    <div className="puzzle-win-modal-overlay" style={{position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999}}>
      <div className="puzzle-win-modal" style={{backgroundColor: '#1a1a4e', padding: '30px', borderRadius: '20px', textAlign: 'center', color: 'white', border: '2px solid #FFD700', maxWidth: '400px'}}>
        <h2>{title || 'You Won! 🎉'}</h2>
        <p>{message || 'Great job completing the puzzle!'}</p>
        {points > 0 && <p style={{fontSize: '1.2rem', color: '#FFD700'}}>+{points} Points!</p>}
        <div style={{display: 'flex', gap: '10px', justifyContent: 'center', marginTop: '20px'}}>
          <button onClick={onPlayAgain} style={{padding: '10px 20px', borderRadius: '10px', backgroundColor: '#4facfe', color: 'white', border: 'none', cursor: 'pointer', fontWeight: 'bold'}}>Play Again</button>
          <button onClick={onClose} style={{padding: '10px 20px', borderRadius: '10px', backgroundColor: 'transparent', color: 'white', border: '1px solid white', cursor: 'pointer'}}>Close</button>
        </div>
      </div>
    </div>
  );
};
import './SolarSystemPuzzle.css';

// Rich child-friendly planet data
const PLANETS_DATA = [
    {
        id: 'sun',
        name: 'Sun',
        nickname: 'Our Glowing Star ☀️',
        order: 0,
        type: 'Star',
        color: '#FFD700',
        gradient: 'radial-gradient(circle, #FFF566 0%, #FF9800 60%, #FF5722 100%)',
        glowColor: 'rgba(255, 180, 0, 0.8)',
        size: 70,
        orbitRadius: 0,
        orbitPeriod: 0,
        distanceFromSun: '0 km (Center)',
        diameter: '1,392,700 km',
        temperature: '5,500 °C (Super Hot!)',
        moonsCount: 0,
        sizeRank: 'Giant Center Star',
        icon: '☀️',
        funFacts: [
            'The Sun is a giant ball of burning plasma at the center of our Solar System!',
            'Over 1 million Earths could fit inside the Sun!',
            'Light from the Sun takes about 8 minutes to travel all the way to Earth.',
            'Without the Sun, Earth would be dark, freezing cold, and have no life.'
        ],
        trivia: 'The Sun accounts for 99.8% of all the mass in the entire Solar System!'
    },
    {
        id: 'mercury',
        name: 'Mercury',
        nickname: 'The Swift Speedster 🏃',
        order: 1,
        type: 'Rocky Planet',
        color: '#B0BEC5',
        gradient: 'radial-gradient(circle, #ECEFF1 0%, #B0BEC5 60%, #546E7A 100%)',
        glowColor: 'rgba(176, 190, 197, 0.6)',
        size: 20,
        orbitRadius: 65,
        orbitPeriod: 8,
        distanceFromSun: '57.9 Million km',
        diameter: '4,879 km',
        temperature: 'Scorching 430°C to Freezing -180°C',
        moonsCount: 0,
        sizeRank: '8th (Smallest Planet)',
        icon: '☿️',
        funFacts: [
            'Mercury is the closest planet to the Sun and the smallest of all 8 planets!',
            'A year on Mercury is super fast—it takes only 88 Earth days to circle the Sun!',
            'Mercury has no atmosphere, so it gets extremely hot in daytime and freezing at night.',
            'It is covered in thousands of meteor craters, making it look like our Moon.'
        ],
        trivia: 'Even though Mercury is closest to the Sun, Venus is actually hotter!'
    },
    {
        id: 'venus',
        name: 'Venus',
        nickname: 'The Bright Twin 🌟',
        order: 2,
        type: 'Rocky Planet',
        color: '#FFB74D',
        gradient: 'radial-gradient(circle, #FFE082 0%, #FFB74D 60%, #E65100 100%)',
        glowColor: 'rgba(255, 183, 77, 0.7)',
        size: 28,
        orbitRadius: 95,
        orbitPeriod: 12,
        distanceFromSun: '108.2 Million km',
        diameter: '12,104 km',
        temperature: '465 °C (Hotter than an oven!)',
        moonsCount: 0,
        sizeRank: '6th Largest',
        icon: '♀️',
        funFacts: [
            'Venus is the hottest planet in the Solar System because thick clouds trap the Sun heat!',
            'Venus spins backwards compared to Earth and most other planets!',
            'It shines so brightly in our night sky that people call it the Evening Star.',
            'A single day on Venus lasts longer than a whole year on Venus!'
        ],
        trivia: 'Venus has thousands of volcanoes on its yellow rocky surface!'
    },
    {
        id: 'earth',
        name: 'Earth',
        nickname: 'The Blue Marble 🌍',
        order: 3,
        type: 'Rocky Planet',
        color: '#29B6F6',
        gradient: 'radial-gradient(circle, #81D4FA 0%, #29B6F6 40%, #66BB6A 70%, #1565C0 100%)',
        glowColor: 'rgba(41, 182, 246, 0.8)',
        size: 30,
        orbitRadius: 130,
        orbitPeriod: 18,
        distanceFromSun: '149.6 Million km',
        diameter: '12,742 km',
        temperature: '15 °C (Just Perfect!)',
        moonsCount: 1,
        sizeRank: '5th Largest',
        icon: '🌍',
        hasMoon: true,
        funFacts: [
            'Earth is our wonderful home and the only planet known to have liquid water & life!',
            'About 71% of Earth surface is covered by beautiful blue oceans.',
            'Earth has one friendly Moon that orbits around us and creates ocean tides.',
            'Our atmosphere shields us from dangerous space radiation and meteors.'
        ],
        trivia: 'Earth is traveling around the Sun at a roaring speed of 107,000 km/h!'
    },
    {
        id: 'mars',
        name: 'Mars',
        nickname: 'The Red Planet 🔴',
        order: 4,
        type: 'Rocky Planet',
        color: '#FF5722',
        gradient: 'radial-gradient(circle, #FF8A65 0%, #FF5722 60%, #BF360C 100%)',
        glowColor: 'rgba(255, 87, 34, 0.7)',
        size: 24,
        orbitRadius: 165,
        orbitPeriod: 25,
        distanceFromSun: '227.9 Million km',
        diameter: '6,779 km',
        temperature: '-60 °C (Chilly Desert!)',
        moonsCount: 2,
        sizeRank: '7th Largest',
        icon: '♂️',
        funFacts: [
            'Mars is nicknamed the Red Planet because iron mineral rust in its soil makes it reddish-orange!',
            'Mars has the biggest volcano in the entire Solar System, Olympus Mons, 3x taller than Mount Everest!',
            'Rovers like Curiosity and Perseverance are currently exploring Mars looking for signs of ancient water.',
            'Mars has 2 tiny potato-shaped moons named Phobos and Deimos.'
        ],
        trivia: 'Sunsets on Mars actually look blue instead of red!'
    },
    {
        id: 'jupiter',
        name: 'Jupiter',
        nickname: 'The Giant King 👑',
        order: 5,
        type: 'Gas Giant',
        color: '#FFA726',
        gradient: 'radial-gradient(circle, #FFE082 0%, #FFB74D 30%, #D84315 70%, #8D6E63 100%)',
        glowColor: 'rgba(255, 167, 38, 0.7)',
        size: 50,
        orbitRadius: 210,
        orbitPeriod: 35,
        distanceFromSun: '778.6 Million km',
        diameter: '139,820 km',
        temperature: '-110 °C (Icy Gas)',
        moonsCount: 95,
        sizeRank: '1st (Largest Planet!)',
        icon: '♃',
        hasSpot: true,
        funFacts: [
            'Jupiter is the largest planet in our Solar System—all other planets could fit inside it!',
            'It has a famous Great Red Spot, which is a gigantic spinning storm larger than planet Earth!',
            'Jupiter spins extremely fast: a day on Jupiter takes only 10 short hours.',
            'It has at least 95 moons, including Ganymede which is bigger than Mercury!'
        ],
        trivia: 'Jupiter acts like a cosmic bodyguard for Earth by attracting dangerous asteroids away!'
    },
    {
        id: 'saturn',
        name: 'Saturn',
        nickname: 'The Ringed Wonder 🪐',
        order: 6,
        type: 'Gas Giant',
        color: '#FBC02D',
        gradient: 'radial-gradient(circle, #FFF59D 0%, #FBC02D 50%, #F57F17 100%)',
        glowColor: 'rgba(251, 192, 45, 0.7)',
        size: 44,
        orbitRadius: 260,
        orbitPeriod: 45,
        distanceFromSun: '1.43 Billion km',
        diameter: '116,460 km',
        temperature: '-140 °C (Freezing Gas)',
        moonsCount: 146,
        sizeRank: '2nd Largest',
        icon: '♄',
        hasRings: true,
        funFacts: [
            'Saturn is famous for its stunning, wide rings made of ice chunks, dust, and rocks!',
            'Saturn is so light and fluffy that if you had a bathtub big enough, Saturn would float on water!',
            'It has 146 moons, more than any other planet in our Solar System.',
            'Its largest moon, Titan, has a thick atmosphere and lakes made of liquid methane.'
        ],
        trivia: 'Saturn rings span over 280,000 km wide, but are only about 10 meters thin!'
    },
    {
        id: 'uranus',
        name: 'Uranus',
        nickname: 'The Sideways Ice Giant 🌀',
        order: 7,
        type: 'Ice Giant',
        color: '#4DD0E1',
        gradient: 'radial-gradient(circle, #E0F7FA 0%, #4DD0E1 60%, #00838F 100%)',
        glowColor: 'rgba(77, 208, 225, 0.7)',
        size: 36,
        orbitRadius: 305,
        orbitPeriod: 55,
        distanceFromSun: '2.87 Billion km',
        diameter: '50,724 km',
        temperature: '-195 °C (Brrr!)',
        moonsCount: 28,
        sizeRank: '3rd Largest',
        icon: '♅',
        hasRings: true,
        funFacts: [
            'Uranus is an Ice Giant planet that rolls on its side like a bowling ball!',
            'It glows with a pretty cyan-blue color due to methane gas in its atmosphere.',
            'Uranus holds the record for the coldest temperature ever recorded on a planet (-224°C)!',
            'It has 13 faint rings and 28 moons named after characters from Shakespeare plays.'
        ],
        trivia: 'Because Uranus spins sideways, its poles get 42 continuous years of sunlight followed by 42 years of darkness!'
    },
    {
        id: 'neptune',
        name: 'Neptune',
        nickname: 'The Windy Sapphire 💨',
        order: 8,
        type: 'Ice Giant',
        color: '#1E88E5',
        gradient: 'radial-gradient(circle, #90CAF9 0%, #1E88E5 60%, #0D47A1 100%)',
        glowColor: 'rgba(30, 136, 229, 0.8)',
        size: 34,
        orbitRadius: 350,
        orbitPeriod: 65,
        distanceFromSun: '4.50 Billion km',
        diameter: '49,244 km',
        temperature: '-200 °C (Deep Freeze)',
        moonsCount: 16,
        sizeRank: '4th Largest',
        icon: '♆',
        funFacts: [
            'Neptune is the farthest major planet from the Sun, appearing as a deep sapphire blue orb!',
            'Neptune has the fastest winds in the Solar System, blowing at speeds over 2,000 km/h!',
            'It takes Neptune 165 Earth years to complete just one single orbit around the Sun.',
            'Its main moon Triton orbits backward and has geysers erupting liquid nitrogen!'
        ],
        trivia: 'It is so far away that noon on Neptune looks like dim twilight on Earth!'
    },
    {
        id: 'pluto',
        name: 'Pluto',
        nickname: 'The Beloved Dwarf Planet 💖',
        order: 9,
        type: 'Dwarf Planet',
        color: '#D7CCC8',
        gradient: 'radial-gradient(circle, #F5F5F5 0%, #D7CCC8 60%, #5D4037 100%)',
        glowColor: 'rgba(215, 204, 200, 0.6)',
        size: 16,
        orbitRadius: 390,
        orbitPeriod: 80,
        distanceFromSun: '5.91 Billion km',
        diameter: '2,376 km',
        temperature: '-230 °C (Extreme Cold)',
        moonsCount: 5,
        sizeRank: 'Dwarf Planet',
        icon: '♇',
        funFacts: [
            'Pluto is a famous dwarf planet located far out in the icy Kuiper Belt!',
            'Pluto has a giant glacier shaped like a loving heart called Tombaugh Regio.',
            'Pluto is smaller than Earth Moon and even smaller than the United States!',
            'Its main moon Charon is so big that Pluto and Charon dance around each other like double planets.'
        ],
        trivia: 'NASA New Horizons spacecraft flew past Pluto in 2015 and sent back high-resolution photos of its heart!'
    }
];

// Sample Trivia Quiz Questions
const QUIZ_QUESTIONS = [
    {
        id: 1,
        question: 'Which planet is known as the "Red Planet"? 🔴',
        options: ['Venus', 'Mars', 'Jupiter', 'Mercury'],
        correct: 'Mars',
        explanation: 'Mars looks red because iron minerals in its soil rust, giving it a rusty reddish hue!'
    },
    {
        id: 2,
        question: 'What is the largest planet in our Solar System? 👑',
        options: ['Saturn', 'Neptune', 'Jupiter', 'Earth'],
        correct: 'Jupiter',
        explanation: 'Jupiter is so massive that all other 7 planets could fit inside it with room to spare!'
    },
    {
        id: 3,
        question: 'Which planet is famous for its bright, spectacular ice rings? 🪐',
        options: ['Saturn', 'Uranus', 'Mars', 'Mercury'],
        correct: 'Saturn',
        explanation: 'Saturn rings are made of billions of icy rock pieces sparkling in sunlight!'
    },
    {
        id: 4,
        question: 'Which planet is closest to the Sun? ☀️',
        options: ['Earth', 'Venus', 'Mercury', 'Mars'],
        correct: 'Mercury',
        explanation: 'Mercury is the 1st planet from the Sun and zooms around it in just 88 days!'
    },
    {
        id: 5,
        question: 'Which planet is our lovely home with liquid water and life? 🌍',
        options: ['Earth', 'Venus', 'Mars', 'Neptune'],
        correct: 'Earth',
        explanation: 'Earth is the 3rd planet from the Sun and the only known planet with water, air, and living beings!'
    },
    {
        id: 6,
        question: 'Which is the hottest planet in the Solar System? 🔥',
        options: ['Mercury', 'Venus', 'Mars', 'Sun'],
        correct: 'Venus',
        explanation: 'Even though Mercury is closer to the Sun, Venus thick clouds trap heat like a blanket, making it 465°C!'
    },
    {
        id: 7,
        question: 'Which planet spins on its side like a rolling bowling ball? 🌀',
        options: ['Neptune', 'Uranus', 'Jupiter', 'Saturn'],
        correct: 'Uranus',
        explanation: 'Uranus has an extreme axial tilt of 98 degrees, so it rolls sideways on its orbital path!'
    }
];

// Planet Matching Cards (Clues -> Planet)
const MATCHING_PAIRS = [
    { clue: 'The Blue Marble & Our Only Home 🌍', planet: 'Earth' },
    { clue: 'The Red Planet with giant volcanoes 🌋', planet: 'Mars' },
    { clue: 'Has magnificent rings made of ice 🪐', planet: 'Saturn' },
    { clue: 'The Giant King with a Great Red Spot 🔴', planet: 'Jupiter' },
    { clue: 'The Scorching Hot Twin wrapped in clouds ☁️', planet: 'Venus' },
    { clue: 'The Swift Speedster closest to the Sun ⚡', planet: 'Mercury' }
];

const SolarSystemPuzzle = () => {
    // Mode states: 'explorer', 'order-puzzle', 'matching-puzzle', 'trivia-quiz'
    const [activeTab, setActiveTab] = useState('explorer');

    // Selected planet for modal/details
    const [selectedPlanet, setSelectedPlanet] = useState(PLANETS_DATA.find(p => p.id === 'earth'));
    const [showFactModal, setShowFactModal] = useState(false);

    // Orbit Animation Controls
    const [isOrbiting, setIsOrbiting] = useState(true);
    const [orbitSpeed, setOrbitSpeed] = useState(1); // 0.5x, 1x, 2x

    // Text to Speech Voice Reader State
    const [isSpeaking, setIsSpeaking] = useState(false);
    const speechUtteranceRef = useRef(null);

    // Order Puzzle State
    const [scrambledPlanets, setScrambledPlanets] = useState([]);
    const [userOrder, setUserOrder] = useState(Array(8).fill(null)); // 8 slots for 8 major planets
    const [draggedPlanet, setDraggedPlanet] = useState(null);
    const [selectedSlotPlanet, setSelectedSlotPlanet] = useState(null); // for tap-to-place touch devices
    const [orderPuzzleSolved, setOrderPuzzleSolved] = useState(false);
    const [orderFeedback, setOrderFeedback] = useState('');

    // Matching Puzzle State
    const [selectedClueIndex, setSelectedClueIndex] = useState(null);
    const [selectedPlanetName, setSelectedPlanetName] = useState(null);
    const [matchedPairs, setMatchedPairs] = useState([]);
    const [matchPuzzleSolved, setMatchPuzzleSolved] = useState(false);

    // Trivia Quiz State
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [selectedAnswer, setSelectedAnswer] = useState(null);
    const [quizScore, setQuizScore] = useState(0);
    const [quizSubmitted, setQuizSubmitted] = useState(false);
    const [quizCompleted, setQuizCompleted] = useState(false);

    // Score & Win Modal State
    const [pointsEarned, setPointsEarned] = useState(0);
    const [showWinModal, setShowWinModal] = useState(false);

    // Initialize Order Puzzle
    useEffect(() => {
        initOrderPuzzle();
        initMatchingPuzzle();
    }, []);

    const initOrderPuzzle = () => {
        // Major 8 planets only for order puzzle (Mercury -> Neptune)
        const majorPlanets = PLANETS_DATA.filter(p => p.id !== 'sun' && p.id !== 'pluto');
        // Shuffle planets
        const shuffled = [...majorPlanets].sort(() => Math.random() - 0.5);
        setScrambledPlanets(shuffled);
        setUserOrder(Array(8).fill(null));
        setOrderPuzzleSolved(false);
        setOrderFeedback('');
        setSelectedSlotPlanet(null);
    };

    const initMatchingPuzzle = () => {
        setMatchedPairs([]);
        setSelectedClueIndex(null);
        setSelectedPlanetName(null);
        setMatchPuzzleSolved(false);
    };

    // Clean speech on unmount
    useEffect(() => {
        return () => {
            if (window.speechSynthesis) {
                window.speechSynthesis.cancel();
            }
        };
    }, []);

    // Speech Synthesis for Kids
    const toggleSpeechFacts = (textToRead) => {
        if (!('speechSynthesis' in window)) {
            alert('Speech synthesis is not supported on this browser.');
            return;
        }

        if (isSpeaking) {
            window.speechSynthesis.cancel();
            setIsSpeaking(false);
            return;
        }

        const utterance = new SpeechSynthesisUtterance(textToRead);
        utterance.rate = 0.9; // Friendly clear pace for kids
        utterance.pitch = 1.1; // Cheerful friendly pitch

        utterance.onend = () => setIsSpeaking(false);
        utterance.onerror = () => setIsSpeaking(false);

        speechUtteranceRef.current = utterance;
        setIsSpeaking(true);
        window.speechSynthesis.speak(utterance);
    };

    // Handle Planet Click in Explorer
    const handlePlanetClick = (planet) => {
        puzzleAudio.playSelect();
        setSelectedPlanet(planet);
        setShowFactModal(true);
        if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
            setIsSpeaking(false);
        }
    };

    // --- Order Puzzle Drag & Drop / Tap Handlers ---
    const handleDragStart = (planet) => {
        puzzleAudio.playSelect();
        setDraggedPlanet(planet);
    };

    const handleDragOver = (e) => {
        e.preventDefault();
    };

    const handleDropOnSlot = (slotIndex) => {
        if (!draggedPlanet) return;
        placePlanetInSlot(draggedPlanet, slotIndex);
        setDraggedPlanet(null);
    };

    // Touch tap selection handler
    const handleTapPlanetSelection = (planet) => {
        puzzleAudio.playSelect();
        if (selectedSlotPlanet?.id === planet.id) {
            setSelectedSlotPlanet(null);
        } else {
            setSelectedSlotPlanet(planet);
        }
    };

    const handleTapSlotPlacement = (slotIndex) => {
        if (selectedSlotPlanet) {
            placePlanetInSlot(selectedSlotPlanet, slotIndex);
            setSelectedSlotPlanet(null);
        }
    };

    const placePlanetInSlot = (planet, slotIndex) => {
        const newOrder = [...userOrder];

        // If planet was already in another slot, remove it from there
        const existingIdx = newOrder.findIndex(p => p && p.id === planet.id);
        if (existingIdx !== -1) {
            newOrder[existingIdx] = null;
        }

        newOrder[slotIndex] = planet;
        setUserOrder(newOrder);

        // Filter out placed planets from scrambled tray
        const placedIds = newOrder.filter(Boolean).map(p => p.id);
        const remaining = PLANETS_DATA.filter(p => p.id !== 'sun' && p.id !== 'pluto' && !placedIds.includes(p.id));
        setScrambledPlanets(remaining);

        puzzleAudio.playSelect();
    };

    const handleRemoveFromSlot = (slotIndex) => {
        const removed = userOrder[slotIndex];
        if (!removed) return;

        const newOrder = [...userOrder];
        newOrder[slotIndex] = null;
        setUserOrder(newOrder);

        setScrambledPlanets(prev => [...prev, removed]);
        puzzleAudio.playSelect();
    };

    const checkOrderPuzzle = () => {
        const correctOrderIds = ['mercury', 'venus', 'earth', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune'];
        let correctCount = 0;

        userOrder.forEach((p, idx) => {
            if (p && p.id === correctOrderIds[idx]) {
                correctCount++;
            }
        });

        if (correctCount === 8) {
            puzzleAudio.playWinFanfare();
            setOrderPuzzleSolved(true);
            setOrderFeedback('🎉 PERFECT! You placed all 8 planets in exact order from the Sun! ⭐⭐⭐');
            setPointsEarned(50);
            setShowWinModal(true);
        } else if (correctCount >= 5) {
            puzzleAudio.playMatch();
            setOrderFeedback(`Almost there! ${correctCount}/8 planets are in correct position. Check Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune!`);
        } else {
            puzzleAudio.playError();
            setOrderFeedback(`Keep trying! ${correctCount}/8 planets correct. Tip: Mercury is 1st (closest to Sun) and Neptune is 8th (farthest)!`);
        }
    };

    const handleOrderHint = () => {
        puzzleAudio.playHint();
        const correctOrderIds = ['mercury', 'venus', 'earth', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune'];
        // Find first empty or wrong slot
        const wrongIdx = userOrder.findIndex((p, idx) => !p || p.id !== correctOrderIds[idx]);
        if (wrongIdx !== -1) {
            const correctTargetId = correctOrderIds[wrongIdx];
            const targetPlanet = PLANETS_DATA.find(p => p.id === correctTargetId);
            setOrderFeedback(`💡 Hint: Planet #${wrongIdx + 1} from the Sun is ${targetPlanet.name} ${targetPlanet.icon}!`);
        }
    };

    // --- Matching Puzzle Handlers ---
    const handleSelectClue = (idx) => {
        puzzleAudio.playSelect();
        setSelectedClueIndex(idx);

        if (selectedPlanetName !== null) {
            attemptMatch(idx, selectedPlanetName);
        }
    };

    const handleSelectPlanetForMatch = (planetName) => {
        puzzleAudio.playSelect();
        setSelectedPlanetName(planetName);

        if (selectedClueIndex !== null) {
            attemptMatch(selectedClueIndex, planetName);
        }
    };

    const attemptMatch = (clueIdx, planetName) => {
        const pair = MATCHING_PAIRS[clueIdx];
        if (pair.planet === planetName) {
            puzzleAudio.playMatch();
            const newMatches = [...matchedPairs, clueIdx];
            setMatchedPairs(newMatches);

            if (newMatches.length === MATCHING_PAIRS.length) {
                puzzleAudio.playWinFanfare();
                setMatchPuzzleSolved(true);
                setPointsEarned(50);
                setShowWinModal(true);
            }
        } else {
            puzzleAudio.playError();
        }

        setSelectedClueIndex(null);
        setSelectedPlanetName(null);
    };

    // --- Trivia Quiz Handlers ---
    const handleSelectQuizOption = (option) => {
        if (quizSubmitted) return;
        puzzleAudio.playSelect();
        setSelectedAnswer(option);
    };

    const handleSubmitQuizAnswer = () => {
        if (!selectedAnswer || quizSubmitted) return;

        const currentQ = QUIZ_QUESTIONS[currentQuestionIndex];
        const isCorrect = selectedAnswer === currentQ.correct;

        setQuizSubmitted(true);

        if (isCorrect) {
            puzzleAudio.playMatch();
            setQuizScore(prev => prev + 100);
        } else {
            puzzleAudio.playError();
        }
    };

    const handleNextQuizQuestion = () => {
        if (currentQuestionIndex < QUIZ_QUESTIONS.length - 1) {
            setCurrentQuestionIndex(prev => prev + 1);
            setSelectedAnswer(null);
            setQuizSubmitted(false);
        } else {
            puzzleAudio.playWinFanfare();
            setQuizCompleted(true);
            setPointsEarned(75);
            setShowWinModal(true);
        }
    };

    const resetQuiz = () => {
        setCurrentQuestionIndex(0);
        setSelectedAnswer(null);
        setQuizSubmitted(false);
        setQuizCompleted(false);
        setQuizScore(0);
    };

    return (
        <div className="solar-system-puzzle-container">
            {/* Header Banner */}
            <div className="solar-header">
                <div className="solar-title-group">
                    <h2 className="solar-title">🪐 Solar System Space Explorer</h2>
                    <p className="solar-subtitle">Discover planets, hear fun facts & solve cosmic space puzzles!</p>
                </div>

                {/* Sub-tabs inside Solar System */}
                <div className="solar-nav-tabs">
                    <button
                        className={`solar-tab-btn ${activeTab === 'explorer' ? 'active' : ''}`}
                        onClick={() => { puzzleAudio.playSelect(); setActiveTab('explorer'); }}
                    >
                        🪐 Solar Model
                    </button>
                    <button
                        className={`solar-tab-btn ${activeTab === 'order-puzzle' ? 'active' : ''}`}
                        onClick={() => { puzzleAudio.playSelect(); setActiveTab('order-puzzle'); }}
                    >
                        🎯 Order Planets
                    </button>
                    <button
                        className={`solar-tab-btn ${activeTab === 'matching-puzzle' ? 'active' : ''}`}
                        onClick={() => { puzzleAudio.playSelect(); setActiveTab('matching-puzzle'); }}
                    >
                        🃏 Planet Match
                    </button>
                    <button
                        className={`solar-tab-btn ${activeTab === 'trivia-quiz' ? 'active' : ''}`}
                        onClick={() => { puzzleAudio.playSelect(); setActiveTab('trivia-quiz'); }}
                    >
                        🧠 Cosmic Quiz
                    </button>
                </div>
            </div>

            {/* TAB 1: INTERACTIVE SOLAR SYSTEM EXPLORER */}
            {activeTab === 'explorer' && (
                <div className="explorer-view">
                    {/* Controls Bar */}
                    <div className="orbit-controls-bar">
                        <button
                            className="orbit-control-btn"
                            onClick={() => setIsOrbiting(!isOrbiting)}
                        >
                            {isOrbiting ? '⏸️ Pause Orbit' : '▶️ Resume Orbit'}
                        </button>
                        <div className="speed-toggle-group">
                            <span className="control-label">Speed:</span>
                            {[0.5, 1, 2].map(speed => (
                                <button
                                    key={speed}
                                    className={`speed-btn ${orbitSpeed === speed ? 'active' : ''}`}
                                    onClick={() => setOrbitSpeed(speed)}
                                >
                                    {speed}x
                                </button>
                            ))}
                        </div>
                        <span className="explorer-hint">💡 Tap any planet to explore facts & voice audio!</span>
                    </div>

                    {/* Cosmic Canvas / Orbit View */}
                    <div className="space-orbit-viewport">
                        <div className="stars-background"></div>

                        {/* Central Sun */}
                        <div
                            className="sun-orb"
                            onClick={() => handlePlanetClick(PLANETS_DATA[0])}
                            title="The Sun"
                        >
                            <span className="sun-pulse"></span>
                            <span className="sun-icon">☀️</span>
                            <span className="planet-tag">Sun</span>
                        </div>

                        {/* Orbiting Planets */}
                        {PLANETS_DATA.slice(1).map((planet, index) => {
                            // Calculate CSS orbit animation duration based on planet.orbitPeriod and speed
                            const animationDuration = (planet.orbitPeriod * 3) / orbitSpeed;

                            return (
                                <div
                                    key={planet.id}
                                    className="orbit-ring"
                                    style={{
                                        width: `${planet.orbitRadius * 2}px`,
                                        height: `${planet.orbitRadius * 2}px`,
                                        borderColor: planet.glowColor
                                    }}
                                >
                                    <div
                                        className={`planet-orbit-wrapper ${isOrbiting ? 'orbiting' : 'paused'}`}
                                        style={{
                                            animationDuration: `${animationDuration}s`
                                        }}
                                    >
                                        <div
                                            className="planet-orb-node"
                                            style={{
                                                width: `${planet.size}px`,
                                                height: `${planet.size}px`,
                                                background: planet.gradient,
                                                boxShadow: `0 0 16px ${planet.glowColor}`
                                            }}
                                            onClick={() => handlePlanetClick(planet)}
                                        >
                                            {/* Saturn Rings */}
                                            {planet.hasRings && <span className="saturn-ring-graphics"></span>}
                                            {/* Earth Moon */}
                                            {planet.hasMoon && <span className="earth-moon-graphics"></span>}
                                            {/* Jupiter Spot */}
                                            {planet.hasSpot && <span className="jupiter-spot-graphics"></span>}

                                            <span className="planet-icon-mini">{planet.icon}</span>
                                            <span className="planet-label-tooltip">{planet.name}</span>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    {/* Quick Planet Selector Carousel */}
                    <div className="planet-carousel">
                        {PLANETS_DATA.map(p => (
                            <button
                                key={p.id}
                                className={`carousel-card ${selectedPlanet.id === p.id ? 'selected' : ''}`}
                                onClick={() => handlePlanetClick(p)}
                            >
                                <span className="carousel-icon">{p.icon}</span>
                                <span className="carousel-name">{p.name}</span>
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* TAB 2: ORDER THE PLANETS PUZZLE */}
            {activeTab === 'order-puzzle' && (
                <div className="order-puzzle-view">
                    <div className="puzzle-instructions-box">
                        <h3>🎯 Drag or Tap Planets into Order from the Sun!</h3>
                        <p>Place all 8 planets in order starting from 1st closest (Mercury) to 8th farthest (Neptune)!</p>
                        <div className="puzzle-action-buttons">
                            <button className="puzzle-action-btn hint-btn" onClick={handleOrderHint}>💡 Hint</button>
                            <button className="puzzle-action-btn reset-btn" onClick={initOrderPuzzle}>🔄 Reset</button>
                        </div>
                    </div>

                    {orderFeedback && (
                        <div className={`order-feedback-alert ${orderPuzzleSolved ? 'success' : ''}`}>
                            {orderFeedback}
                        </div>
                    )}

                    {/* Solar Orbit Slots Row */}
                    <div className="solar-slots-track">
                        <div className="sun-slot-start">
                            <span>☀️ SUN</span>
                        </div>

                        <div className="slots-grid">
                            {Array.from({ length: 8 }).map((_, slotIdx) => {
                                const placedPlanet = userOrder[slotIdx];
                                const isSelectedForPlace = selectedSlotPlanet !== null;

                                return (
                                    <div
                                        key={slotIdx}
                                        className={`planet-drop-slot ${placedPlanet ? 'filled' : ''} ${isSelectedForPlace ? 'target-highlight' : ''}`}
                                        onDragOver={handleDragOver}
                                        onDrop={() => handleDropOnSlot(slotIdx)}
                                        onClick={() => handleTapSlotPlacement(slotIdx)}
                                    >
                                        <span className="slot-number">#{slotIdx + 1}</span>
                                        {placedPlanet ? (
                                            <div
                                                className="placed-planet-card"
                                                style={{ background: placedPlanet.gradient }}
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleRemoveFromSlot(slotIdx);
                                                }}
                                            >
                                                <span className="placed-icon">{placedPlanet.icon}</span>
                                                <span className="placed-name">{placedPlanet.name}</span>
                                                <span className="remove-cross" title="Remove">✕</span>
                                            </div>
                                        ) : (
                                            <span className="slot-placeholder">Drop Here</span>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* Scrambled Planets Tray */}
                    <div className="scrambled-tray-section">
                        <h4>Available Planets (Tap or Drag to place):</h4>
                        <div className="scrambled-planets-grid">
                            {scrambledPlanets.map(planet => {
                                const isSelected = selectedSlotPlanet?.id === planet.id;

                                return (
                                    <div
                                        key={planet.id}
                                        className={`scrambled-planet-card ${isSelected ? 'active-tap' : ''}`}
                                        style={{ background: planet.gradient }}
                                        draggable
                                        onDragStart={() => handleDragStart(planet)}
                                        onClick={() => handleTapPlanetSelection(planet)}
                                    >
                                        <span className="scrambled-icon">{planet.icon}</span>
                                        <span className="scrambled-name">{planet.name}</span>
                                        <span className="scrambled-type">{planet.nickname}</span>
                                    </div>
                                );
                            })}
                            {scrambledPlanets.length === 0 && (
                                <p className="tray-empty-msg">All planets are placed! Click "Check Answer" below!</p>
                            )}
                        </div>
                    </div>

                    <div className="order-check-footer">
                        <button
                            className="btn-check-order"
                            disabled={userOrder.filter(Boolean).length === 0}
                            onClick={checkOrderPuzzle}
                        >
                            ✨ Check My Planet Order ✨
                        </button>
                    </div>
                </div>
            )}

            {/* TAB 3: PLANET MATCHING PUZZLE */}
            {activeTab === 'matching-puzzle' && (
                <div className="matching-puzzle-view">
                    <div className="puzzle-instructions-box">
                        <h3>🃏 Match Cosmic Clues to Planet Cards!</h3>
                        <p>Tap a clue on the left, then tap its matching planet on the right!</p>
                        <button className="puzzle-action-btn reset-btn" onClick={initMatchingPuzzle}>🔄 Play Again</button>
                    </div>

                    <div className="matching-game-layout">
                        {/* Clues Column */}
                        <div className="matching-col">
                            <h4>Cosmic Clues 📖</h4>
                            {MATCHING_PAIRS.map((pair, idx) => {
                                const isMatched = matchedPairs.includes(idx);
                                const isSelected = selectedClueIndex === idx;

                                return (
                                    <div
                                        key={idx}
                                        className={`matching-card clue-card ${isMatched ? 'matched' : ''} ${isSelected ? 'selected' : ''}`}
                                        onClick={() => !isMatched && handleSelectClue(idx)}
                                    >
                                        <span className="matching-text">{pair.clue}</span>
                                        {isMatched && <span className="check-mark">✅</span>}
                                    </div>
                                );
                            })}
                        </div>

                        {/* Planets Column */}
                        <div className="matching-col">
                            <h4>Planets 🪐</h4>
                            {[...MATCHING_PAIRS].sort((a, b) => a.planet.localeCompare(b.planet)).map((pair, idx) => {
                                const planetObj = PLANETS_DATA.find(p => p.name === pair.planet);
                                const isMatched = matchedPairs.some(mIdx => MATCHING_PAIRS[mIdx].planet === pair.planet);
                                const isSelected = selectedPlanetName === pair.planet;

                                return (
                                    <div
                                        key={idx}
                                        className={`matching-card planet-card ${isMatched ? 'matched' : ''} ${isSelected ? 'selected' : ''}`}
                                        style={{ borderColor: planetObj?.color || '#FFD700' }}
                                        onClick={() => !isMatched && handleSelectPlanetForMatch(pair.planet)}
                                    >
                                        <span className="planet-card-icon">{planetObj?.icon}</span>
                                        <span className="matching-text">{pair.planet}</span>
                                        {isMatched && <span className="check-mark">✅</span>}
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </div>
            )}

            {/* TAB 4: COSMIC TRIVIA QUIZ */}
            {activeTab === 'trivia-quiz' && (
                <div className="trivia-quiz-view">
                    {!quizCompleted ? (
                        <div className="quiz-card-container">
                            <div className="quiz-progress-bar">
                                <span>Question {currentQuestionIndex + 1} of {QUIZ_QUESTIONS.length}</span>
                                <span className="quiz-score-badge">⭐ Score: {quizScore}</span>
                            </div>

                            <h3 className="quiz-question-text">
                                {QUIZ_QUESTIONS[currentQuestionIndex].question}
                            </h3>

                            <div className="quiz-options-grid">
                                {QUIZ_QUESTIONS[currentQuestionIndex].options.map((opt, idx) => {
                                    const isSelected = selectedAnswer === opt;
                                    const isCorrect = opt === QUIZ_QUESTIONS[currentQuestionIndex].correct;

                                    let btnStateClass = '';
                                    if (quizSubmitted) {
                                        if (isCorrect) btnStateClass = 'correct-choice';
                                        else if (isSelected) btnStateClass = 'wrong-choice';
                                    } else if (isSelected) {
                                        btnStateClass = 'selected-choice';
                                    }

                                    return (
                                        <button
                                            key={idx}
                                            className={`quiz-option-btn ${btnStateClass}`}
                                            onClick={() => handleSelectQuizOption(opt)}
                                        >
                                            <span className="option-bullet">{String.fromCharCode(65 + idx)}</span>
                                            <span className="option-label">{opt}</span>
                                        </button>
                                    );
                                })}
                            </div>

                            {quizSubmitted && (
                                <div className="quiz-explanation-box">
                                    <p className="explanation-text">
                                        💡 {QUIZ_QUESTIONS[currentQuestionIndex].explanation}
                                    </p>
                                </div>
                            )}

                            <div className="quiz-actions-footer">
                                {!quizSubmitted ? (
                                    <button
                                        className="btn-submit-quiz"
                                        disabled={!selectedAnswer}
                                        onClick={handleSubmitQuizAnswer}
                                    >
                                        Submit Answer ✔️
                                    </button>
                                ) : (
                                    <button
                                        className="btn-next-quiz"
                                        onClick={handleNextQuizQuestion}
                                    >
                                        {currentQuestionIndex < QUIZ_QUESTIONS.length - 1 ? 'Next Question ➔' : 'View Final Score 🏆'}
                                    </button>
                                )}
                            </div>
                        </div>
                    ) : (
                        <div className="quiz-results-container">
                            <span className="result-trophy">🏆</span>
                            <h2>Cosmic Quiz Complete!</h2>
                            <p className="final-score-display">Your Score: {quizScore} / {QUIZ_QUESTIONS.length * 100} Points!</p>
                            <button className="btn-submit-quiz" onClick={resetQuiz}>
                                🔄 Play Quiz Again
                            </button>
                        </div>
                    )}
                </div>
            )}

            {/* PLANET FACT CARD MODAL */}
            {showFactModal && selectedPlanet && (
                <div className="solar-modal-overlay" onClick={() => setShowFactModal(false)}>
                    <div className="solar-fact-card animate-bounce-in" onClick={(e) => e.stopPropagation()}>
                        <button className="solar-modal-close" onClick={() => setShowFactModal(false)}>✕</button>

                        <div className="fact-card-header" style={{ background: selectedPlanet.gradient }}>
                            <span className="fact-header-icon">{selectedPlanet.icon}</span>
                            <div className="fact-header-titles">
                                <h3>{selectedPlanet.name}</h3>
                                <span className="fact-nickname">{selectedPlanet.nickname}</span>
                                <span className="fact-type-badge">{selectedPlanet.type}</span>
                            </div>
                        </div>

                        {/* Speech Synthesis Voice Button */}
                        <div className="voice-reader-bar">
                            <button
                                className={`voice-read-btn ${isSpeaking ? 'speaking' : ''}`}
                                onClick={() => toggleSpeechFacts(
                                    `${selectedPlanet.name}. ${selectedPlanet.nickname}. ${selectedPlanet.funFacts.join(' ')}`
                                )}
                            >
                                {isSpeaking ? '🔊 Stop Reading Voice' : '🗣️ Listen to Facts (Kid Voice)'}
                            </button>
                        </div>

                        <div className="fact-card-body">
                            {/* Fast Stats Grid */}
                            <div className="planet-stats-grid">
                                <div className="stat-pill">
                                    <span className="stat-pill-icon">📏</span>
                                    <span className="stat-pill-label">Size Rank</span>
                                    <span className="stat-pill-val">{selectedPlanet.sizeRank}</span>
                                </div>
                                <div className="stat-pill">
                                    <span className="stat-pill-icon">🚀</span>
                                    <span className="stat-pill-label">Sun Distance</span>
                                    <span className="stat-pill-val">{selectedPlanet.distanceFromSun}</span>
                                </div>
                                <div className="stat-pill">
                                    <span className="stat-pill-icon">🌡️</span>
                                    <span className="stat-pill-label">Temp</span>
                                    <span className="stat-pill-val">{selectedPlanet.temperature}</span>
                                </div>
                                <div className="stat-pill">
                                    <span className="stat-pill-icon">🌙</span>
                                    <span className="stat-pill-label">Moons</span>
                                    <span className="stat-pill-val">{selectedPlanet.moonsCount} Moons</span>
                                </div>
                            </div>

                            {/* Fun Facts Bullet List */}
                            <div className="fun-facts-section">
                                <h4>✨ Fun Facts for Kids</h4>
                                <ul>
                                    {selectedPlanet.funFacts.map((fact, idx) => (
                                        <li key={idx}>🌟 {fact}</li>
                                    ))}
                                </ul>
                            </div>

                            {/* Trivia Box */}
                            <div className="trivia-highlight-box">
                                <span>🤓 Cosmic Curiosity:</span>
                                <p>{selectedPlanet.trivia}</p>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* WIN CELEBRATION MODAL */}
            {showWinModal && (
                <PuzzleWinModal
                    title="Cosmic Explorer Master! 🚀"
                    pointsAwarded={pointsEarned}
                    onReset={() => {
                        setShowWinModal(false);
                        if (activeTab === 'order-puzzle') initOrderPuzzle();
                        if (activeTab === 'matching-puzzle') initMatchingPuzzle();
                        if (activeTab === 'trivia-quiz') resetQuiz();
                    }}
                    onNextPuzzle={() => {
                        setShowWinModal(false);
                        const tabs = ['explorer', 'order-puzzle', 'matching-puzzle', 'trivia-quiz'];
                        const nextIdx = (tabs.indexOf(activeTab) + 1) % tabs.length;
                        setActiveTab(tabs[nextIdx]);
                    }}
                />
            )}
        </div>
    );
};

export default SolarSystemPuzzle;
