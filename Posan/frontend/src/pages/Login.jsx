import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authAPI } from '../services/api';
import './Login.css';

function Login({ setIsAuthenticated }) {
    const [formData, setFormData] = useState({
        username: '',
        password: '',
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const response = await authAPI.login(formData);
            const { access_token, refresh_token, user_id } = response.data;

            // Store tokens and user info
            localStorage.setItem('access_token', access_token);
            localStorage.setItem('token', access_token); // For gamification system
            localStorage.setItem('refresh_token', refresh_token);
            localStorage.setItem('username', formData.username);
            localStorage.setItem('user_id', user_id); // For gamification system

            setIsAuthenticated(true);
            navigate('/magazines');
        } catch (err) {
            setError(err.response?.data?.detail || 'Login failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-page">
            <div className="container">
                <div className="login-container">
                    <div className="login-card card">
                        <h2 className="login-title">Welcome Back! 👋</h2>
                        <p className="login-subtitle">Login to continue your adventure</p>

                        {error && <div className="error-message">{error}</div>}

                        <form onSubmit={handleSubmit} className="login-form">
                            <div className="form-group">
                                <label htmlFor="username">Username</label>
                                <input
                                    type="text"
                                    id="username"
                                    name="username"
                                    value={formData.username}
                                    onChange={handleChange}
                                    required
                                    placeholder="Enter your username"
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="password">Password</label>
                                <input
                                    type="password"
                                    id="password"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    required
                                    placeholder="Enter your password"
                                />
                                <div className="forgot-password-link">
                                    <Link to="/forgot-password">Forgot password?</Link>
                                </div>
                            </div>

                            <button type="submit" className="btn btn-primary btn-large" disabled={loading}>
                                {loading ? 'Logging in...' : 'Login 🚀'}
                            </button>
                        </form>

                        <p className="login-footer">
                            Don't have an account? <Link to="/register">Sign up here!</Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Login;
