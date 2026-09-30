# ai/ai_engine.py

"""
AI Engine
=========

Central orchestrator for the AI Coding Teammate.

The engine connects:

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

The rest of the application should normally communicate
with the AI layer through this class.
"""

from .ai_client import AIClient
from .code_analyzer import CodeAnalyzer
from .code_corrector import CodeCorrector
from .code_explainer import CodeExplainer
from .error_detector import ErrorDetector
from .visual_analyzer import VisualAnalyzer
from .project_analyzer import ProjectAnalyzer
from .conversation import ConversationManager


class AIEngine:
    """
    Main orchestrator for the AI Coding Teammate.

    A single AIClient instance is shared between the
    different AI components.
    """

    def __init__(self, client=None):
        """
        Initialize the AI engine and its components.
        """

        # ----------------------------------------------------
        # SHARED AI CLIENT
        # ----------------------------------------------------

        self.client = client or AIClient(
            engine=self
        )
        # Attach engine reference to provided client for compatibility with tests
        if hasattr(self.client, 'engine'):
            self.client.engine = self

        # ----------------------------------------------------
        # ERROR DETECTOR
        # ----------------------------------------------------

        self.error_detector = ErrorDetector(
            client=self.client
        )

        # ----------------------------------------------------
        # CODE ANALYZER
        # ----------------------------------------------------

        self.code_analyzer = CodeAnalyzer(
            client=self.client,
            error_detector=self.error_detector,
        )

        # ----------------------------------------------------
        # CODE CORRECTOR
        # ----------------------------------------------------

        self.code_corrector = CodeCorrector(
            client=self.client
        )

        # ----------------------------------------------------
        # CODE EXPLAINER
        # ----------------------------------------------------

        self.code_explainer = CodeExplainer(
            client=self.client
        )

        # ----------------------------------------------------
        # VISUAL ANALYZER
        # ----------------------------------------------------

        self.visual_analyzer = VisualAnalyzer(
            client=self.client
        )

        # ----------------------------------------------------
        # PROJECT ANALYZER
        # ----------------------------------------------------

        self.project_analyzer = ProjectAnalyzer(
            client=self.client
        )

        # ----------------------------------------------------
        # CONVERSATION MANAGER
        # ----------------------------------------------------

        self.conversation = ConversationManager(
            client=self.client
        )

    # ========================================================
    # CHAT
    # ========================================================

    def chat(
        self,
        message,
        conversation_history=None,
        project_context=None,
        code_context=None,
    ):
        """
        Talk to the AI Coding Teammate.

        Parameters
        ----------
        message:
            Latest developer message.

        conversation_history:
            Previous conversation messages.

        project_context:
            Optional information about the active project.

        code_context:
            Optional source code currently being viewed
            or edited.
        """

        if not message:
            return {
                "success": False,
                "type": "chat",
                "message": "No message was provided.",
                "content": "No message was provided.",
            }

        return self.conversation.respond(
            message=message,
            conversation_history=(
                conversation_history or []
            ),
            project_context=project_context,
            code_context=code_context,
        )

    # ========================================================
    # CODE ANALYSIS
    # ========================================================

    def analyze_code(
        self,
        code,
        language="text",
        filename="untitled",
    ):
        """
        Analyze source code for problems and improvements.
        """

        return self.code_analyzer.analyze(
            code=code,
            language=language,
            filename=filename,
        )

    # ========================================================
    # ERROR DETECTION
    # ========================================================

    def detect_error(
        self,
        code,
        language="text",
        error=None,
    ):
        """
        Detect or diagnose programming errors.
        """

        return self.error_detector.detect(
            code=code,
            language=language,
            error=error,
        )

    # ========================================================
    # CODE CORRECTION
    # ========================================================

    def correct_code(
        self,
        code,
        language="text",
        filename="untitled",
        problems=None,
    ):
        """
        Generate a corrected version of source code.
        """

        return self.code_corrector.correct(
            code=code,
            language=language,
            filename=filename,
            problems=problems,
        )

    # ========================================================
    # CODE EXPLANATION
    # ========================================================

    def explain_code(
        self,
        code,
        language="text",
        filename="untitled",
    ):
        """
        Explain source code in developer-friendly language.
        """

        return self.code_explainer.explain(
            code=code,
            language=language,
            filename=filename,
        )

    # ========================================================
    # VISUAL ANALYSIS
    # ========================================================

    def analyze_visual(
        self,
        image_data,
        context=None,
    ):
        """
        Analyze an uploaded screenshot or image.
        """

        return self.visual_analyzer.analyze_image(
            image_data=image_data,
            context=context,
        )

    # ========================================================
    # SCREEN ANALYSIS
    # ========================================================

    def analyze_screen(
        self,
        frame_data,
        code_context=None,
    ):
        """
        Analyze a frame captured from screen sharing.
        """

        return self.visual_analyzer.analyze_screen(
            frame_data=frame_data,
            code_context=code_context,
        )

    # ========================================================
    # CAMERA ANALYSIS
    # ========================================================

    def analyze_camera(
        self,
        frame_data,
        code_context=None,
    ):
        """
        Analyze a frame captured from the camera.
        """

        return self.visual_analyzer.analyze_camera(
            frame_data=frame_data,
            code_context=code_context,
        )

    # ========================================================
    # PROJECT ANALYSIS
    # ========================================================

    def analyze_project(
        self,
        project_name,
        description=None,
        language=None,
        framework=None,
        files=None,
    ):
        """
        Analyze the structure and architecture of a project.
        """

        return self.project_analyzer.analyze(
            project_name=project_name,
            description=description,
            language=language,
            framework=framework,
            files=files,
        )

    # ========================================================
    # PROVIDER STATUS
    # ========================================================

    def status(self):
        """
        Return AI engine and provider status.
        """

        client_status = self.client.status()

        configured = bool(
            client_status.get(
                "configured",
                False,
            )
        )

        return {
            "name": "AI Coding Teammate",
            "engine": "AI Coding Teammate",
            "status": (
                "ready"
                if configured
                else "not_configured"
            ),
            "provider": client_status.get(
                "provider",
                "openai",
            ),
            "provider_configured": configured,
            "configured": configured,
            "model": client_status.get(
                "model"
            ),
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


    def health(self):
        """Return health information for the AI engine.

        Mirrors :meth:`status` for backward compatibility.
        """
        status = self.status()
        # Include a success flag for compatibility with tests
        return {"success": True, **status}

    # ============================================================
    # MODULE EXPORTS
    # ============================================================

__all__ = [
    "AIEngine",
]