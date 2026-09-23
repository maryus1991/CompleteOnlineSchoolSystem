// ============================================
// COURSES.JS - صفحه لیست دوره‌ها (نسخه نهایی با دیتای کامل)
// ============================================

// تبدیل عدد به فارسی
function toPersianNumber(num) {
    if (num === undefined || num === null) return '۰';
    const persianDigits = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
    return num.toString().replace(/\d/g, d => persianDigits[d]);
}

// فرمت قیمت
function formatPrice(price) {
    return toPersianNumber(price.toLocaleString()) + ' تومان';
}

// ============================================
// دیتای کامل دوره‌ها (۶ دوره اصلی)
// ============================================
const coursesData = [
    {
        id: 1,
        title: "بوت‌کمپ جامع فرانت‌اند",
        category: "frontend",
        price: 8500000,
        image: "assets/image/front.jpg",
        duration: "۳۲ جلسه",
        level: "مبتدی تا پیشرفته",
        studentsCount: 1247,
        desc: "آموزش کامل HTML، CSS، JavaScript پیشرفته، React.js، Next.js و TypeScript. تمام پروژه‌ها واقعی و قابل ارائه در رزومه هستند.",
        features: ["پروژه محور", "گواهی معتبر", "پشتیبانی ۲۴/۷"]
    },
    {
        id: 2,
        title: "مهندسی بک‌اند با Node.js",
        category: "backend",
        price: 9200000,
        image: "assets/image/node.webp",
        duration: "۲۸ جلسه",
        level: "متوسط تا پیشرفته",
        studentsCount: 892,
        desc: "طراحی API، معماری میکروسرویس، کار با MongoDB، PostgreSQL، Docker و Redis. آماده‌سازی برای ورود به بازار کار.",
        features: ["پروژه محور", "گواهی معتبر", "پشتیبانی ۲۴/۷"]
    },
    {
        id: 3,
        title: "پکیج کامل فول‌استک",
        category: "fullstack",
        price: 15000000,
        image: "assets/image/full.jpg",
        duration: "۴۸ جلسه",
        level: "صفر تا استخدام",
        studentsCount: 2341,
        desc: "همه مهارت‌های لازم برای یک فول‌استک دولوپر حرفه‌ای: فرانت‌اند + بک‌اند + دیتابیس + DevOps.",
        features: ["پروژه محور", "گواهی معتبر", "پشتیبانی ۲۴/۷", "مصاحبه شغلی"]
    },
    {
        id: 4,
        title: "هوش مصنوعی با Python",
        category: "ai",
        price: 11000000,
        image: "assets/image/python.webp",
        duration: "۳۶ جلسه",
        level: "پیشرفته",
        studentsCount: 567,
        desc: "یادگیری ماشین، شبکه‌های عصبی، TensorFlow، Keras، پردازش تصویر و NLP. پروژه‌های واقعی هوش مصنوعی.",
        features: ["پروژه محور", "گواهی معتبر", "پشتیبانی ۲۴/۷"]
    },
    {
        id: 5,
        title: "React Native - ساخت اپ موبایل",
        category: "frontend",
        price: 7800000,
        image: "assets/image/react-native.webp",
        duration: "۲۴ جلسه",
        level: "متوسط",
        studentsCount: 745,
        desc: "ساخت اپلیکیشن‌های موبایل کراس پلتفرم با React Native، Expo، Redux و انتشار در فروشگاه‌ها.",
        features: ["پروژه محور", "گواهی معتبر", "پشتیبانی ۲۴/۷"]
    },
    {
        id: 6,
        title: "دیتاساینس و تحلیل داده",
        category: "ai",
        price: 12500000,
        image: "assets/image/data.jpg",
        duration: "۴۰ جلسه",
        level: "متوسط تا پیشرفته",
        studentsCount: 623,
        desc: "پردازش داده، مصورسازی، pandas، numpy، matplotlib، seaborn و پروژه‌های واقعی تحلیل داده.",
        features: ["پروژه محور", "گواهی معتبر", "پشتیبانی ۲۴/۷"]
    }
];

// ============================================
// مقداردهی اولیه localStorage با دوره‌های خریداری شده (برای نمایش در محصولات من)
// ============================================
function initEnrolledCourses() {
    let enrolled = localStorage.getItem('polaris_enrolled');
    
    // اگر دیتایی وجود نداشت یا خالی بود، دوره‌های پیش‌فرض رو اضافه کن
    if (!enrolled || JSON.parse(enrolled).length === 0) {
        const defaultEnrolled = [
            {
                id: 1,
                title: "بوت‌کمپ جامع فرانت‌اند",
                price: 8500000,
                image: "https://picsum.photos/id/0/400/250",
                progress: 45,
                purchaseDate: new Date().toISOString()
            },
            {
                id: 2,
                title: "مهندسی بک‌اند با Node.js",
                price: 9200000,
                image: "https://picsum.photos/id/1/400/250",
                progress: 20,
                purchaseDate: new Date().toISOString()
            },
            {
                id: 4,
                title: "هوش مصنوعی با Python",
                price: 11000000,
                image: "https://picsum.photos/id/3/400/250",
                progress: 100,
                completedDate: new Date().toISOString(),
                purchaseDate: new Date().toISOString()
            }
        ];
        localStorage.setItem('polaris_enrolled', JSON.stringify(defaultEnrolled));
        console.log('✅ دوره‌های خریداری شده پیش‌فرض به localStorage اضافه شدند');
        enrolled = defaultEnrolled;
    }
    
    return JSON.parse(localStorage.getItem('polaris_enrolled') || '[]');
}

// متغیرهای وضعیت
let currentFilter = "all";
let currentSearch = "";

// نمایش پیام موقت
function showToast(message, isError = false) {
    const oldToast = document.querySelector('.custom-toast');
    if (oldToast) oldToast.remove();
    
    const toast = document.createElement('div');
    toast.className = 'custom-toast';
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        background: ${isError ? '#ff4444' : 'linear-gradient(135deg, #00f2fe, #4facfe)'};
        color: white;
        padding: 14px 28px;
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

// اضافه کردن به سبد خرید
function addToCart(id, title, price, image) {
    let cartItems = JSON.parse(localStorage.getItem("polaris_cart") || "[]");
    
    if (!cartItems.find(item => item.id === id)) {
        cartItems.push({ id, title, price, image });
        localStorage.setItem("polaris_cart", JSON.stringify(cartItems));
        showToast('✅ دوره به سبد خرید اضافه شد');
        updateCartCount();
        return true;
    } else {
        showToast('ℹ️ این دوره قبلاً در سبد خرید است', true);
        return false;
    }
}

// خرید سریع (اضافه به سبد خرید و رفتن به تسویه)
function buyNow(id, title, price, image) {
    addToCart(id, title, price, image);
    setTimeout(() => {
        window.location.href = 'checkout.html';
    }, 500);
}

// مشاهده جزئیات دوره
function viewCourse(courseId) {
    window.location.href = `course-single.html?id=${courseId}`;
}

// آپدیت تعداد سبد خرید
function updateCartCount() {
    const cartItems = JSON.parse(localStorage.getItem("polaris_cart") || "[]");
    const badge = document.getElementById('cartCountBadge');
    if (badge) {
        badge.textContent = cartItems.length;
        badge.style.display = cartItems.length > 0 ? 'inline-flex' : 'none';
    }
}

// بررسی اینکه کاربر قبلاً یک دوره رو خریده یا نه
function isEnrolled(courseId) {
    const enrolled = JSON.parse(localStorage.getItem('polaris_enrolled') || '[]');
    return enrolled.some(course => course.id === courseId);
}

// رندر کردن دوره‌ها
function renderCourses() {
    const container = document.getElementById('coursesContainer');
    if (!container) {
        console.error("coursesContainer not found!");
        return;
    }
    
    let filteredCourses = [...coursesData];
    
    // اعمال فیلتر دسته‌بندی
    if (currentFilter !== "all") {
        filteredCourses = filteredCourses.filter(course => course.category === currentFilter);
    }
    
    // اعمال جستجو
    if (currentSearch.trim() !== "") {
        const searchTerm = currentSearch.toLowerCase().trim();
        filteredCourses = filteredCourses.filter(course => 
            course.title.toLowerCase().includes(searchTerm) || 
            course.desc.toLowerCase().includes(searchTerm)
        );
    }
    
    // حالت بدون نتیجه
    if (filteredCourses.length === 0) {
        container.innerHTML = `
            <div class="no-results">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="60" height="60">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="12" y1="8" x2="12" y2="12"/>
                    <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                <h3>دوره‌ای یافت نشد</h3>
                <p>لطفاً عبارت دیگری را جستجو کنید یا فیلتر دیگری انتخاب کنید.</p>
            </div>
        `;
        return;
    }
    
    // ساخت HTML کارت‌ها
    let html = "";
    for (let i = 0; i < filteredCourses.length; i++) {
        const course = filteredCourses[i];
        const enrolled = isEnrolled(course.id);
        
        html += `
            <div class="course-card" data-category="${course.category}" data-id="${course.id}">
                <div class="course-image">
                    <img src="${course.image}" alt="${course.title}" onerror="this.src='https://picsum.photos/id/20/400/250'">
                    <div class="course-badge">${course.level}</div>
                    ${enrolled ? '<div class="course-badge enrolled-badge" style="background: linear-gradient(135deg, #10b981, #059669); right: auto; left: 15px;">✓ ثبت‌نام شده</div>' : ''}
                </div>
                <div class="course-content">
                    <div class="course-meta">
                        <span>
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="10"/>
                                <polyline points="12 6 12 12 16 14"/>
                            </svg>
                            ${course.duration}
                        </span>
                        <span>
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                                <circle cx="9" cy="7" r="4"/>
                                <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                                <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                            </svg>
                            ${toPersianNumber(course.studentsCount)} دانشجو
                        </span>
                    </div>
                    <h3 class="course-title">${course.title}</h3>
                    <p class="course-desc">${course.desc.substring(0, 100)}${course.desc.length > 100 ? '...' : ''}</p>
                    <div class="course-features">
                        ${course.features.map(f => `<span class="feature-tag">${f}</span>`).join('')}
                    </div>
                    <div class="course-footer">
                        <span class="course-price">${formatPrice(course.price)}</span>
                        <div style="display: flex; gap: 10px;">
                            <button onclick="viewCourse(${course.id})" class="btn btn-outline btn-sm">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                                جزئیات
                            </button>
                            ${!enrolled ? `
                                <button onclick="addToCart(${course.id}, '${course.title.replace(/'/g, "\\'")}', ${course.price}, '${course.image}')" class="btn btn-primary btn-sm">
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
                                    خرید
                                </button>
                                <button onclick="buyNow(${course.id}, '${course.title.replace(/'/g, "\\'")}', ${course.price}, '${course.image}')" class="btn btn-outline btn-sm" style="background: var(--accent-glow);">
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
                                    خرید سریع
                                </button>
                            ` : `
                                <button class="btn btn-outline btn-sm" disabled style="opacity:0.6; cursor:not-allowed;">
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
                                    ثبت‌نام شده
                                </button>
                            `}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    container.innerHTML = html;
}

// رندر کردن محصولات من (دوره‌های خریداری شده) در صفحه داشبورد
function renderMyProducts() {
    const container = document.getElementById('productsList');
    if (!container) return;
    
    const enrolled = JSON.parse(localStorage.getItem('polaris_enrolled') || '[]');
    const currentLang = localStorage.getItem('polaris_lang') || 'fa';
    const tomanText = currentLang === 'fa' ? 'تومان' : 'Toman';
    
    if (enrolled.length === 0) {
        container.innerHTML = `
            <div class="empty-state-glass">
                <div class="empty-icon">🛒</div>
                <h4>${currentLang === 'fa' ? 'هیچ محصولی خریداری نکرده‌اید' : 'No products purchased'}</h4>
                <a href="courses.html" class="btn btn-primary">${currentLang === 'fa' ? 'مشاهده دوره‌ها' : 'View Courses'}</a>
            </div>
        `;
        return;
    }
    
    container.innerHTML = enrolled.map(course => `
        <div class="course-card-small">
            <img src="${course.image}" class="course-img-small" onerror="this.src='https://picsum.photos/id/20/100/100'">
            <div class="course-info-small">
                <h4>${course.title}</h4>
                <div class="progress-small">
                    <div class="progress-bar-small">
                        <div class="progress-fill-small" style="width: ${course.progress || 0}%"></div>
                    </div>
                    <span class="progress-text-small">${toPersianNumber(course.progress || 0)}%</span>
                </div>
                <div class="course-actions-small">
                    <span class="price-small">${course.price.toLocaleString()} ${tomanText}</span>
                    <a href="course-single.html?id=${course.id}" class="btn-small">${course.progress === 100 ? 'مشاهده' : 'ادامه'}</a>
                </div>
            </div>
        </div>
    `).join('');
}

// انیمیشن toast
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    .enrolled-badge {
        position: absolute;
        top: 15px;
        left: 15px;
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
    }
`;
document.head.appendChild(style);

// تنظیم Event Listeners
function setupEventListeners() {
    // فیلترها
    const filterTabs = document.querySelectorAll(".filter-tab");
    if (filterTabs.length > 0) {
        filterTabs.forEach(tab => {
            tab.addEventListener("click", function() {
                filterTabs.forEach(t => t.classList.remove("active"));
                this.classList.add("active");
                currentFilter = this.getAttribute("data-filter");
                renderCourses();
            });
        });
    }
    
    // جستجو
    const searchInput = document.getElementById("searchCourses");
    if (searchInput) {
        searchInput.addEventListener("input", function(e) {
            currentSearch = e.target.value;
            renderCourses();
        });
    }
}

// مقداردهی اولیه
document.addEventListener("DOMContentLoaded", function() {
    console.log("صفحه دوره‌ها بارگذاری شد، در حال رندر کردن...");
    
    // مقداردهی اولیه دوره‌های خریداری شده
    initEnrolledCourses();
    
    // رندر دوره‌ها
    renderCourses();
    setupEventListeners();
    updateCartCount();
    
    // همگام‌سازی با تغییرات سبد خرید
    window.addEventListener('storage', function(e) {
        if (e.key === 'polaris_cart') {
            updateCartCount();
        }
        if (e.key === 'polaris_enrolled') {
            renderCourses();
        }
    });
    
    // قرار دادن توابع در window برای دسترسی از onclick
    window.addToCart = addToCart;
    window.buyNow = buyNow;
    window.viewCourse = viewCourse;
    window.updateCartCount = updateCartCount;
    window.renderMyProducts = renderMyProducts;
});

// برای اطمینان از اجرا شدن اگر DOM قبلاً لود شده بود
if (document.readyState === 'loading') {
    // منتظر DOMContentLoaded می‌مانیم
} else {
    console.log("DOM قبلاً لود شده بود، اجرای مستقیم...");
    initEnrolledCourses();
    renderCourses();
    setupEventListeners();
    updateCartCount();
    window.addToCart = addToCart;
    window.buyNow = buyNow;
    window.viewCourse = viewCourse;
    window.updateCartCount = updateCartCount;
    window.renderMyProducts = renderMyProducts;
}