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
    const [ageGroup, setAgeGroup] = useState('9-11');

    const handleFileSelect = (e) => {
        if (e.target.files.length > 0) {
            setUploadedFile(e.target.files[0]);
        }
    };

    const handleFileUpload = async () => {
        if (!uploadedFile) return;

        setLoading(true);
        const formData = new FormData();
        formData.append('file', uploadedFile);

        try {
            const response = await homeworkAPI.uploadStudyMaterial(formData, ageGroup);
            setStudyData(response.data);
            setStep('results');
        } catch (error) {
            console.error('Error uploading study material:', error);

            let errorMsg = 'Unknown error occurred';

            if (error.response) {
                // The request was made and the server responded with a status code
                // that falls out of the range of 2xx
                const data = error.response.data;
                errorMsg = (typeof data === 'string') ? data : (data.detail || data.message || JSON.stringify(data));
                console.log('Server Error Data:', data);
            } else if (error.request) {
                // The request was made but no response was received
                errorMsg = 'No response from server. The PDF might be too large or the connection timed out.';
                console.log('No Response Error:', error.request);
            } else {
                // Something happened in setting up the request that triggered an Error
                errorMsg = error.message;
            }

            alert(`Failed to process study material:\n\n${errorMsg}\n\nPlease try again.`);
        } finally {
            setLoading(false);
        }
    };

    const generatePractice = async () => {
        setLoading(true);
        try {
            const response = await homeworkAPI.generatePracticeQuestions({
                text: studyData.summary,
                num_mcq: 3,
                num_short: 2,
                age_group: ageGroup
            });
            setPracticeData(response.data);
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
            const evaluations = [];

            // Eval MCQs
            practiceData.mcqs.forEach((q, idx) => {
                const selected = answers[`mcq_${idx}`];
                const isCorrect = selected === q.correct;
                evaluations.push({
                    question: q.question,
                    student_answer: selected || 'No answer',
                    expected_answer: q.correct,
                    score: isCorrect ? 100 : 0,
                    is_correct: isCorrect ? 'yes' : 'no',
                    feedback: isCorrect ? 'Correct! Well done.' : `Oops! The correct answer was ${q.correct}.`
                });
            });

            // Eval Short Answers with AI
            for (let i = 0; i < practiceData.short_answers.length; i++) {
                const q = practiceData.short_answers[i];
                const studentAns = answers[`short_${i}`] || '';

                const response = await homeworkAPI.evaluateAnswer({
                    question: q.question,
                    student_answer: studentAns,
                    expected_answer: q.expected_answer
                });
                evaluations.push(response.data);
            }

            // Get performance analysis
            const perfResponse = await homeworkAPI.analyzePerformance(evaluations);
            setEvaluationData(perfResponse.data);
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
                        <label>Your Age Group:</label>
                        <select value={ageGroup} onChange={(e) => setAgeGroup(e.target.value)}>
                            <option value="6-8">6-8 years</option>
                            <option value="9-11">9-11 years</option>
                            <option value="12-14">12-14 years</option>
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
