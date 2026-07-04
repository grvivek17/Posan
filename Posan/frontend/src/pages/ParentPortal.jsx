import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { usersAPI } from '../services/api';
import './ProfilePage.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

/* inline style constants */
const styles = {
    page: {
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 100%)',
        paddingBottom: '3rem',
    },
    header: {
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '2rem 1.5rem 2.5rem',
        borderRadius: '0 0 32px 32px',
        color: '#fff',
        textAlign: 'center',
        boxShadow: '0 8px 32px rgba(102,126,234,0.35)',
        position: 'relative',
    },
    headerBack: {
        position: 'absolute',
        top: '1.25rem',
        left: '1.25rem',
        background: 'rgba(255,255,255,0.2)',
        border: 'none',
        borderRadius: '50%',
        width: 40,
        height: 40,
        fontSize: '1.3rem',
        color: '#fff',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
    },
    headerTitle: {
        fontSize: '1.8rem',
        fontWeight: 800,
        margin: 0,
    },
    headerSub: {
        opacity: 0.85,
        marginTop: 4,
        fontSize: '1rem',
    },
    container: {
        maxWidth: 900,
        margin: '0 auto',
        padding: '0 1rem',
    },
    tabBar: {
        display: 'flex',
        gap: 8,
        overflowX: 'auto',
        padding: '1.25rem 0 0.5rem',
        marginBottom: '0.5rem',
    },
    tab: (active) => ({
        padding: '10px 20px',
        borderRadius: 24,
        border: 'none',
        fontWeight: 700,
        fontSize: '0.9rem',
        cursor: 'pointer',
        whiteSpace: 'nowrap',
        transition: 'all 0.25s ease',
        background: active ? 'linear-gradient(135deg, #667eea, #764ba2)' : '#fff',
        color: active ? '#fff' : '#555',
        boxShadow: active ? '0 4px 14px rgba(102,126,234,0.4)' : '0 2px 8px rgba(0,0,0,0.06)',
    }),
    section: {
        background: '#fff',
        borderRadius: 20,
        padding: '1.5rem',
        marginBottom: '1.25rem',
        boxShadow: '0 4px 20px rgba(0,0,0,0.06)',
    },
    sectionTitle: {
        fontSize: '1.25rem',
        fontWeight: 700,
        marginBottom: '1rem',
        color: '#1a1a2e',
    },
    childCard: {
        display: 'flex',
        alignItems: 'center',
        gap: 14,
        padding: '14px 16px',
        background: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
        borderRadius: 16,
        marginBottom: 12,
        boxShadow: '0 3px 12px rgba(252,182,159,0.35)',
        cursor: 'pointer',
        transition: 'transform 0.2s ease, box-shadow 0.2s ease',
    },
    childAvatar: {
        width: 52,
        height: 52,
        background: '#fff',
        borderRadius: '50%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '1.8rem',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        flexShrink: 0,
    },
    childInfo: { flex: 1 },
    childName: {
        fontWeight: 700,
        fontSize: '1.05rem',
        color: '#1a1a2e',
        margin: 0,
    },
    childMeta: {
        fontSize: '0.85rem',
        color: '#555',
        margin: 0,
        marginTop: 2,
    },
    childArrow: { fontSize: '1.2rem', color: '#999' },
    formGroup: { marginBottom: 14 },
    label: {
        display: 'block',
        fontWeight: 600,
        fontSize: '0.9rem',
        color: '#333',
        marginBottom: 6,
    },
    input: {
        width: '100%',
        padding: '12px 14px',
        border: '2px solid #e8e8e8',
        borderRadius: 12,
        fontSize: '1rem',
        outline: 'none',
        transition: 'border-color 0.2s',
        boxSizing: 'border-box',
    },
    select: {
        width: '100%',
        padding: '12px 14px',
        border: '2px solid #e8e8e8',
        borderRadius: 12,
        fontSize: '1rem',
        outline: 'none',
        background: '#fff',
        cursor: 'pointer',
        boxSizing: 'border-box',
    },
    btnPrimary: {
        background: 'linear-gradient(135deg, #667eea, #764ba2)',
        color: '#fff',
        border: 'none',
        borderRadius: 14,
        padding: '12px 28px',
        fontSize: '1rem',
        fontWeight: 700,
        cursor: 'pointer',
        transition: 'transform 0.2s, box-shadow 0.2s',
        boxShadow: '0 4px 14px rgba(102,126,234,0.4)',
        width: '100%',
    },
    btnSecondary: {
        background: '#f0f0f5',
        color: '#555',
        border: 'none',
        borderRadius: 14,
        padding: '12px 28px',
        fontSize: '1rem',
        fontWeight: 600,
        cursor: 'pointer',
        width: '100%',
        marginTop: 8,
    },
    btnAdd: {
        background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
        color: '#1a1a2e',
        border: 'none',
        borderRadius: 14,
        padding: '12px 20px',
        fontSize: '0.95rem',
        fontWeight: 700,
        cursor: 'pointer',
        width: '100%',
        boxShadow: '0 4px 14px rgba(67,233,123,0.3)',
        transition: 'transform 0.2s',
    },
    statsGrid: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))',
        gap: 12,
    },
    statCard: (bg) => ({
        background: bg,
        borderRadius: 16,
        padding: '16px 14px',
        textAlign: 'center',
        boxShadow: '0 3px 12px rgba(0,0,0,0.08)',
    }),
    statEmoji: { fontSize: '1.6rem', marginBottom: 4 },
    statValue: {
        fontSize: '1.4rem',
        fontWeight: 800,
        color: '#1a1a2e',
        margin: 0,
    },
    statLabel: {
        fontSize: '0.78rem',
        color: '#666',
        margin: 0,
        marginTop: 2,
        fontWeight: 600,
    },
    activityRow: {
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        padding: '12px 0',
        borderBottom: '1px solid #f0f0f5',
    },
    activityIcon: {
        width: 42,
        height: 42,
        borderRadius: 12,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '1.3rem',
        flexShrink: 0,
    },
    loader: { textAlign: 'center', padding: '3rem 1rem' },
    spinner: {
        width: 48,
        height: 48,
        border: '4px solid #e8e8e8',
        borderTopColor: '#667eea',
        borderRadius: '50%',
        animation: 'spin 0.8s linear infinite',
        margin: '0 auto 1rem',
    },
    errorBox: {
        background: '#fff0f0',
        border: '1px solid #ffcdd2',
        borderRadius: 16,
        padding: '1.5rem',
        textAlign: 'center',
        margin: '2rem 0',
    },
    emptyState: {
        textAlign: 'center',
        padding: '2rem 1rem',
        color: '#999',
    },
    settingsRow: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '14px 0',
        borderBottom: '1px solid #f0f0f5',
        gap: 12,
    },
    settingsLabel: {
        fontWeight: 600,
        fontSize: '0.95rem',
        color: '#333',
    },
    badge: (color) => ({
        display: 'inline-block',
        background: color,
        color: '#fff',
        padding: '4px 12px',
        borderRadius: 20,
        fontSize: '0.78rem',
        fontWeight: 700,
    }),
    childSelector: {
        display: 'flex',
        gap: 8,
        overflowX: 'auto',
        paddingBottom: 8,
        marginBottom: 12,
    },
    childChip: (active) => ({
        padding: '8px 16px',
        borderRadius: 20,
        border: 'none',
        fontWeight: 600,
        fontSize: '0.85rem',
        cursor: 'pointer',
        whiteSpace: 'nowrap',
        background: active ? '#667eea' : '#f0f0f5',
        color: active ? '#fff' : '#555',
        transition: 'all 0.2s',
    }),
};

/* keyframe for spinner - injected once */
const spinnerCSS = `@keyframes spin{to{transform:rotate(360deg)}}`;
if (typeof document !== 'undefined' && !document.getElementById('pp-spin')) {
    const s = document.createElement('style');
    s.id = 'pp-spin';
    s.textContent = spinnerCSS;
    document.head.appendChild(s);
}

/* helpers */
const avatarForChild = (child) => {
    const avatars = ['👦', '👧', '🧒', '👶', '🧒🏽', '👦🏻', '👧🏾'];
    if (child?.gender === 'female') return '👧';
    if (child?.gender === 'male') return '👦';
    const idx = (child?.id || 0) % avatars.length;
    return avatars[idx];
};

const ageGroupLabel = (age) => {
    if (!age) return 'Not set';
    if (age <= 5) return '3-5 yrs (Pre-K)';
    if (age <= 8) return '6-8 yrs (Early Reader)';
    if (age <= 11) return '9-11 yrs (Explorer)';
    return '12+ yrs (Tween)';
};

const STAT_COLORS = [
    'linear-gradient(135deg, #ffecd2, #fcb69f)',
    'linear-gradient(135deg, #a1c4fd, #c2e9fb)',
    'linear-gradient(135deg, #d4fc79, #96e6a1)',
    'linear-gradient(135deg, #fbc2eb, #a6c1ee)',
    'linear-gradient(135deg, #fdcbf1, #e6dee9)',
    'linear-gradient(135deg, #f6d365, #fda085)',
];

function ParentPortal() {
    const navigate = useNavigate();

    const [activeTab, setActiveTab] = useState('children');
    const [children, setChildren] = useState([]);
    const [childStats, setChildStats] = useState({});
    const [selectedChildId, setSelectedChildId] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [parentUser, setParentUser] = useState(null);

    // Add child form
    const [showAddForm, setShowAddForm] = useState(false);
    const [addForm, setAddForm] = useState({ username: '', age: '', gender: '' });
    const [addLoading, setAddLoading] = useState(false);
    const [addError, setAddError] = useState(null);

    // Edit child settings
    const [editingChild, setEditingChild] = useState(null);
    const [editForm, setEditForm] = useState({ age: '', gender: '', age_group: '' });
    const [editLoading, setEditLoading] = useState(false);

    // Recent activity
    const [recentActivity, setRecentActivity] = useState([]);
    const [activityLoading, setActivityLoading] = useState(false);

    const parentUserId = localStorage.getItem('user_id');
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');

    const fetchStatsForChildren = async (childList) => {
        const statsMap = {};
        await Promise.all(
            childList.map(async (child) => {
                const childId = child.id || child.user_id;
                try {
                    const res = await axios.get(`${API_BASE}/gamification-v2/stats`, {
                        params: { user_id: childId },
                        headers: { Authorization: `Bearer ${token}` },
                    });
                    statsMap[childId] = res.data;
                } catch {
                    statsMap[childId] = null;
                }
            })
        );
        setChildStats(statsMap);
    };

    const fetchChildren = useCallback(async () => {
        if (!parentUserId) {
            setError('Please log in to access the Parent Portal.');
            setLoading(false);
            return;
        }
        try {
            setLoading(true);
            setError(null);

            try {
                const userRes = await usersAPI.getCurrentUser(parentUserId);
                setParentUser(userRes.data);
            } catch {
                // non-critical
            }

            const childRes = await usersAPI.getChildProfiles(parentUserId);
            const childList = Array.isArray(childRes.data) ? childRes.data : (childRes.data?.children || []);
            setChildren(childList);

            if (childList.length > 0 && !selectedChildId) {
                setSelectedChildId(childList[0].id || childList[0].user_id);
            }

            await fetchStatsForChildren(childList);
        } catch (err) {
            console.error('Error loading children:', err);
            setError('Failed to load child profiles. Please try again.');
        } finally {
            setLoading(false);
        }
    }, [parentUserId]);

    const fetchRecentActivity = useCallback(async () => {
        if (!token) return;
        setActivityLoading(true);
        try {
            const res = await axios.get(`${API_BASE}/admin/activity/recent`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            setRecentActivity(Array.isArray(res.data) ? res.data : (res.data?.activities || []));
        } catch {
            setRecentActivity([]);
        } finally {
            setActivityLoading(false);
        }
    }, [token]);

    useEffect(() => {
        fetchChildren();
    }, [fetchChildren]);

    useEffect(() => {
        if (activeTab === 'activity') {
            fetchRecentActivity();
        }
    }, [activeTab, fetchRecentActivity]);

    /* add child */
    const handleAddChild = async (e) => {
        e.preventDefault();
        if (!addForm.username.trim()) {
            setAddError('Please enter a username.');
            return;
        }
        setAddLoading(true);
        setAddError(null);
        try {
            await usersAPI.createChildProfile(parentUserId, 0, {
                username: addForm.username.trim(),
                age: addForm.age ? parseInt(addForm.age) : undefined,
                gender: addForm.gender || undefined,
            });
            setAddForm({ username: '', age: '', gender: '' });
            setShowAddForm(false);
            await fetchChildren();
        } catch (err) {
            console.error('Error adding child:', err);
            setAddError(err.response?.data?.detail || 'Failed to add child profile.');
        } finally {
            setAddLoading(false);
        }
    };

    /* edit child settings */
    const startEditing = (child) => {
        setEditingChild(child);
        setEditForm({
            age: child.age || '',
            gender: child.gender || '',
            age_group: child.age_group || '',
        });
    };

    const handleSaveSettings = async (e) => {
        e.preventDefault();
        const childId = editingChild.id || editingChild.user_id;
        setEditLoading(true);
        try {
            await usersAPI.updateChildProfile(childId, {
                age: editForm.age ? parseInt(editForm.age) : undefined,
                gender: editForm.gender || undefined,
                age_group: editForm.age_group || undefined,
            });
            setEditingChild(null);
            await fetchChildren();
        } catch (err) {
            console.error('Error updating child:', err);
            alert(err.response?.data?.detail || 'Failed to update child profile.');
        } finally {
            setEditLoading(false);
        }
    };

    /* derived */
    const selectedChild = children.find(
        (c) => (c.id || c.user_id) === selectedChildId
    );
    const selectedStats = selectedChildId ? childStats[selectedChildId] : null;

    const TABS = [
        { key: 'children', label: 'My Children' },
        { key: 'overview', label: 'Activity Overview' },
        { key: 'activity', label: 'Usage Summary' },
        { key: 'settings', label: 'Content Settings' },
    ];

    /* renders */

    const renderLoading = () => (
        <div style={styles.loader}>
            <div style={styles.spinner} />
            <p style={{ color: '#667eea', fontWeight: 600 }}>Loading Parent Portal...</p>
        </div>
    );

    const renderError = () => (
        <div style={styles.container}>
            <div style={styles.errorBox}>
                <h3 style={{ color: '#c62828', margin: '0.5rem 0' }}>{error}</h3>
                <button
                    style={{ ...styles.btnPrimary, width: 'auto', marginTop: 12 }}
                    onClick={() => { setError(null); fetchChildren(); }}
                >
                    Try Again
                </button>
            </div>
        </div>
    );

    /* Stat cards reusable */
    const renderStatCards = (stats) => {
        if (!stats) {
            return <p style={styles.emptyState}>No stats available yet. Start exploring to earn points!</p>;
        }
        const items = [
            { emoji: 'Points', value: stats.total_points ?? stats.points ?? 0, label: 'Total Points' },
            { emoji: 'Badges', value: stats.badges_earned ?? stats.badges?.length ?? 0, label: 'Badges' },
            { emoji: 'Puzzles', value: stats.puzzles_completed ?? stats.puzzles_solved ?? 0, label: 'Puzzles' },
            { emoji: 'Reading', value: stats.articles_read ?? 0, label: 'Articles Read' },
            { emoji: 'Streak', value: stats.current_streak ?? stats.streak ?? 0, label: 'Day Streak' },
            { emoji: 'Level', value: stats.level ?? stats.current_level ?? 1, label: 'Level' },
        ];
        return (
            <div style={styles.statsGrid}>
                {items.map((item, i) => (
                    <div key={i} style={styles.statCard(STAT_COLORS[i % STAT_COLORS.length])}>
                        <div style={styles.statEmoji}>{item.emoji}</div>
                        <p style={styles.statValue}>{item.value}</p>
                        <p style={styles.statLabel}>{item.label}</p>
                    </div>
                ))}
            </div>
        );
    };

    /* Tab: My Children */
    const renderChildren = () => (
        <>
            <div style={styles.section}>
                <h2 style={styles.sectionTitle}>My Children</h2>

                {children.length === 0 && (
                    <div style={styles.emptyState}>
                        <p style={{ fontWeight: 600, color: '#555' }}>No child profiles yet!</p>
                        <p style={{ fontSize: '0.9rem' }}>Add your first child below to start tracking their learning journey.</p>
                    </div>
                )}

                {children.map((child) => {
                    const id = child.id || child.user_id;
                    return (
                        <div
                            key={id}
                            style={styles.childCard}
                            onClick={() => setSelectedChildId(id)}
                            onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-2px)'; }}
                            onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; }}
                        >
                            <div style={styles.childAvatar}>{avatarForChild(child)}</div>
                            <div style={styles.childInfo}>
                                <p style={styles.childName}>{child.username || child.name || `Child #${id}`}</p>
                                <p style={styles.childMeta}>
                                    {child.age ? `Age ${child.age}` : 'Age not set'} &middot; {ageGroupLabel(child.age)}
                                </p>
                            </div>
                            <span style={styles.childArrow}>&#9654;</span>
                        </div>
                    );
                })}

                {!showAddForm ? (
                    <button
                        style={styles.btnAdd}
                        onClick={() => setShowAddForm(true)}
                        onMouseEnter={(e) => { e.currentTarget.style.transform = 'scale(1.02)'; }}
                        onMouseLeave={(e) => { e.currentTarget.style.transform = 'scale(1)'; }}
                    >
                        + Add a Child
                    </button>
                ) : (
                    <form onSubmit={handleAddChild} style={{ marginTop: 8 }}>
                        <h3 style={{ ...styles.sectionTitle, fontSize: '1.05rem' }}>New Child Profile</h3>

                        {addError && (
                            <p style={{ color: '#c62828', fontSize: '0.9rem', marginBottom: 10 }}>{addError}</p>
                        )}

                        <div style={styles.formGroup}>
                            <label style={styles.label}>Username *</label>
                            <input
                                style={styles.input}
                                type="text"
                                placeholder="e.g. SuperReader123"
                                value={addForm.username}
                                onChange={(e) => setAddForm({ ...addForm, username: e.target.value })}
                                onFocus={(e) => { e.target.style.borderColor = '#667eea'; }}
                                onBlur={(e) => { e.target.style.borderColor = '#e8e8e8'; }}
                                required
                            />
                        </div>
                        <div style={styles.formGroup}>
                            <label style={styles.label}>Age</label>
                            <input
                                style={styles.input}
                                type="number"
                                min="3"
                                max="18"
                                placeholder="e.g. 8"
                                value={addForm.age}
                                onChange={(e) => setAddForm({ ...addForm, age: e.target.value })}
                                onFocus={(e) => { e.target.style.borderColor = '#667eea'; }}
                                onBlur={(e) => { e.target.style.borderColor = '#e8e8e8'; }}
                            />
                        </div>
                        <div style={styles.formGroup}>
                            <label style={styles.label}>Gender (optional)</label>
                            <select
                                style={styles.select}
                                value={addForm.gender}
                                onChange={(e) => setAddForm({ ...addForm, gender: e.target.value })}
                            >
                                <option value="">Prefer not to say</option>
                                <option value="male">Male</option>
                                <option value="female">Female</option>
                                <option value="other">Other</option>
                            </select>
                        </div>
                        <button
                            type="submit"
                            style={{ ...styles.btnPrimary, opacity: addLoading ? 0.7 : 1 }}
                            disabled={addLoading}
                        >
                            {addLoading ? 'Adding...' : 'Add Child'}
                        </button>
                        <button
                            type="button"
                            style={styles.btnSecondary}
                            onClick={() => { setShowAddForm(false); setAddError(null); }}
                        >
                            Cancel
                        </button>
                    </form>
                )}
            </div>

            {selectedChild && selectedStats && (
                <div style={styles.section}>
                    <h2 style={styles.sectionTitle}>
                        {avatarForChild(selectedChild)} {selectedChild.username || selectedChild.name}'s Quick Stats
                    </h2>
                    {renderStatCards(selectedStats)}
                </div>
            )}
        </>
    );

    /* Tab: Activity Overview */
    const renderOverview = () => (
        <>
            {children.length === 0 ? (
                <div style={{ ...styles.section, ...styles.emptyState }}>
                    <p style={{ fontWeight: 600 }}>Add children first to see their activity overview.</p>
                </div>
            ) : (
                <>
                    <div style={styles.childSelector}>
                        {children.map((child) => {
                            const id = child.id || child.user_id;
                            return (
                                <button
                                    key={id}
                                    style={styles.childChip(selectedChildId === id)}
                                    onClick={() => setSelectedChildId(id)}
                                >
                                    {avatarForChild(child)} {child.username || child.name || `Child #${id}`}
                                </button>
                            );
                        })}
                    </div>

                    {selectedChild && (
                        <div style={styles.section}>
                            <h2 style={styles.sectionTitle}>
                                {selectedChild.username || selectedChild.name}'s Activity Overview
                            </h2>
                            {renderStatCards(selectedStats)}

                            {selectedStats && (
                                <div style={{ marginTop: '1.5rem' }}>
                                    <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 10, color: '#333' }}>
                                        Achievements Progress
                                    </h3>
                                    <div style={{
                                        background: '#f7f7fb',
                                        borderRadius: 14,
                                        padding: '16px',
                                    }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                                            <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>
                                                Level {selectedStats.level ?? selectedStats.current_level ?? 1}
                                            </span>
                                            <span style={{ fontSize: '0.85rem', color: '#888' }}>
                                                {selectedStats.points_to_next_level ?? '?'} pts to next level
                                            </span>
                                        </div>
                                        <div style={{
                                            height: 12,
                                            background: '#e8e8e8',
                                            borderRadius: 10,
                                            overflow: 'hidden',
                                        }}>
                                            <div style={{
                                                height: '100%',
                                                width: `${Math.min(100, selectedStats.level_progress ?? 50)}%`,
                                                background: 'linear-gradient(90deg, #667eea, #764ba2)',
                                                borderRadius: 10,
                                                transition: 'width 0.6s ease',
                                            }} />
                                        </div>
                                    </div>

                                    {selectedStats.badges && selectedStats.badges.length > 0 && (
                                        <div style={{ marginTop: '1rem' }}>
                                            <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 8, color: '#333' }}>
                                                Earned Badges
                                            </h3>
                                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                                                {selectedStats.badges.map((badge, i) => (
                                                    <span key={i} style={styles.badge('#667eea')}>
                                                        {badge.icon || ''} {badge.name || badge}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    )}

                    {children.length > 1 && (
                        <div style={styles.section}>
                            <h2 style={styles.sectionTitle}>All Children Comparison</h2>
                            <div style={{ overflowX: 'auto' }}>
                                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                                    <thead>
                                        <tr style={{ borderBottom: '2px solid #e8e8e8' }}>
                                            <th style={{ textAlign: 'left', padding: '10px 8px', fontWeight: 700 }}>Child</th>
                                            <th style={{ textAlign: 'center', padding: '10px 8px' }}>Points</th>
                                            <th style={{ textAlign: 'center', padding: '10px 8px' }}>Badges</th>
                                            <th style={{ textAlign: 'center', padding: '10px 8px' }}>Puzzles</th>
                                            <th style={{ textAlign: 'center', padding: '10px 8px' }}>Level</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {children.map((child) => {
                                            const id = child.id || child.user_id;
                                            const st = childStats[id];
                                            return (
                                                <tr key={id} style={{ borderBottom: '1px solid #f0f0f5' }}>
                                                    <td style={{ padding: '10px 8px', fontWeight: 600 }}>
                                                        {avatarForChild(child)} {child.username || child.name}
                                                    </td>
                                                    <td style={{ textAlign: 'center', padding: '10px 8px' }}>
                                                        {st?.total_points ?? st?.points ?? '-'}
                                                    </td>
                                                    <td style={{ textAlign: 'center', padding: '10px 8px' }}>
                                                        {st?.badges_earned ?? st?.badges?.length ?? '-'}
                                                    </td>
                                                    <td style={{ textAlign: 'center', padding: '10px 8px' }}>
                                                        {st?.puzzles_completed ?? st?.puzzles_solved ?? '-'}
                                                    </td>
                                                    <td style={{ textAlign: 'center', padding: '10px 8px' }}>
                                                        {st?.level ?? st?.current_level ?? '-'}
                                                    </td>
                                                </tr>
                                            );
                                        })}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}
                </>
            )}
        </>
    );

    /* Tab: Usage Summary */
    const renderUsageSummary = () => (
        <>
            {children.length === 0 ? (
                <div style={{ ...styles.section, ...styles.emptyState }}>
                    <p style={{ fontWeight: 600 }}>Add children first to see usage data.</p>
                </div>
            ) : (
                <>
                    <div style={styles.childSelector}>
                        {children.map((child) => {
                            const id = child.id || child.user_id;
                            return (
                                <button
                                    key={id}
                                    style={styles.childChip(selectedChildId === id)}
                                    onClick={() => setSelectedChildId(id)}
                                >
                                    {avatarForChild(child)} {child.username || child.name || `Child #${id}`}
                                </button>
                            );
                        })}
                    </div>

                    {selectedChild && (
                        <div style={styles.section}>
                            <h2 style={styles.sectionTitle}>
                                {selectedChild.username || selectedChild.name}'s Usage Summary
                            </h2>

                            {selectedStats ? (
                                <div>
                                    <div style={styles.activityRow}>
                                        <div style={{ ...styles.activityIcon, background: 'linear-gradient(135deg, #a1c4fd, #c2e9fb)' }}>P</div>
                                        <div style={{ flex: 1 }}>
                                            <p style={{ margin: 0, fontWeight: 600, fontSize: '0.95rem' }}>Puzzles Completed</p>
                                            <p style={{ margin: 0, fontSize: '0.82rem', color: '#888' }}>Brain training activities</p>
                                        </div>
                                        <span style={{ fontWeight: 700, fontSize: '1.1rem', color: '#667eea' }}>
                                            {selectedStats.puzzles_completed ?? selectedStats.puzzles_solved ?? 0}
                                        </span>
                                    </div>
                                    <div style={styles.activityRow}>
                                        <div style={{ ...styles.activityIcon, background: 'linear-gradient(135deg, #d4fc79, #96e6a1)' }}>R</div>
                                        <div style={{ flex: 1 }}>
                                            <p style={{ margin: 0, fontWeight: 600, fontSize: '0.95rem' }}>Articles Read</p>
                                            <p style={{ margin: 0, fontSize: '0.82rem', color: '#888' }}>Reading and learning</p>
                                        </div>
                                        <span style={{ fontWeight: 700, fontSize: '1.1rem', color: '#43a047' }}>
                                            {selectedStats.articles_read ?? 0}
                                        </span>
                                    </div>
                                    <div style={styles.activityRow}>
                                        <div style={{ ...styles.activityIcon, background: 'linear-gradient(135deg, #ffecd2, #fcb69f)' }}>S</div>
                                        <div style={{ flex: 1 }}>
                                            <p style={{ margin: 0, fontWeight: 600, fontSize: '0.95rem' }}>Login Streak</p>
                                            <p style={{ margin: 0, fontSize: '0.82rem', color: '#888' }}>Consecutive days active</p>
                                        </div>
                                        <span style={{ fontWeight: 700, fontSize: '1.1rem', color: '#ef6c00' }}>
                                            {selectedStats.current_streak ?? selectedStats.streak ?? 0} days
                                        </span>
                                    </div>
                                    <div style={styles.activityRow}>
                                        <div style={{ ...styles.activityIcon, background: 'linear-gradient(135deg, #fbc2eb, #a6c1ee)' }}>Pt</div>
                                        <div style={{ flex: 1 }}>
                                            <p style={{ margin: 0, fontWeight: 600, fontSize: '0.95rem' }}>Total Points Earned</p>
                                            <p style={{ margin: 0, fontSize: '0.82rem', color: '#888' }}>Overall score</p>
                                        </div>
                                        <span style={{ fontWeight: 700, fontSize: '1.1rem', color: '#8e24aa' }}>
                                            {selectedStats.total_points ?? selectedStats.points ?? 0}
                                        </span>
                                    </div>
                                    <div style={{ ...styles.activityRow, borderBottom: 'none' }}>
                                        <div style={{ ...styles.activityIcon, background: 'linear-gradient(135deg, #f6d365, #fda085)' }}>Q</div>
                                        <div style={{ flex: 1 }}>
                                            <p style={{ margin: 0, fontWeight: 600, fontSize: '0.95rem' }}>Quizzes Completed</p>
                                            <p style={{ margin: 0, fontSize: '0.82rem', color: '#888' }}>Knowledge tests</p>
                                        </div>
                                        <span style={{ fontWeight: 700, fontSize: '1.1rem', color: '#f57c00' }}>
                                            {selectedStats.quizzes_completed ?? 0}
                                        </span>
                                    </div>
                                </div>
                            ) : (
                                <div style={styles.emptyState}>
                                    <p>No activity data available yet.</p>
                                </div>
                            )}
                        </div>
                    )}

                    {recentActivity.length > 0 && (
                        <div style={styles.section}>
                            <h2 style={styles.sectionTitle}>Recent Activity Feed</h2>
                            {recentActivity.slice(0, 10).map((act, i) => (
                                <div key={i} style={{ ...styles.activityRow, borderBottom: i < 9 ? '1px solid #f0f0f5' : 'none' }}>
                                    <div style={{
                                        ...styles.activityIcon,
                                        background: STAT_COLORS[i % STAT_COLORS.length],
                                    }}>
                                        {act.activity_type === 'puzzle_solved' ? 'P'
                                            : act.activity_type === 'article_read' ? 'R'
                                            : act.activity_type === 'quiz_completed' ? 'Q'
                                            : act.activity_type === 'daily_login' ? 'L'
                                            : 'A'}
                                    </div>
                                    <div style={{ flex: 1 }}>
                                        <p style={{ margin: 0, fontWeight: 600, fontSize: '0.9rem' }}>
                                            {act.activity_type?.replace(/_/g, ' ') || 'Activity'}
                                        </p>
                                        <p style={{ margin: 0, fontSize: '0.8rem', color: '#999' }}>
                                            {act.created_at ? new Date(act.created_at).toLocaleString() : ''}
                                        </p>
                                    </div>
                                    {act.points_earned && (
                                        <span style={styles.badge('#43e97b')}>+{act.points_earned} pts</span>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}

                    {activityLoading && (
                        <div style={styles.loader}>
                            <div style={styles.spinner} />
                            <p style={{ color: '#888', fontSize: '0.9rem' }}>Loading activity...</p>
                        </div>
                    )}
                </>
            )}
        </>
    );

    /* Tab: Content Settings */
    const renderSettings = () => (
        <>
            {children.length === 0 ? (
                <div style={{ ...styles.section, ...styles.emptyState }}>
                    <p style={{ fontWeight: 600 }}>Add children first to manage their settings.</p>
                </div>
            ) : (
                <>
                    <div style={styles.childSelector}>
                        {children.map((child) => {
                            const id = child.id || child.user_id;
                            return (
                                <button
                                    key={id}
                                    style={styles.childChip(selectedChildId === id)}
                                    onClick={() => { setSelectedChildId(id); setEditingChild(null); }}
                                >
                                    {avatarForChild(child)} {child.username || child.name || `Child #${id}`}
                                </button>
                            );
                        })}
                    </div>

                    {selectedChild && !editingChild && (
                        <div style={styles.section}>
                            <h2 style={styles.sectionTitle}>
                                {selectedChild.username || selectedChild.name}'s Settings
                            </h2>

                            <div style={styles.settingsRow}>
                                <span style={styles.settingsLabel}>Username</span>
                                <span style={{ color: '#555' }}>{selectedChild.username || selectedChild.name || '-'}</span>
                            </div>
                            <div style={styles.settingsRow}>
                                <span style={styles.settingsLabel}>Age</span>
                                <span style={{ color: '#555' }}>{selectedChild.age || 'Not set'}</span>
                            </div>
                            <div style={styles.settingsRow}>
                                <span style={styles.settingsLabel}>Age Group</span>
                                <span style={styles.badge('#667eea')}>{ageGroupLabel(selectedChild.age)}</span>
                            </div>
                            <div style={styles.settingsRow}>
                                <span style={styles.settingsLabel}>Gender</span>
                                <span style={{ color: '#555', textTransform: 'capitalize' }}>
                                    {selectedChild.gender || 'Not set'}
                                </span>
                            </div>
                            <div style={{ ...styles.settingsRow, borderBottom: 'none' }}>
                                <span style={styles.settingsLabel}>Content Preferences</span>
                                <span style={styles.badge('#43e97b')}>
                                    {selectedChild.age_group || ageGroupLabel(selectedChild.age)}
                                </span>
                            </div>

                            <button
                                style={{ ...styles.btnPrimary, marginTop: '1rem' }}
                                onClick={() => startEditing(selectedChild)}
                                onMouseEnter={(e) => { e.currentTarget.style.transform = 'scale(1.02)'; }}
                                onMouseLeave={(e) => { e.currentTarget.style.transform = 'scale(1)'; }}
                            >
                                Edit Settings
                            </button>
                        </div>
                    )}

                    {editingChild && (
                        <div style={styles.section}>
                            <h2 style={styles.sectionTitle}>
                                Edit {editingChild.username || editingChild.name}'s Settings
                            </h2>
                            <form onSubmit={handleSaveSettings}>
                                <div style={styles.formGroup}>
                                    <label style={styles.label}>Age</label>
                                    <input
                                        style={styles.input}
                                        type="number"
                                        min="3"
                                        max="18"
                                        placeholder="e.g. 8"
                                        value={editForm.age}
                                        onChange={(e) => setEditForm({ ...editForm, age: e.target.value })}
                                        onFocus={(e) => { e.target.style.borderColor = '#667eea'; }}
                                        onBlur={(e) => { e.target.style.borderColor = '#e8e8e8'; }}
                                    />
                                </div>
                                <div style={styles.formGroup}>
                                    <label style={styles.label}>Gender</label>
                                    <select
                                        style={styles.select}
                                        value={editForm.gender}
                                        onChange={(e) => setEditForm({ ...editForm, gender: e.target.value })}
                                    >
                                        <option value="">Prefer not to say</option>
                                        <option value="male">Male</option>
                                        <option value="female">Female</option>
                                        <option value="other">Other</option>
                                    </select>
                                </div>
                                <div style={styles.formGroup}>
                                    <label style={styles.label}>Age Group / Content Level</label>
                                    <select
                                        style={styles.select}
                                        value={editForm.age_group}
                                        onChange={(e) => setEditForm({ ...editForm, age_group: e.target.value })}
                                    >
                                        <option value="">Auto (based on age)</option>
                                        <option value="3-5">3-5 yrs (Pre-K)</option>
                                        <option value="6-8">6-8 yrs (Early Reader)</option>
                                        <option value="9-11">9-11 yrs (Explorer)</option>
                                        <option value="12+">12+ yrs (Tween)</option>
                                    </select>
                                </div>
                                <button
                                    type="submit"
                                    style={{ ...styles.btnPrimary, opacity: editLoading ? 0.7 : 1 }}
                                    disabled={editLoading}
                                >
                                    {editLoading ? 'Saving...' : 'Save Changes'}
                                </button>
                                <button
                                    type="button"
                                    style={styles.btnSecondary}
                                    onClick={() => setEditingChild(null)}
                                >
                                    Cancel
                                </button>
                            </form>
                        </div>
                    )}
                </>
            )}
        </>
    );

    /* Main render */
    if (loading) return <div style={styles.page}>{renderLoading()}</div>;
    if (error && children.length === 0) return <div style={styles.page}>{renderError()}</div>;

    return (
        <div style={styles.page}>
            <div style={styles.header}>
                <button style={styles.headerBack} onClick={() => navigate(-1)} title="Go back">
                    &#8592;
                </button>
                <h1 style={styles.headerTitle}>Parent Portal</h1>
                <p style={styles.headerSub}>
                    {parentUser?.username ? `Welcome, ${parentUser.username}!` : 'Manage your children\'s learning journey'}
                </p>
            </div>

            <div style={styles.container}>
                <div style={styles.tabBar}>
                    {TABS.map((t) => (
                        <button
                            key={t.key}
                            style={styles.tab(activeTab === t.key)}
                            onClick={() => setActiveTab(t.key)}
                        >
                            {t.label}
                        </button>
                    ))}
                </div>

                {activeTab === 'children' && renderChildren()}
                {activeTab === 'overview' && renderOverview()}
                {activeTab === 'activity' && renderUsageSummary()}
                {activeTab === 'settings' && renderSettings()}
            </div>
        </div>
    );
}

export default ParentPortal;
