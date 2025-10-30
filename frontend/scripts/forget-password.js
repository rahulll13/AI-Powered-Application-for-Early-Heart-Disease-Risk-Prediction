document.addEventListener('DOMContentLoaded', () => {
    // --- CONFIGURATION ---
    const API_URL = 'http://127.0.0.1:5000'; 

    // --- ELEMENT SELECTION ---
    const forgotPasswordForm = document.getElementById('forgotPasswordForm');
    const messageDiv = document.getElementById('messageDiv');
    const proceedButton = document.getElementById('proceedButton');
    const signInLinkContainer = document.getElementById('signInLinkContainer');
    const submitButton = document.getElementById('submitButton'); // Get the submit button
    
    if (forgotPasswordForm) {
        forgotPasswordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // --- START LOADING INDICATOR ---
            const originalButtonHTML = submitButton.innerHTML;
            submitButton.disabled = true;
            submitButton.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Sending...`;

            // Clear previous messages
            messageDiv.textContent = '';
            messageDiv.className = 'mt-4 text-center font-medium';

            const email = document.getElementById('email').value;

            try {
                const response = await fetch(`${API_URL}/forgot-password`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email })
                });

                const data = await response.json();

                if (response.ok) {
                    // SUCCESS: Hide form, show success message and proceed button
                    messageDiv.textContent = data.message || 'If an account with that email exists, a reset link has been sent.';
                    messageDiv.classList.add('text-green-600');
                    forgotPasswordForm.classList.add('hidden');
                    signInLinkContainer.classList.add('hidden');
                    proceedButton.classList.remove('hidden');
                } else {
                    // FAIL: Show error and restore button
                    messageDiv.textContent = data.message || 'Failed to send reset link.';
                    messageDiv.classList.add('text-red-500');
                    submitButton.disabled = false;
                    submitButton.innerHTML = originalButtonHTML;
                }
            } catch (error) {
                // NETWORK ERROR: Show error and restore button
                console.error('Forgot Password Error:', error);
                messageDiv.textContent = 'Could not connect to the server. Please try again later.';
                messageDiv.classList.add('text-red-500');
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonHTML;
            }
        });
    }
});