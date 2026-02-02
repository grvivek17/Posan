import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAdmin } from '../hooks/useAdmin';
import './AdminUsersPage.css';

const AdminUsersPage = () => {
    const navigate = useNavigate();
    const { users, loading, fetchUsers } = useAdmin();
    const [search, setSearch] = useState('');
    const [currentPage, setCurrentPage] = useState(0);
    const limit = 20;

    useEffect(() => {
        fetchUsers(search, currentPage * limit, limit);
    }, [currentPage]);

    const handleSearch = (e) => {
        e.preventDefault();
        setCurrentPage(0);
        fetchUsers(search, 0, limit);
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'Never';
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    };

    const totalPages = users?.total ? Math.ceil(users.total / limit) : 0;

    return (
        <div className="admin-users-page">
            <div className="page-header">
                <div>
                    <button onClick={() => navigate('/admin')} className="back-btn">
                        ← Back to Dashboard
                    </button>
                    <h1>👤 User Management</h1>
                    <p className="page-subtitle">
                        {users?.total || 0} total users
                    </p>
                </div>
            </div>

            {/* Search Bar */}
            <div className="search-section">
                <form onSubmit={handleSearch} className="search-form">
                    <input
                        type="text"
                        placeholder="Search by username or email..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="search-input"
                    />
                    <button type="submit" className="search-btn">
                        🔍 Search
                    </button>
                    {search && (
                        <button
                            type="button"
                            onClick={() => {
                                setSearch('');
                                setCurrentPage(0);
                                fetchUsers('', 0, limit);
                            }}
                            className="clear-btn"
                        >
                            ✕ Clear
                        </button>
                    )}
                </form>
            </div>

            {/* Users Table */}
            <div className="users-table-container">
                {loading ? (
                    <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Loading users...</p>
                    </div>
                ) : users?.users?.length > 0 ? (
                    <>
                        <table className="users-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Username</th>
                                    <th>Email</th>
                                    <th>Full Name</th>
                                    <th>Admin</th>
                                    <th>Joined</th>
                                    <th>Last Login</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {users.users.map((user) => (
                                    <tr key={user.id}>
                                        <td>{user.id}</td>
                                        <td>
                                            <strong>{user.username}</strong>
                                        </td>
                                        <td>{user.email}</td>
                                        <td>{user.full_name || '-'}</td>
                                        <td>
                                            {user.is_admin ? (
                                                <span className="badge admin">👑 Admin</span>
                                            ) : (
                                                <span className="badge user">User</span>
                                            )}
                                        </td>
                                        <td>{formatDate(user.created_at)}</td>
                                        <td>{formatDate(user.last_login)}</td>
                                        <td>
                                            <button
                                                onClick={() => navigate(`/admin/users/${user.id}`)}
                                                className="action-btn view"
                                            >
                                                👁️ View
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
                        <div className="empty-icon">🔍</div>
                        <h3>No users found</h3>
                        <p>Try adjusting your search criteria</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AdminUsersPage;
