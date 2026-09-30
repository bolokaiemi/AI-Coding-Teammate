"""
Project Service

Handles project creation, retrieval, updating, deletion, and ownership.
"""

from datetime import datetime

from database.database import db
from database.models import Project


class ProjectService:
    """Business logic for projects."""

    @staticmethod
    def get_by_id(project_id):
        """Return a project by ID."""
        if not project_id:
            return None

        return db.session.get(Project, int(project_id))

    @staticmethod
    def get_user_project(project_id, user_id):
        """Return a project only if it belongs to the specified user."""

        if not project_id or not user_id:
            return None

        return Project.query.filter_by(
            id=int(project_id),
            user_id=int(user_id),
        ).first()

    @staticmethod
    def get_user_projects(user_id):
        """Return all projects belonging to a user."""

        if not user_id:
            return []

        return Project.query.filter_by(
            user_id=int(user_id)
        ).order_by(
            Project.updated_at.desc()
        ).all()

    @staticmethod
    def create_project(
        user_id,
        name,
        description=None,
        language=None,
        framework=None,
        repository_url=None,
    ):
        """Create a new project."""

        if not user_id:
            raise ValueError("User ID is required.")

        if not name or not name.strip():
            raise ValueError("Project name is required.")

        project = Project(
            user_id=int(user_id),
            name=name.strip(),
            description=description.strip() if description else None,
            language=language.strip() if language else None,
            framework=framework.strip() if framework else None,
            repository_url=(
                repository_url.strip()
                if repository_url
                else None
            ),
        )

        db.session.add(project)
        db.session.commit()

        return project

    @staticmethod
    def update_project(
        project_id,
        user_id,
        name=None,
        description=None,
        language=None,
        framework=None,
        repository_url=None,
        status=None,
    ):
        """Update a project belonging to a user."""

        project = ProjectService.get_user_project(
            project_id,
            user_id,
        )

        if not project:
            raise ValueError("Project not found.")

        if name is not None:
            if not name.strip():
                raise ValueError("Project name cannot be empty.")

            project.name = name.strip()

        if description is not None:
            project.description = description.strip()

        if language is not None:
            project.language = language.strip()

        if framework is not None:
            project.framework = framework.strip()

        if repository_url is not None:
            project.repository_url = repository_url.strip()

        if status is not None:
            project.status = status.strip()

        project.updated_at = datetime.utcnow()

        db.session.commit()

        return project

    @staticmethod
    def delete_project(project_id, user_id):
        """Delete a project belonging to a user."""

        project = ProjectService.get_user_project(
            project_id,
            user_id,
        )

        if not project:
            raise ValueError("Project not found.")

        db.session.delete(project)
        db.session.commit()

        return True

    @staticmethod
    def get_latest_project(user_id):
        """Return the user's most recently updated project."""

        return Project.query.filter_by(
            user_id=int(user_id)
        ).order_by(
            Project.updated_at.desc()
        ).first()

    @staticmethod
    def search_projects(user_id, search_term):
        """Search a user's projects by name or description."""

        query = Project.query.filter_by(
            user_id=int(user_id)
        )

        if search_term:
            search_term = search_term.strip()

            if search_term:
                pattern = f"%{search_term}%"

                query = query.filter(
                    db.or_(
                        Project.name.ilike(pattern),
                        Project.description.ilike(pattern),
                    )
                )

        return query.order_by(
            Project.updated_at.desc()
        ).all()