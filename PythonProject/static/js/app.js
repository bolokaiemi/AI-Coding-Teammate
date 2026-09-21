"use strict";

/*
|--------------------------------------------------------------------------
| AI Coding Teammate - Main Application
|--------------------------------------------------------------------------
*/

const App = {
    config: {
        apiBase: "/api",
        socketUrl: window.location.origin,
        reconnectAttempts: 10,
        reconnectDelay: 2000
    },

    state: {
        authenticated: false,
        currentUser: null,
        currentProject: null,
        currentSession: null,
        aiOnline: false,
        workspace: false
    },

    init() {
        this.detectPage();
        this.bindGlobalEvents();
        this.loadUserStatus();
        this.loadAIStatus();
    },

    detectPage() {
        this.state.workspace =
            document.body.classList.contains("workspace-page") ||
            Boolean(document.querySelector(".workspace"));
    },

    bindGlobalEvents() {
        document.addEventListener("click", (event) => {
            const toggle = event.target.closest("[data-sidebar-toggle]");

            if (toggle) {
                this.toggleSidebar();
            }

            const closeSidebar = event.target.closest("[data-sidebar-close]");

            if (closeSidebar) {
                this.closeSidebar();
            }
        });

        window.addEventListener("beforeunload", () => {
            if (window.CodeEditor && typeof CodeEditor.saveBeforeUnload === "function") {
                CodeEditor.saveBeforeUnload();
            }
        });
    },

    async loadUserStatus() {
        try {
            const response = await fetch(`${this.config.apiBase}/me`);

            if (!response.ok) {
                return;
            }

            const data = await response.json();

            if (data.success) {
                this.state.authenticated = true;
                this.state.currentUser = data.user || null;
            }
        } catch (error) {
            console.warn("Could not load user status:", error);
        }
    },

    async loadAIStatus() {
        try {
            const response = await fetch(`${this.config.apiBase}/ai/status`);

            if (!response.ok) {
                this.setAIStatus(false);
                return;
            }

            const data = await response.json();

            this.state.aiOnline =
                Boolean(data.success) &&
                Boolean(data.configured);

            this.setAIStatus(this.state.aiOnline);
        } catch (error) {
            console.warn("AI status unavailable:", error);
            this.setAIStatus(false);
        }
    },

    setAIStatus(online, processing = false) {
        const dots = document.querySelectorAll(".ai-status-dot");
        const labels = document.querySelectorAll("[data-ai-status]");

        dots.forEach((dot) => {
            dot.classList.remove("offline", "processing");

            if (processing) {
                dot.classList.add("processing");
            } else if (!online) {
                dot.classList.add("offline");
            }
        });

        labels.forEach((label) => {
            if (processing) {
                label.textContent = "AI processing...";
            } else {
                label.textContent = online ? "AI Online" : "AI Offline";
            }
        });
    },

    toggleSidebar() {
        const sidebar = document.querySelector(".sidebar");
        const overlay = document.querySelector(".sidebar-overlay");

        if (!sidebar) {
            return;
        }

        sidebar.classList.toggle("open");

        if (overlay) {
            overlay.classList.toggle(
                "active",
                sidebar.classList.contains("open")
            );
        }
    },

    closeSidebar() {
        const sidebar = document.querySelector(".sidebar");
        const overlay = document.querySelector(".sidebar-overlay");

        if (sidebar) {
            sidebar.classList.remove("open");
        }

        if (overlay) {
            overlay.classList.remove("active");
        }
    },

    async request(url, options = {}) {
        const defaultOptions = {
            headers: {
                "Content-Type": "application/json"
            }
        };

        const finalOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...(options.headers || {})
            }
        };

        const response = await fetch(url, finalOptions);

        let data = {};

        try {
            data = await response.json();
        } catch {
            data = {};
        }

        if (!response.ok) {
            throw new Error(
                data.message ||
                data.error ||
                `Request failed with status ${response.status}`
            );
        }

        return data;
    },

    showToast(message, type = "info") {
        let container = document.querySelector(".toast-container");

        if (!container) {
            container = document.createElement("div");
            container.className = "toast-container";

            Object.assign(container.style, {
                position: "fixed",
                right: "20px",
                bottom: "20px",
                zIndex: "9999",
                display: "flex",
                flexDirection: "column",
                gap: "10px"
            });

            document.body.appendChild(container);
        }

        const toast = document.createElement("div");
        toast.className = `alert alert-${type}`;
        toast.textContent = message;

        container.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 4000);
    },

    escapeHtml(value) {
        const div = document.createElement("div");
        div.textContent = value ?? "";
        return div.innerHTML;
    }
};

document.addEventListener("DOMContentLoaded", () => {
    App.init();
});