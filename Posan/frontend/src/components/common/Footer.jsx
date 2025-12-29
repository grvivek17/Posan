import React from 'react';
import { Link } from 'react-router-dom';
import './Footer.css';

function Footer() {
    return (
        <footer className="footer">
            <div className="container">
                <div className="footer-content">
                    <div className="footer-section">
                        <h3>🎨 POSAN</h3>
                        <p>Making learning fun for kids!</p>
                    </div>

                    <div className="footer-section">
                        <h4>Quick Links</h4>
                        <ul>
                            <li><Link to="/about">About</Link></li>
                            <li><Link to="/magazines">Magazines</Link></li>
                            <li><Link to="/puzzles">Puzzles</Link></li>
                            <li><Link to="/profile">Profile</Link></li>
                        </ul>
                    </div>

                    <div className="footer-section">
                        <h4>Support</h4>
                        <ul>
                            <li><a href="/help">Help Center</a></li>
                            <li><a href="/privacy">Privacy Policy</a></li>
                            <li><a href="/terms">Terms of Service</a></li>
                        </ul>
                    </div>
                </div>

                <div className="footer-bottom">
                    <p>&copy; 2024 POSAN. All rights reserved. Made with ❤️ for kids!</p>
                </div>
            </div>
        </footer>
    );
}

export default Footer;
