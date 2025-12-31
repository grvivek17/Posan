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
            // Create form data for file upload
            const uploadFormData = new FormData();
            uploadFormData.append('file', uploadedFile);

            // Send to OCR + AI analysis endpoint
            const response = await fetch(
                `${API_BASE}/ai/analyze/test-upload?student_name=${encodeURIComponent(formData.studentName)}&subject=${encodeURIComponent(formData.subject)}&age_group=${encodeURIComponent(formData.ageGroup)}`,
                {
                    method: 'POST',
                    body: uploadFormData
                }
            );

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to analyze test paper');
            }

            const data = await response.json();

            // Check if score was detected
            if (!data.score_detected) {
                alert(`⚠️ OCR completed but could not detect score automatically.\n\n${data.message}\n\nExtracted ${data.questions_found} questions.\n\nPlease use manual entry mode to input the score.`);
                setLoading(false);
                return;
            }

            // Score was detected and AI analysis is complete
            setAnalysis({
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

            alert(`✅ Test paper analyzed successfully!\n\nOCR Confidence: ${data.ocr_confidence}\nQuestions Found: ${data.questions_found}\nScore Detected: ${data.score}/${data.total}`);
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
