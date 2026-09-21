"""
Project Analyzer

Builds an understanding of a developer's project and architecture.
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

# Fallback import for prompts (PROJECT_ANALYSIS_PROMPT)
try:
    from .prompts import PROJECT_ANALYSIS_PROMPT
except ImportError:
    import importlib.util, pathlib, sys
    _p = pathlib.Path(__file__).with_name('prompts.py')
    spec = importlib.util.spec_from_file_location('prompts', _p)
    mod = importlib.util.module_from_spec(spec)
    sys.modules['prompts'] = mod
    spec.loader.exec_module(mod)
    PROJECT_ANALYSIS_PROMPT = mod.PROJECT_ANALYSIS_PROMPT

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


class ProjectAnalyzer:
    """Analyze project structure and architecture."""

    def __init__(self, client=None):
        self.client = client or AIClient()

    def analyze(
        self,
        project_name,
        description=None,
        language=None,
        framework=None,
        files=None,
    ):
        """Analyze project context."""

        file_list = files or []

        if isinstance(file_list, list):
            files_text = "\n".join(
                str(item)
                for item in file_list
            )
        else:
            files_text = str(file_list)

        prompt = PROJECT_ANALYSIS_PROMPT.format(
            project_name=project_name or "Unnamed Project",
            description=description or "Not provided.",
            language=language or "Not specified.",
            framework=framework or "Not specified.",
            files=files_text or "No files provided.",
        )

        result = self.client.ask(prompt)

        return create_response(
            response_type="project_analysis",
            message=result.get(
                "content",
                "No project analysis was generated.",
            ),
            model=result.get("model"),
            processing_time=result.get(
                "processing_time"
            ),
        )

    @staticmethod
    def build_context(project):
        """Build AI-readable context from a Project model."""

        if not project:
            return {}

        return {
            "project_id": project.id,
            "name": project.name,
            "description": project.description,
            "language": project.language,
            "framework": project.framework,
            "repository_url": project.repository_url,
            "status": project.status,
        }