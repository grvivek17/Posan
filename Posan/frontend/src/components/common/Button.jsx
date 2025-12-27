import React from 'react';
import './Button.css';

function Button({ children, variant = 'primary', size = 'medium', onClick, className = '', ...props }) {
    const buttonClass = `button button-${variant} button-${size} ${className}`;

    return (
        <button className={buttonClass} onClick={onClick} {...props}>
            {children}
        </button>
    );
}

export default Button;
