import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './BottomNav.css';

function BottomNav() {
    const location = useLocation();

    const navItems = [
        {
            path: '/',
            icon: '🏠',
            label: 'Home',
            activeIcon: '🏠'
        },
        {
            path: '/puzzle-zone',
            icon: '🔍',
            label: 'Explore',
            activeIcon: '🔍'
        },
        {
            path: '/profile',
            icon: '😊',
            label: 'Profile',
            activeIcon: '😊',
            highlight: true
        },
        {
            path: '/magazines',
            icon: '💬',
            label: 'Club',
            activeIcon: '💬'
        }
    ];

    const isActive = (path) => {
        if (path === '/') {
            return location.pathname === '/';
        }
        return location.pathname.startsWith(path);
    };

    return (
        <nav className="bottom-nav">
            <div className="bottom-nav-container">
                {navItems.map((item) => (
                    <Link
                        key={item.path}
                        to={item.path}
                        className={`bottom-nav-item ${isActive(item.path) ? 'active' : ''} ${item.highlight ? 'highlight' : ''}`}
                    >
                        <div className="nav-icon-wrapper">
                            <span className="nav-icon">
                                {isActive(item.path) ? item.activeIcon : item.icon}
                            </span>
                        </div>
                        <span className="nav-label">{item.label}</span>
                    </Link>
                ))}
            </div>
        </nav>
    );
}

export default BottomNav;
