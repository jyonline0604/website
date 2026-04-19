// Main JavaScript - Externalized from inline handlers
// This improves security by removing inline event handlers (XSS prevention)

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all interactive components
    
    // Filter buttons (news.html, chapters.html)
    initFilterButtons();
    
    // Navigation buttons (chapter pages)
    initChapterNavigation();
    
    // Calculator forms (finance.html)
    initCalculators();
});

function initFilterButtons() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all buttons
            filterBtns.forEach(b => b.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');
            
            // Trigger category change event
            const event = new CustomEvent('categoryChange', {
                detail: { category: this.dataset.category }
            });
            document.dispatchEvent(event);
        });
    });
}

function initChapterNavigation() {
    const prevBtns = document.querySelectorAll('.prev-chapter-btn');
    const nextBtns = document.querySelectorAll('.next-chapter-btn');
    
    prevBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            window.history.back();
        });
    });
    
    nextBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const nextUrl = this.href;
            if (nextUrl && nextUrl !== '#') {
                window.location.href = nextUrl;
            }
        });
    });
}

function initCalculators() {
    // Compound interest calculator
    const calcBtns = document.querySelectorAll('.calculate-btn');
    calcBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Trigger calculation event
            const event = new CustomEvent('calculate', {
                detail: { type: this.dataset.calcType }
            });
            document.dispatchEvent(event);
        });
    });
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

console.log('Main JavaScript loaded successfully');
