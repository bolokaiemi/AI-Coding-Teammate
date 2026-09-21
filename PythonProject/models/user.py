# ============================================================
# AI Coding Teammate
# models/users.py
#
# User database model
# ============================================================

from __future__ import annotations

from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)

from database.database import db


# ============================================================
# HELPERS
# ============================================================

def utc_now():
    """
    Return current timezone-aware UTC datetime.
    """
    return datetime.now(timezone.utc)


# ============================================================
# USER MODEL
# ============================================================

class User(UserMixin, db.Model):
    """
    Represents a registered AI Coding Teammate user.
    """

    __tablename__ = "users"

    # --------------------------------------------------------
    # PRIMARY KEY
    # --------------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    # --------------------------------------------------------
    # PERSONAL INFORMATION
    # --------------------------------------------------------

    first_name = db.Column(
        db.String(100),
        nullable=False,
    )

    last_name = db.Column(
        db.String(100),
        nullable=True,
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    occupation = db.Column(
        db.String(150),
        nullable=True,
    )

    # --------------------------------------------------------
    # PASSWORD
    # --------------------------------------------------------

    password_hash = db.Column(
        db.String(255),
        nullable=False,
    )

    # --------------------------------------------------------
    # ACCOUNT STATUS
    # --------------------------------------------------------

    is_verified = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    account_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    is_admin = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    # --------------------------------------------------------
    # AI SETTINGS
    # --------------------------------------------------------

    response_style = db.Column(
        db.String(50),
        nullable=False,
        default="balanced",
    )

    explanation_level = db.Column(
        db.String(50),
        nullable=False,
        default="intermediate",
    )

    auto_analysis = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    visual_explanations = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    # --------------------------------------------------------
    # NOTIFICATION SETTINGS
    # --------------------------------------------------------

    email_notifications = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    analysis_notifications = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    product_updates = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    # --------------------------------------------------------
    # ACCOUNT ACTIVITY
    # --------------------------------------------------------

    last_login_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
    )

    last_seen_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
    )

    # --------------------------------------------------------
    # TIMESTAMPS
    # --------------------------------------------------------

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    # --------------------------------------------------------
    # RELATIONSHIPS
    # --------------------------------------------------------

    projects = db.relationship(
        "Project",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan",
    )

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        first_name: str,
        username: str,
        email: str,
        password: str,
        last_name: str | None = None,
        occupation: str | None = None,
    ):
        self.first_name = first_name.strip()
        self.last_name = (
            last_name.strip()
            if last_name
            else None
        )

        self.username = username.strip().lower()
        self.email = email.strip().lower()
        self.occupation = occupation

        self.set_password(password)

    # ========================================================
    # PASSWORD MANAGEMENT
    # ========================================================

    def set_password(
        self,
        password: str,
    ):
        """
        Hash and store a new password.
        """

        if not password:
            raise ValueError(
                "Password cannot be empty."
            )

        if len(password) < 8:
            raise ValueError(
                "Password must contain at least 8 characters."
            )

        self.password_hash = generate_password_hash(
            password,
            method="pbkdf2:sha256",
        )

    def check_password(
        self,
        password: str,
    ) -> bool:
        """
        Verify a password against the stored hash.
        """

        if not password:
            return False

        return check_password_hash(
            self.password_hash,
            password,
        )

    # ========================================================
    # FLASK-LOGIN ACTIVE STATUS
    # ========================================================

    @property
    def is_active(self):
        """
        Flask-Login uses this property to determine whether
        the account can authenticate.
        """
        return bool(self.account_active)

    # ========================================================
    # DISPLAY NAME
    # ========================================================

    @property
    def full_name(self):
        """
        Return a readable full name.
        """

        parts = [
            self.first_name,
            self.last_name,
        ]

        return " ".join(
            part
            for part in parts
            if part
        )

    # ========================================================
    # LOGIN ACTIVITY
    # ========================================================

    def mark_login(self):
        """
        Mark successful login.
        """

        now = utc_now()

        self.last_login_at = now
        self.last_seen_at = now

    def update_last_seen(self):
        """
        Update last activity time.
        """

        self.last_seen_at = utc_now()

    # ========================================================
    # EMAIL VERIFICATION
    # ========================================================

    def verify_email(self):
        """
        Mark user email/account as verified.
        """

        self.is_verified = True

    # ========================================================
    # ACCOUNT ACTIVATION
    # ========================================================

    def activate_account(self):
        """
        Activate user account.
        """

        self.account_active = True

    def deactivate_account(self):
        """
        Disable user login without deleting account data.
        """

        self.account_active = False

    # ========================================================
    # AI SETTINGS
    # ========================================================

    def update_ai_settings(
        self,
        response_style: str | None = None,
        explanation_level: str | None = None,
        auto_analysis: bool | None = None,
        visual_explanations: bool | None = None,
    ):
        """
        Update AI teammate preferences.
        """

        allowed_response_styles = {
            "balanced",
            "concise",
            "detailed",
            "teaching",
        }

        allowed_explanation_levels = {
            "basic",
            "intermediate",
            "advanced",
        }

        if response_style:

            if response_style not in allowed_response_styles:
                raise ValueError(
                    "Invalid response style."
                )

            self.response_style = response_style

        if explanation_level:

            if explanation_level not in allowed_explanation_levels:
                raise ValueError(
                    "Invalid explanation level."
                )

            self.explanation_level = explanation_level

        if auto_analysis is not None:
            self.auto_analysis = bool(
                auto_analysis
            )

        if visual_explanations is not None:
            self.visual_explanations = bool(
                visual_explanations
            )

    # ========================================================
    # NOTIFICATION SETTINGS
    # ========================================================

    def update_notification_settings(
        self,
        email_notifications: bool | None = None,
        analysis_notifications: bool | None = None,
        product_updates: bool | None = None,
    ):
        """
        Update notification preferences.
        """

        if email_notifications is not None:
            self.email_notifications = bool(
                email_notifications
            )

        if analysis_notifications is not None:
            self.analysis_notifications = bool(
                analysis_notifications
            )

        if product_updates is not None:
            self.product_updates = bool(
                product_updates
            )

    # ========================================================
    # PROJECT COUNT
    # ========================================================

    @property
    def project_count(self):
        """
        Return number of projects belonging to user.
        """

        return len(
            self.projects
        )

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
        include_projects: bool = False,
        include_private: bool = False,
    ):
        """
        Convert user into JSON-compatible dictionary.
        """

        data = {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "username": self.username,
            "occupation": self.occupation,
            "is_verified": self.is_verified,
            "account_active": self.account_active,
            "response_style": self.response_style,
            "explanation_level": self.explanation_level,
            "auto_analysis": self.auto_analysis,
            "visual_explanations": (
                self.visual_explanations
            ),
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
            "updated_at": (
                self.updated_at.isoformat()
                if self.updated_at
                else None
            ),
            "last_login_at": (
                self.last_login_at.isoformat()
                if self.last_login_at
                else None
            ),
        }

        if include_private:

            data.update(
                {
                    "email": self.email,
                    "email_notifications": (
                        self.email_notifications
                    ),
                    "analysis_notifications": (
                        self.analysis_notifications
                    ),
                    "product_updates": (
                        self.product_updates
                    ),
                    "is_admin": self.is_admin,
                    "last_seen_at": (
                        self.last_seen_at.isoformat()
                        if self.last_seen_at
                        else None
                    ),
                }
            )

        if include_projects:

            data["projects"] = [
                project.to_dict(
                    include_files=False
                )
                for project in self.projects
            ]

        return data

    # ========================================================
    # REPRESENTATION
    # ========================================================

    def __repr__(self):
        return (
            f"<User "
            f"id={self.id} "
            f"username='{self.username}' "
            f"email='{self.email}'>"
        )