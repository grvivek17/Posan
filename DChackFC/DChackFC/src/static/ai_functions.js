// AI Concierge Functions

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();

    if (!message) return;

    // Add user message to chat
    addMessageToChat('user', message);
    input.value = '';

    // Get AI response
    const user = JSON.parse(localStorage.getItem('user'));
    try {
        const response = await fetch('/api/v1/ai/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: user.vendor_id || 1,
                message: message
            })
        });

        const result = await response.json();
        if (result.success) {
            addMessageToChat('ai', result.response);

            // Show suggestions if any
            if (result.suggestions && result.suggestions.length > 0) {
                const suggestionsHtml = result.suggestions.map(s =>
                    `<div style="margin-top: 0.5rem; padding: 0.5rem; background: rgba(255,255,255,0.05); border-radius: 0.25rem;">
                        <strong>${s.name}</strong> - ${s.reason}
                    </div>`
                ).join('');
                addMessageToChat('ai', suggestionsHtml, true);
            }
        }
    } catch (error) {
        addMessageToChat('ai', 'Sorry, I encountered an error. Please try again.');
    }
}

function quickMessage(message) {
    document.getElementById('chat-input').value = message;
    sendMessage();
}

function addMessageToChat(sender, message, isHtml = false) {
    const container = document.getElementById('chat-messages');
    const isAI = sender === 'ai';

    const messageDiv = document.createElement('div');
    messageDiv.className = isAI ? 'ai-message' : 'user-message';
    messageDiv.style.cssText = `
        margin-bottom: 1rem;
        padding: 1rem;
        background: ${isAI ? 'rgba(56, 189, 248, 0.1)' : 'rgba(129, 140, 248, 0.1)'};
        border-left: 3px solid ${isAI ? 'var(--accent-color)' : 'var(--secondary-color)'};
        border-radius: 0.5rem;
    `;

    const senderDiv = document.createElement('div');
    senderDiv.style.cssText = 'font-weight: 600; margin-bottom: 0.5rem; color: ' + (isAI ? 'var(--accent-color)' : 'var(--secondary-color)');
    senderDiv.textContent = isAI ? 'AI Concierge' : 'You';

    const contentDiv = document.createElement('div');
    if (isHtml) {
        contentDiv.innerHTML = message;
    } else {
        contentDiv.textContent = message;
    }

    messageDiv.appendChild(senderDiv);
    messageDiv.appendChild(contentDiv);
    container.appendChild(messageDiv);

    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

async function getRecommendations() {
    const appetite = document.getElementById('appetite-select').value;
    const container = document.getElementById('recommendations-list');
    const user = JSON.parse(localStorage.getItem('user'));

    container.innerHTML = '<div class="loading">Getting recommendations...</div>';

    try {
        const response = await fetch('/api/v1/ai/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: user.vendor_id || 1,
                current_appetite: appetite
            })
        });

        const result = await response.json();
        if (result.success) {
            container.innerHTML = result.recommendations.map(rec => `
                <div class="metric-item" style="display: block; margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <div class="metric-value">${rec.name}</div>
                        <div style="color: var(--success-color); font-weight: 600;">${(rec.match_score * 100).toFixed(0)}% Match</div>
                    </div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                        ${rec.reason}
                    </div>
                    <div style="font-size: 0.8rem; color: var(--text-secondary);">
                        ${rec.nutrition.calories} cal • ${rec.nutrition.protein} protein
                    </div>
                </div>
            `).join('');

            if (result.personalization_note) {
                container.innerHTML += `
                    <div style="margin-top: 1rem; padding: 0.75rem; background: rgba(56, 189, 248, 0.1); border-radius: 0.5rem; font-size: 0.85rem; color: var(--accent-color);">
                        💡 ${result.personalization_note}
                    </div>
                `;
            }
        }
    } catch (error) {
        container.innerHTML = '<div class="error">Failed to get recommendations</div>';
    }
}

async function getSmartSubstitution(itemName, reason = 'out_of_stock') {
    try {
        const response = await fetch('/api/v1/ai/substitute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                item_name: itemName,
                reason: reason
            })
        });

        const result = await response.json();
        if (result.success) {
            return result.substitutions;
        }
    } catch (error) {
        console.error('Error getting substitution:', error);
    }
    return [];
}
