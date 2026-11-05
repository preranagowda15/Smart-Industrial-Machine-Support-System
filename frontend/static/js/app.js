/**
 * app.js - Unified client-side authentication & API interaction layer
 * Supports both BIT-PLATE-CV-1.0 and Manufacturing Maintenance Assistant (RAG)
 */

const API_BASE = '/api';

const Auth = {
    getToken() {
        return localStorage.getItem('access_token');
    },
    getRefreshToken() {
        return localStorage.getItem('refresh_token');
    },
    getUser() {
        const u = localStorage.getItem('user_profile');
        try {
            return u ? JSON.parse(u) : null;
        } catch {
            return null;
        }
    },
    setSession(tokens, user) {
        if (tokens.access) localStorage.setItem('access_token', tokens.access);
        if (tokens.refresh) localStorage.setItem('refresh_token', tokens.refresh);
        if (user) localStorage.setItem('user_profile', JSON.stringify(user));
    },
    clearSession() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_profile');
    },
    isAuthenticated() {
        return !!this.getToken();
    },
    logout() {
        const refresh = this.getRefreshToken();
        if (refresh) {
            fetch(`${API_BASE}/auth/logout/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getToken()}`
                },
                body: JSON.stringify({ refresh })
            }).catch(() => {});
        }
        this.clearSession();
        window.location.href = '/login/';
    }
};

/**
 * Enhanced fetch wrapper with automatic JWT authorization, CSRF token handling, and 401 token refresh.
 */
async function apiFetch(endpoint, options = {}) {
    let url = endpoint;
    if (!endpoint.startsWith('http')) {
        if (endpoint.startsWith('/api')) {
            url = endpoint;
        } else if (endpoint.startsWith('/')) {
            url = `${API_BASE}${endpoint}`;
        } else {
            url = `${API_BASE}/${endpoint}`;
        }
    }

    const headers = options.headers ? { ...options.headers } : {};

    // Attach CSRF Token for Django POST/PUT if available in DOM or cookies
    const getCsrfToken = function() {
        const input = document.querySelector('[name=csrfmiddlewaretoken]');
        if (input && input.value) return input.value;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 10) === 'csrftoken=') {
                    return decodeURIComponent(cookie.substring(10));
                }
            }
        }
        return null;
    };
    const csrf = getCsrfToken();
    if (csrf && !headers['X-CSRFToken']) {
        headers['X-CSRFToken'] = csrf;
    }

    // Attach JWT Authorization header
    const token = Auth.getToken();
    if (token && !headers['Authorization']) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    if (!(options.body instanceof FormData) && !headers['Content-Type']) {
        headers['Content-Type'] = 'application/json';
    }

    if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
        options.body = JSON.stringify(options.body);
    }

    options.headers = headers;

    let response = await fetch(url, options);

    // If unauthorized, attempt token refresh once
    if (response.status === 401 && Auth.getRefreshToken() && !url.includes('/login/') && !url.includes('/refresh/')) {
        try {
            const refreshRes = await fetch(`${API_BASE}/auth/refresh/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh: Auth.getRefreshToken() })
            });

            if (refreshRes.ok) {
                const refreshData = await refreshRes.json();
                localStorage.setItem('access_token', refreshData.access);
                headers['Authorization'] = `Bearer ${refreshData.access}`;
                options.headers = headers;
                response = await fetch(url, options);
            } else {
                Auth.clearSession();
                window.location.href = '/login/';
                return response;
            }
        } catch {
            Auth.clearSession();
            window.location.href = '/login/';
            return response;
        }
    }

    return response;
}

/**
 * Global Toast / Notification helper
 */
function showToast(message, type = 'info') {
    const bsType = (type === 'danger' || type === 'error') ? 'danger' : (type === 'success' ? 'success' : (type === 'warning' ? 'warning' : 'info'));
    
    // Check if Bootstrap toast container exists
    const toastContainer = document.getElementById('toast-container');
    if (toastContainer) {
        const toastEl = document.createElement('div');
        toastEl.className = `toast align-items-center text-bg-${bsType} border-0 show mb-2 shadow`;
        toastEl.setAttribute('role', 'alert');
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        toastContainer.appendChild(toastEl);
        setTimeout(() => {
            toastEl.classList.remove('show');
            setTimeout(() => toastEl.remove(), 400);
        }, 4500);
        return;
    }

    // Fallback: Check global alert container
    const alertContainer = document.getElementById('global-alert-container');
    if (alertContainer) {
        const alertEl = document.createElement('div');
        alertEl.className = `alert alert-${bsType} alert-dismissible fade show`;
        alertEl.role = 'alert';
        alertEl.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        alertContainer.appendChild(alertEl);
        setTimeout(() => {
            alertEl.classList.remove('show');
            setTimeout(() => alertEl.remove(), 400);
        }, 4500);
        return;
    }

    // Final fallback
    alert(message);
}

// Unified global App object
const App = {
    Auth,
    apiFetch,
    showToast,
    getCookie(name) {
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    return decodeURIComponent(cookie.substring(name.length + 1));
                }
            }
        }
        return null;
    },
    getAccessToken() {
        return Auth.getToken();
    },
    setTokens(access, refresh) {
        if (access) localStorage.setItem('access_token', access);
        if (refresh) localStorage.setItem('refresh_token', refresh);
    },
    clearTokens() {
        Auth.clearSession();
    }
};

window.App = App;
window.Auth = Auth;
window.apiFetch = apiFetch;

/**
 * Global UI initialization on DOM ready
 */
document.addEventListener('DOMContentLoaded', () => {
    const currentPath = window.location.pathname;
    const user = Auth.getUser();

    // Enforce client authentication on protected pages
    const publicPages = ['/login/', '/register/'];
    if (!publicPages.includes(currentPath) && !Auth.isAuthenticated()) {
        window.location.href = '/login/';
        return;
    }

    // Populate user pill in top navbar
    const userDisplay = document.getElementById('navbar-user-display');
    const roleBadge = document.getElementById('navbar-role-badge');
    if (userDisplay && user) {
        userDisplay.textContent = user.username;
    }
    if (roleBadge && user) {
        roleBadge.textContent = user.role;
        if (user.role === 'ADMIN') {
            roleBadge.className = 'badge bg-danger ms-2';
        } else if (user.role === 'SUPERVISOR') {
            roleBadge.className = 'badge bg-warning text-dark ms-2';
        } else if (user.role === 'ENGINEER') {
            roleBadge.className = 'badge bg-info text-dark ms-2';
        } else {
            roleBadge.className = 'badge bg-primary ms-2';
        }
    }

    // Role-based navigation visibility
    if (user) {
        const supervisorLinks = document.querySelectorAll('.nav-supervisor-only');
        const adminLinks = document.querySelectorAll('.nav-admin-only');
        const engineerLinks = document.querySelectorAll('.nav-engineer-only');
        const inspectionLinks = document.querySelectorAll('.nav-inspection');
        const maintenanceLinks = document.querySelectorAll('.nav-maintenance');

        supervisorLinks.forEach(el => {
            if (user.role === 'OPERATOR' || user.role === 'ENGINEER') {
                el.style.display = 'none';
            }
        });

        adminLinks.forEach(el => {
            if (user.role !== 'ADMIN') {
                el.style.display = 'none';
            }
        });

        engineerLinks.forEach(el => {
            if (user.role !== 'ENGINEER') {
                el.style.display = 'none';
            }
        });

        if (user.role === 'SUPERVISOR') {
            maintenanceLinks.forEach(el => el.style.display = 'none');
        }

        if (user.role === 'ENGINEER') {
            supervisorLinks.forEach(el => el.style.display = 'none');
            adminLinks.forEach(el => el.style.display = 'none');
        }
    }

    // Highlight current sidebar link
    const navLinks = document.querySelectorAll('.sidebar-nav .nav-link');
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });

    // Wire global logout button
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            Auth.logout();
        });
    }
});
