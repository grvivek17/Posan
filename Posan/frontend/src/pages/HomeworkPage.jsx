import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSubscription } from '../hooks/useSubscription';
import { homeworkAPI } from '../services/api';
import ProBadge from '../components/subscription/ProBadge';
import UpgradeModal from '../components/subscription/UpgradeModal';
import TestAnalysis from '../components/homework/TestAnalysis';
import StudyMaterialAssistant from '../components/homework/StudyMaterialAssistant';
import AssignmentTracker from '../components/homework/AssignmentTracker';
import PerformanceWidget from '../components/homework/PerformanceWidget';
import ExamHistoryWidget from '../components/homework/ExamHistoryWidget';
import './HomeworkPage.css';
import './HomeworkPageSidebar.css';

const HomeworkPage = () => {
    const { subscription, isPro, hasFeature } = useSubscription();
    const [selectedGrade, setSelectedGrade] = useState('Grade 4');
    const [activeTab, setActiveTab] = useState('study'); // 'study' or 'test'
    const [quizAnswer, setQuizAnswer] = useState(null);
    const [quizQuestion, setQuizQuestion] = useState({ question: '', correctAnswer: 0, wrongAnswer: 0 });
    const [isAIModalOpen, setIsAIModalOpen] = useState(false);
    const [showUpgradeModal, setShowUpgradeModal] = useState(false);

    const navigate = useNavigate();
    const username = localStorage.getItem('username') || 'Explorer';

    // Dynamic data state
    const [searchQuery, setSearchQuery] = useState('');
    const [assignments, setAssignments] = useState([]);
    const [stats, setStats] = useState(null);
    const [newAssignment, setNewAssignment] = useState({ title: '', subject: '', dueDate: '' });
    const [showAddAssignment, setShowAddAssignment] = useState(false);
    const [assignmentFile, setAssignmentFile] = useState(null);
    const [examHistory, setExamHistory] = useState([]);
    const [performanceData, setPerformanceData] = useState(null);

    const userId = localStorage.getItem('user_id') || 'guest';

    // Load assignments and stats on mount
    useEffect(() => {
        loadAssignments();
        loadStats();
        loadExamHistory();
        loadPerformanceAnalysis();
    }, []);

    // Generate random daily challenge quiz
    useEffect(() => {
        const ops = [
            { symbol: 'x', fn: (a, b) => a * b },
            { symbol: '+', fn: (a, b) => a + b }
        ];
        const op = ops[Math.floor(Math.random() * ops.length)];
        const a = Math.floor(Math.random() * 10) + 2;
        const b = Math.floor(Math.random() * 10) + 2;
        const correct = op.fn(a, b);
        let wrong = correct + (Math.random() < 0.5 ? Math.floor(Math.random() * 5) + 1 : -(Math.floor(Math.random() * 5) + 1));
        if (wrong === correct) wrong = correct + 3;
        setQuizQuestion({ question: `What is ${a} ${op.symbol} ${b}?`, correctAnswer: correct, wrongAnswer: wrong });
    }, []);

    const loadAssignments = async () => {
        try {
            const res = await homeworkAPI.getAssignments(userId);
            setAssignments(res.data.assignments || []);
        } catch (err) {
            console.error('Failed to load assignments:', err);
        }
    };

    const loadStats = async () => {
        try {
            const res = await homeworkAPI.getHomeworkStats(userId);
            setStats(res.data);
        } catch (err) {
            console.error('Failed to load stats:', err);
        }
    };

    const loadExamHistory = async () => {
        try {
            const res = await homeworkAPI.getExamHistory(userId, 10);
            setExamHistory(res.data.exams || []);
        } catch (err) {
            console.error('Failed to load exam history:', err);
        }
    };

    const loadPerformanceAnalysis = async () => {
        try {
            const res = await homeworkAPI.getPerformanceAnalysis(userId);
            setPerformanceData(res.data);
        } catch (err) {
            console.error('Failed to load performance analysis:', err);
        }
    };

    const handleAssignmentsUpdated = () => {
        loadAssignments();
        loadStats();
    };

    const handleSearch = (e) => {
        e.preventDefault();
        if (searchQuery.trim()) {
            setActiveTab('study');
            setIsAIModalOpen(true);
        }
    };

    const getSubjectIcon = (subject) => {
        const icons = { 'Mathematics': '➗', 'Math': '➗', 'Science': '🔬', 'History': '🏛️', 'English': '📖', 'Geography': '🌍', 'Art': '🎨' };
        return icons[subject] || '📝';
    };

    const formatDueDate = (dateStr) => {
        if (!dateStr) return '';
        const due = new Date(dateStr);
        const now = new Date();
        const diff = Math.ceil((due - now) / (1000 * 60 * 60 * 24));
        if (diff < 0) return 'Overdue';
        if (diff === 0) return 'Due: Today';
        if (diff === 1) return 'Due: Tomorrow';
        return `Due: ${due.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}`;
    };

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
                            <h1 className="user-name">
                                {username}!
                                {isPro() && <ProBadge variant="inline" style={{ marginLeft: '10px', fontSize: '0.5em' }} />}
                            </h1>
                            {subscription && (
                                <p style={{ fontSize: '0.85em', color: '#666', marginTop: '4px' }}>
                                    {isPro() ? '🌟 Pro Member' : '📚 Free Plan'}
                                </p>
                            )}
                        </div>
                    </div>
                    <button className="notification-btn" onClick={() => navigate('/achievements')}>
                        <span className="notification-icon">🔔</span>
                    </button>
                </div>

                {/* Search Bar */}
                <form className="search-bar-homework" onSubmit={handleSearch}>
                    <span className="search-icon">🔍</span>
                    <input
                        type="text"
                        placeholder="Search for homework help..."
                        className="search-input-homework"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                </form>

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
                                <p className="quiz-question">{quizQuestion.question}</p>
                                <div className="quiz-answers">
                                    <button
                                        className={`quiz-answer ${quizAnswer === quizQuestion.wrongAnswer ? 'incorrect' : ''}`}
                                        onClick={() => checkAnswer(quizQuestion.wrongAnswer)}
                                    >
                                        {quizQuestion.wrongAnswer}
                                    </button>
                                    <button
                                        className={`quiz-answer ${quizAnswer === quizQuestion.correctAnswer ? 'correct' : ''}`}
                                        onClick={() => checkAnswer(quizQuestion.correctAnswer)}
                                    >
                                        {quizQuestion.correctAnswer}
                                    </button>
                                </div>
                                {quizAnswer === quizQuestion.correctAnswer && (
                                    <p className="quiz-feedback correct">✅ Correct! Great job!</p>
                                )}
                                {quizAnswer === quizQuestion.wrongAnswer && (
                                    <p className="quiz-feedback incorrect">❌ Try again!</p>
                                )}
                            </div>
                        </section>

                        {/* Fun Resources */}
                        <section className="fun-resources">
                            <div className="section-header-hw">
                                <h2 className="section-title-hw">Fun Resources</h2>
                                <button className="view-all-btn" onClick={() => navigate('/magazines')}>View all</button>
                            </div>

                            <div className="resources-list">
                                {funResources.map((resource) => (
                                    <div key={resource.id} className="resource-item" onClick={() => navigate('/magazines')} style={{ cursor: 'pointer' }}>
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
                                        <button className="resource-arrow" onClick={(e) => { e.stopPropagation(); navigate('/magazines'); }}>→</button>
                                    </div>
                                ))}
                            </div>
                        </section>

                        {/* Stuck on a problem? */}
                        <div className="help-banner" onClick={() => { setActiveTab('study'); setIsAIModalOpen(true); }} style={{ cursor: 'pointer' }}>
                            <div className="help-content">
                                <span className="help-icon">📸</span>
                                <div>
                                    <h3 className="help-title">Stuck on a problem?</h3>
                                    <p className="help-subtitle">Snap a photo to get help!</p>
                                </div>
                            </div>
                            <button className="help-arrow" onClick={(e) => { e.stopPropagation(); setActiveTab('study'); setIsAIModalOpen(true); }}>→</button>
                        </div>
                    </div>

                    {/* Right Sidebar */}
                    <div className="homework-sidebar">
                        {/* AI Study Tool Widget */}
                        <div className="sidebar-widget ai-tool-widget">
                            <div className="widget-header">
                                <h3>🤖 AI Study Tool</h3>
                                {!isPro() && <ProBadge variant="small" />}
                            </div>
                            <div className="widget-content">
                                {isPro() ? (
                                    <>
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
                                                <span className="stat-number">{stats?.total_questions_answered || 0}</span>
                                                <span className="stat-label">Questions Answered</span>
                                            </div>
                                            <div className="stat-item">
                                                <span className="stat-number">{stats?.tests_analyzed || 0}</span>
                                                <span className="stat-label">Tests Analyzed</span>
                                            </div>
                                        </div>
                                    </>
                                ) : (
                                    <div className="pro-required-message">
                                        <div className="lock-icon" style={{ fontSize: '3em', marginBottom: '10px' }}>🔒</div>
                                        <p style={{ fontWeight: 'bold', marginBottom: '8px' }}>Pro Feature</p>
                                        <p style={{ fontSize: '0.9em', color: '#666', marginBottom: '15px' }}>
                                            Upgrade to Pro to access AI-powered homework assistance
                                        </p>
                                        <button
                                            className="quick-action-btn"
                                            style={{ width: '100%', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
                                            onClick={() => setShowUpgradeModal(true)}
                                        >
                                            <span>⭐ Upgrade to Pro</span>
                                        </button>
                                        <ul style={{ textAlign: 'left', fontSize: '0.85em', marginTop: '15px', color: '#555' }}>
                                            <li>✅ AI material processing</li>
                                            <li>✅ Unlimited question generation</li>
                                            <li>✅ Test analysis & insights</li>
                                        </ul>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Assignment Tracker Widget */}
                        <AssignmentTracker 
                            userId={userId} 
                            assignments={assignments} 
                            onAssignmentsUpdated={handleAssignmentsUpdated} 
                        />

                        {/* Progress Widget */}
                        <div className="sidebar-widget progress-widget">
                            <div className="widget-header">
                                <h3>📊 Weekly Progress</h3>
                            </div>
                            <div className="widget-content">
                                <div className="progress-stat">
                                    <div className="progress-label">
                                        <span>Avg Score</span>
                                        <span className="progress-value">{stats?.average_score || 0}%</span>
                                    </div>
                                    <div className="progress-bar">
                                        <div className="progress-fill" style={{ width: `${stats?.average_score || 0}%` }}></div>
                                    </div>
                                </div>
                                <div className="progress-stat">
                                    <div className="progress-label">
                                        <span>Assignments</span>
                                        <span className="progress-value">{stats?.completed_assignments || 0}/{stats?.total_assignments || 0}</span>
                                    </div>
                                    <div className="progress-bar">
                                        <div className="progress-fill" style={{ width: `${stats?.total_assignments ? (stats.completed_assignments / stats.total_assignments * 100) : 0}%` }}></div>
                                    </div>
                                </div>
                                <div className="progress-stat">
                                    <div className="progress-label">
                                        <span>Weekly Exams</span>
                                        <span className="progress-value">{stats?.weekly_exams || 0}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Performance Analysis Widget */}
                        <PerformanceWidget performanceData={performanceData} />

                        {/* Exam History Widget */}
                        <ExamHistoryWidget examHistory={examHistory} />
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

            {/* Upgrade Modal */}
            <UpgradeModal
                isOpen={showUpgradeModal}
                onClose={() => setShowUpgradeModal(false)}
                featureName="AI Study Tools"
            />
        </div>
    );
};

export default HomeworkPage;
