import pytest

from app import create_app


@pytest.fixture
def app():
    app = create_app("testing")

    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        WTF_CSRF_ENABLED=False,
    )

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_app_creation(app):
    assert app is not None
    assert app.config["TESTING"] is True


def test_home_page(client):
    response = client.get("/")

    assert response.status_code in (200, 302)


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data is not None
    assert "status" in data


def test_api_health_endpoint(client):
    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data is not None


def test_404_page(client):
    response = client.get(
        "/this-route-does-not-exist"
    )

    assert response.status_code == 404