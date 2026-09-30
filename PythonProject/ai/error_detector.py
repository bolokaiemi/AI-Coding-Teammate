"""
Error Detector
==============

Detects and classifies potential programming errors.

The detector combines:
- Lightweight local checks
- Python AST syntax validation
- Basic JavaScript structural checks
- AI-powered error diagnosis
"""

import ast

from .ai_client import AIClient
from .prompts import ERROR_DETECTION_PROMPT
from .responses import create_analysis_response


class ErrorDetector:
    """Detect programming errors."""

    def __init__(self, client=None):
        """
        Initialize the error detector.

        Args:
            client:
                Optional AIClient instance.
        """

        self.client = client or AIClient()

    # ========================================================
    # AI ERROR DETECTION
    # ========================================================

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

        if code is None:
            code = ""

        if not isinstance(code, str):
            raise TypeError(
                "Code must be supplied as a string."
            )

        language = (
            str(language or "text")
            .strip()
            .lower()
        )

        if not code.strip():
            return create_analysis_response(
                summary="No code was provided.",
                errors=[],
                warnings=[],
                suggestions=[],
            )

        # ----------------------------------------------------
        # RUN LOCAL CHECKS FIRST
        # ----------------------------------------------------

        local_issues = self.detect_basic_syntax(
            code,
            language,
        )

        # ----------------------------------------------------
        # BUILD AI PROMPT
        # ----------------------------------------------------

        prompt = ERROR_DETECTION_PROMPT.format(
            language=language,
            code=code,
            error=(
                error
                or "No specific error supplied."
            ),
        )

        # ----------------------------------------------------
        # CALL AI
        # ----------------------------------------------------

        try:
            result = self.client.ask(
                prompt
            )

        except Exception as exc:
            return create_analysis_response(
                summary=(
                    "Local analysis completed, but AI error "
                    "detection could not be completed."
                ),
                errors=local_issues,
                warnings=[],
                suggestions=[
                    {
                        "severity": "info",
                        "message": str(exc),
                    }
                ],
            )

        if not isinstance(result, dict):
            result = {
                "success": False,
                "content": str(result),
            }

        content = result.get(
            "content"
        ) or "Error detection completed."

        # ----------------------------------------------------
        # RETURN NORMALIZED RESPONSE
        # ----------------------------------------------------

        response = create_analysis_response(
            summary=content,
            errors=local_issues,
            warnings=[],
            suggestions=[],
        )

        # Preserve useful AI metadata when the response helper
        # returns a dictionary.
        if isinstance(response, dict):
            response.setdefault(
                "success",
                result.get(
                    "success",
                    True,
                ),
            )

            response.setdefault(
                "type",
                "error_detection",
            )

            response.setdefault(
                "model",
                result.get("model"),
            )

            response.setdefault(
                "model_name",
                (
                    result.get("model_name")
                    or result.get("model")
                ),
            )

            response.setdefault(
                "processing_time",
                result.get(
                    "processing_time"
                ),
            )

        return response

    # ========================================================
    # LOCAL SYNTAX DETECTION
    # ========================================================

    @staticmethod
    def detect_basic_syntax(
        code,
        language="text",
    ):
        """
        Perform lightweight local checks before calling the AI.

        These checks are intentionally conservative.

        Python uses the built-in AST parser for reliable syntax
        validation.

        JavaScript uses lightweight structural checks and does
        not replace a real JavaScript parser or linter.
        """

        issues = []

        if not code:
            return issues

        if not isinstance(code, str):
            return [
                {
                    "line": None,
                    "severity": "error",
                    "type": "invalid_input",
                    "message": (
                        "Source code must be supplied "
                        "as text."
                    ),
                }
            ]

        language = (
            str(language or "")
            .strip()
            .lower()
        )

        # ----------------------------------------------------
        # PYTHON
        # ----------------------------------------------------

        if language in {
            "python",
            "py",
        }:
            issues.extend(
                ErrorDetector._check_python(
                    code
                )
            )

        # ----------------------------------------------------
        # JAVASCRIPT
        # ----------------------------------------------------

        elif language in {
            "javascript",
            "js",
        }:
            issues.extend(
                ErrorDetector._check_javascript(
                    code
                )
            )

        return issues

    # ========================================================
    # PYTHON CHECKS
    # ========================================================

    @staticmethod
    def _check_python(code):
        """
        Validate Python syntax using the built-in AST parser.
        """

        issues = []

        try:
            ast.parse(
                code
            )

        except SyntaxError as exc:
            issues.append(
                {
                    "line": exc.lineno,
                    "column": exc.offset,
                    "severity": "error",
                    "type": "syntax_error",
                    "message": (
                        exc.msg
                        or "Python syntax error."
                    ),
                }
            )

        except Exception as exc:
            issues.append(
                {
                    "line": None,
                    "severity": "error",
                    "type": "parser_error",
                    "message": str(exc),
                }
            )

        return issues

    # ========================================================
    # JAVASCRIPT CHECKS
    # ========================================================

    @staticmethod
    def _check_javascript(code):
        """
        Perform lightweight JavaScript structural checks.

        This does not replace ESLint or a JavaScript parser.
        """

        issues = []

        # ----------------------------------------------------
        # CURLY BRACES
        # ----------------------------------------------------

        opening_braces = code.count("{")
        closing_braces = code.count("}")

        if opening_braces != closing_braces:
            issues.append(
                {
                    "line": None,
                    "severity": "error",
                    "type": "brace_mismatch",
                    "message": (
                        "Mismatched curly braces detected."
                    ),
                }
            )

        # ----------------------------------------------------
        # PARENTHESES
        # ----------------------------------------------------

        opening_parentheses = code.count("(")
        closing_parentheses = code.count(")")

        if (
            opening_parentheses
            != closing_parentheses
        ):
            issues.append(
                {
                    "line": None,
                    "severity": "error",
                    "type": "parenthesis_mismatch",
                    "message": (
                        "Mismatched parentheses detected."
                    ),
                }
            )

        # ----------------------------------------------------
        # SQUARE BRACKETS
        # ----------------------------------------------------

        opening_brackets = code.count("[")
        closing_brackets = code.count("]")

        if opening_brackets != closing_brackets:
            issues.append(
                {
                    "line": None,
                    "severity": "error",
                    "type": "bracket_mismatch",
                    "message": (
                        "Mismatched square brackets detected."
                    ),
                }
            )

        return issues

    # ========================================================
    # SEVERITY CLASSIFICATION
    # ========================================================

    @staticmethod
    def classify_severity(message):
        """
        Classify a basic error message.

        Returns:
            error
            warning
            info
        """

        if not message:
            return "info"

        message_lower = str(
            message
        ).lower()

        error_words = [
            "syntax",
            "exception",
            "crash",
            "security",
            "undefined",
            "not found",
            "failed",
            "failure",
            "fatal",
            "invalid",
        ]

        if any(
            word in message_lower
            for word in error_words
        ):
            return "error"

        warning_words = [
            "warning",
            "deprecated",
            "performance",
            "slow",
            "unused",
        ]

        if any(
            word in message_lower
            for word in warning_words
        ):
            return "warning"

        return "info"