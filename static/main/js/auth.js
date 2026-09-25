
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


// ========== رویداد اصلی ==========
document.addEventListener('DOMContentLoaded', function() {
    initAuthTabs();
});