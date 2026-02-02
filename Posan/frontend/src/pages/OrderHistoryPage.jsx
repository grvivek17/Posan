import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './OrderHistoryPage.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const OrderHistoryPage = () => {
    const navigate = useNavigate();
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [expandedOrder, setExpandedOrder] = useState(null);

    const getAuthHeaders = () => {
        const token = localStorage.getItem('token');
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };
    };

    useEffect(() => {
        fetchOrders();
    }, []);

    const fetchOrders = async () => {
        try {
            const response = await fetch(`${API_BASE}/store/orders`, {
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

    const getStatusInfo = (status) => {
        const statusMap = {
            'pending': { label: 'Pending', color: '#f59e0b', icon: '⏳' },
            'paid': { label: 'Paid', color: '#10b981', icon: '✅' },
            'processing': { label: 'Processing', color: '#3b82f6', icon: '📦' },
            'shipped': { label: 'Shipped', color: '#8b5cf6', icon: '🚚' },
            'delivered': { label: 'Delivered', color: '#10b981', icon: '🎉' },
            'cancelled': { label: 'Cancelled', color: '#ef4444', icon: '❌' }
        };
        return statusMap[status] || { label: status, color: '#666', icon: '📋' };
    };

    const toggleOrderDetails = (orderId) => {
        setExpandedOrder(expandedOrder === orderId ? null : orderId);
    };

    if (loading) {
        return (
            <div className="orders-loading">
                <div className="spinner"></div>
                <p>Loading your orders...</p>
            </div>
        );
    }

    return (
        <div className="order-history-page">
            {/* Header */}
            <div className="orders-header">
                <div className="orders-header-content">
                    <button className="back-btn" onClick={() => navigate('/store')}>
                        ← Back to Store
                    </button>
                    <div className="orders-title">
                        <h1>📦 My Orders</h1>
                        <p>Track your activity book purchases</p>
                    </div>
                </div>
            </div>

            <div className="orders-container">
                {orders.length === 0 ? (
                    <div className="no-orders">
                        <div className="no-orders-icon">📭</div>
                        <h2>No Orders Yet</h2>
                        <p>You haven't placed any orders yet. Start shopping!</p>
                        <button className="shop-now-btn" onClick={() => navigate('/store')}>
                            🛒 Shop Now
                        </button>
                    </div>
                ) : (
                    <div className="orders-list">
                        {orders.map(order => {
                            const statusInfo = getStatusInfo(order.status);
                            const isExpanded = expandedOrder === order.id;

                            return (
                                <div key={order.id} className={`order-card ${isExpanded ? 'expanded' : ''}`}>
                                    <div
                                        className="order-summary"
                                        onClick={() => toggleOrderDetails(order.id)}
                                    >
                                        <div className="order-main-info">
                                            <div className="order-id-row">
                                                <span className="order-id">Order #{order.id}</span>
                                                <span
                                                    className="order-status"
                                                    style={{ background: statusInfo.color }}
                                                >
                                                    {statusInfo.icon} {statusInfo.label}
                                                </span>
                                            </div>
                                            <div className="order-date">
                                                {formatDate(order.created_at)}
                                            </div>
                                        </div>

                                        <div className="order-quick-info">
                                            <div className="order-items-count">
                                                <span className="count-icon">📚</span>
                                                <span>{order.item_count} {order.item_count === 1 ? 'item' : 'items'}</span>
                                            </div>
                                            <div className="order-total">
                                                {formatPrice(order.total_amount)}
                                            </div>
                                        </div>

                                        <div className="expand-icon">
                                            {isExpanded ? '▲' : '▼'}
                                        </div>
                                    </div>

                                    {isExpanded && (
                                        <div className="order-details">
                                            <div className="order-items-list">
                                                <h4>Order Items</h4>
                                                {order.items.map((item, index) => (
                                                    <div key={index} className="order-item">
                                                        <div className="item-icon">📖</div>
                                                        <div className="item-info">
                                                            <span className="item-name">{item.name}</span>
                                                            <span className="item-qty">Qty: {item.quantity}</span>
                                                        </div>
                                                        <div className="item-price">
                                                            {formatPrice(item.price * item.quantity)}
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>

                                            <div className="order-timeline">
                                                <h4>Order Status</h4>
                                                <div className="timeline">
                                                    <div className={`timeline-step ${['pending', 'paid', 'processing', 'shipped', 'delivered'].includes(order.status) ? 'completed' : ''}`}>
                                                        <div className="step-icon">🛒</div>
                                                        <div className="step-label">Ordered</div>
                                                    </div>
                                                    <div className={`timeline-step ${['paid', 'processing', 'shipped', 'delivered'].includes(order.status) ? 'completed' : ''}`}>
                                                        <div className="step-icon">💳</div>
                                                        <div className="step-label">Paid</div>
                                                    </div>
                                                    <div className={`timeline-step ${['processing', 'shipped', 'delivered'].includes(order.status) ? 'completed' : ''}`}>
                                                        <div className="step-icon">📦</div>
                                                        <div className="step-label">Processing</div>
                                                    </div>
                                                    <div className={`timeline-step ${['shipped', 'delivered'].includes(order.status) ? 'completed' : ''}`}>
                                                        <div className="step-icon">🚚</div>
                                                        <div className="step-label">Shipped</div>
                                                    </div>
                                                    <div className={`timeline-step ${order.status === 'delivered' ? 'completed' : ''}`}>
                                                        <div className="step-icon">🎉</div>
                                                        <div className="step-label">Delivered</div>
                                                    </div>
                                                </div>
                                            </div>

                                            <div className="order-summary-section">
                                                <div className="summary-row">
                                                    <span>Subtotal</span>
                                                    <span>{formatPrice(order.total_amount)}</span>
                                                </div>
                                                <div className="summary-row">
                                                    <span>Shipping</span>
                                                    <span className="free-text">FREE</span>
                                                </div>
                                                <div className="summary-row total">
                                                    <span>Total</span>
                                                    <span>{formatPrice(order.total_amount)}</span>
                                                </div>
                                            </div>

                                            {order.status === 'delivered' && (
                                                <button className="reorder-btn" onClick={() => navigate('/store')}>
                                                    🔄 Order Again
                                                </button>
                                            )}
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

export default OrderHistoryPage;
