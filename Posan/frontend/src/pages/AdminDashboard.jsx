import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAdmin } from '../hooks/useAdmin';
import './AdminDashboard.css';

const AdminDashboard = () => {
    const navigate = useNavigate();
    const { stats, recentActivity, loading, fetchStats, fetchRecentActivity } = useAdmin();

    useEffect(() => {
        fetchStats();
        fetchRecentActivity(20);
    }, []);

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        }).format(amount);
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (minutes < 1) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        return `${days}d ago`;
    };

    if (loading && !stats) {
        return (
            <div className="admin-dashboard">
                <div className="loading-spinner">
                    <div className="spinner"></div>
                    <p>Loading dashboard...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="admin-dashboard">
            <div className="admin-header">
                <div>
                    <h1>📊 Admin Dashboard</h1>
                    <p className="admin-subtitle">Monitor users, subscriptions, and activity</p>
                </div>
                <div className="admin-actions">
                    <button onClick={() => navigate('/admin/users')} className="btn-primary">
                        👤 Manage Users
                    </button>
                    <button onClick={() => navigate('/admin/subscriptions')} className="btn-secondary">
                        💳 Subscriptions
                    </button>
                    <button onClick={() => navigate('/admin/products')} className="btn-secondary">
                        📦 Manage Products
                    </button>
                </div>
            </div>

            {/* Stats Grid */}
            {stats && (
                <>
                    <div className="stats-grid">
                        <div className="stat-card blue">
                            <div className="stat-icon">👥</div>
                            <div className="stat-content">
                                <h3>{stats.users?.total?.toLocaleString() || 0}</h3>
                                <p>Total Users</p>
                                <span className="stat-growth positive">
                                    +{stats.users?.recent_signups || 0} this week
                                </span>
                            </div>
                        </div>

                        <div className="stat-card green">
                            <div className="stat-icon">💎</div>
                            <div className="stat-content">
                                <h3>{stats.subscriptions?.total_active || 0}</h3>
                                <p>Active Pro/Premium</p>
                                <span className="stat-breakdown">
                                    {stats.subscriptions?.pro || 0} Pro • {stats.subscriptions?.premium || 0} Premium
                                </span>
                            </div>
                        </div>

                        <div className="stat-card purple">
                            <div className="stat-icon">💰</div>
                            <div className="stat-content">
                                <h3>{formatCurrency(stats.revenue?.mrr || 0)}</h3>
                                <p>Monthly Recurring Revenue</p>
                                <span className="stat-growth positive">
                                    {stats.users?.growth_rate || '+0%'}
                                </span>
                            </div>
                        </div>

                        <div className="stat-card orange">
                            <div className="stat-icon">🧩</div>
                            <div className="stat-content">
                                <h3>{stats.activity?.total_puzzles_generated?.toLocaleString() || 0}</h3>
                                <p>Puzzles Generated</p>
                                <span className="stat-breakdown">
                                    {stats.activity?.puzzles_today || 0} today
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Subscription Breakdown */}
                    <div className="dashboard-section">
                        <h2>💳 Subscription Distribution</h2>
                        <div className="subscription-breakdown">
                            <div className="breakdown-bar">
                                <div
                                    className="bar-segment pro"
                                    style={{ width: `${(stats.subscriptions?.pro / stats.users?.total * 100) || 0}%` }}
                                >
                                    <span>{stats.subscriptions?.pro || 0} Pro</span>
                                </div>
                                <div
                                    className="bar-segment premium"
                                    style={{ width: `${(stats.subscriptions?.premium / stats.users?.total * 100) || 0}%` }}
                                >
                                    <span>{stats.subscriptions?.premium || 0} Premium</span>
                                </div>
                                <div
                                    className="bar-segment free"
                                    style={{ width: `${(stats.subscriptions?.free / stats.users?.total * 100) || 0}%` }}
                                >
                                    <span>{stats.subscriptions?.free || 0} Free</span>
                                </div>
                            </div>
                            <div className="breakdown-legend">
                                <div className="legend-item">
                                    <span className="legend-color pro"></span>
                                    Pro ({((stats.subscriptions?.pro / stats.users?.total * 100) || 0).toFixed(1)}%)
                                </div>
                                <div className="legend-item">
                                    <span className="legend-color premium"></span>
                                    Premium ({((stats.subscriptions?.premium / stats.users?.total * 100) || 0).toFixed(1)}%)
                                </div>
                                <div className="legend-item">
                                    <span className="legend-color free"></span>
                                    Free ({((stats.subscriptions?.free / stats.users?.total * 100) || 0).toFixed(1)}%)
                                </div>
                            </div>
                        </div>
                    </div>
                </>
            )}

            {/* Recent Activity */}
            <div className="dashboard-section">
                <div className="section-header">
                    <h2>📈 Recent Activity</h2>
                    <button onClick={() => fetchRecentActivity(20)} className="btn-refresh">
                        🔄 Refresh
                    </button>
                </div>

                <div className="activity-list">
                    {recentActivity.length > 0 ? (
                        recentActivity.map((activity, index) => (
                            <div key={index} className="activity-item">
                                <div className="activity-icon">🧩</div>
                                <div className="activity-content">
                                    <p className="activity-text">
                                        <strong>{activity.username}</strong> generated a {activity.difficulty} {activity.puzzle_type} puzzle
                                        {activity.topic && ` about ${activity.topic}`}
                                    </p>
                                    <span className="activity-time">{formatDate(activity.timestamp)}</span>
                                </div>
                            </div>
                        ))
                    ) : (
                        <p className="no-activity">No recent activity</p>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;
