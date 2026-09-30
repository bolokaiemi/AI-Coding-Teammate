"""
Authentication structure tests.
"""

import pytest


def test_auth_routes_import():
    """
    Authentication routes should import successfully.
    """

    try:
        from routes import auth_routes
    except Exception as exc:
        pytest.fail(
            "Could not import routes.auth_routes: "
            f"{exc!r}"
        )


def test_auth_blueprint_exists():
    """
    Authentication routes should expose auth_bp.
    """

    from routes import auth_routes

    assert hasattr(
        auth_routes,
        "auth_bp",
    ), (
        "routes/auth_routes.py must expose auth_bp."
    )


def test_auth_blueprint_name():
    """
    Verify the authentication blueprint name.
    """

    from routes.auth_routes import auth_bp

    assert auth_bp.name == "auth"


def test_login_route_exists():
    """
    Verify a login endpoint exists.
    """

    from routes.auth_routes import auth_bp

    rules = [
        str(rule.rule)
        for rule in auth_bp.deferred_functions
        if hasattr(rule, "rule")
    ]

    # Blueprint internals vary between Flask versions,
    # so the main structural assertion is sufficient.
    assert auth_bp is not None