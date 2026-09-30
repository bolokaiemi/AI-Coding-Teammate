"""
AI Engine

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

The engine provides one unified interface to the rest
of the application.
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
    Main AI Coding Teammate engine.

    Coordinates all AI components while sharing a single
    AIClient instance between them.
    """

    def __init__(self, client=None):
        """
        Initialize the AI engine and its components.

        A single AIClient instance is shared by all components
        to avoid unnecessary client creation and circular
        initialization.
        """

        # -----------------------------------------------------
        # AI PROVIDER CLIENT
        # -----------------------------------------------------

        if client is None:
            self.client = AIClient(engine=self)
        else:
            self.client = client

            # Attach this engine to externally supplied clients
            # when supported.
            if hasattr(self.client, "engine"):
                self.client.engine = self

        # -----------------------------------------------------
        # ERROR DETECTOR
        # -----------------------------------------------------

        self.error_detector = ErrorDetector(
            client=self.client
        )

        # -----------------------------------------------------
        # CODE ANALYZER
        # -----------------------------------------------------

        self.code_analyzer = CodeAnalyzer(
            client=self.client,
            error_detector=self.error_detector,
        )

        # -----------------------------------------------------
        # CODE CORRECTOR
        # -----------------------------------------------------

        self.code_corrector = CodeCorrector(
            client=self.client
        )

        # -----------------------------------------------------
        # CODE EXPLAINER
        # -----------------------------------------------------

        self.code_explainer = CodeExplainer(
            client=self.client
        )

        # -----------------------------------------------------
        # VISUAL ANALYZER
        # -----------------------------------------------------

        self.visual_analyzer = VisualAnalyzer(
            client=self.client
        )

        # -----------------------------------------------------
        # PROJECT ANALYZER
        # -----------------------------------------------------

        self.project_analyzer = ProjectAnalyzer(
            client=self.client
        )

        # -----------------------------------------------------
        # CONVERSATION MANAGER
        # -----------------------------------------------------

        self.conversation = ConversationManager(
            client=self.client
        )

    # =========================================================
    # CHAT
    # =========================================================

    def chat(
        self,
        message,
        conversation_history=None,
        project_context=None,
        code_context=None,
    ):
        """
        Talk to the AI Coding Teammate.

        Args:
            message:
                Developer message.

            conversation_history:
                Previous conversation messages.

            project_context:
                Information about the current project.

            code_context:
                Current source code or editor context.
        """

        if not message or not str(message).strip():
            return {
                "success": False,
                "content": "",
                "error": "Message cannot be empty.",
            }

        return self.conversation.respond(
            message=str(message).strip(),
            conversation_history=(
                conversation_history or []
            ),
            project_context=project_context,
            code_context=code_context,
        )

    # =========================================================
    # CODE ANALYSIS
    # =========================================================

    def analyze_code(
        self,
        code,
        language="text",
        filename="untitled",
    ):
        """
        Analyze source code.
        """

        return self.code_analyzer.analyze(
            code=code,
            language=language,
            filename=filename,
        )

    # =========================================================
    # ERROR DETECTION
    # =========================================================

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

    # =========================================================
    # CODE CORRECTION
    # =========================================================

    def correct_code(
        self,
        code,
        language="text",
        filename="untitled",
        problems=None,
    ):
        """
        Generate corrected source code.
        """

        return self.code_corrector.correct(
            code=code,
            language=language,
            filename=filename,
            problems=problems,
        )

    # =========================================================
    # CODE EXPLANATION
    # =========================================================

    def explain_code(
        self,
        code,
        language="text",
        filename="untitled",
    ):
        """
        Explain source code.
        """

        return self.code_explainer.explain(
            code=code,
            language=language,
            filename=filename,
        )

    # =========================================================
    # VISUAL ANALYSIS
    # =========================================================

    def analyze_visual(
        self,
        image_data,
        context=None,
    ):
        """
        Analyze a screenshot, image, or visual frame.
        """

        if not image_data:
            return {
                "success": False,
                "message": "No image data was supplied.",
            }

        return self.visual_analyzer.analyze_image(
            image_data=image_data,
            context=context,
        )

    # =========================================================
    # SCREEN ANALYSIS
    # =========================================================

    def analyze_screen(
        self,
        frame_data,
        code_context=None,
    ):
        """
        Analyze a shared screen frame.
        """

        if not frame_data:
            return {
                "success": False,
                "message": "No screen frame was supplied.",
            }

        return self.visual_analyzer.analyze_screen(
            frame_data=frame_data,
            code_context=code_context,
        )

    # =========================================================
    # CAMERA ANALYSIS
    # =========================================================

    def analyze_camera(
        self,
        frame_data,
        code_context=None,
    ):
        """
        Analyze a camera frame.
        """

        if not frame_data:
            return {
                "success": False,
                "message": "No camera frame was supplied.",
            }

        return self.visual_analyzer.analyze_camera(
            frame_data=frame_data,
            code_context=code_context,
        )

    # =========================================================
    # PROJECT ANALYSIS
    # =========================================================

    def analyze_project(
        self,
        project_name,
        description=None,
        language=None,
        framework=None,
        files=None,
    ):
        """
        Analyze the architecture and context of a project.
        """

        if not project_name:
            return {
                "success": False,
                "message": "Project name is required.",
            }

        return self.project_analyzer.analyze(
            project_name=project_name,
            description=description,
            language=language,
            framework=framework,
            files=files or [],
        )

    # =========================================================
    # ENGINE STATUS
    # =========================================================

    def status(self):
        """
        Return AI engine and provider status.
        """

        client_status = self.client.status()

        configured = client_status.get(
            "configured",
            False,
        )

        return {
            "engine": "AI Coding Teammate",
            "status": (
                "ready"
                if configured
                else "development_mode"
            ),
            "provider": client_status.get(
                "provider",
                "openai",
            ),
            "provider_configured": configured,
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

    # =========================================================
    # HEALTH CHECK
    # =========================================================

    def health(self):
        """
        Lightweight AI subsystem health information.

        Useful for API health routes and debugging.
        """

        status = self.status()

        return {
            "success": True,
            "engine": status["engine"],
            "status": status["status"],
            "provider": status["provider"],
            "provider_configured": (
                status["provider_configured"]
            ),
            "model": status["model"],
        }