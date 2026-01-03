import { useState } from 'react';
import TestAnalysis from '../components/homework/TestAnalysis';
import StudyMaterialAssistant from '../components/homework/StudyMaterialAssistant';
import './HomeworkPage.css';
import './HomeworkPageSidebar.css';

const HomeworkPage = () => {
    const [selectedGrade, setSelectedGrade] = useState('Grade 4');
    const [activeTab, setActiveTab] = useState('study'); // 'study' or 'test'
    const [quizAnswer, setQuizAnswer] = useState(null);
    const [isAIModalOpen, setIsAIModalOpen] = useState(false);

    const grades = ['Grade 3', 'Grade 4', 'Grade 5', 'Grade 6'];

    const subjects = [
        {
            name: 'Math',
            subtitle: 'Numbers & Shapes',
            icon: '➗',
            color: 'var(--primary-yellow)',
            url: '/ai-content'
        },
        {
            name: 'Science',
            subtitle: 'World & Nature',
            icon: '🔬',
            color: '#A3E4F0',
            url: '/ai-content'
        },
        {
            name: 'History',
            subtitle: 'Time Travel',
            icon: '🏛️',
            color: '#E5E7EB',
            url: '/magazines'
        },
        {
            name: 'English',
            subtitle: 'Reading & Writing',
            icon: '📖',
            color: '#FFE4EF',
            url: '/magazines'
        }
    ];

    const funResources = [
        {
            id: 1,
            category: 'SCIENCE',
            title: 'Why is the sky blue?',
            time: '3 min read',
            icon: '🌍',
            color: '#4ECDC4'
        },
        {
            id: 2,
            category: 'MATH',
            title: 'Fun with numbers',
            time: '5 min read',
            icon: '🎲',
            color: '#FF9F1C'
        }
    ];

    const checkAnswer = (answer) => {
        setQuizAnswer(answer);
        setTimeout(() => setQuizAnswer(null), 2000);
    };

    return (
        <div className="homework-page-new">
            <div className="container">
                {/* Header with Greeting */}
                <div className="homework-header-new">
                    <div className="user-greeting">
                        <div className="user-avatar">👩</div>
                        <div>
                            <p className="greeting-text">Good Morning,</p>
                            <h1 className="user-name">Alex!</h1>
                        </div>
                    </div>
                    <button className="notification-btn">
                        <span className="notification-icon">🔔</span>
                    </button>
                </div>

                {/* Search Bar */}
                <div className="search-bar-homework">
                    <span className="search-icon">🔍</span>
                    <input
                        type="text"
                        placeholder="Search for homework help..."
                        className="search-input-homework"
                    />
                </div>

                {/* Main Content with Sidebar Layout */}
                <div className="homework-layout">
                    {/* Main Content */}
                    <div className="homework-main-content">
                        {/* What are we learning today? */}
                        <section className="learning-section">
                            <h2 className="section-title-hw">
                                What are we <span className="highlight-yellow">learning today?</span>
                            </h2>

                            {/* Grade Selection */}
                            <div className="grade-selector">
                                {grades.map((grade) => (
                                    <button
                                        key={grade}
                                        className={`grade-btn ${selectedGrade === grade ? 'active' : ''}`}
                                        onClick={() => setSelectedGrade(grade)}
                                    >
                                        {grade.replace('Grade ', '')}
                                    </button>
                                ))}
                            </div>

                            {/* Subject Cards */}
                            <div className="subjects-grid">
                                {subjects.map((subject) => (
                                    <div
                                        key={subject.name}
                                        className="subject-card"
                                        style={{ backgroundColor: subject.color }}
                                        onClick={() => window.location.href = subject.url}
                                    >
                                        <div className="subject-icon-large">{subject.icon}</div>
                                        <div className="subject-info">
                                            <h3 className="subject-name">{subject.name}</h3>
                                            <p className="subject-subtitle">{subject.subtitle}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </section>

                        {/* Daily Challenge */}
                        <section className="daily-challenge">
                            <div className="challenge-header">
                                <div>
                                    <span className="challenge-label">DAILY CHALLENGE</span>
                                    <h3 className="challenge-title">Quiz Time!</h3>
                                    <p className="challenge-subtitle">Solve this to earn a badge.</p>
                                </div>
                                <div className="trophy-icon">🏆</div>
                            </div>

                            <div className="quiz-box">
                                <p className="quiz-question">What is 5 x 6?</p>
                                <div className="quiz-answers">
                                    <button
                                        className={`quiz-answer ${quizAnswer === 25 ? 'incorrect' : ''}`}
                                        onClick={() => checkAnswer(25)}
                                    >
                                        25
                                    </button>
                                    <button
                                        className={`quiz-answer ${quizAnswer === 30 ? 'correct' : ''}`}
                                        onClick={() => checkAnswer(30)}
                                    >
                                        30
                                    </button>
                                </div>
                                {quizAnswer === 30 && (
                                    <p className="quiz-feedback correct">✅ Correct! Great job!</p>
                                )}
                                {quizAnswer === 25 && (
                                    <p className="quiz-feedback incorrect">❌ Try again!</p>
                                )}
                            </div>
                        </section>

                        {/* Fun Resources */}
                        <section className="fun-resources">
                            <div className="section-header-hw">
                                <h2 className="section-title-hw">Fun Resources</h2>
                                <button className="view-all-btn">View all</button>
                            </div>

                            <div className="resources-list">
                                {funResources.map((resource) => (
                                    <div key={resource.id} className="resource-item">
                                        <div
                                            className="resource-icon-circle"
                                            style={{ backgroundColor: resource.color }}
                                        >
                                            {resource.icon}
                                        </div>
                                        <div className="resource-info">
                                            <span className="resource-category">{resource.category}</span>
                                            <h4 className="resource-title">{resource.title}</h4>
                                            <span className="resource-time">{resource.time}</span>
                                        </div>
                                        <button className="resource-arrow">→</button>
                                    </div>
                                ))}
                            </div>
                        </section>

                        {/* Stuck on a problem? */}
                        <div className="help-banner">
                            <div className="help-content">
                                <span className="help-icon">📸</span>
                                <div>
                                    <h3 className="help-title">Stuck on a problem?</h3>
                                    <p className="help-subtitle">Snap a photo to get help!</p>
                                </div>
                            </div>
                            <button className="help-arrow">→</button>
                        </div>
                    </div>

                    {/* Right Sidebar */}
                    <div className="homework-sidebar">
                        {/* AI Study Tool Widget */}
                        <div className="sidebar-widget ai-tool-widget">
                            <div className="widget-header">
                                <h3>🤖 AI Study Tool</h3>
                            </div>
                            <div className="widget-content">
                                <p className="widget-description">
                                    Get instant help with homework using AI assistance
                                </p>
                                <div className="quick-actions">
                                    <button className="quick-action-btn open-ai-tool-btn" onClick={() => { setActiveTab('study'); setIsAIModalOpen(true); }}>
                                        <span className="action-icon">📖</span>
                                        <span>Study Help</span>
                                    </button>
                                    <button className="quick-action-btn open-ai-tool-btn" onClick={() => { setActiveTab('test'); setIsAIModalOpen(true); }}>
                                        <span className="action-icon">🎯</span>
                                        <span>Test Analysis</span>
                                    </button>
                                </div>
                                <div className="ai-stats">
                                    <div className="stat-item">
                                        <span className="stat-number">24</span>
                                        <span className="stat-label">Questions Answered</span>
                                    </div>
                                    <div className="stat-item">
                                        <span className="stat-number">5</span>
                                        <span className="stat-label">Tests Analyzed</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Assignment Tracker Widget */}
                        <div className="sidebar-widget assignment-tracker-widget">
                            <div className="widget-header">
                                <h3>📋 Assignment Tracker</h3>
                            </div>
                            <div className="widget-content">
                                <div className="upload-section">
                                    <div className="upload-area">
                                        <div className="upload-icon">📁</div>
                                        <p className="upload-text">Upload Assignment</p>
                                        <p className="upload-subtext">Drag & drop or click to upload</p>
                                        <input
                                            type="file"
                                            className="file-input"
                                            accept=".pdf,.doc,.docx,.jpg,.png"
                                        />
                                    </div>
                                </div>
                                <div className="assignments-list">
                                    <h4 className="assignments-title">Upcoming</h4>
                                    <div className="assignment-item">
                                        <div className="assignment-icon math">➗</div>
                                        <div className="assignment-details">
                                            <p className="assignment-name">Math Worksheet</p>
                                            <p className="assignment-due">Due: Tomorrow</p>
                                        </div>
                                        <span className="assignment-status pending">⏳</span>
                                    </div>
                                    <div className="assignment-item">
                                        <div className="assignment-icon science">🔬</div>
                                        <div className="assignment-details">
                                            <p className="assignment-name">Science Project</p>
                                            <p className="assignment-due">Due: Friday</p>
                                        </div>
                                        <span className="assignment-status pending">⏳</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Progress Widget */}
                        <div className="sidebar-widget progress-widget">
                            <div className="widget-header">
                                <h3>📊 Weekly Progress</h3>
                            </div>
                            <div className="widget-content">
                                <div className="progress-stat">
                                    <div className="progress-label">
                                        <span>Study Time</span>
                                        <span className="progress-value">12h 30m</span>
                                    </div>
                                    <div className="progress-bar">
                                        <div className="progress-fill" style={{ width: '75%' }}></div>
                                    </div>
                                </div>
                                <div className="progress-stat">
                                    <div className="progress-label">
                                        <span>Assignments</span>
                                        <span className="progress-value">4/6</span>
                                    </div>
                                    <div className="progress-bar">
                                        <div className="progress-fill" style={{ width: '66%' }}></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* AI Tools Modal */}
                {isAIModalOpen && (
                    <div className="ai-modal-overlay" onClick={() => setIsAIModalOpen(false)}>
                        <div className="ai-modal-content" onClick={(e) => e.stopPropagation()}>
                            <div className="ai-modal-header">
                                <h2>🚀 AI Study Tools</h2>
                                <button className="modal-close-btn" onClick={() => setIsAIModalOpen(false)}>✕</button>
                            </div>
                            <div className="ai-tabs">
                                <button
                                    className={`ai-tab-btn ${activeTab === 'study' ? 'active' : ''}`}
                                    onClick={() => setActiveTab('study')}
                                >
                                    📖 Study Assistant
                                </button>
                                <button
                                    className={`ai-tab-btn ${activeTab === 'test' ? 'active' : ''}`}
                                    onClick={() => setActiveTab('test')}
                                >
                                    🎯 Test Analysis
                                </button>
                            </div>
                            <div className="ai-tool-container">
                                {activeTab === 'study' ? <StudyMaterialAssistant /> : <TestAnalysis />}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default HomeworkPage;
