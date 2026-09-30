# sockets/__init__.py

"""
AI Coding Teammate - Socket.IO Events
=====================================

Registers all real-time Socket.IO event handlers.

Event modules:
- workspace_events
- chat_events
- code_events
- screen_events
- camera_events
"""


def register_socket_events(socketio):
    """
    Register every Socket.IO event module.

    Call this once from app.py after SocketIO has
    been initialized.
    """

    from sockets.workspace_events import register_workspace_events
    from sockets.chat_events import register_chat_events
    from sockets.code_events import register_code_events
    from sockets.screen_events import register_screen_events
    from sockets.camera_events import register_camera_events

    register_workspace_events(socketio)
    register_chat_events(socketio)
    register_code_events(socketio)
    register_screen_events(socketio)
    register_camera_events(socketio)