"""
Socket.IO backend tests.

These tests verify that the socket event package
can be imported and exposes its registration
interface.
"""

import pytest


def test_socket_package_imports():
    """
    The sockets package should import.
    """

    try:
        import sockets
    except Exception as exc:
        pytest.fail(
            "Could not import sockets package: "
            f"{exc!r}"
        )


def test_register_socket_events_exists():
    """
    sockets/__init__.py should expose
    register_socket_events.
    """

    import sockets

    assert hasattr(
        sockets,
        "register_socket_events",
    )

    assert callable(
        sockets.register_socket_events
    )


def test_workspace_events_import():
    """
    Workspace socket handlers should import.
    """

    try:
        from sockets import workspace_events
    except Exception as exc:
        pytest.fail(
            "workspace_events could not import: "
            f"{exc!r}"
        )


def test_chat_events_import():
    """
    Chat socket handlers should import.
    """

    try:
        from sockets import chat_events
    except Exception as exc:
        pytest.fail(
            "chat_events could not import: "
            f"{exc!r}"
        )


def test_code_events_import():
    """
    Code socket handlers should import.
    """

    try:
        from sockets import code_events
    except Exception as exc:
        pytest.fail(
            "code_events could not import: "
            f"{exc!r}"
        )


def test_screen_events_import():
    """
    Screen socket handlers should import.
    """

    try:
        from sockets import screen_events
    except Exception as exc:
        pytest.fail(
            "screen_events could not import: "
            f"{exc!r}"
        )


def test_camera_events_import():
    """
    Camera socket handlers should import.
    """

    try:
        from sockets import camera_events
    except Exception as exc:
        pytest.fail(
            "camera_events could not import: "
            f"{exc!r}"
        )