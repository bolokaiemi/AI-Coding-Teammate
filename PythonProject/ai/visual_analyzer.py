"""
Visual Analyzer

Analyzes screenshots, screen captures, and camera frames using a
multimodal AI model.
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

# Fallback import for prompts (VISUAL_ANALYSIS_PROMPT)
try:
    from .prompts import VISUAL_ANALYSIS_PROMPT
except ImportError:
    import importlib.util, pathlib, sys
    _p = pathlib.Path(__file__).with_name('prompts.py')
    spec = importlib.util.spec_from_file_location('prompts', _p)
    mod = importlib.util.module_from_spec(spec)
    sys.modules['prompts'] = mod
    spec.loader.exec_module(mod)
    VISUAL_ANALYSIS_PROMPT = mod.VISUAL_ANALYSIS_PROMPT

# Fallback import for responses (create_visual_response)
try:
    from .responses import create_visual_response
except ImportError:
    import importlib.util, pathlib, sys
    _r = pathlib.Path(__file__).with_name('responses.py')
    spec = importlib.util.spec_from_file_location('responses', _r)
    mod = importlib.util.module_from_spec(spec)
    sys.modules['responses'] = mod
    spec.loader.exec_module(mod)
    create_visual_response = mod.create_visual_response


class VisualAnalyzer:
    """Analyze visual developer workspace input."""

    def __init__(self, client=None):
        self.client = client or AIClient()

    def analyze_image(
        self,
        image_data,
        context=None,
    ):
        """
        Analyze an image/screenshot.
        """

        if not image_data:
            return create_visual_response(
                message="No image was provided."
            )

        prompt = VISUAL_ANALYSIS_PROMPT

        if context:
            prompt += (
                "\n\nAdditional developer context:\n"
                f"{context}"
            )

        result = self.client.analyze_image(
            image_data=image_data,
            prompt=prompt,
        )

        return create_visual_response(
            message=result.get(
                "content",
                "No visual analysis was returned.",
            ),
            observations=[],
            errors=[],
            suggestions=[],
        )

    def analyze_screen(
        self,
        frame_data,
        code_context=None,
    ):
        """Analyze a screen-sharing frame."""

        context = (
            "The developer is sharing their computer screen."
        )

        if code_context:
            context += (
                "\n\nCurrent code context:\n"
                f"{code_context}"
            )

        return self.analyze_image(
            frame_data,
            context=context,
        )

    def analyze_camera(
        self,
        frame_data,
        code_context=None,
    ):
        """Analyze a camera frame."""

        context = (
            "The developer is using their camera to show "
            "something to the AI Coding Teammate."
        )

        if code_context:
            context += (
                "\n\nCurrent code context:\n"
                f"{code_context}"
            )

        return self.analyze_image(
            frame_data,
            context=context,
        )