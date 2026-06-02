/* ========================================
   ZARA STYLE - Інтерактивні елементи
   Інтеграція з Django проектом
   ======================================== */

// Зникаюче меню при скролі
document.addEventListener('DOMContentLoaded', function() {
    const header = document.getElementById('siteHeader');
    let lastScroll = 0;

    if (header) {
        window.addEventListener('scroll', function() {
            const currentScroll = window.scrollY;

            if (currentScroll > 80 && currentScroll > lastScroll) {
                header.classList.add('header-hidden');
                header.classList.remove('header-visible');
            } else {
                header.classList.remove('header-hidden');
                header.classList.add('header-visible');
            }
            lastScroll = currentScroll;
        });
        header.classList.add('header-visible');
    }

    // Анімація появи елементів при скролі (Intersection Observer)
    const fadeElements = document.querySelectorAll('.product-card, .hero, .secondary-banner, .category-card');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

    fadeElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(25px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // Анімація для карток, які додаються динамічно
    setTimeout(() => {
        document.querySelectorAll('.product-card').forEach(card => {
            if (card.style.opacity !== '1') {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                observer.observe(card);
            }
        });
    }, 200);
});

// Функція отримання CSRF токену
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Захист від подвійного додавання
let cartRequestInProgress = false;

// Додавання в кошик через AJAX (глобальна функція)
function addToCart(productId, quantity = 1) {
    // Запобігаємо одночасним запитам
    if (cartRequestInProgress) {
        console.log('Запит вже виконується');
        return Promise.reject('Запит вже виконується');
    }

    cartRequestInProgress = true;
    const csrftoken = getCookie('csrftoken');

    return fetch('/cart/add-ajax/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrftoken
        },
        body: `product_id=${productId}&quantity=${quantity}`
    })
    .then(response => response.json())
    .then(data => {
        cartRequestInProgress = false;
        if (data.success) {
            // Оновлюємо лічильник кошика
            const cartBadges = document.querySelectorAll('.cart-count');
            cartBadges.forEach(badge => {
                badge.innerText = data.cart_count;
            });
            showNotification('success', data.message);
            return data;
        } else {
            showNotification('error', data.message);
            throw new Error(data.message);
        }
    })
    .catch(error => {
        cartRequestInProgress = false;
        showNotification('error', 'Помилка при додаванні до кошика');
        console.error('Error:', error);
    });
}

// Показ повідомлень
function showNotification(type, message) {
    // Видаляємо старі повідомлення
    const oldNotification = document.querySelector('.zara-notification');
    if (oldNotification) oldNotification.remove();

    const notification = document.createElement('div');
    notification.className = `zara-notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        z-index: 9999;
        background: ${type === 'success' ? '#28a745' : '#dc3545'};
        color: white;
        padding: 12px 20px;
        border-radius: 0;
        font-size: 0.8rem;
        letter-spacing: 1px;
        font-family: 'Montserrat', sans-serif;
        animation: slideInRight 0.3s ease;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    `;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Додавання CSS анімацій для повідомлень
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    .btn-add-to-cart-loading {
        opacity: 0.7;
        pointer-events: none;
    }
`;
document.head.appendChild(style);

// ===== ОДИН ОБРОБНИК ДЛЯ ВСІХ КНОПОК (ВИПРАВЛЕНО) =====
document.addEventListener('DOMContentLoaded', function() {
    // ЄДИНИЙ обробник через делегування
    document.body.addEventListener('click', function(e) {
        // Шукаємо кнопку
        const btn = e.target.closest('.add-to-cart-btn, .quick-view-btn');
        if (!btn) return;

        // Зупиняємо спливання події
        e.stopPropagation();
        e.preventDefault();

        // Отримуємо ID товару
        const productId = btn.dataset.id;
        if (!productId) return;

        // Запобігаємо повторним клікам
        if (btn.classList.contains('processing')) return;

        // Анімація кнопки
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Додається...';
        btn.classList.add('processing');
        btn.classList.add('btn-add-to-cart-loading');

        // Додаємо в кошик
        addToCart(productId, 1).finally(() => {
            btn.innerHTML = originalText;
            btn.classList.remove('processing');
            btn.classList.remove('btn-add-to-cart-loading');
        });
    });
});

// Вибір розміру на сторінці товару
document.addEventListener('DOMContentLoaded', function() {
    const sizeBtns = document.querySelectorAll('.size-btn');
    if (sizeBtns.length) {
        sizeBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                sizeBtns.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                const sizeInput = document.getElementById('selected-size');
                if (sizeInput) sizeInput.value = this.dataset.size;
            });
        });
    }

    // Вибір кольору
    const colorBtns = document.querySelectorAll('.color-btn');
    if (colorBtns.length) {
        colorBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                colorBtns.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                const colorInput = document.getElementById('selected-color');
                if (colorInput) colorInput.value = this.dataset.color;
            });
        });
    }
});

// Ліниве завантаження зображень
document.addEventListener('DOMContentLoaded', function() {
    const lazyImages = document.querySelectorAll('img[data-src]');
    if (lazyImages.length) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        });
        lazyImages.forEach(img => imageObserver.observe(img));
    }
});

// Плавний скрол до секцій
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href && href !== '#' && href !== '#catalog') {
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
});

// Автоматичне приховування flash-повідомлень через 5 секунд
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 4000);
        });
    }, 1000);
});