// frontend/scripts/reset-password.js

const API_URL = 'http://127.0.0.1:5000';

document.addEventListener('DOMContentLoaded', () => {
    const resetPasswordForm = document.getElementById('resetPasswordForm');
    const messageDiv = document.getElementById('messageDiv');
    const passwordInput = document.getElementById('password');
    const togglePasswordButton = document.getElementById('togglePassword');

    // --- Show/Hide Password Logic ---
    if (togglePasswordButton) {
        togglePasswordButton.addEventListener('click', () => {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);

            // Toggle the eye icon
            if (type === 'password') {
                togglePasswordButton.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye" viewBox="0 0 16 16">
                        <path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8zM1.173 8a13.133 13.133 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.133 13.133 0 0 1 14.828 8c-.816 1.097-2.276 2.24-3.645 2.846C9.879 11.832 8.12 12.5 8 12.5s-1.879-.668-3.172-1.654C2.276 10.24 1.173 9.097 1.173 8z"/>
                        <path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0z"/>
                    </svg>`;
            } else {
                togglePasswordButton.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye-slash-fill" viewBox="0 0 16 16">
                        <path d="m10.79 12.912-1.614-1.615a3.5 3.5 0 0 1-4.474-4.474l-2.06-2.06C.938 6.278 0 8 0 8s3 5.5 8 5.5a7.029 7.029 0 0 0 2.79-.588zM5.21 3.088A7.028 7.028 0 0 1 8 2.5c5 0 8 5.5 8 5.5s-.939 1.721-2.641 3.238l-2.062-2.062a3.5 3.5 0 0 0-4.474-4.474L5.21 3.089z"/>
                        <path d="M5.525 7.646a2.5 2.5 0 0 0 2.829 2.829l-2.83-2.829zm4.95.708-2.829-2.83a2.5 2.5 0 0 1 2.829 2.829zm3.171 6-12-12 .708-.708 12 12-.708.708z"/>
                    </svg>`;
            }
        });
    }

    // --- Form Submission Logic ---
    if (resetPasswordForm) {
        resetPasswordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const token = document.getElementById('token').value;
            const password = passwordInput.value;

            messageDiv.textContent = 'Updating...';
            messageDiv.className = 'alert alert-info mt-3';
            messageDiv.classList.remove('d-none');

            try {
                const response = await fetch(`${API_URL}/reset-password`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ token, password })
                });

                const data = await response.json();

                if (response.ok) {
                    messageDiv.textContent = data.message + ' Redirecting to login...';
                    messageDiv.className = 'alert alert-success mt-3';
                    setTimeout(() => {
                        window.location.href = 'login.html';
                    }, 3000);
                } else {
                    messageDiv.textContent = data.message || 'An error occurred.';
                    messageDiv.className = 'alert alert-danger mt-3';
                }

            } catch (error) {
                messageDiv.textContent = 'A network error occurred. Please try again.';
                messageDiv.className = 'alert alert-danger mt-3';
            }
        });
    }
});



