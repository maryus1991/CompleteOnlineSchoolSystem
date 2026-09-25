document.addEventListener('DOMContentLoaded', function() {
    
    // فعال‌سازی منوی موبایل
    const mobileToggle = document.getElementById('mobileToggle');
    const mobileMenu = document.getElementById('mobileMenu');
    const mobileClose = document.getElementById('mobileClose');
    
    if (mobileToggle) {
        mobileToggle.addEventListener('click', () => mobileMenu?.classList.add('open'));
    }
    if (mobileClose) {
        mobileClose.addEventListener('click', () => mobileMenu?.classList.remove('open'));
    }
    
    // اسکرول هدر
    const header = document.getElementById('header');
    window.addEventListener('scroll', () => {
        header?.classList.toggle('scrolled', window.scrollY > 100);
    });
    
    // فیلتر کردن دوره‌ها
    const filterTabs = document.querySelectorAll('.filter-tab');
    filterTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            filterTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const category = tab.dataset.filter;
            document.querySelectorAll('.course-card').forEach(card => {
                if (category === 'all' || card.dataset.category === category) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
    
    // انتخاب روش پرداخت
    document.querySelectorAll('.payment-method').forEach(method => {
        method.addEventListener('click', () => {
            document.querySelectorAll('.payment-method').forEach(m => m.classList.remove('active'));
            method.classList.add('active');
        });
    });
    
    // تنظیم favicon پویا
    const favicon = document.querySelector('link[rel="icon"]');
    if (favicon) {
        favicon.href = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' stop-color='%2300f2fe'/%3E%3Cstop offset='100%25' stop-color='%234facfe'/%3E%3C/linearGradient%3E%3C/defs%3E%3Ccircle cx='50' cy='50' r='46' stroke='url(%23g)' stroke-width='5' fill='none'/%3E%3Ccircle cx='50' cy='50' r='14' fill='url(%23g)'/%3E%3C/svg%3E";
    }

});

document.addEventListener("DOMContentLoaded", function () {
    const currentPath = window.location.pathname.replace(/\/+$/, "") || "/";

    document.querySelectorAll(".nav-link").forEach(link => {
        const url = new URL(link.href, window.location.origin);
        const linkPath = url.pathname.replace(/\/+$/, "") || "/";

        link.classList.remove("active");

        if (url.origin !== window.location.origin) {
            return;
        }

        // صفحه اصلی
        if (linkPath === "/") {
            if (currentPath === "/") {
                link.classList.add("active");
            }
            return;
        }

        // سایر لینک‌ها
        if (
            currentPath === linkPath ||
            currentPath.startsWith(linkPath + "/")
        ) {
            link.classList.add("active");
        }
    });
});
