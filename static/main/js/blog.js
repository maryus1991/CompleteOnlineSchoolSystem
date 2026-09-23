// ===== بلاگ پست داینامیک و تعاملات =====

document.addEventListener('DOMContentLoaded', function() {
    
    // 1. اسکرول پروگرس بار (مثل سایت اصلی)
    const scrollProgress = document.getElementById('scrollProgress');
    if (scrollProgress) {
        window.addEventListener('scroll', () => {
            const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
            const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const progress = (scrollTop / scrollHeight) * 100;
            scrollProgress.style.width = progress + '%';
        });
    }

    // 2. Preloader زیبا
    const preloader = document.getElementById('preloader');
    const preloaderProgress = document.querySelector('.preloader-progress');
    const preloaderPercent = document.querySelector('.preloader-percent');
    if (preloader) {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 12;
            if (progress >= 100) { 
                progress = 100; 
                clearInterval(interval); 
                setTimeout(() => preloader.classList.add('hide'), 350); 
            }
            if (preloaderProgress) preloaderProgress.style.width = progress + '%';
            if (preloaderPercent) preloaderPercent.textContent = Math.round(progress) + '%';
        }, 90);
    }

    // 3. Custom Cursor (هماهنگ با اتمسفر سایت)
    const cursor = document.querySelector('.cursor');
    const follower = document.querySelector('.cursor-follower');
    if (cursor && follower) {
        document.addEventListener('mousemove', (e) => {
            cursor.style.left = e.clientX + 'px';
            cursor.style.top = e.clientY + 'px';
            setTimeout(() => { 
                follower.style.left = e.clientX + 'px'; 
                follower.style.top = e.clientY + 'px'; 
            }, 80);
        });
        const hoverElements = document.querySelectorAll('a, button, .btn, .post-tags a, .sidebar-widget, .skills-list li');
        hoverElements.forEach(el => {
            el.addEventListener('mouseenter', () => { 
                cursor.style.transform = 'scale(1.6)'; 
                follower.style.transform = 'scale(1.4)'; 
            });
            el.addEventListener('mouseleave', () => { 
                cursor.style.transform = 'scale(1)'; 
                follower.style.transform = 'scale(1)'; 
            });
        });
    }

    // 4. Back to top
    const backToTop = document.getElementById('backToTop');
    window.addEventListener('scroll', () => { 
        if (backToTop) backToTop.classList.toggle('show', window.scrollY > 500); 
    });
    backToTop?.addEventListener('click', () => { 
        window.scrollTo({ top: 0, behavior: 'smooth' }); 
    });

    // 5. افکت Fade-in هنگام اسکرول (AOS-like دستی)
    const fadeElements = document.querySelectorAll('[data-aos]');
    const fadeObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                fadeObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    fadeElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.7s ease, transform 0.7s ease';
        fadeObserver.observe(el);
    });

    // 6. سایدبار خبرنامه (فقط alert برای نمایش)
    const newsletterForm = document.getElementById('sidebarNewsletter');
    newsletterForm?.addEventListener('submit', function(e) {
        e.preventDefault();
        const email = this.querySelector('input').value;
        if (email) {
            alert('✅ با تشکر! ایمیل شما با موفقیت در خبرنامه پولاریس ثبت شد.');
            this.reset();
        } else {
            alert('لطفاً ایمیل خود را وارد کنید.');
        }
    });

    // 7. تنظیمات تم و زبان (تکمیل‌کننده theme-switcher موجود)
    // اگر توی فایل theme-switcher نبود، اینجا یک fallback ساده میذاریم
    if (typeof setTheme === 'undefined') {
        // fallback ساده برای تغییر تم در این صفحه
        const themeBtns = document.querySelectorAll('.theme-btn');
        const setThemeFallback = (theme) => {
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
            themeBtns.forEach(btn => btn.classList.toggle('active', btn.dataset.theme === theme));
        };
        themeBtns.forEach(btn => {
            btn.addEventListener('click', () => setThemeFallback(btn.dataset.theme));
        });
        const savedTheme = localStorage.getItem('theme') || 'dark';
        setThemeFallback(savedTheme);
    }

    // 8. موبایل منو (دسترسی کامل)
    const mobileToggle = document.getElementById('mobileToggle');
    const mobileMenu = document.getElementById('mobileMenu');
    const mobileClose = document.getElementById('mobileClose');
    mobileToggle?.addEventListener('click', () => mobileMenu.classList.add('open'));
    mobileClose?.addEventListener('click', () => mobileMenu.classList.remove('open'));
    document.querySelectorAll('.mobile-nav a').forEach(link => {
        link.addEventListener('click', () => mobileMenu.classList.remove('open'));
    });

    // 9. تنظیم پنل (Settings) - مشابه سایت اصلی
    const settingsPanel = document.getElementById('settingsPanel');
    const settingsToggle = document.getElementById('settingsToggle');
    settingsToggle?.addEventListener('click', (e) => { 
        e.stopPropagation(); 
        settingsPanel.classList.toggle('open'); 
    });
    document.addEventListener('click', (e) => { 
        if (settingsPanel && settingsToggle && !settingsPanel.contains(e.target) && !settingsToggle.contains(e.target)) { 
            settingsPanel.classList.remove('open'); 
        } 
    });

    // 10. ریست دکمه (اختیاری ولی خفن)
    const resetBtn = document.querySelector('.reset-settings');
    resetBtn?.addEventListener('click', () => {
        localStorage.clear();
        document.documentElement.setAttribute('data-theme', 'dark');
        document.documentElement.setAttribute('dir', 'rtl');
        document.documentElement.setAttribute('lang', 'fa');
        window.location.reload();
    });

    console.log('✨ بلاگ پست پولاریس با تمام قوا آماده است!');
});