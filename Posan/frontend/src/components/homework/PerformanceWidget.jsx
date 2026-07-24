import React from 'react';

const PerformanceWidget = ({ performanceData }) => {
    if (!performanceData || !performanceData.summary || performanceData.summary.total_exams === 0) {
        return null;
    }

    return (
        <div className="sidebar-widget performance-widget">
            <div className="widget-header">
                <h3>📈 Performance Analysis</h3>
            </div>
            <div className="widget-content">
                <div className="performance-summary">
                    <div className="perf-stat-row">
                        <span className="perf-label">Overall Trend</span>
                        <span className={`perf-trend ${performanceData.summary.overall_trend}`}>
                            {performanceData.summary.overall_trend === 'improving' ? '📈 Improving' :
                                performanceData.summary.overall_trend === 'declining' ? '📉 Declining' :
                                    performanceData.summary.overall_trend === 'stable' ? '➡️ Stable' : '🆕 Just Started'}
                        </span>
                    </div>
                    <div className="perf-stat-row">
                        <span className="perf-label">Avg Score</span>
                        <span className="perf-value">{performanceData.summary.average_score}%</span>
                    </div>
                    <div className="perf-stat-row">
                        <span className="perf-label">Best / Lowest</span>
                        <span className="perf-value">{performanceData.summary.highest_score}% / {performanceData.summary.lowest_score}%</span>
                    </div>
                    <div className="perf-stat-row">
                        <span className="perf-label">Consistency</span>
                        <div className="progress-bar" style={{ flex: 1, marginLeft: '8px' }}>
                            <div className="progress-fill" style={{ width: `${(performanceData.summary.consistency || 0) * 100}%` }}></div>
                        </div>
                    </div>
                </div>

                {/* Subject breakdown */}
                {Object.keys(performanceData.by_subject || {}).length > 0 && (
                    <div className="subject-breakdown">
                        <h4 className="subject-breakdown-title">By Subject</h4>
                        {Object.entries(performanceData.by_subject).map(([subj, data]) => (
                            <div key={subj} className="perf-stat-row subject-row">
                                <span className="perf-label">{subj}</span>
                                <span className="perf-value subject-value">
                                    {data.average}%
                                    <span className={`trend-icon ${data.trend}`}>
                                        {data.trend === 'improving' ? '↑' : data.trend === 'declining' ? '↓' : '→'}
                                    </span>
                                </span>
                            </div>
                        ))}
                    </div>
                )}

                {/* Knowledge gaps */}
                {performanceData.knowledge_gaps?.critical?.length > 0 && (
                    <div className="knowledge-gaps">
                        <strong className="gaps-title">Focus Areas:</strong>
                        <span className="gaps-list">
                            {performanceData.knowledge_gaps.critical.join(', ')}
                        </span>
                    </div>
                )}

                {/* Recommendations */}
                {performanceData.recommendations?.length > 0 && (
                    <div className="recommendations-section">
                        <h4 className="recommendations-title">Tips</h4>
                        {performanceData.recommendations.slice(0, 3).map((rec, i) => (
                            <p key={i} className="recommendation-text">
                                💡 {rec}
                            </p>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default PerformanceWidget;
