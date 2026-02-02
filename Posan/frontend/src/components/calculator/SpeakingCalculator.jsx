import { useState, useRef, useEffect } from 'react';
import VoiceRecorder from './VoiceRecorder';
import './SpeakingCalculator.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const SpeakingCalculator = () => {
    const [mode, setMode] = useState('voice'); // 'voice' or 'text'
    const [textInput, setTextInput] = useState('');
    const [isProcessing, setIsProcessing] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');
    const [history, setHistory] = useState([]);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const audioRef = useRef(null);
    const hasPlayedWelcome = useRef(false);

    // Play welcome message only once when component first mounts (entering screen)
    useEffect(() => {
        if (!hasPlayedWelcome.current && mode === 'voice') {
            playWelcomeMessage();
            hasPlayedWelcome.current = true;
        }
    }, []); // Empty dependency array - runs only once on mount

    const playWelcomeMessage = () => {
        // Use browser's built-in speech synthesis for instant playback
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(
                "Hello! Tell me what you want to calculate. For example, what is twelve times seven?"
            );

            // Configure voice for kids
            utterance.rate = 0.9; // Slightly slower
            utterance.pitch = 1.1; // Slightly higher pitch
            utterance.volume = 1.0;

            // Try to use a friendly voice if available
            const voices = window.speechSynthesis.getVoices();
            const friendlyVoice = voices.find(voice =>
                voice.name.includes('Female') ||
                voice.name.includes('Jenny') ||
                voice.name.includes('Samantha') ||
                voice.lang.startsWith('en')
            );

            if (friendlyVoice) {
                utterance.voice = friendlyVoice;
            }

            window.speechSynthesis.speak(utterance);
        }
    };

    const handleVoiceRecording = async (transcribedText) => {
        // Now we receive text directly from browser's speech recognition!
        setIsProcessing(true);
        setError('');
        setResult(null);

        try {
            // Use text endpoint since we already have the transcription
            const response = await fetch(`${API_BASE}/calculator/text`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: transcribedText })
            });

            if (!response.ok) {
                throw new Error('Failed to process calculation');
            }

            const data = await response.json();

            if (data.success) {
                setResult(data);
                addToHistory(data);

                // Automatically speak the answer using browser TTS
                speakResponse(data.response_text);
            } else {
                setError(data.error || 'Could not solve the problem');
            }

        } catch (err) {
            console.error('Voice calculation error:', err);
            setError('Failed to process your question. Please try again.');
        } finally {
            setIsProcessing(false);
        }
    };

    const speakResponse = (text) => {
        // Use browser's built-in speech synthesis for instant playback
        if ('speechSynthesis' in window) {
            // Cancel any ongoing speech
            window.speechSynthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(text);

            // Configure voice for kids
            utterance.rate = 0.9; // Slightly slower
            utterance.pitch = 1.1; // Slightly higher pitch
            utterance.volume = 1.0;

            // Try to use a friendly voice if available
            const voices = window.speechSynthesis.getVoices();
            const friendlyVoice = voices.find(voice =>
                voice.name.includes('Female') ||
                voice.name.includes('Jenny') ||
                voice.name.includes('Samantha') ||
                voice.lang.startsWith('en')
            );

            if (friendlyVoice) {
                utterance.voice = friendlyVoice;
            }

            // Track speaking state for UI feedback
            utterance.onstart = () => setIsSpeaking(true);
            utterance.onend = () => setIsSpeaking(false);
            utterance.onerror = () => setIsSpeaking(false);

            window.speechSynthesis.speak(utterance);
        }
    };

    const handleTextCalculation = async (e) => {
        e.preventDefault();

        if (!textInput.trim()) {
            setError('Please enter a math question');
            return;
        }

        setIsProcessing(true);
        setError('');
        setResult(null);

        try {
            const response = await fetch(`${API_BASE}/calculator/text`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: textInput })
            });

            if (!response.ok) {
                throw new Error('Failed to process text');
            }

            const data = await response.json();

            if (data.success) {
                setResult(data);
                addToHistory(data);

                // Automatically speak the answer
                speakResponse(data.response_text);
            } else {
                setError(data.error || 'Could not solve the problem');
            }

        } catch (err) {
            console.error('Text calculation error:', err);
            setError('Failed to process your question. Please try again.');
        } finally {
            setIsProcessing(false);
        }
    };

    const playAudio = (audioUrl) => {
        if (audioRef.current) {
            // Construct full URL
            const fullUrl = audioUrl.startsWith('http')
                ? audioUrl
                : `http://localhost:8000${audioUrl}`;

            audioRef.current.src = fullUrl;
            audioRef.current.play().catch(err => {
                console.error('Audio playback error:', err);
            });
        }
    };

    const addToHistory = (data) => {
        const historyItem = {
            id: Date.now(),
            question: data.transcription,
            expression: data.expression,
            result: data.result,
            timestamp: new Date().toLocaleTimeString()
        };

        setHistory(prev => [historyItem, ...prev].slice(0, 10)); // Keep last 10
    };

    const clearHistory = () => {
        setHistory([]);
        setResult(null);
        setError('');
    };

    const exampleQuestions = [
        "What is twelve times seven?",
        "Twenty five plus three",
        "One hundred divided by four",
        "Five squared",
        "Fifteen minus eight"
    ];

    const tryExample = (question) => {
        setTextInput(question);
        setMode('text');
    };

    return (
        <div className="speaking-calculator">
            <div className="calculator-header">
                <h2>🧮 Speaking Calculator</h2>
                <p>Ask math questions with your voice or type them!</p>
            </div>

            {/* Mode Toggle */}
            <div className="mode-toggle">
                <button
                    className={`mode-btn ${mode === 'voice' ? 'active' : ''}`}
                    onClick={() => setMode('voice')}
                >
                    🎤 Voice Mode
                </button>
                <button
                    className={`mode-btn ${mode === 'text' ? 'active' : ''}`}
                    onClick={() => setMode('text')}
                >
                    ⌨️ Text Mode
                </button>
            </div>

            {/* Input Section */}
            <div className="input-section">
                {mode === 'voice' ? (
                    <>
                        {/* Welcome Message Banner */}
                        <div className="welcome-banner">
                            <div className="welcome-icon">🎤</div>
                            <div className="welcome-text">
                                <strong>Welcome to Voice Calculator!</strong>
                                <p>Tell me what you want to calculate</p>
                            </div>
                            <button
                                className="replay-welcome-btn"
                                onClick={playWelcomeMessage}
                                title="Replay welcome message"
                            >
                                🔊 Replay
                            </button>
                        </div>

                        <VoiceRecorder
                            onRecordingComplete={handleVoiceRecording}
                            isProcessing={isProcessing}
                        />
                    </>
                ) : (
                    <form onSubmit={handleTextCalculation} className="text-input-form">
                        <input
                            type="text"
                            value={textInput}
                            onChange={(e) => setTextInput(e.target.value)}
                            placeholder="e.g., What is twelve times seven?"
                            className="text-input"
                            disabled={isProcessing}
                        />
                        <button
                            type="submit"
                            className="calculate-btn"
                            disabled={isProcessing}
                        >
                            {isProcessing ? '⏳ Calculating...' : '🧮 Calculate'}
                        </button>
                    </form>
                )}
            </div>

            {/* Error Display */}
            {error && (
                <div className="error-message">
                    ❌ {error}
                </div>
            )}

            {/* Result Display */}
            {result && result.success && (
                <div className="result-card">
                    <div className="result-header">
                        <span className="result-badge">✅ Answer</span>
                    </div>

                    <div className="result-content">
                        <div className="result-item">
                            <span className="label">You asked:</span>
                            <span className="value question-text">"{result.transcription}"</span>
                        </div>

                        <div className="result-item">
                            <span className="label">Expression:</span>
                            <span className="value expression-text">{result.expression}</span>
                        </div>

                        <div className="result-item highlighted">
                            <span className="label">Answer:</span>
                            <span className="value result-number">{result.result}</span>
                        </div>

                        <div className="result-item">
                            <span className="label">Explanation:</span>
                            <span className="value explanation-text">{result.response_text}</span>
                        </div>
                    </div>

                    {/* Voice Controls */}
                    <div className="audio-controls">
                        <button
                            className={`replay-btn ${isSpeaking ? 'speaking' : ''}`}
                            onClick={() => speakResponse(result.response_text)}
                            disabled={isSpeaking}
                        >
                            {isSpeaking ? '🔊 Speaking...' : '🔊 Replay Answer'}
                        </button>
                    </div>
                </div>
            )}

            {/* Example Questions */}
            {!result && !error && (
                <div className="examples-section">
                    <h3>Try these examples:</h3>
                    <div className="examples-grid">
                        {exampleQuestions.map((question, index) => (
                            <button
                                key={index}
                                className="example-btn"
                                onClick={() => tryExample(question)}
                            >
                                {question}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* History */}
            {history.length > 0 && (
                <div className="history-section">
                    <div className="history-header">
                        <h3>📜 Recent Calculations</h3>
                        <button className="clear-btn" onClick={clearHistory}>
                            Clear
                        </button>
                    </div>
                    <div className="history-list">
                        {history.map((item) => (
                            <div key={item.id} className="history-item">
                                <div className="history-question">{item.question}</div>
                                <div className="history-calculation">
                                    {item.expression} = <strong>{item.result}</strong>
                                </div>
                                <div className="history-time">{item.timestamp}</div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Hidden audio player */}
            <audio ref={audioRef} style={{ display: 'none' }} />
        </div>
    );
};

export default SpeakingCalculator;
