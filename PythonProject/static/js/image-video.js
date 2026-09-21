"use strict";

/*
|--------------------------------------------------------------------------
| Image / Video Upload and Analysis
|--------------------------------------------------------------------------
*/

const ImageVideo = {
    elements: {
        input: null
    },

    init() {
        this.elements.input =
            document.querySelector(
                "#media-input"
            );

        if (!this.elements.input) {
            return;
        }

        this.elements.input.addEventListener(
            "change",
            (event) => {
                this.handleFiles(
                    event.target.files
                );
            }
        );
    },

    async handleFiles(files) {
        if (!files || !files.length) {
            return;
        }

        for (const file of files) {
            await this.processFile(file);
        }
    },

    async processFile(file) {
        const type = file.type;

        if (type.startsWith("image/")) {
            await this.processImage(file);
            return;
        }

        if (type.startsWith("video/")) {
            await this.processVideo(file);
            return;
        }

        App.showToast(
            "Unsupported media type.",
            "warning"
        );
    },

    async processImage(file) {
        const dataUrl =
            await this.readFile(file);

        this.showPreview(
            dataUrl,
            "image"
        );

        try {
            const result =
                await App.request(
                    `${App.config.apiBase}/visual/analyze`,
                    {
                        method: "POST",
                        body: JSON.stringify({
                            image:
                                dataUrl,
                            context: {
                                project_id:
                                    document.body.dataset.projectId,
                                session_id:
                                    document.body.dataset.sessionId,
                                code:
                                    CodeEditor.getCode()
                            }
                        })
                    }
                );

            Visualizer.showVisualObservation(
                result
            );
        } catch (error) {
            App.showToast(
                error.message,
                "danger"
            );
        }
    },

    async processVideo(file) {
        const dataUrl =
            await this.readFile(file);

        this.showPreview(
            dataUrl,
            "video"
        );

        App.showToast(
            "Video loaded. Video-frame analysis will be processed by the visual pipeline.",
            "info"
        );
    },

    readFile(file) {
        return new Promise(
            (resolve, reject) => {
                const reader =
                    new FileReader();

                reader.onload =
                    () => resolve(
                        reader.result
                    );

                reader.onerror =
                    reject;

                reader.readAsDataURL(file);
            }
        );
    },

    showPreview(source, type) {
        const container =
            document.querySelector(
                ".visualizer-body"
            );

        if (!container) {
            return;
        }

        let element;

        if (type === "image") {
            element =
                document.createElement("img");

            element.src = source;
        } else {
            element =
                document.createElement("video");

            element.src = source;
            element.controls = true;
        }

        element.className =
            "visualizer-video";

        container.prepend(element);
    }
};

document.addEventListener("DOMContentLoaded", () => {
    ImageVideo.init();

    const button =
        document.querySelector(
            "[data-action='media-upload']"
        );

    const input =
        document.querySelector(
            "#media-input"
        );

    if (button && input) {
        button.addEventListener(
            "click",
            () => input.click()
        );
    }
});