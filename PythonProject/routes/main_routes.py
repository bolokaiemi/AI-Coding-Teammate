from flask import Blueprint, render_template


main_bp = Blueprint(
    "main",
    __name__
)


@main_bp.route("/")
def index():
    """
    Public homepage.
    """

    return render_template(
        "index.html"
    )

@main_bp.route("/datenschutz")
def datenschutz():
    return render_template("datenschutz.html")


@main_bp.route("/impressum")
def impressum():
    return render_template("impressum.html")