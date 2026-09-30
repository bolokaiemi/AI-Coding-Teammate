# routes/workspace_routes.py

"""
Workspace Routes
================

Routes for the AI Coding Teammate development workspace.

Responsibilities:
- Open the coding workspace.
- Load a user's project.
- Load project files for the project panel.
- Render the reusable file-tree partial.
- Create coding sessions.
- Receive code-save requests.
- Queue code execution.
- Send code to the AI analysis layer.

Project creation/deletion and file/folder management should remain
in project_routes.py, api_routes.py, and the service layer.
"""

import os

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from flask_login import (
    current_user,
    login_required,
)

from database.database import db
from database.models import (
    CodeSession,
    Project,
)


# ============================================================
# WORKSPACE BLUEPRINT
# ============================================================

workspace_bp = Blueprint(
    "workspace",
    __name__,
    url_prefix="/workspace",
)


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _get_user_project(project_id=None):
    """
    Return a project owned by the authenticated user.

    If project_id is not supplied, return the user's most
    recently updated project.
    """

    if project_id:

        return Project.query.filter_by(
            id=project_id,
            user_id=current_user.id,
        ).first()

    return (
        Project.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            Project.updated_at.desc()
        )
        .first()
    )


def _get_project_directory(project):
    """
    Return the filesystem directory belonging to a project.

    Each project receives its own directory under:

        projects/<project_id>/

    The function does not create the directory.
    """

    if project is None:
        return None

    return os.path.join(
        current_app.root_path,
        "projects",
        str(project.id),
    )


def _build_file_tree(directory):
    """
    Build a lightweight file-tree structure from a directory.

    The returned objects are compatible with
    templates/workspace/_file_tree.html.

    Files/folders outside the project's own directory are never
    included.
    """

    if not directory:
        return []

    if not os.path.isdir(directory):
        return []

    files = []

    try:

        entries = sorted(
            os.scandir(directory),
            key=lambda entry: (
                not entry.is_dir(),
                entry.name.lower(),
            ),
        )

    except OSError:

        current_app.logger.exception(
            "Unable to read project directory: %s",
            directory,
        )

        return []

    for entry in entries:

        # Ignore common hidden/system files.
        if entry.name.startswith("."):
            continue

        item = {
            "id": entry.path,
            "name": entry.name,
            "is_folder": entry.is_dir(),
        }

        # ----------------------------------------------------
        # Load immediate children for folders.
        #
        # This matches the current _file_tree.html structure.
        # Later this can become fully recursive if required.
        # ----------------------------------------------------

        if entry.is_dir():

            children = []

            try:

                child_entries = sorted(
                    os.scandir(entry.path),
                    key=lambda child: (
                        not child.is_dir(),
                        child.name.lower(),
                    ),
                )

                for child in child_entries:

                    if child.name.startswith("."):
                        continue

                    children.append(
                        {
                            "id": child.path,
                            "name": child.name,
                            "is_folder": child.is_dir(),
                        }
                    )

            except OSError:

                current_app.logger.warning(
                    "Unable to read folder: %s",
                    entry.path,
                )

            item["children"] = children

        files.append(item)

    return files


def _get_project_files(project):
    """
    Return the filesystem files belonging to a project.
    """

    project_directory = _get_project_directory(
        project
    )

    return _build_file_tree(
        project_directory
    )


# ============================================================
# MAIN WORKSPACE
# ============================================================

@workspace_bp.route("/")
@login_required
def workspace():
    """
    Open the AI Coding Teammate workspace.

    A project can optionally be selected using:

        /workspace/?project_id=123

    If no project is supplied, the user's most recently
    updated project is opened.
    """

    project_id = request.args.get(
        "project_id",
        type=int,
    )

    project = None

    # --------------------------------------------------------
    # LOAD REQUESTED PROJECT
    # --------------------------------------------------------

    if project_id:

        project = _get_user_project(
            project_id
        )

        if project is None:

            flash(
                "Project not found.",
                "danger",
            )

            return redirect(
                url_for(
                    "dashboard.projects"
                )
            )

    # --------------------------------------------------------
    # LOAD MOST RECENT PROJECT
    # --------------------------------------------------------

    if project is None:

        project = _get_user_project()

    # --------------------------------------------------------
    # CREATE FIRST PROJECT
    #
    # This preserves the behavior from your existing file.
    # --------------------------------------------------------

    if project is None:

        project = Project(
            user_id=current_user.id,
            name="My First AI Project",
            description=(
                "My first project with the "
                "AI Coding Teammate."
            ),
        )

        db.session.add(project)
        db.session.commit()

    # --------------------------------------------------------
    # PROJECT FILES
    # --------------------------------------------------------

    files = _get_project_files(
        project
    )

    # --------------------------------------------------------
    # CURRENT FILE
    #
    # No file is selected automatically yet.
    # project.js / code-editor.js can update this later.
    # --------------------------------------------------------

    current_file = None

    # --------------------------------------------------------
    # MOST RECENT CODE SESSION
    # --------------------------------------------------------

    code_session = (
        CodeSession.query
        .filter_by(
            project_id=project.id
        )
        .order_by(
            CodeSession.created_at.desc()
        )
        .first()
    )

    # --------------------------------------------------------
    # RENDER WORKSPACE
    # --------------------------------------------------------

    return render_template(
        "workspace/workspace.html",
        project=project,
        files=files,
        current_file=current_file,
        code_session=code_session,
    )


# ============================================================
# FILE TREE PARTIAL
# ============================================================

@workspace_bp.route("/file_tree")
@login_required
def file_tree():
    """
    Render only the project's file tree.

    project.js can call:

        /workspace/file_tree?project_id=123

    and replace the existing [data-file-tree] content without
    reloading the entire workspace.
    """

    project_id = request.args.get(
        "project_id",
        type=int,
    )

    # --------------------------------------------------------
    # REQUIRE A PROJECT
    # --------------------------------------------------------

    if not project_id:

        return render_template(
            "workspace/_file_tree.html",
            files=[],
            current_file=None,
        )

    # --------------------------------------------------------
    # VERIFY PROJECT OWNERSHIP
    # --------------------------------------------------------

    project = _get_user_project(
        project_id
    )

    if project is None:

        return render_template(
            "workspace/_file_tree.html",
            files=[],
            current_file=None,
        ), 404

    # --------------------------------------------------------
    # LOAD FILES
    # --------------------------------------------------------

    files = _get_project_files(
        project
    )

    return render_template(
        "workspace/_file_tree.html",
        files=files,
        current_file=None,
    )


# ============================================================
# WORKSPACE STATUS
# ============================================================

@workspace_bp.route("/status")
@login_required
def workspace_status():
    """
    Lightweight endpoint used by the frontend to confirm
    that the workspace backend is available.
    """

    return jsonify(
        {
            "success": True,
            "workspace": "ready",
            "user_id": current_user.id,
        }
    )


# ============================================================
# CREATE CODE SESSION
# ============================================================

@workspace_bp.route(
    "/<int:project_id>/session",
    methods=["POST"],
)
@login_required
def create_session(project_id):
    """
    Create a new coding session for a project.
    """

    project = Project.query.filter_by(
        id=project_id,
        user_id=current_user.id,
    ).first_or_404()

    code_session = CodeSession(
        project_id=project.id
    )

    db.session.add(
        code_session
    )

    db.session.commit()

    return redirect(
        url_for(
            "workspace.workspace",
            project_id=project.id,
        )
    )


# ============================================================
# SAVE CODE
# ============================================================

@workspace_bp.route(
    "/<int:project_id>/save",
    methods=["POST"],
)
@login_required
def save_code(project_id):
    """
    Receive code submitted by the workspace editor.

    Actual persistence should eventually be delegated to
    services/code_service.py.
    """

    project = _get_user_project(
        project_id
    )

    if project is None:

        return jsonify(
            {
                "success": False,
                "error": "Project not found.",
            }
        ), 404

    data = request.get_json(
        silent=True
    ) or {}

    code = data.get(
        "code",
        "",
    )

    filename = data.get(
        "filename",
        "main.py",
    )

    # --------------------------------------------------------
    # TODO
    #
    # Delegate actual persistence to:
    #
    # services/code_service.py
    # --------------------------------------------------------

    return jsonify(
        {
            "success": True,
            "message": (
                "Code received successfully."
            ),
            "filename": filename,
            "length": len(code),
        }
    )


# ============================================================
# RUN CODE
# ============================================================

@workspace_bp.route(
    "/<int:project_id>/run",
    methods=["POST"],
)
@login_required
def run_code(project_id):
    """
    Request execution of workspace code.

    SECURITY:
    Never execute arbitrary user code directly with exec(),
    eval(), subprocess, os.system(), or similar mechanisms
    inside the Flask web process.

    Code execution should eventually be delegated to an
    isolated execution service/container.
    """

    project = _get_user_project(
        project_id
    )

    if project is None:

        return jsonify(
            {
                "success": False,
                "error": "Project not found.",
            }
        ), 404

    data = request.get_json(
        silent=True
    ) or {}

    code = data.get(
        "code",
        "",
    )

    language = data.get(
        "language",
        "python",
    )

    return jsonify(
        {
            "success": True,
            "status": "queued",
            "message": (
                "Code execution will be handled "
                "by the secure execution service."
            ),
            "language": language,
            "code_length": len(code),
        }
    )


# ============================================================
# ANALYZE CODE
# ============================================================

@workspace_bp.route(
    "/<int:project_id>/analyze",
    methods=["POST"],
)
@login_required
def analyze_code(project_id):
    """
    Receive code for AI analysis.

    The actual AI analyzer will eventually be called from
    services/analysis_service.py.
    """

    project = _get_user_project(
        project_id
    )

    if project is None:

        return jsonify(
            {
                "success": False,
                "error": "Project not found.",
            }
        ), 404

    data = request.get_json(
        silent=True
    ) or {}

    code = data.get(
        "code",
        "",
    )

    language = data.get(
        "language",
        "python",
    )

    if not code.strip():

        return jsonify(
            {
                "success": False,
                "error": "No code was supplied.",
            }
        ), 400

    # --------------------------------------------------------
    # TODO
    #
    # Future:
    #
    # result = AnalysisService.analyze(
    #     code=code,
    #     language=language,
    #     project_id=project.id,
    # )
    # --------------------------------------------------------

    return jsonify(
        {
            "success": True,
            "status": "received",
            "message": (
                "Code has been received "
                "for AI analysis."
            ),
            "language": language,
        }
    )