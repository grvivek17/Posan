import React, { useState } from 'react';
import './RunningBanner.css';

function RunningBanner() {
    const [isVisible, setIsVisible] = useState(true);

    if (!isVisible) return null;

    const bannerItems = [
        { icon: '🎂', text: 'Happy Birthday Sanvika! (07 Aug)', highlight: true },
        { icon: '✨', text: 'Wishing you a year filled with magic, laughter & learning! 🎈' },
        { icon: '🎉', text: 'POSAN Celebration Special!', highlight: true },
        { icon: '⭐', text: 'Explore magazines, fun puzzles & exciting games today! 🎮' },
        { icon: '🥳', text: 'Happy Birthday Sanvika! 07 Aug 💖' },
        { icon: '🎁', text: 'Keep shining bright Little Star! 🌟' },
    ];

    return (
        <div className="running-banner-wrapper" role="region" aria-label="Birthday Announcement">
            <div className="running-banner-tag">
                <span className="party-popper">🎉</span>
                <span className="tag-label">SPECIAL</span>
            </div>
            
            <div className="running-banner-track-container">
                <div className="running-banner-track">
                    {/* First copy */}
                    <div className="running-banner-group">
                        {bannerItems.map((item, index) => (
                            <span key={`b1-${index}`} className={`banner-item ${item.highlight ? 'highlight' : ''}`}>
                                <span className="item-icon">{item.icon}</span>
                                <span className="item-text">{item.text}</span>
                                <span className="item-separator">★</span>
                            </span>
                        ))}
                    </div>
                    {/* Duplicate copy for seamless infinite loop */}
                    <div className="running-banner-group" aria-hidden="true">
                        {bannerItems.map((item, index) => (
                            <span key={`b2-${index}`} className={`banner-item ${item.highlight ? 'highlight' : ''}`}>
                                <span className="item-icon">{item.icon}</span>
                                <span className="item-text">{item.text}</span>
                                <span className="item-separator">★</span>
                            </span>
                        ))}
                    </div>
                </div>
            </div>

            <button 
                className="banner-close-btn" 
                onClick={() => setIsVisible(false)} 
                title="Dismiss Banner"
                aria-label="Close banner"
            >
                ✕
            </button>
        </div>
    );
}

export default RunningBanner;
