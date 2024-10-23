function setTheme(themeName) {
    localStorage.setItem('theme', themeName);
    document.documentElement.className = themeName;
}

function applyTheme() {
    const theme = localStorage.getItem('theme') || 'theme-dark';
    setTheme(theme);
}

document.addEventListener('DOMContentLoaded', (event) => {
    applyTheme();
    
    const themeRadios = document.querySelectorAll('input[name="interface_theme"]');
    if (themeRadios) {
        themeRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                setTheme(`theme-${e.target.value}`);
            });
        });
    }
});
