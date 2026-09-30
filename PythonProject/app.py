"""
AI Coding Teammate
==================

Main Flask application.

Combines:

- Flask
- Flask-Login
- Flask-SocketIO
- Database initialization
- Jinja2 templates
- AI coding services
- Real-time AI teammate communication
- Upload handling
- Logging
- Health monitoring
"""

import logging
import os
import uuid

from dotenv import load_dotenv

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from flask_login import LoginManager
from flask_socketio import SocketIO

from config import config
from database.database import init_db
from sockets import register_socket_events


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# EXTENSIONS
# ============================================================

login_manager = LoginManager()

# Socket.IO is created once here and initialized later
# inside create_app().
#
# Do not create another SocketIO instance anywhere else.
socketio = SocketIO(async_mode='threading')


# ============================================================
# FLASK-LOGIN CONFIGURATION
# ============================================================

login_manager.login_view = "auth.login"

login_manager.login_message = (
    "Please log in to access your workspace."
)

login_manager.login_message_category = "info"


# ============================================================
# FLASK-LOGIN USER LOADER
# ============================================================

@login_manager.user_loader
def load_user(user_id):
    """
    Reload an authenticated user from the database.

    Flask-Login stores the user's ID in the session.
    This callback converts that ID back into a User object.
    """

    if not user_id:
        return None

    try:
        user_id = int(user_id)

    except (TypeError, ValueError):
        return None

    try:
        # Local import helps prevent circular imports.
        from database.models import User

        return User.query.filter_by(
            id=user_id
        ).first()

    except Exception as error:
        logging.warning(
            "Unable to load user %s: %s",
            user_id,
            error,
        )

        return None


# ============================================================
# APPLICATION FACTORY
# ============================================================

def create_app(config_name=None):
    """
    Create and configure the Flask application.
    """

    # --------------------------------------------------------
    # Determine environment
    # --------------------------------------------------------

    if config_name is None:
        config_name = os.getenv(
            "FLASK_ENV",
            "development",
        )

    # --------------------------------------------------------
    # Create Flask application
    # --------------------------------------------------------

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    # --------------------------------------------------------
    # Load configuration
    # --------------------------------------------------------

    selected_config = config.get(
        config_name,
        config["default"],
    )

    app.config.from_object(
        selected_config
    )

    # --------------------------------------------------------
    # Testing configuration
    # --------------------------------------------------------

    if config_name == "testing":
        app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
        )

    # --------------------------------------------------------
    # Configure logging
    # --------------------------------------------------------

    configure_logging(app)

    # --------------------------------------------------------
    # Initialize database
    # --------------------------------------------------------

    init_db(app)

    # --------------------------------------------------------
    # Initialize Flask-Login
    # --------------------------------------------------------

    login_manager.init_app(app)

    # --------------------------------------------------------
    # Initialize Socket.IO
    # --------------------------------------------------------

    socketio.init_app(
        app,

        cors_allowed_origins=app.config.get(
            "SOCKETIO_CORS_ALLOWED_ORIGINS",
            "*",
        ),

        logger=app.config.get(
            "SOCKETIO_LOGGER",
            False,
        ),

        engineio_logger=app.config.get(
            "ENGINEIO_LOGGER",
            False,
        ),
    )

    # --------------------------------------------------------
    # Create required directories
    # --------------------------------------------------------

    create_directories(app)

    # --------------------------------------------------------
    # Register Flask blueprints
    # --------------------------------------------------------

    register_blueprints(app)

    # --------------------------------------------------------
    # Register Socket.IO events
    # --------------------------------------------------------
    #
    # IMPORTANT:
    #
    # This replaces the previous:
    #
    #     websocket/handlers.py
    #
    # registration system.
    #
    # sockets/__init__.py now registers:
    #
    # - workspace_events.py
    # - chat_events.py
    # - code_events.py
    # - screen_events.py
    # - camera_events.py
    #
    # Do this only once.
    # --------------------------------------------------------

    register_socket_events(
        socketio
    )

    app.logger.info(
        "Socket.IO event handlers registered."
    )

    # --------------------------------------------------------
    # Register error handlers
    # --------------------------------------------------------

    register_error_handlers(app)

    # --------------------------------------------------------
    # Register template context
    # --------------------------------------------------------

    register_template_context(app)

    # --------------------------------------------------------
    # Register core utility routes
    # --------------------------------------------------------

    register_core_routes(app)

    app.logger.info(
        "AI Coding Teammate application initialized."
    )

    return app


# ============================================================
# DIRECTORY SETUP
# ============================================================

def create_directories(app):
    """
    Create application directories if they do not
    already exist.
    """

    upload_folder = app.config.get(
        "UPLOAD_FOLDER",
        os.path.join(
            app.root_path,
            "uploads",
        ),
    )

    directories = [
        upload_folder,

        os.path.join(
            upload_folder,
            "code",
        ),

        os.path.join(
            upload_folder,
            "images",
        ),

        os.path.join(
            upload_folder,
            "videos",
        ),

        os.path.join(
            upload_folder,
            "screenshots",
        ),

        os.path.join(
            app.root_path,
            "projects",
        ),

        os.path.join(
            app.root_path,
            "logs",
        ),
    ]

    for directory in directories:
        os.makedirs(
            directory,
            exist_ok=True,
        )


# ============================================================
# BLUEPRINT REGISTRATION
# ============================================================

def register_blueprints(app):
    """
    Register all application blueprints.

    Imports remain inside this function to reduce
    circular-import problems.
    """

    # --------------------------------------------------------
    # Main routes
    # --------------------------------------------------------

    try:
        from routes.main_routes import main_bp

        app.register_blueprint(
            main_bp
        )

    except ImportError as error:
        app.logger.warning(
            "Main blueprint could not be loaded: %s",
            error,
        )

    # --------------------------------------------------------
    # Authentication routes
    # --------------------------------------------------------

    try:
        from routes.auth_routes import auth_bp

        app.register_blueprint(
            auth_bp
        )

    except ImportError as error:
        app.logger.warning(
            "Auth blueprint could not be loaded: %s",
            error,
        )

    # --------------------------------------------------------
    # Dashboard routes
    # --------------------------------------------------------

    try:
        from routes.dashboard_routes import dashboard_bp

        app.register_blueprint(
            dashboard_bp
        )

    except ImportError as error:
        app.logger.warning(
            "Dashboard blueprint could not be loaded: %s",
            error,
        )

    # --------------------------------------------------------
    # Workspace routes
    # --------------------------------------------------------

    try:
        from routes.workspace_routes import workspace_bp

        app.register_blueprint(
            workspace_bp
        )

    except ImportError as error:
        app.logger.warning(
            "Workspace blueprint could not be loaded: %s",
            error,
        )

    # --------------------------------------------------------
    # Project routes
    # --------------------------------------------------------

    try:
        from routes.project_routes import project_bp

        app.register_blueprint(
            project_bp
        )

    except ImportError as error:
        app.logger.warning(
            "Project blueprint could not be loaded: %s",
            error,
        )

    # --------------------------------------------------------
    # API routes
    # --------------------------------------------------------

    try:
        from routes.api_routes import api_bp

        app.register_blueprint(
            api_bp
        )

    except ImportError as error:
        app.logger.warning(
            "API blueprint could not be loaded: %s",
            error,
        )


# ============================================================
# ERROR HANDLERS
# ============================================================

def register_error_handlers(app):
    """
    Register application error handlers.
    """

    # --------------------------------------------------------
    # 404 - Page Not Found
    # --------------------------------------------------------

    @app.errorhandler(404)
    def page_not_found(error):

        return render_template(
            "errors/404.html"
        ), 404

    # --------------------------------------------------------
    # 500 - Internal Server Error
    # --------------------------------------------------------

    @app.errorhandler(500)
    def internal_server_error(error):

        error_id = str(
            uuid.uuid4()
        )[:8]

        app.logger.error(
            "Internal server error [%s]: %s",
            error_id,
            error,
        )

        # Roll back an unfinished database transaction
        # when possible.
        try:
            from database.database import db

            db.session.rollback()

        except Exception:
            pass

        return render_template(
            "errors/500.html",
            error_id=error_id,
        ), 500

    # --------------------------------------------------------
    # 413 - Upload Too Large
    # --------------------------------------------------------

    @app.errorhandler(413)
    def request_entity_too_large(error):

        if request.path.startswith(
            "/api/"
        ):
            return jsonify(
                {
                    "success": False,
                    "error": (
                        "Uploaded file is too large."
                    ),
                }
            ), 413

        flash(
            "The uploaded file is too large.",
            "danger",
        )

        return redirect(
            request.referrer
            or url_for(
                "main.index"
            )
        )


# ============================================================
# TEMPLATE CONTEXT
# ============================================================

def register_template_context(app):
    """
    Make common application values available
    automatically inside Jinja2 templates.
    """

    @app.context_processor
    def inject_app_config():

        return {
            "app_name": app.config.get(
                "APP_NAME",
                "AI Coding Teammate",
            ),

            "app_version": app.config.get(
                "APP_VERSION",
                "1.0.0",
            ),

            "ai_name": app.config.get(
                "AI_NAME",
                "AI Teammate",
            ),
        }


# ============================================================
# CORE ROUTES
# ============================================================

def register_core_routes(app):
    """
    Register application-level utility routes.
    """

    # --------------------------------------------------------
    # Health Check
    # --------------------------------------------------------

    @app.route(
        "/health"
    )
    def health_check():
        """
        Health endpoint for local development,
        Docker, deployment platforms, and monitoring.
        """

        return jsonify(
            {
                "status": "healthy",

                "application": app.config.get(
                    "APP_NAME",
                    "AI Coding Teammate",
                ),

                "version": app.config.get(
                    "APP_VERSION",
                    "1.0.0",
                ),
            }
        )

    # --------------------------------------------------------
    # API Health Alias
    # --------------------------------------------------------

    @app.route(
        "/api/health"
    )
    def api_health():

        return jsonify(
            {
                "success": True,
                "status": "healthy",
            }
        )

    # --------------------------------------------------------
    # API Status
    # --------------------------------------------------------

    @app.route(
        "/api/status"
    )
    def api_status():
        """
        Basic AI/API status endpoint.
        """

        return jsonify(
            {
                "success": True,
                "status": "online",

                "ai": {
                    "name": app.config.get(
                        "AI_NAME",
                        "AI Teammate",
                    ),

                    "status": "online",
                },
            }
        )


# ============================================================
# LOGGING
# ============================================================

def configure_logging(app):
    """
    Configure application logging.
    """

    log_level = (
        app.config.get(
            "LOG_LEVEL",
            "INFO",
        )
        .upper()
    )

    logging.basicConfig(
        level=getattr(
            logging,
            log_level,
            logging.INFO,
        ),

        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
    )


# ============================================================
# CREATE APPLICATION
# ============================================================

app = create_app()


# ============================================================
# DEVELOPMENT SERVER
# ============================================================

if __name__ == "__main__":

    host = os.getenv(
        "HOST",
        "127.0.0.1",
    )

    port = int(
        os.getenv(
            "PORT",
            "5001",
        )
    )

    debug_mode = app.config.get(
        "DEBUG",
        False,
    )

    socketio.run(
        app,
        host=host,
        port=port,
        debug=debug_mode,
        allow_unsafe_werkzeug=True,
        use_reloader=False,
    )