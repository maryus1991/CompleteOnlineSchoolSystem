// SCROLL PROGRESS BAR
const scrollProgress = document.getElementById('scrollProgress');
window.addEventListener('scroll', () => {
    const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
    const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const progress = (scrollTop / scrollHeight) * 100;
    if (scrollProgress) scrollProgress.style.width = progress + '%';
});

// PRELOADER
const preloader = document.getElementById('preloader');
const preloaderProgress = document.querySelector('.preloader-progress');
const preloaderPercent = document.querySelector('.preloader-percent');
if (preloader) {
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress >= 100) { 
            progress = 100; 
            clearInterval(interval); 
            setTimeout(() => preloader.classList.add('hide'), 200);
        }
        if (preloaderProgress) preloaderProgress.style.width = progress + '%';
        if (preloaderPercent) preloaderPercent.textContent = toPersianNum(Math.round(progress)) + '%';
    }, 75);
}

// CUSTOM CURSOR
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
    document.querySelectorAll('a, button, .btn, .mentor-card, .course-card, .testimonial-card, .portfolio-card, .blog-card, .event-card').forEach(el => {
        el.addEventListener('mouseenter', () => { 
            cursor.style.transform = 'scale(1.5)'; 
            follower.style.transform = 'scale(1.5)'; 
        });
        el.addEventListener('mouseleave', () => { 
            cursor.style.transform = 'scale(1)'; 
            follower.style.transform = 'scale(1)'; 
        });
    });
}

// BACK TO TOP
const backToTop = document.getElementById('backToTop');
window.addEventListener('scroll', () => { 
    backToTop.classList.toggle('show', window.scrollY > 500); 
});
backToTop?.addEventListener('click', () => { 
    window.scrollTo({ top: 0, behavior: 'smooth' }); 
});

// SETTINGS PANEL
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

// تابع تبدیل اعداد انگلیسی به فارسی
function toPersianNum(num) {
    const persianDigits = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
    return num.toString().replace(/\d/g, digit => persianDigits[digit]);
}

// COUNTER ANIMATION
const countElements = document.querySelectorAll('.counter');
const countObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const el = entry.target;
            const target = parseInt(el.dataset.target);
            let count = 0;
            const duration = 2000;
            const step = target / (duration / 16);
            
            const updateCount = () => {
                count += step;
                if (count < target) { 
                    el.textContent = toPersianNum(Math.round(count)); 
                    requestAnimationFrame(updateCount); 
                } else { 
                    el.textContent = toPersianNum(target); 
                }
            };
            
            requestAnimationFrame(updateCount);
            countObserver.unobserve(el);
        }
    });
}, { threshold: 0.5 });
countElements.forEach(el => countObserver.observe(el));

// PORTFOLIO FILTER
const filterBtns = document.querySelectorAll('.filter-btn');
const portfolioCards = document.querySelectorAll('.portfolio-card');
filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const filter = btn.dataset.filter;
        portfolioCards.forEach(card => {
            if (filter === 'all' || card.dataset.category === filter) {
                card.style.display = 'block';
                setTimeout(() => { 
                    card.style.opacity = '1'; 
                    card.style.transform = 'scale(1)'; 
                }, 10);
            } else {
                card.style.opacity = '0';
                card.style.transform = 'scale(0.8)';
                setTimeout(() => { 
                    card.style.display = 'none'; 
                }, 300);
            }
        });
    });
});

// FAQ ACCORDION
document.querySelectorAll('.faq-question').forEach(button => {
    button.addEventListener('click', () => { 
        button.parentElement.classList.toggle('active'); 
    });
});

// FORM SUBMIT
document.getElementById('contactForm')?.addEventListener('submit', function(e) {
    e.preventDefault();
    const lang = localStorage.getItem('lang') || 'fa';
    alert(lang === 'fa' ? '🚀 پیام شما با موفقیت ارسال شد! به زودی با شما تماس می‌گیریم.' : '🚀 Your message has been sent! We will contact you soon.');
    this.reset();
});

// PARALLAX
window.addEventListener('mousemove', (e) => {
    const moveX = (e.clientX - window.innerWidth / 2) * 0.01;
    const moveY = (e.clientY - window.innerHeight / 2) * 0.01;
    document.querySelectorAll('.hero-glow').forEach(glow => { 
        glow.style.transform = `translate(${moveX}px, ${moveY}px)`; 
    });
});