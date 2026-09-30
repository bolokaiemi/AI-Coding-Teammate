"""
AI Conversation Manager

Maintains AI conversation context and prepares messages for the
AI provider.

The conversation manager connects the developer's message,
conversation history, project context, and current code context
before sending the request to the configured AI provider.
"""

from .ai_client import AIClient
from .prompts import CHAT_PROMPT
from .responses import create_response


class ConversationManager:
    """Manage AI Coding Teammate conversation context."""

    def __init__(self, client=None):
        """
        Initialize the conversation manager.

        A shared AIClient should normally be supplied by AIEngine.
        If the manager is used independently, it creates its own
        client.
        """

        self.client = client or AIClient()

    # =========================================================
    # SYSTEM PROMPT
    # =========================================================

    @staticmethod
    def build_system_prompt(project_context=None):
        """
        Build the system instructions for the AI Coding Teammate.

        Project information is added when available so the AI
        understands the developer's current working environment.
        """

        system_prompt = CHAT_PROMPT.strip()

        if not project_context:
            return system_prompt

        context_lines = []

        if isinstance(project_context, dict):

            project_name = project_context.get("name")
            description = project_context.get("description")
            language = project_context.get("language")
            framework = project_context.get("framework")

            if project_name:
                context_lines.append(
                    f"Project name: {project_name}"
                )

            if description:
                context_lines.append(
                    f"Project description: {description}"
                )

            if language:
                context_lines.append(
                    f"Primary language: {language}"
                )

            if framework:
                context_lines.append(
                    f"Framework: {framework}"
                )

            files = project_context.get("files")

            if files:
                if isinstance(files, (list, tuple)):
                    file_names = [
                        str(item)
                        for item in files
                    ]

                    context_lines.append(
                        "Project files: "
                        + ", ".join(file_names)
                    )

        else:
            context_lines.append(
                f"Project context: {project_context}"
            )

        if context_lines:

            system_prompt += (
                "\n\n"
                "Current project context:\n"
                + "\n".join(context_lines)
            )

        return system_prompt

    # =========================================================
    # CONVERSATION HISTORY
    # =========================================================

    @staticmethod
    def normalize_history(conversation_history):
        """
        Validate and normalize stored conversation history.

        Only supported roles and non-empty text messages are
        included.
        """

        messages = []

        for item in conversation_history or []:

            if not isinstance(item, dict):
                continue

            role = item.get("role")

            if role not in {
                "user",
                "assistant",
                "system",
            }:
                continue

            content = item.get("content", "")

            if content is None:
                continue

            content = str(content).strip()

            if not content:
                continue

            messages.append({
                "role": role,
                "content": content,
            })

        return messages

    # =========================================================
    # CODE CONTEXT
    # =========================================================

    @staticmethod
    def build_user_message(
        latest_message,
        code_context=None,
    ):
        """
        Build the latest developer message.

        The current editor code is attached when supplied so the
        AI can reason about what the developer is working on.
        """

        content = str(
            latest_message or ""
        ).strip()

        if not code_context:
            return content

        code_context = str(code_context).strip()

        if not code_context:
            return content

        return (
            f"{content}\n\n"
            "Current code context:\n"
            "```text\n"
            f"{code_context}\n"
            "```"
        )

    # =========================================================
    # BUILD PROVIDER MESSAGES
    # =========================================================

    def build_messages(
        self,
        conversation_history,
        latest_message,
        project_context=None,
        code_context=None,
    ):
        """
        Build provider-ready conversation messages.

        Message structure:

            system
              ↓
            previous conversation
              ↓
            latest developer message
              ↓
            current code context
        """

        messages = []

        # -----------------------------------------------------
        # SYSTEM INSTRUCTIONS
        # -----------------------------------------------------

        system_prompt = self.build_system_prompt(
            project_context=project_context
        )

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt,
            })

        # -----------------------------------------------------
        # PREVIOUS CONVERSATION
        # -----------------------------------------------------

        history = self.normalize_history(
            conversation_history
        )

        messages.extend(history)

        # -----------------------------------------------------
        # CURRENT DEVELOPER MESSAGE
        # -----------------------------------------------------

        if latest_message:

            user_message = self.build_user_message(
                latest_message=latest_message,
                code_context=code_context,
            )

            if user_message:
                messages.append({
                    "role": "user",
                    "content": user_message,
                })

        return messages

    # =========================================================
    # GENERATE RESPONSE
    # =========================================================

    def respond(
        self,
        message,
        conversation_history=None,
        project_context=None,
        code_context=None,
    ):
        """
        Generate an AI Coding Teammate response.
        """

        if not message or not str(message).strip():

            return create_response(
                response_type="chat",
                message="Please enter a message.",
                success=False,
                error="Message cannot be empty.",
            )

        messages = self.build_messages(
            conversation_history=(
                conversation_history or []
            ),
            latest_message=message,
            project_context=project_context,
            code_context=code_context,
        )

        try:

            result = self.client.chat(
                messages=messages
            )

        except Exception as exc:

            return create_response(
                response_type="chat",
                message=(
                    "The AI Coding Teammate could not "
                    "generate a response."
                ),
                success=False,
                error=str(exc),
            )

        if not isinstance(result, dict):

            return create_response(
                response_type="chat",
                message=(
                    "The AI provider returned an "
                    "invalid response."
                ),
                success=False,
            )

        response_message = (
            result.get("content")
            or result.get("message")
            or "I was unable to generate a response."
        )

        return create_response(
            response_type="chat",
            message=response_message,
            success=result.get(
                "success",
                True,
            ),
            model=result.get("model"),
            processing_time=result.get(
                "processing_time"
            ),
        )