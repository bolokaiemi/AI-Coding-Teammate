import os
from datetime import timedelta

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class Config:
    """Base configuration for the AI Coding Teammate application."""

    # ------------------------------------------------------------------
    # Flask
    # ------------------------------------------------------------------

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "change-this-secret-key-in-production"
    )

    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

    TESTING = False

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "ai_coding_teammate.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ------------------------------------------------------------------
    # Session
    # ------------------------------------------------------------------

    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Set to True when running behind HTTPS in production.
    SESSION_COOKIE_SECURE = (
        os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"
    )

    # ------------------------------------------------------------------
    # File Uploads
    # ------------------------------------------------------------------

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB

    ALLOWED_CODE_EXTENSIONS = {
        "py",
        "js",
        "ts",
        "jsx",
        "tsx",
        "html",
        "htm",
        "css",
        "scss",
        "sass",
        "json",
        "xml",
        "yaml",
        "yml",
        "sql",
        "sh",
        "bash",
        "java",
        "c",
        "cpp",
        "h",
        "hpp",
        "cs",
        "go",
        "rs",
        "php",
        "rb",
        "swift",
        "kt",
        "md",
        "txt",
    }

    ALLOWED_IMAGE_EXTENSIONS = {
        "png",
        "jpg",
        "jpeg",
        "gif",
        "webp",
        "bmp",
    }

    ALLOWED_VIDEO_EXTENSIONS = {
        "mp4",
        "webm",
        "mov",
        "avi",
        "mkv",
    }

    # ------------------------------------------------------------------
    # AI Configuration
    # ------------------------------------------------------------------

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    AI_MODEL = os.getenv(
        "AI_MODEL",
        "gpt-4o"
    )

    AI_TEMPERATURE = float(
        os.getenv("AI_TEMPERATURE", "0.2")
    )

    AI_MAX_TOKENS = int(
        os.getenv("AI_MAX_TOKENS", "4096")
    )

    # ------------------------------------------------------------------
    # AI Behaviour
    # ------------------------------------------------------------------

    AI_NAME = os.getenv(
        "AI_NAME",
        "AI Coding Teammate"
    )

    AI_RESPONSE_STYLE = os.getenv(
        "AI_RESPONSE_STYLE",
        "professional"
    )

    AI_EXPLANATION_LEVEL = os.getenv(
        "AI_EXPLANATION_LEVEL",
        "detailed"
    )

    # ------------------------------------------------------------------
    # WebSocket / Real-Time Configuration
    # ------------------------------------------------------------------

    SOCKETIO_ASYNC_MODE = os.getenv(
        "SOCKETIO_ASYNC_MODE",
        "threading"
    )

    SOCKETIO_CORS_ALLOWED_ORIGINS = os.getenv(
        "SOCKETIO_CORS_ALLOWED_ORIGINS",
        "*"
    )

    # ------------------------------------------------------------------
    # Security
    # ------------------------------------------------------------------

    PASSWORD_MIN_LENGTH = 8

    # ------------------------------------------------------------------
    # Email
    # ------------------------------------------------------------------

    MAIL_SERVER = os.getenv("MAIL_SERVER", "")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = (
        os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    )

    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv(
        "MAIL_DEFAULT_SENDER",
        ""
    )

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------

    APP_NAME = "AI Coding Teammate"

    APP_VERSION = "1.0.0"

    # ------------------------------------------------------------------
    # JSON
    # ------------------------------------------------------------------

    JSON_SORT_KEYS = False

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    LOG_LEVEL = os.getenv(
        "LOG_LEVEL",
        "INFO"
    )


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    DEBUG = False

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    TESTING = False

    SESSION_COOKIE_SECURE = True


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}