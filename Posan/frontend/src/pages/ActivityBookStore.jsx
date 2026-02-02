import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './ActivityBookStore.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const ActivityBookStore = () => {
    const navigate = useNavigate();
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [cart, setCart] = useState({ items: [], total: 0, item_count: 0 });
    const [showCart, setShowCart] = useState(false);
    const [activeCategory, setActiveCategory] = useState('all');
    const [searchQuery, setSearchQuery] = useState('');
    const [addingToCart, setAddingToCart] = useState(null);

    const categories = [
        { value: 'all', label: '🎯 All Books', icon: '📚' },
        { value: 'activity_book', label: 'Activity Books', icon: '✏️' },
        { value: 'puzzle_book', label: 'Puzzle Books', icon: '🧩' },
        { value: 'coloring_book', label: 'Coloring Books', icon: '🎨' },
        { value: 'sticker_book', label: 'Sticker Books', icon: '⭐' },
        { value: 'educational', label: 'Educational', icon: '🎓' },
        { value: 'stories', label: 'Story Books', icon: '📖' },
    ];

    const getAuthHeaders = () => {
        const token = localStorage.getItem('token');
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };
    };

    useEffect(() => {
        fetchProducts();
        fetchCart();
    }, [activeCategory, searchQuery]);

    const fetchProducts = async () => {
        try {
            let url = `${API_BASE}/store/products?limit=50`;
            if (activeCategory !== 'all') {
                url += `&category=${activeCategory}`;
            }
            if (searchQuery) {
                url += `&search=${encodeURIComponent(searchQuery)}`;
            }

            const response = await fetch(url);
            const data = await response.json();
            setProducts(data.products || []);
        } catch (err) {
            console.error('Error fetching products:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchCart = async () => {
        try {
            const response = await fetch(`${API_BASE}/store/cart`, {
                headers: getAuthHeaders()
            });
            if (response.ok) {
                const data = await response.json();
                setCart(data);
            }
        } catch (err) {
            console.error('Error fetching cart:', err);
        }
    };

    const addToCart = async (productId) => {
        setAddingToCart(productId);
        try {
            const response = await fetch(`${API_BASE}/store/cart/add?product_id=${productId}&quantity=1`, {
                method: 'POST',
                headers: getAuthHeaders()
            });

            if (response.ok) {
                fetchCart();
                // Show brief success animation
                setTimeout(() => setAddingToCart(null), 500);
            } else {
                alert('Please login to add items to cart');
                setAddingToCart(null);
            }
        } catch (err) {
            console.error('Error adding to cart:', err);
            setAddingToCart(null);
        }
    };

    const updateCartItem = async (itemId, quantity) => {
        try {
            await fetch(`${API_BASE}/store/cart/update/${itemId}?quantity=${quantity}`, {
                method: 'PUT',
                headers: getAuthHeaders()
            });
            fetchCart();
        } catch (err) {
            console.error('Error updating cart:', err);
        }
    };

    const removeFromCart = async (itemId) => {
        try {
            await fetch(`${API_BASE}/store/cart/remove/${itemId}`, {
                method: 'DELETE',
                headers: getAuthHeaders()
            });
            fetchCart();
        } catch (err) {
            console.error('Error removing from cart:', err);
        }
    };

    const getDiscountPercentage = (price, originalPrice) => {
        if (!originalPrice || originalPrice <= price) return 0;
        return Math.round((1 - price / originalPrice) * 100);
    };

    const formatPrice = (price) => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        }).format(price);
    };

    // Product images based on category (placeholder colors/patterns)
    const getCategoryColor = (category) => {
        const colors = {
            'activity_book': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'puzzle_book': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            'coloring_book': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            'sticker_book': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
            'educational': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            'stories': 'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)'
        };
        return colors[category] || 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    };

    const getCategoryIcon = (category) => {
        const icons = {
            'activity_book': '✏️',
            'puzzle_book': '🧩',
            'coloring_book': '🎨',
            'sticker_book': '⭐',
            'educational': '🎓',
            'stories': '📖'
        };
        return icons[category] || '📚';
    };

    // Render product image or fallback
    const renderProductImage = (product, className = '') => {
        if (product.image_url) {
            return (
                <img
                    src={product.image_url}
                    alt={product.name}
                    className={`product-img ${className}`}
                    onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'flex';
                    }}
                />
            );
        }
        return null;
    };

    if (loading) {
        return (
            <div className="store-loading">
                <div className="spinner"></div>
                <p>Loading amazing books...</p>
            </div>
        );
    }

    return (
        <div className="activity-book-store">
            {/* Store Header */}
            <div className="store-header">
                <div className="store-header-content">
                    <div className="store-title-section">
                        <h1>📚 Kids Activity Book Store</h1>
                        <p>Fun-filled books for curious minds!</p>
                    </div>
                    <div className="store-header-actions">
                        <button
                            className="orders-button"
                            onClick={() => navigate('/store/orders')}
                        >
                            <span>📦</span>
                            <span>My Orders</span>
                        </button>
                        <button
                            className="cart-button"
                            onClick={() => setShowCart(true)}
                        >
                            <span className="cart-icon">🛒</span>
                            {cart.item_count > 0 && (
                                <span className="cart-badge">{cart.item_count}</span>
                            )}
                            <span className="cart-total">{formatPrice(cart.total)}</span>
                        </button>
                    </div>
                </div>
            </div>

            {/* Search Bar */}
            <div className="store-search">
                <input
                    type="text"
                    placeholder="🔍 Search for activity books, puzzles, coloring..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="search-input"
                />
            </div>

            {/* Category Filter */}
            <div className="category-filter">
                {categories.map(cat => (
                    <button
                        key={cat.value}
                        className={`category-btn ${activeCategory === cat.value ? 'active' : ''}`}
                        onClick={() => setActiveCategory(cat.value)}
                    >
                        <span className="cat-icon">{cat.icon}</span>
                        <span className="cat-label">{cat.label}</span>
                    </button>
                ))}
            </div>

            {/* Bestsellers Section */}
            {activeCategory === 'all' && (
                <section className="bestsellers-section">
                    <h2>🔥 Bestsellers</h2>
                    <div className="bestsellers-scroll">
                        {products.filter(p => p.is_bestseller).map(product => (
                            <div key={product.id} className="bestseller-card">
                                <div
                                    className="bestseller-image"
                                    style={{ background: product.image_url ? 'transparent' : getCategoryColor(product.category) }}
                                >
                                    {product.image_url ? (
                                        <img src={product.image_url} alt={product.name} className="product-cover-img" />
                                    ) : (
                                        <span className="book-emoji">{getCategoryIcon(product.category)}</span>
                                    )}
                                    <span className="bestseller-tag">BESTSELLER</span>
                                </div>
                                <div className="bestseller-info">
                                    <h3>{product.name}</h3>
                                    <div className="bestseller-meta">
                                        <span className="age-tag">Ages {product.age_range}</span>
                                        <span className="rating">⭐ {product.rating}</span>
                                    </div>
                                    <div className="price-row">
                                        <span className="price">{formatPrice(product.price)}</span>
                                        {product.original_price && (
                                            <span className="original-price">{formatPrice(product.original_price)}</span>
                                        )}
                                    </div>
                                    <button
                                        className={`add-btn ${addingToCart === product.id ? 'adding' : ''}`}
                                        onClick={() => addToCart(product.id)}
                                        disabled={addingToCart === product.id}
                                    >
                                        {addingToCart === product.id ? '✓ Added!' : '🛒 Add to Cart'}
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>
            )}

            {/* New Arrivals */}
            {activeCategory === 'all' && products.filter(p => p.is_new).length > 0 && (
                <section className="new-arrivals-section">
                    <h2>✨ New Arrivals</h2>
                    <div className="new-arrivals-grid">
                        {products.filter(p => p.is_new).map(product => (
                            <div key={product.id} className="arrival-card">
                                <div
                                    className="arrival-image"
                                    style={{ background: product.image_url ? 'transparent' : getCategoryColor(product.category) }}
                                >
                                    {product.image_url ? (
                                        <img src={product.image_url} alt={product.name} className="product-cover-img-sm" />
                                    ) : (
                                        <span className="book-emoji-lg">{getCategoryIcon(product.category)}</span>
                                    )}
                                    <span className="new-tag">NEW</span>
                                </div>
                                <h3>{product.name}</h3>
                                <p className="arrival-desc">{product.description?.substring(0, 60)}...</p>
                                <div className="arrival-footer">
                                    <span className="price">{formatPrice(product.price)}</span>
                                    <button
                                        className="add-btn-sm"
                                        onClick={() => addToCart(product.id)}
                                    >
                                        + Add
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>
            )}

            {/* All Products Grid */}
            <section className="all-products-section">
                <h2>{activeCategory === 'all' ? '📚 All Books' : categories.find(c => c.value === activeCategory)?.label}</h2>
                <div className="products-grid">
                    {products.map(product => (
                        <div key={product.id} className="product-card">
                            <div
                                className="product-image"
                                style={{ background: product.image_url ? 'transparent' : getCategoryColor(product.category) }}
                            >
                                {product.image_url ? (
                                    <img src={product.image_url} alt={product.name} className="product-cover-img" />
                                ) : (
                                    <span className="product-emoji">{getCategoryIcon(product.category)}</span>
                                )}
                                {product.is_bestseller && <span className="badge bestseller">🔥 Bestseller</span>}
                                {product.is_new && <span className="badge new">✨ New</span>}
                                {getDiscountPercentage(product.price, product.original_price) > 0 && (
                                    <span className="badge discount">
                                        -{getDiscountPercentage(product.price, product.original_price)}%
                                    </span>
                                )}
                            </div>
                            <div className="product-details">
                                <h3>{product.name}</h3>
                                <p className="product-desc">{product.description?.substring(0, 80)}...</p>
                                <div className="product-meta">
                                    <span className="age-badge">Ages {product.age_range}</span>
                                    <span className="pages-badge">{product.pages} pages</span>
                                </div>
                                <div className="product-rating">
                                    <span className="stars">{'⭐'.repeat(Math.floor(product.rating))}</span>
                                    <span className="rating-text">{product.rating} ({product.reviews_count} reviews)</span>
                                </div>
                                <div className="product-footer">
                                    <div className="price-section">
                                        <span className="current-price">{formatPrice(product.price)}</span>
                                        {product.original_price && (
                                            <span className="old-price">{formatPrice(product.original_price)}</span>
                                        )}
                                    </div>
                                    <button
                                        className={`add-to-cart-btn ${addingToCart === product.id ? 'added' : ''}`}
                                        onClick={() => addToCart(product.id)}
                                        disabled={addingToCart === product.id}
                                    >
                                        {addingToCart === product.id ? '✓' : '🛒'}
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {products.length === 0 && (
                    <div className="empty-state">
                        <span className="empty-icon">🔍</span>
                        <h3>No books found</h3>
                        <p>Try a different category or search term</p>
                    </div>
                )}
            </section>

            {/* Cart Sidebar */}
            {showCart && (
                <div className="cart-overlay" onClick={() => setShowCart(false)}>
                    <div className="cart-sidebar" onClick={e => e.stopPropagation()}>
                        <div className="cart-header">
                            <h2>🛒 Your Cart</h2>
                            <button className="close-btn" onClick={() => setShowCart(false)}>✕</button>
                        </div>

                        {cart.items.length === 0 ? (
                            <div className="cart-empty">
                                <span className="empty-cart-icon">🛒</span>
                                <h3>Your cart is empty</h3>
                                <p>Add some amazing books!</p>
                            </div>
                        ) : (
                            <>
                                <div className="cart-items">
                                    {cart.items.map(item => (
                                        <div key={item.id} className="cart-item">
                                            <div className="cart-item-image">
                                                📚
                                            </div>
                                            <div className="cart-item-details">
                                                <h4>{item.name}</h4>
                                                <p className="item-price">{formatPrice(item.price)}</p>
                                                <div className="quantity-controls">
                                                    <button
                                                        onClick={() => updateCartItem(item.id, item.quantity - 1)}
                                                        disabled={item.quantity <= 1}
                                                    >
                                                        −
                                                    </button>
                                                    <span>{item.quantity}</span>
                                                    <button onClick={() => updateCartItem(item.id, item.quantity + 1)}>
                                                        +
                                                    </button>
                                                </div>
                                            </div>
                                            <div className="cart-item-total">
                                                <span>{formatPrice(item.item_total)}</span>
                                                <button
                                                    className="remove-btn"
                                                    onClick={() => removeFromCart(item.id)}
                                                >
                                                    🗑️
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                <div className="cart-footer">
                                    <div className="cart-total-row">
                                        <span>Total ({cart.item_count} items)</span>
                                        <span className="total-amount">{formatPrice(cart.total)}</span>
                                    </div>
                                    <button
                                        className="checkout-btn"
                                        onClick={() => navigate('/store/checkout')}
                                    >
                                        Proceed to Checkout 🚀
                                    </button>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default ActivityBookStore;
