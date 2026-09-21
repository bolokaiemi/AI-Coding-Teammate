"""
AI Coding Teammate - AI Layer
"""

# Lazy attribute access to avoid circular imports
def __getattr__(name):
    if name == "AIEngine":
        # Load AIEngine lazily
        import importlib.util, pathlib, sys
        _path = pathlib.Path(__file__).with_name("ai_engine.py")
        spec = importlib.util.spec_from_file_location("ai_engine", _path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["ai_engine"] = module
        spec.loader.exec_module(module)
        return module.AIEngine
    if name == "AIClient":
        import importlib.util, pathlib, sys
        _path = pathlib.Path(__file__).with_name("ai_client.py")
        spec = importlib.util.spec_from_file_location("ai_client", _path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["ai_client"] = module
        spec.loader.exec_module(module)
        return module.AIClient
    raise AttributeError(f"module 'ai' has no attribute {name!r}")

# Re-export other sub‑modules that do not cause circular imports
from .code_analyzer import CodeAnalyzer
from .code_corrector import CodeCorrector
from .code_explainer import CodeExplainer
from .error_detector import ErrorDetector
from .visual_analyzer import VisualAnalyzer
from .project_analyzer import ProjectAnalyzer
from .conversation import ConversationManager

__all__ = [
    "AIEngine",
    "AIClient",
    "CodeAnalyzer",
    "CodeCorrector",
    "CodeExplainer",
    "ErrorDetector",
    "VisualAnalyzer",
    "ProjectAnalyzer",
    "ConversationManager",
]