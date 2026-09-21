"use strict";

/*
|--------------------------------------------------------------------------
| AI Visualizer
|--------------------------------------------------------------------------
*/

const Visualizer = {
    elements: {
        container: null
    },

    init() {
        this.elements.container =
            document.querySelector("#visualizer") ||
            document.querySelector(".visualizer-body");

        this.bindEvents();
    },

    bindEvents() {
        document.addEventListener("click", (event) => {
            const button =
                event.target.closest(
                    "[data-action='clear-visualizer']"
                );

            if (button) {
                this.clear();
            }
        });
    },

    showAnalysis(data) {
        if (!this.elements.container) {
            return;
        }

        const errors = data.errors || [];
        const warnings = data.warnings || [];
        const suggestions = data.suggestions || [];

        let html = "";

        if (data.summary || data.message) {
            html += `
                <div class="visual-success">
                    <div class="visual-error-title">
                        AI Analysis
                    </div>
                    <div class="visual-error-message">
                        ${App.escapeHtml(
                            data.summary ||
                            data.message ||
                            ""
                        )}
                    </div>
                </div>
            `;
        }

        errors.forEach((error) => {
            html += this.renderProblem(
                error,
                "error"
            );
        });

        warnings.forEach((warning) => {
            html += this.renderProblem(
                warning,
                "warning"
            );
        });

        if (suggestions.length) {
            html += `
                <div class="visual-success">
                    <div class="visual-error-title">
                        Suggestions
                    </div>
                    <ul>
                        ${suggestions.map(
                            item => `
                                <li>
                                    ${App.escapeHtml(
                                        typeof item === "string"
                                            ? item
                                            : JSON.stringify(item)
                                    )}
                                </li>
                            `
                        ).join("")}
                    </ul>
                </div>
            `;
        }

        if (!html) {
            html = this.emptyState(
                "No problems detected."
            );
        }

        this.elements.container.innerHTML = html;
    },

    renderProblem(problem, type = "error") {
        const message =
            typeof problem === "string"
                ? problem
                : problem.message ||
                  problem.description ||
                  JSON.stringify(problem);

        const line =
            typeof problem === "object"
                ? problem.line
                : null;

        return `
            <div class="visual-${type}">
                <div class="visual-error-title">
                    ${type === "error" ? "Error" : "Warning"}
                    ${line ? ` — Line ${line}` : ""}
                </div>

                <div class="visual-error-message">
                    ${App.escapeHtml(message)}
                </div>
            </div>
        `;
    },

    showCorrection(data) {
        if (!this.elements.container) {
            return;
        }

        const explanation =
            data.explanation ||
            data.correction_explanation ||
            "AI generated a corrected version of the code.";

        this.elements.container.innerHTML = `
            <div class="visual-success">
                <div class="visual-error-title">
                    AI Correction
                </div>

                <div class="visual-error-message">
                    ${App.escapeHtml(explanation)}
                </div>
            </div>
        `;
    },

    showExplanation(data) {
        if (!this.elements.container) {
            return;
        }

        this.elements.container.innerHTML = `
            <div class="visual-success">
                <div class="visual-error-title">
                    Code Explanation
                </div>

                <div class="visual-error-message">
                    ${App.escapeHtml(
                        data.explanation ||
                        data.message ||
                        "No explanation returned."
                    )}
                </div>
            </div>
        `;
    },

    handleAnalysis(data) {
        if (!data) {
            return;
        }

        this.showAnalysis(data);
    },

    showVisualObservation(data) {
        if (!this.elements.container) {
            return;
        }

        const observations =
            data.observations || [];

        const errors =
            data.errors || [];

        let html = "";

        if (data.message) {
            html += `
                <div class="visual-success">
                    <div class="visual-error-title">
                        AI Visual Analysis
                    </div>

                    <div class="visual-error-message">
                        ${App.escapeHtml(data.message)}
                    </div>
                </div>
            `;
        }

        observations.forEach((observation) => {
            html += `
                <div class="visual-success">
                    <div class="visual-error-message">
                        ${App.escapeHtml(
                            typeof observation === "string"
                                ? observation
                                : JSON.stringify(observation)
                        )}
                    </div>
                </div>
            `;
        });

        errors.forEach((error) => {
            html += this.renderProblem(error, "error");
        });

        this.elements.container.innerHTML =
            html || this.emptyState(
                "No visual information detected."
            );
    },

    emptyState(message) {
        return `
            <div class="visualizer-empty">
                <div class="visualizer-empty-icon">
                    <span>AI</span>
                </div>

                <p>
                    ${App.escapeHtml(message)}
                </p>
            </div>
        `;
    },

    clear() {
        if (!this.elements.container) {
            return;
        }

        this.elements.container.innerHTML =
            this.emptyState(
                "Show me your code, screen, camera, or project."
            );
    }
};

document.addEventListener("DOMContentLoaded", () => {
    Visualizer.init();
});