# ============================================================
# AI Coding Teammate
# models/project.py
#
# Project database model
# ============================================================

from __future__ import annotations

from datetime import datetime, timezone

from database.database import db


# ============================================================
# HELPER
# ============================================================

def utc_now():
    """
    Return timezone-aware UTC datetime.
    """
    return datetime.now(timezone.utc)


# ============================================================
# PROJECT MODEL
# ============================================================

class Project(db.Model):
    """
    Represents a developer project inside AI Coding Teammate.
    """

    __tablename__ = "projects"

    # --------------------------------------------------------
    # PRIMARY KEY
    # --------------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    # --------------------------------------------------------
    # OWNER
    # --------------------------------------------------------

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # --------------------------------------------------------
    # PROJECT INFORMATION
    # --------------------------------------------------------

    name = db.Column(
        db.String(150),
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=True,
    )

    language = db.Column(
        db.String(50),
        nullable=True,
        default="Python",
    )

    framework = db.Column(
        db.String(100),
        nullable=True,
    )

    # --------------------------------------------------------
    # PROJECT PATH
    # --------------------------------------------------------

    project_path = db.Column(
        db.String(500),
        nullable=True,
    )

    # --------------------------------------------------------
    # PROJECT STATUS
    # --------------------------------------------------------

    status = db.Column(
        db.String(30),
        nullable=False,
        default="active",
        index=True,
    )

    is_archived = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    is_favorite = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    # --------------------------------------------------------
    # AI PROJECT SETTINGS
    # --------------------------------------------------------

    ai_memory_enabled = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    auto_analysis_enabled = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    visual_explanations_enabled = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    file_count = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    analysis_count = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    session_count = db.Column(
        db.Integer,
        nullable=False,
        default=0,
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

    last_opened_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
    )

    # --------------------------------------------------------
    # RELATIONSHIPS
    # --------------------------------------------------------

    files = db.relationship(
        "ProjectFile",
        backref="project",
        lazy=True,
        cascade="all, delete-orphan",
    )

    sessions = db.relationship(
        "CodingSession",
        backref="project",
        lazy=True,
        cascade="all, delete-orphan",
    )

    analyses = db.relationship(
        "CodeAnalysis",
        backref="project",
        lazy=True,
        cascade="all, delete-orphan",
    )

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        user_id: int,
        name: str,
        description: str | None = None,
        language: str | None = "Python",
        framework: str | None = None,
        project_path: str | None = None,
    ):

        self.user_id = user_id
        self.name = name
        self.description = description
        self.language = language
        self.framework = framework
        self.project_path = project_path

    # ========================================================
    # MARK PROJECT OPENED
    # ========================================================

    def mark_opened(self):
        """
        Update the time this project was last opened.
        """

        self.last_opened_at = utc_now()

    # ========================================================
    # ARCHIVE PROJECT
    # ========================================================

    def archive(self):
        """
        Archive the project.
        """

        self.is_archived = True
        self.status = "archived"

    # ========================================================
    # RESTORE PROJECT
    # ========================================================

    def restore(self):
        """
        Restore an archived project.
        """

        self.is_archived = False
        self.status = "active"

    # ========================================================
    # FAVORITE
    # ========================================================

    def favorite(self):
        """
        Mark project as favorite.
        """

        self.is_favorite = True

    def unfavorite(self):
        """
        Remove project from favorites.
        """

        self.is_favorite = False

    # ========================================================
    # STAT COUNTERS
    # ========================================================

    def increment_file_count(self):
        self.file_count += 1

    def decrement_file_count(self):

        if self.file_count > 0:
            self.file_count -= 1

    def increment_analysis_count(self):
        self.analysis_count += 1

    def increment_session_count(self):
        self.session_count += 1

    # ========================================================
    # SERIALIZE
    # ========================================================

    def to_dict(
        self,
        include_files: bool = False,
    ):
        """
        Convert project into a JSON-compatible dictionary.
        """

        data = {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "language": self.language,
            "framework": self.framework,
            "project_path": self.project_path,
            "status": self.status,
            "is_archived": self.is_archived,
            "is_favorite": self.is_favorite,
            "ai_memory_enabled": self.ai_memory_enabled,
            "auto_analysis_enabled": self.auto_analysis_enabled,
            "visual_explanations_enabled": (
                self.visual_explanations_enabled
            ),
            "file_count": self.file_count,
            "analysis_count": self.analysis_count,
            "session_count": self.session_count,
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
            "last_opened_at": (
                self.last_opened_at.isoformat()
                if self.last_opened_at
                else None
            ),
        }

        if include_files:

            data["files"] = [
                file.to_dict()
                for file in self.files
            ]

        return data

    # ========================================================
    # REPRESENTATION
    # ========================================================

    def __repr__(self):
        return (
            f"<Project "
            f"id={self.id} "
            f"name='{self.name}' "
            f"user_id={self.user_id}>"
        )


# ============================================================
# PROJECT FILE MODEL
# ============================================================

class ProjectFile(db.Model):
    """
    Represents a file or folder inside a project.
    """

    __tablename__ = "project_files"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    project_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "projects.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    name = db.Column(
        db.String(255),
        nullable=False,
    )

    path = db.Column(
        db.String(500),
        nullable=True,
    )

    content = db.Column(
        db.Text,
        nullable=True,
        default="",
    )

    language = db.Column(
        db.String(50),
        nullable=True,
    )

    extension = db.Column(
        db.String(20),
        nullable=True,
    )

    is_folder = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    parent_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "project_files.id",
            ondelete="CASCADE",
        ),
        nullable=True,
    )

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

    children = db.relationship(
        "ProjectFile",
        backref=db.backref(
            "parent",
            remote_side=[id],
        ),
        lazy=True,
        cascade="all, delete-orphan",
    )

    # ========================================================
    # SERIALIZE FILE
    # ========================================================

    def to_dict(
        self,
        include_content: bool = True,
    ):

        data = {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "path": self.path,
            "language": self.language,
            "extension": self.extension,
            "is_folder": self.is_folder,
            "parent_id": self.parent_id,
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
        }

        if include_content:
            data["content"] = self.content

        return data

    def __repr__(self):

        return (
            f"<ProjectFile "
            f"id={self.id} "
            f"name='{self.name}' "
            f"project_id={self.project_id}>"
        )