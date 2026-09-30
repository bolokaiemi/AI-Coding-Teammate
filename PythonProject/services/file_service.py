"""
File Service

Handles uploaded code files, screenshots, images, and videos.

Security responsibilities include:
    - validating extensions
    - preventing unsafe filenames
    - controlling upload locations
    - preventing path traversal
    - limiting file types

Actual AI analysis is handled by the AI layer.
"""

import os
import uuid
from pathlib import Path

from werkzeug.utils import secure_filename


class FileService:
    """Business logic for uploaded files."""

    ALLOWED_EXTENSIONS = {
        "py",
        "js",
        "ts",
        "tsx",
        "jsx",
        "html",
        "htm",
        "css",
        "scss",
        "sass",
        "json",
        "xml",
        "yaml",
        "yml",
        "md",
        "txt",
        "sql",
        "java",
        "c",
        "cpp",
        "h",
        "hpp",
        "cs",
        "go",
        "rs",
        "php",
        "rb",
        "swift",
        "kt",
        "kts",
        "sh",
        "bat",
        "ps1",
        "jpg",
        "jpeg",
        "png",
        "gif",
        "webp",
        "mp4",
        "webm",
        "mov",
    }

    CODE_EXTENSIONS = {
        "py",
        "js",
        "ts",
        "tsx",
        "jsx",
        "html",
        "htm",
        "css",
        "scss",
        "sass",
        "json",
        "xml",
        "yaml",
        "yml",
        "sql",
        "java",
        "c",
        "cpp",
        "h",
        "hpp",
        "cs",
        "go",
        "rs",
        "php",
        "rb",
        "swift",
        "kt",
        "kts",
        "sh",
        "bat",
        "ps1",
    }

    IMAGE_EXTENSIONS = {
        "jpg",
        "jpeg",
        "png",
        "gif",
        "webp",
    }

    VIDEO_EXTENSIONS = {
        "mp4",
        "webm",
        "mov",
    }

    @staticmethod
    def get_extension(filename):
        """Return the lowercase file extension."""

        if not filename:
            return ""

        return Path(filename).suffix.lower().lstrip(".")

    @classmethod
    def is_allowed_extension(cls, filename):
        """Check whether the file extension is allowed."""

        extension = cls.get_extension(filename)

        return extension in cls.ALLOWED_EXTENSIONS

    @classmethod
    def is_code_file(cls, filename):
        """Check whether a file is a supported source-code file."""

        return cls.get_extension(filename) in cls.CODE_EXTENSIONS

    @classmethod
    def is_image_file(cls, filename):
        """Check whether a file is an image."""

        return cls.get_extension(filename) in cls.IMAGE_EXTENSIONS

    @classmethod
    def is_video_file(cls, filename):
        """Check whether a file is a video."""

        return cls.get_extension(filename) in cls.VIDEO_EXTENSIONS

    @staticmethod
    def sanitize_filename(filename):
        """Return a safe filename."""

        if not filename:
            raise ValueError("Filename is required.")

        safe_name = secure_filename(filename)

        if not safe_name:
            raise ValueError("Invalid filename.")

        return safe_name

    @classmethod
    def generate_unique_filename(cls, filename):
        """
        Generate a collision-resistant safe filename.
        """

        safe_name = cls.sanitize_filename(filename)

        extension = cls.get_extension(safe_name)

        unique_id = uuid.uuid4().hex

        if extension:
            return f"{unique_id}.{extension}"

        return unique_id

    @classmethod
    def validate_upload(cls, filename):
        """
        Validate an uploaded file.

        Returns a metadata dictionary.
        """

        if not filename:
            raise ValueError("No filename supplied.")

        safe_name = cls.sanitize_filename(filename)

        if not cls.is_allowed_extension(safe_name):
            raise ValueError(
                f"File type '.{cls.get_extension(safe_name)}' "
                "is not allowed."
            )

        extension = cls.get_extension(safe_name)

        if extension in cls.CODE_EXTENSIONS:
            file_type = "code"

        elif extension in cls.IMAGE_EXTENSIONS:
            file_type = "image"

        elif extension in cls.VIDEO_EXTENSIONS:
            file_type = "video"

        else:
            file_type = "other"

        return {
            "original_filename": filename,
            "safe_filename": safe_name,
            "extension": extension,
            "type": file_type,
        }

    @classmethod
    def save_upload(cls, file, upload_directory):
        """
        Save an uploaded Werkzeug FileStorage object.

        Returns:
            Dictionary containing saved file metadata.
        """

        if file is None:
            raise ValueError("No file supplied.")

        original_filename = file.filename

        metadata = cls.validate_upload(
            original_filename
        )

        os.makedirs(
            upload_directory,
            exist_ok=True,
        )

        unique_filename = cls.generate_unique_filename(
            original_filename
        )

        destination = os.path.abspath(
            os.path.join(
                upload_directory,
                unique_filename,
            )
        )

        upload_root = os.path.abspath(
            upload_directory
        )

        if not destination.startswith(
            upload_root + os.sep
        ):
            raise ValueError("Invalid upload path.")

        file.save(destination)

        return {
            **metadata,
            "filename": unique_filename,
            "path": destination,
        }

    @staticmethod
    def delete_file(file_path):
        """Delete an uploaded file safely."""

        if not file_path:
            return False

        if os.path.isfile(file_path):
            os.remove(file_path)
            return True

        return False

    @staticmethod
    def get_file_size(file_path):
        """Return file size in bytes."""

        if not file_path or not os.path.isfile(file_path):
            return 0

        return os.path.getsize(file_path)

    @classmethod
    def get_file_category(cls, filename):
        """Return a simple file category."""

        if cls.is_code_file(filename):
            return "code"

        if cls.is_image_file(filename):
            return "image"

        if cls.is_video_file(filename):
            return "video"

        return "other"