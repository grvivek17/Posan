import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import axios from 'axios';
import './ResetPassword.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

function ResetPassword() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [token, setToken] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [verifying, setVerifying] = useState(true);
    const [tokenValid, setTokenValid] = useState(false);
    const [email, setEmail] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        const tokenParam = searchParams.get('token');
        if (tokenParam) {
            setToken(tokenParam);
            verifyToken(tokenParam);
        } else {
            setError('No reset token provided');
            setVerifying(false);
        }
    }, [searchParams]);

    const verifyToken = async (tokenToVerify) => {
        try {
            const response = await axios.post(
                `${API_BASE}/auth/verify-reset-token`,
                null,
                { params: { token: tokenToVerify } }
            );

            if (response.data.valid) {
                setTokenValid(true);
                setEmail(response.data.email);
            } else {
                setError(response.data.message || 'Invalid or expired reset token');
                setTokenValid(false);
            }
        } catch (err) {
            setError('Failed to verify reset token');
            setTokenValid(false);
        } finally {
            setVerifying(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setMessage('');

        // Validate passwords match
        if (newPassword !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        // Validate password strength
        if (newPassword.length < 6) {
            setError('Password must be at least 6 characters long');
            return;
        }

        setLoading(true);

        try {
            console.log('Resetting password with token:', token);
            console.log('New password length:', newPassword.length);

            const response = await axios.post(
                `${API_BASE}/auth/reset-password`,
                null,
                { params: { token, new_password: newPassword } }
            );

            console.log('Password reset response:', response.data);
            setMessage(response.data.message);

            // Redirect to login after 2 seconds
            setTimeout(() => {
                navigate('/login');
            }, 2000);
        } catch (err) {
            console.error('Password reset error:', err);
            console.error('Error response:', err.response?.data);
            setError(err.response?.data?.detail || 'Failed to reset password. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    if (verifying) {
        return (
            <div className="reset-password-page">
                <div className="container">
                    <div className="reset-password-container">
                        <div className="verifying-box">
                            <div className="spinner"></div>
                            <p>Verifying reset token...</p>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    if (!tokenValid) {
        return (
            <div className="reset-password-page">
                <div className="container">
                    <div className="reset-password-container">
                        <div className="reset-password-card card">
                            <div className="icon-header error">
                                <span className="error-icon-large">⚠️</span>
                            </div>
                            <h2 className="reset-password-title">Invalid Reset Link</h2>
                            <p className="error-text">{error}</p>
                            <div className="action-buttons">
                                <Link to="/forgot-password" className="btn btn-primary">
                                    Request New Link
                                </Link>
                                <Link to="/login" className="btn btn-secondary">
                                    Back to Login
                                </Link>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="reset-password-page">
            <div className="container">
                <div className="reset-password-container">
                    <div className="reset-password-card card">
                        <div className="icon-header">
                            <span className="key-icon">🔑</span>
                        </div>

                        <h2 className="reset-password-title">Reset Your Password</h2>
                        <p className="reset-password-subtitle">
                            Enter a new password for <strong>{email}</strong>
                        </p>

                        {message && (
                            <div className="success-message">
                                <span className="success-icon">✅</span>
                                <p>{message}</p>
                                <p className="redirect-note">Redirecting to login...</p>
                            </div>
                        )}

                        {error && (
                            <div className="error-message">
                                <span className="error-icon">❌</span>
                                <p>{error}</p>
                            </div>
                        )}

                        {!message && (
                            <form onSubmit={handleSubmit} className="reset-password-form">
                                <div className="form-group">
                                    <label htmlFor="newPassword">New Password</label>
                                    <input
                                        type="password"
                                        id="newPassword"
                                        name="newPassword"
                                        value={newPassword}
                                        onChange={(e) => setNewPassword(e.target.value)}
                                        required
                                        minLength="6"
                                        placeholder="Enter new password"
                                    />
                                    <small className="password-hint">
                                        Minimum 6 characters
                                    </small>
                                </div>

                                <div className="form-group">
                                    <label htmlFor="confirmPassword">Confirm Password</label>
                                    <input
                                        type="password"
                                        id="confirmPassword"
                                        name="confirmPassword"
                                        value={confirmPassword}
                                        onChange={(e) => setConfirmPassword(e.target.value)}
                                        required
                                        minLength="6"
                                        placeholder="Confirm new password"
                                    />
                                </div>

                                <button
                                    type="submit"
                                    className="btn btn-primary btn-large"
                                    disabled={loading}
                                >
                                    {loading ? 'Resetting...' : 'Reset Password 🔐'}
                                </button>
                            </form>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ResetPassword;
