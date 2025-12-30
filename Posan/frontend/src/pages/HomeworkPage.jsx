import { useState } from 'react';
import TestAnalysis from '../components/homework/TestAnalysis';
import './HomeworkPage.css';

const HomeworkPage = () => {
    const [activeTab, setActiveTab] = useState('upload'); // 'upload', 'assignments', 'analysis'
    const [assignments, setAssignments] = useState([
        // Sample data - in real app, this would come from backend
        {
            id: 1,
            title: 'Math Worksheet',
            subject: 'Mathematics',
            file: 'math_homework.pdf',
            uploadDate: '2024-12-28',
            status: 'submitted'
        }
    ]);
    const [isDragging, setIsDragging] = useState(false);
    const [uploadForm, setUploadForm] = useState({
        title: '',
        subject: 'Mathematics',
        description: '',
        file: null
    });

    const subjects = [
        { value: 'Mathematics', icon: '🔢', color: '#4caf50' },
        { value: 'Science', icon: '🔬', color: '#2196f3' },
        { value: 'English', icon: '📚', color: '#ff9800' },
        { value: 'History', icon: '🏛️', color: '#9c27b0' },
        { value: 'Art', icon: '🎨', color: '#e91e63' },
        { value: 'Other', icon: '📝', color: '#607d8b' }
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
            setUploadForm({ ...uploadForm, file: files[0] });
        }
    };

    const handleFileSelect = (e) => {
        if (e.target.files.length > 0) {
            setUploadForm({ ...uploadForm, file: e.target.files[0] });
        }
    };

    const handleInputChange = (e) => {
        setUploadForm({
            ...uploadForm,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = (e) => {
        e.preventDefault();

        if (!uploadForm.file || !uploadForm.title) {
            alert('Please provide a title and select a file!');
            return;
        }

        // In real app, this would upload to backend
        const newAssignment = {
            id: assignments.length + 1,
            title: uploadForm.title,
            subject: uploadForm.subject,
            file: uploadForm.file.name,
            uploadDate: new Date().toISOString().split('T')[0],
            status: 'submitted',
            description: uploadForm.description
        };

        setAssignments([newAssignment, ...assignments]);

        // Reset form
        setUploadForm({
            title: '',
            subject: 'Mathematics',
            description: '',
            file: null
        });

        // Reset file input
        document.getElementById('fileInput').value = '';

        alert(`✅ "${uploadForm.title}" uploaded successfully!`);
        setActiveTab('assignments'); // Switch to assignments tab
    };

    const handleDelete = (id) => {
        if (window.confirm('Are you sure you want to delete this assignment?')) {
            setAssignments(assignments.filter(a => a.id !== id));
        }
    };

    const getSubjectInfo = (subject) => {
        return subjects.find(s => s.value === subject) || subjects[subjects.length - 1];
    };

    return (
        <div className="homework-page">
            <div className="homework-header">
                <h1 className="page-title">📚 My Homework</h1>
                <p className="page-subtitle">Manage assignments and get AI-powered test analysis</p>
            </div>

            {/* Homework Tabs */}
            <div className="homework-tabs">
                <button
                    className={`homework-tab ${activeTab === 'upload' ? 'active' : ''}`}
                    onClick={() => setActiveTab('upload')}
                >
                    📤 Upload Assignment
                </button>
                <button
                    className={`homework-tab ${activeTab === 'assignments' ? 'active' : ''}`}
                    onClick={() => setActiveTab('assignments')}
                >
                    📋 My Assignments {assignments.length > 0 && <span className="tab-badge">{assignments.length}</span>}
                </button>
                <button
                    className={`homework-tab ${activeTab === 'analysis' ? 'active' : ''}`}
                    onClick={() => setActiveTab('analysis')}
                >
                    🎯 Test Analysis
                </button>
            </div>

            <div className="homework-content">
                {/* Upload Tab */}
                {activeTab === 'upload' && (
                    <div className="upload-section">
                        <h2 className="section-title">📤 Upload New Assignment</h2>

                        <form onSubmit={handleSubmit} className="upload-form">
                            <div className="form-group">
                                <label htmlFor="title">Assignment Title *</label>
                                <input
                                    type="text"
                                    id="title"
                                    name="title"
                                    value={uploadForm.title}
                                    onChange={handleInputChange}
                                    placeholder="e.g., Math Chapter 5 Exercises"
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="subject">Subject *</label>
                                <select
                                    id="subject"
                                    name="subject"
                                    value={uploadForm.subject}
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
                                <label htmlFor="description">Description (Optional)</label>
                                <textarea
                                    id="description"
                                    name="description"
                                    value={uploadForm.description}
                                    onChange={handleInputChange}
                                    placeholder="Add any notes about this assignment..."
                                    rows="3"
                                ></textarea>
                            </div>

                            <div
                                className={`drop-zone ${isDragging ? 'dragging' : ''} ${uploadForm.file ? 'has-file' : ''}`}
                                onDragOver={handleDragOver}
                                onDragLeave={handleDragLeave}
                                onDrop={handleDrop}
                            >
                                {uploadForm.file ? (
                                    <div className="file-preview">
                                        <div className="file-icon">📄</div>
                                        <div className="file-info">
                                            <p className="file-name">{uploadForm.file.name}</p>
                                            <p className="file-size">
                                                {(uploadForm.file.size / 1024).toFixed(2)} KB
                                            </p>
                                        </div>
                                        <button
                                            type="button"
                                            className="remove-file-btn"
                                            onClick={() => {
                                                setUploadForm({ ...uploadForm, file: null });
                                                document.getElementById('fileInput').value = '';
                                            }}
                                        >
                                            ✕
                                        </button>
                                    </div>
                                ) : (
                                    <>
                                        <div className="drop-icon">📎</div>
                                        <p className="drop-text">Drag & drop your file here</p>
                                        <p className="drop-hint">or</p>
                                        <label htmlFor="fileInput" className="browse-btn">
                                            Browse Files
                                        </label>
                                    </>
                                )}
                                <input
                                    type="file"
                                    id="fileInput"
                                    onChange={handleFileSelect}
                                    accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
                                    style={{ display: 'none' }}
                                />
                            </div>

                            <button type="submit" className="submit-btn">
                                ✓ Upload Assignment
                            </button>
                        </form>
                    </div>
                )}

                {/* Assignments Tab */}
                {activeTab === 'assignments' && (
                    <div className="assignments-section">
                        <h2 className="section-title">📋 My Uploaded Assignments</h2>

                        {assignments.length === 0 ? (
                            <div className="empty-state">
                                <div className="empty-icon">📭</div>
                                <p>No assignments uploaded yet</p>
                                <p className="empty-hint">Upload your first assignment above!</p>
                            </div>
                        ) : (
                            <div className="assignments-grid">
                                {assignments.map(assignment => {
                                    const subjectInfo = getSubjectInfo(assignment.subject);
                                    return (
                                        <div key={assignment.id} className="assignment-card">
                                            <div
                                                className="assignment-header"
                                                style={{ background: `linear-gradient(135deg, ${subjectInfo.color} 0%, ${subjectInfo.color}dd 100%)` }}
                                            >
                                                <div className="subject-badge">
                                                    {subjectInfo.icon} {assignment.subject}
                                                </div>
                                                <div className="status-badge">
                                                    ✓ {assignment.status}
                                                </div>
                                            </div>
                                            <div className="assignment-body">
                                                <h3 className="assignment-title">{assignment.title}</h3>
                                                {assignment.description && (
                                                    <p className="assignment-description">{assignment.description}</p>
                                                )}
                                                <div className="assignment-meta">
                                                    <span className="file-name">📄 {assignment.file}</span>
                                                    <span className="upload-date">📅 {assignment.uploadDate}</span>
                                                </div>
                                            </div>
                                            <div className="assignment-actions">
                                                <button className="action-btn view-btn">
                                                    👁️ View
                                                </button>
                                                <button className="action-btn download-btn">
                                                    ⬇️ Download
                                                </button>
                                                <button
                                                    className="action-btn delete-btn"
                                                    onClick={() => handleDelete(assignment.id)}
                                                >
                                                    🗑️ Delete
                                                </button>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </div>
                )}

                {/* Test Analysis Tab */}
                {activeTab === 'analysis' && (
                    <div className="test-analysis-container">
                        <TestAnalysis />
                    </div>
                )}
            </div>
        </div>
    );
};

export default HomeworkPage;
