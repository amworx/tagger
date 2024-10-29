document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');
    const sidebarCollapseBtn = document.getElementById('sidebarCollapseBtn');

    if (sidebarCollapseBtn) {
        sidebarCollapseBtn.addEventListener('click', function() {
            sidebar.classList.toggle('sidebar-collapsed');
            content.classList.toggle('content-expanded');
        });
    }

    // Close sidebar on mobile when clicking outside
    document.addEventListener('click', function(event) {
        const isClickInsideSidebar = sidebar.contains(event.target);
        const isClickOnCollapseBtn = sidebarCollapseBtn && sidebarCollapseBtn.contains(event.target);

        if (!isClickInsideSidebar && !isClickOnCollapseBtn && window.innerWidth <= 768) {
            sidebar.classList.remove('active');
        }
    });
});
