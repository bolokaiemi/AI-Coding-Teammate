# ============================================================
# AI Coding Teammate
# handlers.py
# Application Error Handlers
# ============================================================

import logging
import uuid

from flask import render_template, request


# ============================================================
# LOGGER
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# REGISTER ERROR HANDLERS
# ============================================================

def register_error_handlers(app):
    """
    Register all custom application error handlers.

    Usage in app.py:

        from handlers import register_error_handlers

        register_error_handlers(app)
    """

    # ========================================================
    # 400 - BAD REQUEST
    # ========================================================

    @app.errorhandler(400)
    def bad_request(error):
        logger.warning(
            "400 Bad Request: %s %s",
            request.method,
            request.path,
        )

        return render_template(
            "errors/404.html"
        ), 400


    # ========================================================
    # 401 - UNAUTHORIZED
    # ========================================================

    @app.errorhandler(401)
    def unauthorized(error):
        logger.warning(
            "401 Unauthorized: %s %s",
            request.method,
            request.path,
        )

        return render_template(
            "errors/404.html"
        ), 401


    # ========================================================
    # 403 - FORBIDDEN
    # ========================================================

    @app.errorhandler(403)
    def forbidden(error):
        logger.warning(
            "403 Forbidden: %s %s",
            request.method,
            request.path,
        )

        return render_template(
            "errors/404.html"
        ), 403


    # ========================================================
    # 404 - PAGE NOT FOUND
    # ========================================================

    @app.errorhandler(404)
    def page_not_found(error):
        logger.info(
            "404 Page Not Found: %s %s",
            request.method,
            request.path,
        )

        return render_template(
            "errors/404.html"
        ), 404


    # ========================================================
    # 405 - METHOD NOT ALLOWED
    # ========================================================

    @app.errorhandler(405)
    def method_not_allowed(error):
        logger.warning(
            "405 Method Not Allowed: %s %s",
            request.method,
            request.path,
        )

        return render_template(
            "errors/404.html"
        ), 405


    # ========================================================
    # 413 - FILE TOO LARGE
    # ========================================================

    @app.errorhandler(413)
    def request_entity_too_large(error):
        logger.warning(
            "413 File Too Large: %s %s",
            request.method,
            request.path,
        )

        return render_template(
            "errors/500.html",
            error_id="UPLOAD_TOO_LARGE",
        ), 413


    # ========================================================
    # 500 - INTERNAL SERVER ERROR
    # ========================================================

    @app.errorhandler(500)
    def internal_server_error(error):

        error_id = str(uuid.uuid4())[:8].upper()

        logger.exception(
            "500 Internal Server Error "
            "[Error ID: %s] "
            "Method: %s "
            "Path: %s",
            error_id,
            request.method,
            request.path,
        )

        return render_template(
            "errors/500.html",
            error_id=error_id,
        ), 500


    # ========================================================
    # GENERIC EXCEPTION HANDLER
    # ========================================================

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):

        # ----------------------------------------------------
        # Preserve HTTP exceptions such as 404 / 403 / 405
        # ----------------------------------------------------

        if hasattr(error, "code") and error.code:
            return error

        error_id = str(uuid.uuid4())[:8].upper()

        logger.exception(
            "Unhandled Exception "
            "[Error ID: %s] "
            "Method: %s "
            "Path: %s "
            "Error: %s",
            error_id,
            request.method,
            request.path,
            str(error),
        )

        return render_template(
            "errors/500.html",
            error_id=error_id,
        ), 500