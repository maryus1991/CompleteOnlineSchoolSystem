
(function () {
    const html = document.documentElement;
    const btn = document.getElementById('themeToggle');
    const textEl = document.getElementById('themeToggleText');
    const moon = document.querySelector('.theme-icon-moon');
    const sun = document.querySelector('.theme-icon-sun');
    const KEY = 'dashboard-theme';

    function applyTheme(theme) {
        html.setAttribute('data-theme', theme);
        try { localStorage.setItem(KEY, theme); } catch (e) {}

        const isDark = theme === 'dark';
        if (moon) moon.style.display = isDark ? 'block' : 'none';
        if (sun) sun.style.display = isDark ? 'none' : 'block';
        if (textEl) textEl.textContent = isDark ? 'تم روشن' : 'تم تاریک';
        if (btn) btn.setAttribute('aria-label', isDark ? 'تغییر به تم روشن' : 'تغییر به تم تاریک');
    }

    let saved = 'dark';
    try {
        saved = localStorage.getItem(KEY) || html.getAttribute('data-theme') || 'dark';
    } catch (e) {}
    applyTheme(saved === 'light' ? 'light' : 'dark');

    if (btn) {
        btn.addEventListener('click', function () {
            const current = html.getAttribute('data-theme') || 'dark';
            applyTheme(current === 'dark' ? 'light' : 'dark');
        });
    }
})();
