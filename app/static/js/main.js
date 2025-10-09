// backend/app/static/js/main.js

// Global variable to store JWT after retrieval
let globalAccessToken = null;

document.addEventListener('DOMContentLoaded', async function() {
    // --- Global AJAX Fetch Wrapper ---
    // This function will be used for ALL authenticated API calls.
    window.authenticatedFetch = async function(url, options = {}) {
        if (!globalAccessToken) {
            // Attempt to retrieve token if not already stored
            try {
                const tokenResponse = await fetch('/get-jwt-token', { method: 'GET' });
                if (tokenResponse.ok) {
                    const tokenData = await tokenResponse.json();
                    globalAccessToken = tokenData.access_token;
                } else {
                    // If no token, or token invalid, redirect to login
                    console.warn("No valid JWT token available for API call. Redirecting to login.");
                    window.location.href = '/login';
                    throw new Error("No JWT token.");
                }
            } catch (error) {
                console.error("Error retrieving JWT token:", error);
                window.location.href = '/login'; // Critical failure, force login
                throw error;
            }
        }

        // Add Authorization header
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${globalAccessToken}`,
            // Add CSRF token for POST/PUT/DELETE if form-based
        };
        if (options.headers) { // Merge user-provided headers
            Object.assign(headers, options.headers);
        }

        // Include CSRF token if present and it's a non-GET request
        if (['POST', 'PUT', 'DELETE'].includes(options.method) && document.getElementById('csrf_token')) {
            headers['X-CSRFToken'] = document.getElementById('csrf_token').value;
        }

        const fetchOptions = {
            ...options,
            headers: headers,
        };

        const response = await fetch(url, fetchOptions);

        // Handle 401 Unauthorized / 403 Forbidden globally for API calls
        if (response.status === 401 || response.status === 403) {
            const errorData = await response.json();
            console.warn(`Authentication/Authorization error (${response.status}): ${errorData.message}`);
            alert(`Session Expired or Unauthorized: ${errorData.message}. Please log in again.`); // Use browser alert
            window.location.href = '/login'; // Redirect on unauthorized
            throw new Error("Unauthorized access.");
        }

        return response;
    };


    // --- Logout Button Logic (UPDATED to use new endpoint) ---
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', async function(event) {
            event.preventDefault(); 
            
            try {
                // Use authenticatedFetch to hit the backend /api/auth/logout endpoint
                const response = await window.authenticatedFetch('/api/auth/logout', { method: 'POST' });
                
                if (response.ok) {
                    globalAccessToken = null; // Clear token on successful logout
                    localStorage.clear(); // Clear local storage (e.g., cached user_name/email)
                    window.location.href = '/login'; // Redirect to login page
                } else {
                    const errorData = await response.json();
                    console.error('Logout failed:', errorData.message || response.statusText);
                    alert('Logout failed: ' + (errorData.message || 'Unknown error')); 
                }
            } catch (error) {
                console.error('Logout error:', error);
                alert('An error occurred during logout. Please try again.');
            }
        });
    }

    // --- General Flash Message Dismissal (Bootstrap handles most of it) ---
    const flashMessages = document.querySelectorAll('.alert'); 
    flashMessages.forEach(function (msg) {
        if (!msg.classList.contains('alert-dismissible')) {
            setTimeout(() => {
                msg.classList.add('fade');
                setTimeout(() => msg.remove(), 300);
            }, 3000);
        }
    });

    // --- KaTeX auto-render (initial load) ---
    if (typeof renderMathInElement !== 'undefined') {
        renderMathInElement(document.body, {
            delimiters: [
                { left: "$$", right: "$$", display: true },
                { left: "$", right: "$", display: false },
                { left: "\\(", right: "\\)", display: false },
                { left: "\\[", right: "\\]", display: true }
            ],
            throwOnError: false
        });
    }

    // --- CKEditor 5 Initialization (Needs to be reactive for dynamic content/modals) ---
    // If you plan to use CKEditor within dynamic content or modals, you will need to
    // re-call ClassicEditor.create() when those elements are added to the DOM or shown.
    // Ensure window.ClassicEditor is available from the CDN script.
    // Example for dynamically loaded forms or modals:
    $(document).on('shown.bs.modal', function(e) {
        $(e.target).find('textarea.ckeditor-init').each(function() {
            const textarea = this;
            if (!textarea.ckeditorInstance) { // Check if it's already initialized
                ClassicEditor.create(textarea)
                    .then(editor => {
                        textarea.ckeditorInstance = editor; // Store instance
                        // console.log('CKEditor initialized in modal:', textarea.id);
                    })
                    .catch(error => {
                        console.error('Error initializing CKEditor in modal:', error);
                    });
            }
        });
    });

    // You can add a class 'ckeditor-init' to your textareas that need CKEditor
    // e.g., <textarea id="examDescription" name="description" rows="3" class="ckeditor-init"></textarea>
    // Initial page load CKEditor init (for static textareas)
    document.querySelectorAll('textarea.ckeditor-init').forEach(textarea => {
        if (!textarea.ckeditorInstance) {
            ClassicEditor.create(textarea)
                .then(editor => {
                    textarea.ckeditorInstance = editor;
                    // console.log('CKEditor initialized on page load:', textarea.id);
                })
                .catch(error => {
                    console.error('Error initializing CKEditor on page load:', error);
                });
        }
    });

});