import pytest

from app import create_app, socketio
from database.database import db


@pytest.fixture
def app():
    app = create_app("testing")

    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def socket_client(app):
    return socketio.test_client(
        app,
        flask_test_client=app.test_client()
    )


def test_socket_connection(
    socket_client
):
    assert socket_client.is_connected()


def test_socket_disconnect(
    socket_client
):
    socket_client.disconnect()

    assert not socket_client.is_connected()


def test_client_ready(
    socket_client
):
    socket_client.emit(
        "client_ready",
        {
            "timestamp": 123456
        }
    )

    received = socket_client.get_received()

    assert isinstance(
        received,
        list
    )


def test_join_workspace(
    socket_client
):
    socket_client.emit(
        "join_workspace",
        {
            "project_id": 1,
            "session_id": 1
        }
    )

    received = socket_client.get_received()

    assert isinstance(
        received,
        list
    )


def test_leave_workspace(
    socket_client
):
    socket_client.emit(
        "leave_workspace",
        {
            "project_id": 1
        }
    )

    received = socket_client.get_received()

    assert isinstance(
        received,
        list
    )