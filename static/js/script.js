const sidebar = document.getElementById('sidebar');
const sidebarToggle = document.getElementById('sidebarToggle');
const userProfileBtn = document.getElementById('userProfileBtn');
const profileDropdown = document.getElementById('profileDropdown');

if (sidebarToggle) {
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
    });
}

if (userProfileBtn) {
    userProfileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        profileDropdown.classList.toggle('show');
    });

    document.addEventListener('click', () => {
        if (profileDropdown.classList.contains('show')) {
            profileDropdown.classList.remove('show');
        }
    });

    profileDropdown.addEventListener('click', (e) => {
        e.stopPropagation();
    });
}

document.querySelectorAll('.theme-option').forEach((option) => {
    option.addEventListener('click', () => {
        document.querySelectorAll('.theme-option').forEach((o) => o.classList.remove('active'));
        option.classList.add('active');
    });
});
