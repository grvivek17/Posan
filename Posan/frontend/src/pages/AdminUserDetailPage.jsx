import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAdmin } from '../hooks/useAdmin';
import './AdminUserDetailPage.css';

const AdminUserDetailPage = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { fetchUserDetails, upgradeUser, deleteUser, updateUser, resetPassword, loading } = useAdmin();
    const [user, setUser] = useState(null);
    const [showUpgradeModal, setShowUpgradeModal] = useState(false);
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [showEditModal, setShowEditModal] = useState(false);
    const [showPasswordModal, setShowPasswordModal] = useState(false);
    const [actionLoading, setActionLoading] = useState(false);

    // Edit form state
    const [editForm, setEditForm] = useState({
        username: '',
        email: '',
        full_name: '',
        is_admin: false
    });

    // Password reset state
    const [newPassword, setNewPassword] = useState('');

    useEffect(() => {
        loadUser();
    }, [id]);

    const loadUser = async () => {
        try {
            const data = await fetchUserDetails(id);
            setUser(data);
        } catch (err) {
            console.error('Error loading user:', err);
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'Never';
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const handleUpgrade = async (tier) => {
        setActionLoading(true);
        try {
            await upgradeUser(id, tier);
            alert(`✅ User upgraded to ${tier}!`);
            setShowUpgradeModal(false);
            loadUser();
        } catch (err) {
            alert(`❌ Failed to upgrade: ${err.message}`);
        } finally {
            setActionLoading(false);
        }
    };

    const handleDelete = async () => {
        setActionLoading(true);
        try {
            await deleteUser(id);
            alert('✅ User deleted successfully');
            navigate('/admin/users');
        } catch (err) {
            alert(`❌ Failed to delete: ${err.message}`);
        } finally {
            setActionLoading(false);
        }
    };

    const openEditModal = () => {
        setEditForm({
            username: user.user.username || '',
            email: user.user.email || '',
            full_name: user.user.full_name || '',
            is_admin: user.user.is_admin || false
        });
        setShowEditModal(true);
    };

    const handleEditSubmit = async () => {
        setActionLoading(true);
        try {
            await updateUser(id, editForm);
            alert('✅ User updated successfully!');
            setShowEditModal(false);
            loadUser();
        } catch (err) {
            alert(`❌ Failed to update: ${err.message}`);
        } finally {
            setActionLoading(false);
        }
    };

    const handlePasswordReset = async () => {
        if (newPassword.length < 6) {
            alert('❌ Password must be at least 6 characters');
            return;
        }
        setActionLoading(true);
        try {
            await resetPassword(id, newPassword);
            alert('✅ Password reset successfully!');
            setShowPasswordModal(false);
            setNewPassword('');
        } catch (err) {
            alert(`❌ Failed to reset password: ${err.message}`);
        } finally {
            setActionLoading(false);
        }
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

    if (loading && !user) {
        return (
            <div className="admin-user-detail">
                <div className="loading-state">
                    <div className="spinner"></div>
                    <p>Loading user details...</p>
                </div>
            </div>
        );
    }

    if (!user) {
        return (
            <div className="admin-user-detail">
                <div className="error-state">
                    <h2>❌ User not found</h2>
                    <button onClick={() => navigate('/admin/users')}>← Back to Users</button>
                </div>
            </div>
        );
    }

    return (
        <div className="admin-user-detail">
            <div className="page-header">
                <button onClick={() => navigate('/admin/users')} className="back-btn">
                    ← Back to Users
                </button>
                <h1>👤 User Details</h1>
            </div>

            <div className="user-detail-grid">
                {/* User Info Card */}
                <div className="detail-card main-info">
                    <div className="user-avatar-large">
                        {user.user.username.charAt(0).toUpperCase()}
                    </div>
                    <h2>{user.user.username}</h2>
                    <p className="email">{user.user.email}</p>
                    {user.user.is_admin && (
                        <span className="admin-badge">👑 Administrator</span>
                    )}
                </div>

                {/* Subscription Card */}
                <div className="detail-card subscription-info">
                    <h3>💳 Subscription</h3>
                    {user.subscription ? (
                        <div className="subscription-details">
                            <div className="tier-row">
                                {getTierBadge(user.subscription.tier)}
                                <span className={`status ${user.subscription.is_active ? 'active' : 'inactive'}`}>
                                    {user.subscription.is_active ? '✅ Active' : '❌ Inactive'}
                                </span>
                            </div>

                            <div className="info-grid">
                                <div className="info-item">
                                    <label>Status</label>
                                    <span>{user.subscription.status}</span>
                                </div>
                                <div className="info-item">
                                    <label>Expires</label>
                                    <span>{user.subscription.expires_at ? formatDate(user.subscription.expires_at) : 'Never'}</span>
                                </div>
                                <div className="info-item">
                                    <label>Payment Provider</label>
                                    <span>{user.subscription.payment_provider || 'N/A'}</span>
                                </div>
                                <div className="info-item">
                                    <label>Created</label>
                                    <span>{formatDate(user.subscription.created_at)}</span>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <p className="no-subscription">No subscription data</p>
                    )}
                </div>

                {/* Activity Card */}
                <div className="detail-card activity-info">
                    <h3>📊 Activity Stats</h3>
                    <div className="activity-stats">
                        <div className="activity-stat">
                            <span className="stat-value">{user.activity?.total_puzzle_generations || 0}</span>
                            <span className="stat-label">Puzzles Generated</span>
                        </div>
                        <div className="activity-stat">
                            <span className="stat-value">{user.activity?.active_days || 0}</span>
                            <span className="stat-label">Active Days</span>
                        </div>
                    </div>
                </div>

                {/* Account Details Card */}
                <div className="detail-card account-info">
                    <h3>📋 Account Details</h3>
                    <div className="info-grid">
                        <div className="info-item">
                            <label>User ID</label>
                            <span>#{user.user.id}</span>
                        </div>
                        <div className="info-item">
                            <label>Full Name</label>
                            <span>{user.user.full_name || 'Not set'}</span>
                        </div>
                        <div className="info-item">
                            <label>Joined</label>
                            <span>{formatDate(user.user.created_at)}</span>
                        </div>
                        <div className="info-item">
                            <label>Last Login</label>
                            <span>{formatDate(user.user.last_login)}</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Action Buttons */}
            <div className="action-section">
                <h3>⚡ Admin Actions</h3>
                <div className="action-buttons">
                    <button
                        onClick={openEditModal}
                        className="action-btn edit"
                    >
                        ✏️ Edit User
                    </button>
                    <button
                        onClick={() => setShowPasswordModal(true)}
                        className="action-btn password"
                    >
                        🔑 Reset Password
                    </button>
                    <button
                        onClick={() => setShowUpgradeModal(true)}
                        className="action-btn upgrade"
                    >
                        ⬆️ Upgrade Subscription
                    </button>
                    <button
                        onClick={() => setShowDeleteModal(true)}
                        className="action-btn delete"
                    >
                        🗑️ Delete User
                    </button>
                </div>
            </div>

            {/* Upgrade Modal */}
            {showUpgradeModal && (
                <div className="modal-overlay" onClick={() => setShowUpgradeModal(false)}>
                    <div className="modal-content" onClick={e => e.stopPropagation()}>
                        <h2>⬆️ Upgrade User</h2>
                        <p>Select subscription tier for <strong>{user.user.username}</strong>:</p>
                        <div className="upgrade-options">
                            <button
                                onClick={() => handleUpgrade('pro')}
                                disabled={actionLoading}
                                className="tier-btn pro"
                            >
                                💎 Pro (₹99/mo)
                            </button>
                            <button
                                onClick={() => handleUpgrade('premium')}
                                disabled={actionLoading}
                                className="tier-btn premium"
                            >
                                👑 Premium (₹999/yr)
                            </button>
                        </div>
                        <button
                            onClick={() => setShowUpgradeModal(false)}
                            className="cancel-btn"
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            )}

            {/* Delete Modal */}
            {showDeleteModal && (
                <div className="modal-overlay" onClick={() => setShowDeleteModal(false)}>
                    <div className="modal-content delete-modal" onClick={e => e.stopPropagation()}>
                        <h2>⚠️ Delete User</h2>
                        <p>Are you sure you want to delete <strong>{user.user.username}</strong>?</p>
                        <p className="warning">This action cannot be undone. All user data will be permanently deleted.</p>
                        <div className="modal-actions">
                            <button
                                onClick={() => setShowDeleteModal(false)}
                                className="cancel-btn"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleDelete}
                                disabled={actionLoading}
                                className="confirm-delete-btn"
                            >
                                {actionLoading ? 'Deleting...' : '🗑️ Yes, Delete User'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Edit User Modal */}
            {showEditModal && (
                <div className="modal-overlay" onClick={() => setShowEditModal(false)}>
                    <div className="modal-content edit-modal" onClick={e => e.stopPropagation()}>
                        <h2>✏️ Edit User</h2>
                        <p>Update details for <strong>{user.user.username}</strong></p>

                        <div className="edit-form">
                            <div className="form-group">
                                <label>Username</label>
                                <input
                                    type="text"
                                    value={editForm.username}
                                    onChange={e => setEditForm({ ...editForm, username: e.target.value })}
                                    placeholder="Username"
                                />
                            </div>

                            <div className="form-group">
                                <label>Email</label>
                                <input
                                    type="email"
                                    value={editForm.email}
                                    onChange={e => setEditForm({ ...editForm, email: e.target.value })}
                                    placeholder="Email"
                                />
                            </div>

                            <div className="form-group">
                                <label>Full Name</label>
                                <input
                                    type="text"
                                    value={editForm.full_name}
                                    onChange={e => setEditForm({ ...editForm, full_name: e.target.value })}
                                    placeholder="Full Name (optional)"
                                />
                            </div>

                            <div className="form-group checkbox-group">
                                <label>
                                    <input
                                        type="checkbox"
                                        checked={editForm.is_admin}
                                        onChange={e => setEditForm({ ...editForm, is_admin: e.target.checked })}
                                    />
                                    <span>Administrator Access</span>
                                </label>
                            </div>
                        </div>

                        <div className="modal-actions">
                            <button onClick={() => setShowEditModal(false)} className="cancel-btn">
                                Cancel
                            </button>
                            <button
                                onClick={handleEditSubmit}
                                disabled={actionLoading}
                                className="save-btn"
                            >
                                {actionLoading ? 'Saving...' : '💾 Save Changes'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Password Reset Modal */}
            {showPasswordModal && (
                <div className="modal-overlay" onClick={() => setShowPasswordModal(false)}>
                    <div className="modal-content password-modal" onClick={e => e.stopPropagation()}>
                        <h2>🔑 Reset Password</h2>
                        <p>Set a new password for <strong>{user.user.username}</strong></p>

                        <div className="edit-form">
                            <div className="form-group">
                                <label>New Password</label>
                                <input
                                    type="password"
                                    value={newPassword}
                                    onChange={e => setNewPassword(e.target.value)}
                                    placeholder="Enter new password (min 6 characters)"
                                    minLength={6}
                                />
                            </div>
                        </div>

                        <div className="modal-actions">
                            <button onClick={() => { setShowPasswordModal(false); setNewPassword(''); }} className="cancel-btn">
                                Cancel
                            </button>
                            <button
                                onClick={handlePasswordReset}
                                disabled={actionLoading || newPassword.length < 6}
                                className="save-btn"
                            >
                                {actionLoading ? 'Resetting...' : '🔑 Reset Password'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AdminUserDetailPage;
