import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './CheckoutPage.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const CheckoutPage = () => {
    const navigate = useNavigate();
    const [cart, setCart] = useState({ items: [], total: 0, item_count: 0 });
    const [loading, setLoading] = useState(true);
    const [processing, setProcessing] = useState(false);
    const [orderSuccess, setOrderSuccess] = useState(false);
    const [orderId, setOrderId] = useState(null);

    const [formData, setFormData] = useState({
        fullName: '',
        phone: '',
        address: '',
        city: '',
        state: '',
        pincode: '',
        landmark: ''
    });

    const [errors, setErrors] = useState({});

    const getAuthHeaders = () => {
        const token = localStorage.getItem('token');
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };
    };

    useEffect(() => {
        fetchCart();
    }, []);

    const fetchCart = async () => {
        try {
            const response = await fetch(`${API_BASE}/store/cart`, {
                headers: getAuthHeaders()
            });
            if (response.ok) {
                const data = await response.json();
                setCart(data);
                if (data.items.length === 0) {
                    navigate('/store');
                }
            }
        } catch (err) {
            console.error('Error fetching cart:', err);
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

    const validateForm = () => {
        const newErrors = {};

        if (!formData.fullName.trim()) newErrors.fullName = 'Name is required';
        if (!formData.phone.trim()) newErrors.phone = 'Phone number is required';
        else if (!/^\d{10}$/.test(formData.phone)) newErrors.phone = 'Enter valid 10-digit phone number';
        if (!formData.address.trim()) newErrors.address = 'Address is required';
        if (!formData.city.trim()) newErrors.city = 'City is required';
        if (!formData.state.trim()) newErrors.state = 'State is required';
        if (!formData.pincode.trim()) newErrors.pincode = 'PIN code is required';
        else if (!/^\d{6}$/.test(formData.pincode)) newErrors.pincode = 'Enter valid 6-digit PIN code';

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: '' }));
        }
    };

    const handleCheckout = async () => {
        if (!validateForm()) return;

        setProcessing(true);

        const fullAddress = `${formData.fullName}\n${formData.address}\n${formData.landmark ? formData.landmark + '\n' : ''}${formData.city}, ${formData.state} - ${formData.pincode}`;

        try {
            // Create the order
            const response = await fetch(`${API_BASE}/store/checkout?shipping_address=${encodeURIComponent(fullAddress)}&phone=${formData.phone}`, {
                method: 'POST',
                headers: getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error('Failed to create order');
            }

            const orderData = await response.json();

            // Initialize Razorpay
            if (window.Razorpay) {
                const options = {
                    key: 'rzp_test_YourTestKey', // Replace with actual key
                    amount: orderData.razorpay_order.amount,
                    currency: orderData.razorpay_order.currency,
                    name: 'POSAN Activity Books',
                    description: `Order #${orderData.order_id}`,
                    image: '/logo.png',
                    handler: async function (response) {
                        // Payment successful - confirm the order
                        try {
                            await fetch(`${API_BASE}/store/orders/${orderData.order_id}/confirm-payment?payment_id=${response.razorpay_payment_id}`, {
                                method: 'POST',
                                headers: getAuthHeaders()
                            });

                            setOrderId(orderData.order_id);
                            setOrderSuccess(true);
                        } catch (err) {
                            console.error('Error confirming payment:', err);
                            alert('Payment received but confirmation failed. Please contact support.');
                        }
                    },
                    prefill: {
                        name: formData.fullName,
                        contact: formData.phone
                    },
                    theme: {
                        color: '#667eea'
                    }
                };

                const rzp = new window.Razorpay(options);
                rzp.open();
            } else {
                // Razorpay not loaded - simulate success for demo
                setOrderId(orderData.order_id);
                setOrderSuccess(true);
            }
        } catch (err) {
            console.error('Checkout error:', err);
            alert('Failed to process checkout. Please try again.');
        } finally {
            setProcessing(false);
        }
    };

    if (loading) {
        return (
            <div className="checkout-loading">
                <div className="spinner"></div>
                <p>Loading checkout...</p>
            </div>
        );
    }

    if (orderSuccess) {
        return (
            <div className="checkout-page">
                <div className="order-success">
                    <div className="success-icon">🎉</div>
                    <h1>Order Placed Successfully!</h1>
                    <p className="order-id">Order ID: #{orderId}</p>
                    <div className="success-message">
                        <p>📦 Your activity books are on their way!</p>
                        <p>You'll receive a confirmation email shortly.</p>
                    </div>
                    <div className="success-actions">
                        <button onClick={() => navigate('/store')} className="continue-btn">
                            🛒 Continue Shopping
                        </button>
                        <button onClick={() => navigate('/store/orders')} className="orders-btn">
                            📋 View Orders
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="checkout-page">
            <div className="checkout-container">
                {/* Header */}
                <div className="checkout-header">
                    <button className="back-btn" onClick={() => navigate('/store')}>
                        ← Back to Store
                    </button>
                    <h1>🛒 Checkout</h1>
                </div>

                <div className="checkout-grid">
                    {/* Shipping Form */}
                    <div className="shipping-section">
                        <h2>📍 Shipping Address</h2>

                        <div className="form-group">
                            <label>Full Name *</label>
                            <input
                                type="text"
                                name="fullName"
                                value={formData.fullName}
                                onChange={handleInputChange}
                                placeholder="Enter your full name"
                                className={errors.fullName ? 'error' : ''}
                            />
                            {errors.fullName && <span className="error-text">{errors.fullName}</span>}
                        </div>

                        <div className="form-group">
                            <label>Phone Number *</label>
                            <input
                                type="tel"
                                name="phone"
                                value={formData.phone}
                                onChange={handleInputChange}
                                placeholder="10-digit mobile number"
                                maxLength={10}
                                className={errors.phone ? 'error' : ''}
                            />
                            {errors.phone && <span className="error-text">{errors.phone}</span>}
                        </div>

                        <div className="form-group">
                            <label>Address *</label>
                            <textarea
                                name="address"
                                value={formData.address}
                                onChange={handleInputChange}
                                placeholder="House/Flat No., Building, Street"
                                rows={3}
                                className={errors.address ? 'error' : ''}
                            />
                            {errors.address && <span className="error-text">{errors.address}</span>}
                        </div>

                        <div className="form-group">
                            <label>Landmark (Optional)</label>
                            <input
                                type="text"
                                name="landmark"
                                value={formData.landmark}
                                onChange={handleInputChange}
                                placeholder="Near landmark"
                            />
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label>City *</label>
                                <input
                                    type="text"
                                    name="city"
                                    value={formData.city}
                                    onChange={handleInputChange}
                                    placeholder="City"
                                    className={errors.city ? 'error' : ''}
                                />
                                {errors.city && <span className="error-text">{errors.city}</span>}
                            </div>

                            <div className="form-group">
                                <label>State *</label>
                                <select
                                    name="state"
                                    value={formData.state}
                                    onChange={handleInputChange}
                                    className={errors.state ? 'error' : ''}
                                >
                                    <option value="">Select State</option>
                                    <option value="Andhra Pradesh">Andhra Pradesh</option>
                                    <option value="Karnataka">Karnataka</option>
                                    <option value="Kerala">Kerala</option>
                                    <option value="Maharashtra">Maharashtra</option>
                                    <option value="Tamil Nadu">Tamil Nadu</option>
                                    <option value="Telangana">Telangana</option>
                                    <option value="Delhi">Delhi</option>
                                    <option value="Gujarat">Gujarat</option>
                                    <option value="Rajasthan">Rajasthan</option>
                                    <option value="Uttar Pradesh">Uttar Pradesh</option>
                                    <option value="West Bengal">West Bengal</option>
                                    <option value="Other">Other</option>
                                </select>
                                {errors.state && <span className="error-text">{errors.state}</span>}
                            </div>
                        </div>

                        <div className="form-group half">
                            <label>PIN Code *</label>
                            <input
                                type="text"
                                name="pincode"
                                value={formData.pincode}
                                onChange={handleInputChange}
                                placeholder="6-digit PIN"
                                maxLength={6}
                                className={errors.pincode ? 'error' : ''}
                            />
                            {errors.pincode && <span className="error-text">{errors.pincode}</span>}
                        </div>
                    </div>

                    {/* Order Summary */}
                    <div className="order-summary">
                        <h2>📦 Order Summary</h2>

                        <div className="cart-items-summary">
                            {cart.items.map(item => (
                                <div key={item.id} className="summary-item">
                                    <div className="item-info">
                                        <span className="item-name">{item.name}</span>
                                        <span className="item-qty">× {item.quantity}</span>
                                    </div>
                                    <span className="item-price">{formatPrice(item.item_total)}</span>
                                </div>
                            ))}
                        </div>

                        <div className="price-breakdown">
                            <div className="price-row">
                                <span>Subtotal ({cart.item_count} items)</span>
                                <span>{formatPrice(cart.total)}</span>
                            </div>
                            <div className="price-row">
                                <span>Shipping</span>
                                <span className="free">FREE</span>
                            </div>
                            <div className="price-row total">
                                <span>Total</span>
                                <span>{formatPrice(cart.total)}</span>
                            </div>
                        </div>

                        <button
                            className="place-order-btn"
                            onClick={handleCheckout}
                            disabled={processing}
                        >
                            {processing ? (
                                <>Processing...</>
                            ) : (
                                <>💳 Pay {formatPrice(cart.total)}</>
                            )}
                        </button>

                        <div className="secure-badge">
                            🔒 Secure Payment powered by Razorpay
                        </div>

                        <div className="delivery-info">
                            <div className="info-item">
                                <span className="icon">🚚</span>
                                <span>Free delivery across India</span>
                            </div>
                            <div className="info-item">
                                <span className="icon">📅</span>
                                <span>Delivery in 5-7 business days</span>
                            </div>
                            <div className="info-item">
                                <span className="icon">↩️</span>
                                <span>Easy 7-day returns</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CheckoutPage;
