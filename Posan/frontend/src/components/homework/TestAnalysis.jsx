import { useState } from 'react';
import './TestAnalysis.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const TestAnalysis = () => {
    const [loading, setLoading] = useState(false);
    const [analysis, setAnalysis] = useState(null);
    const [uploadedFile, setUploadedFile] = useState(null);
    const [isDragging, setIsDragging] = useState(false);
    const [analysisMode, setAnalysisMode] = useState('upload'); // 'upload' or 'manual'
    const [formData, setFormData] = useState({
        studentName: '',
        subject: 'Mathematics',
        score: '',
        total: '100',
        ageGroup: '6-8',
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
            // In a real implementation, this would:
            // 1. Upload the file to backend
            // 2. Use OCR (Tesseract, EasyOCR, or Hugging Face vision models) to extract text
            // 3. Parse the text to identify questions, answers, marks
            // 4. Send to AI for analysis

            // For now, we'll simulate the analysis with a mock score
            // In production, you'd integrate with OCR libraries

            const mockAnalysis = {
                subject: formData.subject,
                score: 75,
                total: 100,
                percentage: 75,
                performance_level: 'good',
                analysis: `**Performance Summary:**
Great work on this ${formData.subject} test, ${formData.studentName}! You scored 75 out of 100, showing solid understanding of the material.

**Strengths:**
- Clear handwriting and well-organized answers
- Strong understanding of core concepts
- Good attention to detail in calculations

**Areas for Growth:**
- Some questions were left incomplete - work on time management
- Review the sections where partial credit was given
- Practice more word problems to improve problem-solving speed

**Personalized Recommendations:**
1. Create a study schedule: Dedicate 30 minutes daily to review weak topics
2. Use visual aids and diagrams to help understand complex concepts
3. Practice similar problems from your textbook to build confidence

**Next Steps:**
Review the marked test paper carefully, identify patterns in mistakes, and create a list of topics to revise. Schedule a review session with your teacher for questions that were challenging.`,
                motivational_quote: "Every mistake is a step towards learning. Keep growing!",
                weak_areas: ['Time management', 'Complex word problems'],
                strong_areas: ['Basic concepts', 'Calculations', 'Organization']
            };

            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 3000));

            setAnalysis(mockAnalysis);

            alert('✅ Test paper analyzed! Note: This is a demo analysis. Full OCR integration requires additional backend setup.');
        } catch (err) {
            alert('Error analyzing test. Please try again!');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
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
            setAnalysis(data);
        } catch (err) {
            alert('Error analyzing test. Please try again!');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const getPerformanceColor = (level) => {
        const colors = {
            'excellent': '#4caf50',
            'very good': '#8bc34a',
            'good': '#2196f3',
            'satisfactory': '#ff9800',
            'needs improvement': '#f44336'
        };
        return colors[level] || '#666';
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
                            <p>Upload a clear photo or scan of the marked test paper. Our AI will read the content, evaluate answers, and provide personalized recommendations.</p>
                            <p className="note"><strong>Note:</strong> This is a demo version. Full OCR integration with Tesseract or EasyOCR requires additional backend setup.</p>
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

            {
                analysis && (
                    <div className="analysis-results">
                        <div className="results-header">
                            <h3>📊 Analysis for {analysis.score}/{analysis.total}</h3>
                            <div className="score-badge" style={{ background: getPerformanceColor(analysis.performance_level) }}>
                                {analysis.percentage}% - {analysis.performance_level}
                            </div>
                        </div>

                        <div className="motivational-quote">
                            <div className="quote-icon">💡</div>
                            <p className="quote-text">"{analysis.motivational_quote}"</p>
                        </div>

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

                        {(analysis.strong_areas.length > 0 || analysis.weak_areas.length > 0) && (
                            <div className="areas-summary">
                                {analysis.strong_areas.length > 0 && (
                                    <div className="areas-card strong">
                                        <h4>✨ Strengths</h4>
                                        <ul>
                                            {analysis.strong_areas.map((area, idx) => (
                                                <li key={idx}>{area}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                                {analysis.weak_areas.length > 0 && (
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
                )
            }
        </div >
    );
};

export default TestAnalysis;
