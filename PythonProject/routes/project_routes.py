from flask import (
    Blueprint,
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
from database.models import Project


project_bp = Blueprint(
    "project",
    __name__,
    url_prefix="/projects"
)


# ----------------------------------------------------------------------
# Create Project
# ----------------------------------------------------------------------

@project_bp.route(
    "/create",
    methods=["POST"]
)
@login_required
def create_project():
    """
    Create a new developer project.
    """

    name = request.form.get(
        "name",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    language = request.form.get(
        "language",
        ""
    ).strip()

    framework = request.form.get(
        "framework",
        ""
    ).strip()

    if not name:

        flash(
            "Project name is required.",
            "danger"
        )

        return redirect(
            url_for("dashboard.projects")
        )

    project = Project(
        user_id=current_user.id,
        name=name,
        description=description,
        language=language,
        framework=framework,
    )

    db.session.add(project)
    db.session.commit()

    flash(
        "Project created successfully.",
        "success"
    )

    return redirect(
        url_for(
            "workspace.workspace",
            project_id=project.id
        )
    )


# ----------------------------------------------------------------------
# Open Project
# ----------------------------------------------------------------------

@project_bp.route(
    "/<int:project_id>"
)
@login_required
def view_project(project_id):
    """
    Open a project in the AI workspace.
    """

    project = Project.query.filter_by(
        id=project_id,
        user_id=current_user.id
    ).first_or_404()

    return redirect(
        url_for(
            "workspace.workspace",
            project_id=project.id
        )
    )


# ----------------------------------------------------------------------
# Delete Project
# ----------------------------------------------------------------------

@project_bp.route(
    "/<int:project_id>/delete",
    methods=["POST"]
)
@login_required
def delete_project(project_id):
    """
    Delete a project belonging to the current user.
    """

    project = Project.query.filter_by(
        id=project_id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(project)
    db.session.commit()

    flash(
        "Project deleted successfully.",
        "success"
    )

    return redirect(
        url_for("dashboard.projects")
    )


# ----------------------------------------------------------------------
# Project Information API
# ----------------------------------------------------------------------

@project_bp.route(
    "/<int:project_id>/info"
)
@login_required
def project_info(project_id):
    """
    Return project information as JSON.
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

    return jsonify({
        "success": True,
        "project": {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "language": getattr(
                project,
                "language",
                None
            ),
            "framework": getattr(
                project,
                "framework",
                None
            ),
        }
    })


# ----------------------------------------------------------------------
# Update Project
# ----------------------------------------------------------------------

@project_bp.route(
    "/<int:project_id>/update",
    methods=["POST"]
)
@login_required
def update_project(project_id):
    """
    Update project information.
    """

    project = Project.query.filter_by(
        id=project_id,
        user_id=current_user.id
    ).first_or_404()

    data = request.get_json(
        silent=True
    )

    if data:

        if "name" in data:
            project.name = data["name"].strip()

        if "description" in data:
            project.description = (
                data["description"].strip()
            )

        if hasattr(project, "language"):
            if "language" in data:
                project.language = data["language"]

        if hasattr(project, "framework"):
            if "framework" in data:
                project.framework = data["framework"]

    else:

        project.name = request.form.get(
            "name",
            project.name
        ).strip()

        project.description = request.form.get(
            "description",
            project.description or ""
        ).strip()

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Project updated successfully."
    })