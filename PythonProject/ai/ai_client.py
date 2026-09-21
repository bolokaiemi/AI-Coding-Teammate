"""
AI Coding Teammate - AI Layer

This package contains the intelligence layer of the application.

The AI layer is responsible for:

    - communicating with the configured AI provider
    - analyzing source code
    - detecting programming errors
    - correcting code
    - explaining code
    - analyzing screenshots and screen frames
    - understanding project context
    - maintaining AI conversation context
    - formatting AI responses for the frontend
"""

# AIEngine will be imported lazily inside AIClient.__init__

class AIClient:
    """Client wrapper for AIEngine interactions.

    Provides provider status and dummy request methods. Holds a reference to
    the engine (if supplied) to avoid circular imports.
    """

    def __init__(self, engine=None):
        # The engine may be passed in by AIEngine to avoid recursion.
        self.engine = engine

    def _provider_status(self):
        """Return basic provider configuration status.

        Checks for an OpenAI API key and reports the configured model.
        """
        import os
        configured = bool(os.getenv("OPENAI_API_KEY"))
        return {
            "configured": configured,
            "model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
        }

    def status(self):
        """Return provider status without delegating to the engine.

        This prevents infinite recursion when AIEngine.status calls
        self.client.status.
        """
        return self._provider_status()

    def ask(self, prompt: str):
        """Send a prompt to the AI provider.

        When no API key is configured, returns a dummy successful response.
        """
        if not self._provider_status()["configured"]:
            return {"content": f"[Dummy response] {prompt[:50]}...", "success": True}
        raise NotImplementedError("AI provider integration not available in this environment.")

    def chat(self, messages):
        """Perform a chat interaction.

        Returns a placeholder response when the provider is not configured.
        """
        if not self._provider_status()["configured"]:
            return {"content": "[Dummy chat response]", "success": True}
        raise NotImplementedError("Chat integration not implemented.")

    def analyze(self, code):
        """Analyze code for issues."""
        return self.engine.analyze(code)

    def correct(self, code, error):
        """Correct code based on error."""
        return self.engine.correct(code, error)

    def explain(self, code):
        """Explain the provided code."""
        return self.engine.explain(code)

if __name__ != "__main__":
    # Demo block removed to avoid circular imports.
    pass


__all__ = [
    "AIEngine",
    "AIClient",
    "CodeAnalyzer",
    "CodeCorrector",
    "CodeExplainer",
    "ErrorDetector",
    "VisualAnalyzer",
    "ProjectAnalyzer",
    "ConversationManager",
]