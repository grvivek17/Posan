import React, { useState } from 'react';
import { homeworkAPI } from '../../services/api';

const AssignmentTracker = ({ userId, assignments, onAssignmentsUpdated }) => {
    const [showAddAssignment, setShowAddAssignment] = useState(false);
    const [newAssignment, setNewAssignment] = useState({ title: '', subject: '', dueDate: '' });
    const [assignmentFile, setAssignmentFile] = useState(null);

    const handleCreateAssignment = async () => {
        if (!newAssignment.title) return;
        try {
            const formData = new FormData();
            formData.append('title', newAssignment.title);
            formData.append('user_id', userId);
            if (newAssignment.subject) formData.append('subject', newAssignment.subject);
            if (newAssignment.dueDate) formData.append('due_date', newAssignment.dueDate);
            if (assignmentFile) formData.append('file', assignmentFile);

            await homeworkAPI.createAssignment(formData);
            setNewAssignment({ title: '', subject: '', dueDate: '' });
            setAssignmentFile(null);
            setShowAddAssignment(false);
            onAssignmentsUpdated();
        } catch (err) {
            console.error('Failed to create assignment:', err);
            alert('Failed to create assignment');
        }
    };

    const handleToggleAssignmentStatus = async (id, currentStatus) => {
        const nextStatus = currentStatus === 'completed' ? 'pending' : 'completed';
        try {
            await homeworkAPI.updateAssignmentStatus(id, nextStatus);
            onAssignmentsUpdated();
        } catch (err) {
            console.error('Failed to update assignment:', err);
        }
    };

    const handleDeleteAssignment = async (id) => {
        try {
            await homeworkAPI.deleteAssignment(id);
            onAssignmentsUpdated();
        } catch (err) {
            console.error('Failed to delete assignment:', err);
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

    return (
        <div className="sidebar-widget assignment-tracker-widget">
            <div className="widget-header">
                <h3>📋 Assignment Tracker</h3>
                <button
                    className="add-assignment-btn"
                    onClick={() => setShowAddAssignment(!showAddAssignment)}
                >
                    {showAddAssignment ? '✕' : '+'}
                </button>
            </div>
            <div className="widget-content">
                {showAddAssignment && (
                    <div className="add-assignment-form">
                        <input
                            type="text"
                            placeholder="Assignment title..."
                            value={newAssignment.title}
                            onChange={(e) => setNewAssignment({ ...newAssignment, title: e.target.value })}
                            className="assignment-input"
                        />
                        <select
                            value={newAssignment.subject}
                            onChange={(e) => setNewAssignment({ ...newAssignment, subject: e.target.value })}
                            className="assignment-input"
                        >
                            <option value="">Select Subject</option>
                            <option value="Mathematics">Mathematics</option>
                            <option value="Science">Science</option>
                            <option value="English">English</option>
                            <option value="History">History</option>
                        </select>
                        <input
                            type="date"
                            value={newAssignment.dueDate}
                            onChange={(e) => setNewAssignment({ ...newAssignment, dueDate: e.target.value })}
                            className="assignment-input"
                        />
                        <input
                            type="file"
                            accept=".pdf,.doc,.docx,.jpg,.png"
                            onChange={(e) => setAssignmentFile(e.target.files[0] || null)}
                            className="assignment-file-input"
                        />
                        <button
                            onClick={handleCreateAssignment}
                            disabled={!newAssignment.title}
                            className="btn-create-assignment"
                        >
                            Add Assignment
                        </button>
                    </div>
                )}
                <div className="assignments-list">
                    <h4 className="assignments-title">
                        {assignments.length > 0 ? `Assignments (${assignments.length})` : 'No assignments yet'}
                    </h4>
                    {assignments.map((a) => (
                        <div key={a.id} className="assignment-item">
                            <div
                                className={`assignment-icon ${a.subject?.toLowerCase() || ''}`}
                                onClick={() => handleToggleAssignmentStatus(a.id, a.status)}
                                style={{ cursor: 'pointer' }}
                            >
                                {a.status === 'completed' ? '✅' : getSubjectIcon(a.subject)}
                            </div>
                            <div className="assignment-details">
                                <p className="assignment-name" style={{ textDecoration: a.status === 'completed' ? 'line-through' : 'none' }}>
                                    {a.title}
                                </p>
                                <p className="assignment-due">{formatDueDate(a.due_date)}</p>
                            </div>
                            <span
                                className={`assignment-status ${a.status}`}
                                onClick={() => handleDeleteAssignment(a.id)}
                                style={{ cursor: 'pointer' }}
                                title="Delete"
                            >
                                {a.status === 'completed' ? '🗑️' : '⏳'}
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default AssignmentTracker;
