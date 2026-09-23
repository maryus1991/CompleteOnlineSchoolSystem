// ============================================
// PAYMENT-STATUS.JS - اسکریپت صفحات وضعیت پرداخت
// ============================================

function formatPrice(price) {
    return price.toLocaleString() + " تومان";
}

document.addEventListener("DOMContentLoaded", function() {
    const urlParams = new URLSearchParams(window.location.search);
    const ref = urlParams.get("ref");
    
    const paymentData = JSON.parse(localStorage.getItem("last_payment") || "{}");
    
    // بررسی اینکه در صفحه موفق هستیم یا ناموفق
    const isSuccessPage = window.location.pathname.includes("payment-success");
    
    if (isSuccessPage) {
        displaySuccessPage(paymentData);
    } else {
        displayFailedPage(paymentData);
    }
});

function displaySuccessPage(paymentData) {
    if (paymentData.status !== "success") {
        // اگر اطلاعات پرداخت موفق وجود نداشت
        document.getElementById("transactionId").textContent = "نامشخص";
        document.getElementById("paymentAmount").textContent = "0 تومان";
        document.getElementById("paymentDate").textContent = "-";
        return;
    }
    
    document.getElementById("transactionId").textContent = paymentData.paymentId || "-";
    document.getElementById("paymentAmount").textContent = formatPrice(paymentData.amount || 0);
    document.getElementById("paymentDate").textContent = paymentData.date || new Date().toLocaleDateString("fa-IR");
    
    // نمایش دوره‌های خریداری شده
    const purchasedContainer = document.getElementById("purchasedCourses");
    if (purchasedContainer && paymentData.items && paymentData.items.length > 0) {
        let html = "<h4>📚 دوره‌های خریداری شده:</h4>";
        paymentData.items.forEach(item => {
            html += `
                <div class="course-list-item">
                    <span>${item.title}</span>
                    <span>${formatPrice(item.price)}</span>
                </div>
            `;
        });
        purchasedContainer.innerHTML = html;
    }
}

function displayFailedPage(paymentData) {
    document.getElementById("failedTransactionId").textContent = paymentData.paymentId || "-";
    document.getElementById("failedAmount").textContent = formatPrice(paymentData.amount || 0);
}