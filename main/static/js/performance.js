// Performance optimizations for the application
document.addEventListener('DOMContentLoaded', function() {
    // Lazy load images
    lazyLoadImages();
    
    // Debounce event handlers
    setupDebouncedEvents();
    
    // Optimize animations
    optimizeAnimations();
});

// Lazy load images to improve page load performance
function lazyLoadImages() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    const src = img.getAttribute('data-src');
                    
                    if (src) {
                        img.src = src;
                        img.removeAttribute('data-src');
                    }
                    
                    observer.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    } else {
        // Fallback for browsers that don't support IntersectionObserver
        document.querySelectorAll('img[data-src]').forEach(img => {
            img.src = img.getAttribute('data-src');
            img.removeAttribute('data-src');
        });
    }
}

// Debounce function to limit how often a function can be called
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

// Setup debounced event handlers for better performance
function setupDebouncedEvents() {
    // Debounce scroll events
    const debouncedScroll = debounce(() => {
        // Handle scroll events here
        console.log('Scroll event debounced');
    }, 100);
    
    window.addEventListener('scroll', debouncedScroll);
    
    // Debounce resize events
    const debouncedResize = debounce(() => {
        // Handle resize events here
        console.log('Resize event debounced');
    }, 250);
    
    window.addEventListener('resize', debouncedResize);
    
    // Debounce input events for search fields
    document.querySelectorAll('input[type="search"], input[type="text"].search-input').forEach(input => {
        const debouncedInput = debounce((e) => {
            // Handle input events here
            console.log('Input event debounced', e.target.value);
        }, 300);
        
        input.addEventListener('input', debouncedInput);
    });
}

// Optimize animations for better performance
function optimizeAnimations() {
    // Use requestAnimationFrame for smooth animations
    const animateElements = document.querySelectorAll('.animate-on-scroll');
    
    if (animateElements.length > 0) {
        let lastScrollPosition = window.scrollY;
        
        const handleScroll = () => {
            // Only run if scroll position has changed significantly
            if (Math.abs(window.scrollY - lastScrollPosition) < 10) {
                requestAnimationFrame(handleScroll);
                return;
            }
            
            lastScrollPosition = window.scrollY;
            
            animateElements.forEach(element => {
                const elementTop = element.getBoundingClientRect().top;
                const elementVisible = 150;
                
                if (elementTop < window.innerHeight - elementVisible) {
                    element.classList.add('active');
                } else {
                    element.classList.remove('active');
                }
            });
            
            requestAnimationFrame(handleScroll);
        };
        
        requestAnimationFrame(handleScroll);
    }
    
    // Reduce paint operations by using transform instead of top/left
    document.querySelectorAll('.animated-element').forEach(element => {
        element.style.transform = 'translateZ(0)'; // Hardware acceleration
    });
}