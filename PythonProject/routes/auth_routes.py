from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)

from flask_login import (
    login_user,
    logout_user,
    current_user,
    login_required,
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)

from database.database import db
from database.models import User


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


# ----------------------------------------------------------------------
# Login
# ----------------------------------------------------------------------

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Authenticate an existing user.
    """

    if current_user.is_authenticated:
        return redirect(
            url_for("dashboard.dashboard")
        )

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        remember = request.form.get(
            "remember"
        ) == "on"

        if not email or not password:
            flash(
                "Please enter your email and password.",
                "danger"
            )

            return render_template(
                "auth/login.html"
            )

        user = User.query.filter_by(
            email=email
        ).first()

        if user is None:

            flash(
                "Invalid email or password.",
                "danger"
            )

            return render_template(
                "auth/login.html"
            )

        if not check_password_hash(
            user.password,
            password
        ):

            flash(
                "Invalid email or password.",
                "danger"
            )

            return render_template(
                "auth/login.html"
            )

        login_user(
            user,
            remember=remember
        )

        next_page = request.args.get(
            "next"
        )

        if next_page:
            return redirect(next_page)

        flash(
            "Welcome back!",
            "success"
        )

        return redirect(
            url_for("dashboard.dashboard")
        )

    return render_template(
        "auth/login.html"
    )


# ----------------------------------------------------------------------
# Register
# ----------------------------------------------------------------------

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Create a new user account.
    """

    if current_user.is_authenticated:
        return redirect(
            url_for("dashboard.dashboard")
        )

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

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        terms = request.form.get(
            "terms"
        )

        # --------------------------------------------------------------
        # Validation
        # --------------------------------------------------------------

        if not first_name or not last_name:
            flash(
                "Please enter your first and last name.",
                "danger"
            )

            return render_template(
                "auth/register.html"
            )

        if not email:
            flash(
                "Please enter your email address.",
                "danger"
            )

            return render_template(
                "auth/register.html"
            )

        if len(password) < 8:
            flash(
                "Password must contain at least 8 characters.",
                "danger"
            )

            return render_template(
                "auth/register.html"
            )

        if password != confirm_password:
            flash(
                "Passwords do not match.",
                "danger"
            )

            return render_template(
                "auth/register.html"
            )

        if not terms:
            flash(
                "You must accept the terms and conditions.",
                "danger"
            )

            return render_template(
                "auth/register.html"
            )

        # --------------------------------------------------------------
        # Check Existing User
        # --------------------------------------------------------------

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash(
                "An account with this email already exists.",
                "warning"
            )

            return redirect(
                url_for("auth.login")
            )

        # --------------------------------------------------------------
        # Create User
        # --------------------------------------------------------------

        hashed_password = generate_password_hash(
            password
        )

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_password,
        )

        db.session.add(user)
        db.session.commit()

        login_user(user)

        flash(
            "Your account has been created successfully.",
            "success"
        )

        return redirect(
            url_for("dashboard.dashboard")
        )

    return render_template(
        "auth/register.html"
    )


# ----------------------------------------------------------------------
# Logout
# ----------------------------------------------------------------------

@auth_bp.route("/logout")
@login_required
def logout():
    """
    Log the current user out.
    """

    logout_user()

    flash(
        "You have been logged out.",
        "info"
    )

    return redirect(
        url_for("main.index")
    )


# ----------------------------------------------------------------------
# Forgot Password
# ----------------------------------------------------------------------

@auth_bp.route(
    "/forgot-password",
    methods=["GET", "POST"]
)
def forgot_password():
    """
    Request a password reset.
    """

    if current_user.is_authenticated:
        return redirect(
            url_for("dashboard.dashboard")
        )

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        if not email:
            flash(
                "Please enter your email address.",
                "danger"
            )

            return render_template(
                "auth/forgot_password.html"
            )

        user = User.query.filter_by(
            email=email
        ).first()

        # Do not expose whether an account exists.
        if user:
            # Email reset implementation will be connected
            # through services/email_service.py.
            pass

        flash(
            "If an account exists for that email, "
            "a password reset link has been sent.",
            "info"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "auth/forgot_password.html"
    )


# ----------------------------------------------------------------------
# Reset Password
# ----------------------------------------------------------------------

@auth_bp.route(
    "/reset-password/<token>",
    methods=["GET", "POST"]
)
def reset_password(token):
    """
    Reset a user's password using a reset token.

    Token validation/email delivery will be connected to the
    email service.
    """

    if current_user.is_authenticated:
        return redirect(
            url_for("dashboard.dashboard")
        )

    # Token validation will be implemented in the security service.
    user = None

    if user is None:
        flash(
            "This password reset link is invalid or has expired.",
            "danger"
        )

        return redirect(
            url_for("auth.forgot_password")
        )

    if request.method == "POST":

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if len(password) < 8:
            flash(
                "Password must contain at least 8 characters.",
                "danger"
            )

            return render_template(
                "auth/reset_password.html",
                token=token
            )

        if password != confirm_password:
            flash(
                "Passwords do not match.",
                "danger"
            )

            return render_template(
                "auth/reset_password.html",
                token=token
            )

        user.password = generate_password_hash(
            password
        )

        db.session.commit()

        flash(
            "Your password has been reset successfully.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "auth/reset_password.html",
        token=token
    )