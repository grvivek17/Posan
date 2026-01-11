import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './ForgotPassword.css';

function ForgotPassword() {
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [resetLink, setResetLink] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setMessage('');
        setResetLink('');
        setLoading(true);

        try {
            const response = await axios.post(
                'http://localhost:8000/api/v1/auth/forgot-password',
                null,
                { params: { email } }
            );

            setMessage(response.data.message);

            // For testing: show the reset link
            if (response.data.reset_link) {
                setResetLink(response.data.reset_link);
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to send reset email. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="forgot-password-page">
            <div className="container">
                <div className="forgot-password-container">
                    <div className="forgot-password-card card">
                        <div className="icon-header">
                            <span className="lock-icon">🔒</span>
                        </div>

                        <h2 className="forgot-password-title">Forgot Password?</h2>
                        <p className="forgot-password-subtitle">
                            No worries! Enter your email and we'll send you reset instructions.
                        </p>

                        {message && (
                            <div className="success-message">
                                <span className="success-icon">✅</span>
                                <p>{message}</p>
                                {resetLink && (
                                    <div className="reset-link-box">
                                        <p className="test-note">
                                            <strong>For testing:</strong> Click the link below
                                        </p>
                                        <a href={resetLink} className="reset-link-btn">
                                            Reset Password →
                                        </a>
                                    </div>
                                )}
                            </div>
                        )}

                        {error && (
                            <div className="error-message">
                                <span className="error-icon">❌</span>
                                <p>{error}</p>
                            </div>
                        )}

                        {!message && (
                            <form onSubmit={handleSubmit} className="forgot-password-form">
                                <div className="form-group">
                                    <label htmlFor="email">Email Address</label>
                                    <input
                                        type="email"
                                        id="email"
                                        name="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                        placeholder="your.email@example.com"
                                        className="email-input"
                                    />
                                </div>

                                <button
                                    type="submit"
                                    className="btn btn-primary btn-large"
                                    disabled={loading}
                                >
                                    {loading ? 'Sending...' : 'Send Reset Link 📧'}
                                </button>
                            </form>
                        )}

                        <div className="back-to-login">
                            <Link to="/login" className="back-link">
                                ← Back to Login
                            </Link>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ForgotPassword;
