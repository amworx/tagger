function setTheme(themeName) {
    localStorage.setItem('theme', themeName);
    document.documentElement.className = themeName;
}

function applyTheme() {
    const theme = localStorage.getItem('theme') || 'theme-dark';
    setTheme(theme);
}

document.addEventListener('DOMContentLoaded', (event) => {
    const htmlElement = document.documentElement;
    const themeToggle = document.getElementById('theme-toggle');

    if (themeToggle) {
        themeToggle.addEventListener('change', function() {
            if (this.checked) {
                htmlElement.setAttribute('data-theme', 'theme-dark');
                localStorage.setItem('theme', 'theme-dark');
            } else {
                htmlElement.setAttribute('data-theme', 'theme-light');
                localStorage.setItem('theme', 'theme-light');
            }
        });
    }

    // Set initial theme based on localStorage or default to light theme
    const currentTheme = localStorage.getItem('theme') || 'theme-light';
    htmlElement.setAttribute('data-theme', currentTheme);
    if (themeToggle) {
        themeToggle.checked = currentTheme === 'theme-dark';
    }
});
