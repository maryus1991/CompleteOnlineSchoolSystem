// ============================================
// CART-PAGE.JS - اسکریپت صفحه سبد خرید
// ============================================

function formatPrice(price) {
    return price.toLocaleString() + " تومان";
}

function renderCartItems() {
    const cartItems = JSON.parse(localStorage.getItem("polaris_cart") || "[]");
    const container = document.getElementById("cartItemsContainer");
    const summaryContainer = document.getElementById("cartSummary");
    
    if (!container) return;
    
    if (cartItems.length === 0) {
        container.innerHTML = `
            <div class="empty-cart">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <circle cx="9" cy="21" r="1"/>
                    <circle cx="20" cy="21" r="1"/>
                    <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
                </svg>
                <h3>سبد خرید شما خالی است</h3>
                <p>دوره مورد نظر خود را از صفحه دوره‌ها انتخاب کنید.</p>
                <a href="courses.html" class="btn btn-primary" style="margin-top: 20px;">مشاهده دوره‌ها</a>
            </div>
        `;
        if (summaryContainer) summaryContainer.style.display = "none";
        updateCartCount();
        return;
    }
    
    if (summaryContainer) summaryContainer.style.display = "block";
    
    let html = "";
    let total = 0;
    
    cartItems.forEach((item, index) => {
        total += item.price;
        html += `
            <div class="cart-item" data-id="${item.id}">
                <img src="${item.image || 'assets/image/default-course.jpg'}" alt="${item.title}" onerror="this.src='assets/image/default-course.jpg'">
                <div class="cart-item-info">
                    <h4>${item.title}</h4>
                    <span class="cart-item-price">${formatPrice(item.price)}</span>
                </div>
                <button class="cart-item-remove" onclick="removeFromCart(${item.id})">✕</button>
            </div>
        `;
    });
    
    container.innerHTML = html;
    
    // به‌روزرسانی خلاصه سبد خرید
    document.getElementById("summaryItemCount").textContent = cartItems.length;
    document.getElementById("summaryTotal").textContent = formatPrice(total);
    document.getElementById("summaryPayable").textContent = formatPrice(total);
    
    updateCartCount();
}

function removeFromCart(courseId) {
    let cartItems = JSON.parse(localStorage.getItem("polaris_cart") || "[]");
    cartItems = cartItems.filter(item => item.id !== courseId);
    localStorage.setItem("polaris_cart", JSON.stringify(cartItems));
    renderCartItems();
    showToast("🗑️ دوره از سبد خرید حذف شد");
}

function proceedToCheckout() {
    const cartItems = JSON.parse(localStorage.getItem("polaris_cart") || "[]");
    if (cartItems.length === 0) {
        showToast("⚠️ سبد خرید شما خالی است!");
        return;
    }
    window.location.href = "checkout.html";
}

function showToast(message) {
    const toast = document.createElement("div");
    toast.className = "cart-toast";
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        background: var(--accent-gradient);
        color: white;
        padding: 12px 24px;
        border-radius: 50px;
        z-index: 9999;
        font-weight: 600;
        animation: slideInRight 0.3s ease;
    `;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function updateCartCount() {
    const cartItems = JSON.parse(localStorage.getItem("polaris_cart") || "[]");
    const countElements = document.querySelectorAll(".cart-count");
    countElements.forEach(el => {
        el.textContent = cartItems.length;
        el.style.display = cartItems.length > 0 ? "inline-flex" : "none";
    });
}

// استایل انیمیشن
const style = document.createElement("style");
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
`;
document.head.appendChild(style);

document.addEventListener("DOMContentLoaded", function() {
    renderCartItems();
});