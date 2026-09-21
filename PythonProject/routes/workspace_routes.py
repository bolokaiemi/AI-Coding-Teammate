from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
)

from flask_login import (
    login_required,
    current_user,
)

from database.database import db
from database.models import (
    Project,
    CodeSession,
)


workspace_bp = Blueprint(
    "workspace",
    __name__,
    url_prefix="/workspace"
)


# ----------------------------------------------------------------------
# Main Workspace
# ----------------------------------------------------------------------

@workspace_bp.route("/")
@login_required
def workspace():
    """
    Open the AI Coding Teammate workspace.

    Optional project_id allows the workspace to open a specific
    developer project.
    """

    project_id = request.args.get(
        "project_id",
        type=int
    )

    project = None

    if project_id:

        project = Project.query.filter_by(
            id=project_id,
            user_id=current_user.id
        ).first()

        if project is None:
            flash(
                "Project not found.",
                "danger"
            )

            return redirect(
                url_for("dashboard.projects")
            )

    # --------------------------------------------------------------
    # If no project was supplied, use the latest project.
    # --------------------------------------------------------------

    if project is None:

        project = Project.query.filter_by(
            user_id=current_user.id
        ).order_by(
            Project.updated_at.desc()
        ).first()

    # --------------------------------------------------------------
    # Create a workspace project if the user has none.
    # --------------------------------------------------------------

    if project is None:

        project = Project(
            user_id=current_user.id,
            name="My First AI Project",
            description=(
                "My first project with the AI Coding Teammate."
            ),
        )

        db.session.add(project)
        db.session.commit()

    # --------------------------------------------------------------
    # Code sessions
    # --------------------------------------------------------------

    code_session = CodeSession.query.filter_by(
        project_id=project.id
    ).order_by(
        CodeSession.created_at.desc()
    ).first()

    return render_template(
        "workspace/workspace.html",
        project=project,
        code_session=code_session,
    )


# ----------------------------------------------------------------------
# Create Code Session
# ----------------------------------------------------------------------

@workspace_bp.route(
    "/<int:project_id>/session",
    methods=["POST"]
)
@login_required
def create_session(project_id):
    """
    Create a new coding session.
    """

    project = Project.query.filter_by(
        id=project_id,
        user_id=current_user.id
    ).first_or_404()

    session = CodeSession(
        project_id=project.id
    )

    db.session.add(session)
    db.session.commit()

    return redirect(
        url_for(
            "workspace.workspace",
            project_id=project.id
        )
    )


# ----------------------------------------------------------------------
# Save Code
# ----------------------------------------------------------------------

@workspace_bp.route(
    "/<int:project_id>/save",
    methods=["POST"]
)
@login_required
def save_code(project_id):
    """
    Save code submitted by the workspace editor.
    """

    project = Project.query.filter_by(
        id=project_id,
        user_id=current_user.id
    ).first()

    if project is None:
        return jsonify({
            "success": False,
            "error": "Project not found."
        }), 404

    data = request.get_json(
        silent=True
    ) or {}

    code = data.get(
        "code",
        ""
    )

    filename = data.get(
        "filename",
        "main.py"
    )

    # Actual file/session persistence will be handled by
    # code_service.py.

    return jsonify({
        "success": True,
        "message": "Code received successfully.",
        "filename": filename,
        "length": len(code),
    })


# ----------------------------------------------------------------------
# Run Code
# ----------------------------------------------------------------------

@workspace_bp.route(
    "/<int:project_id>/run",
    methods=["POST"]
)
@login_required
def run_code(project_id):
    """
    Execute code through the future secure execution service.

    IMPORTANT:
    Never execute arbitrary user code directly with exec()
    inside the Flask process.
    """

    project = Project.query.filter_by(
        id=project_id,
        user_id=current_user.id
    ).first()

    if project is None:
        return jsonify({
            "success": False,
            "error": "Project not found."
        }), 404

    data = request.get_json(
        silent=True
    ) or {}

    code = data.get(
        "code",
        ""
    )

    language = data.get(
        "language",
        "python"
    )

    return jsonify({
        "success": True,
        "status": "queued",
        "message": (
            "Code execution will be handled by "
            "the secure execution service."
        ),
        "language": language,
        "code_length": len(code),
    })


# ----------------------------------------------------------------------
# Analyze Code
# ----------------------------------------------------------------------

@workspace_bp.route(
    "/<int:project_id>/analyze",
    methods=["POST"]
)
@login_required
def analyze_code(project_id):
    """
    Send code to the AI analysis layer.
    """

    project = Project.query.filter_by(
        id=project_id,
        user_id=current_user.id
    ).first()

    if project is None:
        return jsonify({
            "success": False,
            "error": "Project not found."
        }), 404

    data = request.get_json(
        silent=True
    ) or {}

    code = data.get(
        "code",
        ""
    )

    language = data.get(
        "language",
        "python"
    )

    if not code.strip():
        return jsonify({
            "success": False,
            "error": "No code was supplied."
        }), 400

    # AI analyzer will be connected here.
    #
    # Example future flow:
    #
    # result = analyze_code(
    #     code=code,
    #     language=language,
    #     project_id=project.id
    # )

    return jsonify({
        "success": True,
        "status": "received",
        "message": (
            "Code has been received for AI analysis."
        ),
        "language": language,
    })