import React from 'react';
import './Card.css';

function Card({ children, className = '', hover = true, ...props }) {
    const cardClass = `card ${hover ? 'card-hover' : ''} ${className}`;

    return (
        <div className={cardClass} {...props}>
            {children}
        </div>
    );
}

export default Card;
