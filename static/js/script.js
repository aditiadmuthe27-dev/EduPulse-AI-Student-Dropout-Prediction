// DOM Elements
const sidebar = document.getElementById('sidebar');
const sidebarToggle = document.getElementById('sidebarToggle');
const userProfileBtn = document.getElementById('userProfileBtn');
const profileDropdown = document.getElementById('profileDropdown');

// Toggle Sidebar
sidebarToggle.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
});

// Toggle Profile Dropdown
userProfileBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    profileDropdown.classList.toggle('show');
});

// Close dropdown when clicking outside
document.addEventListener('click', () => {
    if (profileDropdown.classList.contains('show')) {
        profileDropdown.classList.remove('show');
    }
});

// Prevent dropdown from closing when clicking inside it
profileDropdown.addEventListener('click', (e) => {
    e.stopPropagation();
});
