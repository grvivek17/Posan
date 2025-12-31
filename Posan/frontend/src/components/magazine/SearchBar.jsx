import React from 'react';
import './SearchBar.css';

function SearchBar({ value, onChange, placeholder = "Search magazines, stories..." }) {
    return (
        <div className="search-bar">
            <span className="search-icon">🔍</span>
            <input
                type="text"
                className="search-input"
                placeholder={placeholder}
                value={value}
                onChange={(e) => onChange(e.target.value)}
            />
        </div>
    );
}

export default SearchBar;
