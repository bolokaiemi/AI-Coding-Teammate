# sockets/code_events.py

"""
Code Socket Events
==================

Handles:
- code_analyze
- code_correct
"""

from flask_login import current_user
from flask_socketio import emit

from database.models import Project


def _get_user_project(project_id):
    """
    Verify that a project belongs to the current user.
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


def register_code_events(socketio):
    """
    Register code-related Socket.IO handlers.
    """

    # ========================================================
    # ANALYZE CODE
    # ========================================================

    @socketio.on("code_analyze")
    def handle_code_analyze(data=None):
        """
        Analyze code sent from the workspace editor.
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

        code = str(
            data.get(
                "code",
                "",
            )
        )

        language = str(
            data.get(
                "language",
                "python",
            )
        ).strip()

        # ----------------------------------------------------
        # VALIDATE CODE
        # ----------------------------------------------------

        if not code.strip():

            emit(
                "code_analysis_result",
                {
                    "success": False,
                    "error": (
                        "No code was supplied."
                    ),
                },
            )

            return

        # ----------------------------------------------------
        # VERIFY PROJECT
        # ----------------------------------------------------

        project = None

        if project_id:

            project = _get_user_project(
                project_id
            )

            if project is None:

                emit(
                    "code_analysis_result",
                    {
                        "success": False,
                        "error": (
                            "Project not found."
                        ),
                    },
                )

                return

        # ----------------------------------------------------
        # FUTURE AI ANALYSIS SERVICE
        # ----------------------------------------------------
        #
        # from services.analysis_service import AnalysisService
        #
        # result = AnalysisService.analyze(
        #     code=code,
        #     language=language,
        #     project_id=project.id,
        # )
        #
        # ----------------------------------------------------

        result = {
            "errors": [],
            "warnings": [],
            "suggestions": [],
        }

        emit(
            "code_analysis_result",
            {
                "success": True,
                "project_id": (
                    project.id
                    if project
                    else None
                ),
                "session_id": session_id,
                "language": language,
                "analysis": result,
                "message": (
                    "Code received successfully "
                    "for AI analysis."
                ),
            },
        )

    # ========================================================
    # CORRECT CODE
    # ========================================================

    @socketio.on("code_correct")
    def handle_code_correct(data=None):
        """
        Request an AI-generated correction.
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

        code = str(
            data.get(
                "code",
                "",
            )
        )

        language = str(
            data.get(
                "language",
                "python",
            )
        ).strip()

        if not code.strip():

            emit(
                "code_correction_result",
                {
                    "success": False,
                    "error": (
                        "No code was supplied."
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
                    "code_correction_result",
                    {
                        "success": False,
                        "error": (
                            "Project not found."
                        ),
                    },
                )

                return

        # ----------------------------------------------------
        # FUTURE AI CORRECTION SERVICE
        # ----------------------------------------------------

        corrected_code = code

        emit(
            "code_correction_result",
            {
                "success": True,
                "project_id": (
                    project.id
                    if project
                    else None
                ),
                "session_id": session_id,
                "language": language,
                "original_code": code,
                "corrected_code": corrected_code,
                "explanation": (
                    "The AI correction service "
                    "will provide corrections here."
                ),
            },
        )