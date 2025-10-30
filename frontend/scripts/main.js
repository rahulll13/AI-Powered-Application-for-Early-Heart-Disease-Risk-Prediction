// frontend/scripts/main.js

// Declare global constants here, and ONLY here, so all other scripts can use them.
const API_URL = 'http://127.0.0.1:5000';
const token = localStorage.getItem('accessToken');

// --- Theme Switching Logic ---

/**
 * Applies a theme by setting a 'data-theme' attribute on the root <html> element.
 * It also sets the state of the toggle switch.
 * @param {string} theme - The theme to apply ('light' or 'dark').
 */
function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    const themeToggle = document.getElementById('theme-checkbox');
    if (themeToggle) {
        themeToggle.checked = theme === 'dark';
    }
}

/**
 * Handles the 'change' event from the theme toggle switch.
 * Saves the user's preference to localStorage.
 * @param {Event} e - The change event from the checkbox.
 */
function switchTheme(e) {
    const theme = e.target.checked ? 'dark' : 'light';
    localStorage.setItem('theme', theme);
    applyTheme(theme);
}

// On initial page load, apply the saved theme from localStorage, or default to 'light'.
const savedTheme = localStorage.getItem('theme') || 'light';
applyTheme(savedTheme);

// --- End of Theme Logic ---


/**
 * Fetches the navbar HTML, injects it into the page, and sets up its event listeners.
 */
async function loadNavbar() {
    // On pages with a navbar, we must be logged in. Redirect if no token is found.
    // This check excludes auth pages which don't have a navbar container.
    if (!token && document.getElementById('navbar-container')) {
        window.location.href = 'index.html';
        return;
    }

    try {
        const response = await fetch('_navbar.html');
        if (!response.ok) return;
        const navbarHtml = await response.text();
        const navbarContainer = document.getElementById('navbar-container');
        
        if (navbarContainer) {
            navbarContainer.innerHTML = navbarHtml;
        }

        // Re-initialize theme logic AFTER the navbar (with the toggle) is loaded into the page.
        const themeToggle = document.getElementById('theme-checkbox');
        applyTheme(localStorage.getItem('theme') || 'light');
        if (themeToggle) {
            themeToggle.addEventListener('change', switchTheme, false);
        }

        // Set up the logout button.
        const logoutButton = document.getElementById('logoutButton');
        if (logoutButton) {
            logoutButton.addEventListener('click', () => {
                localStorage.removeItem('accessToken');
                window.location.href = 'index.html';
            });
        }
    } catch (error) {
        console.error('Failed to load the navbar:', error);
    }
}

// This runs the navbar loading function on any page that has a navbar container.
if (document.getElementById('navbar-container')) {
    document.addEventListener('DOMContentLoaded', loadNavbar);
}

/**
 * A shared helper function to handle common API errors, like an expired session.
 * @param {HTMLElement} errorDiv - The div element where the error message should be displayed.
 * @param {object} data - The JSON data from the server's error response.
 * @param {Response} response - The raw fetch response object.
 */
function handleApiError(errorDiv, data, response) {
    if (response.status === 401 || response.status === 422) {
        errorDiv.innerHTML = `<div class="alert alert-danger mt-4">Your session has expired. Redirecting to login...</div>`;
        setTimeout(() => {
            localStorage.removeItem('accessToken');
            window.location.href = 'index.html';
        }, 3000);
    } else {
        const message = data.message || 'A server error occurred. Please try again later.';
        errorDiv.innerHTML = `<div class="alert alert-danger mt-4">${message}</div>`;
    }
}