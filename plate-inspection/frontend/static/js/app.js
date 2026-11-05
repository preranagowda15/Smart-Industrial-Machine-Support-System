/**
 * app.js - Core client-side authentication & API interaction layer
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
 * Enhanced fetch wrapper with automatic JWT authorization and 401 token refresh.
 */
async function apiFetch(endpoint, options = {}) {
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint.startsWith('/') ? endpoint : '/' + endpoint}`;
    const headers = options.headers ? { ...options.headers } : {};

    const token = Auth.getToken();
    if (token && !headers['Authorization']) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    if (!(options.body instanceof FormData) && !headers['Content-Type']) {
        headers['Content-Type'] = 'application/json';
    }

    options.headers = headers;

    let response = await fetch(url, options);

    // If unauthorized, attempt token refresh once
    if (response.status === 401 && Auth.getRefreshToken()) {
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
 * Global UI initialization on DOM ready
 */
document.addEventListener('DOMContentLoaded', () => {
    const currentPath = window.location.pathname;
    const user = Auth.getUser();

    // Enforce authentication on protected pages
    if (currentPath !== '/login/' && !Auth.isAuthenticated()) {
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
        } else {
            roleBadge.className = 'badge bg-primary ms-2';
        }
    }

    // Role-based navigation visibility
    if (user) {
        const supervisorLinks = document.querySelectorAll('.nav-supervisor-only');
        const adminLinks = document.querySelectorAll('.nav-admin-only');

        supervisorLinks.forEach(el => {
            if (user.role === 'OPERATOR') {
                el.style.display = 'none';
            }
        });

        adminLinks.forEach(el => {
            if (user.role !== 'ADMIN') {
                el.style.display = 'none';
            }
        });
    }

    // Highlight current sidebar link
    const navLinks = document.querySelectorAll('.sidebar-nav .nav-link');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
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

