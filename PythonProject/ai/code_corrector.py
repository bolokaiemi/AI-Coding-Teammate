"""
Code Corrector
==============

Generates corrected versions of source code based on detected
problems or developer instructions.

This module works with:
- AIClient
- CODE_CORRECTION_PROMPT
- create_correction_response
- CodeAnalyzer
- ErrorDetector
- Socket.IO code correction events
"""

import re

from .ai_client import AIClient
from .prompts import CODE_CORRECTION_PROMPT
from .responses import create_correction_response


class CodeCorrector:
    """Generate corrected programming code."""

    def __init__(self, client=None):
        """
        Initialize the code corrector.

        Args:
            client:
                Optional AIClient instance.

                Supplying a client allows the same AI connection
                to be shared between the analyzer, corrector,
                explainer, and other AI components.
        """

        self.client = client or AIClient()

    # ========================================================
    # MAIN CORRECTION METHOD
    # ========================================================

    def correct(
        self,
        code,
        language="text",
        filename="untitled",
        problems=None,
    ):
        """
        Generate a corrected version of source code.

        Args:
            code:
                Source code to correct.

            language:
                Programming language used by the source file.

            filename:
                Name of the file being corrected.

            problems:
                Optional list/string describing known problems.

        Returns:
            Dictionary containing the original code,
            corrected code, and explanation.
        """

        # ----------------------------------------------------
        # VALIDATE CODE
        # ----------------------------------------------------

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

        filename = (
            str(filename or "untitled")
            .strip()
        )

        # ----------------------------------------------------
        # EMPTY CODE
        # ----------------------------------------------------

        if not code.strip():
            return create_correction_response(
                original_code="",
                corrected_code="",
                explanation="No code was provided.",
            )

        # ----------------------------------------------------
        # FORMAT DETECTED PROBLEMS
        # ----------------------------------------------------

        problem_text = self._format_problems(
            problems
        )

        # ----------------------------------------------------
        # BUILD AI PROMPT
        # ----------------------------------------------------

        prompt = CODE_CORRECTION_PROMPT.format(
            language=language,
            filename=filename,
            code=code,
            problems=problem_text,
        )

        # ----------------------------------------------------
        # REQUEST AI CORRECTION
        # ----------------------------------------------------

        try:
            result = self.client.ask(
                prompt
            )

        except Exception as error:
            return create_correction_response(
                original_code=code,
                corrected_code=code,
                explanation=(
                    "The AI correction request failed. "
                    f"{error}"
                ),
            )

        # ----------------------------------------------------
        # NORMALIZE RESULT
        # ----------------------------------------------------

        if not isinstance(result, dict):
            result = {
                "success": False,
                "content": str(result),
            }

        content = result.get(
            "content",
            "",
        )

        if content is None:
            content = ""

        if not isinstance(content, str):
            content = str(content)

        # ----------------------------------------------------
        # HANDLE EMPTY AI RESPONSE
        # ----------------------------------------------------

        if not content.strip():
            return create_correction_response(
                original_code=code,
                corrected_code=code,
                explanation=(
                    "The AI did not return a corrected "
                    "version of the code."
                ),
            )

        # ----------------------------------------------------
        # EXTRACT CORRECTED CODE
        # ----------------------------------------------------

        corrected_code = self.extract_code(
            content,
            language,
        )

        # Never replace valid source code with an empty result.
        if not corrected_code.strip():
            corrected_code = code

        # ----------------------------------------------------
        # EXTRACT EXPLANATION
        # ----------------------------------------------------

        explanation = self.extract_explanation(
            content,
            corrected_code,
        )

        # ----------------------------------------------------
        # BUILD RESPONSE
        # ----------------------------------------------------

        response = create_correction_response(
            original_code=code,
            corrected_code=corrected_code,
            explanation=explanation,
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
                "correction",
            )

            response.setdefault(
                "model",
                result.get(
                    "model"
                ),
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
    # PROBLEM FORMATTING
    # ========================================================

    @classmethod
    def _format_problems(
        cls,
        problems,
    ):
        """
        Convert detected problems into text suitable for
        CODE_CORRECTION_PROMPT.
        """

        if not problems:
            return (
                "Review the code for bugs, syntax errors, "
                "logic problems, and unsafe behavior."
            )

        if isinstance(
            problems,
            (list, tuple, set),
        ):
            formatted = [
                cls._format_problem(
                    problem
                )
                for problem in problems
            ]

            formatted = [
                problem
                for problem in formatted
                if problem
            ]

            if formatted:
                return "\n".join(
                    formatted
                )

            return (
                "Review the code for problems."
            )

        if isinstance(
            problems,
            dict,
        ):
            return cls._format_problem(
                problems
            )

        return str(
            problems
        ).strip()

    @staticmethod
    def _format_problem(problem):
        """
        Format an individual detected problem.
        """

        if problem is None:
            return ""

        if isinstance(
            problem,
            dict,
        ):
            line = problem.get(
                "line"
            )

            message = (
                problem.get("message")
                or problem.get("error")
                or problem.get("description")
                or problem.get("type")
                or str(problem)
            )

            severity = problem.get(
                "severity"
            )

            prefix = ""

            if severity:
                prefix = (
                    f"[{str(severity).upper()}] "
                )

            if line is not None:
                return (
                    f"{prefix}Line {line}: "
                    f"{message}"
                )

            return (
                f"{prefix}{message}"
            )

        return str(
            problem
        ).strip()

    # ========================================================
    # CODE EXTRACTION
    # ========================================================

    @staticmethod
    def extract_code(
        content,
        language="text",
    ):
        """
        Extract corrected source code from an AI response.

        Supports responses such as:

            ```python
            print("Hello")
            ```

        and generic code fences:

            ```
            print("Hello")
            ```

        If no fenced block exists, the complete response is
        returned as a fallback.
        """

        if not content:
            return ""

        if not isinstance(
            content,
            str,
        ):
            content = str(
                content
            )

        content = content.strip()

        if not content:
            return ""

        # ----------------------------------------------------
        # FIND MARKDOWN CODE BLOCKS
        # ----------------------------------------------------

        pattern = re.compile(
            r"```([A-Za-z0-9_+\-#.]*)(?:\r?\n)"
            r"(.*?)```",
            re.DOTALL,
        )

        matches = pattern.findall(
            content
        )

        if matches:
            normalized_language = (
                str(language or "")
                .strip()
                .lower()
            )

            # ------------------------------------------------
            # PREFER A BLOCK MATCHING THE REQUESTED LANGUAGE
            # ------------------------------------------------

            for block_language, block_code in matches:

                block_language = (
                    block_language
                    .strip()
                    .lower()
                )

                if (
                    normalized_language
                    and block_language
                    == normalized_language
                ):
                    return block_code.strip()

            # ------------------------------------------------
            # OTHERWISE USE THE FIRST CODE BLOCK
            # ------------------------------------------------

            return matches[0][1].strip()

        # ----------------------------------------------------
        # FALLBACK
        # ----------------------------------------------------

        return content

    # ========================================================
    # EXPLANATION EXTRACTION
    # ========================================================

    @staticmethod
    def extract_explanation(
        content,
        corrected_code,
    ):
        """
        Extract explanatory text surrounding the corrected
        code block.
        """

        if not content:
            return (
                "No explanation was returned."
            )

        if not isinstance(
            content,
            str,
        ):
            content = str(
                content
            )

        content = content.strip()

        if not content:
            return (
                "No explanation was returned."
            )

        # ----------------------------------------------------
        # REMOVE MARKDOWN CODE BLOCKS
        # ----------------------------------------------------

        explanation = re.sub(
            r"```[A-Za-z0-9_+\-#.]*"
            r"(?:\r?\n).*?```",
            "",
            content,
            flags=re.DOTALL,
        )

        explanation = (
            explanation
            .strip()
            .strip("-")
            .strip()
        )

        if explanation:
            return explanation

        # ----------------------------------------------------
        # AI RETURNED ONLY CODE
        # ----------------------------------------------------

        if (
            corrected_code
            and content == corrected_code.strip()
        ):
            return (
                "The AI generated a corrected "
                "version of the code."
            )

        return (
            "The AI generated a corrected version of the "
            "code. Review the suggested changes before "
            "applying them."
        )