import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './AdminProductsPage.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const AdminProductsPage = () => {
    const navigate = useNavigate();
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [editingProduct, setEditingProduct] = useState(null);
    const [saving, setSaving] = useState(false);

    const categories = [
        { value: 'activity_book', label: 'Activity Book' },
        { value: 'puzzle_book', label: 'Puzzle Book' },
        { value: 'coloring_book', label: 'Coloring Book' },
        { value: 'sticker_book', label: 'Sticker Book' },
        { value: 'educational', label: 'Educational' },
        { value: 'stories', label: 'Stories' },
    ];

    const [formData, setFormData] = useState({
        name: '',
        description: '',
        price: '',
        original_price: '',
        category: 'activity_book',
        age_range: '',
        pages: '',
        is_bestseller: false,
        is_new: false,
        is_available: true,
        stock: 100,
        image_url: ''
    });

    const getAuthHeaders = () => {
        const token = localStorage.getItem('token');
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };
    };

    useEffect(() => {
        fetchProducts();
    }, []);

    const fetchProducts = async () => {
        try {
            const response = await fetch(`${API_BASE}/store/products?limit=100`);
            const data = await response.json();
            setProducts(data.products || []);
        } catch (err) {
            console.error('Error fetching products:', err);
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

    const openAddModal = () => {
        setEditingProduct(null);
        setFormData({
            name: '',
            description: '',
            price: '',
            original_price: '',
            category: 'activity_book',
            age_range: '',
            pages: '',
            is_bestseller: false,
            is_new: false,
            is_available: true,
            stock: 100,
            image_url: ''
        });
        setShowModal(true);
    };

    const openEditModal = (product) => {
        setEditingProduct(product);
        setFormData({
            name: product.name || '',
            description: product.description || '',
            price: product.price?.toString() || '',
            original_price: product.original_price?.toString() || '',
            category: product.category || 'activity_book',
            age_range: product.age_range || '',
            pages: product.pages?.toString() || '',
            is_bestseller: product.is_bestseller || false,
            is_new: product.is_new || false,
            is_available: product.is_available !== false,
            stock: product.stock || 100,
            image_url: product.image_url || ''
        });
        setShowModal(true);
    };

    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSave = async () => {
        if (!formData.name || !formData.price) {
            alert('Name and price are required');
            return;
        }

        setSaving(true);
        try {
            const productData = {
                ...formData,
                price: parseFloat(formData.price),
                original_price: formData.original_price ? parseFloat(formData.original_price) : null,
                pages: formData.pages ? parseInt(formData.pages) : null,
                stock: parseInt(formData.stock)
            };

            const url = editingProduct
                ? `${API_BASE}/admin/products/${editingProduct.id}`
                : `${API_BASE}/admin/products`;

            const method = editingProduct ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method,
                headers: getAuthHeaders(),
                body: JSON.stringify(productData)
            });

            if (response.ok) {
                alert(editingProduct ? '✅ Product updated!' : '✅ Product added!');
                setShowModal(false);
                fetchProducts();
            } else {
                throw new Error('Failed to save product');
            }
        } catch (err) {
            console.error('Error saving product:', err);
            alert('Failed to save product');
        } finally {
            setSaving(false);
        }
    };

    const handleDelete = async (productId) => {
        if (!confirm('Are you sure you want to delete this product?')) return;

        try {
            const response = await fetch(`${API_BASE}/admin/products/${productId}`, {
                method: 'DELETE',
                headers: getAuthHeaders()
            });

            if (response.ok) {
                alert('✅ Product deleted');
                fetchProducts();
            }
        } catch (err) {
            console.error('Error deleting product:', err);
            alert('Failed to delete product');
        }
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

    if (loading) {
        return (
            <div className="admin-loading">
                <div className="spinner"></div>
                <p>Loading products...</p>
            </div>
        );
    }

    return (
        <div className="admin-products-page">
            {/* Header */}
            <div className="page-header">
                <button className="back-btn" onClick={() => navigate('/admin')}>
                    ← Back to Dashboard
                </button>
                <div className="header-content">
                    <h1>📦 Manage Products</h1>
                    <button className="add-btn" onClick={openAddModal}>
                        ➕ Add Product
                    </button>
                </div>
                <p className="subtitle">{products.length} products in store</p>
            </div>

            {/* Products Table */}
            <div className="products-table-container">
                <table className="products-table">
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th>Category</th>
                            <th>Price</th>
                            <th>Stock</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {products.map(product => (
                            <tr key={product.id}>
                                <td className="product-cell">
                                    <div className="product-info">
                                        <span className="product-icon">{getCategoryIcon(product.category)}</span>
                                        <div>
                                            <span className="product-name">{product.name}</span>
                                            <span className="product-age">Ages {product.age_range}</span>
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    <span className="category-badge">{product.category?.replace('_', ' ')}</span>
                                </td>
                                <td>
                                    <div className="price-cell">
                                        <span className="current-price">{formatPrice(product.price)}</span>
                                        {product.original_price && (
                                            <span className="original-price">{formatPrice(product.original_price)}</span>
                                        )}
                                    </div>
                                </td>
                                <td>
                                    <span className={`stock-badge ${product.stock < 10 ? 'low' : ''}`}>
                                        {product.stock}
                                    </span>
                                </td>
                                <td>
                                    <div className="status-badges">
                                        {product.is_bestseller && <span className="badge bestseller">🔥 Bestseller</span>}
                                        {product.is_new && <span className="badge new">✨ New</span>}
                                        {!product.is_available && <span className="badge unavailable">Hidden</span>}
                                    </div>
                                </td>
                                <td>
                                    <div className="action-buttons">
                                        <button className="edit-btn" onClick={() => openEditModal(product)}>
                                            ✏️
                                        </button>
                                        <button className="delete-btn" onClick={() => handleDelete(product.id)}>
                                            🗑️
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Add/Edit Modal */}
            {showModal && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal-content" onClick={e => e.stopPropagation()}>
                        <h2>{editingProduct ? '✏️ Edit Product' : '➕ Add Product'}</h2>

                        <div className="modal-form">
                            <div className="form-group">
                                <label>Product Name *</label>
                                <input
                                    type="text"
                                    name="name"
                                    value={formData.name}
                                    onChange={handleInputChange}
                                    placeholder="e.g., Fun Activity Book for Kids"
                                />
                            </div>

                            <div className="form-group">
                                <label>Description</label>
                                <textarea
                                    name="description"
                                    value={formData.description}
                                    onChange={handleInputChange}
                                    placeholder="Describe the book..."
                                    rows={3}
                                />
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label>Price (₹) *</label>
                                    <input
                                        type="number"
                                        name="price"
                                        value={formData.price}
                                        onChange={handleInputChange}
                                        placeholder="299"
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Original Price (₹)</label>
                                    <input
                                        type="number"
                                        name="original_price"
                                        value={formData.original_price}
                                        onChange={handleInputChange}
                                        placeholder="399"
                                    />
                                </div>
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label>Category</label>
                                    <select
                                        name="category"
                                        value={formData.category}
                                        onChange={handleInputChange}
                                    >
                                        {categories.map(cat => (
                                            <option key={cat.value} value={cat.value}>
                                                {cat.label}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                                <div className="form-group">
                                    <label>Age Range</label>
                                    <input
                                        type="text"
                                        name="age_range"
                                        value={formData.age_range}
                                        onChange={handleInputChange}
                                        placeholder="e.g., 5-8"
                                    />
                                </div>
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label>Pages</label>
                                    <input
                                        type="number"
                                        name="pages"
                                        value={formData.pages}
                                        onChange={handleInputChange}
                                        placeholder="100"
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Stock</label>
                                    <input
                                        type="number"
                                        name="stock"
                                        value={formData.stock}
                                        onChange={handleInputChange}
                                        placeholder="100"
                                    />
                                </div>
                            </div>

                            <div className="form-group">
                                <label>Image URL (optional)</label>
                                <input
                                    type="url"
                                    name="image_url"
                                    value={formData.image_url}
                                    onChange={handleInputChange}
                                    placeholder="https://..."
                                />
                            </div>

                            <div className="checkbox-row">
                                <label className="checkbox-label">
                                    <input
                                        type="checkbox"
                                        name="is_bestseller"
                                        checked={formData.is_bestseller}
                                        onChange={handleInputChange}
                                    />
                                    <span>🔥 Bestseller</span>
                                </label>
                                <label className="checkbox-label">
                                    <input
                                        type="checkbox"
                                        name="is_new"
                                        checked={formData.is_new}
                                        onChange={handleInputChange}
                                    />
                                    <span>✨ New Arrival</span>
                                </label>
                                <label className="checkbox-label">
                                    <input
                                        type="checkbox"
                                        name="is_available"
                                        checked={formData.is_available}
                                        onChange={handleInputChange}
                                    />
                                    <span>👁️ Visible</span>
                                </label>
                            </div>
                        </div>

                        <div className="modal-actions">
                            <button className="cancel-btn" onClick={() => setShowModal(false)}>
                                Cancel
                            </button>
                            <button
                                className="save-btn"
                                onClick={handleSave}
                                disabled={saving}
                            >
                                {saving ? 'Saving...' : '💾 Save Product'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AdminProductsPage;
