import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAdmin } from '../hooks/useAdmin';
import './AdminDashboard.css';

const AdminDashboard = () => {
    const navigate = useNavigate();
    const { stats, recentActivity, loading, fetchStats, fetchRecentActivity, fetchMagazines, refreshMagazines } = useAdmin();

    const [magazines, setMagazines] = useState([]);
    const [magLoading, setMagLoading] = useState(false);
    const [magRefreshing, setMagRefreshing] = useState(false);
    const [magResult, setMagResult] = useState(null);

    useEffect(() => {
        fetchStats();
        fetchRecentActivity(20);
        loadMagazines();
    }, []);

    const loadMagazines = async () => {
        setMagLoading(true);
        try {
            const data = await fetchMagazines();
            setMagazines(data);
        } finally {
            setMagLoading(false);
        }
    };

    const handleRefreshMagazines = async (force = false) => {
        setMagRefreshing(true);
        setMagResult(null);
        try {
            const result = await refreshMagazines(force);
            setMagResult(result);
            await loadMagazines();
        } catch (err) {
            setMagResult({ status: 'error', message: err.message || 'Refresh failed' });
        } finally {
            setMagRefreshing(false);
        }
    };

    const getMagazineStats = () => {
        const now = new Date();
        const currentMonth = now.getMonth() + 1;
        const currentYear = now.getFullYear();
        const currentMonthMags = magazines.filter(m => {
            if (!m.publication_date) return false;
            const d = new Date(m.publication_date);
            return d.getMonth() + 1 === currentMonth && d.getFullYear() === currentYear;
        });
        const ageGroups = {};
        magazines.forEach(m => {
            ageGroups[m.age_group] = (ageGroups[m.age_group] || 0) + 1;
        });
        return { total: magazines.length, currentMonth: currentMonthMags.length, ageGroups };
    };

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
                    <button onClick={() => navigate('/admin/orders')} className="btn-secondary">
                        🛒 Manage Orders
                    </button>
                    <button onClick={() => navigate('/admin/promotional-email')} className="btn-secondary email-btn">
                        📧 Promotional Email
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

            {/* Magazine Management */}
            <div className="dashboard-section magazine-management">
                <div className="section-header">
                    <h2>📚 Magazine Management</h2>
                    <div className="mag-header-actions">
                        <button
                            onClick={loadMagazines}
                            className="btn-refresh"
                            disabled={magLoading}
                        >
                            {magLoading ? '...' : '🔄'} Reload List
                        </button>
                    </div>
                </div>

                {(() => {
                    const magStats = getMagazineStats();
                    const monthName = new Date().toLocaleString('default', { month: 'long', year: 'numeric' });
                    return (
                        <>
                            <div className="mag-stats-row">
                                <div className="mag-stat-chip">
                                    <span className="mag-stat-number">{magStats.total}</span>
                                    <span className="mag-stat-label">Total Magazines</span>
                                </div>
                                <div className={`mag-stat-chip ${magStats.currentMonth > 0 ? 'green' : 'red'}`}>
                                    <span className="mag-stat-number">{magStats.currentMonth}</span>
                                    <span className="mag-stat-label">{monthName}</span>
                                </div>
                                {Object.entries(magStats.ageGroups).map(([age, count]) => (
                                    <div className="mag-stat-chip" key={age}>
                                        <span className="mag-stat-number">{count}</span>
                                        <span className="mag-stat-label">Ages {age}</span>
                                    </div>
                                ))}
                            </div>

                            <div className="mag-actions-row">
                                <button
                                    className="mag-action-btn refresh-btn"
                                    onClick={() => handleRefreshMagazines(false)}
                                    disabled={magRefreshing}
                                >
                                    {magRefreshing ? (
                                        <><span className="spinner-inline"></span> Fetching from web...</>
                                    ) : (
                                        <>🌐 Refresh This Month</>
                                    )}
                                </button>
                                <button
                                    className="mag-action-btn force-btn"
                                    onClick={() => handleRefreshMagazines(true)}
                                    disabled={magRefreshing}
                                >
                                    {magRefreshing ? (
                                        <><span className="spinner-inline"></span> Regenerating...</>
                                    ) : (
                                        <>🔄 Force Regenerate</>
                                    )}
                                </button>
                            </div>
                            <p className="mag-help-text">
                                <strong>Refresh:</strong> Fetches new magazines from web sources if none exist for this month.
                                <strong> Force Regenerate:</strong> Deletes existing magazines for this month and creates fresh ones from RSS feeds &amp; web scraping.
                            </p>

                            {magResult && (
                                <div className={`mag-result ${magResult.status === 'error' ? 'error' : magResult.status === 'skipped' ? 'skipped' : 'success'}`}>
                                    <strong>{magResult.status === 'success' ? '✅' : magResult.status === 'skipped' ? '⏭️' : '❌'} {magResult.status?.toUpperCase()}</strong>
                                    <span>{magResult.message}</span>
                                    {magResult.magazines && (
                                        <div className="mag-result-details">
                                            {magResult.magazines.map((m, i) => (
                                                <span key={i} className="mag-result-tag">
                                                    {m.title} ({m.articles_count} articles)
                                                </span>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}

                            {magazines.length > 0 && (
                                <div className="mag-list">
                                    <h3>Recent Magazines</h3>
                                    <div className="mag-grid">
                                        {magazines.slice(0, 8).map(mag => (
                                            <div key={mag.id} className="mag-card-mini" onClick={() => navigate(`/magazines/${mag.id}`)}>
                                                <div className="mag-card-cover">
                                                    {mag.cover_image_url ? (
                                                        <img src={mag.cover_image_url} alt={mag.title} />
                                                    ) : (
                                                        <div className="mag-placeholder">📚</div>
                                                    )}
                                                </div>
                                                <div className="mag-card-info">
                                                    <h4>{mag.title}</h4>
                                                    <span className="mag-age-badge">{mag.age_group}</span>
                                                    <span className="mag-issue">#{mag.issue_number}</span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </>
                    );
                })()}
            </div>

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
