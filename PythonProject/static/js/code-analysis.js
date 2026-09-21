"use strict";

/*
|--------------------------------------------------------------------------
| Code Analysis / Correction
|--------------------------------------------------------------------------
*/

const CodeAnalysis = {
    state: {
        processing: false,
        lastAnalysis: null
    },

    async analyze() {
        const code = CodeEditor.getCode();

        if (!code.trim()) {
            App.showToast(
                "Please enter some code first.",
                "warning"
            );
            return;
        }

        this.setProcessing(true);

        try {
            const data = await App.request(
                `${App.config.apiBase}/code/analyze`,
                {
                    method: "POST",
                    body: JSON.stringify({
                        code,
                        language: CodeEditor.getLanguage(),
                        filename: CodeEditor.getFilename(),
                        project_id: this.getProjectId(),
                        session_id: this.getSessionId()
                    })
                }
            );

            this.handleAnalysisResult(data);
        } catch (error) {
            console.error("Code analysis failed:", error);

            App.showToast(
                error.message,
                "danger"
            );
        } finally {
            this.setProcessing(false);
        }
    },

    async detectError(errorMessage = null) {
        const code = CodeEditor.getCode();

        if (!code.trim()) {
            return;
        }

        this.setProcessing(true);

        try {
            const data = await App.request(
                `${App.config.apiBase}/code/detect-error`,
                {
                    method: "POST",
                    body: JSON.stringify({
                        code,
                        language: CodeEditor.getLanguage(),
                        error: errorMessage
                    })
                }
            );

            this.handleAnalysisResult(data);
        } catch (error) {
            App.showToast(
                error.message,
                "danger"
            );
        } finally {
            this.setProcessing(false);
        }
    },

    async correct() {
        const code = CodeEditor.getCode();

        if (!code.trim()) {
            App.showToast(
                "There is no code to correct.",
                "warning"
            );
            return;
        }

        this.setProcessing(true);

        try {
            const data = await App.request(
                `${App.config.apiBase}/code/correct`,
                {
                    method: "POST",
                    body: JSON.stringify({
                        code,
                        language: CodeEditor.getLanguage(),
                        filename: CodeEditor.getFilename(),
                        problems: this.state.lastAnalysis?.errors || []
                    })
                }
            );

            this.handleCorrectionResult(data);
        } catch (error) {
            App.showToast(
                error.message,
                "danger"
            );
        } finally {
            this.setProcessing(false);
        }
    },

    async explain() {
        const code = CodeEditor.getCode();

        if (!code.trim()) {
            return;
        }

        this.setProcessing(true);

        try {
            const data = await App.request(
                `${App.config.apiBase}/code/explain`,
                {
                    method: "POST",
                    body: JSON.stringify({
                        code,
                        language: CodeEditor.getLanguage(),
                        filename: CodeEditor.getFilename()
                    })
                }
            );

            if (
                window.Visualizer &&
                typeof Visualizer.showExplanation === "function"
            ) {
                Visualizer.showExplanation(data);
            }
        } catch (error) {
            App.showToast(
                error.message,
                "danger"
            );
        } finally {
            this.setProcessing(false);
        }
    },

    handleAnalysisResult(data) {
        this.state.lastAnalysis = data;

        if (
            window.Visualizer &&
            typeof Visualizer.showAnalysis === "function"
        ) {
            Visualizer.showAnalysis(data);
        }

        this.setProcessing(false);
    },

    handleCorrectionResult(data) {
        if (!data || !data.success) {
            App.showToast(
                data?.message || "Code correction failed.",
                "danger"
            );
            return;
        }

        if (data.corrected_code) {
            CodeEditor.replaceCode(
                data.corrected_code
            );
        }

        if (
            window.Visualizer &&
            typeof Visualizer.showCorrection === "function"
        ) {
            Visualizer.showCorrection(data);
        }

        App.showToast(
            "Corrected code received from AI.",
            "success"
        );
    },

    setProcessing(processing) {
        this.state.processing = processing;

        App.setAIStatus(
            App.state.aiOnline,
            processing
        );
    },

    getProjectId() {
        return document.body.dataset.projectId || null;
    },

    getSessionId() {
        return document.body.dataset.sessionId || null;
    }
};

document.addEventListener("DOMContentLoaded", () => {
    const analyzeButton =
        document.querySelector("[data-action='analyze-code']");

    const correctButton =
        document.querySelector("[data-action='correct-code']");

    const explainButton =
        document.querySelector("[data-action='explain-code']");

    if (analyzeButton) {
        analyzeButton.addEventListener("click", () => {
            CodeAnalysis.analyze();
        });
    }

    if (correctButton) {
        correctButton.addEventListener("click", () => {
            CodeAnalysis.correct();
        });
    }

    if (explainButton) {
        explainButton.addEventListener("click", () => {
            CodeAnalysis.explain();
        });
    }
});