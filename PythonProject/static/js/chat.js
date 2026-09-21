"use strict";

/*
|--------------------------------------------------------------------------
| AI Teammate Chat
|--------------------------------------------------------------------------
*/

const Chat = {
    elements: {
        messages: null,
        input: null,
        send: null
    },

    state: {
        sending: false
    },

    init() {
        this.elements.messages =
            document.querySelector("#chat-messages") ||
            document.querySelector(".chat-messages");

        this.elements.input =
            document.querySelector("#chat-input") ||
            document.querySelector(".chat-input");

        this.elements.send =
            document.querySelector("#chat-send") ||
            document.querySelector(".chat-send");

        if (!this.elements.input) {
            return;
        }

        this.bindEvents();
    },

    bindEvents() {
        if (this.elements.send) {
            this.elements.send.addEventListener(
                "click",
                () => this.send()
            );
        }

        this.elements.input.addEventListener(
            "keydown",
            (event) => {
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

    async send() {
        const message =
            this.elements.input.value.trim();

        if (!message || this.state.sending) {
            return;
        }

        this.state.sending = true;

        this.addMessage(
            "user",
            message
        );

        this.elements.input.value = "";

        try {
            const data = await App.request(
                `${App.config.apiBase}/ai/chat`,
                {
                    method: "POST",
                    body: JSON.stringify({
                        message,
                        project_id: this.getProjectId(),
                        session_id: this.getSessionId(),
                        code_context: CodeEditor.getCode()
                    })
                }
            );

            this.handleAIResponse(data);
        } catch (error) {
            this.addMessage(
                "ai",
                `Sorry, I could not process that request: ${error.message}`
            );
        } finally {
            this.state.sending = false;
        }
    },

    handleAIResponse(data) {
        if (!data) {
            return;
        }

        const message =
            data.message ||
            data.response ||
            data.content ||
            data.error;

        if (message) {
            this.addMessage(
                "ai",
                message
            );
        }
    },

    addMessage(role, message) {
        if (!this.elements.messages) {
            return;
        }

        const wrapper =
            document.createElement("div");

        wrapper.className =
            `chat-message ${role}`;

        wrapper.innerHTML = `
            <div class="chat-bubble">
                ${App.escapeHtml(message)}
            </div>
        `;

        this.elements.messages.appendChild(wrapper);

        this.elements.messages.scrollTop =
            this.elements.messages.scrollHeight;
    },

    getProjectId() {
        return document.body.dataset.projectId || null;
    },

    getSessionId() {
        return document.body.dataset.sessionId || null;
    }
};

document.addEventListener("DOMContentLoaded", () => {
    Chat.init();
});