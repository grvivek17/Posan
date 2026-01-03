import { useState } from 'react';
import { homeworkAPI } from '../../services/api';
import './StudyMaterialAssistant.css';

const StudyMaterialAssistant = () => {
    const [step, setStep] = useState('upload'); // upload, results, practice, evaluation
    const [loading, setLoading] = useState(false);
    const [uploadedFile, setUploadedFile] = useState(null);
    const [isDragging, setIsDragging] = useState(false);
    const [studyData, setStudyData] = useState(null);
    const [practiceData, setPracticeData] = useState(null);
    const [answers, setAnswers] = useState({});
    const [evaluationData, setEvaluationData] = useState(null);

    // NEW: Multi-agent system fields
    const [subject, setSubject] = useState('Mathematics');
    const [grade, setGrade] = useState(5);
    const [materialId, setMaterialId] = useState(null);
    const [indexName, setIndexName] = useState(null);

    const handleFileSelect = (e) => {
        if (e.target.files.length > 0) {
            setUploadedFile(e.target.files[0]);
        }
    };

    // NEW: Use integrated multi-agent workflow
    const handleFileUpload = async () => {
        if (!uploadedFile) return;

        setLoading(true);
        const formData = new FormData();
        formData.append('file', uploadedFile);

        try {
            // Use the integrated workflow: Upload → Process → Generate Questions
            const response = await homeworkAPI.uploadAndGeneratePractice(
                formData,
                subject,
                grade,
                10 // Generate 10 questions
            );

            const data = response.data;

            // Store material info
            setMaterialId(data.material_id);
            setIndexName(data.index_name);

            // Format study data for display
            setStudyData({
                summary: `Processed ${data.chunks_created} sections from your study material.`,
                topics: data.topics || [],
                chunks_created: data.chunks_created,
                filename: data.metadata?.filename
            });

            // Format questions for practice
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
                raw_questions: questions // Keep original for grading
            });

            setStep('results');
        } catch (error) {
            console.error('Error in multi-agent workflow:', error);

            let errorMsg = 'Unknown error occurred';

            if (error.response) {
                const data = error.response.data;
                errorMsg = (typeof data === 'string') ? data : (data.detail || data.message || JSON.stringify(data));
                console.log('Server Error Data:', data);
            } else if (error.request) {
                errorMsg = 'No response from server. The PDF might be too large or the connection timed out.';
                console.log('No Response Error:', error.request);
            } else {
                errorMsg = error.message;
            }

            alert(`Failed to process study material:\n\n${errorMsg}\n\nPlease try again.`);
        } finally {
            setLoading(false);
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

    return (
        <div className="study-assistant">
            <div className="assistant-header">
                <h2>📚 AI Study Assistant</h2>
                <p>Upload material and let AI help you learn!</p>
            </div>

            {step === 'upload' && (
                <div className="upload-section">
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
                        <select value={grade} onChange={(e) => setGrade(parseInt(e.target.value))}>
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

                    <div className={`drop-zone ${uploadedFile ? 'has-file' : ''}`}>
                        <div className="upload-icon">📄</div>
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
                        {loading ? '🧠 Processing Material...' : '✨ Create Study Plan'}
                    </button>
                </div>
            )}

            {step === 'results' && studyData && (
                <div className="results-section animate-fade">
                    <div className="summary-card">
                        <h3>📖 Smart Summary</h3>
                        <div className="summary-content">
                            {studyData.summary.split('\n').map((para, i) => (
                                para.trim() && <p key={i}>{para}</p>
                            ))}
                        </div>
                    </div>

                    <div className="topics-list">
                        <h3>🎯 Key Topics to Master</h3>
                        <div className="topic-chips">
                            {studyData.key_topics.map((topic, i) => (
                                <span key={i} className="topic-chip">{topic}</span>
                            ))}
                        </div>
                    </div>

                    <div className="action-footer">
                        <button className="back-btn" onClick={() => setStep('upload')}>Upload New</button>
                        <button className="practice-btn" onClick={generatePractice}>
                            {loading ? '📝 Creating Quiz...' : '📝 Ready to Practice?'}
                        </button>
                    </div>
                </div>
            )}

            {step === 'practice' && practiceData && (
                <div className="practice-section animate-slide">
                    <h3>✍️ Practice Time</h3>

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
                            </div>
                        ))}

                        {practiceData.short_answers.map((q, i) => (
                            <div key={i} className="question-item short">
                                <p className="q-text">{practiceData.mcqs.length + i + 1}. {q.question}</p>
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
                        {loading ? '🤖 AI Evaluation...' : '✅ Submit Answers'}
                    </button>
                </div>
            )}

            {step === 'evaluation' && evaluationData && (
                <div className="eval-section animate-fade">
                    <div className="perf-header">
                        <div className="score-circle">
                            <span className="score-num">{evaluationData.average_score}%</span>
                            <span className="score-label">Average Score</span>
                        </div>
                        <div className="perf-msg">
                            <h3>{evaluationData.performance_level}</h3>
                            <p>You completed {evaluationData.total_questions} questions!</p>
                        </div>
                    </div>

                    <div className="reco-box">
                        <h4>🌱 Personalized Recommendations</h4>
                        <div className="reco-content">
                            {evaluationData.recommendations.split('\n').map((line, i) => (
                                line.trim() && <p key={i}>{line}</p>
                            ))}
                        </div>
                    </div>

                    <div className="ans-review">
                        <h4>📝 Answer Review</h4>
                        <div className="review-list">
                            {evaluationData.individual_results.map((res, i) => (
                                <div key={i} className={`review-item ${res.is_correct === 'yes' ? 'correct' : 'incorrect'}`}>
                                    <p className="rev-q"><strong>Q:</strong> {res.question}</p>
                                    <p className="rev-ans"><strong>Your Answer:</strong> {res.student_answer}</p>
                                    <div className="feedback-small">{res.feedback}</div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <button className="back-btn" onClick={() => setStep('upload')}>Start New Session</button>
                </div>
            )}
        </div>
    );
};

export default StudyMaterialAssistant;
