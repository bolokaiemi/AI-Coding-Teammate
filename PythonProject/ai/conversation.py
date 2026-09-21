"""
AI Conversation Manager

Maintains AI conversation context and prepares messages for the
AI provider.
"""

# Fallback import for AIClient
try:
    from .ai_client import AIClient
except ImportError:
    import importlib.util, pathlib, sys
    _a = pathlib.Path(__file__).with_name('ai_client.py')
    spec = importlib.util.spec_from_file_location('ai_client', _a)
    mod = importlib.util.module_from_spec(spec)
    sys.modules['ai_client'] = mod
    spec.loader.exec_module(mod)
    AIClient = mod.AIClient

# Fallback import for prompts (CHAT_PROMPT)
try:
    from .prompts import CHAT_PROMPT
except ImportError:
    import importlib.util, pathlib, sys
    _p = pathlib.Path(__file__).with_name('prompts.py')
    spec = importlib.util.spec_from_file_location('prompts', _p)
    mod = importlib.util.module_from_spec(spec)
    sys.modules['prompts'] = mod
    spec.loader.exec_module(mod)
    CHAT_PROMPT = mod.CHAT_PROMPT

# Fallback import for responses (create_response)
try:
    from .responses import create_response
except ImportError:
    import importlib.util, pathlib, sys
    _r = pathlib.Path(__file__).with_name('responses.py')
    spec = importlib.util.spec_from_file_location('responses', _r)
    mod = importlib.util.module_from_spec(spec)
    sys.modules['responses'] = mod
    spec.loader.exec_module(mod)
    create_response = mod.create_response


class ConversationManager:
    """Manage AI conversation context."""

    def __init__(self, client=None):
        self.client = client or AIClient()

    def build_messages(
        self,
        conversation_history,
        latest_message,
        code_context=None,
    ):
        """Build provider-ready conversation messages."""

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

            content = item.get(
                "content",
                "",
            )

            if not content:
                continue

            messages.append(
                {
                    "role": role,
                    "content": content,
                }
            )

        if latest_message:
            content = latest_message

            if code_context:
                content += (
                    "\n\nCurrent code context:\n"
                    "```text\n"
                    f"{code_context}\n"
                    "```"
                )

            messages.append(
                {
                    "role": "user",
                    "content": content,
                }
            )

        return messages

    def respond(
        self,
        message,
        conversation_history=None,
        project_context=None,
        code_context=None,
    ):
        """Generate an AI teammate response."""

        messages = self.build_messages(
            conversation_history=(
                conversation_history or []
            ),
            latest_message=message,
            code_context=code_context,
        )

        result = self.client.chat(
            messages=messages,
        )

        return create_response(
            response_type="chat",
            message=result.get(
                "content",
                "I was unable to generate a response.",
            ),
            model=result.get("model"),
            processing_time=result.get(
                "processing_time"
            ),
        )