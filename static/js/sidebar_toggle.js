document.addEventListener('DOMContentLoaded', () => {
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');

    sidebarToggle.addEventListener('click', () => {
        const isCollapsed = sidebar.classList.toggle('collapsed');
        sidebarToggle.setAttribute('aria-expanded', !isCollapsed);
    });
});
