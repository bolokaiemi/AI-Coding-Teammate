"""
Code Explainer

Explains source code in developer-friendly language.
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

# Fallback import for prompts (CODE_EXPLANATION_PROMPT)
try:
    from .prompts import CODE_EXPLANATION_PROMPT
except ImportError:
    import importlib.util, pathlib, sys
    _p = pathlib.Path(__file__).with_name('prompts.py')
    spec = importlib.util.spec_from_file_location('prompts', _p)
    mod = importlib.util.module_from_spec(spec)
    sys.modules['prompts'] = mod
    spec.loader.exec_module(mod)
    CODE_EXPLANATION_PROMPT = mod.CODE_EXPLANATION_PROMPT

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


class CodeExplainer:
    """Explain source code."""

    def __init__(self, client=None):
        self.client = client or AIClient()

    def explain(
        self,
        code,
        language="text",
        filename="untitled",
    ):
        """Generate a code explanation."""

        if not code:
            return create_response(
                response_type="explanation",
                message="No code was provided.",
            )

        prompt = CODE_EXPLANATION_PROMPT.format(
            language=language or "text",
            filename=filename or "untitled",
            code=code,
        )

        result = self.client.ask(prompt)

        return create_response(
            response_type="explanation",
            message=result.get(
                "content",
                "No explanation was generated.",
            ),
            model=result.get("model"),
            processing_time=result.get(
                "processing_time"
            ),
        )