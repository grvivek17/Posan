import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import PointsDisplay from './PointsDisplay';
import './Header.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

function Header({ isAuthenticated, setIsAuthenticated }) {
    const navigate = useNavigate();
    const [username, setUsername] = useState('');
    const [isAdmin, setIsAdmin] = useState(false);

    useEffect(() => {
        // Get username from localStorage when component mounts or auth changes
        if (isAuthenticated) {
            const storedUsername = localStorage.getItem('username');
            setUsername(storedUsername || 'User');

            // Check if user is admin
            const checkAdmin = async () => {
                try {
                    const token = localStorage.getItem('token');
                    if (!token) return;

                    const response = await fetch(`${API_BASE}/users/me`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });

                    if (response.ok) {
                        const userData = await response.json();
                        setIsAdmin(userData.is_admin || false);
                    }
                } catch (err) {
                    console.error('Error checking admin status:', err);
                }
            };
            checkAdmin();
        } else {
            setIsAdmin(false);
        }
    }, [isAuthenticated]);

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_id');
        localStorage.removeItem('username');
        setIsAuthenticated(false);
        setIsAdmin(false);
        setUsername('');
        navigate('/');
    };

    return (
        <header className="header">
            <div className="container">
                <div className="header-content">
                    {/* Left: Logo */}
                    <Link to="/" className="logo">
                        <h1 className="logo-text">🎨 POSAN</h1>
                    </Link>

                    {/* Center: Main Navigation */}
                    {isAuthenticated && (
                        <nav className="nav-center">
                            <Link to="/magazines" className="nav-link">📚 Magazines</Link>
                            <Link to="/puzzle-zone" className="nav-link">🧩 Puzzles</Link>
                            <Link to="/games" className="nav-link">🎮 Games</Link>
                            <Link to="/homework" className="nav-link">📝 Homework</Link>
                            <Link to="/planner" className="nav-link">📅 Planner</Link>
                            <Link to="/ai-content" className="nav-link">🤖 AI Creator</Link>
                        </nav>
                    )}

                    {/* Right: User Section */}
                    <div className="nav-right">
                        {isAuthenticated ? (
                            <>
                                <Link to="/about" className="nav-link-secondary">About</Link>
                                {isAdmin && (
                                    <Link to="/admin" className="nav-link-admin">⚙️ Admin</Link>
                                )}
                                <div className="divider"></div>
                                <Link to="/achievements">
                                    <PointsDisplay compact={true} />
                                </Link>
                                <Link to="/store" className="cart-link" title="Activity Book Store">
                                    🛒
                                </Link>
                                <div className="user-menu">
                                    <div className="username-label">{username}</div>
                                    <Link to="/profile" className="profile-link">
                                        <span className="profile-icon">👤</span>
                                    </Link>
                                    <button onClick={handleLogout} className="btn btn-logout">
                                        Logout
                                    </button>
                                </div>
                            </>
                        ) : (
                            <>
                                <Link to="/about" className="nav-link-secondary">About</Link>
                                <Link to="/store" className="cart-link" title="Activity Book Store">
                                    🛒
                                </Link>
                                <Link to="/login" className="btn btn-primary">Login</Link>
                                <Link to="/register" className="btn btn-secondary">Sign Up</Link>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </header>
    );
}

export default Header;
