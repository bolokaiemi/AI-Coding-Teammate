"""
Screen Service

Handles screen-sharing input received from the browser.

The browser is responsible for capturing the screen with:
    navigator.mediaDevices.getDisplayMedia()

This service prepares/stores metadata about incoming frames.

Actual AI vision processing belongs in:
    ai/visual_analyzer.py
"""

import base64
import binascii
import time


class ScreenService:
    """Business logic for screen-sharing data."""

    @staticmethod
    def validate_frame(frame_data):
        """
        Validate a base64/data-URL screen frame.
        """

        if not frame_data:
            return False

        if isinstance(frame_data, str):
            return len(frame_data) > 20

        return False

    @staticmethod
    def decode_frame(frame_data):
        """
        Decode a browser data URL/base64 frame.

        Returns:
            bytes
        """

        if not ScreenService.validate_frame(frame_data):
            raise ValueError("Invalid screen frame.")

        try:
            if "," in frame_data:
                _, encoded_data = frame_data.split(",", 1)
            else:
                encoded_data = frame_data

            return base64.b64decode(
                encoded_data,
                validate=True,
            )

        except (ValueError, binascii.Error) as exc:
            raise ValueError(
                "Unable to decode screen frame."
            ) from exc

    @staticmethod
    def prepare_frame(frame_data):
        """
        Prepare screen data for the AI vision layer.

        The returned object can later be passed to
        ai.visual_analyzer.
        """

        if not ScreenService.validate_frame(frame_data):
            raise ValueError("Invalid screen frame.")

        return {
            "type": "screen",
            "frame": frame_data,
            "timestamp": time.time(),
        }

    @staticmethod
    def create_analysis_context(
        frame_data,
        project_id=None,
        code_context=None,
    ):
        """
        Create a context package for future multimodal AI analysis.
        """

        return {
            "source": "screen",
            "project_id": project_id,
            "frame": frame_data,
            "code_context": code_context,
            "timestamp": time.time(),
        }

    @staticmethod
    def get_supported_features():
        """Return screen-analysis capabilities."""

        return {
            "screen_capture": True,
            "frame_analysis": True,
            "code_detection": True,
            "error_detection": True,
            "ui_analysis": True,
            "visual_explanation": True,
        }