import pytest

from app import create_app
from database.database import db
from database.models import User


@pytest.fixture
def app():
    app = create_app("testing")

    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        WTF_CSRF_ENABLED=False,
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def create_test_user():
    user = User(
        first_name="Test",
        last_name="Developer",
        email="test@example.com",
        password="TestPassword123!",
        occupation="Software Engineer",
        is_active=True,
        is_verified=True,
    )

    db.session.add(user)
    db.session.commit()

    return user


def test_register_page(client):
    response = client.get("/register")

    assert response.status_code in (200, 302)


def test_login_page(client):
    response = client.get("/login")

    assert response.status_code in (200, 302)


def test_user_creation(app):
    with app.app_context():
        user = create_test_user()

        assert user.id is not None
        assert user.email == "test@example.com"


def test_password_is_not_plain_text(app):
    with app.app_context():
        user = create_test_user()

        assert user.password != "TestPassword123!"


def test_login(client, app):
    with app.app_context():
        create_test_user()

    response = client.post(
        "/login",
        data={
            "email": "test@example.com",
            "password": "TestPassword123!",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200


def test_invalid_login(client, app):
    with app.app_context():
        create_test_user()

    response = client.post(
        "/login",
        data={
            "email": "test@example.com",
            "password": "WrongPassword!",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200


def test_logout(client):
    response = client.get(
        "/logout",
        follow_redirects=True
    )

    assert response.status_code == 200