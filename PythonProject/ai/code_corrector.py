"""
Code Corrector

Generates corrected versions of source code based on detected
problems or developer instructions.
"""

# Fallback import for AIClient
try:
    from .ai_client import AIClient
except ImportError:
    import importlib.util, pathlib, sys
    _a = pathlib.Path(__file__).with_name("ai_client.py")
    spec = importlib.util.spec_from_file_location("ai_client", _a)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ai_client"] = mod
    spec.loader.exec_module(mod)
    AIClient = mod.AIClient

# Fallback import for prompts (CODE_CORRECTION_PROMPT)
try:
    from .prompts import CODE_CORRECTION_PROMPT
except ImportError:
    import importlib.util, pathlib, sys
    _p = pathlib.Path(__file__).with_name("prompts.py")
    spec = importlib.util.spec_from_file_location("prompts", _p)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["prompts"] = mod
    spec.loader.exec_module(mod)
    CODE_CORRECTION_PROMPT = mod.CODE_CORRECTION_PROMPT

# Fallback import for responses (create_correction_response)
try:
    from .responses import create_correction_response
except ImportError:
    import importlib.util, pathlib, sys
    _r = pathlib.Path(__file__).with_name("responses.py")
    spec = importlib.util.spec_from_file_location("responses", _r)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["responses"] = mod
    spec.loader.exec_module(mod)
    create_correction_response = mod.create_correction_response



class CodeCorrector:
    """Correct programming code."""

    def __init__(self, client=None):
        self.client = client or AIClient()

    def correct(
        self,
        code,
        language="text",
        filename="untitled",
        problems=None,
    ):
        """Generate corrected code."""

        if not code:
            return create_correction_response(
                original_code="",
                corrected_code="",
                explanation="No code was provided.",
            )

        if isinstance(problems, list):
            problem_text = "\n".join(
                self._format_problem(problem)
                for problem in problems
            )
        else:
            problem_text = (
                problems
                or "Review the code for problems."
            )

        prompt = CODE_CORRECTION_PROMPT.format(
            language=language or "text",
            filename=filename or "untitled",
            code=code,
            problems=problem_text,
        )

        result = self.client.ask(prompt)

        content = result.get(
            "content",
            "",
        )

        corrected_code = self.extract_code(
            content,
            language,
        )

        explanation = self.extract_explanation(
            content,
            corrected_code,
        )

        return create_correction_response(
            original_code=code,
            corrected_code=corrected_code,
            explanation=explanation,
        )

    @staticmethod
    def _format_problem(problem):
        """Format an individual problem."""

        if isinstance(problem, dict):
            line = problem.get("line")
            message = problem.get(
                "message",
                str(problem),
            )

            if line:
                return f"Line {line}: {message}"

            return str(message)

        return str(problem)

    @staticmethod
    def extract_code(content, language="text"):
        """
        Extract code from a markdown code block.

        If the model did not use a code block, return the full
        response as a fallback.
        """

        if not content:
            return ""

        marker = f"```{language}"

        if marker in content:
            try:
                return (
                    content
                    .split(marker, 1)[1]
                    .split("```", 1)[0]
                    .strip()
                )
            except IndexError:
                pass

        if "```" in content:
            try:
                return (
                    content
                    .split("```", 1)[1]
                    .split("```", 1)[0]
                    .strip()
                )
            except IndexError:
                pass

        return content.strip()

    @staticmethod
    def extract_explanation(
        content,
        corrected_code,
    ):
        """Extract a simple explanation from the AI response."""

        if not content:
            return "No explanation was returned."

        if corrected_code and content.strip() == corrected_code:
            return "The code was corrected."

        return (
            "The AI generated a corrected version of the code. "
            "Review the suggested changes before applying them."
        )