"""
Error Detector

Detects and classifies potential programming errors.
"""

import re

try:
    from .ai_client import AIClient
except ImportError:
    # Fallback for script execution (no package context)
    import importlib.util, pathlib, sys
    _path = pathlib.Path(__file__).with_name("ai_client.py")
    spec = importlib.util.spec_from_file_location("ai_client", _path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["ai_client"] = module
    spec.loader.exec_module(module)
    AIClient = module.AIClient
# Fallback import for prompts
try:
    from .prompts import ERROR_DETECTION_PROMPT
except ImportError:
    import importlib.util, pathlib, sys
    _p = pathlib.Path(__file__).with_name("prompts.py")
    spec = importlib.util.spec_from_file_location("prompts", _p)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["prompts"] = mod
    spec.loader.exec_module(mod)
    ERROR_DETECTION_PROMPT = mod.ERROR_DETECTION_PROMPT

# Fallback import for responses
try:
    from .responses import create_analysis_response
except ImportError:
    import importlib.util, pathlib, sys
    _r = pathlib.Path(__file__).with_name("responses.py")
    spec = importlib.util.spec_from_file_location("responses", _r)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["responses"] = mod
    spec.loader.exec_module(mod)
    create_analysis_response = mod.create_analysis_response


class ErrorDetector:
    """Detect programming errors."""

    def __init__(self, client=None):
        self.client = client or AIClient()

    def detect(
        self,
        code,
        language="text",
        error=None,
    ):
        """
        Detect errors in source code.

        If a specific error message is supplied, the AI focuses
        on diagnosing that error.
        """

        if not code:
            return create_analysis_response(
                summary="No code was provided.",
            )

        prompt = ERROR_DETECTION_PROMPT.format(
            language=language or "text",
            code=code,
            error=error or "No specific error supplied.",
        )

        result = self.client.ask(prompt)

        return create_analysis_response(
            summary=result.get("content"),
            errors=[],
            warnings=[],
            suggestions=[],
        )

    @staticmethod
    def detect_basic_syntax(code, language):
        """
        Perform lightweight local checks before calling the AI.

        This is intentionally conservative and does not replace
        a real parser/compiler.
        """

        issues = []

        if not code:
            return issues

        language = (language or "").lower()

        if language == "python":
            lines = code.splitlines()

            for index, line in enumerate(lines, start=1):
                stripped = line.strip()

                if not stripped:
                    continue

                if stripped.startswith(
                    ("if ", "for ", "while ", "def ", "class ")
                ):
                    if not stripped.endswith(":"):
                        issues.append(
                            {
                                "line": index,
                                "severity": "error",
                                "message": (
                                    "This Python statement may "
                                    "require a trailing colon."
                                ),
                            }
                        )

        if language in {"javascript", "js"}:
            if "console.log(" in code:
                # Informational only.
                pass

            if code.count("{") != code.count("}"):
                issues.append(
                    {
                        "line": None,
                        "severity": "error",
                        "message": (
                            "Mismatched curly braces detected."
                        ),
                    }
                )

        return issues

    @staticmethod
    def classify_severity(message):
        """Classify a basic error message."""

        message_lower = message.lower()

        if any(
            word in message_lower
            for word in [
                "syntax",
                "exception",
                "crash",
                "security",
                "undefined",
                "not found",
            ]
        ):
            return "error"

        if any(
            word in message_lower
            for word in [
                "warning",
                "deprecated",
                "performance",
            ]
        ):
            return "warning"

        return "info"