"""
AI Engine

Central orchestrator for the AI Coding Teammate.

This class connects:

    Chat
       ↓
    Code Analysis
       ↓
    Error Detection
       ↓
    Code Correction
       ↓
    Code Explanation
       ↓
    Visual Analysis
       ↓
    Project Analysis

The engine provides one unified interface to the rest of the
application.
"""

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
if __name__ != "__main__":
    try:
        from .code_analyzer import CodeAnalyzer
        from .code_corrector import CodeCorrector
        from .code_explainer import CodeExplainer
        from .error_detector import ErrorDetector
        from .visual_analyzer import VisualAnalyzer
        from .project_analyzer import ProjectAnalyzer
        from .conversation import ConversationManager
    except ImportError:
        from ai.code_analyzer import CodeAnalyzer
        from ai.code_corrector import CodeCorrector
        from ai.code_explainer import CodeExplainer
        from ai.error_detector import ErrorDetector
        from ai.visual_analyzer import VisualAnalyzer
        from ai.project_analyzer import ProjectAnalyzer
        from ai.conversation import ConversationManager


class AIEngine:
    """Main AI Coding Teammate engine."""

    def __init__(self, client=None):
        # Use the existing engine instance when creating the client to avoid recursion.
        self.client = client or AIClient(engine=self)

        self.error_detector = ErrorDetector(
            self.client
        )

        self.code_analyzer = CodeAnalyzer(
            client=self.client,
            error_detector=self.error_detector,
        )

        self.code_corrector = CodeCorrector(
            self.client
        )

        self.code_explainer = CodeExplainer(
            self.client
        )

        self.visual_analyzer = VisualAnalyzer(
            self.client
        )

        self.project_analyzer = ProjectAnalyzer(
            self.client
        )

        self.conversation = ConversationManager(
            self.client
        )

    def chat(
        self,
        message,
        conversation_history=None,
        project_context=None,
        code_context=None,
    ):
        """Talk to the AI Coding Teammate."""

        return self.conversation.respond(
            message=message,
            conversation_history=(
                conversation_history or []
            ),
            project_context=project_context,
            code_context=code_context,
        )

    def analyze_code(
        self,
        code,
        language="text",
        filename="untitled",
    ):
        """Analyze source code."""
        CODE_ANALYSIS_PROMPT = """
Analyze the following source code.

Language:
{language}

Filename:
{filename}

Code:
```{language}
{code}
```
"""

        return self.code_analyzer.analyze(
            code=code,
            language=language,
            filename=filename,
        )

    def detect_error(
        self,
        code,
        language="text",
        error=None,
    ):
        """Detect or diagnose an error."""

        return self.error_detector.detect(
            code=code,
            language=language,
            error=error,
        )

    def correct_code(
        self,
        code,
        language="text",
        filename="untitled",
        problems=None,
    ):
        """Generate corrected code."""

        return self.code_corrector.correct(
            code=code,
            language=language,
            filename=filename,
            problems=problems,
        )

    def explain_code(
        self,
        code,
        language="text",
        filename="untitled",
    ):
        """Explain source code."""

        return self.code_explainer.explain(
            code=code,
            language=language,
            filename=filename,
        )

    def analyze_visual(
        self,
        image_data,
        context=None,
    ):
        """Analyze a screenshot or visual frame."""

        return self.visual_analyzer.analyze_image(
            image_data=image_data,
            context=context,
        )

    def analyze_screen(
        self,
        frame_data,
        code_context=None,
    ):
        """Analyze a shared screen frame."""

        return self.visual_analyzer.analyze_screen(
            frame_data=frame_data,
            code_context=code_context,
        )

    def analyze_camera(
        self,
        frame_data,
        code_context=None,
    ):
        """Analyze a camera frame."""

        return self.visual_analyzer.analyze_camera(
            frame_data=frame_data,
            code_context=code_context,
        )

    def analyze_project(
        self,
        project_name,
        description=None,
        language=None,
        framework=None,
        files=None,
    ):
        """Analyze project architecture."""

        return self.project_analyzer.analyze(
            project_name=project_name,
            description=description,
            language=language,
            framework=framework,
            files=files,
        )

    def status(self):
        """Return AI engine status."""

        client_status = self.client.status()

        return {
            "engine": "AI Coding Teammate",
            "status": (
                "ready"
                if client_status["configured"]
                else "not_configured"
            ),
            "provider_configured": client_status[
                "configured"
            ],
            "model": client_status["model"],
            "capabilities": {
                "chat": True,
                "code_analysis": True,
                "error_detection": True,
                "code_correction": True,
                "code_explanation": True,
                "visual_analysis": True,
                "screen_analysis": True,
                "camera_analysis": True,
                "project_analysis": True,
            },
        }