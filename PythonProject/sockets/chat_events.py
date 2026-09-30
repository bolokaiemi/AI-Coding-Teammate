# sockets/chat_events.py

"""
Chat Socket Events
==================

Handles:
- chat_message
- chat_response
- ai_typing
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


def register_chat_events(socketio):
    """
    Register AI chat Socket.IO events.
    """

    @socketio.on("chat_message")
    def handle_chat_message(data=None):
        """
        Receive a chat message from the workspace.
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

        message = str(
            data.get(
                "message",
                "",
            )
        ).strip()

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

        # ----------------------------------------------------
        # VALIDATE MESSAGE
        # ----------------------------------------------------

        if not message:

            emit(
                "error",
                {
                    "message": (
                        "Chat message cannot be empty."
                    )
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
                    "error",
                    {
                        "message": (
                            "Project not found."
                        )
                    },
                )

                return

        # ----------------------------------------------------
        # TYPING INDICATOR
        # ----------------------------------------------------

        emit(
            "ai_typing",
            {
                "typing": True,
            },
        )

        try:

            # ------------------------------------------------
            # AI SERVICE CONNECTION
            # ------------------------------------------------
            #
            # Later this section should call:
            #
            # from services.chat_service import ChatService
            #
            # response = ChatService.send_message(
            #     user_id=current_user.id,
            #     project_id=project.id if project else None,
            #     session_id=session_id,
            #     message=message,
            #     code=code,
            # )
            #
            # ------------------------------------------------

            response_text = (
                "I received your message. "
                "The AI Coding Teammate conversation "
                "service will process it here."
            )

            emit(
                "chat_response",
                {
                    "success": True,
                    "response": response_text,
                    "project_id": (
                        project.id
                        if project
                        else None
                    ),
                    "session_id": session_id,
                    "code_received": bool(
                        code.strip()
                    ),
                },
            )

        except Exception:

            emit(
                "chat_response",
                {
                    "success": False,
                    "error": (
                        "The AI Teammate could not "
                        "process the message."
                    ),
                },
            )

        finally:

            emit(
                "ai_typing",
                {
                    "typing": False,
                },
            )