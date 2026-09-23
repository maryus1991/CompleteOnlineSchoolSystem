// ============================================
// COURSE-SINGLE.JS - صفحه جزئیات دوره (با عکس‌های واقعی)
// ============================================

// تبدیل عدد به فارسی
function toPersianNumber(num) {
    const persianDigits = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
    return num.toString().replace(/\d/g, d => persianDigits[d]);
}

// فرمت قیمت
function formatPrice(price) {
    return toPersianNumber(price.toLocaleString()) + ' تومان';
}

// تصاویر دوره‌ها (از فایل‌های واقعی پروژه)
const courseImages = {
    1: "assets/image/front.jpg",
    2: "assets/image/node.webp",
    3: "assets/image/full.jpg",
    4: "assets/image/python.webp",
    5: "assets/image/js.webp",
    6: "assets/image/docker.webp"
};

// آواتارهای مربیان (بر اساس جنسیت)
const avatarImages = {
    // مردها
    male1: "assets/image/user1.jpg",
    male2: "assets/image/user2.jpg",
    male3: "assets/image/user3.jpg",
    // زنها
    female1: "assets/image/user4.jpg",
    female2: "assets/image/user5.jpg",
    female3: "assets/image/user6.jpg"
};

// داده‌های کامل دوره‌ها
const coursesData = {
    1: {
        id: 1,
        title: "بوت‌کمپ جامع فرانت‌اند",
        price: 8500000,
        image: courseImages[1],
        duration: "۳۲ جلسه",
        level: "مبتدی تا پیشرفته",
        status: "در حال ثبت‌نام",
        studentsCount: 1247,
        lastUpdate: "دی ۱۴۰۴",
        description: "آموزش کامل فرانت‌اند از صفر تا صد با پروژه‌های واقعی",
        longDescription: "این بوت‌کمپ ۳۲ جلسه‌ای شما را از سطح مبتدی به یک فرانت‌اندکار حرفه‌ای تبدیل می‌کند. سرفصل‌ها شامل: مبانی وب، HTML5/CSS3، Flexbox و Grid، جاوااسکریپت مدرن (ES6+)، React.js با Hooks و Context API، Next.js، TypeScript، Git و GitHub، و پروژه نهایی فروشگاه اینترنتی. تمام پروژه‌ها واقعی و قابل ارائه در رزومه هستند.",
        curriculum: [
            { title: "مقدمه‌ای بر دنیای وب و اینترنت", duration: "۲ ساعت" },
            { title: "HTML5 و ساختار صفحات وب مدرن", duration: "۴ ساعت" },
            { title: "CSS3 و استایل‌دهی حرفه‌ای (Flexbox, Grid, Animations)", duration: "۸ ساعت" },
            { title: "JavaScript مدرن (ES6+, Async, API, DOM)", duration: "۱۲ ساعت" },
            { title: "React.js - مبانی تا پیشرفته (Hooks, Context, Router)", duration: "۱۴ ساعت" },
            { title: "Next.js و SSR (Server Side Rendering)", duration: "۸ ساعت" },
            { title: "TypeScript و تایپ‌های پیشرفته", duration: "۶ ساعت" },
            { title: "Git & GitHub - ورژن کنترل حرفه‌ای", duration: "۴ ساعت" },
            { title: "پروژه نهایی: فروشگاه اینترنتی کامل", duration: "۱۰ ساعت" }
        ],
        instructor: {
            name: "آرش محمدی",
            role: "Senior Front-End Engineer در گوگل",
            bio: "با بیش از ۱۰ سال سابقه در توسعه محصولات وب بزرگ، عضو تیم‌های فنی گوگل و منتور ارشد آکادمی پولاریس. بیش از ۵۰۰۰ دانشجو در سراسر ایران تحت نظر ایشان آموزش دیده‌اند.",
            avatar: avatarImages.male1,
            experience: "۱۰+ سال",
            courses: "۱۲ دوره"
        },
        reviews: [
            { name: "محمد رضایی", avatar: avatarImages.male3, text: "بی‌نظیرترین دوره‌ای که تا حالا دیدم. محتوا بسیار کامل و پروژه‌ها عالی بودن.", rating: 5 },
            { name: "زهرا حسینی", avatar: avatarImages.female1, text: "بعد از این دوره تونستم به راحتی مصاحبه فرانت‌اند رو پشت سر بذارم. ممنون از تیم پولاریس.", rating: 5 },
            { name: "علی کریمی", avatar: avatarImages.male2, text: "پشتیبانی عالی و محتوای به‌روز. حتماً دوره‌های دیگه رو هم تهیه می‌کنم.", rating: 5 }
        ]
    },
    2: {
        id: 2,
        title: "مهندسی بک‌اند با Node.js",
        price: 9200000,
        image: courseImages[2],
        duration: "۲۸ جلسه",
        level: "متوسط تا پیشرفته",
        status: "در حال ثبت‌نام",
        studentsCount: 892,
        lastUpdate: "آذر ۱۴۰۴",
        description: "طراحی و پیاده‌سازی APIهای مقیاس‌پذیر با Node.js و Express",
        longDescription: "دوره جامع بک‌اند با Node.js شامل مبانی سرور، Express.js، طراحی RESTful API، GraphQL، احراز هویت (JWT، OAuth)، دیتابیس‌های MongoDB و PostgreSQL، Docker، Redis و استقرار پروژه روی سرورهای ابری.",
        curriculum: [
            { title: "مفاهیم بک‌اند و معماری سرور", duration: "۳ ساعت" },
            { title: "Node.js و Event Loop", duration: "۴ ساعت" },
            { title: "Express.js و مسیریابی پیشرفته", duration: "۵ ساعت" },
            { title: "RESTful API Design - اصول و بهترین‌ها", duration: "۶ ساعت" },
            { title: "MongoDB و Mongoose ODM", duration: "۶ ساعت" },
            { title: "PostgreSQL و Sequelize ORM", duration: "۵ ساعت" },
            { title: "احراز هویت و امنیت (JWT, OAuth, Bcrypt)", duration: "۵ ساعت" },
            { title: "Redis و کش‌سازی", duration: "۳ ساعت" },
            { title: "Docker و کانتینریزیشن", duration: "۴ ساعت" },
            { title: "پروژه نهایی: پلتفرم فروشگاهی کامل", duration: "۸ ساعت" }
        ],
        instructor: {
            name: "سارا احمدی",
            role: "Back-End Engineer در آمازون",
            bio: "متخصص معماری میکروسرویس و سیستم‌های توزیع‌شده با سابقه ۸ سال کار در آمازون و مایکروسافت.",
            avatar: avatarImages.female2,
            experience: "۸+ سال",
            courses: "۸ دوره"
        },
        reviews: [
            { name: "رضا محمدی", avatar: avatarImages.male1, text: "بسیار عالی و کاربردی. تدریس سارا خانم فوق‌العاده روان و مفید بود.", rating: 5 },
            { name: "نرگس احمدی", avatar: avatarImages.female3, text: "بعد از این دوره تونستم اولین پروژه بک‌اند خودم رو راه‌اندازی کنم.", rating: 5 }
        ]
    },
    3: {
        id: 3,
        title: "پکیج کامل فول‌استک",
        price: 15000000,
        image: courseImages[3],
        duration: "۴۸ جلسه",
        level: "صفر تا استخدام",
        status: "پرفروش‌ترین",
        studentsCount: 2341,
        lastUpdate: "بهمن ۱۴۰۴",
        description: "همه مهارت‌های لازم برای یک فول‌استک دولوپر حرفه‌ای در یک پکیج کامل",
        longDescription: "پکیج فول‌استک شامل هر دو دوره فرانت‌اند و بک‌اند به علاوه مبانی DevOps، پروژه‌های عملی گسترده، آمادگی برای مصاحبه شغلی و ساخت CV حرفه‌ای. با گذراندن این دوره می‌توانید به تنهایی یک وب‌اپلیکیشن کامل از صفر تا صد طراحی و پیاده‌سازی کنید.",
        curriculum: [
            { title: "بخش اول: فرانت‌اند کامل (HTML, CSS, JS, React, Next)", duration: "۲۴ جلسه" },
            { title: "بخش دوم: بک‌اند با Node.js و Express", duration: "۱۴ جلسه" },
            { title: "بخش سوم: دیتابیس‌ها (MongoDB, PostgreSQL)", duration: "۴ جلسه" },
            { title: "بخش چهارم: DevOps و Docker", duration: "۳ جلسه" },
            { title: "بخش پنجم: پروژه نهایی فول‌استک", duration: "۳ جلسه" }
        ],
        instructor: {
            name: "علی رضایی",
            role: "Full-Stack Architect در اسنپ",
            bio: "تبدیل ایده‌های پیچیده به محصولات مقیاس‌پذیر با معماری مدرن. بیش از ۱۲ سال تجربه در شرکت‌های بزرگ.",
            avatar: avatarImages.male2,
            experience: "۱۲+ سال",
            courses: "۱۵ دوره"
        },
        reviews: [
            { name: "مهدی کریمی", avatar: avatarImages.male1, text: "بهترین سرمایه‌گذاری که تو عمرم کردم. بعد از این دوره استخدام شدم.", rating: 5 },
            { name: "فاطمه نوری", avatar: avatarImages.female1, text: "پشتیبانی عالی و محتوای خیلی کامل. واقعاً ارزش خرید داره.", rating: 5 }
        ]
    },
    4: {
        id: 4,
        title: "هوش مصنوعی با Python",
        price: 11000000,
        image: courseImages[4],
        duration: "۳۶ جلسه",
        level: "پیشرفته",
        status: "جدید",
        studentsCount: 567,
        lastUpdate: "اسفند ۱۴۰۴",
        description: "یادگیری ماشین، شبکه‌های عصبی و پروژه‌های واقعی AI",
        longDescription: "دوره تخصصی هوش مصنوعی شامل Python پیشرفته، NumPy، Pandas، Matplotlib، Scikit-learn، TensorFlow، Keras، شبکه‌های عصبی عمیق، پردازش تصویر (OpenCV) و پردازش زبان طبیعی (NLP).",
        curriculum: [
            { title: "Python پیشرفته برای دیتاساینس", duration: "۶ ساعت" },
            { title: "دیتاساینس و تحلیل داده (NumPy, Pandas)", duration: "۸ ساعت" },
            { title: "مصورسازی داده (Matplotlib, Seaborn)", duration: "۴ ساعت" },
            { title: "یادگیری ماشین (Scikit-learn)", duration: "۱۰ ساعت" },
            { title: "یادگیری عمیق با TensorFlow و Keras", duration: "۱۰ ساعت" },
            { title: "پردازش تصویر با OpenCV", duration: "۴ ساعت" },
            { title: "پردازش زبان طبیعی (NLP)", duration: "۴ ساعت" },
            { title: "پروژه نهایی هوش مصنوعی", duration: "۶ ساعت" }
        ],
        instructor: {
            name: "دکتر مریم حسینی",
            role: "AI Research Scientist",
            bio: "PhD در هوش مصنوعی از دانشگاه صنعتی شریف، محقق ارشد در حوزه یادگیری عمیق و بینایی کامپیوتر.",
            avatar: avatarImages.female1,
            experience: "۷+ سال",
            courses: "۶ دوره"
        },
        reviews: [
            { name: "کیان رستمی", avatar: avatarImages.male3, text: "دکتر حسینی فوق‌العاده مسلط و با حوصله تدریس می‌کنند. واقعاً لذت بردم.", rating: 5 },
            { name: "الناز صفری", avatar: avatarImages.female2, text: "دوره بسیار سنگین و کامل. برای کسایی که واقعاً می‌خوان AI یاد بگیرن عالیه.", rating: 5 }
        ]
    },
    5: {
        id: 5,
        title: "TypeScript پیشرفته",
        price: 7800000,
        image: courseImages[5],
        duration: "۲۴ جلسه",
        level: "متوسط",
        status: "در حال ثبت‌نام",
        studentsCount: 745,
        lastUpdate: "دی ۱۴۰۴",
        description: "تایپ‌های پیشرفته، جنریک‌ها، دکوریتورها و طراحی scalable applications",
        longDescription: "دوره تخصصی TypeScript شامل تایپ‌های پیشرفته، جنریک‌ها، utility types، دکوریتورها، declaration merging، ماژول‌ها و استفاده عملی در پروژه‌های React و Node.js. همچنین آشنایی با Deno و Bun.",
        curriculum: [
            { title: "مبانی TypeScript و تایپ‌های پایه", duration: "۴ ساعت" },
            { title: "اینترفیس‌ها و تایپ‌های پیشرفته", duration: "۴ ساعت" },
            { title: "جنریک‌ها و Utility Types", duration: "۵ ساعت" },
            { title: "دکوریتورها و متادیتا", duration: "۳ ساعت" },
            { title: "TypeScript با React و Next.js", duration: "۴ ساعت" },
            { title: "TypeScript با Node.js", duration: "۴ ساعت" }
        ],
        instructor: {
            name: "آرش محمدی",
            role: "Senior Front-End Engineer",
            bio: "توسعه‌دهنده ارشد فرانت‌اند با بیش از ۸ سال سابقه کار با TypeScript در پروژه‌های بزرگ مقیاس.",
            avatar: avatarImages.male1,
            experience: "۸+ سال",
            courses: "۵ دوره"
        },
        reviews: [
            { name: "سعید ملکی", avatar: avatarImages.male3, text: "دوره عالی و عملی. تونستم تایپ‌اسکریپت رو حرفه‌ای یاد بگیرم.", rating: 5 }
        ]
    },
    6: {
        id: 6,
        title: "Docker و Kubernetes",
        price: 12500000,
        image: courseImages[6],
        duration: "۴۰ جلسه",
        level: "متوسط تا پیشرفته",
        status: "در حال ثبت‌نام",
        studentsCount: 623,
        lastUpdate: "بهمن ۱۴۰۴",
        description: "کانتینریزیشن، ارکستراسیون و استقرار خودکار اپلیکیشن‌ها",
        longDescription: "دوره جامع DevOps شامل Docker (image, container, network, volume, docker-compose)، Kubernetes (pods, services, deployments, ingress, configmap, secrets)، CI/CD با GitLab/GitHub Actions، Helm و استقرار در ابر.",
        curriculum: [
            { title: "مفاهیم کانتینر و Docker", duration: "۶ ساعت" },
            { title: "Docker Compose و شبکه‌سازی", duration: "۶ ساعت" },
            { title: "Kubernetes - مفاهیم پایه", duration: "۸ ساعت" },
            { title: "مدیریت استیبل و اسکیلینگ", duration: "۶ ساعت" },
            { title: "CI/CD و استقرار خودکار", duration: "۶ ساعت" },
            { title: "Helm و مدیریت پکیج", duration: "۴ ساعت" },
            { title: "پروژه نهایی: استقرار کامل اپ", duration: "۴ ساعت" }
        ],
        instructor: {
            name: "دکتر مریم حسینی",
            role: "DevOps Lead",
            bio: "متخصص زیرساخت و معماری ابری با بیش از ۷ سال سابقه کار با Kubernetes در شرکت‌های بزرگ.",
            avatar: avatarImages.female1,
            experience: "۷+ سال",
            courses: "۴ دوره"
        },
        reviews: [
            { name: "حمید رضایی", avatar: avatarImages.male2, text: "بسیار کاربردی و به‌روز. بعد از این دوره تونستم به عنوان DevOps مشغول به کار بشم.", rating: 5 }
        ]
    }
};

// دوره‌های مشابه
const relatedCoursesList = [1, 2, 3, 4, 5, 6];

// بررسی ثبت‌نام قبلی
function checkIfEnrolled(courseId) {
    const enrolled = JSON.parse(localStorage.getItem("polaris_enrolled") || "[]");
    return enrolled.some(c => c.id === courseId);
}

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

// خرید سریع
function buyNow(id, title, price, image) {
    addToCart(id, title, price, image);
    setTimeout(() => {
        window.location.href = 'checkout.html';
    }, 500);
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

// تولید ستاره‌ها
function renderStars(rating) {
    let stars = '';
    for (let i = 0; i < 5; i++) {
        if (i < rating) {
            stars += `<svg viewBox="0 0 24 24" fill="#ffc107" stroke="none" width="16" height="16"><polygon points="12 17.27 18.18 21 16.54 13.97 22 9.24 14.81 8.63 12 2 9.19 8.63 2 9.24 7.46 13.97 5.82 21 12 17.27"/></svg>`;
        } else {
            stars += `<svg viewBox="0 0 24 24" fill="none" stroke="#ffc107" width="16" height="16"><polygon points="12 17.27 18.18 21 16.54 13.97 22 9.24 14.81 8.63 12 2 9.19 8.63 2 9.24 7.46 13.97 5.82 21 12 17.27"/></svg>`;
        }
    }
    return stars;
}

// بارگذاری جزئیات دوره
function loadCourseDetails() {
    const urlParams = new URLSearchParams(window.location.search);
    const courseId = parseInt(urlParams.get("id"));
    
    const course = coursesData[courseId] || coursesData[1];
    const isEnrolled = checkIfEnrolled(course.id);
    
    const container = document.getElementById("courseContent");
    if (!container) return;
    
    let html = `
        <div class="course-hero">
            <div class="course-hero-info">
                <h1>${course.title}</h1>
                <div class="course-meta-list">
                    <div class="meta-item">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                        <span>${course.duration}</span>
                    </div>
                    <div class="meta-item">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
                        <span>${course.level}</span>
                    </div>
                    <div class="meta-item">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                        <span>${toPersianNumber(course.studentsCount)} دانشجو</span>
                    </div>
                    <div class="meta-item">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                        <span>آخرین بروزرسانی: ${course.lastUpdate}</span>
                    </div>
                </div>
                <div class="course-price-large">${formatPrice(course.price)}</div>
                <p class="course-description">${course.longDescription}</p>
                
                <div class="course-features">
                    <div class="feature-item">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                        <span>${course.instructor.name} - ${course.instructor.role}</span>
                    </div>
                    <div class="feature-item">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22 6 12 13 2 6"/></svg>
                        <span>گواهی معتبر پایان دوره</span>
                    </div>
                    <div class="feature-item">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
                        <span>دسترسی مادام‌العمر</span>
                    </div>
                    <div class="feature-item">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
                        <span>پشتیبانی ۲۴/۷</span>
                    </div>
                </div>
            </div>
            
            <div class="course-sidebar-card">
                <img src="${course.image}" alt="${course.title}" onerror="this.src='assets/image/front.jpg'">
                <div class="course-price">${formatPrice(course.price)}</div>
                ${!isEnrolled ? `
                    <button onclick="addToCart(${course.id}, '${course.title.replace(/'/g, "\\'")}', ${course.price}, '${course.image}')" class="btn btn-primary">افزودن به سبد خرید</button>
                    <button onclick="buyNow(${course.id}, '${course.title.replace(/'/g, "\\'")}', ${course.price}, '${course.image}')" class="btn btn-outline" style="margin-top: 10px;">خرید سریع</button>
                ` : `
                    <button class="btn btn-outline" disabled style="opacity:0.6;">✓ قبلاً ثبت‌نام کرده‌اید</button>
                    <a href="dashboard.html" class="btn btn-primary" style="display:block; text-align:center; margin-top:10px;">رفتن به داشبورد</a>
                `}
                <div class="secure-badge" style="margin-top: 20px; font-size:0.7rem; color:var(--text-muted); text-align:center;">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
                    <span>پرداخت امن و رمزنگاری شده</span>
                </div>
            </div>
        </div>
        
        <div class="curriculum-section">
            <h2>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="24" height="24"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
                سرفصل‌های دوره
            </h2>
            ${course.curriculum.map((item, index) => `
                <div class="curriculum-item">
                    <div class="curriculum-title">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                        <span>جلسه ${index + 1}: ${item.title}</span>
                    </div>
                    <div class="curriculum-duration">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                        ${item.duration}
                    </div>
                </div>
            `).join('')}
        </div>
        
        <div class="instructor-section">
            <img src="${course.instructor.avatar}" alt="${course.instructor.name}" class="instructor-avatar" onerror="this.src='assets/image/user1.jpg'">
            <div class="instructor-info">
                <h3>${course.instructor.name}</h3>
                <div class="instructor-badge">${course.instructor.role}</div>
                <div style="display: flex; gap: 20px; margin: 12px 0;">
                    <span style="color:var(--text-muted);">${course.instructor.experience} تجربه</span>
                    <span style="color:var(--text-muted);">${course.instructor.courses} دوره</span>
                </div>
                <p>${course.instructor.bio}</p>
            </div>
        </div>
        
        <div class="reviews-section">
            <h2>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="24" height="24"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
                نظرات دانشجویان
            </h2>
            <div class="reviews-grid">
                ${course.reviews.map(review => `
                    <div class="review-card">
                        <div class="review-header">
                            <img src="${review.avatar}" alt="${review.name}" class="review-avatar" onerror="this.src='assets/image/user5.jpg'">
                            <div>
                                <strong>${review.name}</strong>
                                <div class="review-stars">${renderStars(review.rating)}</div>
                            </div>
                        </div>
                        <p class="review-text">${review.text}</p>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    // اضافه کردن دوره‌های مشابه
    const otherCourses = relatedCoursesList.filter(id => id !== course.id).slice(0, 3);
    if (otherCourses.length > 0) {
        html += `
            <div class="related-courses" style="margin-top: 50px;">
                <h2 style="margin-bottom: 30px; font-size:1.6rem;">دوره‌های مشابه</h2>
                <div class="related-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 24px;">
                    ${otherCourses.map(id => {
                        const c = coursesData[id];
                        if (!c) return '';
                        return `
                            <a href="course-single.html?id=${c.id}" class="related-card" style="background: var(--bg-card); border-radius: 20px; padding: 20px; border: 1px solid var(--border-color); text-decoration: none; display: block; transition: all 0.3s ease;">
                                <img src="${c.image}" alt="${c.title}" style="width:100%; border-radius:14px; aspect-ratio:16/9; object-fit:cover; margin-bottom:14px;" onerror="this.src='assets/image/front.jpg'">
                                <h4 style="color:var(--text-primary); margin-bottom:8px;">${c.title}</h4>
                                <div class="price" style="color:var(--accent-color); font-weight:700;">${formatPrice(c.price)}</div>
                            </a>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

// انیمیشن toast
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
`;
document.head.appendChild(style);

// مقداردهی اولیه
document.addEventListener("DOMContentLoaded", function() {
    loadCourseDetails();
    updateCartCount();
    
    // همگام‌سازی با تغییرات سبد خرید
    window.addEventListener('storage', (e) => {
        if (e.key === 'polaris_cart') {
            updateCartCount();
        }
    });
    
    // قرار دادن توابع در window
    window.addToCart = addToCart;
    window.buyNow = buyNow;
    window.updateCartCount = updateCartCount;
});