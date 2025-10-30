// frontend/scripts/auth.js

const API_URL = 'http://127.0.0.1:5000';

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const errorMessageDiv = document.getElementById('errorMessage');
    const togglePassword = document.getElementById('togglePassword');
    const eyeIcon = document.getElementById('eyeIcon');

    // --- Login Form Handler ---
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            try {
                const response = await fetch(`${API_URL}/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                const data = await response.json();
                if (response.ok) {
                    localStorage.setItem('accessToken', data.access_token);
                    window.location.href = 'prediction.html'; // Redirect to the main prediction page
                } else {
                    errorMessageDiv.textContent = data.message || 'Login failed.';
                    errorMessageDiv.classList.remove('d-none');
                }
            } catch (error) {
                errorMessageDiv.textContent = 'Could not connect to the server. Please try again later.';
                errorMessageDiv.classList.remove('d-none');
            }
        });
    }

    // --- Registration Form Handler ---
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch(`${API_URL}/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, email, password })
                });
                const data = await response.json();
                if (response.ok) {
                     alert('Registration successful! Please log in.');
                    // Change this line to point to the new login page
                    window.location.href = 'login.html'; 
                } else {
                    errorMessageDiv.textContent = data.message || 'Registration failed.';
                    errorMessageDiv.classList.remove('d-none');
                }
            } catch (error) {
                errorMessageDiv.textContent = 'Could not connect to the server. Please try again later.';
                errorMessageDiv.classList.remove('d-none');
            }
        });
    }
    
   document.addEventListener('DOMContentLoaded', () => {
    // --- CONFIGURATION ---
    // IMPORTANT: Replace this with the actual URL of your backend API
    const API_URL = 'http://127.0.0.1:5000'; 

    // --- ELEMENT SELECTION ---
    const loginForm = document.getElementById('loginForm');
    const passwordInput = document.getElementById('password');
    const togglePasswordButton = document.getElementById('togglePassword');
    const eyeIcon = document.getElementById('eyeIcon');
    const errorMessageDiv = document.getElementById('errorMessage');

    // --- LOGIC 1: Password Visibility Toggle ---
    if (togglePasswordButton) {
        togglePasswordButton.addEventListener('click', () => {
            const isPassword = passwordInput.type === 'password';
            passwordInput.type = isPassword ? 'text' : 'password';
            eyeIcon.classList.toggle('fa-eye');
            eyeIcon.classList.toggle('fa-eye-slash');
        });
    }
    // --- LOGIC 2: Form Submission for Registration ---
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            // Prevent the default form submission (which reloads the page)
            e.preventDefault();
            
            // Clear any previous error messages
            errorMessageDiv.textContent = '';

            // --- GATHER FORM DATA ---
            const username = document.getElementById('regUsername').value;
            const email = document.getElementById('regEmail').value;
            const password = passwordInput.value;
            // Get the value of the selected radio button ('patient' or 'doctor')
            const role = document.querySelector('input[name="role"]:checked').value;

            // --- SEND DATA TO SERVER ---
            try {
                const response = await fetch(`${API_URL}/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, email, password, role })
                });

                const data = await response.json();

                if (response.ok) {
                    // SUCCESS: The account was created successfully
                    alert('Registration successful! You will now be redirected to the login page.');
                    window.location.href = 'login.html'; // Redirect to the login page
                } else {
                    // FAIL: The server returned an error (e.g., username taken)
                    errorMessageDiv.textContent = data.message || 'Registration failed. Please try again.';
                }
            } catch (error) {
                // NETWORK ERROR: Could not connect to the server
                console.error('Registration Error:', error);
                errorMessageDiv.textContent = 'Could not connect to the server. Please try again later.';
            }
        });
    }
});
});



