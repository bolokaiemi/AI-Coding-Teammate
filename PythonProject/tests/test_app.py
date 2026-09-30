"""
Application startup tests.
"""

import pytest


def test_app_module_imports():
    """
    app.py should import without crashing.
    """

    try:
        import app
    except Exception as exc:
        pytest.fail(
            f"app.py could not be imported: {exc!r}"
        )


def test_application_exists():
    """
    Verify that app.py exposes a Flask application
    or application factory.
    """

    import app as app_module

    application = getattr(
        app_module,
        "app",
        None,
    )

    factory = getattr(
        app_module,
        "create_app",
        None,
    )

    assert (
        application is not None
        or callable(factory)
    ), (
        "app.py must expose either `app` "
        "or `create_app()`."
    )


def test_socketio_exists():
    """
    Verify that Socket.IO is configured.
    """

    import app as app_module

    socketio = getattr(
        app_module,
        "socketio",
        None,
    )

    assert socketio is not None, (
        "app.py should expose a SocketIO instance."
    )


def test_app_is_flask_application():
    """
    Verify the exposed application is Flask-based.
    """

    import app as app_module

    application = getattr(
        app_module,
        "app",
        None,
    )

    if application is None:
        pytest.skip(
            "Application uses create_app() factory."
        )

    from flask import Flask

    assert isinstance(
        application,
        Flask,
    )