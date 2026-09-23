// ============================================
// CART.JS - سبد خرید (بدون پنل تنظیمات)
// ============================================

// تبدیل عدد به فارسی
function toPersianNumber(num) {
    const persianDigits = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
    return num.toString().replace(/\d/g, d => persianDigits[d]);
}

// فرمت قیمت به تومان (فارسی)
function formatPrice(price) {
    const formatted = price.toLocaleString();
    return toPersianNumber(formatted) + ' تومان';
}

// کلاس سبد خرید
class ShoppingCart {
    constructor() {
        this.items = this.loadFromStorage();
        this.updateCartUI();
        this.updateCartBadge();
    }

    loadFromStorage() {
        const saved = localStorage.getItem('polaris_cart');
        return saved ? JSON.parse(saved) : [];
    }

    saveToStorage() {
        localStorage.setItem('polaris_cart', JSON.stringify(this.items));
        this.updateCartUI();
        this.updateCartBadge();
        window.dispatchEvent(new Event('storage'));
    }

    addItem(course) {
        const exists = this.items.find(item => item.id === course.id);
        if (!exists) {
            this.items.push({
                id: course.id,
                title: course.title,
                price: course.price,
                image: course.image
            });
            this.saveToStorage();
            this.showToast('✅ دوره به سبد خرید اضافه شد');
        } else {
            this.showToast('ℹ️ این دوره قبلاً در سبد خرید است');
        }
    }

    removeItem(id) {
        this.items = this.items.filter(item => item.id !== id);
        this.saveToStorage();
        this.showToast('🗑️ دوره از سبد خرید حذف شد');
        this.updateCartUI();
    }

    getTotal() {
        return this.items.reduce((sum, item) => sum + item.price, 0);
    }

    updateCartBadge() {
        const badges = document.querySelectorAll('#cartCountBadge, .cart-count, #cartCountHeader');
        const count = this.items.length;
        badges.forEach(badge => {
            if (badge) {
                badge.textContent = count;
                badge.style.display = count > 0 ? 'inline-flex' : 'none';
            }
        });
    }

    updateCartUI() {
        const container = document.getElementById('cartItemsContainer');
        if (!container) return;

        if (this.items.length === 0) {
            container.innerHTML = `
                <div class="empty-cart">
                    <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <circle cx="9" cy="21" r="1"></circle>
                        <circle cx="20" cy="21" r="1"></circle>
                        <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
                    </svg>
                    <h3>سبد خرید شما خالی است</h3>
                    <p>دوره مورد نظر خود را از صفحه دوره‌ها انتخاب کنید.</p>
                    <a href="courses.html" class="btn btn-primary" style="margin-top: 20px;">مشاهده دوره‌ها</a>
                </div>
            `;
            const summary = document.getElementById('cartSummary');
            if (summary) summary.style.opacity = '0.5';
            
            const itemCountEl = document.getElementById('summaryItemCount');
            const totalEl = document.getElementById('summaryTotal');
            const payableEl = document.getElementById('summaryPayable');
            if (itemCountEl) itemCountEl.innerHTML = '0';
            if (totalEl) totalEl.innerHTML = `0 تومان`;
            if (payableEl) payableEl.innerHTML = `0 تومان`;
            return;
        }

        const summary = document.getElementById('cartSummary');
        if (summary) summary.style.opacity = '1';

        let html = '';
        this.items.forEach(item => {
            html += `
                <div class="cart-item" data-id="${item.id}">
                    <img src="${item.image || 'assets/image/front.jpg'}" alt="${item.title}" onerror="this.src='assets/image/front.jpg'">
                    <div class="cart-item-info">
                        <h4>${item.title}</h4>
                        <span class="cart-item-price">${formatPrice(item.price)}</span>
                    </div>
                    <button class="cart-item-remove" onclick="cart.removeItem(${item.id})" title="حذف">✕</button>
                </div>
            `;
        });
        container.innerHTML = html;

        const total = this.getTotal();
        const itemCount = this.items.length;

        const itemCountEl = document.getElementById('summaryItemCount');
        const totalEl = document.getElementById('summaryTotal');
        const payableEl = document.getElementById('summaryPayable');

        if (itemCountEl) itemCountEl.innerHTML = toPersianNumber(itemCount);
        if (totalEl) totalEl.innerHTML = formatPrice(total);
        if (payableEl) payableEl.innerHTML = formatPrice(total);
    }

    showToast(message) {
        const oldToast = document.querySelector('.custom-toast');
        if (oldToast) oldToast.remove();
        
        const toast = document.createElement('div');
        toast.className = 'custom-toast';
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: linear-gradient(135deg, #00f2fe, #4facfe);
            color: white;
            padding: 12px 24px;
            border-radius: 50px;
            z-index: 9999;
            font-weight: 600;
            animation: slideIn 0.3s ease;
            box-shadow: 0 5px 20px rgba(0,0,0,0.3);
            font-family: 'Peyda', sans-serif;
        `;
        document.body.appendChild(toast);
        setTimeout(() => {
            if (toast) toast.remove();
        }, 3000);
    }
}

// نمونه گلوبال از سبد خرید
const cart = new ShoppingCart();

// تابع پرداخت
function proceedToCheckout() {
    if (cart.items.length === 0) {
        cart.showToast('⚠️ سبد خرید شما خالی است!');
        return;
    }
    window.location.href = 'checkout.html';
}

// انیمیشن toast
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    .empty-cart { text-align: center; padding: 60px 20px; }
    .empty-cart svg { width: 80px; height: 80px; margin-bottom: 20px; opacity: 0.5; stroke: var(--text-muted); }
    .empty-cart h3 { margin-bottom: 15px; font-size: 1.3rem; }
    .empty-cart p { color: var(--text-muted); margin-bottom: 10px; }
    .cart-count, #cartCountBadge, #cartCountHeader { 
        position: absolute; 
        top: -8px; 
        right: -8px; 
        background: linear-gradient(135deg, #00f2fe, #4facfe); 
        color: white; 
        font-size: 0.65rem; 
        font-weight: bold; 
        min-width: 18px; 
        height: 18px; 
        border-radius: 50%; 
        display: inline-flex; 
        align-items: center; 
        justify-content: center; 
        padding: 0 4px;
    }
    .header-actions { position: relative; }
    .cart-btn { position: relative; }
`;
document.head.appendChild(style);

// مقداردهی اولیه هنگام لود صفحه
document.addEventListener('DOMContentLoaded', () => {
    cart.updateCartBadge();
    
    // همگام‌سازی با سایر تب‌ها
    window.addEventListener('focus', () => {
        cart.items = cart.loadFromStorage();
        cart.updateCartUI();
        cart.updateCartBadge();
    });
    
    window.addEventListener('storage', (e) => {
        if (e.key === 'polaris_cart') {
            cart.items = cart.loadFromStorage();
            cart.updateCartUI();
            cart.updateCartBadge();
        }
    });
});