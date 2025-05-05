// Theme toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check for saved theme preference or use system preference
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
        document.documentElement.classList.add('dark-theme');
        if (document.querySelector('#theme-toggle')) {
            document.querySelector('#theme-toggle').checked = true;
        }
    }
    
    // Add event listener to theme toggle if it exists
    const themeToggle = document.querySelector('#theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('change', function() {
            if (this.checked) {
                document.documentElement.classList.add('dark-theme');
                localStorage.setItem('theme', 'dark');
            } else {
                document.documentElement.classList.remove('dark-theme');
                localStorage.setItem('theme', 'light');
            }
        });
    }
});