// Core App Utilities & API Client
const App = {
  getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  },

  getAccessToken() {
    return localStorage.getItem("access_token");
  },

  setTokens(access, refresh) {
    if (access) localStorage.setItem("access_token", access);
    if (refresh) localStorage.setItem("refresh_token", refresh);
  },

  clearTokens() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  },

  async apiFetch(url, options = {}) {
    options.headers = options.headers || {};
    
    // Add CSRF Token
    const csrf = this.getCookie("csrftoken");
    if (csrf) {
      options.headers["X-CSRFToken"] = csrf;
    }

    // Add JWT Token if available
    const token = this.getAccessToken();
    if (token) {
      options.headers["Authorization"] = `Bearer ${token}`;
    }

    // If body is plain object and not FormData, stringify
    if (options.body && typeof options.body === "object" && !(options.body instanceof FormData)) {
      options.headers["Content-Type"] = "application/json";
      options.body = JSON.stringify(options.body);
    }

    try {
      const response = await fetch(url, options);
      if (response.status === 401 && !url.includes("/login/")) {
        console.warn("Session expired or unauthorized. Redirecting to login.");
        window.location.href = "/login/";
        return null;
      }
      return response;
    } catch (err) {
      console.error("API Fetch Error:", err);
      this.showToast("Network request failed: " + err.message, "danger");
      throw err;
    }
  },

  showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toastEl = document.createElement("div");
    toastEl.className = `toast align-items-center text-bg-${type} border-0 show mb-2`;
    toastEl.setAttribute("role", "alert");
    toastEl.innerHTML = `
      <div class="d-flex">
        <div class="toast-body">${message}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    `;
    container.appendChild(toastEl);
    setTimeout(() => {
      toastEl.classList.remove("show");
      toastEl.remove();
    }, 4500);
  }
};
