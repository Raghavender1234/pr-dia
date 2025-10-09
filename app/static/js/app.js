// In static/js/app.js

/**
 * A helper function to decode a JWT token to get user information.
 * @param {string} token The JWT token.
 * @returns {object|null} The decoded payload or null if invalid.
 */
function decodeJwt(token) {
    try {
        // atob is a built-in browser function to decode base64
        return JSON.parse(atob(token.split('.')[1]));
    } catch (e) {
        console.error("Failed to decode JWT:", e);
        return null;
    }
}

/**
 * A global wrapper for the fetch API that automatically adds the
 * Authorization header with the JWT token.
 * @param {string} url The URL for the API endpoint.
 * @param {object} options Standard fetch options object.
 * @returns {Promise<Response>} The fetch promise.
 */
async function authenticatedFetch(url, options = {}) {
    const token = localStorage.getItem('access_token');
    const headers = { ...(options.headers || {}) };

    if (token) {
        headers['Authorization'] = 'Bearer ' + token;
    }

    if (options.body && !(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
        if (typeof options.body === 'object') {
            options.body = JSON.stringify(options.body);
        }
    }
    
    const response = await fetch(url, { ...options, headers });

    if (response.status === 401) {
        console.error("Authentication error (401). Logging out.");
        localStorage.removeItem('access_token');
        window.location.href = '/login';
    }
    
    return response;
}
window.authenticatedFetch = authenticatedFetch;


/**
 * Main function that runs on every page load to set up the UI.
 */
document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('access_token');
    const decodedToken = decodeJwt(token);
    const isLoggedIn = !!decodedToken;

    const navGuest = document.getElementById('nav-guest');
    const navUser = document.getElementById('nav-user');
    const userNamePlaceholder = document.getElementById('user-name-placeholder');
    const userDropdownName = document.getElementById('user-dropdown-name');
    const userDropdownEmail = document.getElementById('user-dropdown-email');
    const userDropdownMenu = document.querySelector('#userProfileDropdown + .dropdown-menu');
    const mainNav = document.querySelector('#nav-user > .dropdown'); // The dropdown li itself

    // --- 1. HANDLE AUTHENTICATION STATE ---
    if (isLoggedIn) {
        navGuest.classList.add('d-none');
        navUser.classList.remove('d-none');

        // Populate user info from token
        userNamePlaceholder.textContent = decodedToken.user_name || 'Account';
        userDropdownName.textContent = decodedToken.user_name || 'User';
        userDropdownEmail.textContent = decodedToken.email || 'No email found in token';

        // --- 2. BUILD ROLE-SPECIFIC NAVIGATION ---
        let navLinks = '';
        let dropdownLinks = '';
        
        const userType = decodedToken.user_type;

        // --- STUDENT LINKS ---
        if (userType === 'student') {
            navLinks = `
                <li class="nav-item"><a class="nav-link" href="/student/dashboard">Dashboard</a></li>
                <li class="nav-item"><a class="nav-link" href="/student/my-exams">My Exams</a></li>
                <li class="nav-item"><a class="nav-link" href="/student/mock-tests">Mock Tests</a></li>
            `;
            dropdownLinks = `
                <li><a class="dropdown-item" href="/student/my-organizations"><i class="bi bi-building"></i> My Organizations</a></li>
                <li><a class="dropdown-item" href="/student/my-review-list"><i class="bi bi-bookmark-star-fill"></i> Review List</a></li>
                <li><a class="dropdown-item" href="/student/transactions"><i class="bi bi-receipt"></i> My Transactions</a></li>
            `;
        } 
        // --- ADMIN LINKS ---
        else if (userType === 'main_co_admin' || userType === 'co_admin') {
            navLinks = `
                <li class="nav-item"><a class="nav-link" href="/${userType}/dashboard">Dashboard</a></li>
                <li class="nav-item"><a class="nav-link" href="/admin/exams">Exams & Content</a></li>
                <li class="nav-item"><a class="nav-link" href="/admin/mock-tests">Mock Tests</a></li>
            `;
            if (userType === 'main_co_admin') {
                navLinks += `<li class="nav-item"><a class="nav-link" href="/main-co-admin/users">Manage Users</a></li>`;
                dropdownLinks = `<li><a class="dropdown-item" href="/organization/settings"><i class="bi bi-gear-fill"></i> Org Settings</a></li>`;
            }
        } 
        // --- SUPER ADMIN LINKS ---
        else if (userType === 'super_admin') {
            navLinks = `
                <li class="nav-item"><a class="nav-link" href="/super-admin/dashboard">Dashboard</a></li>
                <li class="nav-item"><a class="nav-link" href="/super-admin/organizations-users">Organizations & Users</a></li>
                <li class="nav-item"><a class="nav-link" href="/super-admin/plans">Plans</a></li>
                <li class="nav-item"><a class="nav-link" href="/super-admin/archive"><i class="bi bi-archive-fill"></i> Archive</a></li>
            `;
        }
        
        // Insert the generated links into the DOM
        mainNav.insertAdjacentHTML('beforebegin', navLinks);
        document.querySelector('#userProfileDropdown + .dropdown-menu .dropdown-divider').insertAdjacentHTML('afterend', dropdownLinks);

        // Logout Button
        document.getElementById('logoutButton').addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('access_token');
            window.location.href = '/login'; // Redirect to login after clearing token
        });

    } else {
        navGuest.classList.remove('d-none');
        navUser.classList.add('d-none');
    }

    // --- 3. HANDLE MULTI-TENANCY (SUBDOMAIN) LOGIC ---
    const hostname = window.location.hostname;
    const parts = hostname.split('.');
    let subdomain = null;

    if ((hostname.includes('localhost') || hostname.includes('127.0.0.1')) && parts.length > 1) {
         if(!isNaN(parts[0])) { /* ignore port numbers like 127.0.0.1 */ }
         else { subdomain = parts[0]; }
    } else if (!hostname.includes('localhost') && parts.length > 2) {
         if (parts[0] !== 'www') subdomain = parts[0];
    }
    
    if (subdomain) {
        try {
            // NOTE: You must create this new public API endpoint. I will provide the code for it next.
            const response = await fetch(`/api/public/organization-details?subdomain=${subdomain}`);
            if (response.ok) {
                const org = await response.json();
                const brandContent = document.getElementById('navbar-brand-content');
                const brandLink = document.getElementById('navbar-brand-link');

                brandLink.href = '/'; 
                
                let brandHTML = '';
                if (org.logo_url) {
                    brandHTML = `<img src="${org.logo_url}" alt="${org.name} Logo" style="height: 36px; border-radius: 6px;">`;
                } else {
                    brandHTML = `<span class="org-avatar-badge">${org.name.substring(0, 2).toUpperCase()}</span>`;
                }
                brandHTML += `<span class="ms-2">${org.name}</span>`;
                brandContent.innerHTML = brandHTML;
            }
        } catch (error) {
            console.error("Failed to fetch organization details:", error);
        }
    }
});