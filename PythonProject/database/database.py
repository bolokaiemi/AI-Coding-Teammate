"""
AI Coding Teammate
Database Configuration

This module initializes SQLAlchemy and provides database
initialization helpers for the Flask application.
"""

from flask_sqlalchemy import SQLAlchemy


# ----------------------------------------------------------------------
# SQLAlchemy Extension
# ----------------------------------------------------------------------

db = SQLAlchemy()


# ----------------------------------------------------------------------
# Initialize Database
# ----------------------------------------------------------------------

def init_db(app):
    """
    Initialize SQLAlchemy with the Flask application.

    The tables are created automatically when the application
    starts in development mode.
    """

    db.init_app(app)

    with app.app_context():
        # Ensure all models are imported so that SQLAlchemy knows about them
        from . import models
        db.create_all()


# ----------------------------------------------------------------------
# Close Database Session
# ----------------------------------------------------------------------

def close_db(exception=None):
    """
    Remove the current SQLAlchemy session.

    This can be registered with Flask's teardown mechanism.
    """

    db.session.remove()