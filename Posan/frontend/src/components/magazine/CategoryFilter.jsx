import React from 'react';
import './CategoryFilter.css';

const categories = [
    { id: 'all', name: 'All', icon: '📚' },
    { id: 'science', name: 'Science', icon: '🔬' },
    { id: 'comics', name: 'Comics', icon: '💭' },
    { id: 'animals', name: 'Animals', icon: '🦁' },
    { id: 'adventure', name: 'Adventure', icon: '🗺️' },
    { id: 'space', name: 'Space', icon: '🚀' },
];

function CategoryFilter({ activeCategory, onCategoryChange }) {
    return (
        <div className="category-filter">
            {categories.map((category) => (
                <button
                    key={category.id}
                    className={`category-pill ${activeCategory === category.id ? 'active' : ''}`}
                    onClick={() => onCategoryChange(category.id)}
                >
                    <span className="category-icon">{category.icon}</span>
                    {category.name}
                </button>
            ))}
        </div>
    );
}

export default CategoryFilter;
