"""
Code Service

Handles code sessions, source code persistence, execution status,
and code retrieval.

IMPORTANT:
This service does NOT execute arbitrary user code directly inside
the Flask application. Code execution should later be delegated
to an isolated sandbox/container.
"""

from datetime import datetime

from database.database import db
from database.models import CodeSession, Project


class CodeService:
    """Business logic for code sessions."""

    @staticmethod
    def get_session(session_id):
        """Return a code session by ID."""

        if not session_id:
            return None

        return db.session.get(CodeSession, int(session_id))

    @staticmethod
    def get_project_sessions(project_id):
        """Return all code sessions for a project."""

        if not project_id:
            return []

        return CodeSession.query.filter_by(
            project_id=int(project_id)
        ).order_by(
            CodeSession.updated_at.desc()
        ).all()

    @staticmethod
    def get_latest_session(project_id):
        """Return the most recently updated code session."""

        return CodeSession.query.filter_by(
            project_id=int(project_id)
        ).order_by(
            CodeSession.updated_at.desc()
        ).first()

    @staticmethod
    def create_session(
        project_id,
        title=None,
        filename=None,
        language=None,
        code="",
    ):
        """Create a new code session."""

        project = db.session.get(Project, int(project_id))

        if not project:
            raise ValueError("Project not found.")

        session = CodeSession(
            project_id=project.id,
            title=title or "Untitled Session",
            filename=filename,
            language=language,
            code=code or "",
            status="active",
        )

        db.session.add(session)

        project.updated_at = datetime.utcnow()

        db.session.commit()

        return session

    @staticmethod
    def save_code(
        session_id,
        code,
        filename=None,
        language=None,
    ):
        """Save code to an existing session."""

        session = CodeService.get_session(session_id)

        if not session:
            raise ValueError("Code session not found.")

        session.code = code or ""

        if filename is not None:
            session.filename = filename

        if language is not None:
            session.language = language

        session.updated_at = datetime.utcnow()

        if session.project:
            session.project.updated_at = datetime.utcnow()

        db.session.commit()

        return session

    @staticmethod
    def update_session(
        session_id,
        title=None,
        filename=None,
        language=None,
        code=None,
        status=None,
    ):
        """Update a code session."""

        session = CodeService.get_session(session_id)

        if not session:
            raise ValueError("Code session not found.")

        if title is not None:
            session.title = title

        if filename is not None:
            session.filename = filename

        if language is not None:
            session.language = language

        if code is not None:
            session.code = code

        if status is not None:
            session.status = status

        session.updated_at = datetime.utcnow()

        if session.project:
            session.project.updated_at = datetime.utcnow()

        db.session.commit()

        return session

    @staticmethod
    def set_execution_result(
        session_id,
        output=None,
        error=None,
        status="completed",
    ):
        """Store the result of sandboxed code execution."""

        session = CodeService.get_session(session_id)

        if not session:
            raise ValueError("Code session not found.")

        session.execution_output = output
        session.execution_error = error
        session.status = status
        session.updated_at = datetime.utcnow()

        db.session.commit()

        return session

    @staticmethod
    def delete_session(session_id):
        """Delete a code session."""

        session = CodeService.get_session(session_id)

        if not session:
            raise ValueError("Code session not found.")

        db.session.delete(session)
        db.session.commit()

        return True

    @staticmethod
    def get_code(session_id):
        """Return the source code for a session."""

        session = CodeService.get_session(session_id)

        if not session:
            raise ValueError("Code session not found.")

        return session.code or ""

    @staticmethod
    def get_session_context(session_id):
        """
        Return useful context for the AI engine.
        """

        session = CodeService.get_session(session_id)

        if not session:
            return None

        return {
            "session_id": session.id,
            "project_id": session.project_id,
            "filename": session.filename,
            "language": session.language,
            "code": session.code or "",
            "execution_output": session.execution_output,
            "execution_error": session.execution_error,
            "status": session.status,
        }