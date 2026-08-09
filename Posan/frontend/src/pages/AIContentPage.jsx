import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import AudioPlayer from '../components/podcasts/AudioPlayer';
import SpeakingCalculator from '../components/calculator/SpeakingCalculator';
import ProBadge from '../components/subscription/ProBadge';
import UpgradeModal from '../components/subscription/UpgradeModal';
import { useSubscription } from '../hooks/useSubscription';
import './AIContentPage.css';

// Use environment variable or fallback to localhost for development
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const AIContentPage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [activeTab, setActiveTab] = useState('story');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');

    // Form states
    const [topic, setTopic] = useState('');
    const [ageGroup, setAgeGroup] = useState('6-8');
    const [wordCount, setWordCount] = useState(200);
    const [details, setDetails] = useState('');
    const [articleType, setArticleType] = useState('educational');
    const [numQuestions, setNumQuestions] = useState(5);

    // Podcast states
    const [podcastDuration, setPodcastDuration] = useState('short');
    const [podcastStyle, setPodcastStyle] = useState('fun');
    const [currentPodcast, setCurrentPodcast] = useState(null);

    // Subscription
    const { subscription, hasFeature, isPro } = useSubscription();
    const [showUpgradeModal, setShowUpgradeModal] = useState(false);
    const [upgradeFeatureName, setUpgradeFeatureName] = useState('');

    const ageGroups = [
        { value: '3-5', label: '🧒 Toddlers (3-5 years)' },
        { value: '6-8', label: '👦 Early (6-8 years)' },
        { value: '9-11', label: '🧑 Middle (9-11 years)' },
        { value: '12-14', label: '👨‍🎓 Preteens (12-14 years)' }
    ];

    const articleTypes = [
        { value: 'educational', label: '📚 Educational' },
        { value: 'fun_facts', label: '🤯 Fun Facts' },
        { value: 'how_to', label: '🛠️ How-To Guide' },
        { value: 'science', label: '🔬 Science' }
    ];

    // Handle navigation from weekly highlights
    useEffect(() => {
        if (location.state?.showPodcast && location.state?.podcastData) {
            const podcastData = location.state.podcastData;

            // Set the podcast data
            setCurrentPodcast({
                ...podcastData,
                id: Date.now(),
                createdAt: new Date().toISOString()
            });

            // Set result to display
            setResult({ type: 'podcast', data: podcastData });

            // Switch to podcast tab
            setActiveTab('podcast');

            // Clear the navigation state
            navigate(location.pathname, { replace: true, state: {} });
        }
    }, [location.state]);

    const generateContent = async (type) => {
        if (!topic.trim() && type !== 'fact' && type !== 'riddle') {
            setError('Please enter a topic!');
            return;
        }

        setLoading(true);
        setError('');
        setResult(null);

        try {
            let response;
            const headers = { 'Content-Type': 'application/json' };

            switch (type) {
                case 'story':
                    response = await fetch(`${API_BASE}/ai/generate/story`, {
                        method: 'POST',
                        headers,
                        body: JSON.stringify({ topic, age_group: ageGroup, word_count: wordCount, details: details })
                    });
                    break;
                case 'article':
                    response = await fetch(`${API_BASE}/ai/generate/article`, {
                        method: 'POST',
                        headers,
                        body: JSON.stringify({ topic, age_group: ageGroup, article_type: articleType })
                    });
                    break;
                case 'quiz':
                    response = await fetch(`${API_BASE}/ai/generate/quiz`, {
                        method: 'POST',
                        headers,
                        body: JSON.stringify({ topic, age_group: ageGroup, num_questions: numQuestions })
                    });
                    break;
                case 'fact':
                    response = await fetch(`${API_BASE}/ai/generate/fun-fact?topic=${encodeURIComponent(topic)}&age_group=${ageGroup}`);
                    break;
                case 'riddle':
                    response = await fetch(`${API_BASE}/ai/generate/riddle?topic=${encodeURIComponent(topic)}&age_group=${ageGroup}`);
                    break;
                case 'words':
                    response = await fetch(`${API_BASE}/ai/generate/word-search`, {
                        method: 'POST',
                        headers,
                        body: JSON.stringify({ topic, age_group: ageGroup, num_words: 10 })
                    });
                    break;
                case 'podcast':
                    response = await fetch(`${API_BASE}/podcasts/generate`, {
                        method: 'POST',
                        headers,
                        body: JSON.stringify({
                            topic,
                            age_group: ageGroup,
                            duration: podcastDuration,
                            style: podcastStyle
                        })
                    });
                    break;
                default:
                    throw new Error('Unknown content type');
            }

            if (!response.ok) throw new Error('Failed to generate content');

            const data = await response.json();

            // Special handling for podcast
            if (type === 'podcast') {
                setCurrentPodcast({
                    ...data,
                    id: Date.now(),
                    createdAt: new Date().toISOString()
                });
            }

            setResult({ type, data });
        } catch (err) {
            setError(err.message || 'Something went wrong!');
        } finally {
            setLoading(false);
        }
    };

    const renderResult = () => {
        if (!result) return null;

        const { type, data } = result;

        switch (type) {
            case 'story':
            case 'article':
                return (
                    <div className="result-card story-result">
                        <h3 className="result-title">{data.title}</h3>
                        <div className="result-meta">
                            <span className="badge">{data.age_group} years</span>
                            {data.word_count && <span className="badge">{data.word_count} words</span>}
                        </div>
                        <div className="result-content">
                            {data.content.split('\n').map((paragraph, i) => (
                                <p key={i}>{paragraph}</p>
                            ))}
                        </div>
                    </div>
                );

            case 'quiz':
                return (
                    <div className="result-card quiz-result">
                        <h3 className="result-title">🧠 Quiz Questions</h3>
                        {data.map((q, i) => (
                            <div key={i} className="quiz-question">
                                <h4>Question {i + 1}: {q.question}</h4>
                                <ul className="quiz-options">
                                    {q.options?.map((opt, j) => (
                                        <li key={j}>{String.fromCharCode(65 + j)}) {opt}</li>
                                    ))}
                                </ul>
                                {q.correct_answer && (
                                    <p className="quiz-answer">✅ Answer: {q.correct_answer}</p>
                                )}
                                {q.explanation && (
                                    <p className="quiz-explanation">💡 {q.explanation}</p>
                                )}
                            </div>
                        ))}
                    </div>
                );

            case 'fact':
                return (
                    <div className="result-card fact-result">
                        <h3 className="result-title">🌟 Fun Fact</h3>
                        <p className="fun-fact-text">{data.fun_fact}</p>
                    </div>
                );

            case 'riddle':
                return (
                    <div className="result-card riddle-result">
                        <h3 className="result-title">🤔 Riddle</h3>
                        <p className="riddle-text">{data.riddle}</p>
                        <details className="riddle-answer">
                            <summary>Show Answer</summary>
                            <p>{data.answer}</p>
                        </details>
                    </div>
                );

            case 'words':
                return (
                    <div className="result-card words-result">
                        <h3 className="result-title">🔤 Word Search Words</h3>
                        <div className="word-list">
                            {data.words?.map((word, i) => (
                                <span key={i} className="word-badge">{word}</span>
                            ))}
                        </div>
                    </div>
                );

            case 'podcast':
                return (
                    <div className="result-card podcast-result">
                        <h3 className="result-title">🎙️ {data.topic || 'Your Podcast'}</h3>
                        <div className="result-meta">
                            <span className="badge">{data.metadata?.style || 'fun'}</span>
                            <span className="badge">{data.metadata?.estimated_minutes || 3} min</span>
                            <span className="badge">{data.metadata?.age_group || ageGroup}</span>
                        </div>

                        {/* Audio Player */}
                        {currentPodcast && (
                            <AudioPlayer
                                script={currentPodcast.script}
                                podcastId={currentPodcast.id?.toString()}
                                topic={currentPodcast.topic}
                            />
                        )}

                        {/* Script */}
                        <div className="podcast-script-container">
                            <h4>📝 Podcast Script:</h4>
                            <div className="podcast-script-content">
                                {data.script?.split('\n').map((line, i) => {
                                    if (line.trim().startsWith('[') && line.trim().endsWith(']')) {
                                        return <h5 key={i} className="script-section">{line.trim()}</h5>;
                                    } else if (line.trim()) {
                                        return <p key={i}>{line}</p>;
                                    }
                                    return null;
                                })}
                            </div>
                        </div>
                    </div>
                );

            default:
                return <pre>{JSON.stringify(data, null, 2)}</pre>;
        }
    };

    return (
        <div className="ai-content-page">
            <div className="ai-header">
                <div className="header-content">
                    <div style={{ textAlign: 'center' }}>
                        <h1>🤖 AI Content Creator</h1>
                        <p>Create amazing content for kids using AI magic!</p>
                    </div>
                    {isPro() && (
                        <div className="subscription-badge">
                            <ProBadge variant="inline" showLabel={true} />
                        </div>
                    )}
                </div>
            </div>

            {/* Upgrade Modal */}
            <UpgradeModal
                isOpen={showUpgradeModal}
                onClose={() => setShowUpgradeModal(false)}
                featureName={upgradeFeatureName}
            />

            <div className="ai-content-wrapper">
                <div className="ai-tabs">
                    <button
                        className={`tab ${activeTab === 'story' ? 'active' : ''}`}
                        onClick={() => setActiveTab('story')}
                    >
                        📖 Story
                    </button>
                    <button
                        className={`tab ${activeTab === 'article' ? 'active' : ''}`}
                        onClick={() => setActiveTab('article')}
                    >
                        📰 Article
                    </button>
                    <button
                        className={`tab ${activeTab === 'quiz' ? 'active' : ''}`}
                        onClick={() => setActiveTab('quiz')}
                    >
                        🧠 Quiz
                    </button>
                    <button
                        className={`tab ${activeTab === 'fun' ? 'active' : ''}`}
                        onClick={() => setActiveTab('fun')}
                    >
                        🎉 Fun Stuff
                    </button>
                    <button
                        className={`tab ${activeTab === 'podcast' ? 'active' : ''}`}
                        onClick={() => setActiveTab('podcast')}
                    >
                        🎙️ Podcast
                    </button>
                    <button
                        className={`tab ${activeTab === 'calculator' ? 'active' : ''}`}
                        onClick={() => setActiveTab('calculator')}
                    >
                        🧮 Calculator
                    </button>
                </div>

                {/* Calculator has its own UI, hide form when active */}
                {activeTab === 'calculator' ? (
                    <SpeakingCalculator />
                ) : (
                    <div className="ai-form-container">
                        <div className="form-group">
                            <label htmlFor="topic">✨ What topic do you want to explore?</label>
                            <input
                                type="text"
                                id="topic"
                                placeholder="e.g., dinosaurs, space, ocean animals, friendship..."
                                value={topic}
                                onChange={(e) => setTopic(e.target.value)}
                                className="topic-input"
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="ageGroup">👶 Age Group</label>
                            <select
                                id="ageGroup"
                                value={ageGroup}
                                onChange={(e) => setAgeGroup(e.target.value)}
                                className="select-input"
                            >
                                {ageGroups.map(ag => (
                                    <option key={ag.value} value={ag.value}>{ag.label}</option>
                                ))}
                            </select>
                        </div>

                        {activeTab === 'story' && (
                            <>
                                <div className="form-group">
                                    <label htmlFor="wordCount">📏 Story Length</label>
                                    <input
                                        type="range"
                                        id="wordCount"
                                        min="100"
                                        max="500"
                                        value={wordCount}
                                        onChange={(e) => setWordCount(Number(e.target.value))}
                                    />
                                    <span className="range-value">{wordCount} words</span>
                                </div>
                                <div className="form-group">
                                    <label>Story Details / Plot (Optional)</label>
                                    <textarea
                                        value={details}
                                        onChange={(e) => setDetails(e.target.value)}
                                        placeholder="e.g., The main character is a brave dog named Max who finds a hidden treasure..."
                                        disabled={loading}
                                        rows={3}
                                        maxLength={200}
                                    />
                                </div>
                                <button
                                    className="generate-btn"
                                    onClick={() => generateContent('story')}
                                    disabled={loading}
                                >
                                    {loading ? '✨ Creating Story...' : '📖 Generate Story'}
                                </button>
                            </>
                        )}

                        {activeTab === 'article' && (
                            <>
                                <div className="form-group">
                                    <label htmlFor="articleType">📚 Article Type</label>
                                    <select
                                        id="articleType"
                                        value={articleType}
                                        onChange={(e) => setArticleType(e.target.value)}
                                        className="select-input"
                                    >
                                        {articleTypes.map(at => (
                                            <option key={at.value} value={at.value}>{at.label}</option>
                                        ))}
                                    </select>
                                </div>
                                <button
                                    className="generate-btn"
                                    onClick={() => generateContent('article')}
                                    disabled={loading}
                                >
                                    {loading ? '✨ Writing Article...' : '📰 Generate Article'}
                                </button>
                            </>
                        )}

                        {activeTab === 'quiz' && (
                            <>
                                <div className="form-group">
                                    <label htmlFor="numQuestions">❓ Number of Questions</label>
                                    <input
                                        type="range"
                                        id="numQuestions"
                                        min="3"
                                        max="10"
                                        value={numQuestions}
                                        onChange={(e) => setNumQuestions(Number(e.target.value))}
                                    />
                                    <span className="range-value">{numQuestions} questions</span>
                                </div>
                                <button
                                    className="generate-btn"
                                    onClick={() => generateContent('quiz')}
                                    disabled={loading}
                                >
                                    {loading ? '✨ Creating Quiz...' : '🧠 Generate Quiz'}
                                </button>
                            </>
                        )}

                        {activeTab === 'fun' && (
                            <div className="fun-buttons">
                                <button
                                    className="generate-btn fun-btn"
                                    onClick={() => generateContent('fact')}
                                    disabled={loading}
                                >
                                    {loading ? '✨ Finding...' : '🌟 Get Fun Fact'}
                                </button>
                                <button
                                    className="generate-btn fun-btn"
                                    onClick={() => generateContent('riddle')}
                                    disabled={loading}
                                >
                                    {loading ? '✨ Thinking...' : '🤔 Get Riddle'}
                                </button>
                                <button
                                    className="generate-btn fun-btn"
                                    onClick={() => generateContent('words')}
                                    disabled={loading}
                                >
                                    {loading ? '✨ Finding...' : '🔤 Word Search Words'}
                                </button>
                            </div>
                        )}

                        {activeTab === 'podcast' && (
                            <>
                                <div className="form-group">
                                    <label htmlFor="podcastDuration">⏱️ Duration</label>
                                    <select
                                        id="podcastDuration"
                                        value={podcastDuration}
                                        onChange={(e) => setPodcastDuration(e.target.value)}
                                        className="select-input"
                                    >
                                        <option value="short">Short (2-3 min)</option>
                                        <option value="medium">Medium (5 min)</option>
                                        <option value="long">Long (10 min)</option>
                                    </select>
                                </div>
                                <div className="form-group">
                                    <label htmlFor="podcastStyle">🎨 Style</label>
                                    <select
                                        id="podcastStyle"
                                        value={podcastStyle}
                                        onChange={(e) => setPodcastStyle(e.target.value)}
                                        className="select-input"
                                    >
                                        <option value="fun">🎉 Fun & Exciting</option>
                                        <option value="educational">📚 Educational</option>
                                        <option value="story">📖 Story-based</option>
                                    </select>
                                </div>
                                <button
                                    className="generate-btn"
                                    onClick={() => generateContent('podcast')}
                                    disabled={loading}
                                >
                                    {loading ? '🎙️ Creating Podcast...' : '🎧 Generate Podcast'}
                                </button>
                            </>
                        )}

                        {error && <div className="error-message">❌ {error}</div>}
                    </div>
                )}

                {loading && (
                    <div className="loading-container">
                        <div className="loading-spinner"></div>
                        <p>AI is working its magic... ✨</p>
                    </div>
                )}

                <div className="results-container">
                    {renderResult()}
                </div>
            </div>
        </div>
    );
};

export default AIContentPage;
