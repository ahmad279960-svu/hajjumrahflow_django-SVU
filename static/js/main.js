// static/js/main.js

document.addEventListener("DOMContentLoaded", function() {

    // Initialize Feather Icons
    feather.replace();

    // --- Animate cards on scroll view ---
    const cards = document.querySelectorAll('.card');
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = `fadeInUp 0.6s ${entry.target.dataset.delay || '0s'} forwards`;
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Add a slight delay to each card for a staggered effect
    cards.forEach((card, index) => {
        card.style.opacity = '0'; // Start hidden
        card.dataset.delay = `${index * 100}ms`;
        observer.observe(card);
    });
    
    // Add fadeInUp animation to head
    const style = document.createElement('style');
    style.innerHTML = `
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    `;
    document.head.appendChild(style);

    // --- Sidebar Link Hover Effect (JavaScript enhancement) ---
    // This is for a more advanced hover effect, complementing the CSS transition.
    const sidebarLinks = document.querySelectorAll('.sidebar .nav-link');

    sidebarLinks.forEach(link => {
        link.addEventListener('mouseenter', () => {
            // Add a class that might trigger a JS-driven animation or a more complex CSS animation
            // For now, the CSS hover effects are sufficient and cleaner.
            // This space is kept for future, more complex JS-driven UI effects if desired.
        });
        link.addEventListener('mouseleave', () => {
            // Remove the class
        });
    });

});