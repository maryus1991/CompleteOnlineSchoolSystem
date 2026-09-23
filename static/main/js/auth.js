// ============================================
// AUTH.JS - اسکریپت صفحه ورود و ثبت‌نام با ترجمه کامل
// ============================================

// ========== ترجمه‌ها ==========
const translationsData = {
    fa: {
        // هدر
        "nav.home": "خانه",
        "nav.roadmap": "مسیر یادگیری",
        "nav.courses": "دوره‌ها",
        "nav.portfolio": "نمونه‌کارها",
        "nav.stats": "دستاوردها",
        "nav.mentors": "منتورها",
        "nav.blog": "وبلاگ",
        "nav.events": "رویدادها",
        "nav.testimonials": "نظرات",
        "nav.faq": "سوالات",
        "nav.contact": "تماس",
        "nav.account": "حساب",
        "nav.cart": "سبد خرید",
        "nav.dashboard": "پیشخوان",
        
        // فوتر
        "footer.desc": "فرماندهی نسل بعدی برنامه‌نویسان.",
        "footer.quick": "دسترسی سریع",
        "footer.links": "لینک‌های مهم",
        "footer.social": "همراه ما باشید",
        "footer.about": "درباره ما",
        "footer.careers": "فرصت‌های شغلی",
        "footer.faq": "سوالات متداول",
        "footer.privacy": "قوانین",
        "footer.terms": "حریم خصوصی",
        "footer.copyright": "© ۲۰۲۶ آکادمی پولاریس. با ❤️ برای نسل بعدی برنامه‌نویسان ایران.",
        
        // صفحات احراز هویت
        "auth.welcomeTitle": "خوش آمدید",
        "auth.login": "ورود",
        "auth.register": "ثبت‌نام",
        "auth.email": "آدرس ایمیل",
        "auth.password": "رمز عبور",
        "auth.fullname": "نام و نام خانوادگی",
        "auth.phone": "شماره تماس (اختیاری)",
        "auth.confirmPassword": "تکرار رمز عبور",
        "auth.remember": "مرا به خاطر بسپار",
        "auth.forgot": "فراموشی رمز عبور؟",
        "auth.loginBtn": "ورود به حساب کاربری",
        "auth.registerBtn": "ساخت حساب کاربری",
        "auth.terms": "قوانین و مقررات را می‌پذیرم",
        "auth.or": "یا ادامه با",
        "auth.google": "گوگل",
        "auth.github": "گیت‌هاب",
        
        // باکس ادمین
        "auth.adminTitle": "دسترسی سریع ادمین",
        "auth.adminHint": "برای ورود سریع کلیک کنید",
        
        // متن سمت چپ
        "auth.leftText": "به خانواده بزرگ پولاریس بپیوندید و آینده شغلی خود را بسازید.",
        "auth.statUsers": "کاربر فعال",
        
        // پیام‌ها
        "msg.fillAll": "لطفاً ایمیل و رمز عبور را وارد کنید",
        "msg.fillAllRegister": "لطفاً تمام فیلدهای ضروری را پر کنید",
        "msg.acceptTerms": "لطفاً قوانین و مقررات را بپذیرید",
        "msg.passwordMismatch": "رمز عبور و تکرار آن مطابقت ندارند",
        "msg.passwordLength": "رمز عبور باید حداقل ۶ کاراکتر باشد",
        "msg.emailExists": "این ایمیل قبلاً ثبت نام کرده است",
        "msg.loginSuccess": "ورود موفق! در حال انتقال...",
        "msg.registerSuccess": "ثبت نام موفق! در حال انتقال...",
        "msg.loginError": "ایمیل یا رمز عبور اشتباه است",
        "msg.adminFilled": "اطلاعات ادمین وارد شد! حالا روی دکمه ورود کلیک کنید."
    },
    en: {
        // Header
        "nav.home": "Home",
        "nav.roadmap": "Roadmap",
        "nav.courses": "Courses",
        "nav.portfolio": "Portfolio",
        "nav.stats": "Stats",
        "nav.mentors": "Mentors",
        "nav.blog": "Blog",
        "nav.events": "Events",
        "nav.testimonials": "Reviews",
        "nav.faq": "FAQ",
        "nav.contact": "Contact",
        "nav.account": "Account",
        "nav.cart": "Cart",
        "nav.dashboard": "Dashboard",
        
        // Footer
        "footer.desc": "Commanding next-gen programmers.",
        "footer.quick": "Quick Access",
        "footer.links": "Important Links",
        "footer.social": "Follow Us",
        "footer.about": "About Us",
        "footer.careers": "Careers",
        "footer.faq": "FAQ",
        "footer.privacy": "Terms",
        "footer.terms": "Privacy",
        "footer.copyright": "© 2026 Polaris Academy. With ❤️ for Iran's next-gen programmers.",
        
        // Auth pages
        "auth.welcomeTitle": "Welcome Back",
        "auth.login": "Login",
        "auth.register": "Register",
        "auth.email": "Email Address",
        "auth.password": "Password",
        "auth.fullname": "Full Name",
        "auth.phone": "Phone Number (Optional)",
        "auth.confirmPassword": "Confirm Password",
        "auth.remember": "Remember Me",
        "auth.forgot": "Forgot Password?",
        "auth.loginBtn": "Login to Account",
        "auth.registerBtn": "Create Account",
        "auth.terms": "I accept Terms & Conditions",
        "auth.or": "Or continue with",
        "auth.google": "Google",
        "auth.github": "GitHub",
        
        // Admin box
        "auth.adminTitle": "Quick Admin Access",
        "auth.adminHint": "Click to login quickly",
        
        // Left side text
        "auth.leftText": "Join the Polaris family and build your future career.",
        "auth.statUsers": "Active Users",
        
        // Messages
        "msg.fillAll": "Please enter email and password",
        "msg.fillAllRegister": "Please fill all required fields",
        "msg.acceptTerms": "Please accept the terms and conditions",
        "msg.passwordMismatch": "Passwords do not match",
        "msg.passwordLength": "Password must be at least 6 characters",
        "msg.emailExists": "This email is already registered",
        "msg.loginSuccess": "Login successful! Redirecting...",
        "msg.registerSuccess": "Registration successful! Redirecting...",
        "msg.loginError": "Invalid email or password",
        "msg.adminFilled": "Admin credentials filled! Click the login button."
    }
};

let currentLanguage = 'fa';

// ========== تابع اعمال ترجمه ==========
function applyTranslations() {
    const t = translationsData[currentLanguage];
    if (!t) return;
    
    // تمام المان‌های دارای data-i18n
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (t[key]) {
            if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                if (el.hasAttribute('placeholder')) {
                    el.placeholder = t[key];
                }
            } else if (el.tagName === 'BUTTON' && el.classList.contains('lang-btn')) {
                // دکمه‌های زبان را تغییر نده
                return;
            } else {
                el.innerHTML = t[key];
            }
        }
    });
    
    document.documentElement.setAttribute('lang', currentLanguage);
    document.documentElement.setAttribute('dir', currentLanguage === 'fa' ? 'rtl' : 'ltr');
    localStorage.setItem('polaris_lang', currentLanguage);
}

// ========== تابع تغییر زبان ==========
function setLanguage(lang) {
    if (lang !== 'fa' && lang !== 'en') return;
    currentLanguage = lang;
    applyTranslations();
    
    // آپدیت کلاس active دکمه‌های زبان
    document.querySelectorAll('.lang-btn').forEach(btn => {
        const btnLang = btn.getAttribute('data-lang');
        if (btnLang === lang) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

// ========== اکانت ادمین پیش‌فرض ==========
const ADMIN_ACCOUNT = {
    id: 1,
    name: "مدیر سیستم",
    email: "admin@polaris.com",
    password: "admin123",
    phone: "02100000000",
    avatar: "assets/image/default-avatar.jpg",
    role: "admin",
    registeredAt: new Date().toISOString(),
    enrolledCourses: []
};

function initAdminAccount() {
    const users = JSON.parse(localStorage.getItem('polaris_users') || '[]');
    const adminExists = users.find(u => u.email === ADMIN_ACCOUNT.email);
    
    if (!adminExists) {
        users.unshift(ADMIN_ACCOUNT);
        localStorage.setItem('polaris_users', JSON.stringify(users));
        console.log('✅ اکانت ادمین ایجاد شد: admin@polaris.com / admin123');
    }
}

// ========== توابع تب‌ها ==========
function initAuthTabs() {
    const tabs = document.querySelectorAll('.auth-tab');
    const forms = document.querySelectorAll('.auth-form');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.getAttribute('data-tab');
            
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            forms.forEach(form => {
                form.classList.remove('active');
                if (form.id === `${target}Form`) {
                    form.classList.add('active');
                }
            });
        });
    });
}

// ========== فرم ورود ==========
function initLoginForm() {
    const form = document.getElementById('loginFormElement');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const email = document.getElementById('loginEmail').value.trim();
        const password = document.getElementById('loginPassword').value;
        const rememberMe = document.getElementById('rememberMe')?.checked || false;
        const messageDiv = document.getElementById('loginMessage');
        const t = translationsData[currentLanguage];
        
        if (!email || !password) {
            showMessage(messageDiv, '❌ ' + t['msg.fillAll'], 'error');
            return;
        }
        
        const users = JSON.parse(localStorage.getItem('polaris_users') || '[]');
        const user = users.find(u => u.email === email && u.password === password);
        
        if (user) {
            const currentUser = {
                id: user.id,
                name: user.name,
                email: user.email,
                avatar: user.avatar || 'assets/image/default-avatar.jpg',
                role: user.role || 'user',
                registeredAt: user.registeredAt
            };
            localStorage.setItem('polaris_current_user', JSON.stringify(currentUser));
            
            if (rememberMe) {
                localStorage.setItem('polaris_remember', 'true');
            }
            
            showMessage(messageDiv, '✅ ' + t['msg.loginSuccess'], 'success');
            
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1000);
        } else {
            showMessage(messageDiv, '❌ ' + t['msg.loginError'], 'error');
        }
    });
}

// ========== فرم ثبت‌نام ==========
function initRegisterForm() {
    const form = document.getElementById('registerFormElement');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const name = document.getElementById('regName').value.trim();
        const email = document.getElementById('regEmail').value.trim();
        const phone = document.getElementById('regPhone').value.trim();
        const password = document.getElementById('regPassword').value;
        const confirmPassword = document.getElementById('regConfirmPassword').value;
        const acceptTerms = document.getElementById('acceptTerms')?.checked || false;
        const messageDiv = document.getElementById('registerMessage');
        const t = translationsData[currentLanguage];
        
        if (!name || !email || !password) {
            showMessage(messageDiv, '❌ ' + t['msg.fillAllRegister'], 'error');
            return;
        }
        
        if (!acceptTerms) {
            showMessage(messageDiv, '❌ ' + t['msg.acceptTerms'], 'error');
            return;
        }
        
        if (password !== confirmPassword) {
            showMessage(messageDiv, '❌ ' + t['msg.passwordMismatch'], 'error');
            return;
        }
        
        if (password.length < 6) {
            showMessage(messageDiv, '❌ ' + t['msg.passwordLength'], 'error');
            return;
        }
        
        const users = JSON.parse(localStorage.getItem('polaris_users') || '[]');
        if (users.find(u => u.email === email)) {
            showMessage(messageDiv, '❌ ' + t['msg.emailExists'], 'error');
            return;
        }
        
        const newUser = {
            id: Date.now(),
            name: name,
            email: email,
            phone: phone,
            password: password,
            avatar: 'assets/image/default-avatar.jpg',
            role: 'user',
            registeredAt: new Date().toISOString(),
            enrolledCourses: []
        };
        
        users.push(newUser);
        localStorage.setItem('polaris_users', JSON.stringify(users));
        
        const currentUser = {
            id: newUser.id,
            name: newUser.name,
            email: newUser.email,
            avatar: newUser.avatar,
            role: newUser.role,
            registeredAt: newUser.registeredAt
        };
        localStorage.setItem('polaris_current_user', JSON.stringify(currentUser));
        
        showMessage(messageDiv, '✅ ' + t['msg.registerSuccess'], 'success');
        
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1000);
    });
}

// ========== نمایش پیام ==========
function showMessage(element, message, type) {
    if (!element) return;
    element.textContent = message;
    element.className = `auth-message ${type}`;
    element.style.display = 'block';
    
    setTimeout(() => {
        element.style.opacity = '0';
        setTimeout(() => {
            element.style.display = 'none';
            element.style.opacity = '1';
            element.className = 'auth-message';
        }, 300);
    }, 4000);
}

// ========== بررسی ورود قبلی ==========
function checkAndRedirectIfLoggedIn() {
    const currentUser = JSON.parse(localStorage.getItem('polaris_current_user'));
    if (currentUser) {
        window.location.href = 'dashboard.html';
    }
}

// ========== خروج از حساب ==========
window.logoutUser = function() {
    localStorage.removeItem('polaris_current_user');
    localStorage.removeItem('polaris_remember');
    window.location.href = 'auth.html';
};

// ========== ورود سریع ادمین ==========
window.fillAdminCredentials = function() {
    const emailInput = document.getElementById('loginEmail');
    const passwordInput = document.getElementById('loginPassword');
    const t = translationsData[currentLanguage];
    
    if (emailInput && passwordInput) {
        emailInput.value = 'admin@polaris.com';
        passwordInput.value = 'admin123';
        
        // اعمال event برای فعال شدن افکت لیبل
        emailInput.dispatchEvent(new Event('input'));
        passwordInput.dispatchEvent(new Event('input'));
        
        // انیمیشن باکس
        const adminBox = document.querySelector('.admin-info-box');
        if (adminBox) {
            adminBox.style.transform = 'scale(1.02)';
            adminBox.style.borderColor = '#00f2fe';
            setTimeout(() => {
                adminBox.style.transform = 'scale(1)';
            }, 300);
        }
        
        showToastMessage('✅ ' + t['msg.adminFilled']);
    }
};

// ========== پیام toast ==========
function showToastMessage(msg) {
    const toast = document.createElement('div');
    toast.innerHTML = msg;
    toast.style.cssText = `
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        background: var(--accent-gradient);
        color: white;
        padding: 12px 24px;
        border-radius: 50px;
        z-index: 10000;
        font-weight: 600;
        font-family: 'Peyda', sans-serif;
        animation: fadeInUp 0.3s ease;
        box-shadow: 0 5px 20px rgba(0,0,0,0.3);
    `;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// ========== ورود با شبکه‌های اجتماعی ==========
window.handleSocialLogin = function(provider) {
    const providerName = provider === 'google' ? (currentLanguage === 'fa' ? 'گوگل' : 'Google') : (currentLanguage === 'fa' ? 'گیت‌هاب' : 'GitHub');
    showToastMessage(`🚀 در حال اتصال به ${providerName}... این قابلیت به زودی فعال می‌شود.`);
};

// ========== آپدیت شمارنده سبد خرید ==========
function updateCartBadge() {
    const cartItems = JSON.parse(localStorage.getItem('polaris_cart') || '[]');
    const badge = document.getElementById('cartCountBadge');
    if (badge) {
        const count = cartItems.length;
        badge.textContent = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
    }
}

// ========== آپدیت آمار کاربران ==========
function updateUserStats() {
    const users = JSON.parse(localStorage.getItem('polaris_users') || '[]');
    const userCount = users.length;
    const statElement = document.getElementById('statUsers');
    if (statElement) {
        statElement.textContent = userCount.toLocaleString() + '+';
    }
}

// ========== مقداردهی اولیه دکمه‌های زبان ==========
function initLanguageButtons() {
    const langButtons = document.querySelectorAll('.lang-btn');
    langButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const lang = btn.getAttribute('data-lang');
            setLanguage(lang);
        });
    });
}

// ========== رویداد اصلی ==========
document.addEventListener('DOMContentLoaded', function() {
    // بازیابی زبان ذخیره شده
    const savedLang = localStorage.getItem('polaris_lang') || 'fa';
    currentLanguage = savedLang;
    
    // اعمال ترجمه اولیه
    applyTranslations();
    
    // مقداردهی اولیه
    initAdminAccount();
    initAuthTabs();
    initLoginForm();
    initRegisterForm();
    initLanguageButtons();
    checkAndRedirectIfLoggedIn();
    
    // آپدیت آمار
    updateUserStats();
    updateCartBadge();
    
    // اتصال رویداد باکس ادمین
    const adminBox = document.getElementById('adminQuickLogin');
    if (adminBox) {
        adminBox.addEventListener('click', fillAdminCredentials);
    }
    
    console.log('✅ Auth.js loaded successfully | Language:', currentLanguage);
});