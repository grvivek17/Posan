import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAdmin } from '../hooks/useAdmin';
import './AdminSubscriptionsPage.css';

const AdminSubscriptionsPage = () => {
    const navigate = useNavigate();
    const { subscriptions, loading, fetchSubscriptions } = useAdmin();
    const [tierFilter, setTierFilter] = useState('');
    const [statusFilter, setStatusFilter] = useState('');
    const [currentPage, setCurrentPage] = useState(0);
    const limit = 20;

    useEffect(() => {
        fetchSubscriptions(tierFilter, statusFilter, currentPage * limit, limit);
    }, [tierFilter, statusFilter, currentPage]);

    const formatDate = (dateString) => {
        if (!dateString) return 'Never';
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    };

    const getTierBadge = (tier) => {
        switch (tier) {
            case 'pro':
                return <span className="tier-badge pro">💎 Pro</span>;
            case 'premium':
                return <span className="tier-badge premium">👑 Premium</span>;
            default:
                return <span className="tier-badge free">📚 Free</span>;
        }
    };

    const getStatusBadge = (isActive, status) => {
        if (isActive) {
            return <span className="status-badge active">✅ Active</span>;
        } else if (status === 'cancelled') {
            return <span className="status-badge cancelled">❌ Cancelled</span>;
        } else {
            return <span className="status-badge expired">⏰ Expired</span>;
        }
    };

    const totalPages = subscriptions?.total ? Math.ceil(subscriptions.total / limit) : 0;

    // Calculate summary stats
    const proCount = subscriptions?.subscriptions?.filter(s => s.tier === 'pro' && s.is_active).length || 0;
    const premiumCount = subscriptions?.subscriptions?.filter(s => s.tier === 'premium' && s.is_active).length || 0;

    return (
        <div className="admin-subscriptions-page">
            <div className="page-header">
                <div>
                    <button onClick={() => navigate('/admin')} className="back-btn">
                        ← Back to Dashboard
                    </button>
                    <h1>💳 Subscriptions</h1>
                    <p className="page-subtitle">
                        {subscriptions?.total || 0} total subscriptions
                    </p>
                </div>
            </div>

            {/* Summary Cards */}
            <div className="summary-cards">
                <div className="summary-card pro">
                    <div className="summary-icon">💎</div>
                    <div className="summary-content">
                        <h3>{proCount}</h3>
                        <p>Active Pro</p>
                        <span>₹99/month each</span>
                    </div>
                </div>
                <div className="summary-card premium">
                    <div className="summary-icon">👑</div>
                    <div className="summary-content">
                        <h3>{premiumCount}</h3>
                        <p>Active Premium</p>
                        <span>₹999/year each</span>
                    </div>
                </div>
                <div className="summary-card revenue">
                    <div className="summary-icon">💰</div>
                    <div className="summary-content">
                        <h3>₹{(proCount * 99 + premiumCount * 83.25).toLocaleString()}</h3>
                        <p>Monthly Revenue</p>
                        <span>Estimated MRR</span>
                    </div>
                </div>
            </div>

            {/* Filters */}
            <div className="filters-section">
                <div className="filter-group">
                    <label>Tier:</label>
                    <select
                        value={tierFilter}
                        onChange={(e) => {
                            setTierFilter(e.target.value);
                            setCurrentPage(0);
                        }}
                    >
                        <option value="">All Tiers</option>
                        <option value="pro">Pro</option>
                        <option value="premium">Premium</option>
                        <option value="free">Free</option>
                    </select>
                </div>
                <div className="filter-group">
                    <label>Status:</label>
                    <select
                        value={statusFilter}
                        onChange={(e) => {
                            setStatusFilter(e.target.value);
                            setCurrentPage(0);
                        }}
                    >
                        <option value="">All Status</option>
                        <option value="active">Active</option>
                        <option value="cancelled">Cancelled</option>
                        <option value="expired">Expired</option>
                    </select>
                </div>
                <button
                    onClick={() => {
                        setTierFilter('');
                        setStatusFilter('');
                        setCurrentPage(0);
                    }}
                    className="clear-filters-btn"
                >
                    ✕ Clear Filters
                </button>
            </div>

            {/* Subscriptions Table */}
            <div className="subscriptions-table-container">
                {loading ? (
                    <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Loading subscriptions...</p>
                    </div>
                ) : subscriptions?.subscriptions?.length > 0 ? (
                    <>
                        <table className="subscriptions-table">
                            <thead>
                                <tr>
                                    <th>User</th>
                                    <th>Email</th>
                                    <th>Tier</th>
                                    <th>Status</th>
                                    <th>Expires</th>
                                    <th>Payment</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {subscriptions.subscriptions.map((sub) => (
                                    <tr key={sub.id}>
                                        <td>
                                            <strong>{sub.username}</strong>
                                        </td>
                                        <td>{sub.email}</td>
                                        <td>{getTierBadge(sub.tier)}</td>
                                        <td>{getStatusBadge(sub.is_active, sub.status)}</td>
                                        <td>
                                            {sub.expires_at ? (
                                                <span className={new Date(sub.expires_at) < new Date() ? 'expired-date' : ''}>
                                                    {formatDate(sub.expires_at)}
                                                </span>
                                            ) : (
                                                <span className="no-expiry">No expiry</span>
                                            )}
                                        </td>
                                        <td>
                                            {sub.payment_provider ? (
                                                <span className="payment-provider">{sub.payment_provider}</span>
                                            ) : (
                                                <span className="no-payment">-</span>
                                            )}
                                        </td>
                                        <td>
                                            <button
                                                onClick={() => navigate(`/admin/users/${sub.user_id}`)}
                                                className="action-btn"
                                            >
                                                👁️ View User
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>

                        {/* Pagination */}
                        {totalPages > 1 && (
                            <div className="pagination">
                                <button
                                    onClick={() => setCurrentPage(p => Math.max(0, p - 1))}
                                    disabled={currentPage === 0}
                                    className="page-btn"
                                >
                                    ← Previous
                                </button>

                                <span className="page-info">
                                    Page {currentPage + 1} of {totalPages}
                                </span>

                                <button
                                    onClick={() => setCurrentPage(p => Math.min(totalPages - 1, p + 1))}
                                    disabled={currentPage >= totalPages - 1}
                                    className="page-btn"
                                >
                                    Next →
                                </button>
                            </div>
                        )}
                    </>
                ) : (
                    <div className="empty-state">
                        <div className="empty-icon">💳</div>
                        <h3>No subscriptions found</h3>
                        <p>Try adjusting your filters</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AdminSubscriptionsPage;
