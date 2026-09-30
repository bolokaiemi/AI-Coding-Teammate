# sockets/workspace_events.py

"""
Workspace Socket Events
=======================

Handles:
- client_ready
- join_workspace
- leave_workspace
"""

from flask import request
from flask_login import current_user
from flask_socketio import (
    emit,
    join_room,
    leave_room,
)

from database.models import Project


def _project_room(project_id):
    """
    Return the Socket.IO room name for a project.
    """

    return f"project:{project_id}"


def _get_user_project(project_id):
    """
    Return a project only when it belongs to the
    authenticated user.
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


def register_workspace_events(socketio):
    """
    Register workspace Socket.IO handlers.
    """

    # ========================================================
    # CLIENT READY
    # ========================================================

    @socketio.on("client_ready")
    def handle_client_ready(data=None):
        """
        Called after the browser establishes its
        Socket.IO connection.
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

        emit(
            "ai_status",
            {
                "online": True,
                "message": (
                    "AI Coding Teammate is online."
                ),
            },
        )

    # ========================================================
    # JOIN WORKSPACE
    # ========================================================

    @socketio.on("join_workspace")
    def handle_join_workspace(data=None):
        """
        Join the Socket.IO room belonging to a project.
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

        if not project_id:

            emit(
                "error",
                {
                    "message": (
                        "Project ID is required."
                    )
                },
            )

            return

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

        room = _project_room(
            project.id
        )

        join_room(
            room
        )

        emit(
            "workspace_joined",
            {
                "success": True,
                "project_id": project.id,
                "session_id": session_id,
                "room": room,
            },
        )

    # ========================================================
    # LEAVE WORKSPACE
    # ========================================================

    @socketio.on("leave_workspace")
    def handle_leave_workspace(data=None):
        """
        Leave a project's Socket.IO room.
        """

        if not current_user.is_authenticated:
            return

        data = data or {}

        project_id = data.get(
            "project_id"
        )

        if not project_id:
            return

        project = _get_user_project(
            project_id
        )

        if project is None:
            return

        room = _project_room(
            project.id
        )

        leave_room(
            room
        )

        emit(
            "workspace_left",
            {
                "success": True,
                "project_id": project.id,
            },
        )

    # ========================================================
    # DISCONNECT
    # ========================================================

    @socketio.on("disconnect")
    def handle_disconnect(reason=None):
        """
        Handle browser/socket disconnection.

        Socket.IO automatically removes disconnected clients
        from rooms, so no manual leave_room() is required.
        """

        socket_id = getattr(
            request,
            "sid",
            None,
        )

        print(
            "AI Coding Teammate socket disconnected:",
            socket_id,
            reason,
        )