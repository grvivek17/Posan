import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './AdminOrdersPage.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const AdminOrdersPage = () => {
    const navigate = useNavigate();
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');
    const [expandedOrder, setExpandedOrder] = useState(null);
    const [updating, setUpdating] = useState(null);

    const getAuthHeaders = () => {
        const token = localStorage.getItem('token');
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };
    };

    useEffect(() => {
        fetchOrders();
    }, [filter]);

    const fetchOrders = async () => {
        try {
            let url = `${API_BASE}/store/admin/orders`;
            if (filter !== 'all') {
                url += `?status=${filter}`;
            }
            const response = await fetch(url, {
                headers: getAuthHeaders()
            });
            if (response.ok) {
                const data = await response.json();
                setOrders(data.orders || []);
            }
        } catch (err) {
            console.error('Error fetching orders:', err);
        } finally {
            setLoading(false);
        }
    };

    const updateOrderStatus = async (orderId, newStatus) => {
        setUpdating(orderId);
        try {
            const response = await fetch(`${API_BASE}/store/admin/orders/${orderId}/status?status=${newStatus}`, {
                method: 'PUT',
                headers: getAuthHeaders()
            });

            if (response.ok) {
                // Update local state
                setOrders(orders.map(order =>
                    order.id === orderId ? { ...order, status: newStatus } : order
                ));
            } else {
                alert('Failed to update order status');
            }
        } catch (err) {
            console.error('Error updating order:', err);
            alert('Failed to update order status');
        } finally {
            setUpdating(null);
        }
    };

    const formatPrice = (price) => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        }).format(price);
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-IN', {
            day: 'numeric',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const statusOptions = [
        { value: 'pending', label: 'Pending', color: '#f59e0b', icon: '⏳' },
        { value: 'paid', label: 'Paid', color: '#10b981', icon: '✅' },
        { value: 'processing', label: 'Processing', color: '#3b82f6', icon: '📦' },
        { value: 'shipped', label: 'Shipped', color: '#8b5cf6', icon: '🚚' },
        { value: 'delivered', label: 'Delivered', color: '#059669', icon: '🎉' },
        { value: 'cancelled', label: 'Cancelled', color: '#ef4444', icon: '❌' }
    ];

    const getStatusInfo = (status) => {
        return statusOptions.find(s => s.value === status) || { label: status, color: '#666', icon: '📋' };
    };

    const filterOptions = [
        { value: 'all', label: 'All Orders' },
        { value: 'pending', label: 'Pending' },
        { value: 'paid', label: 'Paid' },
        { value: 'processing', label: 'Processing' },
        { value: 'shipped', label: 'Shipped' },
        { value: 'delivered', label: 'Delivered' },
        { value: 'cancelled', label: 'Cancelled' }
    ];

    const getOrderStats = () => {
        const stats = {
            total: orders.length,
            pending: orders.filter(o => o.status === 'pending').length,
            processing: orders.filter(o => ['paid', 'processing'].includes(o.status)).length,
            shipped: orders.filter(o => o.status === 'shipped').length,
            completed: orders.filter(o => o.status === 'delivered').length
        };
        return stats;
    };

    const stats = getOrderStats();

    if (loading) {
        return (
            <div className="admin-loading">
                <div className="spinner"></div>
                <p>Loading orders...</p>
            </div>
        );
    }

    return (
        <div className="admin-orders-page">
            {/* Header */}
            <div className="page-header">
                <button className="back-btn" onClick={() => navigate('/admin')}>
                    ← Back to Dashboard
                </button>
                <div className="header-content">
                    <h1>📦 Order Management</h1>
                    <p className="subtitle">View and manage customer orders</p>
                </div>
            </div>

            {/* Stats Cards */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon total">📊</div>
                    <div className="stat-info">
                        <span className="stat-value">{stats.total}</span>
                        <span className="stat-label">Total Orders</span>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon pending">⏳</div>
                    <div className="stat-info">
                        <span className="stat-value">{stats.pending}</span>
                        <span className="stat-label">Pending</span>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon processing">📦</div>
                    <div className="stat-info">
                        <span className="stat-value">{stats.processing}</span>
                        <span className="stat-label">Processing</span>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon shipped">🚚</div>
                    <div className="stat-info">
                        <span className="stat-value">{stats.shipped}</span>
                        <span className="stat-label">Shipped</span>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon completed">✅</div>
                    <div className="stat-info">
                        <span className="stat-value">{stats.completed}</span>
                        <span className="stat-label">Completed</span>
                    </div>
                </div>
            </div>

            {/* Filter Tabs */}
            <div className="filter-tabs">
                {filterOptions.map(option => (
                    <button
                        key={option.value}
                        className={`filter-tab ${filter === option.value ? 'active' : ''}`}
                        onClick={() => setFilter(option.value)}
                    >
                        {option.label}
                    </button>
                ))}
            </div>

            {/* Orders List */}
            <div className="orders-container">
                {orders.length === 0 ? (
                    <div className="no-orders">
                        <div className="no-orders-icon">📭</div>
                        <h3>No Orders Found</h3>
                        <p>No orders match the selected filter.</p>
                    </div>
                ) : (
                    <div className="orders-list">
                        {orders.map(order => {
                            const statusInfo = getStatusInfo(order.status);
                            const isExpanded = expandedOrder === order.id;

                            return (
                                <div key={order.id} className={`order-card ${isExpanded ? 'expanded' : ''}`}>
                                    <div className="order-header" onClick={() => setExpandedOrder(isExpanded ? null : order.id)}>
                                        <div className="order-main">
                                            <div className="order-id-section">
                                                <span className="order-id">Order #{order.id}</span>
                                                <span
                                                    className="status-badge"
                                                    style={{ background: statusInfo.color }}
                                                >
                                                    {statusInfo.icon} {statusInfo.label}
                                                </span>
                                            </div>
                                            <div className="order-meta">
                                                <span className="order-date">📅 {formatDate(order.created_at)}</span>
                                                <span className="order-customer">👤 {order.user_email || 'Customer'}</span>
                                            </div>
                                        </div>
                                        <div className="order-summary">
                                            <span className="order-items">📚 {order.item_count} items</span>
                                            <span className="order-total">{formatPrice(order.total_amount)}</span>
                                        </div>
                                        <div className="expand-icon">{isExpanded ? '▲' : '▼'}</div>
                                    </div>

                                    {isExpanded && (
                                        <div className="order-details">
                                            {/* Order Items */}
                                            <div className="details-section">
                                                <h4>📦 Order Items</h4>
                                                <div className="items-list">
                                                    {order.items?.map((item, index) => (
                                                        <div key={index} className="item-row">
                                                            <span className="item-name">{item.name}</span>
                                                            <span className="item-qty">× {item.quantity}</span>
                                                            <span className="item-price">{formatPrice(item.price * item.quantity)}</span>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>

                                            {/* Shipping Address */}
                                            {order.shipping_address && (
                                                <div className="details-section">
                                                    <h4>📍 Shipping Address</h4>
                                                    <p className="shipping-address">{order.shipping_address}</p>
                                                </div>
                                            )}

                                            {/* Status Update */}
                                            <div className="details-section">
                                                <h4>🔄 Update Status</h4>
                                                <div className="status-buttons">
                                                    {statusOptions.map(status => (
                                                        <button
                                                            key={status.value}
                                                            className={`status-btn ${order.status === status.value ? 'active' : ''}`}
                                                            style={{
                                                                background: order.status === status.value ? status.color : '#f3f4f6',
                                                                color: order.status === status.value ? 'white' : '#333'
                                                            }}
                                                            onClick={() => updateOrderStatus(order.id, status.value)}
                                                            disabled={updating === order.id || order.status === status.value}
                                                        >
                                                            {updating === order.id ? '...' : `${status.icon} ${status.label}`}
                                                        </button>
                                                    ))}
                                                </div>
                                            </div>

                                            {/* Order Summary */}
                                            <div className="order-totals">
                                                <div className="total-row">
                                                    <span>Subtotal</span>
                                                    <span>{formatPrice(order.total_amount)}</span>
                                                </div>
                                                <div className="total-row">
                                                    <span>Shipping</span>
                                                    <span className="free">FREE</span>
                                                </div>
                                                <div className="total-row grand-total">
                                                    <span>Total</span>
                                                    <span>{formatPrice(order.total_amount)}</span>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
};

export default AdminOrdersPage;
