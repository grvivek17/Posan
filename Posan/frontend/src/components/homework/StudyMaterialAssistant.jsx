import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { homeworkAPI } from '../../services/api';
import './StudyMaterialAssistant.css';

const StudyMaterialAssistant = ({ initialSubject = 'Mathematics' }) => {
    const [step, setStep] = useState('upload'); // upload, results, practice, evaluation
    const [loading, setLoading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [uploadedFile, setUploadedFile] = useState(null);
    const [isDragging, setIsDragging] = useState(false);
    const [studyData, setStudyData] = useState(null);
    const [practiceData, setPracticeData] = useState(null);
    const [answers, setAnswers] = useState({});
    const [evaluationData, setEvaluationData] = useState(null);
    const [showHints, setShowHints] = useState({});

    // NEW: Multi-agent system fields
    const [subject, setSubject] = useState(initialSubject);
    const [grade, setGrade] = useState(5);
    const [materialId, setMaterialId] = useState(null);
    const [indexName, setIndexName] = useState(null);

    useEffect(() => {
        if (initialSubject) {
            setSubject(initialSubject);
        }
    }, [initialSubject]);

    // Bulk upload state
    const [uploadMode, setUploadMode] = useState('single'); // 'single' or 'bulk'
    const [bulkFiles, setBulkFiles] = useState([]);
    const [bulkResults, setBulkResults] = useState(null);
    const [processingFile, setProcessingFile] = useState('');
    const bulkInputRef = useRef(null);

    const handleFileSelect = (e) => {
        if (e.target.files.length > 0) {
            setUploadedFile(e.target.files[0]);
        }
    };

    // Bulk file handlers
    const handleBulkFileSelect = (e) => {
        const newFiles = Array.from(e.target.files);
        const validFiles = newFiles.filter(f => {
            const ext = f.name.toLowerCase().split('.').pop();
            return ['pdf', 'jpg', 'jpeg', 'png'].includes(ext);
        });
        setBulkFiles(prev => {
            const combined = [...prev, ...validFiles];
            return combined.slice(0, 10); // max 10 files
        });
        if (bulkInputRef.current) bulkInputRef.current.value = '';
    };

    const removeBulkFile = (index) => {
        setBulkFiles(prev => prev.filter((_, i) => i !== index));
    };

    const clearBulkFiles = () => {
        setBulkFiles([]);
        setBulkResults(null);
    };

    const getFileIcon = (filename) => {
        const ext = filename.toLowerCase().split('.').pop();
        if (ext === 'pdf') return '\uD83D\uDCC4';
        if (['jpg', 'jpeg', 'png'].includes(ext)) return '\uD83D\uDDBC\uFE0F';
        return '\uD83D\uDCC1';
    };

    const formatFileSize = (bytes) => {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    };

    // Bulk upload handler
    const handleBulkUpload = async () => {
        if (bulkFiles.length === 0) return;

        setLoading(true);
        setUploadProgress(0);
        setProcessingFile('Preparing files...');

        const formData = new FormData();
        bulkFiles.forEach(file => {
            formData.append('files', file);
        });

        try {
            const response = await homeworkAPI.bulkUploadAndGeneratePractice(
                formData,
                subject,
                grade,
                5, // 5 questions per file
                (progressEvent) => {
                    const pct = Math.round((progressEvent.loaded * 100) / (progressEvent.total || progressEvent.loaded));
                    setUploadProgress(pct);
                    if (pct < 100) {
                        setProcessingFile(`Uploading files... ${pct}%`);
                    } else {
                        setProcessingFile('AI is analyzing your materials...');
                    }
                }
            );

            const data = response.data;

            setBulkResults(data);

            // Format study data from combined results
            setStudyData({
                summary: `Processed ${data.files_processed} file(s) with ${data.total_chunks} sections total.${data.files_failed > 0 ? ` ${data.files_failed} file(s) failed.` : ''}`,
                key_topics: data.topics || [],
                chunks_created: data.total_chunks,
                file_results: data.file_results || []
            });

            // Format combined questions for practice
            const questions = data.questions || [];
            const mcqs = questions.filter(q => q.type === 'mcq');
            const shortAnswers = questions.filter(q => q.type === 'short_answer');

            setPracticeData({
                mcqs: mcqs.map(q => {
                    const optionsArray = q.options
                        ? Object.entries(q.options).map(([key, value]) => `${key}) ${value}`)
                        : [];
                    return {
                        question: q.question,
                        options: optionsArray,
                        correct: q.correct_answer,
                        hint: q.hint,
                        id: q.id
                    };
                }),
                short_answers: shortAnswers.map(q => ({
                    question: q.question,
                    expected_answer: q.expected_answer,
                    hint: q.hint,
                    id: q.id
                })),
                raw_questions: questions
            });

            if (questions.length > 0) {
                setStep('practice');
            } else {
                setStep('results');
            }
        } catch (error) {
            console.error('Error in bulk upload workflow:', error);
            let errorMsg = 'Unknown error occurred';
            if (error.response) {
                const data = error.response.data;
                if (typeof data === 'string') errorMsg = data;
                else if (data.detail) {
                    errorMsg = typeof data.detail === 'string' ? data.detail
                        : Array.isArray(data.detail) ? data.detail.map(err => `${err.loc?.join(' > ') || 'Field'}: ${err.msg}`).join('\n')
                        : JSON.stringify(data.detail, null, 2);
                } else if (data.message) errorMsg = data.message;
                else if (data.error) errorMsg = data.error;
                else errorMsg = JSON.stringify(data, null, 2);
            } else if (error.request) {
                errorMsg = 'No response from server. Files might be too large or the connection timed out.';
            } else {
                errorMsg = error.message;
            }
            alert(`Bulk upload failed:\n\n${errorMsg}\n\nPlease try again.`);
        } finally {
            setLoading(false);
            setUploadProgress(0);
            setProcessingFile('');
        }
    };

    // NEW: Use integrated multi-agent workflow
    const handleFileUpload = async () => {
        if (!uploadedFile) return;

        setLoading(true);
        setUploadProgress(0);
        const formData = new FormData();
        formData.append('file', uploadedFile);

        try {
            // Use the integrated workflow: Upload -> Process -> Generate Questions
            const response = await homeworkAPI.uploadAndGeneratePractice(
                formData,
                subject,
                grade,
                10, // Generate 10 questions
                (progressEvent) => {
                    const pct = Math.round((progressEvent.loaded * 100) / (progressEvent.total || progressEvent.loaded));
                    setUploadProgress(pct);
                }
            );

            const data = response.data;

            // Store material info
            setMaterialId(data.material_id);
            setIndexName(data.index_name);

            // Format study data for display
            setStudyData({
                summary: `Processed ${data.chunks_created} sections from your study material.`,
                key_topics: data.topics || [],  // Changed from 'topics' to 'key_topics' to match UI
                chunks_created: data.chunks_created,
                filename: data.metadata?.filename
            });

            // Format questions for practice
            const questions = data.questions || [];
            const mcqs = questions.filter(q => q.type === 'mcq');
            const shortAnswers = questions.filter(q => q.type === 'short_answer');

            setPracticeData({
                mcqs: mcqs.map(q => {
                    // Convert options object {A: "...", B: "...", C: "...", D: "..."} to array
                    const optionsArray = q.options
                        ? Object.entries(q.options).map(([key, value]) => `${key}) ${value}`)
                        : [];

                    return {
                        question: q.question,
                        options: optionsArray,
                        correct: q.correct_answer,
                        hint: q.hint,
                        id: q.id
                    };
                }),
                short_answers: shortAnswers.map(q => ({
                    question: q.question,
                    expected_answer: q.expected_answer,
                    hint: q.hint,
                    id: q.id
                })),
                raw_questions: questions // Keep original for grading
            });

            // NEW: Automatically show practice questions if they were generated
            if (questions.length > 0) {
                setStep('practice');  // Skip results, go directly to practice
            } else {
                setStep('results');  // Show results if no questions generated
            }
        } catch (error) {
            console.error('Error in multi-agent workflow:', error);

            let errorMsg = 'Unknown error occurred';

            if (error.response) {
                // Server responded with error
                const data = error.response.data;
                console.log('Server Error Data:', data);

                // Try to extract meaningful error message
                if (typeof data === 'string') {
                    errorMsg = data;
                } else if (data.detail) {
                    // FastAPI validation errors or custom errors
                    if (typeof data.detail === 'string') {
                        errorMsg = data.detail;
                    } else if (Array.isArray(data.detail)) {
                        // Validation errors array
                        errorMsg = data.detail.map(err =>
                            `${err.loc?.join(' → ') || 'Field'}: ${err.msg}`
                        ).join('\n');
                    } else {
                        errorMsg = JSON.stringify(data.detail, null, 2);
                    }
                } else if (data.message) {
                    errorMsg = data.message;
                } else if (data.error) {
                    errorMsg = data.error;
                } else {
                    // Last resort: stringify the whole object
                    errorMsg = JSON.stringify(data, null, 2);
                }
            } else if (error.request) {
                errorMsg = 'No response from server. The PDF might be too large or the connection timed out.';
                console.log('No Response Error:', error.request);
            } else {
                errorMsg = error.message;
            }

            alert(`Failed to process study material:\n\n${errorMsg}\n\nPlease try again.`);
        } finally {
            setLoading(false);
            setUploadProgress(0);
        }
    };

    // Keep practice generation for when user wants more questions
    const generatePractice = async () => {
        setLoading(true);
        try {
            // Generate more questions from the indexed material
            const response = await homeworkAPI.generateQuestionsFromMaterial(
                indexName,
                studyData.topics[0] || 'general',
                subject,
                grade,
                10
            );

            const data = response.data;
            const questions = data.questions || [];
            const mcqs = questions.filter(q => q.type === 'mcq');
            const shortAnswers = questions.filter(q => q.type === 'short_answer');

            setPracticeData({
                mcqs: mcqs.map(q => ({
                    question: q.question,
                    options: q.options || {},
                    correct: q.correct_answer,
                    hint: q.hint,
                    id: q.id
                })),
                short_answers: shortAnswers.map(q => ({
                    question: q.question,
                    expected_answer: q.expected_answer,
                    hint: q.hint,
                    id: q.id
                })),
                raw_questions: questions
            });

            setStep('practice');
        } catch (error) {
            console.error('Error generating questions:', error);
            alert('Failed to generate practice questions.');
        } finally {
            setLoading(false);
        }
    };

    const handleMCQChange = (index, option) => {
        setAnswers({
            ...answers,
            [`mcq_${index}`]: option
        });
    };

    const handleShortAnswerChange = (index, value) => {
        setAnswers({
            ...answers,
            [`short_${index}`]: value
        });
    };

    const toggleHint = (key) => {
        setShowHints(prev => ({ ...prev, [key]: !prev[key] }));
    };

    const submitPractice = async () => {
        setLoading(true);
        try {
            // NEW: Use multi-agent auto-grading
            const questionsForGrading = [];

            // Add MCQ answers
            practiceData.mcqs.forEach((q, idx) => {
                questionsForGrading.push({
                    type: 'mcq',
                    question: q.question,
                    options: q.options,
                    correct_answer: q.correct,
                    student_answer: answers[`mcq_${idx}`] || '',
                    hint: q.hint,
                    id: q.id
                });
            });

            // Add short answer responses
            practiceData.short_answers.forEach((q, idx) => {
                questionsForGrading.push({
                    type: 'short_answer',
                    question: q.question,
                    expected_answer: q.expected_answer,
                    student_answer: answers[`short_${idx}`] || '',
                    hint: q.hint,
                    id: q.id
                });
            });

            // Grade all questions at once with the exam analysis agent
            const response = await homeworkAPI.gradeExam(
                questionsForGrading,
                localStorage.getItem('user_id') || 'guest',
                null // exam_id
            );

            const gradingResult = response.data;

            // Format evaluation data for display
            setEvaluationData({
                evaluations: gradingResult.graded_questions.map(q => ({
                    question: q.question,
                    student_answer: q.student_answer,
                    expected_answer: q.correct_answer || q.expected_answer,
                    score: q.score * 100, // Convert to percentage
                    is_correct: q.is_correct ? 'yes' : 'no',
                    feedback: q.feedback
                })),
                total_score: gradingResult.total_score,
                max_score: gradingResult.max_score,
                percentage: gradingResult.percentage,
                grade: gradingResult.grade,
                overall_feedback: gradingResult.feedback,
                knowledge_gaps: gradingResult.knowledge_gaps || [],
                recommendations: gradingResult.recommendations || [],
                correct_count: gradingResult.metadata?.correct_count || 0,
                question_count: gradingResult.metadata?.question_count || 0
            });

            setStep('evaluation');
        } catch (error) {
            console.error('Error submitting practice:', error);
            alert('Failed to evaluate answers.');
        } finally {
            setLoading(false);
        }
    };

    const resetToUpload = () => {
        setStep('upload');
        setUploadedFile(null);
        setBulkFiles([]);
        setBulkResults(null);
        setStudyData(null);
        setPracticeData(null);
        setAnswers({});
        setEvaluationData(null);
        setShowHints({});
    };

    return (
        <div className="study-assistant">
            <div className="assistant-header">
                <h2>AI Study Assistant</h2>
                <p>Upload material and let AI help you learn!</p>
            </div>

            {step === 'upload' && (
                <div className="upload-section">
                    {/* Upload mode toggle */}
                    <div className="upload-mode-toggle">
                        <button
                            className={`mode-btn ${uploadMode === 'single' ? 'active' : ''}`}
                            onClick={() => setUploadMode('single')}
                        >
                            Single File
                        </button>
                        <button
                            className={`mode-btn ${uploadMode === 'bulk' ? 'active' : ''}`}
                            onClick={() => setUploadMode('bulk')}
                        >
                            Bulk Upload
                        </button>
                    </div>

                    <div className="age-group-simple">
                        <label>Subject:</label>
                        <select value={subject} onChange={(e) => setSubject(e.target.value)}>
                            <option value="Mathematics">Mathematics</option>
                            <option value="Science">Science</option>
                            <option value="English">English</option>
                            <option value="Social Studies">Social Studies</option>
                            <option value="General">General</option>
                        </select>
                    </div>

                    <div className="age-group-simple">
                        <label>Grade Level:</label>
                        <select value={String(grade)} onChange={(e) => setGrade(parseInt(e.target.value))}>
                            <option value="1">Grade 1</option>
                            <option value="2">Grade 2</option>
                            <option value="3">Grade 3</option>
                            <option value="4">Grade 4</option>
                            <option value="5">Grade 5</option>
                            <option value="6">Grade 6</option>
                            <option value="7">Grade 7</option>
                            <option value="8">Grade 8</option>
                        </select>
                    </div>

                    {/* Single file upload */}
                    {uploadMode === 'single' && (
                        <>
                            <div className={`drop-zone ${uploadedFile ? 'has-file' : ''}`}>
                                <div className="upload-icon">{'\uD83D\uDCC4'}</div>
                                <input
                                    type="file"
                                    id="pdf-upload"
                                    accept=".pdf"
                                    onChange={handleFileSelect}
                                    hidden
                                />
                                <label htmlFor="pdf-upload" className="browse-btn">
                                    {uploadedFile ? uploadedFile.name : 'Select Study PDF'}
                                </label>
                                <p className="upload-hint">Upload your school notes or textbook pages</p>
                            </div>

                            <button
                                className="process-btn"
                                onClick={handleFileUpload}
                                disabled={!uploadedFile || loading}
                            >
                                {loading
                                    ? (uploadProgress > 0 && uploadProgress < 100
                                        ? `Uploading... ${uploadProgress}%`
                                        : 'Processing Material...')
                                    : 'Create Study Plan'}
                            </button>
                            {loading && uploadProgress > 0 && (
                                <div className="upload-progress-bar">
                                    <div
                                        className="upload-progress-fill"
                                        style={{ width: `${uploadProgress}%` }}
                                    />
                                </div>
                            )}
                        </>
                    )}

                    {/* Bulk file upload */}
                    {uploadMode === 'bulk' && (
                        <>
                            <div
                                className={`drop-zone bulk-drop-zone ${isDragging ? 'dragging' : ''} ${bulkFiles.length > 0 ? 'has-file' : ''}`}
                                onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                                onDragLeave={() => setIsDragging(false)}
                                onDrop={(e) => {
                                    e.preventDefault();
                                    setIsDragging(false);
                                    const droppedFiles = Array.from(e.dataTransfer.files).filter(f => {
                                        const ext = f.name.toLowerCase().split('.').pop();
                                        return ['pdf', 'jpg', 'jpeg', 'png'].includes(ext);
                                    });
                                    setBulkFiles(prev => [...prev, ...droppedFiles].slice(0, 10));
                                }}
                            >
                                <div className="upload-icon">{'\uD83D\uDCDA'}</div>
                                <input
                                    type="file"
                                    id="bulk-upload"
                                    ref={bulkInputRef}
                                    accept=".pdf,.jpg,.jpeg,.png"
                                    multiple
                                    onChange={handleBulkFileSelect}
                                    hidden
                                />
                                <label htmlFor="bulk-upload" className="browse-btn">
                                    Select Multiple Files
                                </label>
                                <p className="upload-hint">
                                    Upload up to 10 PDFs or images at once. Drag & drop supported.
                                </p>
                            </div>

                            {/* File list */}
                            {bulkFiles.length > 0 && (
                                <div className="bulk-file-list">
                                    <div className="bulk-file-header">
                                        <span className="bulk-file-count">
                                            {bulkFiles.length} file{bulkFiles.length !== 1 ? 's' : ''} selected
                                        </span>
                                        <button className="bulk-clear-btn" onClick={clearBulkFiles}>
                                            Clear All
                                        </button>
                                    </div>
                                    {bulkFiles.map((file, idx) => (
                                        <div key={idx} className="bulk-file-item">
                                            <span className="bulk-file-icon">{getFileIcon(file.name)}</span>
                                            <div className="bulk-file-info">
                                                <span className="bulk-file-name">{file.name}</span>
                                                <span className="bulk-file-size">{formatFileSize(file.size)}</span>
                                            </div>
                                            <button
                                                className="bulk-remove-btn"
                                                onClick={() => removeBulkFile(idx)}
                                                title="Remove file"
                                            >
                                                x
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            )}

                            <button
                                className="process-btn"
                                onClick={handleBulkUpload}
                                disabled={bulkFiles.length === 0 || loading}
                            >
                                {loading
                                    ? processingFile || 'Processing...'
                                    : `Analyze ${bulkFiles.length} File${bulkFiles.length !== 1 ? 's' : ''} & Create Study Plan`}
                            </button>

                            {loading && uploadProgress > 0 && (
                                <div className="upload-progress-bar">
                                    <div
                                        className="upload-progress-fill"
                                        style={{ width: `${uploadProgress}%` }}
                                    />
                                </div>
                            )}
                        </>
                    )}
                </div>
            )}

            {step === 'results' && studyData && (
                <div className="results-section animate-fade">
                    <div className="summary-card">
                        <h3>Smart Summary</h3>
                        <div className="summary-content">
                            {studyData.summary.split('\n').map((para, i) => (
                                para.trim() && <p key={i}>{para}</p>
                            ))}
                        </div>
                    </div>

                    {/* Per-file breakdown for bulk uploads */}
                    {studyData.file_results && studyData.file_results.length > 1 && (
                        <div className="bulk-results-breakdown">
                            <h3>File Breakdown</h3>
                            {studyData.file_results.map((fr, idx) => (
                                <div key={idx} className="bulk-result-item">
                                    <span className="bulk-result-icon">{getFileIcon(fr.filename)}</span>
                                    <div className="bulk-result-info">
                                        <span className="bulk-result-name">{fr.filename}</span>
                                        <span className="bulk-result-meta">
                                            {fr.chunks_created} sections | {fr.questions_generated} questions | {fr.topics.length} topics
                                        </span>
                                    </div>
                                    <span className={`bulk-result-status ${fr.status}`}>
                                        {fr.status === 'success' ? 'Done' : 'Failed'}
                                    </span>
                                </div>
                            ))}
                        </div>
                    )}

                    {bulkResults?.failed_files?.length > 0 && (
                        <div className="bulk-failed-notice">
                            <h4>Failed Files</h4>
                            {bulkResults.failed_files.map((ff, idx) => (
                                <p key={idx}><strong>{ff.filename}:</strong> {ff.error}</p>
                            ))}
                        </div>
                    )}

                    <div className="topics-list">
                        <h3>Key Topics to Master</h3>
                        <div className="topic-chips">
                            {studyData.key_topics.map((topic, i) => (
                                <span key={i} className="topic-chip">{topic}</span>
                            ))}
                        </div>
                    </div>

                    <div className="action-footer">
                        <button className="back-btn" onClick={resetToUpload}>Upload New</button>
                        <button className="practice-btn" onClick={generatePractice}>
                            {loading ? 'Creating Quiz...' : 'Ready to Practice?'}
                        </button>
                    </div>
                </div>
            )}

            {step === 'practice' && practiceData && (
                <div className="practice-section animate-slide">
                    <h3>Practice Time</h3>

                    {/* Show bulk summary banner if applicable */}
                    {bulkResults && (
                        <div className="bulk-practice-banner">
                            Questions from {bulkResults.files_processed} file{bulkResults.files_processed !== 1 ? 's' : ''} |{' '}
                            {practiceData.mcqs.length} MCQs + {practiceData.short_answers.length} short answers
                        </div>
                    )}

                    <div className="questions-list">
                        {practiceData.mcqs.map((q, i) => (
                            <div key={i} className="question-item mcq">
                                <p className="q-text">{i + 1}. {q.question}</p>
                                <div className="options-grid">
                                    {q.options.map((opt, oi) => (
                                        <button
                                            key={oi}
                                            className={`option-btn ${answers[`mcq_${i}`] === opt[0] ? 'selected' : ''}`}
                                            onClick={() => handleMCQChange(i, opt[0])}
                                        >
                                            {opt}
                                        </button>
                                    ))}
                                </div>
                                {q.hint && (
                                    <div className="hint-section">
                                        <button className="hint-btn" onClick={() => toggleHint(`mcq_${i}`)}>
                                            {showHints[`mcq_${i}`] ? 'Hide Hint' : 'Show Hint'}
                                        </button>
                                        {showHints[`mcq_${i}`] && (
                                            <p className="hint-text">{q.hint}</p>
                                        )}
                                    </div>
                                )}
                            </div>
                        ))}

                        {practiceData.short_answers.map((q, i) => (
                            <div key={i} className="question-item short">
                                <p className="q-text">{practiceData.mcqs.length + i + 1}. {q.question}</p>
                                {q.hint && (
                                    <div className="hint-section">
                                        <button className="hint-btn" onClick={() => toggleHint(`short_${i}`)}>
                                            {showHints[`short_${i}`] ? 'Hide Hint' : 'Show Hint'}
                                        </button>
                                        {showHints[`short_${i}`] && (
                                            <p className="hint-text">{q.hint}</p>
                                        )}
                                    </div>
                                )}
                                <textarea
                                    className="short-ans-input"
                                    placeholder="Type your answer here..."
                                    value={answers[`short_${i}`] || ''}
                                    onChange={(e) => handleShortAnswerChange(i, e.target.value)}
                                />
                            </div>
                        ))}
                    </div>

                    <button
                        className="submit-btn"
                        onClick={submitPractice}
                        disabled={loading}
                    >
                        {loading ? 'AI Evaluation...' : 'Submit Answers'}
                    </button>
                </div>
            )}

            {step === 'evaluation' && evaluationData && (
                <div className="eval-section animate-fade">
                    <div className="perf-header">
                        <div className="score-circle">
                            <span className="score-num">{Math.round(evaluationData.percentage)}%</span>
                            <span className="score-label">Score: {evaluationData.total_score}/{evaluationData.max_score}</span>
                        </div>
                        <div className="perf-msg">
                            <h3>Grade: {evaluationData.grade}</h3>
                            <p>You completed {evaluationData.question_count} questions ({evaluationData.correct_count} correct)!</p>
                        </div>
                    </div>

                    {evaluationData.overall_feedback && (
                        <div className="reco-box" style={{ marginBottom: '16px', background: '#F0F4FF', borderLeft: '4px solid #667eea' }}>
                            <h4>Overall Feedback</h4>
                            <div className="reco-content">
                                <p>{evaluationData.overall_feedback}</p>
                            </div>
                        </div>
                    )}

                    {evaluationData.knowledge_gaps && evaluationData.knowledge_gaps.length > 0 && (
                        <div className="reco-box" style={{ marginBottom: '16px', background: '#FFF3E0', borderLeft: '4px solid #ff9800' }}>
                            <h4>Knowledge Gaps to Focus On</h4>
                            <div className="reco-content">
                                {evaluationData.knowledge_gaps.map((gap, i) => (
                                    <p key={i}><strong>{gap.topic}:</strong> {gap.percentage}% correct ({gap.questions_correct}/{gap.questions_attempted} questions)</p>
                                ))}
                            </div>
                        </div>
                    )}

                    <div className="reco-box">
                        <h4>Personalized Recommendations</h4>
                        <div className="reco-content">
                            {Array.isArray(evaluationData.recommendations)
                                ? evaluationData.recommendations.map((line, i) => (
                                    typeof line === 'string' && line.trim() && <p key={i}>{line}</p>
                                ))
                                : typeof evaluationData.recommendations === 'string'
                                    ? evaluationData.recommendations.split('\n').map((line, i) => (
                                        line.trim() && <p key={i}>{line}</p>
                                    ))
                                    : <p>Keep practicing to improve your skills!</p>
                            }
                        </div>
                    </div>

                    <div className="ans-review">
                        <h4>Answer Review</h4>
                        <div className="review-list">
                            {evaluationData.evaluations.map((res, i) => (
                                <div key={i} className={`review-item ${res.is_correct === 'yes' ? 'correct' : 'incorrect'}`}>
                                    <p className="rev-q"><strong>Q:</strong> {res.question}</p>
                                    <p className="rev-ans"><strong>Your Answer:</strong> {res.student_answer}</p>
                                    {res.expected_answer && (
                                        <p className="rev-expected"><strong>Expected:</strong> {res.expected_answer}</p>
                                    )}
                                    <div className="feedback-small">{res.feedback}</div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <button className="back-btn" onClick={resetToUpload}>Start New Session</button>
                </div>
            )}
        </div>
    );
};

export default StudyMaterialAssistant;
