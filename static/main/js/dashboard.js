// ============================================
// DASHBOARD.JS - داشبورد حرفه‌ای
// ============================================

// تبدیل عدد به فارسی
function toPersianNumber(num) {
    if (num === undefined || num === null) return '۰';
    const persianDigits = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
    return num.toString().replace(/\d/g, d => persianDigits[d]);
}

// مقداردهی اولیه داده‌ها در localStorage با ۴ دوره کامل
function initData() {
    const courses = [
        { id: 1, title: 'بوت‌کمپ جامع فرانت‌اند', price: 8500000, image: 'assets/image/front.jpg', progress: 45 },
        { id: 2, title: 'مهندسی بک‌اند با Node.js', price: 9200000, image: 'assets/image/node.webp', progress: 20 },
        { id: 3, title: 'پکیج کامل فول‌استک', price: 15000000, image: 'assets/image/full.jpg', progress: 80 },
        { id: 4, title: 'هوش مصنوعی با Python', price: 11000000, image: 'assets/image/python.webp', progress: 100, completedDate: '2026-05-01' }
    ];
    
    if (!localStorage.getItem('polaris_enrolled')) {
        localStorage.setItem('polaris_enrolled', JSON.stringify(courses));
    }
    
    if (!localStorage.getItem('polaris_cart')) {
        localStorage.setItem('polaris_cart', JSON.stringify([
            { id: 2, title: 'مهندسی بک‌اند با Node.js', price: 9200000, image: 'assets/image/node.webp' }
        ]));
    }
    
    if (!localStorage.getItem('polaris_current_user')) {
        localStorage.setItem('polaris_current_user', JSON.stringify({
            id: 1, name: 'کاربر مهمان', email: 'guest@polaris.com', phone: '09123456789', avatar: 'assets/image/user5.jpg'
        }));
    }
    
    if (!localStorage.getItem('polaris_users')) {
        localStorage.setItem('polaris_users', JSON.stringify([
            { id: 1, name: 'کاربر مهمان', email: 'guest@polaris.com', phone: '09123456789', password: '123456', avatar: 'assets/image/user5.jpg' }
        ]));
    }
}

// بارگذاری پروفایل کاربر
function loadUserProfile() {
    const user = JSON.parse(localStorage.getItem('polaris_current_user') || '{}');
    const defaultUser = { name: 'کاربر مهمان', email: 'guest@polaris.com', avatar: 'assets/image/user5.jpg' };
    const currentUser = user.id ? user : defaultUser;
    
    const welcomeName = document.getElementById('welcomeUserName');
    const sidebarName = document.getElementById('sidebarUserName');
    const sidebarEmail = document.getElementById('sidebarUserEmail');
    const sidebarAvatar = document.getElementById('sidebarAvatar');
    
    if (welcomeName) welcomeName.textContent = currentUser.name;
    if (sidebarName) sidebarName.textContent = currentUser.name;
    if (sidebarEmail) sidebarEmail.textContent = currentUser.email;
    
    if (sidebarAvatar) {
        if (currentUser.avatar && currentUser.avatar.startsWith('data:image')) {
            sidebarAvatar.src = currentUser.avatar;
        } else {
            sidebarAvatar.src = currentUser.avatar || 'assets/image/user5.jpg';
        }
    }
    
    if (!user.id) {
        localStorage.setItem('polaris_current_user', JSON.stringify(defaultUser));
    }
}

// بارگذاری آمار
function loadStats() {
    const enrolled = JSON.parse(localStorage.getItem('polaris_enrolled') || '[]');
    const completed = enrolled.filter(c => c.progress === 100);
    const inProgress = enrolled.filter(c => c.progress > 0 && c.progress < 100);
    let totalProgress = enrolled.reduce((s, c) => s + (c.progress || 0), 0);
    const avgProgress = enrolled.length ? Math.floor(totalProgress / enrolled.length) : 0;
    const totalHours = Math.floor(enrolled.reduce((s, c) => s + ((c.progress || 0) / 100) * 40, 0));
    const points = completed.length * 100 + inProgress.length * 30;
    const streak = localStorage.getItem('polaris_streak') || '۱';
    const rank = points > 500 ? '#۱' : points > 200 ? '#۲' : '#۳';
    
    const setText = (id, val) => { const el = document.getElementById(id); if (el) el.innerHTML = val; };
    setText('totalCourses', toPersianNumber(enrolled.length));
    setText('completedCourses', toPersianNumber(completed.length));
    setText('certificatesCount', toPersianNumber(completed.length));
    setText('hoursSpent', toPersianNumber(totalHours));
    setText('streakDays', streak);
    setText('totalPoints', toPersianNumber(points));
    setText('userRank', rank);
    setText('sidebarCourses', toPersianNumber(enrolled.length));
    setText('sidebarCompleted', toPersianNumber(completed.length));
    setText('sidebarPoints', toPersianNumber(points));
    setText('coursesTrend', enrolled.length > 0 ? '+۱۲%' : '۰%');
    setText('completedTrend', completed.length > 0 ? '+۸%' : '۰%');
    setText('certificatesTrend', completed.length > 0 ? '+۵%' : '۰%');
    setText('hoursTrend', totalHours > 0 ? '+۲۳%' : '۰%');
}

function loadRecommendedCourses() {
    const container = document.getElementById('recommendedCourses');
    if (!container) return;
    
    container.innerHTML = [
        { id: 5, title: 'TypeScript پیشرفته', level: 'پیشرفته', image: 'assets/image/js.webp' },
        { id: 6, title: 'Docker و Kubernetes', level: 'متوسط', image: 'assets/image/docker.webp' },
        { id: 7, title: 'GitHub Copilot', level: 'مبتدی تا پیشرفته', image: 'assets/image/github.webp' }
    ].map(c => `<a href="course-single.html?id=${c.id}" class="recommended-card"><img src="${c.image}" class="recommended-img" onerror="this.src='assets/image/front.jpg'"><div class="recommended-info"><h4>${c.title}</h4><p>${c.level}</p></div></a>`).join('');
}

function updateCartBadge() {
    const cart = JSON.parse(localStorage.getItem('polaris_cart') || '[]');
    const badge = document.getElementById('cartCountBadge');
    if (badge) { badge.textContent = cart.length; badge.style.display = cart.length > 0 ? 'flex' : 'none'; }
}

function showToast(msg) {
    const toast = document.createElement('div');
    toast.innerHTML = msg;
    toast.style.cssText = 'position:fixed; bottom:30px; left:50%; transform:translateX(-50%); background:linear-gradient(135deg, #00f2fe, #4facfe); color:white; padding:12px 24px; border-radius:50px; z-index:10000; font-weight:600; animation:fadeInUp 0.3s ease;';
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// ========== بخش‌های محتوایی ==========

window.showEditAccount = function() {
    const user = JSON.parse(localStorage.getItem('polaris_current_user') || '{}');
    
    document.getElementById('dynamicContent').innerHTML = `
        <div class="welcome-premium"><div class="welcome-content"><div class="welcome-badge"><span class="badge-dot"></span><span>ویرایش حساب</span></div><h1 class="welcome-title">ویرایش <span class="gradient-text">پروفایل</span></h1><p class="welcome-desc">اطلاعات شخصی خود را به‌روزرسانی کنید</p></div></div>
        <div style="padding:25px"><form id="editProfileForm" class="edit-profile-form"><div class="form-group-glass"><input type="text" id="editName" value="${user.name || ''}" placeholder=" "><label>نام و نام خانوادگی</label></div><div class="form-group-glass"><input type="email" id="editEmail" value="${user.email || ''}" placeholder=" "><label>آدرس ایمیل</label></div><div class="form-group-glass"><input type="tel" id="editPhone" value="${user.phone || ''}" placeholder=" "><label>شماره تماس</label></div><div class="form-group-glass"><input type="password" id="editPassword" placeholder=" "><label>رمز عبور جدید (اختیاری)</label></div><div class="form-buttons"><button type="submit" class="btn-save">ذخیره تغییرات</button><button type="button" class="btn-cancel" onclick="location.reload()">انصراف</button></div></form></div>
        <div class="section-footer"><a href="#" class="view-all-link" onclick="showEditAccount(); return false;">→ صفحه تنظیمات پیشرفته</a></div>
    `;
    const form = document.getElementById('editProfileForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const newName = document.getElementById('editName').value.trim();
            const newEmail = document.getElementById('editEmail').value.trim();
            const newPhone = document.getElementById('editPhone').value.trim();
            if (!newName || !newEmail) { showToast('❌ نام و ایمیل الزامی است'); return; }
            const user = JSON.parse(localStorage.getItem('polaris_current_user') || '{}');
            user.name = newName; user.email = newEmail; user.phone = newPhone;
            localStorage.setItem('polaris_current_user', JSON.stringify(user));
            const users = JSON.parse(localStorage.getItem('polaris_users') || '[]');
            const idx = users.findIndex(u => u.id === user.id);
            if (idx !== -1) { users[idx].name = newName; users[idx].email = newEmail; users[idx].phone = newPhone; localStorage.setItem('polaris_users', JSON.stringify(users)); }
            showToast('✅ اطلاعات با موفقیت به‌روزرسانی شد');
            location.reload();
        });
    }
};

window.showMyProducts = function() {
    const enrolled = JSON.parse(localStorage.getItem('polaris_enrolled') || '[]');
    
    document.getElementById('dynamicContent').innerHTML = `
        <div class="welcome-premium"><div class="welcome-content"><div class="welcome-badge"><span class="badge-dot"></span><span>محصولات من</span></div><h1 class="welcome-title">دوره‌های <span class="gradient-text">خریداری شده</span></h1><p class="welcome-desc">دوره‌هایی که ثبت‌نام کرده‌اید</p></div></div>
        <div style="padding:25px"><div class="courses-grid-small" id="productsList"></div></div>
        <div class="section-footer"><a href="courses.html" class="view-all-link">→ مشاهده همه دوره‌ها</a></div>
    `;
    const container = document.getElementById('productsList');
    if (!container) return;
    if (enrolled.length === 0) { 
        container.innerHTML = `<div class="empty-state-glass"><div class="empty-icon">🛒</div><h4>هیچ محصولی خریداری نکرده‌اید</h4><a href="courses.html" class="btn btn-primary">مشاهده دوره‌ها</a></div>`; 
        return; 
    }
    container.innerHTML = enrolled.map(c => `
        <div class="course-card-small"><img src="${c.image}" class="course-img-small" onerror="this.src='assets/image/front.jpg'"><div class="course-info-small"><h4>${c.title}</h4><div class="progress-small"><div class="progress-bar-small"><div class="progress-fill-small" style="width: ${c.progress}%"></div></div><span class="progress-text-small">${toPersianNumber(c.progress)}%</span></div><div class="course-actions-small"><span class="price-small">${c.price.toLocaleString()} تومان</span><a href="course-single.html?id=${c.id}" class="btn-small">${c.progress === 100 ? 'مشاهده' : 'ادامه'}</a></div></div></div>
    `).join('');
};

window.showCertificates = function() {
    const enrolled = JSON.parse(localStorage.getItem('polaris_enrolled') || '[]');
    const completed = enrolled.filter(c => c.progress === 100);
    
    document.getElementById('dynamicContent').innerHTML = `
        <div class="welcome-premium"><div class="welcome-content"><div class="welcome-badge"><span class="badge-dot"></span><span>گواهی‌ها</span></div><h1 class="welcome-title">گواهی‌های <span class="gradient-text">دریافت شده</span></h1><p class="welcome-desc">گواهی‌های دوره‌های تکمیل شده</p></div></div>
        <div style="padding:25px"><div class="certificates-grid-small" id="certificatesList"></div></div>
        <div class="section-footer"><a href="#" class="view-all-link" onclick="showCertificates(); return false;">→ مشاهده همه گواهی‌ها</a></div>
    `;
    const container = document.getElementById('certificatesList');
    if (!container) return;
    if (completed.length === 0) { 
        container.innerHTML = `<div class="empty-state-glass"><div class="empty-icon">🎓</div><h4>گواهی دریافت نکرده‌اید</h4><p>دوره‌های خود را کامل کنید</p></div>`; 
        return; 
    }
    container.innerHTML = completed.map(c => `
        <div class="certificate-card-small"><div class="certificate-icon-small">🏅</div><div class="certificate-info-small"><h4>${c.title}</h4><p>تاریخ: ${new Date(c.completedDate || Date.now()).toLocaleDateString('fa-IR')}</p></div><button class="certificate-download-small" onclick="showToast('✅ گواهی ${c.title} دانلود شد!')">📥 دریافت</button></div>
    `).join('');
};

window.showMyCourses = function() {
    const enrolled = JSON.parse(localStorage.getItem('polaris_enrolled') || '[]');
    
    document.getElementById('dynamicContent').innerHTML = `
        <div class="welcome-premium"><div class="welcome-content"><div class="welcome-badge"><span class="badge-dot"></span><span>دوره‌های من</span></div><h1 class="welcome-title">دوره‌های <span class="gradient-text">ثبت‌نام شده</span></h1><p class="welcome-desc">همه دوره‌هایی که ثبت‌نام کرده‌اید</p></div></div>
        <div style="padding:25px"><div class="courses-grid-small" id="myCoursesList"></div></div>
        <div class="section-footer"><a href="courses.html" class="view-all-link">→ مشاهده همه دوره‌ها</a></div>
    `;
    const container = document.getElementById('myCoursesList');
    if (!container) return;
    if (enrolled.length === 0) { 
        container.innerHTML = `<div class="empty-state-glass"><div class="empty-icon">📚</div><h4>هیچ دوره‌ای ثبت‌نام نکرده‌اید</h4><a href="courses.html" class="btn btn-primary">مشاهده دوره‌ها</a></div>`; 
        return; 
    }
    container.innerHTML = enrolled.map(c => `
        <div class="course-card-small"><img src="${c.image}" class="course-img-small" onerror="this.src='assets/image/front.jpg'"><div class="course-info-small"><h4>${c.title}</h4><div class="progress-small"><div class="progress-bar-small"><div class="progress-fill-small" style="width: ${c.progress}%"></div></div><span class="progress-text-small">${toPersianNumber(c.progress)}%</span></div><div class="course-actions-small"><span class="status-badge-small ${c.progress === 100 ? 'completed' : 'progress'}">${c.progress === 100 ? 'تکمیل شده' : 'در حال یادگیری'}</span><a href="course-single.html?id=${c.id}" class="btn-small">${c.progress === 100 ? 'مشاهده' : 'ادامه'}</a></div></div></div>
    `).join('');
};

window.showCart = function() {
    const cart = JSON.parse(localStorage.getItem('polaris_cart') || '[]');
    
    document.getElementById('dynamicContent').innerHTML = `
        <div class="welcome-premium"><div class="welcome-content"><div class="welcome-badge"><span class="badge-dot"></span><span>سبد خرید</span></div><h1 class="welcome-title">سبد <span class="gradient-text">خرید</span></h1><p class="welcome-desc">دوره‌های انتخاب شده برای خرید</p></div></div>
        <div style="padding:25px"><div id="cartItemsList" class="cart-items-small"></div><div id="cartTotal" class="cart-total-small"></div><div class="cart-actions-small"><a href="checkout.html" class="btn-primary-small">پرداخت</a><a href="courses.html" class="btn-outline-small">ادامه خرید</a></div></div>
        <div class="section-footer"><a href="cart.html" class="view-all-link">→ رفتن به صفحه سبد خرید</a></div>
    `;
    const container = document.getElementById('cartItemsList');
    if (!container) return;
    if (cart.length === 0) { 
        container.innerHTML = `<div class="empty-state-glass"><div class="empty-icon">🛒</div><h4>سبد خرید شما خالی است</h4><a href="courses.html" class="btn btn-primary">مشاهده دوره‌ها</a></div>`; 
        return; 
    }
    let total = 0;
    container.innerHTML = cart.map(item => { total += item.price; return `<div class="cart-item-small"><img src="${item.image}" class="cart-img-small" onerror="this.src='assets/image/front.jpg'"><div class="cart-info-small"><h4>${item.title}</h4><span class="cart-price-small">${item.price.toLocaleString()} تومان</span></div><button onclick="removeFromCart(${item.id})" class="cart-remove-small">🗑️ حذف</button></div>`; }).join('');
    document.getElementById('cartTotal').innerHTML = `جمع کل: ${total.toLocaleString()} تومان`;
};

window.removeFromCart = function(id) {
    let cart = JSON.parse(localStorage.getItem('polaris_cart') || '[]');
    cart = cart.filter(item => item.id !== id);
    localStorage.setItem('polaris_cart', JSON.stringify(cart));
    window.showCart();
    updateCartBadge();
    showToast('🗑️ دوره از سبد خرید حذف شد');
};

window.showSupport = function() {
    document.getElementById('dynamicContent').innerHTML = `
        <div class="welcome-premium"><div class="welcome-content"><div class="welcome-badge"><span class="badge-dot"></span><span>پشتیبانی</span></div><h1 class="welcome-title">پشتیبانی <span class="gradient-text">۲۴ ساعته</span></h1><p class="welcome-desc">ما همیشه در کنار شما هستیم</p></div></div>
        <div style="padding:25px"><div class="support-grid"><div class="support-card"><div class="support-icon"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.362 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.338 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg></div><h3>تلفن پشتیبانی</h3><p>۰۲۱-۱۲۳۴۵۶۷۸</p><a href="tel:02112345678" class="support-link">تماس بگیرید</a></div><div class="support-card"><div class="support-icon"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg></div><h3>ایمیل</h3><p>support@polaris.com</p><a href="mailto:support@polaris.com" class="support-link">ارسال ایمیل</a></div><div class="support-card"><div class="support-icon"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg></div><h3>چت آنلاین</h3><p>پاسخگویی فوری</p><button onclick="showToast('💬 در حال اتصال به تیم پشتیبانی...')" class="support-chat">شروع چت</button></div></div><div class="support-info"><h4>ساعات پاسخگویی</h4><p>شنبه تا پنجشنبه: ۹ صبح تا ۸ شب</p><p>جمعه‌ها: ۱۰ صبح تا ۴ عصر</p><p>آدرس: تهران، خیابان ولیعصر، پلاک ۱۲۳</p></div></div>
    `;
};

window.logout = function() {
    localStorage.removeItem('polaris_current_user');
    window.location.href = 'index.html';
};

function initSidebarButtons() {
    document.querySelectorAll('.sidebar-menu-item').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.getAttribute('data-section');
            document.querySelectorAll('.sidebar-menu-item').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const actions = { editAccount: 'showEditAccount', myProducts: 'showMyProducts', certificates: 'showCertificates', myCourses: 'showMyCourses', cart: 'showCart', support: 'showSupport', logout: 'logout' };
            if (actions[section]) window[actions[section]]();
            else location.reload();
        });
    });
}

// مقداردهی اولیه
document.addEventListener('DOMContentLoaded', function() {
    initData();
    loadUserProfile();
    loadStats();
    loadRecommendedCourses();
    updateCartBadge();
    initSidebarButtons();
});