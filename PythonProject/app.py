import os
import uuid
import logging

from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    jsonify,
)

from flask_login import LoginManager
from flask_socketio import SocketIO
from dotenv import load_dotenv
from config import config
from database.database import init_db

# Initialize Flask extensions
login_manager = LoginManager()

socketio = SocketIO(async_mode='threading')


# ----------------------------------------------------------------------
# Load environment variables
# ----------------------------------------------------------------------

load_dotenv()



# --------------------------------------------------------------
# Initialize Extensions
# --------------------------------------------------------------

# Extension initialization moved to create_app

# ----------------------------------------------------------------------
# Application Factory
# ----------------------------------------------------------------------

def create_app(config_name=None):
    """
    Create and configure the Flask application.
    """

    if config_name is None:
        config_name = os.getenv(
            "FLASK_ENV",
            "development"
        )

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    # --------------------------------------------------------------
    # Configuration
    # --------------------------------------------------------------
    # Load configuration
    app.config.from_object(
        config.get(
            config_name,
            config["default"]
        )
    )

    # Initialize database
    init_db(app)


    # --------------------------------------------------------------
    # Initialize Extensions
    # --------------------------------------------------------------

    login_manager.init_app(app)

    socketio.init_app(
        app,
        cors_allowed_origins=app.config.get(
            "SOCKETIO_CORS_ALLOWED_ORIGINS",
            "*"
        ),
    )

    # --------------------------------------------------------------
    # Login Manager
    # --------------------------------------------------------------

    login_manager.login_view = "auth.login"

    login_manager.login_message = (
        "Please log in to access your workspace."
    )

    login_manager.login_message_category = "info"

    # --------------------------------------------------------------
    # Create Required Directories
    # --------------------------------------------------------------

    create_directories(app)

    # --------------------------------------------------------------
    # Register Blueprints
    # --------------------------------------------------------------

    register_blueprints(app)

    # --------------------------------------------------------------
    # Register WebSocket Handlers
    # --------------------------------------------------------------

    register_socket_handlers()

    # --------------------------------------------------------------
    # Error Handlers
    # --------------------------------------------------------------

    register_error_handlers(app)

    # --------------------------------------------------------------
    # Template Context
    # --------------------------------------------------------------

    register_template_context(app)

    # --------------------------------------------------------------
    # Application Routes
    # --------------------------------------------------------------

    register_core_routes(app)

    # --------------------------------------------------------------
    # Logging
    # --------------------------------------------------------------

    configure_logging(app)

    return app


# ----------------------------------------------------------------------
# Directory Setup
# ----------------------------------------------------------------------

def create_directories(app):
    """
    Create application directories if they do not already exist.
    """

    directories = [
        app.config["UPLOAD_FOLDER"],

        os.path.join(
            app.config["UPLOAD_FOLDER"],
            "code"
        ),

        os.path.join(
            app.config["UPLOAD_FOLDER"],
            "images"
        ),

        os.path.join(
            app.config["UPLOAD_FOLDER"],
            "videos"
        ),

        os.path.join(
            app.config["UPLOAD_FOLDER"],
            "screenshots"
        ),

        os.path.join(
            app.root_path,
            "projects"
        ),

        os.path.join(
            app.root_path,
            "logs"
        ),
    ]

    for directory in directories:
        os.makedirs(
            directory,
            exist_ok=True
        )


# ----------------------------------------------------------------------
# Blueprint Registration
# ----------------------------------------------------------------------

def register_blueprints(app):
    """
    Register all application blueprints.

    Blueprints are imported inside this function to avoid circular
    imports during application startup.
    """

    try:
        from routes.main_routes import main_bp
        app.register_blueprint(main_bp)

    except ImportError as error:
        app.logger.warning(
            "Main blueprint could not be loaded: %s",
            error
        )

    try:
        from routes.auth_routes import auth_bp
        app.register_blueprint(auth_bp)

    except ImportError as error:
        app.logger.warning(
            "Auth blueprint could not be loaded: %s",
            error
        )

    try:
        from routes.dashboard_routes import dashboard_bp
        app.register_blueprint(dashboard_bp)

    except ImportError as error:
        app.logger.warning(
            "Dashboard blueprint could not be loaded: %s",
            error
        )

    try:
        from routes.workspace_routes import workspace_bp
        app.register_blueprint(workspace_bp)

    except ImportError as error:
        app.logger.warning(
            "Workspace blueprint could not be loaded: %s",
            error
        )

    try:
        from routes.project_routes import project_bp
        app.register_blueprint(project_bp)

    except ImportError as error:
        app.logger.warning(
            "Project blueprint could not be loaded: %s",
            error
        )

    try:
        from routes.api_routes import api_bp
        app.register_blueprint(api_bp)

    except ImportError as error:
        app.logger.warning(
            "API blueprint could not be loaded: %s",
            error
        )


# ----------------------------------------------------------------------
# WebSocket Registration
# ----------------------------------------------------------------------

def register_socket_handlers():
    """
    Register real-time WebSocket handlers.

    The actual handlers live inside websocket/handlers.py and related
    modules.
    """

    try:
        from websocket.handlers import register_handlers

        register_handlers(socketio)

        logging.info(
            "WebSocket handlers registered successfully."
        )

    except ImportError as error:
        logging.warning(
            "WebSocket handlers could not be loaded: %s",
            error
        )


# ----------------------------------------------------------------------
# Error Handlers
# ----------------------------------------------------------------------

def register_error_handlers(app):

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template(
            "errors/404.html"
        ), 404

    @app.errorhandler(500)
    def internal_server_error(error):

        error_id = str(uuid.uuid4())[:8]

        app.logger.error(
            "Internal server error [%s]: %s",
            error_id,
            error,
        )

        return render_template(
            "errors/500.html",
            error_id=error_id,
        ), 500

    @app.errorhandler(413)
    def request_entity_too_large(error):

        if request.path.startswith("/api/"):
            return jsonify({
                "success": False,
                "error": "Uploaded file is too large."
            }), 413

        flash(
            "The uploaded file is too large.",
            "danger"
        )

        return redirect(
            request.referrer or url_for("main.index")
        )


# ----------------------------------------------------------------------
# Template Context
# ----------------------------------------------------------------------

def register_template_context(app):

    @app.context_processor
    def inject_app_config():

        return {
            "app_name": app.config["APP_NAME"],
            "app_version": app.config["APP_VERSION"],
            "ai_name": app.config["AI_NAME"],
        }


# ----------------------------------------------------------------------
# Core Routes
# ----------------------------------------------------------------------

def register_core_routes(app):

    @app.route("/health")
    def health_check():
        """
        Health-check endpoint useful for development,
        Docker, deployment platforms, and monitoring.
        """

        return jsonify({
            "status": "healthy",
            "application": app.config["APP_NAME"],
            "version": app.config["APP_VERSION"],
        })

    @app.route("/api/status")
    def api_status():
        """
        Basic API status endpoint.
        """

        return jsonify({
            "success": True,
            "status": "online",
            "ai": {
                "name": app.config["AI_NAME"],
                "status": "online",
            },
        })


# ----------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------

def configure_logging(app):

    log_level = app.config.get(
        "LOG_LEVEL",
        "INFO"
    ).upper()

    logging.basicConfig(
        level=getattr(
            logging,
            log_level,
            logging.INFO
        ),
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
    )


# ----------------------------------------------------------------------
# Flask-Login User Loader
# ----------------------------------------------------------------------

@login_manager.user_loader
def load_user(user_id):
    """
    Load a user from the database for Flask-Login.

    The User model is imported here rather than at module level
    to avoid circular imports during application initialization.
    """

    try:
        from database.models import User

        return User.query.get(int(user_id))

    except (ImportError, ValueError, TypeError) as error:

        logging.warning(
            "Unable to load user %s: %s",
            user_id,
            error
        )

        return None


# ----------------------------------------------------------------------
# Create Application
# ----------------------------------------------------------------------

app = create_app()


# ----------------------------------------------------------------------
# Development Server
# ----------------------------------------------------------------------

if __name__ == "__main__":

    socketio.run(

        app,
        allow_unsafe_werkzeug=True,
        host=os.getenv(
            "HOST",
            "127.0.0.1"
        ),
        port=int(
            os.getenv(
                "PORT",
                "5001"
            )
        ),
        debug=app.config.get(
            "DEBUG",
            False
        ),
    )