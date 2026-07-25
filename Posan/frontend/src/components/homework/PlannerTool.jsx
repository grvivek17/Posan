import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../../styles/planner.css';

const PlannerTool = ({ initialSubject = '' }) => {
    const [gamification, setGamification] = useState({
        current_streak: 0,
        max_streak: 0,
        total_points: 0
    });
    
    const [plans, setPlans] = useState([]);
    
    const [formData, setFormData] = useState({
        subject: initialSubject,
        topics: '',
        start_date: '',
        end_date: ''
    });
    
    useEffect(() => {
        if (initialSubject) {
            setFormData(prev => ({ ...prev, subject: initialSubject }));
        }
    }, [initialSubject]);
    
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const fetchGamification = async () => {
        try {
            const token = localStorage.getItem('access_token');
            const res = await axios.get('https://posan-backend-po1f.onrender.com/api/v1/planner/gamification', {
                headers: { Authorization: `Bearer ${token}` }
            });
            setGamification(res.data);
        } catch (err) {
            console.error("Error fetching gamification stats", err);
        }
    };

    const fetchPlans = async () => {
        try {
            const token = localStorage.getItem('access_token');
            const res = await axios.get('https://posan-backend-po1f.onrender.com/api/v1/planner/plans', {
                headers: { Authorization: `Bearer ${token}` }
            });
            setPlans(res.data.plans || []);
        } catch (err) {
            console.error("Error fetching study plans", err);
        }
    };

    useEffect(() => {
        fetchGamification();
        fetchPlans();
    }, []);

    const handleInputChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleGenerate = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        
        try {
            const token = localStorage.getItem('access_token');
            const payload = {
                subject: formData.subject,
                topics: formData.topics.split(',').map(t => t.trim()).filter(t => t),
                start_date: formData.start_date,
                end_date: formData.end_date
            };
            
            await axios.post('https://posan-backend-po1f.onrender.com/api/v1/planner/generate', payload, {
                headers: { Authorization: `Bearer ${token}` }
            });
            
            // Refresh data
            setFormData({ subject: '', topics: '', start_date: '', end_date: '' });
            await fetchPlans();
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to generate plan');
        } finally {
            setLoading(false);
        }
    };

    const handleCompleteSession = async (sessionId) => {
        try {
            const token = localStorage.getItem('access_token');
            await axios.post(`https://posan-backend-po1f.onrender.com/api/v1/planner/sessions/${sessionId}/complete`, {}, {
                headers: { Authorization: `Bearer ${token}` }
            });
            
            // Optimistically update or re-fetch
            fetchGamification();
            fetchPlans();
        } catch (err) {
            console.error("Error completing session", err);
        }
    };

    return (
        <div className="planner-container" style={{ padding: '0', maxWidth: '100%' }}>
            <header className="planner-header" style={{ marginBottom: '1.5rem' }}>
                <div className="gamification-stats" style={{ padding: '1rem' }}>
                    <div className="stat-card">
                        <span className="stat-icon">🔥</span>
                        <span className="stat-value">{gamification.current_streak}</span>
                        <span className="stat-label">Current Streak</span>
                    </div>
                    <div className="stat-card">
                        <span className="stat-icon">🏆</span>
                        <span className="stat-value">{gamification.max_streak}</span>
                        <span className="stat-label">Max Streak</span>
                    </div>
                    <div className="stat-card">
                        <span className="stat-icon">⭐</span>
                        <span className="stat-value">{gamification.total_points}</span>
                        <span className="stat-label">Total Points</span>
                    </div>
                </div>
            </header>

            <div className="planner-content" style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1rem' }}>
                <section className="generator-section" style={{ padding: '1.5rem' }}>
                    <h2 style={{ fontSize: '1.25rem' }}>Generate New Plan</h2>
                    {error && <div style={{ color: 'red', marginBottom: '1rem' }}>{error}</div>}
                    <form onSubmit={handleGenerate}>
                        <div className="form-group">
                            <label>Subject</label>
                            <input 
                                type="text" 
                                name="subject" 
                                placeholder="e.g., Biology" 
                                value={formData.subject}
                                onChange={handleInputChange}
                                required 
                            />
                        </div>
                        <div className="form-group">
                            <label>Topics (comma separated)</label>
                            <textarea 
                                name="topics" 
                                placeholder="e.g., Cell Structure, Photosynthesis, Genetics"
                                value={formData.topics}
                                onChange={handleInputChange}
                                required 
                                style={{ minHeight: '80px' }}
                            />
                        </div>
                        <div className="form-group">
                            <label>Start Date</label>
                            <input 
                                type="date" 
                                name="start_date" 
                                value={formData.start_date}
                                onChange={handleInputChange}
                                required 
                            />
                        </div>
                        <div className="form-group">
                            <label>End Date</label>
                            <input 
                                type="date" 
                                name="end_date" 
                                value={formData.end_date}
                                onChange={handleInputChange}
                                required 
                            />
                        </div>
                        <button type="submit" className="btn-generate" disabled={loading}>
                            {loading ? (
                                <><span className="loading-spinner"></span> Generating...</>
                            ) : (
                                "Generate Study Plan"
                            )}
                        </button>
                    </form>
                </section>

                <section className="plans-section" style={{ padding: '1.5rem', maxHeight: '60vh', overflowY: 'auto' }}>
                    <h2 style={{ fontSize: '1.25rem' }}>Your Study Plans</h2>
                    {plans.length === 0 ? (
                        <div className="no-plans">No study plans yet. Generate one to get started!</div>
                    ) : (
                        plans.map(plan => (
                            <div key={plan.id} className="plan-card" style={{ marginBottom: '1rem' }}>
                                <div className="plan-header">
                                    <h3 style={{ fontSize: '1.1rem' }}>{plan.title}</h3>
                                    <span className="plan-meta">{plan.completed_sessions} / {plan.total_sessions} completed</span>
                                </div>
                                <div className="sessions-list">
                                    {plan.sessions.map(session => (
                                        <div key={session.id} className={`session-item ${session.is_completed ? 'completed' : ''}`} style={{ padding: '0.75rem' }}>
                                            <div className="session-info">
                                                <div className="session-date">{new Date(session.date).toLocaleDateString()}</div>
                                                <h4 className="session-topic" style={{ fontSize: '0.95rem' }}>{session.topic}</h4>
                                                <div className="session-duration">⏱️ {session.duration_minutes} mins</div>
                                            </div>
                                            <div className="session-action">
                                                {session.is_completed ? (
                                                    <span className="completed-badge" style={{ fontSize: '0.85rem' }}>✓ +{session.points_earned} pts</span>
                                                ) : (
                                                    <button 
                                                        className="btn-complete" 
                                                        style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}
                                                        onClick={() => handleCompleteSession(session.id)}
                                                    >
                                                        Mark Complete
                                                    </button>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))
                    )}
                </section>
            </div>
        </div>
    );
};

export default PlannerTool;
