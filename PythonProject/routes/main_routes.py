# routes/main_routes.py

from flask import Blueprint, render_template


# ============================================================
# MAIN BLUEPRINT
# ============================================================

main_bp = Blueprint(
    "main",
    __name__
)


# ============================================================
# PUBLIC HOMEPAGE
# ============================================================

@main_bp.route("/")
def index():
    """
    Render the public AI Coding Teammate landing page.
    """

    return render_template(
        "index.html"
    )


# ============================================================
# DATENSCHUTZ
# ============================================================

@main_bp.route("/datenschutz")
def datenschutz():
    """
    Render the Datenschutz page.
    """

    return render