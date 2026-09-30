"""
Authentication Routes
=====================

Handles:

- User registration
- User login
- User logout
- Forgot password requests
- Password reset pages

Database and authentication business logic is delegated
to services/user_service.py.
"""

from urllib.parse import urljoin, urlparse

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)

from services.user_service import UserService


# ============================================================
# BLUEPRINT
# ============================================================

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
)


# ============================================================
# REDIRECT SECURITY
# ============================================================

def is_safe_redirect_url(target):
    """
    Return True only when the redirect target belongs to
    the current application.

    This prevents an attacker from using the login page
    as an open redirect to an external website.
    """

    if not target:
        return False

    try:
        host_url = urlparse(request.host_url)

        redirect_url = urlparse(
            urljoin(
                request.host_url,
                target,
            )
        )

        return (
            redirect_url.scheme in ("http", "https")
            and host_url.netloc == redirect_url.netloc
        )

    except (TypeError, ValueError):
        return False


# ============================================================
# LOGIN
# ============================================================

@auth_bp.route(
    "/login",
    methods=["GET", "POST"],
)
def login():
    """
    Authenticate an existing user.
    """

    # --------------------------------------------------------
    # Already authenticated
    # --------------------------------------------------------

    if current_user.is_authenticated:

        return redirect(
            url_for(
                "dashboard.dashboard"
            )
        )

    # --------------------------------------------------------
    # Login submission
    # --------------------------------------------------------

    if request.method == "POST":

        email = (
            request.form.get(
                "email",
                "",
            )
            .strip()
            .lower()
        )

        password = request.form.get(
            "password",
            "",
        )

        remember = (
            request.form.get("remember")
            == "on"
        )

        # ----------------------------------------------------
        # Validate email
        # ----------------------------------------------------

        if not email:

            flash(
                "Please enter your email address.",
                "danger",
            )

            return render_template(
                "auth/login.html",
                email=email,
            )

        # ----------------------------------------------------
        # Validate password
        # ----------------------------------------------------

        if not password:

            flash(
                "Please enter your password.",
                "danger",
            )

            return render_template(
                "auth/login.html",
                email=email,
            )

        # ----------------------------------------------------
        # Authenticate
        # ----------------------------------------------------

        try:

            user = UserService.authenticate(
                email=email,
                password=password,
            )

        except Exception:

            # Do not expose database/internal errors
            # to the browser.

            flash(
                "Unable to log in right now. "
                "Please try again.",
                "danger",
            )

            return render_template(
                "auth/login.html",
                email=email,
            )

        # ----------------------------------------------------
        # Invalid credentials
        # ----------------------------------------------------

        if not user:

            flash(
                "Invalid email or password.",
                "danger",
            )

            return render_template(
                "auth/login.html",
                email=email,
            )

        # ----------------------------------------------------
        # Login
        # ----------------------------------------------------

        login_user(
            user,
            remember=remember,
        )

        flash(
            "Welcome back!",
            "success",
        )

        # ----------------------------------------------------
        # Return user to originally requested page
        # ----------------------------------------------------

        next_page = request.args.get(
            "next"
        )

        if (
            next_page
            and is_safe_redirect_url(next_page)
        ):
            return redirect(
                next_page
            )

        # ----------------------------------------------------
        # Default destination
        # ----------------------------------------------------

        return redirect(
            url_for(
                "dashboard.dashboard"
            )
        )

    # --------------------------------------------------------
    # GET request
    # --------------------------------------------------------

    return render_template(
        "auth/login.html"
    )


# ============================================================
# REGISTER
# ============================================================

@auth_bp.route(
    "/register",
    methods=["GET", "POST"],
)
def register():
    """
    Create a new AI Coding Teammate account.
    """

    # --------------------------------------------------------
    # Already authenticated
    # --------------------------------------------------------

    if current_user.is_authenticated:

        return redirect(
            url_for(
                "dashboard.dashboard"
            )
        )

    # --------------------------------------------------------
    # Registration submission
    # --------------------------------------------------------

    if request.method == "POST":

        first_name = (
            request.form.get(
                "first_name",
                "",
            )
            .strip()
        )

        last_name = (
            request.form.get(
                "last_name",
                "",
            )
            .strip()
        )

        email = (
            request.form.get(
                "email",
                "",
            )
            .strip()
            .lower()
        )

        password = request.form.get(
            "password",
            "",
        )

        confirm_password = request.form.get(
            "confirm_password",
            "",
        )

        occupation = (
            request.form.get(
                "occupation",
                "",
            )
            .strip()
        )

        bio = (
            request.form.get(
                "bio",
                "",
            )
            .strip()
        )

        # Keep the terms field from your original route.
        terms = request.form.get(
            "terms"
        )

        # ----------------------------------------------------
        # Validate first name
        # ----------------------------------------------------

        if not first_name:

            flash(
                "Please enter your first name.",
                "danger",
            )

            return render_template(
                "auth/register.html",
                form=request.form,
            )

        # ----------------------------------------------------
        # Validate last name
        # ----------------------------------------------------

        if not last_name:

            flash(
                "Please enter your last name.",
                "danger",
            )

            return render_template(
                "auth/register.html",
                form=request.form,
            )

        # ----------------------------------------------------
        # Validate email
        # ----------------------------------------------------

        if not email:

            flash(
                "Please enter your email address.",
                "danger",
            )

            return render_template(
                "auth/register.html",
                form=request.form,
            )

        # ----------------------------------------------------
        # Validate password
        # ----------------------------------------------------

        if not password:

            flash(
                "Please enter a password.",
                "danger",
            )

            return render_template(
                "auth/register.html",
                form=request.form,
            )

        if len(password) < 8:

            flash(
                "Password must contain at least "
                "8 characters.",
                "danger",
            )

            return render_template(
                "auth/register.html",
                form=request.form,
            )

        # ----------------------------------------------------
        # Password confirmation
        # ----------------------------------------------------

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "danger",
            )

            return render_template(
                "auth/register.html",
                form=request.form,
            )

        # ----------------------------------------------------
        # Terms and conditions
        # ----------------------------------------------------

        if not terms:

            flash(
                "You must accept the terms and conditions.",
                "danger",
            )

            return render_template(
                "auth/register.html",
                form=request.form,
            )

        # ----------------------------------------------------
        # Existing account
        # ----------------------------------------------------

        try:

            existing_user = UserService.get_by_email(
                email
            )

        except Exception:

            flash(
                "Unable to check your account information "
                "right now. Please try again.",
                "danger",
            )

            return render_template(
                "auth/register.html",
                form=request.form,
            )

        if existing_user:

            flash(
                "An account with this email already exists.",
                "warning",
            )

            return render_template(
                "auth/register.html",
                form=request.form,
            )

        # ----------------------------------------------------
        # Create account
        # ----------------------------------------------------

        try:

            user = UserService.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                occupation=occupation or None,
                bio=bio or None,
            )

        except ValueError as error:

            flash(
                str(error),
                "danger",
            )

            return render_template(
                "auth/register.html",
                form=request.form,
            )

        except Exception:

            flash(
                "An unexpected error occurred while "
                "creating your account. Please try again.",
                "danger",
            )

            return render_template(
                "auth/register.html",
                form=request.form,
            )

        # ----------------------------------------------------
        # Automatically login new user
        #
        # This preserves the behavior of your original
        # auth_routes.py.
        # ----------------------------------------------------

        login_user(
            user
        )

        flash(
            "Your account has been created successfully.",
            "success",
        )

        # ----------------------------------------------------
        # Go directly to dashboard
        # ----------------------------------------------------

        return redirect(
            url_for(
                "dashboard.dashboard"
            )
        )

    # --------------------------------------------------------
    # GET request
    # --------------------------------------------------------

    return render_template(
        "auth/register.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@auth_bp.route(
    "/logout"
)
@login_required
def logout():
    """
    End the current user's authenticated session.
    """

    logout_user()

    flash(
        "You have been logged out.",
        "info",
    )

    # Preserve the behavior of your original file:
    # return to the homepage.

    return redirect(
        url_for(
            "main.index"
        )
    )


# ============================================================
# FORGOT PASSWORD
# ============================================================

@auth_bp.route(
    "/forgot-password",
    methods=["GET", "POST"],
)
def forgot_password():
    """
    Request password reset instructions.

    The response deliberately does not reveal whether
    an email address exists in the database.
    """

    if current_user.is_authenticated:

        return redirect(
            url_for(
                "dashboard.dashboard"
            )
        )

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == "POST":

        email = (
            request.form.get(
                "email",
                "",
            )
            .strip()
            .lower()
        )

        # ----------------------------------------------------
        # Validate email
        # ----------------------------------------------------

        if not email:

            flash(
                "Please enter your email address.",
                "danger",
            )

            return render_template(
                "auth/forgot_password.html"
            )

        # ----------------------------------------------------
        # Find user
        # ----------------------------------------------------

        try:

            user = UserService.get_by_email(
                email
            )

        except Exception:

            # Do not reveal internal database errors.
            user = None

        # ----------------------------------------------------
        # Existing user
        # ----------------------------------------------------

        if user:

            # =================================================
            # PASSWORD RESET EMAIL
            # =================================================
            #
            # This is intentionally not activated yet.
            #
            # Later:
            #
            # from services.password_reset_service import (
            #     PasswordResetService,
            # )
            #
            # from services.email_service import EmailService
            #
            #
            # token = (
            #     PasswordResetService.generate_token(user)
            # )
            #
            #
            # reset_url = url_for(
            #     "auth.reset_password",
            #     token=token,
            #     _external=True,
            # )
            #
            #
            # EmailService.send_password_reset(
            #     email=user.email,
            #     reset_url=reset_url,
            # )
            #
            # =================================================

            pass

        # ----------------------------------------------------
        # Generic response
        #
        # Never reveal whether the account exists.
        # ----------------------------------------------------

        flash(
            "If an account exists for that email, "
            "password reset instructions will be sent.",
            "info",
        )

        # ----------------------------------------------------
        # IMPORTANT
        #
        # Your existing project does not currently require
        # reset_password_sent.html.
        #
        # Redirect to login to avoid TemplateNotFound.
        # ----------------------------------------------------

        return redirect(
            url_for(
                "auth.login"
            )
        )

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    return render_template(
        "auth/forgot_password.html"
    )


# ============================================================
# RESET PASSWORD
# ============================================================

@auth_bp.route(
    "/reset-password/<token>",
    methods=["GET", "POST"],
)
def reset_password(token):
    """
    Reset a user's password.

    IMPORTANT:

    Password reset remains disabled until the token is
    securely verified.

    A reset token must NEVER be treated directly as a
    database user ID.
    """

    if current_user.is_authenticated:

        return redirect(
            url_for(
                "dashboard.dashboard"
            )
        )

    # --------------------------------------------------------
    # Token required
    # --------------------------------------------------------

    if not token:

        flash(
            "The password reset link is invalid.",
            "danger",
        )

        return redirect(
            url_for(
                "auth.forgot_password"
            )
        )

    # ========================================================
    # SECURE TOKEN VERIFICATION
    # ========================================================
    #
    # We will replace this section when we create:
    #
    # services/password_reset_service.py
    #
    #
    # Future:
    #
    # user_id = PasswordResetService.verify_token(token)
    #
    #
    # Until verification exists, do NOT allow a password
    # change.
    # ========================================================

    user_id = None

    # --------------------------------------------------------
    # Invalid / unverified token
    # --------------------------------------------------------

    if not user_id:

        flash(
            "This password reset link is invalid "
            "or has expired.",
            "danger",
        )

        return redirect(
            url_for(
                "auth.forgot_password"
            )
        )

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == "POST":

        password = request.form.get(
            "password",
            "",
        )

        confirm_password = request.form.get(
            "confirm_password",
            "",
        )

        # ----------------------------------------------------
        # Password required
        # ----------------------------------------------------

        if not password:

            flash(
                "Please enter a new password.",
                "danger",
            )

            return render_template(
                "auth/reset_password.html",
                token=token,
            )

        # ----------------------------------------------------
        # Minimum password length
        # ----------------------------------------------------

        if len(password) < 8:

            flash(
                "Password must contain at least "
                "8 characters.",
                "danger",
            )

            return render_template(
                "auth/reset_password.html",
                token=token,
            )

        # ----------------------------------------------------
        # Password confirmation
        # ----------------------------------------------------

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "danger",
            )

            return render_template(
                "auth/reset_password.html",
                token=token,
            )

        # ----------------------------------------------------
        # Reset password
        # ----------------------------------------------------

        try:

            UserService.reset_password(
                user_id=user_id,
                new_password=password,
            )

        except ValueError as error:

            flash(
                str(error),
                "danger",
            )

            return render_template(
                "auth/reset_password.html",
                token=token,
            )

        except Exception:

            flash(
                "Unable to reset your password. "
                "Please try again.",
                "danger",
            )

            return render_template(
                "auth/reset_password.html",
                token=token,
            )

        # ----------------------------------------------------
        # Success
        # ----------------------------------------------------

        flash(
            "Your password has been reset successfully. "
            "You can now log in.",
            "success",
        )

        return redirect(
            url_for(
                "auth.login"
            )
        )

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    return render_template(
        "auth/reset_password.html",
        token=token,
    )