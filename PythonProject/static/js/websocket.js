"use strict";

/*
|--------------------------------------------------------------------------
| WebSocket / Socket.IO Manager
|--------------------------------------------------------------------------
*/

const SocketManager = {
    socket: null,

    state: {
        connected: false,
        workspaceJoined: false,
        reconnectAttempts: 0
    },

    handlers: {},

    init() {
        if (typeof io === "undefined") {
            console.warn(
                "Socket.IO client library is not loaded."
            );
            return;
        }

        this.connect();
    },

    connect() {
        this.socket = io(App.config.socketUrl, {
            transports: ["websocket", "polling"],
            reconnection: true,
            reconnectionAttempts: App.config.reconnectAttempts,
            reconnectionDelay: App.config.reconnectDelay
        });

        this.registerCoreEvents();
        this.registerApplicationEvents();
    },

    registerCoreEvents() {
        this.socket.on("connect", () => {
            this.state.connected = true;
            this.state.reconnectAttempts = 0;

            console.log("Connected to AI Coding Teammate.");

            this.emit("client_ready", {
                timestamp: Date.now()
            });
        });

        this.socket.on("disconnect", (reason) => {
            this.state.connected = false;
            this.state.workspaceJoined = false;

            console.warn("Socket disconnected:", reason);
        });

        this.socket.on("connect_error", (error) => {
            this.state.reconnectAttempts++;

            console.warn(
                "Socket connection error:",
                error.message
            );
        });

        this.socket.on("error", (data) => {
            console.error("Socket error:", data);

            if (window.App) {
                App.showToast(
                    data.message || "WebSocket error.",
                    "danger"
                );
            }
        });
    },

    registerApplicationEvents() {
        this.socket.on("ai_status", (data) => {
            const online = Boolean(data?.online);
            App.setAIStatus(online);
        });

        this.socket.on("chat_response", (data) => {
            if (window.Chat && typeof Chat.handleAIResponse === "function") {
                Chat.handleAIResponse(data);
            }
        });

        this.socket.on("code_analysis_result", (data) => {
            if (
                window.CodeAnalysis &&
                typeof CodeAnalysis.handleAnalysisResult === "function"
            ) {
                CodeAnalysis.handleAnalysisResult(data);
            }
        });

        this.socket.on("code_correction_result", (data) => {
            if (
                window.CodeAnalysis &&
                typeof CodeAnalysis.handleCorrectionResult === "function"
            ) {
                CodeAnalysis.handleCorrectionResult(data);
            }
        });

        this.socket.on("screen_analysis", (data) => {
            if (
                window.Visualizer &&
                typeof Visualizer.handleAnalysis === "function"
            ) {
                Visualizer.handleAnalysis(data);
            }
        });

        this.socket.on("camera_analysis", (data) => {
            if (
                window.Visualizer &&
                typeof Visualizer.handleAnalysis === "function"
            ) {
                Visualizer.handleAnalysis(data);
            }
        });
    },

    emit(event, data = {}) {
        if (!this.socket || !this.state.connected) {
            console.warn(
                `Cannot emit "${event}". Socket is not connected.`
            );
            return false;
        }

        this.socket.emit(event, data);
        return true;
    },

    on(event, callback) {
        if (!this.socket) {
            return;
        }

        this.socket.on(event, callback);
    },

    joinWorkspace(projectId, sessionId = null) {
        const success = this.emit("join_workspace", {
            project_id: projectId,
            session_id: sessionId
        });

        if (success) {
            this.state.workspaceJoined = true;
        }
    },

    leaveWorkspace(projectId) {
        this.emit("leave_workspace", {
            project_id: projectId
        });

        this.state.workspaceJoined = false;
    },

    sendChat(message, context = {}) {
        return this.emit("chat_message", {
            message,
            ...context
        });
    },

    sendCodeAnalysis(data) {
        return this.emit("code_analyze", data);
    },

    sendCodeCorrection(data) {
        return this.emit("code_correct", data);
    },

    sendScreenFrame(data) {
        return this.emit("screen_frame", data);
    },

    sendCameraFrame(data) {
        return this.emit("camera_frame", data);
    }
};

document.addEventListener("DOMContentLoaded", () => {
    SocketManager.init();
});