// JavaScript for basic form validation and UI enhancements

document.addEventListener('DOMContentLoaded', () => {
    // Login form validation
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            const username = loginForm.username.value.trim();
            const password = loginForm.password.value.trim();
            if (!username || !password) {
                e.preventDefault();
                alert('Please enter both username and password.');
            }
        });
    }

    // Register form validation
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            const username = registerForm.username.value.trim();
            const email = registerForm.email.value.trim();
            const password = registerForm.password.value.trim();
            const confirmPassword = registerForm.confirm_password.value.trim();

            if (!username || !email || !password || !confirmPassword) {
                e.preventDefault();
                alert('Please fill in all fields.');
                return;
            }

            if (password !== confirmPassword) {
                e.preventDefault();
                alert('Passwords do not match.');
                return;
            }

            // Basic email format check
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailPattern.test(email)) {
                e.preventDefault();
                alert('Please enter a valid email address.');
                return;
            }
        });
    }
});
