"""
User Service

Handles user creation, retrieval, profile updates, authentication,
and account-related database operations.
"""

from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from database.database import db
from database.models import User


class UserService:
    """Business logic for users."""

    @staticmethod
    def get_by_id(user_id):
        """Return a user by ID."""
        if not user_id:
            return None

        return db.session.get(User, int(user_id))

    @staticmethod
    def get_by_email(email):
        """Return a user by email address."""
        if not email:
            return None

        return User.query.filter_by(
            email=email.strip().lower()
        ).first()

    @staticmethod
    def create_user(
        first_name,
        last_name,
        email,
        password,
        occupation=None,
        bio=None,
    ):
        """Create and persist a new user."""

        if not first_name or not last_name:
            raise ValueError("First name and last name are required.")

        if not email:
            raise ValueError("Email address is required.")

        if not password:
            raise ValueError("Password is required.")

        normalized_email = email.strip().lower()

        existing_user = UserService.get_by_email(normalized_email)

        if existing_user:
            raise ValueError("A user with this email already exists.")

        user = User(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            email=normalized_email,
            password=generate_password_hash(password),
            occupation=occupation.strip() if occupation else None,
            bio=bio.strip() if bio else None,
        )

        db.session.add(user)
        db.session.commit()

        return user

    @staticmethod
    def verify_password(user, password):
        """Verify a user's password."""

        if not user or not password:
            return False

        return check_password_hash(user.password, password)

    @staticmethod
    def authenticate(email, password):
        """
        Authenticate a user.

        Returns:
            User instance if credentials are valid.
            None otherwise.
        """

        user = UserService.get_by_email(email)

        if not user:
            return None

        if not user.is_active:
            return None

        if not UserService.verify_password(user, password):
            return None

        user.last_login = datetime.utcnow()
        db.session.commit()

        return user

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
        """Update user profile information."""

        user = UserService.get_by_id(user_id)

        if not user:
            raise ValueError("User not found.")

        if first_name is not None:
            user.first_name = first_name.strip()

        if last_name is not None:
            user.last_name = last_name.strip()

        if email is not None:
            normalized_email = email.strip().lower()

            existing = UserService.get_by_email(normalized_email)

            if existing and existing.id != user.id:
                raise ValueError(
                    "Another account already uses this email."
                )

            user.email = normalized_email

        if occupation is not None:
            user.occupation = occupation.strip()

        if bio is not None:
            user.bio = bio.strip()

        if profile_image is not None:
            user.profile_image = profile_image

        user.updated_at = datetime.utcnow()

        db.session.commit()

        return user

    @staticmethod
    def change_password(user_id, current_password, new_password):
        """Change the user's password."""

        user = UserService.get_by_id(user_id)

        if not user:
            raise ValueError("User not found.")

        if not UserService.verify_password(user, current_password):
            raise ValueError("Current password is incorrect.")

        if not new_password:
            raise ValueError("New password is required.")

        user.password = generate_password_hash(new_password)
        user.updated_at = datetime.utcnow()

        db.session.commit()

        return True

    @staticmethod
    def deactivate_user(user_id):
        """Deactivate a user account."""

        user = UserService.get_by_id(user_id)

        if not user:
            raise ValueError("User not found.")

        user.is_active = False
        user.updated_at = datetime.utcnow()

        db.session.commit()

        return user

    @staticmethod
    def activate_user(user_id):
        """Activate a user account."""

        user = UserService.get_by_id(user_id)

        if not user:
            raise ValueError("User not found.")

        user.is_active = True
        user.updated_at = datetime.utcnow()

        db.session.commit()

        return user

    @staticmethod
    def mark_verified(user_id):
        """Mark a user's email/account as verified."""

        user = UserService.get_by_id(user_id)

        if not user:
            raise ValueError("User not found.")

        user.is_verified = True
        user.updated_at = datetime.utcnow()

        db.session.commit()

        return user