"""
Code Analyzer

Combines local lightweight checks with AI-powered code analysis.
"""

import json

# Import ErrorDetector with fallback for script execution
import importlib.util, pathlib, sys
_path = pathlib.Path(__file__).with_name("error_detector.py")
spec = importlib.util.spec_from_file_location("error_detector", _path)
module = importlib.util.module_from_spec(spec)
sys.modules["error_detector"] = module
spec.loader.exec_module(module)
ErrorDetector = module.ErrorDetector

try:
    from .prompts import CODE_ANALYSIS_PROMPT
except ImportError:
    import importlib.util, pathlib, sys
    _p = pathlib.Path(__file__).with_name("prompts.py")
    spec = importlib.util.spec_from_file_location("prompts", _p)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["prompts"] = mod
    spec.loader.exec_module(mod)
    CODE_ANALYSIS_PROMPT = mod.CODE_ANALYSIS_PROMPT

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


class CodeAnalyzer:
    """Analyze source code."""

    def __init__(
        self,
        client=None,
        error_detector=None,
    ):
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
        
        self.client = client or AIClient()

        self.error_detector = (
            error_detector
            or ErrorDetector(self.client)
        )

    def analyze(
        self,
        code,
        language="text",
        filename="untitled",
    ):
        """Perform complete code analysis."""

        if not code:
            return create_analysis_response(
                summary="No code was provided."
            )

        local_issues = (
            self.error_detector.detect_basic_syntax(
                code,
                language,
            )
        )

        prompt = CODE_ANALYSIS_PROMPT.format(
            language=language or "text",
            filename=filename or "untitled",
            code=code,
        )

        ai_result = self.client.ask(prompt)

        return {
            "success": ai_result.get(
                "success",
                False,
            ),
            "type": "analysis",
            "summary": ai_result.get(
                "content",
                "Analysis completed.",
            ),
            "errors": local_issues,
            "warnings": [],
            "suggestions": [],
            "highlighted_lines": [
                issue.get("line")
                for issue in local_issues
                if issue.get("line") is not None
            ],
            "model": ai_result.get("model"),
            "processing_time": ai_result.get(
                "processing_time"
            ),
        }

    @staticmethod
    def parse_json_response(content):
        """
        Attempt to parse structured JSON from an AI response.

        Useful when the model is instructed to return JSON.
        """

        if not content:
            return None

        try:
            return json.loads(content)

        except json.JSONDecodeError:
            pass

        # Handle markdown JSON blocks.
        if "```json" in content:
            try:
                json_content = (
                    content
                    .split("```json", 1)[1]
                    .split("```", 1)[0]
                    .strip()
                )

                return json.loads(json_content)

            except (
                IndexError,
                json.JSONDecodeError,
            ):
                return None

        return None