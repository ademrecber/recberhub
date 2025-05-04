// Performance optimizations
document.addEventListener('DOMContentLoaded', () => {
    // Lazy load images
    const lazyLoadImages = () => {
        const lazyImages = document.querySelectorAll('img[data-src]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
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
        } else {
            // Fallback for browsers without IntersectionObserver
            lazyImages.forEach(img => {
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
            });
        }
    };
    
    // Debounce function to limit function calls
    const debounce = (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    };
    
    // Throttle function to limit function calls
    const throttle = (func, limit) => {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func(...args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    };
    
    // Optimize scroll events
    const optimizeScroll = () => {
        const scrollHandlers = [];
        
        // Add scroll handler
        window.addScrollHandler = (handler, options = {}) => {
            const { throttleTime = 100, element = window } = options;
            const throttledHandler = throttle(handler, throttleTime);
            scrollHandlers.push({ element, handler: throttledHandler });
            element.addEventListener('scroll', throttledHandler, { passive: true });
            return throttledHandler;
        };
        
        // Remove scroll handler
        window.removeScrollHandler = (handler, element = window) => {
            const index = scrollHandlers.findIndex(h => h.handler === handler && h.element === element);
            if (index !== -1) {
                element.removeEventListener('scroll', handler);
                scrollHandlers.splice(index, 1);
            }
        };
    };
    
    // Optimize resize events
    const optimizeResize = () => {
        const resizeHandlers = [];
        let resizeTimeout;
        
        // Add resize handler
        window.addResizeHandler = (handler, options = {}) => {
            const { debounceTime = 150 } = options;
            const debouncedHandler = debounce(handler, debounceTime);
            resizeHandlers.push(debouncedHandler);
            window.addEventListener('resize', debouncedHandler);
            return debouncedHandler;
        };
        
        // Remove resize handler
        window.removeResizeHandler = (handler) => {
            const index = resizeHandlers.indexOf(handler);
            if (index !== -1) {
                window.removeEventListener('resize', handler);
                resizeHandlers.splice(index, 1);
            }
        };
    };
    
    // Optimize DOM updates
    const optimizeDOMUpdates = () => {
        // Batch DOM updates
        window.batchDOMUpdates = (updates) => {
            return new Promise(resolve => {
                requestAnimationFrame(() => {
                    updates();
                    resolve();
                });
            });
        };
    };
    
    // Initialize optimizations
    lazyLoadImages();
    optimizeScroll();
    optimizeResize();
    optimizeDOMUpdates();
    
    // Observe DOM changes to apply optimizations to new elements
    const observer = new MutationObserver(() => {
        lazyLoadImages();
    });
    
    observer.observe(document.body, { 
        childList: true, 
        subtree: true 
    });
});