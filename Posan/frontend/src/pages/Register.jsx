import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authAPI } from '../services/api';
import './Login.css';

function Register({ setIsAuthenticated }) {
    const [formData, setFormData] = useState({
        email: '',
        username: '',
        password: '',
        role: 'child',
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
            const response = await authAPI.register(formData);
            const { access_token, refresh_token } = response.data;

            // Store tokens and username
            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', refresh_token);
            localStorage.setItem('username', formData.username);

            setIsAuthenticated(true);
            navigate('/magazines');
        } catch (err) {
            setError(err.response?.data?.detail || 'Registration failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-page">
            <div className="container">
                <div className="login-container">
                    <div className="login-card card">
                        <h2 className="login-title">Join POSAN! 🎨</h2>
                        <p className="login-subtitle">Create your account and start exploring</p>

                        {error && <div className="error-message">{error}</div>}

                        <form onSubmit={handleSubmit} className="login-form">
                            <div className="form-group">
                                <label htmlFor="email">Email</label>
                                <input
                                    type="email"
                                    id="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    required
                                    placeholder="your.email@example.com"
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="username">Username</label>
                                <input
                                    type="text"
                                    id="username"
                                    name="username"
                                    value={formData.username}
                                    onChange={handleChange}
                                    required
                                    placeholder="Choose a cool username"
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
                                    minLength={6}
                                    placeholder="At least 6 characters"
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="role">I am a...</label>
                                <select
                                    id="role"
                                    name="role"
                                    value={formData.role}
                                    onChange={handleChange}
                                    required
                                >
                                    <option value="child">Kid</option>
                                    <option value="parent">Parent/Guardian</option>
                                </select>
                            </div>

                            <button type="submit" className="btn btn-primary btn-large" disabled={loading}>
                                {loading ? 'Creating account...' : 'Sign Up 🚀'}
                            </button>
                        </form>

                        <p className="login-footer">
                            Already have an account? <Link to="/login">Login here!</Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Register;
