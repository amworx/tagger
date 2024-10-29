document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');
    const sidebarCollapseBtn = document.getElementById('sidebarCollapseBtn');

    function toggleSidebar() {
        sidebar.classList.toggle('active');
        content.classList.toggle('active');
    }

    if (sidebarCollapseBtn) {
        sidebarCollapseBtn.addEventListener('click', toggleSidebar);
    }

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(event) {
        const isClickInside = sidebar.contains(event.target) || (sidebarCollapseBtn && sidebarCollapseBtn.contains(event.target));
        if (!isClickInside && window.innerWidth <= 992 && sidebar.classList.contains('active')) {
            toggleSidebar();
        }
    });

    // Adjust layout on window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 992) {
            sidebar.classList.remove('active');
            content.classList.remove('active');
        }
    });

    // Load sidebar state from localStorage
    const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (sidebarCollapsed && window.innerWidth > 992) {
        sidebar.classList.add('collapsed');
        content.classList.add('expanded');
    }

    // Save sidebar state to localStorage on toggle
    if (sidebarCollapseBtn) {
        sidebarCollapseBtn.addEventListener('click', function() {
            if (window.innerWidth > 992) {
                const isCollapsed = sidebar.classList.toggle('collapsed');
                content.classList.toggle('expanded');
                localStorage.setItem('sidebarCollapsed', isCollapsed);
            }
        });
    }
});
