"use strict";

/*
|--------------------------------------------------------------------------
| Screen Sharing
|--------------------------------------------------------------------------
*/

const ScreenShare = {
    state: {
        active: false,
        stream: null,
        video: null,
        canvas: null,
        context: null,
        timer: null,
        interval: 1500
    },

    async start() {
        if (this.state.active) {
            return;
        }

        try {
            const stream =
                await navigator.mediaDevices.getDisplayMedia({
                    video: true,
                    audio: false
                });

            this.state.stream = stream;
            this.state.active = true;

            this.createVideoElement(stream);
            this.createCanvas();

            this.updateButton(true);

            const track =
                stream.getVideoTracks()[0];

            track.addEventListener(
                "ended",
                () => this.stop()
            );

            this.startFrameCapture();

            App.showToast(
                "Screen sharing started.",
                "success"
            );
        } catch (error) {
            console.error(
                "Screen sharing failed:",
                error
            );

            App.showToast(
                "Screen sharing was cancelled or unavailable.",
                "warning"
            );
        }
    },

    stop() {
        if (this.state.timer) {
            clearInterval(this.state.timer);
            this.state.timer = null;
        }

        if (this.state.stream) {
            this.state.stream
                .getTracks()
                .forEach(track => track.stop());
        }

        this.state.stream = null;
        this.state.active = false;

        this.updateButton(false);
    },

    createVideoElement(stream) {
        let video =
            document.querySelector("#screen-preview");

        if (!video) {
            video =
                document.createElement("video");

            video.id = "screen-preview";
            video.className =
                "visualizer-video";

            video.autoplay = true;
            video.muted = true;
            video.playsInline = true;

            const container =
                document.querySelector(".visualizer-body");

            if (container) {
                container.prepend(video);
            }
        }

        video.srcObject = stream;

        this.state.video = video;
    },

    createCanvas() {
        const canvas =
            document.createElement("canvas");

        canvas.width = 1280;
        canvas.height = 720;

        this.state.canvas = canvas;
        this.state.context =
            canvas.getContext("2d");
    },

    startFrameCapture() {
        this.state.timer =
            setInterval(
                () => this.captureFrame(),
                this.state.interval
            );
    },

    captureFrame() {
        const video = this.state.video;

        if (
            !video ||
            video.readyState <
                HTMLMediaElement.HAVE_CURRENT_DATA
        ) {
            return;
        }

        const canvas = this.state.canvas;
        const context = this.state.context;

        const width =
            video.videoWidth || 1280;

        const height =
            video.videoHeight || 720;

        canvas.width = width;
        canvas.height = height;

        context.drawImage(
            video,
            0,
            0,
            width,
            height
        );

        const frame =
            canvas.toDataURL(
                "image/jpeg",
                0.65
            );

        this.sendFrame(frame);
    },

    sendFrame(frame) {
        const data = {
            frame,
            project_id:
                document.body.dataset.projectId || null,
            session_id:
                document.body.dataset.sessionId || null,
            code_context:
                CodeEditor.getCode()
        };

        if (
            window.SocketManager &&
            SocketManager.state.connected
        ) {
            SocketManager.sendScreenFrame(data);
        } else {
            this.analyzeViaHTTP(data);
        }
    },

    async analyzeViaHTTP(data) {
        try {
            const result =
                await App.request(
                    `${App.config.apiBase}/screen/analyze`,
                    {
                        method: "POST",
                        body: JSON.stringify(data)
                    }
                );

            Visualizer.showVisualObservation(
                result
            );
        } catch (error) {
            console.error(
                "Screen analysis failed:",
                error
            );
        }
    },

    updateButton(active) {
        const button =
            document.querySelector(
                "[data-action='screen-share']"
            );

        if (!button) {
            return;
        }

        button.classList.toggle(
            "active",
            active
        );

        button.setAttribute(
            "aria-pressed",
            String(active)
        );

        const label =
            button.querySelector("span");

        if (label) {
            label.textContent =
                active
                    ? "Stop Screen"
                    : "Share Screen";
        }
    }
};

document.addEventListener("DOMContentLoaded", () => {
    const button =
        document.querySelector(
            "[data-action='screen-share']"
        );

    if (button) {
        button.addEventListener(
            "click",
            () => {
                if (ScreenShare.state.active) {
                    ScreenShare.stop();
                } else {
                    ScreenShare.start();
                }
            }
        );
    }
});