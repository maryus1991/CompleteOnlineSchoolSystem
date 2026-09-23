function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    document.querySelectorAll('.theme-btn').forEach(btn => btn.classList.toggle('active', btn.dataset.theme === theme));
    localStorage.setItem('theme', theme);
}
document.querySelectorAll('.theme-btn').forEach(btn => btn.addEventListener('click', () => setTheme(btn.dataset.theme)));

function setLanguage(lang) {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.dataset.i18n;
        if (translations[lang] && translations[lang][key]) el.textContent = translations[lang][key];
    });
    document.documentElement.setAttribute('lang', lang);
    document.querySelectorAll('.lang-btn').forEach(btn => btn.classList.toggle('active', btn.dataset.lang === lang));
    localStorage.setItem('lang', lang);
}
document.querySelectorAll('.lang-btn').forEach(btn => btn.addEventListener('click', () => setLanguage(btn.dataset.lang)));

function setDirection(dir) {
    document.documentElement.setAttribute('dir', dir);
    document.querySelectorAll('.dir-btn').forEach(btn => btn.classList.toggle('active', btn.dataset.dir === dir));
    // جابجایی موقعیت منو
    const nav = document.getElementById('mainNav');
    const headerInner = document.querySelector('.header-inner');
    const logo = document.querySelector('.logo');
    if (dir === 'ltr') {
        document.body.style.direction = 'ltr';
        if (headerInner) headerInner.style.flexDirection = 'row';
    } else {
        document.body.style.direction = 'rtl';
        if (headerInner) headerInner.style.flexDirection = 'row';
    }
    localStorage.setItem('dir', dir);
}
document.querySelectorAll('.dir-btn').forEach(btn => btn.addEventListener('click', () => setDirection(btn.dataset.dir)));

document.querySelector('.reset-settings')?.addEventListener('click', () => {
    localStorage.clear();
    setTheme('dark');
    setLanguage('fa');
    setDirection('rtl');
});

const currentTheme = localStorage.getItem('theme') || 'dark';
const currentLang = localStorage.getItem('lang') || 'fa';
const currentDir = localStorage.getItem('dir') || 'rtl';
setTheme(currentTheme);
setLanguage(currentLang);
setDirection(currentDir);