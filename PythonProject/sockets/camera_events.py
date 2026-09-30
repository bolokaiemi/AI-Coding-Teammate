# sockets/camera_events.py

"""
Camera Socket Events
====================

Handles:
- camera_frame
- camera_analysis

Used when the developer shows the AI Coding Teammate
something through their camera.
"""

from flask_login import current_user
from flask_socketio import emit

from database.models import Project


def _get_user_project(project_id):
    """
    Verify project ownership.
    """

    if not current_user.is_authenticated:
        return None

    try:
        project_id = int(project_id)
    except (TypeError, ValueError):
        return None

    return Project.query.filter_by(
        id=project_id,
        user_id=current_user.id,
    ).first()


def register_camera_events(socketio):
    """
    Register camera Socket.IO events.
    """

    @socketio.on("camera_frame")
    def handle_camera_frame(data=None):
        """
        Receive a captured camera frame.
        """

        if not current_user.is_authenticated:

            emit(
                "error",
                {
                    "message": (
                        "Authentication is required."
                    )
                },
            )

            return

        data = data or {}

        project_id = data.get(
            "project_id"
        )

        session_id = data.get(
            "session_id"
        )

        frame = data.get(
            "frame"
        )

        if not frame:

            emit(
                "camera_analysis",
                {
                    "success": False,
                    "error": (
                        "No camera frame was supplied."
                    ),
                },
            )

            return

        project = None

        if project_id:

            project = _get_user_project(
                project_id
            )

            if project is None:

                emit(
                    "camera_analysis",
                    {
                        "success": False,
                        "error": (
                            "Project not found."
                        ),
                    },
                )

                return

        # ----------------------------------------------------
        # FUTURE CAMERA AI SERVICE
        # ----------------------------------------------------
        #
        # from services.camera_service import CameraService
        #
        # result = CameraService.analyze_frame(
        #     frame=frame,
        #     project_id=project.id,
        # )
        #
        # ----------------------------------------------------

        result = {
            "objects": [],
            "text": [],
            "code_detected": False,
            "errors": [],
            "observations": [],
            "suggestions": [],
        }

        emit(
            "camera_analysis",
            {
                "success": True,
                "project_id": (
                    project.id
                    if project
                    else None
                ),
                "session_id": session_id,
                "analysis": result,
            },
        )