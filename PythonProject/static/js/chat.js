"use strict";

/*
|--------------------------------------------------------------------------
| AI Coding Teammate - Chat Manager
|--------------------------------------------------------------------------
|
| Handles:
|
| - Chat initialization
| - Chat ready / disconnected states
| - User messages
| - AI responses
| - Keyboard submission
| - Project/session context
| - Code context
| - Connection overlay
| - Sending state
|
*/


const Chat = {

    /*
    |--------------------------------------------------------------------------
    | Elements
    |--------------------------------------------------------------------------
    */

    elements: {
        messages: null,
        input: null,
        send: null,
        overlay: null
    },


    /*
    |--------------------------------------------------------------------------
    | State
    |--------------------------------------------------------------------------
    */

    state: {
        ready: false,
        sending: false,
        initialized: false
    },


    /*
    |--------------------------------------------------------------------------
    | Initialize
    |--------------------------------------------------------------------------
    */

    init() {

        /*
         * Prevent duplicate initialization.
         */

        if (this.state.initialized) {
            return;
        }


        /*
         * Support both IDs and data attributes.
         */

        this.elements.messages =
            document.querySelector(
                "[data-chat-messages]"
            ) ||
            document.getElementById(
                "chat-messages"
            ) ||
            document.querySelector(
                ".chat-messages"
            );


        this.elements.input =
            document.querySelector(
                "[data-chat-input]"
            ) ||
            document.getElementById(
                "chat-input"
            ) ||
            document.querySelector(
                ".chat-input"
            );


        this.elements.send =
            document.querySelector(
                "[data-chat-send]"
            ) ||
            document.getElementById(
                "chat-send"
            ) ||
            document.querySelector(
                ".chat-send"
            );


        this.elements.overlay =
            document.querySelector(
                "[data-connecting-overlay]"
            );


        /*
         * Chat may not exist on every page.
         */

        if (!this.elements.input) {

            console.debug(
                "Chat input not found on this page."
            );

            return;
        }


        this.state.initialized = true;


        /*
         * Start disabled until Socket.IO is ready.
         */

        this.setEnabled(
            false
        );


        this.showConnectingOverlay();


        this.bindEvents();


        /*
         * Socket.IO may already have connected before
         * Chat.init() finished.
         */

        if (
            window.SocketManager &&
            window.SocketManager.state &&
            window.SocketManager.state.connected
        ) {

            this.onReady();
        }
    },


    /*
    |--------------------------------------------------------------------------
    | Bind Events
    |--------------------------------------------------------------------------
    */

    bindEvents() {

        /*
         * Send button.
         */

        if (this.elements.send) {

            this.elements.send.addEventListener(
                "click",
                () => {

                    this.send();
                }
            );
        }


        /*
         * Enter sends the message.
         *
         * Shift + Enter creates a new line.
         */

        this.elements.input.addEventListener(
            "keydown",
            event => {

                if (
                    event.key === "Enter" &&
                    !event.shiftKey
                ) {

                    event.preventDefault();

                    this.send();
                }
            }
        );
    },


    /*
    |--------------------------------------------------------------------------
    | Chat Ready
    |--------------------------------------------------------------------------
    |
    | Called by SocketManager after Socket.IO connects.
    |
    */

    onReady() {

        this.state.ready = true;


        this.hideConnectingOverlay();


        this.setEnabled(
            true
        );


        if (this.elements.input) {

            this.elements.input.focus();
        }


        console.log(
            "AI Coding Teammate chat is ready."
        );
    },


    /*
    |--------------------------------------------------------------------------
    | Chat Disconnected
    |--------------------------------------------------------------------------
    |
    | Called by SocketManager when the Socket.IO connection
    | is lost.
    |
    */

    onDisconnect(reason = null) {

        this.state.ready = false;

        this.state.sending = false;


        this.setEnabled(
            false
        );


        this.showConnectingOverlay(
            "Reconnecting..."
        );


        if (reason) {

            console.warn(
                "AI chat disconnected:",
                reason
            );
        }
    },


    /*
    |--------------------------------------------------------------------------
    | Enable / Disable Chat
    |--------------------------------------------------------------------------
    */

    setEnabled(enabled) {

        if (this.elements.input) {

            this.elements.input.disabled =
                !enabled;
        }


        if (this.elements.send) {

            this.elements.send.disabled =
                !enabled;
        }
    },


    /*
    |--------------------------------------------------------------------------
    | Show Connecting Overlay
    |--------------------------------------------------------------------------
    */

    showConnectingOverlay(
        message = "Connecting to AI Teammate..."
    ) {

        const overlay =
            this.elements.overlay ||
            document.querySelector(
                "[data-connecting-overlay]"
            );


        if (!overlay) {
            return;
        }


        overlay.hidden = false;


        /*
         * Optional text element:
         *
         * data-connecting-text
         */

        const text =
            overlay.querySelector(
                "[data-connecting-text]"
            );


        if (text) {

            text.textContent =
                message;
        }
    },


    /*
    |--------------------------------------------------------------------------
    | Hide Connecting Overlay
    |--------------------------------------------------------------------------
    */

    hideConnectingOverlay() {

        const overlay =
            this.elements.overlay ||
            document.querySelector(
                "[data-connecting-overlay]"
            );


        if (overlay) {

            overlay.hidden = true;
        }
    },


    /*
    |--------------------------------------------------------------------------
    | Send Message
    |--------------------------------------------------------------------------
    */

    async send() {

        if (!this.elements.input) {
            return;
        }


        const message =
            this.elements.input.value.trim();


        if (!message) {
            return;
        }


        if (this.state.sending) {
            return;
        }


        /*
         * Do not send while disconnected.
         */

        if (!this.state.ready) {

            this.showMessage(
                "AI Teammate is still connecting.",
                "warning"
            );

            return;
        }


        this.state.sending = true;


        /*
         * Display user's message immediately.
         */

        this.addMessage(
            "user",
            message
        );


        /*
         * Clear input.
         */

        this.elements.input.value =
            "";


        /*
         * Temporarily disable send button.
         */

        if (this.elements.send) {

            this.elements.send.disabled =
                true;
        }


        try {

            const payload = {

                message:
                    message,

                project_id:
                    this.getProjectId(),

                session_id:
                    this.getSessionId(),

                /*
                 * api_routes.py currently expects "code".
                 */

                code:
                    this.getCodeContext()
            };


            /*
             * -------------------------------------------------
             * HTTP CHAT REQUEST
             * -------------------------------------------------
             *
             * We currently use /api/ai/chat because that route
             * already exists in api_routes.py.
             *
             * Socket.IO still manages the real-time workspace
             * connection and can later become the primary
             * streaming chat transport.
             */

            const data =
                await this.request(
                    "/api/ai/chat",
                    {
                        method: "POST",

                        body:
                            JSON.stringify(
                                payload
                            )
                    }
                );


            this.handleAIResponse(
                data
            );


        } catch (error) {

            console.error(
                "Chat request failed:",
                error
            );


            this.addMessage(
                "ai",
                (
                    "Sorry, I could not process " +
                    `that request: ${error.message}`
                )
            );


        } finally {

            this.state.sending =
                false;


            /*
             * Only re-enable when the socket is
             * still connected.
             */

            if (
                this.elements.send &&
                this.state.ready
            ) {

                this.elements.send.disabled =
                    false;
            }


            if (
                this.elements.input &&
                this.state.ready
            ) {

                this.elements.input.focus();
            }
        }
    },


    /*
    |--------------------------------------------------------------------------
    | Request Helper
    |--------------------------------------------------------------------------
    */

    async request(
        url,
        options = {}
    ) {

        /*
         * Prefer App.request().
         */

        if (
            window.App &&
            typeof window.App.request ===
                "function"
        ) {

            return window.App.request(
                url,
                options
            );
        }


        /*
         * Fallback if App.request is unavailable.
         */

        const requestOptions = {
            credentials:
                "same-origin",

            ...options,

            headers: {
                "Content-Type":
                    "application/json",

                ...(options.headers || {})
            }
        };


        const response =
            await fetch(
                url,
                requestOptions
            );


        let data;


        try {

            data =
                await response.json();


        } catch (error) {

            throw new Error(
                "The server returned an invalid response."
            );
        }


        if (!response.ok) {

            throw new Error(
                data.error ||
                data.message ||
                `Request failed (${response.status}).`
            );
        }


        if (
            data &&
            data.success === false
        ) {

            throw new Error(
                data.error ||
                data.message ||
                "Chat request failed."
            );
        }


        return data;
    },


    /*
    |--------------------------------------------------------------------------
    | Handle AI Response
    |--------------------------------------------------------------------------
    */

    handleAIResponse(data) {

        if (!data) {
            return;
        }


        const message =
            data.message ||
            data.response ||
            data.content ||
            data.error;


        if (!message) {

            console.warn(
                "AI response did not contain a message.",
                data
            );

            return;
        }


        this.addMessage(
            "ai",
            message
        );
    },


    /*
    |--------------------------------------------------------------------------
    | AI Typing State
    |--------------------------------------------------------------------------
    |
    | SocketManager can call this when the backend emits:
    |
    | ai_typing
    |
    */

    handleTyping(data) {

        const typing =
            Boolean(
                data?.typing
            );


        const indicator =
            document.querySelector(
                "[data-chat-typing]"
            );


        if (!indicator) {
            return;
        }


        indicator.hidden =
            !typing;
    },


    /*
    |--------------------------------------------------------------------------
    | Add Message
    |--------------------------------------------------------------------------
    */

    addMessage(
        role,
        message
    ) {

        if (!this.elements.messages) {

            console.warn(
                "Chat message container was not found."
            );

            return;
        }


        const wrapper =
            document.createElement(
                "div"
            );


        wrapper.className =
            `chat-message ${role}`;


        /*
         * Do not place raw AI/user content into innerHTML.
         *
         * textContent prevents injected HTML or JavaScript
         * from being executed.
         */

        const bubble =
            document.createElement(
                "div"
            );


        bubble.className =
            "chat-bubble";


        bubble.textContent =
            String(
                message
            );


        wrapper.appendChild(
            bubble
        );


        this.elements.messages.appendChild(
            wrapper
        );


        this.elements.messages.scrollTop =
            this.elements.messages.scrollHeight;
    },


    /*
    |--------------------------------------------------------------------------
    | Get Code Context
    |--------------------------------------------------------------------------
    */

    getCodeContext() {

        if (
            window.CodeEditor &&
            typeof window.CodeEditor.getCode ===
                "function"
        ) {

            try {

                return (
                    window.CodeEditor.getCode() ||
                    ""
                );


            } catch (error) {

                console.warn(
                    "Could not read editor code:",
                    error
                );
            }
        }


        return "";
    },


    /*
    |--------------------------------------------------------------------------
    | Get Project ID
    |--------------------------------------------------------------------------
    */

    getProjectId() {

        /*
         * Prefer Project manager.
         */

        if (
            window.Project &&
            typeof window.Project.getProjectId ===
                "function"
        ) {

            const projectId =
                window.Project.getProjectId();


            if (projectId) {
                return projectId;
            }
        }


        /*
         * SocketManager fallback.
         */

        if (
            window.SocketManager &&
            window.SocketManager.state?.projectId
        ) {

            return window.SocketManager
                .state
                .projectId;
        }


        /*
         * Workspace element fallback.
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
         * URL fallback.
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

        /*
         * Prefer SocketManager.
         */

        if (
            window.SocketManager &&
            window.SocketManager.state?.sessionId
        ) {

            return window.SocketManager
                .state
                .sessionId;
        }


        /*
         * Workspace element.
         */

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
    | Toast / UI Message
    |--------------------------------------------------------------------------
    */

    showMessage(
        message,
        type = "info"
    ) {

        if (
            window.App &&
            typeof window.App.showToast ===
                "function"
        ) {

            window.App.showToast(
                message,
                type
            );

            return;
        }


        console.log(
            `[${type}] ${message}`
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

        Chat.init();
    }
);


/*
|--------------------------------------------------------------------------
| Global Access
|--------------------------------------------------------------------------
*/

window.Chat = Chat;