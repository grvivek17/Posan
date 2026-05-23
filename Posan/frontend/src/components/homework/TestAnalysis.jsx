import { useState } from 'react';
import './TestAnalysis.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const TestAnalysis = () => {
    const [loading, setLoading] = useState(false);
    const [analysis, setAnalysis] = useState(null);
    const [uploadedFile, setUploadedFile] = useState(null);
    const [isDragging, setIsDragging] = useState(false);
    const [analysisMode, setAnalysisMode] = useState('upload'); // 'upload' or 'manual'
    const [showAnswerKey, setShowAnswerKey] = useState(false);
    const [answerKeyRows, setAnswerKeyRows] = useState([
        { question_number: 1, answer: '', marks: 5 }
    ]);
    const [formData, setFormData] = useState({
        studentName: '',
        subject: 'Mathematics',
        score: '',
        total: '100',
        ageGroup: '6-8',
        grade: 3,
        weakAreas: '',
        strongAreas: ''
    });

    const subjects = [
        { value: 'Mathematics', icon: '🔢' },
        { value: 'Science', icon: '🔬' },
        { value: 'English', icon: '📚' },
        { value: 'History', icon: '🏛️' },
        { value: 'Geography', icon: '🌍' },
        { value: 'Art', icon: '🎨' }
    ];

    const ageGroups = [
        { value: '3-5', label: 'Toddler (3-5)' },
        { value: '6-8', label: 'Early Elementary (6-8)' },
        { value: '9-11', label: 'Middle Elementary (9-11)' },
        { value: '12-14', label: 'Middle School (12-14)' }
    ];

    const grades = [
        { value: 1, label: 'Grade 1', age: '6-7' },
        { value: 2, label: 'Grade 2', age: '7-8' },
        { value: 3, label: 'Grade 3', age: '8-9' },
        { value: 4, label: 'Grade 4', age: '9-10' },
        { value: 5, label: 'Grade 5', age: '10-11' },
        { value: 6, label: 'Grade 6', age: '11-12' },
        { value: 7, label: 'Grade 7', age: '12-13' },
        { value: 8, label: 'Grade 8', age: '13-14' }
    ];

    // Answer key helpers
    const addAnswerKeyRow = () => {
        const nextNum = answerKeyRows.length + 1;
        setAnswerKeyRows([...answerKeyRows, { question_number: nextNum, answer: '', marks: 5 }]);
    };

    const removeAnswerKeyRow = (index) => {
        if (answerKeyRows.length <= 1) return;
        setAnswerKeyRows(answerKeyRows.filter((_, i) => i !== index));
    };

    const updateAnswerKeyRow = (index, field, value) => {
        const updated = [...answerKeyRows];
        updated[index] = { ...updated[index], [field]: value };
        setAnswerKeyRows(updated);
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    };

    const handleFileSelect = (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    };

    const handleFileUpload = (file) => {
        // Validate file type
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
        if (!validTypes.includes(file.type)) {
            alert('Please upload a JPG, PNG, or PDF file');
            return;
        }

        // Validate file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            alert('File size must be less than 10MB');
            return;
        }

        setUploadedFile(file);
    };

    const analyzeUploadedTest = async () => {
        if (!uploadedFile) {
            alert('Please upload a test paper first!');
            return;
        }

        if (!formData.studentName || !formData.subject) {
            alert('Please enter student name and subject!');
            return;
        }

        setLoading(true);
        setAnalysis(null);

        try {
            // Create form data for file upload
            const uploadFormData = new FormData();
            uploadFormData.append('file', uploadedFile);

            // Build query params
            let url = `${API_BASE}/ai/analyze/test-upload?student_name=${encodeURIComponent(formData.studentName)}&subject=${encodeURIComponent(formData.subject)}&age_group=${encodeURIComponent(formData.ageGroup)}&grade=${formData.grade}`;

            // Add model answers if answer key is provided
            if (showAnswerKey && answerKeyRows.some(r => r.answer.trim())) {
                const validAnswers = answerKeyRows.filter(r => r.answer.trim());
                url += `&model_answers=${encodeURIComponent(JSON.stringify(validAnswers))}`;
            }

            // Send to OCR + AI analysis endpoint
            const response = await fetch(url, {
                method: 'POST',
                body: uploadFormData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to analyze test paper');
            }

            const data = await response.json();

            // Handle structured report response
            if (data.analysis_type === 'structured_report') {
                setAnalysis({
                    type: 'structured',
                    subject: data.subject,
                    score: data.score,
                    total: data.total,
                    percentage: data.percentage,
                    performance_level: data.performance_level,
                    questions_found: data.questions_found,
                    correct_count: data.correct_count,
                    incorrect_count: data.incorrect_count,
                    strong_zones: data.strong_zones || [],
                    weak_zones: data.weak_zones || [],
                    focus_plan: data.focus_plan || {},
                    teacher_insights: data.teacher_insights,
                    encouragement: data.encouragement,
                    student_name: data.student_name,
                    grade: data.grade
                });
            }
            // Handle score-based fallback
            else if (data.analysis_type === 'score_based') {
                setAnalysis({
                    type: 'legacy',
                    subject: data.subject,
                    score: data.score,
                    total: data.total,
                    percentage: data.percentage,
                    performance_level: data.performance_level,
                    analysis: data.analysis,
                    motivational_quote: data.motivational_quote,
                    weak_areas: data.weak_areas || [],
                    strong_areas: data.strong_areas || []
                });
            }
            // No score or questions found
            else {
                alert(`Could not extract questions or score from this test paper.\n\n${data.message}\n\nPlease use manual entry mode or try a clearer image.`);
                setLoading(false);
                return;
            }

        } catch (err) {
            let errorMessage = 'Error analyzing test. ';

            if (err.message.includes('Tesseract')) {
                errorMessage += 'OCR service is not properly configured. Please ensure Tesseract is installed on the server.';
            } else {
                errorMessage += err.message || 'Please try again!';
            }

            alert(errorMessage);
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData({
            ...formData,
            [name]: name === 'grade' ? parseInt(value) : value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!formData.studentName || !formData.score) {
            alert('Please enter student name and score!');
            return;
        }

        setLoading(true);
        setAnalysis(null);

        try {
            const weakAreas = formData.weakAreas
                ? formData.weakAreas.split(',').map(s => s.trim()).filter(Boolean)
                : [];
            const strongAreas = formData.strongAreas
                ? formData.strongAreas.split(',').map(s => s.trim()).filter(Boolean)
                : [];

            const response = await fetch(`${API_BASE}/ai/analyze/test`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    subject: formData.subject,
                    score: parseInt(formData.score),
                    total: parseInt(formData.total),
                    age_group: formData.ageGroup,
                    student_name: formData.studentName,
                    weak_areas: weakAreas,
                    strong_areas: strongAreas
                })
            });

            if (!response.ok) throw new Error('Failed to analyze test');

            const data = await response.json();
            setAnalysis({ type: 'legacy', ...data });
        } catch (err) {
            alert('Error analyzing test. Please try again!');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const getPerformanceColor = (level) => {
        const colors = {
            'Excellent': '#4caf50',
            'Very Good': '#8bc34a',
            'Good': '#2196f3',
            'Satisfactory': '#ff9800',
            'Needs Improvement': '#f44336',
            'excellent': '#4caf50',
            'very good': '#8bc34a',
            'good': '#2196f3',
            'satisfactory': '#ff9800',
            'needs improvement': '#f44336'
        };
        return colors[level] || '#666';
    };

    const getActivityIcon = (type) => {
        const icons = {
            'hands_on': '🧪',
            'writing': '✏️',
            'fun': '🎮',
            'creative': '🎨',
            'practice': '📝',
            'real_world': '🌍',
            'collaborative': '👥'
        };
        return icons[type] || '📌';
    };

    // ===== STRUCTURED REPORT RENDERER =====
    const renderStructuredReport = () => {
        if (!analysis || analysis.type !== 'structured') return null;

        return (
            <div className="structured-report">
                {/* Header with score and performance */}
                <div className="report-header">
                    <div className="report-student-info">
                        <h3>Report for {analysis.student_name}</h3>
                        <span className="report-meta">
                            {analysis.subject} | Grade {analysis.grade}
                        </span>
                    </div>
                    <div className="report-score-ring">
                        <div
                            className="score-ring"
                            style={{
                                '--score-pct': `${analysis.percentage}%`,
                                '--score-color': getPerformanceColor(analysis.performance_level)
                            }}
                        >
                            <span className="score-number">{analysis.percentage}%</span>
                            <span className="score-label">{analysis.score}/{analysis.total}</span>
                        </div>
                        <div
                            className="performance-badge"
                            style={{ background: getPerformanceColor(analysis.performance_level) }}
                        >
                            {analysis.performance_level}
                        </div>
                    </div>
                </div>

                {/* Question stats */}
                <div className="question-stats">
                    <div className="stat-item correct">
                        <span className="stat-icon">✓</span>
                        <span className="stat-value">{analysis.correct_count}</span>
                        <span className="stat-label">Correct</span>
                    </div>
                    <div className="stat-item incorrect">
                        <span className="stat-icon">✗</span>
                        <span className="stat-value">{analysis.incorrect_count}</span>
                        <span className="stat-label">Incorrect</span>
                    </div>
                    <div className="stat-item total">
                        <span className="stat-icon">Q</span>
                        <span className="stat-value">{analysis.questions_found}</span>
                        <span className="stat-label">Total</span>
                    </div>
                </div>

                {/* Encouragement */}
                {analysis.encouragement && (
                    <div className="encouragement-banner">
                        <span className="encouragement-icon">💪</span>
                        <p>{analysis.encouragement}</p>
                    </div>
                )}

                {/* Teacher insights */}
                {analysis.teacher_insights && (
                    <div className="teacher-insights">
                        <h4>📋 Teacher Corrections Detected</h4>
                        <div className="teacher-stats">
                            {analysis.teacher_insights.ticks_detected > 0 && (
                                <span className="teacher-stat tick">
                                    ✓ {analysis.teacher_insights.ticks_detected} ticks
                                </span>
                            )}
                            {analysis.teacher_insights.crosses_detected > 0 && (
                                <span className="teacher-stat cross">
                                    ✗ {analysis.teacher_insights.crosses_detected} crosses
                                </span>
                            )}
                            {analysis.teacher_insights.marks_detected > 0 && (
                                <span className="teacher-stat marks">
                                    🔢 {analysis.teacher_insights.marks_detected} marks found
                                </span>
                            )}
                        </div>
                        {analysis.teacher_insights.comments.length > 0 && (
                            <div className="teacher-comments">
                                {analysis.teacher_insights.comments.map((c, i) => (
                                    <p key={i} className="teacher-comment">"{c}"</p>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* === A. STRONG ZONES === */}
                <div className="report-section strong-zones-section">
                    <div className="section-header">
                        <span className="section-letter">A</span>
                        <h3>Strong Zones</h3>
                        <span className="section-tagline">Topics where you shine!</span>
                    </div>
                    <div className="zones-grid">
                        {analysis.strong_zones.map((zone, idx) => (
                            <div key={idx} className="zone-card strong">
                                <div className="zone-icon">⭐</div>
                                <h4>{zone.topic}</h4>
                                <p className="zone-evidence">{zone.evidence}</p>
                                <p className="zone-message">{zone.message}</p>
                            </div>
                        ))}
                    </div>
                </div>

                {/* === B. WEAK ZONES === */}
                {analysis.weak_zones.length > 0 && (
                    <div className="report-section weak-zones-section">
                        <div className="section-header">
                            <span className="section-letter">B</span>
                            <h3>Weak Zones</h3>
                            <span className="section-tagline">Areas to work on next</span>
                        </div>
                        <div className="zones-grid">
                            {analysis.weak_zones.map((zone, idx) => (
                                <div key={idx} className="zone-card weak">
                                    <div className="zone-icon">🎯</div>
                                    <h4>{zone.topic}</h4>
                                    <p className="zone-issue">{zone.issue}</p>
                                    <p className="zone-message">{zone.message}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* === C. FOCUS PLAN === */}
                <div className="report-section focus-plan-section">
                    <div className="section-header">
                        <span className="section-letter">C</span>
                        <h3>Focus Plan</h3>
                        <span className="section-tagline">Your path to improvement</span>
                    </div>

                    {analysis.focus_plan.summary && (
                        <p className="focus-summary">{analysis.focus_plan.summary}</p>
                    )}

                    {/* Activities */}
                    {analysis.focus_plan.activities && analysis.focus_plan.activities.length > 0 && (
                        <div className="focus-activities">
                            <h4>📚 Recommended Activities</h4>
                            <div className="activities-list">
                                {analysis.focus_plan.activities.map((act, idx) => (
                                    <div key={idx} className="activity-card">
                                        <div className="activity-header">
                                            <span className="activity-icon">
                                                {getActivityIcon(act.type)}
                                            </span>
                                            <h5>{act.title}</h5>
                                            {act.duration && (
                                                <span className="activity-duration">
                                                    ⏱ {act.duration}
                                                </span>
                                            )}
                                        </div>
                                        <p className="activity-desc">{act.description}</p>
                                        <span className={`activity-type-badge ${act.type}`}>
                                            {act.type.replace('_', ' ')}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Specific Tips */}
                    {analysis.focus_plan.specific_tips && analysis.focus_plan.specific_tips.length > 0 && (
                        <div className="focus-tips">
                            <h4>💡 Study Tips</h4>
                            <ol className="tips-list">
                                {analysis.focus_plan.specific_tips.map((tip, idx) => (
                                    <li key={idx}>{tip}</li>
                                ))}
                            </ol>
                        </div>
                    )}

                    {/* Goals */}
                    <div className="focus-goals">
                        {analysis.focus_plan.daily_goal && (
                            <div className="goal-item daily">
                                <span className="goal-icon">📅</span>
                                <div>
                                    <strong>Daily Goal</strong>
                                    <p>{analysis.focus_plan.daily_goal}</p>
                                </div>
                            </div>
                        )}
                        {analysis.focus_plan.weekly_goal && (
                            <div className="goal-item weekly">
                                <span className="goal-icon">📆</span>
                                <div>
                                    <strong>Weekly Goal</strong>
                                    <p>{analysis.focus_plan.weekly_goal}</p>
                                </div>
                            </div>
                        )}
                    </div>

                    {analysis.focus_plan.encouragement && (
                        <div className="focus-encouragement">
                            <span>🌟</span>
                            <p>{analysis.focus_plan.encouragement}</p>
                        </div>
                    )}
                </div>
            </div>
        );
    };

    // ===== LEGACY REPORT RENDERER (for manual/score-based) =====
    const renderLegacyReport = () => {
        if (!analysis || analysis.type !== 'legacy') return null;

        return (
            <div className="analysis-results">
                <div className="results-header">
                    <h3>📊 Analysis for {analysis.score}/{analysis.total}</h3>
                    <div className="score-badge" style={{ background: getPerformanceColor(analysis.performance_level) }}>
                        {analysis.percentage}% - {analysis.performance_level}
                    </div>
                </div>

                {analysis.motivational_quote && (
                    <div className="motivational-quote">
                        <div className="quote-icon">💡</div>
                        <p className="quote-text">"{analysis.motivational_quote}"</p>
                    </div>
                )}

                {analysis.analysis && (
                    <div className="analysis-content">
                        {analysis.analysis.split('\n').map((line, index) => {
                            if (line.trim().startsWith('**') && line.trim().endsWith('**')) {
                                return <h4 key={index} className="analysis-heading">{line.replace(/\*\*/g, '')}</h4>;
                            } else if (line.trim()) {
                                return <p key={index} className="analysis-text">{line}</p>;
                            }
                            return null;
                        })}
                    </div>
                )}

                {(analysis.strong_areas?.length > 0 || analysis.weak_areas?.length > 0) && (
                    <div className="areas-summary">
                        {analysis.strong_areas?.length > 0 && (
                            <div className="areas-card strong">
                                <h4>✨ Strengths</h4>
                                <ul>
                                    {analysis.strong_areas.map((area, idx) => (
                                        <li key={idx}>{area}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                        {analysis.weak_areas?.length > 0 && (
                            <div className="areas-card weak">
                                <h4>🎯 Focus Areas</h4>
                                <ul>
                                    {analysis.weak_areas.map((area, idx) => (
                                        <li key={idx}>{area}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                )}
            </div>
        );
    };

    return (
        <div className="test-analysis">
            <h2 className="section-title">🎯 AI Test Analysis & Recommendations</h2>
            <p className="section-subtitle">Upload test paper or enter results manually for AI-powered analysis</p>

            {/* Analysis Mode Tabs */}
            <div className="analysis-mode-tabs">
                <button
                    className={`mode-tab ${analysisMode === 'upload' ? 'active' : ''}`}
                    onClick={() => setAnalysisMode('upload')}
                >
                    📄 Upload Test Paper
                </button>
                <button
                    className={`mode-tab ${analysisMode === 'manual' ? 'active' : ''}`}
                    onClick={() => setAnalysisMode('manual')}
                >
                    ⌨️ Enter Manually
                </button>
            </div>

            {analysisMode === 'upload' ? (
                /* Upload Mode */
                <div className="upload-mode">
                    <div className="form-row">
                        <div className="form-group">
                            <label htmlFor="studentName">Student Name *</label>
                            <input
                                type="text"
                                id="studentName"
                                name="studentName"
                                value={formData.studentName}
                                onChange={handleInputChange}
                                placeholder="Enter student name"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="subject">Subject *</label>
                            <select
                                id="subject"
                                name="subject"
                                value={formData.subject}
                                onChange={handleInputChange}
                            >
                                {subjects.map(subject => (
                                    <option key={subject.value} value={subject.value}>
                                        {subject.icon} {subject.value}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div className="form-group">
                            <label htmlFor="grade">Grade Level *</label>
                            <select
                                id="grade"
                                name="grade"
                                value={formData.grade}
                                onChange={handleInputChange}
                            >
                                {grades.map(g => (
                                    <option key={g.value} value={g.value}>
                                        {g.label} (Age {g.age})
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {/* Answer Key Toggle */}
                    <div className="answer-key-section">
                        <button
                            type="button"
                            className={`answer-key-toggle ${showAnswerKey ? 'active' : ''}`}
                            onClick={() => setShowAnswerKey(!showAnswerKey)}
                        >
                            {showAnswerKey ? '▼' : '▶'} 📋 Add Answer Key / Rubric (Optional)
                        </button>

                        {showAnswerKey && (
                            <div className="answer-key-form">
                                <p className="answer-key-hint">
                                    Enter the correct answers for each question. This helps the AI compare student answers against the rubric.
                                </p>
                                <div className="answer-key-table">
                                    <div className="answer-key-header">
                                        <span className="ak-col-num">Q#</span>
                                        <span className="ak-col-answer">Correct Answer</span>
                                        <span className="ak-col-marks">Marks</span>
                                        <span className="ak-col-action"></span>
                                    </div>
                                    {answerKeyRows.map((row, idx) => (
                                        <div key={idx} className="answer-key-row">
                                            <input
                                                type="number"
                                                className="ak-input-num"
                                                value={row.question_number}
                                                onChange={(e) => updateAnswerKeyRow(idx, 'question_number', parseInt(e.target.value) || 1)}
                                                min="1"
                                            />
                                            <input
                                                type="text"
                                                className="ak-input-answer"
                                                value={row.answer}
                                                onChange={(e) => updateAnswerKeyRow(idx, 'answer', e.target.value)}
                                                placeholder="Enter correct answer..."
                                            />
                                            <input
                                                type="number"
                                                className="ak-input-marks"
                                                value={row.marks}
                                                onChange={(e) => updateAnswerKeyRow(idx, 'marks', parseInt(e.target.value) || 1)}
                                                min="1"
                                            />
                                            <button
                                                type="button"
                                                className="ak-remove-btn"
                                                onClick={() => removeAnswerKeyRow(idx)}
                                                disabled={answerKeyRows.length <= 1}
                                            >
                                                ✕
                                            </button>
                                        </div>
                                    ))}
                                </div>
                                <button
                                    type="button"
                                    className="ak-add-btn"
                                    onClick={addAnswerKeyRow}
                                >
                                    + Add Question
                                </button>
                            </div>
                        )}
                    </div>

                    <div
                        className={`test-drop-zone ${isDragging ? 'dragging' : ''} ${uploadedFile ? 'has-file' : ''}`}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                    >
                        {uploadedFile ? (
                            <div className="file-preview-box">
                                <div className="file-icon-large">
                                    {uploadedFile.type.includes('pdf') ? '📄' : '🖼️'}
                                </div>
                                <div className="file-details">
                                    <p className="file-name-large">{uploadedFile.name}</p>
                                    <p className="file-size-large">
                                        {(uploadedFile.size / 1024).toFixed(2)} KB
                                    </p>
                                    <p className="file-type">{uploadedFile.type}</p>
                                </div>
                                <button
                                    type="button"
                                    className="remove-file-large"
                                    onClick={() => setUploadedFile(null)}
                                >
                                    ✕ Remove
                                </button>
                            </div>
                        ) : (
                            <>
                                <div className="upload-icon">📋</div>
                                <h3>Upload Test Paper</h3>
                                <p className="upload-text">Drag & drop test paper here</p>
                                <p className="upload-hint">or</p>
                                <label htmlFor="testFileInput" className="upload-browse-btn">
                                    📁 Browse Files
                                </label>
                                <p className="upload-formats">Supports: JPG, PNG, PDF (max 10MB)</p>
                            </>
                        )}
                        <input
                            type="file"
                            id="testFileInput"
                            onChange={handleFileSelect}
                            accept=".pdf,.jpg,.jpeg,.png"
                            style={{ display: 'none' }}
                        />
                    </div>

                    <button
                        className="analyze-btn"
                        onClick={analyzeUploadedTest}
                        disabled={loading || !uploadedFile}
                    >
                        {loading ? '🤖 AI is reading and analyzing...' : '🎯 Analyze Test Paper with AI'}
                    </button>

                    <div className="info-box">
                        <div className="info-icon">ℹ️</div>
                        <div>
                            <strong>How it works:</strong>
                            <p>Upload a clear photo or scan of the marked test paper. Our AI will read the content, detect teacher corrections (ticks, crosses, marks in red ink), evaluate answers, and provide a structured report with Strong Zones, Weak Zones, and a personalized Focus Plan.</p>
                            <p className="note"><strong>Tip:</strong> Adding an Answer Key helps the AI compare student answers against correct answers for more accurate evaluation.</p>
                        </div>
                    </div>
                </div>
            ) : (
                /* Manual Mode - existing form */
                <form onSubmit={handleSubmit} className="analysis-form">
                    <div className="form-row">
                        <div className="form-group">
                            <label htmlFor="studentName">Student Name *</label>
                            <input
                                type="text"
                                id="studentName"
                                name="studentName"
                                value={formData.studentName}
                                onChange={handleInputChange}
                                placeholder="Enter student name"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="subject">Subject *</label>
                            <select
                                id="subject"
                                name="subject"
                                value={formData.subject}
                                onChange={handleInputChange}
                            >
                                {subjects.map(subject => (
                                    <option key={subject.value} value={subject.value}>
                                        {subject.icon} {subject.value}
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label htmlFor="score">Score Achieved *</label>
                            <input
                                type="number"
                                id="score"
                                name="score"
                                value={formData.score}
                                onChange={handleInputChange}
                                placeholder="e.g., 85"
                                min="0"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="total">Total Marks</label>
                            <input
                                type="number"
                                id="total"
                                name="total"
                                value={formData.total}
                                onChange={handleInputChange}
                                min="1"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="ageGroup">Age Group</label>
                            <select
                                id="ageGroup"
                                name="ageGroup"
                                value={formData.ageGroup}
                                onChange={handleInputChange}
                            >
                                {ageGroups.map(group => (
                                    <option key={group.value} value={group.value}>
                                        {group.label}
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>

                    <div className="form-group">
                        <label htmlFor="strongAreas">Strong Areas (comma-separated, optional)</label>
                        <input
                            type="text"
                            id="strongAreas"
                            name="strongAreas"
                            value={formData.strongAreas}
                            onChange={handleInputChange}
                            placeholder="e.g., Geometry, Algebra, Word Problems"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="weakAreas">Areas Needing Improvement (comma-separated, optional)</label>
                        <input
                            type="text"
                            id="weakAreas"
                            name="weakAreas"
                            value={formData.weakAreas}
                            onChange={handleInputChange}
                            placeholder="e.g., Fractions, Decimals, Time"
                        />
                    </div>

                    <button type="submit" className="analyze-btn" disabled={loading}>
                        {loading ? '🤖 AI is analyzing...' : '🎯 Analyze Test Results'}
                    </button>
                </form>
            )}

            {
                loading && (
                    <div className="loading-state">
                        <div className="loading-spinner"></div>
                        <p>AI is carefully analyzing the test results...</p>
                    </div>
                )
            }

            {/* Render appropriate report type */}
            {analysis && analysis.type === 'structured' && renderStructuredReport()}
            {analysis && analysis.type === 'legacy' && renderLegacyReport()}
        </div >
    );
};

export default TestAnalysis;
