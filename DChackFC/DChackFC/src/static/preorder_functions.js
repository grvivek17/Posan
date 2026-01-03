
// Preorder Functions
let preorderCart = [];

async function loadVendorMenuForPreorder() {
    const vendorId = document.getElementById('vendor-select')?.value || 1;
    const container = document.getElementById('menu-items');

    try {
        const response = await fetch(`/api/v1/menu/?vendor_id=${vendorId}`);
        const result = await response.json();

        if (result.success) {
            container.innerHTML = result.items.map(item => {
                const outOfStock = item.stock_available === 0;
                const rating = '⭐'.repeat(Math.round(item.avg_rating));

                return `
                    <div class="metric-item" style="display: block; margin-bottom: 1rem; opacity: ${outOfStock ? 0.5 : 1};">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <div>
                                <div class="metric-value">${item.name} ${outOfStock ? '(Out of Stock)' : ''}</div>
                                <div class="metric-label">${item.category} • ${rating} (${item.total_ratings})</div>
                                <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.25rem;">
                                    ${item.nutrition_info.calories} cal • ${item.nutrition_info.protein} protein
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-weight: 600; margin-bottom: 0.5rem;">$${item.price}</div>
                                ${!outOfStock ? `
                                    <button onclick="addToPreorderCart(${item.id}, '${item.name}', ${item.price}, ${item.max_per_order})" 
                                        style="padding: 0.25rem 0.75rem; border-radius: 0.25rem; border: none; background: var(--accent-color); color: white; cursor: pointer;">
                                        Add
                                    </button>
                                ` : ''}
                            </div>
                        </div>
                        ${item.stock_available > 0 && item.stock_available < 10 ? `
                            <div style="font-size: 0.8rem; color: var(--warning-color);">Only ${item.stock_available} left!</div>
                        ` : ''}
                    </div>
                `;
            }).join('');
        }
    } catch (error) {
        console.error('Error loading menu:', error);
    }
}

function addToPreorderCart(id, name, price, maxPerOrder) {
    const existingItem = preorderCart.find(item => item.id === id);

    if (existingItem) {
        if (existingItem.quantity >= maxPerOrder) {
            alert(`Maximum ${maxPerOrder} items allowed per order for ${name}`);
            return;
        }
        existingItem.quantity++;
    } else {
        preorderCart.push({ id, name, price, quantity: 1, maxPerOrder });
    }

    updatePreorderCartUI();
}

function updatePreorderCartUI() {
    const container = document.getElementById('cart-items');
    const totalEl = document.getElementById('cart-total');

    if (preorderCart.length === 0) {
        container.innerHTML = '<div class="loading" style="padding: 1rem;">Cart is empty</div>';
        totalEl.textContent = '$0.00';
        return;
    }

    let total = 0;
    container.innerHTML = preorderCart.map((item, index) => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;
        return `
            <div class="metric-item" style="margin-bottom: 0.5rem;">
                <div style="flex: 1;">
                    <div>${item.name}</div>
                    <div style="font-size: 0.8rem; color: var(--text-secondary);">
                        ${item.quantity} x $${item.price} ${item.quantity >= item.maxPerOrder ? '(Max)' : ''}
                    </div>
                </div>
                <div style="display: flex; gap: 0.5rem; align-items: center;">
                    <span>$${itemTotal.toFixed(2)}</span>
                    <button onclick="removeFromPreorderCart(${index})" style="padding: 0.25rem 0.5rem; border-radius: 0.25rem; border: none; background: var(--danger-color); color: white; cursor: pointer;">×</button>
                </div>
            </div>
        `;
    }).join('');

    totalEl.textContent = `$${total.toFixed(2)}`;
}

function removeFromPreorderCart(index) {
    preorderCart.splice(index, 1);
    updatePreorderCartUI();
}

async function placePreorder() {
    if (preorderCart.length === 0) {
        alert('Cart is empty');
        return;
    }

    const scheduleTime = document.getElementById('schedule-time').value;
    if (!scheduleTime) {
        alert('Please select a pickup time');
        return;
    }

    const user = JSON.parse(localStorage.getItem('user'));
    const vendorId = parseInt(document.getElementById('vendor-select').value);
    const total = preorderCart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const customizationNotes = document.getElementById('customization-notes').value;

    try {
        const response = await fetch('/api/v1/preorder/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                vendor_id: vendorId,
                items: preorderCart,
                total_amount: total,
                customer_name: user.name,
                scheduled_for: new Date(scheduleTime).toISOString(),
                customization_notes: customizationNotes || null
            })
        });

        const result = await response.json();
        if (result.success) {
            window.location.href = `/static/pickup.html?id=${result.preorder.id}`;
        }
    } catch (error) {
        alert('Failed to place preorder');
    }
}

async function loadPreorderDetails(preorderId) {
    try {
        const response = await fetch(`/api/v1/preorder/${preorderId}`);
        const result = await response.json();

        if (result.success) {
            const p = result.preorder;
            document.getElementById('order-number').textContent = p.order_number;
            document.getElementById('qr-code').src = p.qr_code;
            document.getElementById('otp-display').textContent = p.otp;
            document.getElementById('scheduled-time').textContent = new Date(p.scheduled_for).toLocaleString();
            document.getElementById('eta-time').textContent = new Date(p.eta).toLocaleTimeString();
            document.getElementById('total-amount').textContent = `$${p.total_amount.toFixed(2)}`;
            document.getElementById('order-status').textContent = p.status.toUpperCase();

            if (p.customization_notes) {
                document.getElementById('customization-section').style.display = 'block';
                document.getElementById('customization-notes').textContent = p.customization_notes;

                if (p.customization_approved !== null) {
                    const responseText = p.customization_approved
                        ? `✓ Approved ${p.additional_cost > 0 ? `(+$${p.additional_cost})` : ''}`
                        : '✗ Not approved';
                    document.getElementById('customization-response').innerHTML = `
                        <div style="color: ${p.customization_approved ? 'var(--success-color)' : 'var(--danger-color)'}; font-weight: 600;">
                            ${responseText}
                        </div>
                    `;
                } else {
                    document.getElementById('customization-response').innerHTML = `
                        <div style="color: var(--warning-color);">Pending vendor response...</div>
                    `;
                }
            }
        }
    } catch (error) {
        console.error('Error loading preorder:', error);
    }
}
