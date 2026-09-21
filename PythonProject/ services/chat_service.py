"""
Chat Service

Handles conversations between the developer and the AI Coding Teammate.
"""

from database.database import db
from database.models import Conversation, Project


class ChatService:
    """Business logic for AI conversations."""

    @staticmethod
    def get_message(message_id):
        """Return a conversation message by ID."""

        if not message_id:
            return None

        return db.session.get(
            Conversation,
            int(message_id)
        )

    @staticmethod
    def get_project_messages(project_id, limit=100):
        """Return recent conversation messages."""

        if not project_id:
            return []

        return Conversation.query.filter_by(
            project_id=int(project_id)
        ).order_by(
            Conversation.created_at.asc()
        ).limit(limit).all()

    @staticmethod
    def add_message(
        project_id,
        role,
        message,
        code_context=None,
        filename=None,
        line_number=None,
        message_type="text",
    ):
        """Add a message to a project conversation."""

        project = db.session.get(Project, int(project_id))

        if not project:
            raise ValueError("Project not found.")

        if role not in {"user", "assistant", "system"}:
            raise ValueError("Invalid conversation role.")

        if not message or not message.strip():
            raise ValueError("Message cannot be empty.")

        conversation = Conversation(
            project_id=project.id,
            role=role,
            message=message.strip(),
            code_context=code_context,
            filename=filename,
            line_number=line_number,
            message_type=message_type or "text",
        )

        db.session.add(conversation)
        db.session.commit()

        return conversation

    @staticmethod
    def add_user_message(
        project_id,
        message,
        code_context=None,
        filename=None,
        line_number=None,
        message_type="text",
    ):
        """Store a developer message."""

        return ChatService.add_message(
            project_id=project_id,
            role="user",
            message=message,
            code_context=code_context,
            filename=filename,
            line_number=line_number,
            message_type=message_type,
        )

    @staticmethod
    def add_ai_message(
        project_id,
        message,
        code_context=None,
        filename=None,
        line_number=None,
        message_type="text",
    ):
        """Store an AI teammate response."""

        return ChatService.add_message(
            project_id=project_id,
            role="assistant",
            message=message,
            code_context=code_context,
            filename=filename,
            line_number=line_number,
            message_type=message_type,
        )

    @staticmethod
    def get_recent_context(project_id, limit=20):
        """
        Return conversation history in a format suitable for an AI model.
        """

        messages = ChatService.get_project_messages(
            project_id,
            limit=limit,
        )

        return [
            {
                "role": message.role,
                "content": message.message,
            }
            for message in messages
        ]

    @staticmethod
    def clear_project_chat(project_id):
        """Delete all conversation messages for a project."""

        messages = Conversation.query.filter_by(
            project_id=int(project_id)
        ).all()

        for message in messages:
            db.session.delete(message)

        db.session.commit()

        return True