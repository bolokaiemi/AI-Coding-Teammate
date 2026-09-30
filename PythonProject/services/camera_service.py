"""
Camera Service

Handles camera frames received from the browser.

The browser captures camera data using:
    navigator.mediaDevices.getUserMedia()

AI vision processing will eventually be handled by:
    ai/visual_analyzer.py
"""

import base64
import binascii
import time


class CameraService:
    """Business logic for camera input."""

    @staticmethod
    def validate_frame(frame_data):
        """Validate a base64/data-URL camera frame."""

        if not frame_data:
            return False

        if isinstance(frame_data, str):
            return len(frame_data) > 20

        return False

    @staticmethod
    def decode_frame(frame_data):
        """Decode a camera frame into raw bytes."""

        if not CameraService.validate_frame(frame_data):
            raise ValueError("Invalid camera frame.")

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
                "Unable to decode camera frame."
            ) from exc

    @staticmethod
    def prepare_frame(frame_data):
        """
        Prepare camera data for the AI vision engine.
        """

        if not CameraService.validate_frame(frame_data):
            raise ValueError("Invalid camera frame.")

        return {
            "type": "camera",
            "frame": frame_data,
            "timestamp": time.time(),
        }

    @staticmethod
    def create_analysis_context(
        frame_data,
        project_id=None,
        code_context=None,
    ):
        """Create multimodal AI context from camera input."""

        return {
            "source": "camera",
            "project_id": project_id,
            "frame": frame_data,
            "code_context": code_context,
            "timestamp": time.time(),
        }

    @staticmethod
    def get_supported_features():
        """Return camera-analysis capabilities."""

        return {
            "camera_capture": True,
            "frame_analysis": True,
            "object_detection": True,
            "code_detection": True,
            "visual_question_answering": True,
            "visual_explanation": True,
        }