from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)

from flask_login import (
    login_required,
    current_user,
)

from database.database import db
from database.models import (
    Project,
    CodeSession,
    Analysis,
)


dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/dashboard"
)


# ----------------------------------------------------------------------
# Dashboard
# ----------------------------------------------------------------------

@dashboard_bp.route("/")
@login_required
def dashboard():
    """
    Main developer dashboard.
    """

    projects = Project.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Project.updated_at.desc()
    ).all()

    project_count = len(projects)

    session_count = CodeSession.query.join(
        Project
    ).filter(
        Project.user_id == current_user.id
    ).count()

    analysis_count = Analysis.query.join(
        CodeSession
    ).join(
        Project
    ).filter(
        Project.user_id == current_user.id
    ).count()

    return render_template(
        "dashboard/dashboard.html",
        projects=projects,
        project_count=project_count,
        session_count=session_count,
        analysis_count=analysis_count,
        ai_session_count=session_count,
    )


# ----------------------------------------------------------------------
# Projects
# ----------------------------------------------------------------------

@dashboard_bp.route("/projects")
@login_required
def projects():
    """
    Display all projects belonging to the current user.
    """

    projects = Project.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Project.updated_at.desc()
    ).all()

    return render_template(
        "dashboard/projects.html",
        projects=projects
    )


# ----------------------------------------------------------------------
# Settings
# ----------------------------------------------------------------------

@dashboard_bp.route(
    "/settings",
    methods=["GET", "POST"]
)
@login_required
def settings():
    """
    User account and AI preferences.
    """

    if request.method == "POST":

        first_name = request.form.get(
            "first_name",
            ""
        ).strip()

        last_name = request.form.get(
            "last_name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        occupation = request.form.get(
            "occupation",
            ""
        ).strip()

        if first_name:
            current_user.first_name = first_name

        if last_name:
            current_user.last_name = last_name

        if email:
            current_user.email = email

        if hasattr(
            current_user,
            "occupation"
        ):
            current_user.occupation = occupation

        db.session.commit()

        flash(
            "Your settings have been updated.",
            "success"
        )

        return redirect(
            url_for("dashboard.settings")
        )

    return render_template(
        "dashboard/settings.html"
    )