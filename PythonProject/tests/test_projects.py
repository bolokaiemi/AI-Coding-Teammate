import pytest

from app import create_app
from database.database import db
from database.models import User, Project


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
def client(app):
    return app.test_client()


def create_user():
    user = User(
        first_name="Test",
        last_name="Developer",
        email="developer@example.com",
        password="TestPassword123!",
        occupation="AI Engineer",
        is_active=True,
        is_verified=True,
    )

    db.session.add(user)
    db.session.commit()

    return user


def create_project(user_id):
    project = Project(
        user_id=user_id,
        name="AI Coding Teammate",
        description="AI-powered development workspace",
        language="Python",
        framework="Flask",
        status="active",
    )

    db.session.add(project)
    db.session.commit()

    return project


def test_project_creation(app):
    with app.app_context():
        user = create_user()

        project = create_project(
            user.id
        )

        assert project.id is not None
        assert project.name == "AI Coding Teammate"
        assert project.user_id == user.id


def test_project_relationship(app):
    with app.app_context():
        user = create_user()

        project = create_project(
            user.id
        )

        assert project in user.projects


def test_projects_page(client):
    response = client.get(
        "/dashboard/projects"
    )

    assert response.status_code in (
        200,
        302
    )


def test_project_model_defaults(app):
    with app.app_context():
        user = create_user()

        project = create_project(
            user.id
        )

        assert project.status == "active"


def test_project_deletion(app):
    with app.app_context():
        user = create_user()

        project = create_project(
            user.id
        )

        project_id = project.id

        db.session.delete(project)
        db.session.commit()

        deleted = db.session.get(
            Project,
            project_id
        )

        assert deleted is None