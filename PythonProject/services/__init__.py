"""
AI Coding Teammate - Service Layer

The service layer contains application/business logic that sits between
Flask routes, database models, and the AI engine.

Services:
    user_service       - User/account operations
    project_service    - Project management
    code_service       - Code/session management
    chat_service       - AI conversation management
    analysis_service   - Code analysis and correction persistence
    screen_service     - Screen-sharing frame handling
    camera_service     - Camera frame handling
    file_service       - Uploaded file management
"""

# Fallback imports for service classes
def _load_module(module_name, class_name):
    try:
        module = __import__(module_name, globals(), locals(), [class_name])
        return getattr(module, class_name)
    except ImportError:
        import importlib.util, pathlib, sys
        _path = pathlib.Path(__file__).with_name(f"{module_name}.py")
        spec = importlib.util.spec_from_file_location(module_name, _path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = mod
        spec.loader.exec_module(mod)
        return getattr(mod, class_name)

UserService = _load_module('user_service', 'UserService')
ProjectService = _load_module('project_service', 'ProjectService')
CodeService = _load_module('code_service', 'CodeService')
ChatService = _load_module('chat_service', 'ChatService')
AnalysisService = _load_module('analysis_service', 'AnalysisService')
ScreenService = _load_module('screen_service', 'ScreenService')
CameraService = _load_module('camera_service', 'CameraService')
FileService = _load_module('file_service', 'FileService')


__all__ = [
    "UserService",
    "ProjectService",
    "CodeService",
    "ChatService",
    "AnalysisService",
    "ScreenService",
    "CameraService",
    "FileService",
]