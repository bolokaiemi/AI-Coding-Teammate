"use strict";

/*
|--------------------------------------------------------------------------
| Voice Input / Text-to-Speech
|--------------------------------------------------------------------------
*/

const Voice = {
    recognition: null,

    state: {
        listening: false,
        supported: false
    },

    init() {
        const SpeechRecognition =
            window.SpeechRecognition ||
            window.webkitSpeechRecognition;

        if (!SpeechRecognition) {
            console.warn(
                "Speech recognition is not supported."
            );
            return;
        }

        this.state.supported = true;

        this.recognition =
            new SpeechRecognition();

        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.lang =
            document.documentElement.lang ||
            "en-US";

        this.recognition.onstart = () => {
            this.state.listening = true;
            this.updateButton(true);
        };

        this.recognition.onend = () => {
            this.state.listening = false;
            this.updateButton(false);
        };

        this.recognition.onerror = (event) => {
            console.error(
                "Speech recognition error:",
                event.error
            );

            this.state.listening = false;
            this.updateButton(false);
        };

        this.recognition.onresult = (event) => {
            let transcript = "";

            for (
                let i = event.resultIndex;
                i < event.results.length;
                i++
            ) {
                transcript +=
                    event.results[i][0].transcript;
            }

            const input =
                document.querySelector(
                    "#chat-input"
                ) ||
                document.querySelector(
                    ".chat-input"
                );

            if (input) {
                input.value =
                    transcript.trim();
            }
        };
    },

    toggle() {
        if (!this.state.supported) {
            App.showToast(
                "Voice recognition is not supported by this browser.",
                "warning"
            );
            return;
        }

        if (this.state.listening) {
            this.stop();
        } else {
            this.start();
        }
    },

    start() {
        if (!this.recognition) {
            return;
        }

        try {
            this.recognition.start();
        } catch (error) {
            console.warn(
                "Could not start recognition:",
                error
            );
        }
    },

    stop() {
        if (!this.recognition) {
            return;
        }

        this.recognition.stop();
    },

    speak(text) {
        if (
            !("speechSynthesis" in window) ||
            !text
        ) {
            return;
        }

        window.speechSynthesis.cancel();

        const utterance =
            new SpeechSynthesisUtterance(text);

        utterance.rate = 1;
        utterance.pitch = 1;

        window.speechSynthesis.speak(
            utterance
        );
    },

    updateButton(active) {
        const button =
            document.querySelector(
                "[data-action='voice']"
            );

        if (!button) {
            return;
        }

        button.classList.toggle(
            "active",
            active
        );

        const label =
            button.querySelector("span");

        if (label) {
            label.textContent =
                active
                    ? "Listening..."
                    : "Voice";
        }
    }
};

document.addEventListener("DOMContentLoaded", () => {
    Voice.init();

    const button =
        document.querySelector(
            "[data-action='voice']"
        );

    if (button) {
        button.addEventListener(
            "click",
            () => Voice.toggle()
        );
    }
});