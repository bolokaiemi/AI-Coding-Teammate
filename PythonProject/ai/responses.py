# Minimal response utilities

def create_analysis_response(summary: str = "", success: bool = True, **extra):
    """Return a simple analysis response dictionary.

    Parameters
    ----------
    summary: str
        Human‑readable summary of the analysis.
    success: bool
        Indicates whether the analysis succeeded.
    **extra: dict
        Additional fields that callers may expect.
    """
    resp = {"content": summary, "success": success}
    resp.update(extra)
    return resp


def create_correction_response(original_code: str = "", corrected_code: str = "", explanation: str = "", **extra):
    """Return a simple correction response dictionary.

    Parameters
    ----------
    original_code: str
        The original source code provided.
    corrected_code: str
        The corrected version of the code.
    explanation: str
        Explanation of the changes.
    **extra: dict
        Additional fields if needed.
    """
    resp = {
        "original_code": original_code,
        "corrected_code": corrected_code,
        "explanation": explanation,
    }
    resp.update(extra)
    return resp


def create_response(response_type: str = "", message: str = "", **extra):
    """Generic response creator used by various modules.

    Parameters
    ----------
    response_type: str
        Kind of response (e.g., "explanation").
    message: str
        Main content or message.
    **extra: dict
        Additional fields such as model, processing_time, etc.
    """
    resp = {"type": response_type, "message": message}
    resp.update(extra)
    return resp


def create_visual_response(message: str = "", observations: list = None, errors: list = None, suggestions: list = None, **extra):
    """Create a response dictionary for visual analysis.

    Parameters
    ----------
    message: str
        Primary message or summary of the analysis.
    observations: list
        List of observations extracted from the image.
    errors: list
        Any detected errors or issues.
    suggestions: list
        Suggested actions or improvements.
    **extra: dict
        Additional fields callers may need.
    """
    resp = {
        "message": message,
        "observations": observations or [],
        "errors": errors or [],
        "suggestions": suggestions or [],
    }
    resp.update(extra)
    return resp
