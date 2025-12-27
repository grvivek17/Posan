import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './AIContentPage.css';

const API_BASE = 'http://localhost:8000/api/v1';

const AIContentPage = () => {
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState('story');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');

    // Form states
    const [topic, setTopic] = useState('');
    const [ageGroup, setAgeGroup] = useState('6-8');
    const [wordCount, setWordCount] = useState(200);
    const [articleType, setArticleType] = useState('educational');
    const [numQuestions, setNumQuestions] = useState(5);

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

    const generateContent = async (type) => {
        if (!topic.trim()) {
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
                        body: JSON.stringify({ topic, age_group: ageGroup, word_count: wordCount })
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
                default:
                    throw new Error('Unknown content type');
            }

            if (!response.ok) throw new Error('Failed to generate content');

            const data = await response.json();
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

            default:
                return <pre>{JSON.stringify(data, null, 2)}</pre>;
        }
    };

    return (
        <div className="ai-content-page">
            <div className="ai-header">
                <h1>🤖 AI Content Creator</h1>
                <p>Create amazing content for kids using AI magic!</p>
            </div>

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
            </div>

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

                {error && <div className="error-message">❌ {error}</div>}
            </div>

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
    );
};

export default AIContentPage;
