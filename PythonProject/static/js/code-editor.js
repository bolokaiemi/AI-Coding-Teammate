"use strict";

/*
|--------------------------------------------------------------------------
| Code Editor
|--------------------------------------------------------------------------
*/

const CodeEditor = {
    elements: {
        code: null,
        lineNumbers: null,
        filename: null,
        language: null
    },

    state: {
        dirty: false,
        lastSavedCode: "",
        saveTimer: null
    },

    init() {
        this.elements.code =
            document.querySelector("#code-editor") ||
            document.querySelector(".code-area");

        this.elements.lineNumbers =
            document.querySelector("#line-numbers") ||
            document.querySelector(".line-numbers");

        this.elements.filename =
            document.querySelector("#filename");

        this.elements.language =
            document.querySelector("#language");

        if (!this.elements.code) {
            return;
        }

        this.bindEvents();
        this.updateLineNumbers();

        this.state.lastSavedCode = this.getCode();
    },

    bindEvents() {
        this.elements.code.addEventListener("input", () => {
            this.state.dirty = true;

            this.updateLineNumbers();
            this.scheduleAutoSave();
        });

        this.elements.code.addEventListener("scroll", () => {
            if (this.elements.lineNumbers) {
                this.elements.lineNumbers.scrollTop =
                    this.elements.code.scrollTop;
            }
        });

        this.elements.code.addEventListener("keydown", (event) => {
            this.handleKeyboard(event);
        });
    },

    handleKeyboard(event) {
        if (event.key === "Tab") {
            event.preventDefault();

            const start = this.elements.code.selectionStart;
            const end = this.elements.code.selectionEnd;

            const value = this.elements.code.value;

            this.elements.code.value =
                value.substring(0, start) +
                "    " +
                value.substring(end);

            this.elements.code.selectionStart =
                this.elements.code.selectionEnd =
                    start + 4;

            this.updateLineNumbers();
            this.state.dirty = true;
        }

        if (
            (event.ctrlKey || event.metaKey) &&
            event.key.toLowerCase() === "s"
        ) {
            event.preventDefault();
            this.save();
        }
    },

    getCode() {
        return this.elements.code
            ? this.elements.code.value
            : "";
    },

    setCode(code) {
        if (!this.elements.code) {
            return;
        }

        this.elements.code.value = code || "";

        this.updateLineNumbers();

        this.state.dirty = true;
    },

    getLanguage() {
        if (this.elements.language) {
            return this.elements.language.value;
        }

        return document.body.dataset.language || "python";
    },

    getFilename() {
        if (this.elements.filename) {
            return this.elements.filename.value ||
                this.elements.filename.textContent;
        }

        return "main.py";
    },

    updateLineNumbers() {
        if (!this.elements.lineNumbers) {
            return;
        }

        const lineCount =
            this.getCode().split("\n").length;

        let html = "";

        for (let i = 1; i <= lineCount; i++) {
            html += `${i}<br>`;
        }

        this.elements.lineNumbers.innerHTML = html;
    },

    scheduleAutoSave() {
        clearTimeout(this.state.saveTimer);

        this.state.saveTimer = setTimeout(() => {
            if (this.state.dirty) {
                this.save();
            }
        }, 2000);
    },

    async save() {
        if (!this.elements.code) {
            return;
        }

        const projectId =
            document.body.dataset.projectId;

        const sessionId =
            document.body.dataset.sessionId;

        if (!projectId || !sessionId) {
            return;
        }

        try {
            const data = await App.request(
                `/workspace/session/${sessionId}/save`,
                {
                    method: "POST",
                    body: JSON.stringify({
                        code: this.getCode()
                    })
                }
            );

            if (data.success) {
                this.state.dirty = false;
                this.state.lastSavedCode = this.getCode();
            }
        } catch (error) {
            console.error("Code save failed:", error);
        }
    },

    saveBeforeUnload() {
        if (!this.state.dirty) {
            return;
        }

        const sessionId =
            document.body.dataset.sessionId;

        if (!sessionId) {
            return;
        }

        const payload = JSON.stringify({
            code: this.getCode()
        });

        navigator.sendBeacon(
            `/workspace/session/${sessionId}/save`,
            new Blob(
                [payload],
                { type: "application/json" }
            )
        );
    },

    insertCode(code) {
        if (!this.elements.code) {
            return;
        }

        const start =
            this.elements.code.selectionStart;

        const end =
            this.elements.code.selectionEnd;

        const current =
            this.elements.code.value;

        this.elements.code.value =
            current.substring(0, start) +
            code +
            current.substring(end);

        this.elements.code.selectionStart =
            this.elements.code.selectionEnd =
                start + code.length;

        this.updateLineNumbers();
        this.state.dirty = true;
    },

    replaceCode(code) {
        this.setCode(code);
    }
};

document.addEventListener("DOMContentLoaded", () => {
    CodeEditor.init();
});