"""
Code Analyzer
=============

Combines lightweight local code checks with AI-powered
analysis for the AI Coding Teammate.

Responsibilities:
- Run local syntax/error detection
- Send code to the AI model for deeper analysis
- Parse structured AI responses when available
- Return results compatible with AnalysisService
"""

import json

from .ai_client import AIClient
from .error_detector import ErrorDetector
from .prompts import CODE_ANALYSIS_PROMPT
from .responses import create_analysis_response


class CodeAnalyzer:
    """Analyze source code using local and AI-powered checks."""

    def __init__(
        self,
        client=None,
        error_detector=None,
    ):
        """
        Initialize the code analyzer.

        Args:
            client:
                Optional AIClient instance.

            error_detector:
                Optional ErrorDetector instance.
        """

        self.client = client or AIClient()

        self.error_detector = (
            error_detector
            or ErrorDetector(self.client)
        )

    # ========================================================
    # MAIN ANALYSIS
    # ========================================================

    def analyze(
        self,
        code,
        language="text",
        filename="untitled",
    ):
        """
        Perform complete code analysis.

        The process combines:

        1. Local lightweight syntax/error detection.
        2. AI-powered semantic analysis.
        3. Structured response parsing.
        4. A normalized result for AnalysisService.
        """

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
            return create_analysis_response(
                summary="No code was provided."
            )

        # ----------------------------------------------------
        # LOCAL ANALYSIS
        # ----------------------------------------------------

        try:
            local_issues = (
                self.error_detector.detect_basic_syntax(
                    code,
                    language,
                )
            )

        except Exception as error:
            local_issues = [
                {
                    "type": "local_analysis_error",
                    "message": str(error),
                    "line": None,
                }
            ]

        local_issues = local_issues or []

        # ----------------------------------------------------
        # BUILD AI PROMPT
        # ----------------------------------------------------

        prompt = CODE_ANALYSIS_PROMPT.format(
            language=language,
            filename=filename,
            code=code,
        )

        # ----------------------------------------------------
        # AI ANALYSIS
        # ----------------------------------------------------

        try:
            ai_result = self.client.ask(
                prompt
            )

        except Exception as error:
            return {
                "success": False,
                "type": "analysis",
                "status": "failed",
                "summary": (
                    "AI analysis could not be completed."
                ),
                "explanation": str(error),
                "errors": local_issues,
                "warnings": [],
                "suggestions": [],
                "highlighted_lines": (
                    self._extract_highlighted_lines(
                        local_issues
                    )
                ),
                "original_code": code,
                "corrected_code": None,
                "correction_explanation": None,
                "model": None,
                "model_name": None,
                "processing_time": None,
            }

        if not isinstance(ai_result, dict):
            ai_result = {
                "success": False,
                "content": str(ai_result),
            }

        # ----------------------------------------------------
        # GET AI CONTENT
        # ----------------------------------------------------

        content = ai_result.get(
            "content",
            "",
        )

        if content is None:
            content = ""

        if not isinstance(content, str):
            content = str(content)

        # ----------------------------------------------------
        # ATTEMPT STRUCTURED JSON PARSING
        # ----------------------------------------------------

        structured = (
            self.parse_json_response(
                content
            )
        )

        # ----------------------------------------------------
        # STRUCTURED AI RESPONSE
        # ----------------------------------------------------

        if isinstance(
            structured,
            dict,
        ):
            ai_errors = structured.get(
                "errors",
                [],
            ) or []

            warnings = structured.get(
                "warnings",
                [],
            ) or []

            suggestions = structured.get(
                "suggestions",
                [],
            ) or []

            # Keep both local errors and AI-detected errors.
            errors = self._merge_issues(
                local_issues,
                ai_errors,
            )

            summary = structured.get(
                "summary"
            ) or content or "Analysis completed."

            explanation = structured.get(
                "explanation"
            ) or summary

            corrected_code = structured.get(
                "corrected_code"
            )

            correction_explanation = (
                structured.get(
                    "correction_explanation"
                )
            )

            visual_data = structured.get(
                "visual_data"
            )

            code_flow = structured.get(
                "code_flow"
            )

        # ----------------------------------------------------
        # PLAIN-TEXT AI RESPONSE
        # ----------------------------------------------------

        else:
            errors = local_issues
            warnings = []
            suggestions = []

            summary = (
                content
                or "Analysis completed."
            )

            explanation = summary

            corrected_code = None
            correction_explanation = None
            visual_data = None
            code_flow = None

        # ----------------------------------------------------
        # HIGHLIGHTED LINES
        # ----------------------------------------------------

        highlighted_lines = (
            self._extract_highlighted_lines(
                errors
            )
        )

        # ----------------------------------------------------
        # MODEL INFORMATION
        # ----------------------------------------------------

        model_name = (
            ai_result.get("model")
            or ai_result.get("model_name")
        )

        # ----------------------------------------------------
        # FINAL NORMALIZED RESPONSE
        # ----------------------------------------------------

        return {
            "success": ai_result.get(
                "success",
                True,
            ),

            "type": "analysis",

            "status": (
                "completed"
                if ai_result.get(
                    "success",
                    True,
                )
                else "failed"
            ),

            "summary": summary,

            "explanation": explanation,

            "errors": errors,

            "warnings": warnings,

            "suggestions": suggestions,

            "error_count": len(
                errors
            ),

            "warning_count": len(
                warnings
            ),

            "original_code": code,

            "corrected_code": (
                corrected_code
            ),

            "correction_explanation": (
                correction_explanation
            ),

            "visual_data": visual_data,

            "code_flow": code_flow,

            "highlighted_lines": (
                highlighted_lines
            ),

            # Keep "model" for compatibility with
            # existing code.
            "model": model_name,

            # AnalysisService uses model_name.
            "model_name": model_name,

            "processing_time": (
                ai_result.get(
                    "processing_time"
                )
            ),
        }

    # ========================================================
    # JSON RESPONSE PARSER
    # ========================================================

    @staticmethod
    def parse_json_response(content):
        """
        Attempt to parse structured JSON from an AI response.

        Supports:
        - Raw JSON
        - ```json fenced blocks
        - Generic ``` fenced blocks
        """

        if not content:
            return None

        if not isinstance(
            content,
            str,
        ):
            return None

        content = content.strip()

        # ----------------------------------------------------
        # RAW JSON
        # ----------------------------------------------------

        try:
            return json.loads(
                content
            )

        except json.JSONDecodeError:
            pass

        # ----------------------------------------------------
        # MARKDOWN JSON BLOCK
        # ----------------------------------------------------

        if "```json" in content:
            try:
                json_content = (
                    content
                    .split(
                        "```json",
                        1,
                    )[1]
                    .split(
                        "```",
                        1,
                    )[0]
                    .strip()
                )

                return json.loads(
                    json_content
                )

            except (
                IndexError,
                json.JSONDecodeError,
            ):
                pass

        # ----------------------------------------------------
        # GENERIC MARKDOWN CODE BLOCK
        # ----------------------------------------------------

        if "```" in content:
            try:
                block = (
                    content
                    .split(
                        "```",
                        1,
                    )[1]
                    .split(
                        "```",
                        1,
                    )[0]
                    .strip()
                )

                return json.loads(
                    block
                )

            except (
                IndexError,
                json.JSONDecodeError,
            ):
                pass

        return None

    # ========================================================
    # ISSUE MERGING
    # ========================================================

    @staticmethod
    def _merge_issues(
        local_issues,
        ai_issues,
    ):
        """
        Merge local and AI-detected issues while avoiding
        obvious duplicates.
        """

        merged = []
        seen = set()

        for issue in (
            list(local_issues or [])
            + list(ai_issues or [])
        ):
            if isinstance(
                issue,
                dict,
            ):
                key = (
                    issue.get("type"),
                    issue.get("message"),
                    issue.get("line"),
                )

            else:
                key = str(issue)

            if key in seen:
                continue

            seen.add(key)
            merged.append(issue)

        return merged

    # ========================================================
    # HIGHLIGHTED LINES
    # ========================================================

    @staticmethod
    def _extract_highlighted_lines(
        issues,
    ):
        """
        Extract unique source-code line numbers from issues.
        """

        lines = set()

        for issue in issues or []:
            if not isinstance(
                issue,
                dict,
            ):
                continue

            line = issue.get(
                "line"
            )

            if line is None:
                continue

            try:
                line = int(line)

            except (
                TypeError,
                ValueError,
            ):
                continue

            if line > 0:
                lines.add(
                    line
                )

        return sorted(
            lines
        )