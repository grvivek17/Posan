import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Header.css';

function Header({ isAuthenticated, setIsAuthenticated }) {
    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_id');
        setIsAuthenticated(false);
        navigate('/');
    };

    return (
        <header className="header">
            <div className="container">
                <div className="header-content">
                    <Link to="/" className="logo">
                        <h1 className="logo-text">🎨 POSAN</h1>
                    </Link>

                    <nav className="nav">
                        {isAuthenticated ? (
                            <>
                                <Link to="/magazines" className="nav-link">📚 Magazines</Link>
                                <Link to="/puzzles" className="nav-link">🧩 Puzzles</Link>
                                <Link to="/ai-content" className="nav-link">🤖 AI Creator</Link>
                                <Link to="/profile" className="nav-link">👤 Profile</Link>
                                <button onClick={handleLogout} className="btn btn-secondary">
                                    Logout
                                </button>
                            </>
                        ) : (
                            <>
                                <Link to="/login" className="btn btn-primary">Login</Link>
                                <Link to="/register" className="btn btn-secondary">Sign Up</Link>
                            </>
                        )}
                    </nav>
                </div>
            </div>
        </header>
    );
}

export default Header;
