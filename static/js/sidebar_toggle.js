document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const toggleButton = document.getElementById('sidebar-toggle');

    toggleButton.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');
    });
});
