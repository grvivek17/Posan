import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './AdminPromotionalEmailPage.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const AdminPromotionalEmailPage = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    // SMTP Status
    const [smtpStatus, setSmtpStatus] = useState(null);

    // New Arrivals Data
    const [newArrivals, setNewArrivals] = useState(null);
    const [daysBack, setDaysBack] = useState(7);

    // Subscribers
    const [subscribers, setSubscribers] = useState([]);
    const [selectedEmails, setSelectedEmails] = useState([]);

    // Email Preview
    const [previewHtml, setPreviewHtml] = useState('');
    const [showPreview, setShowPreview] = useState(false);

    // Custom Email Form
    const [customEmail, setCustomEmail] = useState({
        subject: '',
        heading: '',
        content: '',
        ctaText: 'Learn More',
        ctaUrl: '#'
    });

    // Active Tab
    const [activeTab, setActiveTab] = useState('weekly');

    const getAuthHeaders = () => {
        const token = localStorage.getItem('token');
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };
    };

    // Fetch SMTP Status
    const fetchSmtpStatus = async () => {
        try {
            const response = await fetch(`${API_BASE}/admin/promotional-email/smtp-status`, {
                headers: getAuthHeaders()
            });
            if (response.ok) {
                const data = await response.json();
                setSmtpStatus(data);
            }
        } catch (err) {
            console.error('Error fetching SMTP status:', err);
        }
    };

    // Fetch New Arrivals
    const fetchNewArrivals = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE}/admin/promotional-email/new-arrivals?days=${daysBack}`, {
                headers: getAuthHeaders()
            });
            if (!response.ok) throw new Error('Failed to fetch new arrivals');
            const data = await response.json();
            setNewArrivals(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    // Fetch Subscribers
    const fetchSubscribers = async () => {
        try {
            const response = await fetch(`${API_BASE}/admin/promotional-email/subscribers`, {
                headers: getAuthHeaders()
            });
            if (response.ok) {
                const data = await response.json();
                setSubscribers(data.subscribers || []);
            }
        } catch (err) {
            console.error('Error fetching subscribers:', err);
        }
    };

    // Preview Email
    const previewEmail = async () => {
        setLoading(true);
        try {
            const response = await fetch(
                `${API_BASE}/admin/promotional-email/preview-weekly-arrivals?days=${daysBack}`,
                {
                    method: 'POST',
                    headers: getAuthHeaders()
                }
            );
            if (!response.ok) throw new Error('Failed to generate preview');
            const data = await response.json();
            setPreviewHtml(data.html);
            setShowPreview(true);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    // Send Weekly Arrivals Email
    const sendWeeklyArrivalsEmail = async () => {
        if (selectedEmails.length === 0) {
            setError('Please select at least one recipient');
            return;
        }

        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_BASE}/admin/promotional-email/send-weekly-arrivals`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({
                    recipient_emails: selectedEmails,
                    recipient_name: 'Dear Reader',
                    days_back: daysBack
                })
            });
            if (!response.ok) throw new Error('Failed to send email');
            const data = await response.json();
            setSuccess(`✅ ${data.message}`);
            setSelectedEmails([]);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    // Send Custom Email
    const sendCustomEmail = async () => {
        if (selectedEmails.length === 0) {
            setError('Please select at least one recipient');
            return;
        }
        if (!customEmail.subject || !customEmail.heading || !customEmail.content) {
            setError('Please fill in all required fields');
            return;
        }

        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_BASE}/admin/promotional-email/send-custom`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({
                    recipient_emails: selectedEmails,
                    subject: customEmail.subject,
                    heading: customEmail.heading,
                    content: customEmail.content,
                    cta_text: customEmail.ctaText,
                    cta_url: customEmail.ctaUrl
                })
            });
            if (!response.ok) throw new Error('Failed to send email');
            const data = await response.json();
            setSuccess(`✅ ${data.message}`);
            setSelectedEmails([]);
            setCustomEmail({ subject: '', heading: '', content: '', ctaText: 'Learn More', ctaUrl: '#' });
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    // Send Test Email
    const sendTestEmail = async () => {
        const testEmail = prompt('Enter email address to send test:');
        if (!testEmail) return;

        setLoading(true);
        try {
            const response = await fetch(`${API_BASE}/admin/promotional-email/send-test?to_email=${testEmail}`, {
                method: 'POST',
                headers: getAuthHeaders()
            });
            const data = await response.json();
            if (data.success) {
                setSuccess('✅ Test email sent successfully!');
            } else {
                setError(`Failed: ${data.error}`);
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    // Send to All Users
    const sendToAllUsers = async () => {
        if (!window.confirm('⚠️ Are you sure you want to send promotional email to ALL users?')) {
            return;
        }

        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_BASE}/admin/promotional-email/send-to-all-users`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({
                    subject: '🌟 This Week\'s New Arrivals at POSAN! 📚',
                    include_new_magazines: true,
                    include_new_products: true,
                    days_back: daysBack
                })
            });
            if (!response.ok) throw new Error('Failed to send emails');
            const data = await response.json();
            setSuccess(`✅ ${data.message} (${data.total_recipients} recipients)`);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    // Toggle email selection
    const toggleEmailSelection = (email) => {
        setSelectedEmails(prev =>
            prev.includes(email)
                ? prev.filter(e => e !== email)
                : [...prev, email]
        );
    };

    // Select all emails
    const selectAllEmails = () => {
        if (selectedEmails.length === subscribers.length) {
            setSelectedEmails([]);
        } else {
            setSelectedEmails(subscribers.map(s => s.email));
        }
    };

    useEffect(() => {
        fetchSmtpStatus();
        fetchNewArrivals();
        fetchSubscribers();
    }, []);

    useEffect(() => {
        fetchNewArrivals();
    }, [daysBack]);

    // Auto-clear messages
    useEffect(() => {
        if (success || error) {
            const timer = setTimeout(() => {
                setSuccess(null);
                setError(null);
            }, 5000);
            return () => clearTimeout(timer);
        }
    }, [success, error]);

    return (
        <div className="admin-promo-email-page">
            <div className="promo-header">
                <button className="back-btn" onClick={() => navigate('/admin')}>
                    ← Back to Admin
                </button>
                <h1>📧 Promotional Email Campaign</h1>
                <p className="subtitle">Send beautiful promotional emails to your users</p>
            </div>

            {/* Status Messages */}
            {error && <div className="message error-message">❌ {error}</div>}
            {success && <div className="message success-message">{success}</div>}

            {/* SMTP Status Card */}
            <div className="smtp-status-card">
                <h3>📡 SMTP Configuration</h3>
                {smtpStatus ? (
                    <div className="smtp-info">
                        <span className={`status-badge ${smtpStatus.configured ? 'configured' : 'not-configured'}`}>
                            {smtpStatus.configured ? '✅ Configured' : '❌ Not Configured'}
                        </span>
                        <span className="smtp-detail">Host: {smtpStatus.smtp_host}</span>
                        <span className="smtp-detail">User: {smtpStatus.smtp_user}</span>
                        <button className="test-btn" onClick={sendTestEmail} disabled={loading || !smtpStatus.configured}>
                            🧪 Send Test Email
                        </button>
                    </div>
                ) : (
                    <p>Loading SMTP status...</p>
                )}
            </div>

            {/* Tab Navigation */}
            <div className="tab-navigation">
                <button
                    className={`tab-btn ${activeTab === 'weekly' ? 'active' : ''}`}
                    onClick={() => setActiveTab('weekly')}
                >
                    📰 Weekly Arrivals
                </button>
                <button
                    className={`tab-btn ${activeTab === 'custom' ? 'active' : ''}`}
                    onClick={() => setActiveTab('custom')}
                >
                    ✏️ Custom Email
                </button>
            </div>

            <div className="promo-content">
                {/* Left Column - Content */}
                <div className="content-column">
                    {activeTab === 'weekly' ? (
                        <>
                            {/* Days Back Selector */}
                            <div className="days-selector">
                                <label>Show arrivals from last:</label>
                                <select value={daysBack} onChange={(e) => setDaysBack(Number(e.target.value))}>
                                    <option value={3}>3 days</option>
                                    <option value={7}>7 days (1 week)</option>
                                    <option value={14}>14 days (2 weeks)</option>
                                    <option value={30}>30 days (1 month)</option>
                                </select>
                            </div>

                            {/* New Arrivals Summary */}
                            {newArrivals && (
                                <div className="arrivals-summary">
                                    <h3>📦 New Arrivals Summary</h3>
                                    <div className="summary-cards">
                                        <div className="summary-card magazines">
                                            <span className="count">{newArrivals.summary.new_magazines_count}</span>
                                            <span className="label">New Magazines</span>
                                        </div>
                                        <div className="summary-card products">
                                            <span className="count">{newArrivals.summary.new_products_count}</span>
                                            <span className="label">New Products</span>
                                        </div>
                                    </div>

                                    {/* Magazine List */}
                                    {newArrivals.magazines.length > 0 && (
                                        <div className="arrivals-list">
                                            <h4>📚 Magazines</h4>
                                            {newArrivals.magazines.map(mag => (
                                                <div key={mag.id} className="arrival-item magazine">
                                                    <strong>{mag.title}</strong>
                                                    <span className="badge">Issue #{mag.issue_number}</span>
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    {/* Products List */}
                                    {newArrivals.products.length > 0 && (
                                        <div className="arrivals-list">
                                            <h4>🛒 Products</h4>
                                            {newArrivals.products.map(prod => (
                                                <div key={prod.id} className="arrival-item product">
                                                    <strong>{prod.name}</strong>
                                                    <span className="price">₹{prod.price}</span>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Preview Button */}
                            <button className="preview-btn" onClick={previewEmail} disabled={loading}>
                                👁️ Preview Email
                            </button>
                        </>
                    ) : (
                        /* Custom Email Form */
                        <div className="custom-email-form">
                            <h3>✏️ Compose Custom Email</h3>

                            <div className="form-group">
                                <label>Subject *</label>
                                <input
                                    type="text"
                                    value={customEmail.subject}
                                    onChange={(e) => setCustomEmail({ ...customEmail, subject: e.target.value })}
                                    placeholder="Enter email subject..."
                                />
                            </div>

                            <div className="form-group">
                                <label>Heading *</label>
                                <input
                                    type="text"
                                    value={customEmail.heading}
                                    onChange={(e) => setCustomEmail({ ...customEmail, heading: e.target.value })}
                                    placeholder="Main heading in the email..."
                                />
                            </div>

                            <div className="form-group">
                                <label>Content * (HTML supported)</label>
                                <textarea
                                    value={customEmail.content}
                                    onChange={(e) => setCustomEmail({ ...customEmail, content: e.target.value })}
                                    placeholder="Write your email content here... You can use HTML tags."
                                    rows={6}
                                />
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label>Button Text</label>
                                    <input
                                        type="text"
                                        value={customEmail.ctaText}
                                        onChange={(e) => setCustomEmail({ ...customEmail, ctaText: e.target.value })}
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Button URL</label>
                                    <input
                                        type="text"
                                        value={customEmail.ctaUrl}
                                        onChange={(e) => setCustomEmail({ ...customEmail, ctaUrl: e.target.value })}
                                    />
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Right Column - Recipients */}
                <div className="recipients-column">
                    <div className="recipients-header">
                        <h3>👥 Recipients ({selectedEmails.length} selected)</h3>
                        <button className="select-all-btn" onClick={selectAllEmails}>
                            {selectedEmails.length === subscribers.length ? 'Deselect All' : 'Select All'}
                        </button>
                    </div>

                    <div className="subscribers-list">
                        {subscribers.map(sub => (
                            <label key={sub.id} className="subscriber-item">
                                <input
                                    type="checkbox"
                                    checked={selectedEmails.includes(sub.email)}
                                    onChange={() => toggleEmailSelection(sub.email)}
                                />
                                <div className="subscriber-info">
                                    <span className="name">{sub.full_name || sub.username}</span>
                                    <span className="email">{sub.email}</span>
                                </div>
                            </label>
                        ))}
                    </div>

                    {/* Send Buttons */}
                    <div className="send-actions">
                        <button
                            className="send-btn primary"
                            onClick={activeTab === 'weekly' ? sendWeeklyArrivalsEmail : sendCustomEmail}
                            disabled={loading || selectedEmails.length === 0}
                        >
                            {loading ? '⏳ Sending...' : `📤 Send to ${selectedEmails.length} Selected`}
                        </button>

                        {activeTab === 'weekly' && (
                            <button
                                className="send-btn danger"
                                onClick={sendToAllUsers}
                                disabled={loading}
                            >
                                🚀 Send to All Users ({subscribers.length})
                            </button>
                        )}
                    </div>
                </div>
            </div>

            {/* Email Preview Modal */}
            {showPreview && (
                <div className="preview-modal-overlay" onClick={() => setShowPreview(false)}>
                    <div className="preview-modal" onClick={(e) => e.stopPropagation()}>
                        <div className="preview-header">
                            <h3>📧 Email Preview</h3>
                            <button className="close-btn" onClick={() => setShowPreview(false)}>×</button>
                        </div>
                        <div className="preview-content">
                            <iframe
                                srcDoc={previewHtml}
                                title="Email Preview"
                                style={{ width: '100%', height: '600px', border: 'none' }}
                            />
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AdminPromotionalEmailPage;
