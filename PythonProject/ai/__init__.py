"""
AI Coding Teammate - AI Layer
=============================

Central package interface for the AI layer.

The AIEngine and AIClient classes are loaded lazily to help
prevent circular-import problems during application startup.
"""

import importlib.util
import pathlib
import sys


# ============================================================
# LAZY MODULE LOADER
# ============================================================

def _load_class(module_filename, module_name, class_name):
    """
    Load a class from an AI module lazily.

    This helps prevent circular imports when AIEngine or
    AIClient depend on other modules inside the ai package.
    """

    module_path = pathlib.Path(
        __file__
    ).with_name(
        module_filename
    )

    spec = importlib.util.spec_from_file_location(
        module_name,
        module_path,
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            f"Unable to load AI module: {module_filename}"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    sys.modules[module_name] = module

    spec.loader.exec_module(
        module
    )

    return getattr(
        module,
        class_name,
    )


# ============================================================
# LAZY ATTRIBUTE ACCESS
# ============================================================

def __getattr__(name):
    """
    Lazily expose classes that may otherwise cause
    circular-import problems.
    """

    if name == "AIEngine":
        return _load_class(
            module_filename="ai_engine.py",
            module_name="ai_engine",
            class_name="AIEngine",
        )

    if name == "AIClient":
        return _load_class(
            module_filename="ai_client.py",
            module_name="ai_client",
            class_name="AIClient",
        )

    raise AttributeError(
        f"module 'ai' has no attribute {name!r}"
    )


# ============================================================
# SAFE AI MODULE EXPORTS
# ============================================================

from .code_analyzer import CodeAnalyzer
from .code_corrector import CodeCorrector
from .code_explainer import CodeExplainer
from .error_detector import ErrorDetector
from .visual_analyzer import VisualAnalyzer
from .project_analyzer import ProjectAnalyzer
from .conversation import ConversationManager


# ============================================================
# PUBLIC AI INTERFACE
# ============================================================

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