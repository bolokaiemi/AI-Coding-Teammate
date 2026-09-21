"""
AI Coding Teammate
Database Models

Database models for:

    User
    Project
    CodeSession
    Conversation
    Analysis

Relationships:

    User
        └── Projects
              ├── Code Sessions
              │      └── Analysis Results
              │
              └── Conversations
"""

from datetime import datetime

from flask_login import UserMixin

from database.database import db


# ======================================================================
# USER
# ======================================================================

class User(UserMixin, db.Model):
    """
    Application user.

    A user can own multiple projects.
    """

    __tablename__ = "users"

    # ------------------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ------------------------------------------------------------------
    # Personal Information
    # ------------------------------------------------------------------

    first_name = db.Column(
        db.String(100),
        nullable=False
    )

    last_name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
        index=True
    )

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    password = db.Column(
        db.String(255),
        nullable=False
    )

    # ------------------------------------------------------------------
    # Profile
    # ------------------------------------------------------------------

    occupation = db.Column(
        db.String(150),
        nullable=True
    )

    bio = db.Column(
        db.Text,
        nullable=True
    )

    profile_image = db.Column(
        db.String(500),
        nullable=True
    )

    # ------------------------------------------------------------------
    # Account Status
    # ------------------------------------------------------------------

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    is_verified = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    # ------------------------------------------------------------------
    # Timestamps
    # ------------------------------------------------------------------

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    last_login = db.Column(
        db.DateTime,
        nullable=True
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    projects = db.relationship(
        "Project",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy=True
    )

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self):
        return (
            f"<User {self.id}: "
            f"{self.email}>"
        )

    @property
    def full_name(self):
        """
        Return the user's full name.
        """

        return (
            f"{self.first_name} "
            f"{self.last_name}"
        ).strip()


# ======================================================================
# PROJECT
# ======================================================================

class Project(db.Model):
    """
    Developer project.

    Each project belongs to one user and can contain multiple
    coding sessions and conversations.
    """

    __tablename__ = "projects"

    # ------------------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ------------------------------------------------------------------
    # User Relationship
    # ------------------------------------------------------------------

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    user = db.relationship(
        "User",
        back_populates="projects"
    )

    # ------------------------------------------------------------------
    # Project Information
    # ------------------------------------------------------------------

    name = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    language = db.Column(
        db.String(100),
        nullable=True
    )

    framework = db.Column(
        db.String(100),
        nullable=True
    )

    repository_url = db.Column(
        db.String(500),
        nullable=True
    )

    # ------------------------------------------------------------------
    # Project Status
    # ------------------------------------------------------------------

    status = db.Column(
        db.String(50),
        default="active",
        nullable=False
    )

    # ------------------------------------------------------------------
    # Timestamps
    # ------------------------------------------------------------------

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    code_sessions = db.relationship(
        "CodeSession",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy=True
    )

    conversations = db.relationship(
        "Conversation",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy=True
    )

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self):
        return (
            f"<Project {self.id}: "
            f"{self.name}>"
        )


# ======================================================================
# CODE SESSION
# ======================================================================

class CodeSession(db.Model):
    """
    Coding/debugging session.

    A project can contain many coding sessions.

    A session represents a period where the developer works
    with the AI Coding Teammate.
    """

    __tablename__ = "code_sessions"

    # ------------------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ------------------------------------------------------------------
    # Project Relationship
    # ------------------------------------------------------------------

    project_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "projects.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    project = db.relationship(
        "Project",
        back_populates="code_sessions"
    )

    # ------------------------------------------------------------------
    # Session Information
    # ------------------------------------------------------------------

    title = db.Column(
        db.String(200),
        nullable=True
    )

    filename = db.Column(
        db.String(255),
        nullable=True
    )

    language = db.Column(
        db.String(100),
        nullable=True
    )

    code = db.Column(
        db.Text,
        nullable=True
    )

    # ------------------------------------------------------------------
    # Execution Information
    # ------------------------------------------------------------------

    execution_output = db.Column(
        db.Text,
        nullable=True
    )

    execution_error = db.Column(
        db.Text,
        nullable=True
    )

    execution_status = db.Column(
        db.String(50),
        nullable=True
    )

    # ------------------------------------------------------------------
    # Session Status
    # ------------------------------------------------------------------

    status = db.Column(
        db.String(50),
        default="active",
        nullable=False
    )

    # ------------------------------------------------------------------
    # Timestamps
    # ------------------------------------------------------------------

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    analyses = db.relationship(
        "Analysis",
        back_populates="code_session",
        cascade="all, delete-orphan",
        lazy=True
    )

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self):
        return (
            f"<CodeSession {self.id}: "
            f"{self.filename}>"
        )


# ======================================================================
# CONVERSATION
# ======================================================================

class Conversation(db.Model):
    """
    AI teammate conversation.

    Stores messages between the developer and the AI.

    Example:

        User:
            Why is this function returning None?

        AI:
            The function does not have a return statement...
    """

    __tablename__ = "conversations"

    # ------------------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ------------------------------------------------------------------
    # Project Relationship
    # ------------------------------------------------------------------

    project_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "projects.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    project = db.relationship(
        "Project",
        back_populates="conversations"
    )

    # ------------------------------------------------------------------
    # Conversation Data
    # ------------------------------------------------------------------

    role = db.Column(
        db.String(30),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    # ------------------------------------------------------------------
    # Optional Context
    # ------------------------------------------------------------------

    code_context = db.Column(
        db.Text,
        nullable=True
    )

    filename = db.Column(
        db.String(255),
        nullable=True
    )

    line_number = db.Column(
        db.Integer,
        nullable=True
    )

    # ------------------------------------------------------------------
    # Message Metadata
    # ------------------------------------------------------------------

    message_type = db.Column(
        db.String(50),
        default="text",
        nullable=False
    )

    # Possible values:

    # text
    # code
    # error
    # correction
    # explanation
    # screen
    # camera
    # voice

    # ------------------------------------------------------------------
    # Timestamps
    # ------------------------------------------------------------------

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self):
        return (
            f"<Conversation {self.id}: "
            f"{self.role}>"
        )


# ======================================================================
# ANALYSIS
# ======================================================================

class Analysis(db.Model):
    """
    AI code/visual analysis result.

    Each analysis belongs to a CodeSession.

    This is where the AI Visualizer's findings can be persisted.
    """

    __tablename__ = "analysis_results"

    # ------------------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ------------------------------------------------------------------
    # Code Session Relationship
    # ------------------------------------------------------------------

    code_session_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "code_sessions.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    code_session = db.relationship(
        "CodeSession",
        back_populates="analyses"
    )

    # ------------------------------------------------------------------
    # Analysis Type
    # ------------------------------------------------------------------

    analysis_type = db.Column(
        db.String(50),
        nullable=False,
        default="code"
    )

    # Possible values:

    # code
    # screen
    # camera
    # image
    # video
    # runtime
    # security
    # performance

    # ------------------------------------------------------------------
    # Analysis Status
    # ------------------------------------------------------------------

    status = db.Column(
        db.String(50),
        nullable=False,
        default="completed"
    )

    # Possible values:

    # pending
    # processing
    # completed
    # failed

    # ------------------------------------------------------------------
    # Error Information
    # ------------------------------------------------------------------

    error_count = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    warning_count = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    errors = db.Column(
        db.JSON,
        nullable=True
    )

    warnings = db.Column(
        db.JSON,
        nullable=True
    )

    suggestions = db.Column(
        db.JSON,
        nullable=True
    )

    # ------------------------------------------------------------------
    # AI Explanation
    # ------------------------------------------------------------------

    summary = db.Column(
        db.Text,
        nullable=True
    )

    explanation = db.Column(
        db.Text,
        nullable=True
    )

    # ------------------------------------------------------------------
    # Code Correction
    # ------------------------------------------------------------------

    original_code = db.Column(
        db.Text,
        nullable=True
    )

    corrected_code = db.Column(
        db.Text,
        nullable=True
    )

    correction_explanation = db.Column(
        db.Text,
        nullable=True
    )

    # ------------------------------------------------------------------
    # Visualizer Information
    # ------------------------------------------------------------------

    visual_data = db.Column(
        db.JSON,
        nullable=True
    )

    code_flow = db.Column(
        db.JSON,
        nullable=True
    )

    highlighted_lines = db.Column(
        db.JSON,
        nullable=True
    )

    # ------------------------------------------------------------------
    # AI Metadata
    # ------------------------------------------------------------------

    model_name = db.Column(
        db.String(150),
        nullable=True
    )

    processing_time = db.Column(
        db.Float,
        nullable=True
    )

    # ------------------------------------------------------------------
    # Timestamps
    # ------------------------------------------------------------------

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    completed_at = db.Column(
        db.DateTime,
        nullable=True
    )

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self):
        return (
            f"<Analysis {self.id}: "
            f"{self.analysis_type}>"
        )