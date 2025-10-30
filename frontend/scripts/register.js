// File: scripts/register.js

document.addEventListener('DOMContentLoaded', () => {
    // --- CONFIGURATION ---
    const API_URL = 'http://127.0.0.1:5000'; 

    // --- ELEMENT SELECTION (for register page) ---
    const registerForm = document.getElementById('registerForm');
    const passwordInput = document.getElementById('regPassword');
    const togglePasswordButton = document.getElementById('toggleRegPassword');
    const eyeIcon = document.getElementById('regEyeIcon');
    const errorMessageDiv = document.getElementById('errorMessage');

    // --- PASSWORD VISIBILITY TOGGLE (for register page) ---
    if (togglePasswordButton) {
        togglePasswordButton.addEventListener('click', () => {
            const isPassword = passwordInput.type === 'password';
            passwordInput.type = isPassword ? 'text' : 'password';
            eyeIcon.classList.toggle('fa-eye');
            eyeIcon.classList.toggle('fa-eye-slash');
        });
    }

    // --- REGISTRATION FORM SUBMISSION ---
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            errorMessageDiv.textContent = '';

            // Get values from the REGISTER form
            const username = document.getElementById('regUsername').value;
            const email = document.getElementById('regEmail').value;
            const password = document.getElementById('regPassword').value;
            const role = document.querySelector('input[name="role"]:checked').value;

            try {
                const response = await fetch(`${API_URL}/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, email, password, role })
                });

                const data = await response.json();

                if (response.ok) {
                    alert('Registration successful! Please log in.');
                    window.location.href = 'login.html';
                } else {
                    errorMessageDiv.textContent = data.message || 'Registration failed.';
                }
            } catch (error) {
                console.error("Registration Error:", error);
                errorMessageDiv.textContent = 'Could not connect to the server.';
            }
        });
    }
});