// ============================================
// CHECKOUT.JS - صفحه تسویه حساب (بدون پنل تنظیمات)
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

// بارگذاری محصولات سبد خرید
function loadOrderSummary() {
    const cartItems = JSON.parse(localStorage.getItem("polaris_cart") || "[]");
    const container = document.getElementById("checkoutItems");
    
    if (!container) return;
    
    if (cartItems.length === 0) {
        container.innerHTML = `
            <div class="empty-cart-message">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <circle cx="9" cy="21" r="1"/>
                    <circle cx="20" cy="21" r="1"/>
                    <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
                </svg>
                <p>سبد خرید شما خالی است</p>
                <a href="courses.html" class="btn btn-primary" style="margin-top: 20px;">مشاهده دوره‌ها</a>
            </div>
        `;
        document.getElementById("checkoutTotal").innerHTML = formatPrice(0);
        document.getElementById("checkoutPayable").innerHTML = formatPrice(0);
        return;
    }
    
    let html = '<div class="cart-items-list">';
    let total = 0;
    
    cartItems.forEach(item => {
        total += item.price;
        html += `
            <div class="checkout-item">
                <div class="checkout-item-info">
                    <div class="checkout-item-image">
                        <img src="${item.image || 'assets/image/front.jpg'}" alt="${item.title}" onerror="this.src='assets/image/front.jpg'">
                    </div>
                    <div class="checkout-item-details">
                        <h4>${item.title}</h4>
                        <span class="checkout-item-price">${formatPrice(item.price)}</span>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
    document.getElementById("checkoutTotal").innerHTML = formatPrice(total);
    document.getElementById("checkoutPayable").innerHTML = formatPrice(total);
}

// پردازش تسویه حساب
function processCheckout(event) {
    event.preventDefault();
    
    const cartItems = JSON.parse(localStorage.getItem("polaris_cart") || "[]");
    if (cartItems.length === 0) {
        alert("⚠️ سبد خرید شما خالی است!");
        return false;
    }
    
    const fullName = document.getElementById("fullName")?.value;
    const phone = document.getElementById("phone")?.value;
    const email = document.getElementById("email")?.value;
    
    if (!fullName || !phone || !email) {
        alert("❌ لطفاً تمام فیلدهای ضروری را پر کنید!");
        return false;
    }
    
    const selectedMethod = document.querySelector(".payment-card.active")?.dataset.method || "zarinpal";
    const total = cartItems.reduce((sum, item) => sum + item.price, 0);
    const paymentId = "PAY-" + Date.now();
    
    const paymentData = {
        status: "processing",
        amount: total,
        paymentId: paymentId,
        date: new Date().toLocaleDateString("fa-IR"),
        items: cartItems,
        userInfo: {
            fullName: fullName,
            phone: phone,
            email: email,
            nationalCode: document.getElementById("nationalCode")?.value || '',
            postalCode: document.getElementById("postalCode")?.value || '',
            address: document.getElementById("address")?.value || ''
        }
    };
    localStorage.setItem("last_payment", JSON.stringify(paymentData));
    
    const isSuccess = Math.random() > 0.2;
    
    if (isSuccess) {
        paymentData.status = "success";
        localStorage.setItem("last_payment", JSON.stringify(paymentData));
        
        let enrolled = JSON.parse(localStorage.getItem("polaris_enrolled") || "[]");
        cartItems.forEach(item => {
            if (!enrolled.find(e => e.id === item.id)) {
                enrolled.push({
                    id: item.id,
                    title: item.title,
                    price: item.price,
                    image: item.image,
                    progress: 0,
                    purchaseDate: new Date().toISOString()
                });
            }
        });
        localStorage.setItem("polaris_enrolled", JSON.stringify(enrolled));
        localStorage.setItem("polaris_cart", "[]");
        
        window.location.href = "payment-success.html?ref=" + paymentId;
    } else {
        paymentData.status = "failed";
        localStorage.setItem("last_payment", JSON.stringify(paymentData));
        window.location.href = "payment-failed.html?ref=" + paymentId;
    }
    
    return false;
}

// آپدیت بج سبد خرید
function updateCartBadge() {
    const cartItems = JSON.parse(localStorage.getItem("polaris_cart") || "[]");
    const badge = document.getElementById('cartCountBadge');
    if (badge) {
        badge.textContent = cartItems.length;
        badge.style.display = cartItems.length > 0 ? 'inline-flex' : 'none';
    }
}

// مقداردهی اولیه
document.addEventListener("DOMContentLoaded", function() {
    // بارگذاری محصولات
    loadOrderSummary();
    
    // آپدیت بج سبد خرید
    updateCartBadge();
    
    // انتخاب روش پرداخت
    document.querySelectorAll(".payment-card").forEach(method => {
        method.addEventListener("click", () => {
            document.querySelectorAll(".payment-card").forEach(m => m.classList.remove("active"));
            method.classList.add("active");
        });
    });
    
    // ثبت فرم
    const form = document.getElementById('checkoutForm');
    if (form) {
        form.addEventListener('submit', processCheckout);
    }
    
    // همگام‌سازی با تغییرات سبد خرید در تب دیگر
    window.addEventListener('storage', (e) => {
        if (e.key === 'polaris_cart') {
            loadOrderSummary();
            updateCartBadge();
        }
    });
});