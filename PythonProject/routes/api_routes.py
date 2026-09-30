# routes/api_routes.py

"""
AI Coding Teammate API Routes
=============================

Handles API operations used by the workspace frontend.

Responsibilities:
- API health/status.
- AI chat.
- Code analysis/correction/explanation.
- Visual, screen, and camera analysis.
- Project folder creation.
- Project file uploads.
- File analysis.
- Current-user information.

Project CRUD belongs in project_routes.py.
Workspace page rendering belongs in workspace_routes.py.
"""

import os

from flask import (
    Blueprint,
    current_app,
    jsonify,
    request,
)

from flask_login import (
    current_user,
    login_required,
)

from werkzeug.utils import secure_filename

from database.models import Project

# AI Coding Teammate engine
from ai.ai_engine import AIEngine


# ============================================================
# API BLUEPRINT
# ============================================================

api_bp = Blueprint(
    "api",
    __name__,
    url_prefix="/api",
)


# ============================================================
# AI ENGINE
# ============================================================

# Create one AI engine instance for this application process.
ai_engine = AIEngine()


# ============================================================
# ALLOWED PROJECT FILE EXTENSIONS
# ============================================================

ALLOWED_PROJECT_EXTENSIONS = {
    "py",
    "js",
    "ts",
    "html",
    "css",
    "json",
    "sql",
    "md",
    "txt",
    "java",
    "cpp",
    "c",
    "h",
    "hpp",
    "go",
    "rs",
    "php",
    "rb",
    "sh",
    "yaml",
    "yml",
    "xml",
    "toml",
    "ini",
}


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _get_user_project(project_id):
    """
    Return a project only when it belongs to the
    currently authenticated user.
    """

    if not project_id:
        return None

    try:
        project_id = int(project_id)

    except (TypeError, ValueError):
        return None

    return Project.query.filter_by(
        id=project_id,
        user_id=current_user.id,
    ).first()


def _project_directory(project):
    """
    Return the filesystem directory for a project.

    Project files are stored under:

        projects/<project_id>/
    """

    return os.path.join(
        current_app.root_path,
        "projects",
        str(project.id),
    )


def _ensure_project_directory(project):
    """
    Ensure that a project's filesystem directory exists.
    """

    directory = _project_directory(
        project
    )

    os.makedirs(
        directory,
        exist_ok=True,
    )

    return directory


def _allowed_project_file(filename):
    """
    Return True when the file extension is permitted.
    """

    if not filename:
        return False

    if "." not in filename:
        return False

    extension = (
        filename
        .rsplit(".", 1)[1]
        .lower()
    )

    return extension in ALLOWED_PROJECT_EXTENSIONS


def _safe_child_path(root, relative_path=""):
    """
    Resolve a path underneath a project directory and prevent
    path traversal outside the project.

    Returns None if the path is unsafe.
    """

    root = os.path.abspath(
        root
    )

    relative_path = (
        relative_path or ""
    ).strip()

    if not relative_path:
        return root

    candidate = os.path.abspath(
        os.path.join(
            root,
            relative_path,
        )
    )

    try:

        if os.path.commonpath(
            [
                root,
                candidate,
            ]
        ) != root:

            return None

    except ValueError:

        return None

    return candidate


def _build_project_context(project):
    """
    Build lightweight project context for the AI conversation.

    Do not expose unnecessary user information.
    """

    if project is None:
        return None

    context = {
        "id": project.id,
    }

    for attribute in (
        "name",
        "description",
        "language",
        "framework",
    ):
        value = getattr(
            project,
            attribute,
            None,
        )

        if value:
            context[attribute] = value

    return context


# ============================================================
# CREATE PROJECT FOLDER
# ============================================================

@api_bp.route(
    "/folder/create",
    methods=["POST"],
)
@login_required
def create_folder():
    """
    Create a folder inside a project.

    Expected JSON:

    {
        "project_id": 1,
        "name": "services"
    }

    Optional nested parent:

    {
        "project_id": 1,
        "name": "helpers",
        "parent": "services"
    }
    """

    data = request.get_json(
        silent=True
    ) or {}

    project_id = data.get(
        "project_id"
    )

    folder_name = str(
        data.get(
            "name",
            "",
        )
    ).strip()

    parent = str(
        data.get(
            "parent",
            "",
        )
    ).strip()

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not project_id:

        return jsonify(
            {
                "success": False,
                "error": (
                    "Project ID is required."
                ),
            }
        ), 400

    if not folder_name:

        return jsonify(
            {
                "success": False,
                "error": (
                    "Folder name is required."
                ),
            }
        ), 400

    # --------------------------------------------------------
    # VERIFY PROJECT OWNERSHIP
    # --------------------------------------------------------

    project = _get_user_project(
        project_id
    )

    if project is None:

        return jsonify(
            {
                "success": False,
                "error": (
                    "Project not found."
                ),
            }
        ), 404

    # --------------------------------------------------------
    # PREVENT UNSAFE FOLDER NAMES
    # --------------------------------------------------------

    if (
        folder_name in {".", ".."}
        or "/" in folder_name
        or "\\" in folder_name
        or "\x00" in folder_name
    ):

        return jsonify(
            {
                "success": False,
                "error": (
                    "Invalid folder name."
                ),
            }
        ), 400

    # --------------------------------------------------------
    # PROJECT DIRECTORY
    # --------------------------------------------------------

    project_root = _ensure_project_directory(
        project
    )

    parent_directory = _safe_child_path(
        project_root,
        parent,
    )

    if parent_directory is None:

        return jsonify(
            {
                "success": False,
                "error": (
                    "Invalid parent folder."
                ),
            }
        ), 400

    if not os.path.isdir(
        parent_directory
    ):

        return jsonify(
            {
                "success": False,
                "error": (
                    "Parent folder does not exist."
                ),
            }
        ), 404

    # --------------------------------------------------------
    # CREATE FOLDER
    # --------------------------------------------------------

    folder_path = os.path.join(
        parent_directory,
        folder_name,
    )

    try:

        os.makedirs(
            folder_path,
            exist_ok=False,
        )

    except FileExistsError:

        return jsonify(
            {
                "success": False,
                "error": (
                    "Folder already exists."
                ),
            }
        ), 409

    except OSError:

        current_app.logger.exception(
            "Unable to create project folder."
        )

        return jsonify(
            {
                "success": False,
                "error": (
                    "Unable to create folder."
                ),
            }
        ), 500

    return jsonify(
        {
            "success": True,
            "message": (
                "Folder created successfully."
            ),
            "name": folder_name,
            "project_id": project.id,
        }
    ), 201


# ============================================================
# UPLOAD PROJECT FILES
# ============================================================

@api_bp.route(
    "/upload",
    methods=["POST"],
)
@login_required
def upload_project_files():
    """
    Upload one or more source files into a project.

    Expected multipart/form-data:

        project_id
        files

    Optional:

        parent
    """

    project_id = request.form.get(
        "project_id",
        type=int,
    )

    parent = request.form.get(
        "parent",
        "",
    ).strip()

    if not project_id:

        return jsonify(
            {
                "success": False,
                "error": (
                    "Project ID is required."
                ),
            }
        ), 400

    project = _get_user_project(
        project_id
    )

    if project is None:

        return jsonify(
            {
                "success": False,
                "error": (
                    "Project not found."
                ),
            }
        ), 404

    uploaded_files = request.files.getlist(
        "files"
    )

    if not uploaded_files:

        single_file = request.files.get(
            "file"
        )

        if single_file:

            uploaded_files = [
                single_file
            ]

    if not uploaded_files:

        return jsonify(
            {
                "success": False,
                "error": (
                    "No files were uploaded."
                ),
            }
        ), 400

    project_root = _ensure_project_directory(
        project
    )

    destination = _safe_child_path(
        project_root,
        parent,
    )

    if destination is None:

        return jsonify(
            {
                "success": False,
                "error": (
                    "Invalid upload destination."
                ),
            }
        ), 400

    if not os.path.isdir(
        destination
    ):

        return jsonify(
            {
                "success": False,
                "error": (
                    "Upload destination does not exist."
                ),
            }
        ), 404

    saved_files = []
    rejected_files = []

    for uploaded_file in uploaded_files:

        original_name = (
            uploaded_file.filename or ""
        ).strip()

        if not original_name:
            continue

        filename = secure_filename(
            original_name
        )

        if not filename:

            rejected_files.append(
                {
                    "name": original_name,
                    "reason": (
                        "Invalid filename."
                    ),
                }
            )

            continue

        if not _allowed_project_file(
            filename
        ):

            rejected_files.append(
                {
                    "name": original_name,
                    "reason": (
                        "File type is not allowed."
                    ),
                }
            )

            continue

        file_path = os.path.join(
            destination,
            filename,
        )

        try:

            uploaded_file.save(
                file_path
            )

            saved_files.append(
                {
                    "name": filename,
                }
            )

        except OSError:

            current_app.logger.exception(
                "Unable to save uploaded file: %s",
                filename,
            )

            rejected_files.append(
                {
                    "name": original_name,
                    "reason": (
                        "Unable to save file."
                    ),
                }
            )

    if not saved_files:

        return jsonify(
            {
                "success": False,
                "error": (
                    "No valid files were uploaded."
                ),
                "rejected": rejected_files,
            }
        ), 400

    return jsonify(
        {
            "success": True,
            "message": (
                "Files uploaded successfully."
            ),
            "project_id": project.id,
            "files": saved_files,
            "rejected": rejected_files,
        }
    ), 201


# ============================================================
# API HEALTH
# ============================================================

@api_bp.route(
    "/health"
)
def health():
    """
    API health check.
    """

    return jsonify(
        {
            "success": True,
            "status": "online",
            "service": (
                "AI Coding Teammate API"
            ),
        }
    )


# ============================================================
# AI STATUS
# ============================================================

@api_bp.route(
    "/ai/status"
)
def ai_status():
    """
    Return the real AI teammate/provider status.
    """

    try:

        status = ai_engine.status()

        return jsonify(
            {
                "success": True,
                "ai": status,
            }
        )

    except Exception as error:

        current_app.logger.exception(
            "Unable to retrieve AI status."
        )

        return jsonify(
            {
                "success": False,
                "error": str(error),
            }
        ), 500


# ============================================================
# AI CHAT
# ============================================================

@api_bp.route(
    "/ai/chat",
    methods=["POST"],
)
@login_required
def ai_chat():
    """
    Send a message to the AI Coding Teammate.

    Expected JSON:

    {
        "message": "Explain this code",
        "project_id": 1,
        "session_id": "...",
        "code_context": "..."
    }

    For backward compatibility, "code" is also accepted.
    """

    data = request.get_json(
        silent=True
    ) or {}

    message = str(
        data.get(
            "message",
            "",
        )
    ).strip()

    project_id = data.get(
        "project_id"
    )

    session_id = data.get(
        "session_id"
    )

    code_context = data.get(
        "code_context"
    )

    if code_context is None:
        code_context = data.get(
            "code",
            "",
        )

    code_context = str(
        code_context or ""
    )

    conversation_history = data.get(
        "conversation_history",
        [],
    )

    if not isinstance(
        conversation_history,
        list,
    ):
        conversation_history = []

    # --------------------------------------------------------
    # VALIDATE MESSAGE
    # --------------------------------------------------------

    if not message:

        return jsonify(
            {
                "success": False,
                "error": (
                    "Message cannot be empty."
                ),
            }
        ), 400

    # --------------------------------------------------------
    # OPTIONAL PROJECT OWNERSHIP CHECK
    # --------------------------------------------------------

    project = None

    if project_id:

        project = _get_user_project(
            project_id
        )

        if project is None:

            return jsonify(
                {
                    "success": False,
                    "error": (
                        "Project not found."
                    ),
                }
            ), 404

    # --------------------------------------------------------
    # BUILD PROJECT CONTEXT
    # --------------------------------------------------------

    project_context = _build_project_context(
        project
    )

    # --------------------------------------------------------
    # REAL AI CONVERSATION
    # --------------------------------------------------------

    try:

        result = ai_engine.chat(
            message=message,
            conversation_history=conversation_history,
            project_context=project_context,
            code_context=(
                code_context
                if code_context.strip()
                else None
            ),
        )

        if not isinstance(
            result,
            dict,
        ):

            raise TypeError(
                "AI engine returned an invalid response."
            )

        response_message = (
            result.get("message")
            or result.get("content")
            or result.get("response")
        )

        if not response_message:

            response_message = (
                "The AI Coding Teammate did not "
                "return a message."
            )

        return jsonify(
            {
                "success": True,
                "message": response_message,
                "response": response_message,
                "project_id": (
                    project.id
                    if project is not None
                    else None
                ),
                "session_id": session_id,
                "code_received": bool(
                    code_context.strip()
                ),
                "model": result.get(
                    "model"
                ),
                "processing_time": result.get(
                    "processing_time"
                ),
            }
        )

    except Exception as error:

        current_app.logger.exception(
            "AI chat request failed."
        )

        return jsonify(
            {
                "success": False,
                "error": (
                    "The AI Coding Teammate could not "
                    "process the request."
                ),
                "details": str(error),
            }
        ), 500


# ============================================================
# CODE ANALYSIS
# ============================================================

@api_bp.route(
    "/code/analyze",
    methods=["POST"],
)
@login_required
def code_analyze():
    """
    Analyze source code.
    """

    data = request.get_json(
        silent=True
    ) or {}

    code = str(
        data.get(
            "code",
            "",
        )
    )

    language = str(
        data.get(
            "language",
            "python",
        )
    ).strip()

    filename = str(
        data.get(
            "filename",
            "untitled",
        )
    ).strip()

    if not code.strip():

        return jsonify(
            {
                "success": False,
                "error": (
                    "No code supplied."
                ),
            }
        ), 400

    try:

        result = ai_engine.analyze_code(
            code=code,
            language=language,
            filename=filename,
        )

        return jsonify(
            result
        )

    except Exception as error:

        current_app.logger.exception(
            "AI code analysis failed."
        )

        return jsonify(
            {
                "success": False,
                "error": (
                    "Code analysis failed."
                ),
                "details": str(error),
            }
        ), 500


# ============================================================
# CODE CORRECTION
# ============================================================

@api_bp.route(
    "/code/correct",
    methods=["POST"],
)
@login_required
def code_correct():
    """
    Request corrected code from the AI.
    """

    data = request.get_json(
        silent=True
    ) or {}

    code = str(
        data.get(
            "code",
            "",
        )
    )

    language = str(
        data.get(
            "language",
            "python",
        )
    ).strip()

    filename = str(
        data.get(
            "filename",
            "untitled",
        )
    ).strip()

    problems = data.get(
        "problems"
    )

    if not code.strip():

        return jsonify(
            {
                "success": False,
                "error": (
                    "No code supplied."
                ),
            }
        ), 400

    try:

        result = ai_engine.correct_code(
            code=code,
            language=language,
            filename=filename,
            problems=problems,
        )

        return jsonify(
            result
        )

    except Exception as error:

        current_app.logger.exception(
            "AI code correction failed."
        )

        return jsonify(
            {
                "success": False,
                "error": (
                    "Code correction failed."
                ),
                "details": str(error),
            }
        ), 500


# ============================================================
# CODE EXPLANATION
# ============================================================

@api_bp.route(
    "/code/explain",
    methods=["POST"],
)
@login_required
def code_explain():
    """
    Ask the AI to explain source code.
    """

    data = request.get_json(
        silent=True
    ) or {}

    code = str(
        data.get(
            "code",
            "",
        )
    )

    language = str(
        data.get(
            "language",
            "python",
        )
    ).strip()

    filename = str(
        data.get(
            "filename",
            "untitled",
        )
    ).strip()

    if not code.strip():

        return jsonify(
            {
                "success": False,
                "error": (
                    "No code supplied."
                ),
            }
        ), 400

    try:

        result = ai_engine.explain_code(
            code=code,
            language=language,
            filename=filename,
        )

        return jsonify(
            result
        )

    except Exception as error:

        current_app.logger.exception(
            "AI code explanation failed."
        )

        return jsonify(
            {
                "success": False,
                "error": (
                    "Code explanation failed."
                ),
                "details": str(error),
            }
        ), 500


# ============================================================
# VISUAL ANALYSIS
# ============================================================

@api_bp.route(
    "/visual/analyze",
    methods=["POST"],
)
@login_required
def visual_analyze():
    """
    Analyze an uploaded image, screenshot,
    or visual frame.
    """

    data = request.get_json(
        silent=True
    ) or {}

    image_data = data.get(
        "image"
    )

    project_id = data.get(
        "project_id"
    )

    context = data.get(
        "context"
    )

    if not image_data:

        return jsonify(
            {
                "success": False,
                "error": (
                    "No image data supplied."
                ),
            }
        ), 400

    if project_id:

        project = _get_user_project(
            project_id
        )

        if project is None:

            return jsonify(
                {
                    "success": False,
                    "error": (
                        "Project not found."
                    ),
                }
            ), 404

    try:

        result = ai_engine.analyze_visual(
            image_data=image_data,
            context=context,
        )

        return jsonify(
            result
        )

    except Exception as error:

        current_app.logger.exception(
            "AI visual analysis failed."
        )

        return jsonify(
            {
                "success": False,
                "error": (
                    "Visual analysis failed."
                ),
                "details": str(error),
            }
        ), 500


# ============================================================
# SCREEN ANALYSIS
# ============================================================

@api_bp.route(
    "/screen/analyze",
    methods=["POST"],
)
@login_required
def screen_analyze():
    """
    Receive a screenshot/frame from screen sharing.
    """

    data = request.get_json(
        silent=True
    ) or {}

    frame = data.get(
        "frame"
    )

    code_context = data.get(
        "code_context"
    )

    if not frame:

        return jsonify(
            {
                "success": False,
                "error": (
                    "No screen frame supplied."
                ),
            }
        ), 400

    try:

        result = ai_engine.analyze_screen(
            frame_data=frame,
            code_context=code_context,
        )

        return jsonify(
            result
        )

    except Exception as error:

        current_app.logger.exception(
            "AI screen analysis failed."
        )

        return jsonify(
            {
                "success": False,
                "error": (
                    "Screen analysis failed."
                ),
                "details": str(error),
            }
        ), 500


# ============================================================
# CAMERA ANALYSIS
# ============================================================

@api_bp.route(
    "/camera/analyze",
    methods=["POST"],
)
@login_required
def camera_analyze():
    """
    Receive a camera frame for AI visual analysis.
    """

    data = request.get_json(
        silent=True
    ) or {}

    frame = data.get(
        "frame"
    )

    code_context = data.get(
        "code_context"
    )

    if not frame:

        return jsonify(
            {
                "success": False,
                "error": (
                    "No camera frame supplied."
                ),
            }
        ), 400

    try:

        result = ai_engine.analyze_camera(
            frame_data=frame,
            code_context=code_context,
        )

        return jsonify(
            result
        )

    except Exception as error:

        current_app.logger.exception(
            "AI camera analysis failed."
        )

        return jsonify(
            {
                "success": False,
                "error": (
                    "Camera analysis failed."
                ),
                "details": str(error),
            }
        ), 500


# ============================================================
# FILE ANALYSIS
# ============================================================

@api_bp.route(
    "/file/analyze",
    methods=["POST"],
)
@login_required
def file_analyze():
    """
    Receive a file for future AI analysis.

    This endpoint analyzes a submitted file.

    It is different from /api/upload, which stores files
    inside the selected project.
    """

    if "file" not in request.files:

        return jsonify(
            {
                "success": False,
                "error": (
                    "No file uploaded."
                ),
            }
        ), 400

    uploaded_file = request.files[
        "file"
    ]

    if not uploaded_file.filename:

        return jsonify(
            {
                "success": False,
                "error": (
                    "No filename supplied."
                ),
            }
        ), 400

    filename = secure_filename(
        uploaded_file.filename
    )

    if not filename:

        return jsonify(
            {
                "success": False,
                "error": (
                    "Invalid filename."
                ),
            }
        ), 400

    return jsonify(
        {
            "success": True,
            "filename": filename,
            "message": (
                "File received successfully."
            ),
        }
    )


# ============================================================
# CURRENT USER
# ============================================================

@api_bp.route(
    "/me"
)
@login_required
def current_user_info():
    """
    Return basic information about the authenticated user.
    """

    return jsonify(
        {
            "success": True,
            "user": {
                "id": current_user.id,
                "first_name": getattr(
                    current_user,
                    "first_name",
                    "",
                ),
                "last_name": getattr(
                    current_user,
                    "last_name",
                    "",
                ),
                "email": getattr(
                    current_user,
                    "email",
                    "",
                ),
            },
        }
    )