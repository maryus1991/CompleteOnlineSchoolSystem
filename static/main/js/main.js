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

    // فعال‌سازی لینک منوی صفحه جاری
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