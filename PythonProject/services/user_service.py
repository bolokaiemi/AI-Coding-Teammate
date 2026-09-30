"""
User Service
============

Handles:

- User creation
- User retrieval
- Authentication
- Password verification
- Profile updates
- Password changes
- Password resets after token verification
- Account activation/deactivation
- Account verification
"""

from datetime import datetime, timezone

from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)

from database.database import db
from database.models import User


class UserService:
    """Business logic for application users."""

    # =========================================================
    # GET USER BY ID
    # =========================================================

    @staticmethod
    def get_by_id(user_id):
        """
        Return a user by database ID.

        Returns None when the ID is invalid or the user
        does not exist.
        """

        if not user_id:
            return None

        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            return None

        return db.session.get(
            User,
            user_id,
        )

    # =========================================================
    # GET USER BY EMAIL
    # =========================================================

    @staticmethod
    def get_by_email(email):
        """
        Return a user by email address.

        Email addresses are normalized to lowercase.
        """

        if not email:
            return None

        normalized_email = (
            str(email)
            .strip()
            .lower()
        )

        if not normalized_email:
            return None

        return User.query.filter_by(
            email=normalized_email
        ).first()

    # =========================================================
    # CREATE USER
    # =========================================================

    @staticmethod
    def create_user(
        first_name,
        last_name,
        email,
        password,
        occupation=None,
        bio=None,
    ):
        """
        Create and persist a new user.

        Passwords are never stored as plain text.
        """

        first_name = (
            str(first_name).strip()
            if first_name
            else ""
        )

        last_name = (
            str(last_name).strip()
            if last_name
            else ""
        )

        normalized_email = (
            str(email).strip().lower()
            if email
            else ""
        )

        # -----------------------------------------------------
        # Validation
        # -----------------------------------------------------

        if not first_name:
            raise ValueError(
                "First name is required."
            )

        if not last_name:
            raise ValueError(
                "Last name is required."
            )

        if not normalized_email:
            raise ValueError(
                "Email address is required."
            )

        if not password:
            raise ValueError(
                "Password is required."
            )

        if len(password) < 8:
            raise ValueError(
                "Password must contain at least 8 characters."
            )

        # -----------------------------------------------------
        # Duplicate email check
        # -----------------------------------------------------

        existing_user = (
            UserService.get_by_email(
                normalized_email
            )
        )

        if existing_user:
            raise ValueError(
                "A user with this email already exists."
            )

        # -----------------------------------------------------
        # Create user
        # -----------------------------------------------------

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=normalized_email,
            password=generate_password_hash(
                password
            ),
            occupation=(
                occupation.strip()
                if occupation
                else None
            ),
            bio=(
                bio.strip()
                if bio
                else None
            ),
        )

        try:
            db.session.add(user)
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return user

    # =========================================================
    # VERIFY PASSWORD
    # =========================================================

    @staticmethod
    def verify_password(
        user,
        password,
    ):
        """
        Check a plain-text password against the user's
        stored password hash.
        """

        if not user:
            return False

        if not password:
            return False

        if not getattr(
            user,
            "password",
            None,
        ):
            return False

        try:
            return check_password_hash(
                user.password,
                password,
            )

        except (
            ValueError,
            TypeError,
        ):
            return False

    # =========================================================
    # AUTHENTICATE
    # =========================================================

    @staticmethod
    def authenticate(
        email,
        password,
    ):
        """
        Authenticate a user.

        Returns:
            User instance when credentials are valid.
            None when authentication fails.
        """

        if not email or not password:
            return None

        user = (
            UserService.get_by_email(
                email
            )
        )

        if not user:
            return None

        # -----------------------------------------------------
        # Check account status
        # -----------------------------------------------------

        if not user.is_active:
            return None

        # -----------------------------------------------------
        # Verify password
        # -----------------------------------------------------

        if not UserService.verify_password(
            user,
            password,
        ):
            return None

        # -----------------------------------------------------
        # Update login timestamp
        # -----------------------------------------------------

        user.last_login = (
            datetime.now(
                timezone.utc
            )
        )

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return user

    # =========================================================
    # UPDATE PROFILE
    # =========================================================

    @staticmethod
    def update_profile(
        user_id,
        first_name=None,
        last_name=None,
        email=None,
        occupation=None,
        bio=None,
        profile_image=None,
    ):
        """
        Update a user's profile.
        """

        user = (
            UserService.get_by_id(
                user_id
            )
        )

        if not user:
            raise ValueError(
                "User not found."
            )

        # -----------------------------------------------------
        # First name
        # -----------------------------------------------------

        if first_name is not None:

            first_name = (
                first_name.strip()
            )

            if not first_name:
                raise ValueError(
                    "First name cannot be empty."
                )

            user.first_name = (
                first_name
            )

        # -----------------------------------------------------
        # Last name
        # -----------------------------------------------------

        if last_name is not None:

            last_name = (
                last_name.strip()
            )

            if not last_name:
                raise ValueError(
                    "Last name cannot be empty."
                )

            user.last_name = (
                last_name
            )

        # -----------------------------------------------------
        # Email
        # -----------------------------------------------------

        if email is not None:

            normalized_email = (
                email.strip().lower()
            )

            if not normalized_email:
                raise ValueError(
                    "Email cannot be empty."
                )

            existing_user = (
                UserService.get_by_email(
                    normalized_email
                )
            )

            if (
                existing_user
                and
                existing_user.id
                != user.id
            ):
                raise ValueError(
                    "Another account already uses this email."
                )

            user.email = (
                normalized_email
            )

        # -----------------------------------------------------
        # Occupation
        # -----------------------------------------------------

        if occupation is not None:

            user.occupation = (
                occupation.strip()
                or None
            )

        # -----------------------------------------------------
        # Bio
        # -----------------------------------------------------

        if bio is not None:

            user.bio = (
                bio.strip()
                or None
            )

        # -----------------------------------------------------
        # Profile image
        # -----------------------------------------------------

        if profile_image is not None:

            user.profile_image = (
                profile_image
            )

        user.updated_at = (
            datetime.now(
                timezone.utc
            )
        )

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return user

    # =========================================================
    # CHANGE PASSWORD
    # =========================================================

    @staticmethod
    def change_password(
        user_id,
        current_password,
        new_password,
    ):
        """
        Change the password of an authenticated user.

        The current password must be verified first.
        """

        user = (
            UserService.get_by_id(
                user_id
            )
        )

        if not user:
            raise ValueError(
                "User not found."
            )

        # -----------------------------------------------------
        # Verify existing password
        # -----------------------------------------------------

        if not UserService.verify_password(
            user,
            current_password,
        ):
            raise ValueError(
                "Current password is incorrect."
            )

        # -----------------------------------------------------
        # Validate new password
        # -----------------------------------------------------

        if not new_password:
            raise ValueError(
                "New password is required."
            )

        if len(new_password) < 8:
            raise ValueError(
                "New password must contain at least 8 characters."
            )

        if UserService.verify_password(
            user,
            new_password,
        ):
            raise ValueError(
                "The new password must be different "
                "from the current password."
            )

        # -----------------------------------------------------
        # Update password
        # -----------------------------------------------------

        user.password = (
            generate_password_hash(
                new_password
            )
        )

        user.updated_at = (
            datetime.now(
                timezone.utc
            )
        )

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return True

    # =========================================================
    # RESET PASSWORD
    # =========================================================

    @staticmethod
    def reset_password(
        user_id,
        new_password,
    ):
        """
        Reset a user's password.

        IMPORTANT:
        This method must only be called AFTER a password
        reset token has been successfully verified.
        """

        user = (
            UserService.get_by_id(
                user_id
            )
        )

        if not user:
            raise ValueError(
                "User not found."
            )

        if not new_password:
            raise ValueError(
                "New password is required."
            )

        if len(new_password) < 8:
            raise ValueError(
                "New password must contain at least 8 characters."
            )

        user.password = (
            generate_password_hash(
                new_password
            )
        )

        user.updated_at = (
            datetime.now(
                timezone.utc
            )
        )

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return True

    # =========================================================
    # DEACTIVATE ACCOUNT
    # =========================================================

    @staticmethod
    def deactivate_user(user_id):
        """
        Disable a user account.
        """

        user = (
            UserService.get_by_id(
                user_id
            )
        )

        if not user:
            raise ValueError(
                "User not found."
            )

        user.is_active = False

        user.updated_at = (
            datetime.now(
                timezone.utc
            )
        )

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return user

    # =========================================================
    # ACTIVATE ACCOUNT
    # =========================================================

    @staticmethod
    def activate_user(user_id):
        """
        Enable a previously disabled user account.
        """

        user = (
            UserService.get_by_id(
                user_id
            )
        )

        if not user:
            raise ValueError(
                "User not found."
            )

        user.is_active = True

        user.updated_at = (
            datetime.now(
                timezone.utc
            )
        )

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return user

    # =========================================================
    # MARK ACCOUNT VERIFIED
    # =========================================================

    @staticmethod
    def mark_verified(user_id):
        """
        Mark a user's account/email as verified.
        """

        user = (
            UserService.get_by_id(
                user_id
            )
        )

        if not user:
            raise ValueError(
                "User not found."
            )

        user.is_verified = True

        user.updated_at = (
            datetime.now(
                timezone.utc
            )
        )

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return user