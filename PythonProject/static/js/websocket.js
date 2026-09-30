"use strict";

/*
|--------------------------------------------------------------------------
| AI Coding Teammate - Workspace Socket Manager
|--------------------------------------------------------------------------
|
| Handles real-time communication between the coding workspace
| and the Flask-SocketIO backend.
|
| Responsibilities:
|
| - Connect to Socket.IO
| - Track connection state
| - Join and leave project workspaces
| - Enable Chat when Socket.IO is ready
| - Receive AI chat responses
| - Receive code analysis results
| - Receive code correction results
| - Receive screen analysis
| - Receive camera analysis
| - Update connection indicators
|
*/


const SocketManager = {

    socket: null,

    state: {
        connected: false,
        workspaceJoined: false,
        reconnectAttempts: 0,
        projectId: null,
        sessionId: null
    },


    /*
    |--------------------------------------------------------------------------
    | Initialize
    |--------------------------------------------------------------------------
    */

    init() {

        if (typeof io === "undefined") {

            console.warn(
                "Socket.IO client library is not loaded."
            );

            this.updateConnectionUI(
                "offline",
                "Socket.IO unavailable"
            );

            return;
        }


        /*
         * Prevent duplicate connections if init()
         * accidentally runs more than once.
         */

        if (this.socket) {

            console.warn(
                "SocketManager has already been initialized."
            );

            return;
        }


        this.state.projectId =
            this.getProjectId();


        this.state.sessionId =
            this.getSessionId();


        this.connect();
    },


    /*
    |--------------------------------------------------------------------------
    | Get Project ID
    |--------------------------------------------------------------------------
    */

    getProjectId() {

        /*
         * Prefer Project.getProjectId() when project.js
         * has already been loaded.
         */

        if (
            window.Project &&
            typeof window.Project.getProjectId === "function"
        ) {

            const projectId =
                window.Project.getProjectId();


            if (projectId) {
                return projectId;
            }
        }


        /*
         * Workspace fallback:
         *
         * <div
         *     class="workspace-page"
         *     data-project-id="1"
         * >
         */

        const workspace =
            document.querySelector(
                "[data-project-id]"
            );


        if (
            workspace &&
            workspace.dataset.projectId
        ) {

            return workspace.dataset.projectId;
        }


        /*
         * URL fallback:
         *
         * /workspace/?project_id=1
         */

        const params =
            new URLSearchParams(
                window.location.search
            );


        return params.get(
            "project_id"
        );
    },


    /*
    |--------------------------------------------------------------------------
    | Get Session ID
    |--------------------------------------------------------------------------
    */

    getSessionId() {

        const workspace =
            document.querySelector(
                "[data-session-id]"
            );


        if (
            workspace &&
            workspace.dataset.sessionId
        ) {

            return workspace.dataset.sessionId;
        }


        return null;
    },


    /*
    |--------------------------------------------------------------------------
    | Connect
    |--------------------------------------------------------------------------
    */

    connect() {

        /*
         * App.config is preferred when available.
         *
         * If socketUrl is empty, Socket.IO connects
         * to the current Flask server automatically.
         */

        const socketUrl =
            window.App?.config?.socketUrl ||
            undefined;


        const reconnectAttempts =
            window.App?.config?.reconnectAttempts ??
            10;


        const reconnectDelay =
            window.App?.config?.reconnectDelay ??
            1000;


        this.updateConnectionUI(
            "connecting",
            "Connecting..."
        );


        this.socket = io(
            socketUrl,
            {
                transports: [
                    "websocket",
                    "polling"
                ],

                reconnection: true,

                reconnectionAttempts:
                    reconnectAttempts,

                reconnectionDelay:
                    reconnectDelay
            }
        );


        this.registerCoreEvents();

        this.registerApplicationEvents();
    },


    /*
    |--------------------------------------------------------------------------
    | Register Core Socket Events
    |--------------------------------------------------------------------------
    */

    registerCoreEvents() {

        if (!this.socket) {
            return;
        }


        /*
         * CONNECT
         */

        this.socket.on(
            "connect",
            () => {

                this.state.connected = true;

                this.state.reconnectAttempts = 0;


                console.log(
                    "Connected to AI Coding Teammate."
                );


                this.updateConnectionUI(
                    "online",
                    "Connected"
                );


                this.updateAIStatus(
                    true
                );


                /*
                 * IMPORTANT:
                 *
                 * Chat.onReady() belongs here.
                 *
                 * The chat becomes usable only after
                 * Socket.IO is connected.
                 */

                if (
                    window.Chat &&
                    typeof window.Chat.onReady ===
                        "function"
                ) {

                    window.Chat.onReady();
                }


                /*
                 * Notify server that the browser client
                 * is ready.
                 */

                this.emit(
                    "client_ready",
                    {
                        timestamp:
                            Date.now()
                    }
                );


                /*
                 * Automatically join the current project
                 * workspace after connection.
                 */

                if (
                    this.state.projectId
                ) {

                    this.joinWorkspace(
                        this.state.projectId,
                        this.state.sessionId
                    );
                }
            }
        );


        /*
         * DISCONNECT
         */

        this.socket.on(
            "disconnect",
            reason => {

                this.state.connected = false;

                this.state.workspaceJoined = false;


                console.warn(
                    "Socket disconnected:",
                    reason
                );


                this.updateConnectionUI(
                    "offline",
                    "Disconnected"
                );


                this.updateAIStatus(
                    false
                );


                /*
                 * Allow Chat to disable itself while
                 * connection is unavailable.
                 */

                if (
                    window.Chat &&
                    typeof window.Chat.onDisconnect ===
                        "function"
                ) {

                    window.Chat.onDisconnect(
                        reason
                    );
                }
            }
        );


        /*
         * CONNECTION ERROR
         */

        this.socket.on(
            "connect_error",
            error => {

                this.state.connected = false;

                this.state.reconnectAttempts += 1;


                console.warn(
                    "Socket connection error:",
                    error?.message ||
                    error
                );


                this.updateConnectionUI(
                    "offline",
                    "Connection error"
                );


                this.updateAIStatus(
                    false
                );
            }
        );


        /*
         * GENERIC SERVER ERROR
         */

        this.socket.on(
            "error",
            data => {

                console.error(
                    "Socket error:",
                    data
                );


                const message =
                    data?.message ||
                    "WebSocket error.";


                if (
                    window.App &&
                    typeof window.App.showToast ===
                        "function"
                ) {

                    window.App.showToast(
                        message,
                        "danger"
                    );
                }
            }
        );
    },


    /*
    |--------------------------------------------------------------------------
    | Register Application Events
    |--------------------------------------------------------------------------
    */

    registerApplicationEvents() {

        if (!this.socket) {
            return;
        }


        /*
         * AI STATUS
         */

        this.socket.on(
            "ai_status",
            data => {

                const online =
                    Boolean(
                        data?.online
                    );


                this.updateAIStatus(
                    online
                );
            }
        );


        /*
         * WORKSPACE JOINED
         */

        this.socket.on(
            "workspace_joined",
            data => {

                this.state.workspaceJoined =
                    true;


                console.log(
                    "Joined AI workspace:",
                    data
                );
            }
        );


        /*
         * WORKSPACE LEFT
         */

        this.socket.on(
            "workspace_left",
            data => {

                this.state.workspaceJoined =
                    false;


                console.log(
                    "Left AI workspace:",
                    data
                );
            }
        );


        /*
         * CHAT RESPONSE
         */

        this.socket.on(
            "chat_response",
            data => {

                if (
                    window.Chat &&
                    typeof window.Chat
                        .handleAIResponse ===
                        "function"
                ) {

                    window.Chat.handleAIResponse(
                        data
                    );
                }
            }
        );


        /*
         * AI TYPING
         */

        this.socket.on(
            "ai_typing",
            data => {

                if (
                    window.Chat &&
                    typeof window.Chat
                        .handleTyping ===
                        "function"
                ) {

                    window.Chat.handleTyping(
                        data
                    );
                }
            }
        );


        /*
         * CODE ANALYSIS RESULT
         */

        this.socket.on(
            "code_analysis_result",
            data => {

                if (
                    window.CodeAnalysis &&
                    typeof window.CodeAnalysis
                        .handleAnalysisResult ===
                        "function"
                ) {

                    window.CodeAnalysis
                        .handleAnalysisResult(
                            data
                        );
                }
            }
        );


        /*
         * CODE CORRECTION RESULT
         */

        this.socket.on(
            "code_correction_result",
            data => {

                if (
                    window.CodeAnalysis &&
                    typeof window.CodeAnalysis
                        .handleCorrectionResult ===
                        "function"
                ) {

                    window.CodeAnalysis
                        .handleCorrectionResult(
                            data
                        );
                }
            }
        );


        /*
         * SCREEN ANALYSIS
         */

        this.socket.on(
            "screen_analysis",
            data => {

                if (
                    window.Visualizer &&
                    typeof window.Visualizer
                        .handleAnalysis ===
                        "function"
                ) {

                    window.Visualizer
                        .handleAnalysis(
                            data
                        );
                }
            }
        );


        /*
         * CAMERA ANALYSIS
         */

        this.socket.on(
            "camera_analysis",
            data => {

                if (
                    window.Visualizer &&
                    typeof window.Visualizer
                        .handleAnalysis ===
                        "function"
                ) {

                    window.Visualizer
                        .handleAnalysis(
                            data
                        );
                }
            }
        );


        /*
         * VISUAL ANALYSIS
         */

        this.socket.on(
            "visual_analysis",
            data => {

                if (
                    window.Visualizer &&
                    typeof window.Visualizer
                        .handleAnalysis ===
                        "function"
                ) {

                    window.Visualizer
                        .handleAnalysis(
                            data
                        );
                }
            }
        );
    },


    /*
    |--------------------------------------------------------------------------
    | Update Connection UI
    |--------------------------------------------------------------------------
    */

    updateConnectionUI(
        state,
        text
    ) {

        const indicator =
            document.getElementById(
                "connectionIndicator"
            );


        const status =
            document.getElementById(
                "connectionStatus"
            );


        if (indicator) {

            indicator.classList.remove(
                "online",
                "offline",
                "connecting"
            );


            indicator.classList.add(
                state
            );
        }


        if (status) {

            status.textContent =
                text;
        }
    },


    /*
    |--------------------------------------------------------------------------
    | Update AI Status
    |--------------------------------------------------------------------------
    */

    updateAIStatus(online) {

        /*
         * Use App helper if available.
         */

        if (
            window.App &&
            typeof window.App.setAIStatus ===
                "function"
        ) {

            window.App.setAIStatus(
                online
            );

            return;
        }


        /*
         * Workspace fallback.
         */

        const indicator =
            document.getElementById(
                "aiStatusIndicator"
            );


        const text =
            document.getElementById(
                "aiStatusText"
            );


        if (indicator) {

            indicator.classList.toggle(
                "online",
                online
            );


            indicator.classList.toggle(
                "offline",
                !online
            );
        }


        if (text) {

            text.textContent =
                online
                    ? "AI Teammate Online"
                    : "AI Teammate Offline";
        }
    },


    /*
    |--------------------------------------------------------------------------
    | Emit Socket Event
    |--------------------------------------------------------------------------
    */

    emit(
        event,
        data = {}
    ) {

        if (
            !this.socket ||
            !this.state.connected
        ) {

            console.warn(
                `Cannot emit "${event}". Socket is not connected.`
            );

            return false;
        }


        this.socket.emit(
            event,
            data
        );


        return true;
    },


    /*
    |--------------------------------------------------------------------------
    | Listen for Custom Socket Event
    |--------------------------------------------------------------------------
    */

    on(
        event,
        callback
    ) {

        if (
            !this.socket ||
            typeof callback !== "function"
        ) {

            return false;
        }


        this.socket.on(
            event,
            callback
        );


        return true;
    },


    /*
    |--------------------------------------------------------------------------
    | Remove Custom Socket Event
    |--------------------------------------------------------------------------
    */

    off(
        event,
        callback
    ) {

        if (!this.socket) {
            return false;
        }


        if (callback) {

            this.socket.off(
                event,
                callback
            );

        } else {

            this.socket.off(
                event
            );
        }


        return true;
    },


    /*
    |--------------------------------------------------------------------------
    | Join Workspace
    |--------------------------------------------------------------------------
    */

    joinWorkspace(
        projectId,
        sessionId = null
    ) {

        if (!projectId) {

            console.warn(
                "Cannot join workspace without a project ID."
            );

            return false;
        }


        this.state.projectId =
            projectId;


        this.state.sessionId =
            sessionId;


        const success =
            this.emit(
                "join_workspace",
                {
                    project_id:
                        projectId,

                    session_id:
                        sessionId
                }
            );


        /*
         * This means the join request was emitted.
         *
         * If your backend sends "workspace_joined",
         * that event will confirm the actual join.
         */

        if (success) {

            console.log(
                `Joining workspace for project ${projectId}.`
            );
        }


        return success;
    },


    /*
    |--------------------------------------------------------------------------
    | Leave Workspace
    |--------------------------------------------------------------------------
    */

    leaveWorkspace(
        projectId = null
    ) {

        const targetProjectId =
            projectId ||
            this.state.projectId;


        if (!targetProjectId) {
            return false;
        }


        const success =
            this.emit(
                "leave_workspace",
                {
                    project_id:
                        targetProjectId
                }
            );


        if (success) {

            this.state.workspaceJoined =
                false;
        }


        return success;
    },


    /*
    |--------------------------------------------------------------------------
    | Send Chat Message
    |--------------------------------------------------------------------------
    */

    sendChat(
        message,
        context = {}
    ) {

        const cleanMessage =
            String(
                message || ""
            ).trim();


        if (!cleanMessage) {
            return false;
        }


        return this.emit(
            "chat_message",
            {
                message:
                    cleanMessage,

                project_id:
                    this.state.projectId,

                session_id:
                    this.state.sessionId,

                ...context
            }
        );
    },


    /*
    |--------------------------------------------------------------------------
    | Send Code Analysis
    |--------------------------------------------------------------------------
    */

    sendCodeAnalysis(
        data = {}
    ) {

        return this.emit(
            "code_analyze",
            {
                project_id:
                    this.state.projectId,

                session_id:
                    this.state.sessionId,

                ...data
            }
        );
    },


    /*
    |--------------------------------------------------------------------------
    | Send Code Correction
    |--------------------------------------------------------------------------
    */

    sendCodeCorrection(
        data = {}
    ) {

        return this.emit(
            "code_correct",
            {
                project_id:
                    this.state.projectId,

                session_id:
                    this.state.sessionId,

                ...data
            }
        );
    },


    /*
    |--------------------------------------------------------------------------
    | Send Screen Frame
    |--------------------------------------------------------------------------
    */

    sendScreenFrame(
        data = {}
    ) {

        return this.emit(
            "screen_frame",
            {
                project_id:
                    this.state.projectId,

                session_id:
                    this.state.sessionId,

                ...data
            }
        );
    },


    /*
    |--------------------------------------------------------------------------
    | Send Camera Frame
    |--------------------------------------------------------------------------
    */

    sendCameraFrame(
        data = {}
    ) {

        return this.emit(
            "camera_frame",
            {
                project_id:
                    this.state.projectId,

                session_id:
                    this.state.sessionId,

                ...data
            }
        );
    },


    /*
    |--------------------------------------------------------------------------
    | Disconnect
    |--------------------------------------------------------------------------
    */

    disconnect() {

        if (!this.socket) {
            return;
        }


        if (
            this.state.connected &&
            this.state.projectId
        ) {

            this.leaveWorkspace(
                this.state.projectId
            );
        }


        this.socket.disconnect();


        this.socket = null;

        this.state.connected =
            false;

        this.state.workspaceJoined =
            false;


        this.updateConnectionUI(
            "offline",
            "Disconnected"
        );
    }
};


/*
|--------------------------------------------------------------------------
| DOM Ready
|--------------------------------------------------------------------------
*/

document.addEventListener(
    "DOMContentLoaded",
    () => {

        SocketManager.init();
    }
);


/*
|--------------------------------------------------------------------------
| Leave Workspace Before Page Exit
|--------------------------------------------------------------------------
*/

window.addEventListener(
    "beforeunload",
    () => {

        if (
            SocketManager.state.connected &&
            SocketManager.state.projectId
        ) {

            SocketManager.leaveWorkspace(
                SocketManager.state.projectId
            );
        }
    }
);


/*
|--------------------------------------------------------------------------
| Global Access
|--------------------------------------------------------------------------
*/

window.SocketManager =
    SocketManager;