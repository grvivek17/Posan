import './ProBadge.css';

const ProBadge = ({ variant = 'small', showLabel = true }) => {
    return (
        <div className={`pro-badge ${variant}`}>
            {variant === 'small' && (
                <span className="pro-badge-icon">✨ PRO</span>
            )}

            {variant === 'large' && (
                <div className="pro-badge-large">
                    <div className="pro-badge-icon-large">👑</div>
                    {showLabel && <span className="pro-badge-text">Premium Feature</span>}
                </div>
            )}

            {variant === 'inline' && (
                <span className="pro-badge-inline">
                    <span className="crown-icon">👑</span>
                    {showLabel && <span>PRO</span>}
                </span>
            )}
        </div>
    );
};

export default ProBadge;
