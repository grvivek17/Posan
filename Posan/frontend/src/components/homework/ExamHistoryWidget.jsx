import React from 'react';

const ExamHistoryWidget = ({ examHistory }) => {
    if (!examHistory || examHistory.length === 0) {
        return null;
    }

    return (
        <div className="sidebar-widget exam-history-widget">
            <div className="widget-header">
                <h3>📝 Recent Exams</h3>
            </div>
            <div className="widget-content">
                {examHistory.slice(0, 5).map((exam) => (
                    <div key={exam.id} className="exam-history-item">
                        <div className={`exam-badge ${
                            exam.percentage >= 80 ? 'excellent' : 
                            exam.percentage >= 60 ? 'good' : 'needs-improvement'
                        }`}>
                            {exam.letter_grade || '-'}
                        </div>
                        <div className="exam-info">
                            <p className="exam-subject">
                                {exam.subject || 'Practice'}
                            </p>
                            <p className="exam-date">
                                {exam.created_at ? new Date(exam.created_at).toLocaleDateString() : ''}
                            </p>
                        </div>
                        <div className="exam-score">
                            {exam.percentage ? `${Math.round(exam.percentage)}%` : '-'}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ExamHistoryWidget;
