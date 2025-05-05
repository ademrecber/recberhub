// Main scripts.js file for the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Scripts loaded');
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Handle form submissions with AJAX
    document.querySelectorAll('form[data-ajax="true"]').forEach(form => {
        form.addEventListener('submit', handleAjaxForm);
    });
    
    // Initialize any custom components
    initializeCustomComponents();
});

function handleAjaxForm(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const url = form.action;
    const formData = new FormData(form);
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
        },
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.redirect) {
                window.location.href = data.redirect;
            } else if (data.message) {
                showMessage(data.message, 'success');
            }
        } else {
            showMessage(data.message || 'Bir hata oluştu', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('Bir hata oluştu', 'danger');
    });
}

function showMessage(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const container = document.querySelector('.container') || document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
    }, 5000);
}

function initializeCustomComponents() {
    // Add any custom component initialization here
    console.log('Custom components initialized');
}