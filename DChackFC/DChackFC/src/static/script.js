document.addEventListener('DOMContentLoaded', () => {
    // Check if we are on the main dashboard
    if (document.getElementById('peak-hours-content')) {
        fetchDashboardData();
    }

    // Setup login form if exists
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    // Load menu if on vendor page
    if (document.getElementById('menu-list')) {
        loadVendorMenu();
    }
});

// Auth Functions
async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const role = document.getElementById('role').value;
    const errorMsg = document.getElementById('error-msg');

    try {
        const response = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, role })
        });

        const data = await response.json();

        if (data.success) {
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));

            if (role === 'vendor') {
                window.location.href = '/static/vendor.html';
            } else if (role === 'admin') {
                window.location.href = '/static/admin.html';
            } else {
                window.location.href = '/static/order.html';
            }
        } else {
            errorMsg.textContent = 'Invalid credentials';
            errorMsg.style.display = 'block';
        }
    } catch (error) {
        errorMsg.textContent = 'Login failed';
        errorMsg.style.display = 'block';
    }
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/static/login.html';
}

// Order Functions
let cart = [];

function addToCart(name, price) {
    cart.push({ name, price, quantity: 1 });
    updateCartUI();
}

function updateCartUI() {
    const container = document.getElementById('cart-items');
    const totalEl = document.getElementById('cart-total');

    if (cart.length === 0) {
        container.innerHTML = '<div class="loading" style="padding: 1rem;">Cart is empty</div>';
        totalEl.textContent = '$0.00';
        return;
    }

    let total = 0;
    container.innerHTML = cart.map((item, index) => {
        total += item.price;
        return `
            <div class="metric-item" style="margin-bottom: 0.5rem;">
                <span>${item.name}</span>
                <span>$${item.price}</span>
            </div>
        `;
    }).join('');

    totalEl.textContent = `$${total.toFixed(2)}`;
}

async function placeOrder() {
    if (cart.length === 0) return;

    const user = JSON.parse(localStorage.getItem('user'));
    const total = cart.reduce((sum, item) => sum + item.price, 0);

    try {
        const response = await fetch('/api/v1/orders/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                vendor_id: 1, // Default to 1 for now, should be dynamic based on selection
                items: cart,
                total_amount: total,
                customer_name: user.name
            })
        });

        const result = await response.json();
        if (result.success) {
            alert('Order placed successfully! Order #' + result.order.order_number);
            cart = [];
            updateCartUI();
        }
    } catch (error) {
        alert('Failed to place order');
    }
}

// Vendor Functions
async function loadVendorOrders() {
    const container = document.getElementById('orders-list');
    if (!container) return;

    const user = JSON.parse(localStorage.getItem('user'));
    const vendorId = user.vendor_id || 1;

    try {
        const response = await fetch(`/api/v1/orders/vendor/${vendorId}`);
        const result = await response.json();

        if (result.success && result.orders.length > 0) {
            container.innerHTML = result.orders.map(order => `
                <div class="metric-item" style="display: block; margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span style="color: var(--accent-color); font-weight: 600;">${order.order_number}</span>
                        <span class="metric-label">${new Date(order.created_at).toLocaleTimeString()}</span>
                    </div>
                    <div style="margin-bottom: 0.5rem;">
                        ${order.items.map(item => `<div>${item.quantity}x ${item.name}</div>`).join('')}
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 0.5rem;">
                        <span style="font-weight: 600;">$${order.total_amount.toFixed(2)}</span>
                        <span style="background: rgba(255,255,255,0.1); padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.8rem;">${order.status}</span>
                    </div>
                </div>
            `).join('');

            // Update stats
            document.getElementById('total-orders').textContent = result.orders.length;
            const revenue = result.orders.reduce((sum, o) => sum + o.total_amount, 0);
            document.getElementById('total-revenue').textContent = `$${revenue.toFixed(2)}`;
        } else {
            container.innerHTML = '<div class="loading">No active orders</div>';
        }
    } catch (error) {
        console.error('Error loading orders:', error);
    }
}

async function loadVendorMenu() {
    const container = document.getElementById('menu-list');
    const user = JSON.parse(localStorage.getItem('user'));
    const vendorId = user.vendor_id || 1;

    try {
        const response = await fetch(`/api/v1/menu/?vendor_id=${vendorId}`);
        const result = await response.json();

        if (result.success) {
            container.innerHTML = result.items.map(item => `
                <div class="metric-item">
                    <div>
                        <div class="metric-value">${item.name}</div>
                        <div class="metric-label">${item.category}</div>
                    </div>
                    <div style="font-weight: 600;">$${item.price}</div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading menu:', error);
    }
}

async function addMenuItem() {
    const name = document.getElementById('new-item-name').value;
    const price = parseFloat(document.getElementById('new-item-price').value);
    const category = document.getElementById('new-item-category').value;
    const user = JSON.parse(localStorage.getItem('user'));

    if (!name || !price) return;

    try {
        const response = await fetch('/api/v1/menu/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                vendor_id: user.vendor_id || 1,
                name,
                price,
                category
            })
        });

        const result = await response.json();
        if (result.success) {
            loadVendorMenu();
            document.getElementById('new-item-name').value = '';
            document.getElementById('new-item-price').value = '';
        }
    } catch (error) {
        alert('Failed to add item');
    }
}

// Admin Functions
async function loadAdminDashboard() {
    try {
        const [statsRes, vendorsRes] = await Promise.all([
            fetch('/api/v1/admin/stats'),
            fetch('/api/v1/admin/vendors')
        ]);

        const stats = await statsRes.json();
        const vendors = await vendorsRes.json();

        if (stats.success) {
            document.getElementById('total-vendors').textContent = stats.stats.total_vendors;
            document.getElementById('active-vendors').textContent = stats.stats.active_vendors;
            document.getElementById('total-orders').textContent = stats.stats.total_orders;
            document.getElementById('total-revenue').textContent = `$${stats.stats.total_revenue.toFixed(2)}`;
        }

        if (vendors.success) {
            document.getElementById('vendors-list').innerHTML = vendors.vendors.map(v => `
                <div class="metric-item">
                    <div>
                        <div class="metric-value">${v.name}</div>
                        <div class="metric-label">${v.email}</div>
                    </div>
                    <span style="color: ${v.status === 'Active' ? 'var(--success-color)' : 'var(--text-secondary)'}">${v.status}</span>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading admin dashboard:', error);
    }
}

// Dashboard Functions (Existing)
async function fetchDashboardData() {
    const vendorId = 1;
    try {
        await Promise.all([
            fetchPeakHours(vendorId),
            fetchInventory(vendorId),
            fetchPricing(vendorId)
        ]);
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

async function fetchPeakHours(vendorId) {
    const container = document.getElementById('peak-hours-content');
    try {
        const response = await fetch(`/api/v1/forecast/vendors/${vendorId}/forecast/peak-hours`);
        const result = await response.json();

        if (result.success) {
            const html = result.data.map((item, index) => `
                <div class="metric-item" style="animation-delay: ${index * 100}ms">
                    <div style="width: 100%">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span class="metric-label">${formatHour(item.hour)}</span>
                            <span class="metric-value">${item.predicted_orders} orders</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${(item.predicted_orders / 60) * 100}%"></div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 0.25rem; font-size: 0.8rem; color: var(--text-secondary);">
                            <span>Staff needed: ${item.recommended_staff}</span>
                            <span>${(item.confidence_score * 100).toFixed(0)}% confidence</span>
                        </div>
                    </div>
                </div>
            `).join('');
            container.innerHTML = `<div class="metric-container">${html}</div>`;

            setTimeout(() => {
                document.querySelectorAll('.progress-fill').forEach(el => {
                    const width = el.style.width;
                    el.style.width = '0';
                    setTimeout(() => el.style.width = width, 50);
                });
            }, 100);
        }
    } catch (e) {
        container.innerHTML = '<div class="error">Failed to load peak hours</div>';
    }
}

async function fetchInventory(vendorId) {
    const container = document.getElementById('inventory-content');
    try {
        const response = await fetch(`/api/v1/forecast/vendors/${vendorId}/forecast/inventory`);
        const result = await response.json();

        if (result.success) {
            container.innerHTML = '<div class="metric-item"><span class="metric-label">Status</span><span class="metric-value" style="color: var(--success-color)">Optimized</span></div>';
        }
    } catch (e) {
        container.innerHTML = '<div class="error">Failed to load inventory</div>';
    }
}

async function fetchPricing(vendorId) {
    const container = document.getElementById('pricing-content');
    try {
        const response = await fetch(`/api/v1/forecast/vendors/${vendorId}/forecast/pricing`);
        const result = await response.json();

        if (result.success) {
            container.innerHTML = '<div class="metric-item"><span class="metric-label">Strategy</span><span class="metric-value" style="color: var(--accent-color)">Dynamic</span></div>';
        }
    } catch (e) {
        container.innerHTML = '<div class="error">Failed to load pricing</div>';
    }
}

function formatHour(hour) {
    return new Date(0, 0, 0, hour).toLocaleTimeString('en-US', {
        hour: 'numeric',
        hour12: true
    });
}
 
 / /   P r e o r d e r   F u n c t i o n s  
 l e t   p r e o r d e r C a r t   =   [ ] ;  
  
 a s y n c   f u n c t i o n   l o a d V e n d o r M e n u F o r P r e o r d e r ( )   {  
         c o n s t   v e n d o r I d   =   d o c u m e n t . g e t E l e m e n t B y I d ( ' v e n d o r - s e l e c t ' ) ? . v a l u e   | |   1 ;  
         c o n s t   c o n t a i n e r   =   d o c u m e n t . g e t E l e m e n t B y I d ( ' m e n u - i t e m s ' ) ;  
  
         t r y   {  
                 c o n s t   r e s p o n s e   =   a w a i t   f e t c h ( ` / a p i / v 1 / m e n u / ? v e n d o r _ i d = $ { v e n d o r I d } ` ) ;  
                 c o n s t   r e s u l t   =   a w a i t   r e s p o n s e . j s o n ( ) ;  
  
                 i f   ( r e s u l t . s u c c e s s )   {  
                         c o n t a i n e r . i n n e r H T M L   =   r e s u l t . i t e m s . m a p ( i t e m   = >   {  
                                 c o n s t   o u t O f S t o c k   =   i t e m . s t o c k _ a v a i l a b l e   = = =   0 ;  
                                 c o n s t   r a t i n g   =   ' ‚ ≠ ê ' . r e p e a t ( M a t h . r o u n d ( i t e m . a v g _ r a t i n g ) ) ;  
  
                                 r e t u r n   `  
                                         < d i v   c l a s s = " m e t r i c - i t e m "   s t y l e = " d i s p l a y :   b l o c k ;   m a r g i n - b o t t o m :   1 r e m ;   o p a c i t y :   $ { o u t O f S t o c k   ?   0 . 5   :   1 } ; " >  
                                                 < d i v   s t y l e = " d i s p l a y :   f l e x ;   j u s t i f y - c o n t e n t :   s p a c e - b e t w e e n ;   m a r g i n - b o t t o m :   0 . 5 r e m ; " >  
                                                         < d i v >  
                                                                 < d i v   c l a s s = " m e t r i c - v a l u e " > $ { i t e m . n a m e }   $ { o u t O f S t o c k   ?   ' ( O u t   o f   S t o c k ) '   :   ' ' } < / d i v >  
                                                                 < d i v   c l a s s = " m e t r i c - l a b e l " > $ { i t e m . c a t e g o r y }   ‚ ¨ ¢   $ { r a t i n g }   ( $ { i t e m . t o t a l _ r a t i n g s } ) < / d i v >  
                                                                 < d i v   s t y l e = " f o n t - s i z e :   0 . 8 r e m ;   c o l o r :   v a r ( - - t e x t - s e c o n d a r y ) ;   m a r g i n - t o p :   0 . 2 5 r e m ; " >  
                                                                         $ { i t e m . n u t r i t i o n _ i n f o . c a l o r i e s }   c a l   ‚ ¨ ¢   $ { i t e m . n u t r i t i o n _ i n f o . p r o t e i n }   p r o t e i n  
                                                                 < / d i v >  
                                                         < / d i v >  
                                                         < d i v   s t y l e = " t e x t - a l i g n :   r i g h t ; " >  
                                                                 < d i v   s t y l e = " f o n t - w e i g h t :   6 0 0 ;   m a r g i n - b o t t o m :   0 . 5 r e m ; " > $ $ { i t e m . p r i c e } < / d i v >  
                                                                 $ { ! o u t O f S t o c k   ?   `  
                                                                         < b u t t o n   o n c l i c k = " a d d T o P r e o r d e r C a r t ( $ { i t e m . i d } ,   ' $ { i t e m . n a m e } ' ,   $ { i t e m . p r i c e } ,   $ { i t e m . m a x _ p e r _ o r d e r } ) "    
                                                                                 s t y l e = " p a d d i n g :   0 . 2 5 r e m   0 . 7 5 r e m ;   b o r d e r - r a d i u s :   0 . 2 5 r e m ;   b o r d e r :   n o n e ;   b a c k g r o u n d :   v a r ( - - a c c e n t - c o l o r ) ;   c o l o r :   w h i t e ;   c u r s o r :   p o i n t e r ; " >  
                                                                                 A d d  
                                                                         < / b u t t o n >  
                                                                 `   :   ' ' }  
                                                         < / d i v >  
                                                 < / d i v >  
                                                 $ { i t e m . s t o c k _ a v a i l a b l e   >   0   & &   i t e m . s t o c k _ a v a i l a b l e   <   1 0   ?   `  
                                                         < d i v   s t y l e = " f o n t - s i z e :   0 . 8 r e m ;   c o l o r :   v a r ( - - w a r n i n g - c o l o r ) ; " > O n l y   $ { i t e m . s t o c k _ a v a i l a b l e }   l e f t ! < / d i v >  
                                                 `   :   ' ' }  
                                         < / d i v >  
                                 ` ;  
                         } ) . j o i n ( ' ' ) ;  
                 }  
         }   c a t c h   ( e r r o r )   {  
                 c o n s o l e . e r r o r ( ' E r r o r   l o a d i n g   m e n u : ' ,   e r r o r ) ;  
         }  
 }  
  
 f u n c t i o n   a d d T o P r e o r d e r C a r t ( i d ,   n a m e ,   p r i c e ,   m a x P e r O r d e r )   {  
         c o n s t   e x i s t i n g I t e m   =   p r e o r d e r C a r t . f i n d ( i t e m   = >   i t e m . i d   = = =   i d ) ;  
  
         i f   ( e x i s t i n g I t e m )   {  
                 i f   ( e x i s t i n g I t e m . q u a n t i t y   > =   m a x P e r O r d e r )   {  
                         a l e r t ( ` M a x i m u m   $ { m a x P e r O r d e r }   i t e m s   a l l o w e d   p e r   o r d e r   f o r   $ { n a m e } ` ) ;  
                         r e t u r n ;  
                 }  
                 e x i s t i n g I t e m . q u a n t i t y + + ;  
         }   e l s e   {  
                 p r e o r d e r C a r t . p u s h ( {   i d ,   n a m e ,   p r i c e ,   q u a n t i t y :   1 ,   m a x P e r O r d e r   } ) ;  
         }  
  
         u p d a t e P r e o r d e r C a r t U I ( ) ;  
 }  
  
 f u n c t i o n   u p d a t e P r e o r d e r C a r t U I ( )   {  
         c o n s t   c o n t a i n e r   =   d o c u m e n t . g e t E l e m e n t B y I d ( ' c a r t - i t e m s ' ) ;  
         c o n s t   t o t a l E l   =   d o c u m e n t . g e t E l e m e n t B y I d ( ' c a r t - t o t a l ' ) ;  
  
         i f   ( p r e o r d e r C a r t . l e n g t h   = = =   0 )   {  
                 c o n t a i n e r . i n n e r H T M L   =   ' < d i v   c l a s s = " l o a d i n g "   s t y l e = " p a d d i n g :   1 r e m ; " > C a r t   i s   e m p t y < / d i v > ' ;  
                 t o t a l E l . t e x t C o n t e n t   =   ' $ 0 . 0 0 ' ;  
                 r e t u r n ;  
         }  
  
         l e t   t o t a l   =   0 ;  
         c o n t a i n e r . i n n e r H T M L   =   p r e o r d e r C a r t . m a p ( ( i t e m ,   i n d e x )   = >   {  
                 c o n s t   i t e m T o t a l   =   i t e m . p r i c e   *   i t e m . q u a n t i t y ;  
                 t o t a l   + =   i t e m T o t a l ;  
                 r e t u r n   `  
                         < d i v   c l a s s = " m e t r i c - i t e m "   s t y l e = " m a r g i n - b o t t o m :   0 . 5 r e m ; " >  
                                 < d i v   s t y l e = " f l e x :   1 ; " >  
                                         < d i v > $ { i t e m . n a m e } < / d i v >  
                                         < d i v   s t y l e = " f o n t - s i z e :   0 . 8 r e m ;   c o l o r :   v a r ( - - t e x t - s e c o n d a r y ) ; " >  
                                                 $ { i t e m . q u a n t i t y }   x   $ $ { i t e m . p r i c e }   $ { i t e m . q u a n t i t y   > =   i t e m . m a x P e r O r d e r   ?   ' ( M a x ) '   :   ' ' }  
                                         < / d i v >  
                                 < / d i v >  
                                 < d i v   s t y l e = " d i s p l a y :   f l e x ;   g a p :   0 . 5 r e m ;   a l i g n - i t e m s :   c e n t e r ; " >  
                                         < s p a n > $ $ { i t e m T o t a l . t o F i x e d ( 2 ) } < / s p a n >  
                                         < b u t t o n   o n c l i c k = " r e m o v e F r o m P r e o r d e r C a r t ( $ { i n d e x } ) "   s t y l e = " p a d d i n g :   0 . 2 5 r e m   0 . 5 r e m ;   b o r d e r - r a d i u s :   0 . 2 5 r e m ;   b o r d e r :   n o n e ;   b a c k g r o u n d :   v a r ( - - d a n g e r - c o l o r ) ;   c o l o r :   w h i t e ;   c u r s o r :   p o i n t e r ; " > √  < / b u t t o n >  
                                 < / d i v >  
                         < / d i v >  
                 ` ;  
         } ) . j o i n ( ' ' ) ;  
  
         t o t a l E l . t e x t C o n t e n t   =   ` $ $ { t o t a l . t o F i x e d ( 2 ) } ` ;  
 }  
  
 f u n c t i o n   r e m o v e F r o m P r e o r d e r C a r t ( i n d e x )   {  
         p r e o r d e r C a r t . s p l i c e ( i n d e x ,   1 ) ;  
         u p d a t e P r e o r d e r C a r t U I ( ) ;  
 }  
  
 a s y n c   f u n c t i o n   p l a c e P r e o r d e r ( )   {  
         i f   ( p r e o r d e r C a r t . l e n g t h   = = =   0 )   {  
                 a l e r t ( ' C a r t   i s   e m p t y ' ) ;  
                 r e t u r n ;  
         }  
  
         c o n s t   s c h e d u l e T i m e   =   d o c u m e n t . g e t E l e m e n t B y I d ( ' s c h e d u l e - t i m e ' ) . v a l u e ;  
         i f   ( ! s c h e d u l e T i m e )   {  
                 a l e r t ( ' P l e a s e   s e l e c t   a   p i c k u p   t i m e ' ) ;  
                 r e t u r n ;  
         }  
  
         c o n s t   u s e r   =   J S O N . p a r s e ( l o c a l S t o r a g e . g e t I t e m ( ' u s e r ' ) ) ;  
         c o n s t   v e n d o r I d   =   p a r s e I n t ( d o c u m e n t . g e t E l e m e n t B y I d ( ' v e n d o r - s e l e c t ' ) . v a l u e ) ;  
         c o n s t   t o t a l   =   p r e o r d e r C a r t . r e d u c e ( ( s u m ,   i t e m )   = >   s u m   +   ( i t e m . p r i c e   *   i t e m . q u a n t i t y ) ,   0 ) ;  
         c o n s t   c u s t o m i z a t i o n N o t e s   =   d o c u m e n t . g e t E l e m e n t B y I d ( ' c u s t o m i z a t i o n - n o t e s ' ) . v a l u e ;  
  
         t r y   {  
                 c o n s t   r e s p o n s e   =   a w a i t   f e t c h ( ' / a p i / v 1 / p r e o r d e r / ' ,   {  
                         m e t h o d :   ' P O S T ' ,  
                         h e a d e r s :   {   ' C o n t e n t - T y p e ' :   ' a p p l i c a t i o n / j s o n '   } ,  
                         b o d y :   J S O N . s t r i n g i f y ( {  
                                 v e n d o r _ i d :   v e n d o r I d ,  
                                 i t e m s :   p r e o r d e r C a r t ,  
                                 t o t a l _ a m o u n t :   t o t a l ,  
                                 c u s t o m e r _ n a m e :   u s e r . n a m e ,  
                                 s c h e d u l e d _ f o r :   n e w   D a t e ( s c h e d u l e T i m e ) . t o I S O S t r i n g ( ) ,  
                                 c u s t o m i z a t i o n _ n o t e s :   c u s t o m i z a t i o n N o t e s   | |   n u l l  
                         } )  
                 } ) ;  
  
                 c o n s t   r e s u l t   =   a w a i t   r e s p o n s e . j s o n ( ) ;  
                 i f   ( r e s u l t . s u c c e s s )   {  
                         w i n d o w . l o c a t i o n . h r e f   =   ` / s t a t i c / p i c k u p . h t m l ? i d = $ { r e s u l t . p r e o r d e r . i d } ` ;  
                 }  
         }   c a t c h   ( e r r o r )   {  
                 a l e r t ( ' F a i l e d   t o   p l a c e   p r e o r d e r ' ) ;  
         }  
 }  
  
 a s y n c   f u n c t i o n   l o a d P r e o r d e r D e t a i l s ( p r e o r d e r I d )   {  
         t r y   {  
                 c o n s t   r e s p o n s e   =   a w a i t   f e t c h ( ` / a p i / v 1 / p r e o r d e r / $ { p r e o r d e r I d } ` ) ;  
                 c o n s t   r e s u l t   =   a w a i t   r e s p o n s e . j s o n ( ) ;  
  
                 i f   ( r e s u l t . s u c c e s s )   {  
                         c o n s t   p   =   r e s u l t . p r e o r d e r ;  
                         d o c u m e n t . g e t E l e m e n t B y I d ( ' o r d e r - n u m b e r ' ) . t e x t C o n t e n t   =   p . o r d e r _ n u m b e r ;  
                         d o c u m e n t . g e t E l e m e n t B y I d ( ' q r - c o d e ' ) . s r c   =   p . q r _ c o d e ;  
                         d o c u m e n t . g e t E l e m e n t B y I d ( ' o t p - d i s p l a y ' ) . t e x t C o n t e n t   =   p . o t p ;  
                         d o c u m e n t . g e t E l e m e n t B y I d ( ' s c h e d u l e d - t i m e ' ) . t e x t C o n t e n t   =   n e w   D a t e ( p . s c h e d u l e d _ f o r ) . t o L o c a l e S t r i n g ( ) ;  
                         d o c u m e n t . g e t E l e m e n t B y I d ( ' e t a - t i m e ' ) . t e x t C o n t e n t   =   n e w   D a t e ( p . e t a ) . t o L o c a l e T i m e S t r i n g ( ) ;  
                         d o c u m e n t . g e t E l e m e n t B y I d ( ' t o t a l - a m o u n t ' ) . t e x t C o n t e n t   =   ` $ $ { p . t o t a l _ a m o u n t . t o F i x e d ( 2 ) } ` ;  
                         d o c u m e n t . g e t E l e m e n t B y I d ( ' o r d e r - s t a t u s ' ) . t e x t C o n t e n t   =   p . s t a t u s . t o U p p e r C a s e ( ) ;  
  
                         i f   ( p . c u s t o m i z a t i o n _ n o t e s )   {  
                                 d o c u m e n t . g e t E l e m e n t B y I d ( ' c u s t o m i z a t i o n - s e c t i o n ' ) . s t y l e . d i s p l a y   =   ' b l o c k ' ;  
                                 d o c u m e n t . g e t E l e m e n t B y I d ( ' c u s t o m i z a t i o n - n o t e s ' ) . t e x t C o n t e n t   =   p . c u s t o m i z a t i o n _ n o t e s ;  
  
                                 i f   ( p . c u s t o m i z a t i o n _ a p p r o v e d   ! = =   n u l l )   {  
                                         c o n s t   r e s p o n s e T e x t   =   p . c u s t o m i z a t i o n _ a p p r o v e d  
                                                 ?   ` ‚ S   A p p r o v e d   $ { p . a d d i t i o n a l _ c o s t   >   0   ?   ` ( + $ $ { p . a d d i t i o n a l _ c o s t } ) `   :   ' ' } `  
                                                 :   ' ‚ S   N o t   a p p r o v e d ' ;  
                                         d o c u m e n t . g e t E l e m e n t B y I d ( ' c u s t o m i z a t i o n - r e s p o n s e ' ) . i n n e r H T M L   =   `  
                                                 < d i v   s t y l e = " c o l o r :   $ { p . c u s t o m i z a t i o n _ a p p r o v e d   ?   ' v a r ( - - s u c c e s s - c o l o r ) '   :   ' v a r ( - - d a n g e r - c o l o r ) ' } ;   f o n t - w e i g h t :   6 0 0 ; " >  
                                                         $ { r e s p o n s e T e x t }  
                                                 < / d i v >  
                                         ` ;  
                                 }   e l s e   {  
                                         d o c u m e n t . g e t E l e m e n t B y I d ( ' c u s t o m i z a t i o n - r e s p o n s e ' ) . i n n e r H T M L   =   `  
                                                 < d i v   s t y l e = " c o l o r :   v a r ( - - w a r n i n g - c o l o r ) ; " > P e n d i n g   v e n d o r   r e s p o n s e . . . < / d i v >  
                                         ` ;  
                                 }  
                         }  
                 }  
         }   c a t c h   ( e r r o r )   {  
                 c o n s o l e . e r r o r ( ' E r r o r   l o a d i n g   p r e o r d e r : ' ,   e r r o r ) ;  
         }  
 }  
 