"""
Project route and model tests.
"""

import pytest


def test_project_routes_import():
    """
    Project routes should import successfully.
    """

    try:
        from routes import project_routes
    except Exception as exc:
        pytest.fail(
            "Could not import project routes: "
            f"{exc!r}"
        )


def test_project_blueprint_exists():
    """
    project_routes.py should expose project_bp.
    """

    from routes import project_routes

    assert hasattr(
        project_routes,
        "project_bp",
    )


def test_project_blueprint_name():
    """
    Verify the project blueprint name.
    """

    from routes.project_routes import project_bp

    assert project_bp.name == "project"


def test_project_blueprint_prefix():
    """
    Project URLs should use /projects.
    """

    from routes.project_routes import project_bp

    assert project_bp.url_prefix == "/projects"


def test_project_model_import():
    """
    Project database model should be available.
    """

    try:
        from database.models import Project
    except Exception as exc:
        pytest.fail(
            "Could not import Project model: "
            f"{exc!r}"
        )

    assert Project is not None


def test_workspace_routes_import():
    """
    Workspace routes should import successfully.
    """

    try:
        from routes import workspace_routes
    except Exception as exc:
        pytest.fail(
            "Could not import workspace routes: "
            f"{exc!r}"
        )


def test_workspace_blueprint():
    """
    Verify workspace blueprint configuration.
    """

    from routes.workspace_routes import (
        workspace_bp,
    )

    assert workspace_bp.name == "workspace"

    assert workspace_bp.url_prefix == (
        "/workspace"
    )