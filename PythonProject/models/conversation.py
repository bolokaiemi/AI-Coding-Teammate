# ============================================================
# AI Coding Teammate
# ai/conversion.py
#
# Data conversion and normalization utilities for the AI layer.
# ============================================================

from __future__ import annotations

import base64
import io
import json
import mimetypes
import re
from pathlib import Path
from typing import Any

from PIL import Image


# ============================================================
# CONFIGURATION
# ============================================================

MAX_TEXT_SIZE = 2_000_000       # 2 MB
MAX_IMAGE_SIZE = 10_000_000     # 10 MB
MAX_IMAGE_DIMENSION = 1600

SUPPORTED_TEXT_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".html",
    ".htm",
    ".css",
    ".scss",
    ".json",
    ".md",
    ".txt",
    ".sql",
    ".java",
    ".c",
    ".cpp",
    ".cc",
    ".h",
    ".hpp",
    ".go",
    ".rs",
    ".php",
    ".rb",
    ".sh",
    ".yaml",
    ".yml",
    ".xml",
    ".toml",
    ".ini",
    ".cfg",
}

SUPPORTED_IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".bmp",
}


# ============================================================
# CUSTOM EXCEPTION
# ============================================================

class ConversionError(Exception):
    """
    Raised when incoming data cannot safely be converted.
    """

    pass


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(
    text: str | bytes | None,
) -> str:
    """
    Convert incoming text into a normalized UTF-8 string.
    """

    if text is None:
        return ""

    if isinstance(text, bytes):

        try:
            text = text.decode("utf-8")

        except UnicodeDecodeError:
            text = text.decode(
                "utf-8",
                errors="replace",
            )

    if not isinstance(text, str):
        text = str(text)

    # Normalize newlines.
    text = text.replace(
        "\r\n",
        "\n",
    ).replace(
        "\r",
        "\n",
    )

    # Remove null bytes.
    text = text.replace(
        "\x00",
        "",
    )

    return text


# ============================================================
# CODE NORMALIZATION
# ============================================================

def normalize_code(
    code: str | bytes | None,
) -> str:
    """
    Normalize source code without changing its meaning.
    """

    code = normalize_text(code)

    if not code:
        return ""

    lines = code.splitlines()

    cleaned_lines = []

    for line in lines:

        # Remove trailing whitespace but preserve indentation.
        cleaned_lines.append(
            line.rstrip()
        )

    return "\n".join(
        cleaned_lines
    )


# ============================================================
# LANGUAGE DETECTION
# ============================================================

def language_from_filename(
    filename: str | None,
) -> str:
    """
    Determine programming language from filename extension.
    """

    if not filename:
        return "unknown"

    extension = Path(
        filename
    ).suffix.lower()

    language_map = {
        ".py": "python",

        ".js": "javascript",
        ".jsx": "javascript",

        ".ts": "typescript",
        ".tsx": "typescript",

        ".html": "html",
        ".htm": "html",

        ".css": "css",
        ".scss": "scss",

        ".json": "json",

        ".sql": "sql",

        ".java": "java",

        ".c": "c",

        ".cpp": "cpp",
        ".cc": "cpp",

        ".h": "c",
        ".hpp": "cpp",

        ".go": "go",

        ".rs": "rust",

        ".php": "php",

        ".rb": "ruby",

        ".sh": "shell",

        ".md": "markdown",

        ".yaml": "yaml",
        ".yml": "yaml",

        ".xml": "xml",

        ".toml": "toml",

        ".txt": "text",
    }

    return language_map.get(
        extension,
        "unknown",
    )


# ============================================================
# SAFE FILE NAME
# ============================================================

def safe_filename(
    filename: str,
) -> str:
    """
    Remove directory components and dangerous characters from
    an incoming filename.

    This is not a replacement for full upload validation.
    """

    filename = Path(
        filename
    ).name

    filename = filename.strip()

    filename = re.sub(
        r"[^A-Za-z0-9._\- ]",
        "_",
        filename,
    )

    if not filename:
        filename = "untitled"

    return filename


# ============================================================
# FILE TYPE
# ============================================================

def detect_file_type(
    filename: str,
) -> str:
    """
    Determine the general file category.
    """

    extension = Path(
        filename
    ).suffix.lower()

    if extension in SUPPORTED_TEXT_EXTENSIONS:
        return "text"

    if extension in SUPPORTED_IMAGE_EXTENSIONS:
        return "image"

    return "unknown"


# ============================================================
# READ TEXT FILE
# ============================================================

def read_text_file(
    file_path: str | Path,
) -> dict[str, Any]:
    """
    Read a source-code or text file.
    """

    path = Path(
        file_path
    )

    if not path.exists():
        raise ConversionError(
            f"File does not exist: {path}"
        )

    if not path.is_file():
        raise ConversionError(
            "The supplied path is not a file."
        )

    if path.stat().st_size > MAX_TEXT_SIZE:
        raise ConversionError(
            "The text file is too large."
        )

    extension = path.suffix.lower()

    if extension not in SUPPORTED_TEXT_EXTENSIONS:
        raise ConversionError(
            f"Unsupported text file type: {extension}"
        )

    try:

        content = path.read_text(
            encoding="utf-8",
        )

    except UnicodeDecodeError:

        content = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

    content = normalize_code(
        content
    )

    return {
        "type": "code",
        "filename": path.name,
        "language": language_from_filename(
            path.name
        ),
        "content": content,
        "size": path.stat().st_size,
    }


# ============================================================
# BYTES -> BASE64
# ============================================================

def bytes_to_base64(
    data: bytes,
) -> str:
    """
    Convert raw bytes to Base64.
    """

    if not isinstance(
        data,
        bytes,
    ):
        raise ConversionError(
            "Expected bytes."
        )

    return base64.b64encode(
        data
    ).decode(
        "utf-8"
    )


# ============================================================
# BASE64 -> BYTES
# ============================================================

def base64_to_bytes(
    data: str,
) -> bytes:
    """
    Convert Base64 string into raw bytes.
    """

    if not data:
        raise ConversionError(
            "Base64 data is empty."
        )

    try:

        return base64.b64decode(
            data,
            validate=True,
        )

    except Exception as error:

        raise ConversionError(
            "Invalid Base64 data."
        ) from error


# ============================================================
# PARSE DATA URL
# ============================================================

def parse_data_url(
    data_url: str,
) -> tuple[str, bytes]:
    """
    Convert a browser Data URL into MIME type and raw bytes.

    Example:

        data:image/jpeg;base64,/9j/4AAQ...
    """

    if not data_url:
        raise ConversionError(
            "Data URL is empty."
        )

    match = re.match(
        r"^data:([^;,]+);base64,(.+)$",
        data_url,
        flags=re.DOTALL,
    )

    if not match:
        raise ConversionError(
            "Invalid Data URL."
        )

    mime_type = match.group(1)

    encoded_data = match.group(2)

    try:

        raw_data = base64.b64decode(
            encoded_data
        )

    except Exception as error:

        raise ConversionError(
            "Unable to decode Data URL."
        ) from error

    return (
        mime_type,
        raw_data,
    )


# ============================================================
# IMAGE BYTES -> PIL IMAGE
# ============================================================

def bytes_to_image(
    data: bytes,
) -> Image.Image:
    """
    Convert image bytes into a Pillow Image object.
    """

    if len(data) > MAX_IMAGE_SIZE:
        raise ConversionError(
            "Image is too large."
        )

    try:

        image = Image.open(
            io.BytesIO(data)
        )

        image.load()

        return image.convert(
            "RGB"
        )

    except Exception as error:

        raise ConversionError(
            "Unable to decode image."
        ) from error


# ============================================================
# BASE64 -> IMAGE
# ============================================================

def base64_to_image(
    data: str,
) -> Image.Image:
    """
    Convert Base64 image data into a Pillow image.
    """

    raw_data = base64_to_bytes(
        data
    )

    return bytes_to_image(
        raw_data
    )


# ============================================================
# DATA URL -> IMAGE
# ============================================================

def data_url_to_image(
    data_url: str,
) -> Image.Image:
    """
    Convert browser canvas/camera/screen Data URL into an image.
    """

    mime_type, raw_data = parse_data_url(
        data_url
    )

    if not mime_type.startswith(
        "image/"
    ):
        raise ConversionError(
            "Data URL does not contain an image."
        )

    return bytes_to_image(
        raw_data
    )


# ============================================================
# RESIZE IMAGE
# ============================================================

def resize_image(
    image: Image.Image,
    max_dimension: int = MAX_IMAGE_DIMENSION,
) -> Image.Image:
    """
    Resize an image while preserving aspect ratio.

    Large screen/camera frames do not usually need to be sent
    to the AI model at their original resolution.
    """

    width, height = image.size

    if (
        width <= max_dimension
        and height <= max_dimension
    ):
        return image

    image = image.copy()

    image.thumbnail(
        (
            max_dimension,
            max_dimension,
        ),
        Image.Resampling.LANCZOS,
    )

    return image


# ============================================================
# IMAGE -> BYTES
# ============================================================

def image_to_bytes(
    image: Image.Image,
    image_format: str = "JPEG",
    quality: int = 85,
) -> bytes:
    """
    Convert a Pillow image into encoded image bytes.
    """

    output = io.BytesIO()

    image = image.convert(
        "RGB"
    )

    image.save(
        output,
        format=image_format,
        quality=quality,
        optimize=True,
    )

    return output.getvalue()


# ============================================================
# IMAGE -> BASE64
# ============================================================

def image_to_base64(
    image: Image.Image,
    image_format: str = "JPEG",
    quality: int = 85,
) -> str:
    """
    Convert Pillow image into Base64.
    """

    image_bytes = image_to_bytes(
        image=image,
        image_format=image_format,
        quality=quality,
    )

    return bytes_to_base64(
        image_bytes
    )


# ============================================================
# PREPARE CAMERA FRAME
# ============================================================

def prepare_camera_frame(
    data_url: str,
) -> dict[str, Any]:
    """
    Convert a camera frame received from JavaScript into a
    normalized image payload.
    """

    image = data_url_to_image(
        data_url
    )

    image = resize_image(
        image
    )

    encoded = image_to_base64(
        image
    )

    return {
        "type": "image",
        "source": "camera",
        "mime_type": "image/jpeg",
        "width": image.width,
        "height": image.height,
        "base64": encoded,
    }


# ============================================================
# PREPARE SCREEN FRAME
# ============================================================

def prepare_screen_frame(
    data_url: str,
) -> dict[str, Any]:
    """
    Convert a screen-share frame received from JavaScript into
    an AI-ready image payload.
    """

    image = data_url_to_image(
        data_url
    )

    image = resize_image(
        image
    )

    encoded = image_to_base64(
        image
    )

    return {
        "type": "image",
        "source": "screen",
        "mime_type": "image/jpeg",
        "width": image.width,
        "height": image.height,
        "base64": encoded,
    }


# ============================================================
# READ IMAGE FILE
# ============================================================

def read_image_file(
    file_path: str | Path,
) -> dict[str, Any]:
    """
    Convert an uploaded image into an AI-ready payload.
    """

    path = Path(
        file_path
    )

    if not path.exists():
        raise ConversionError(
            f"Image does not exist: {path}"
        )

    if not path.is_file():
        raise ConversionError(
            "Image path is not a file."
        )

    if path.stat().st_size > MAX_IMAGE_SIZE:
        raise ConversionError(
            "Image file is too large."
        )

    extension = path.suffix.lower()

    if extension not in SUPPORTED_IMAGE_EXTENSIONS:
        raise ConversionError(
            f"Unsupported image type: {extension}"
        )

    try:

        with Image.open(path) as source_image:
            image = source_image.convert(
                "RGB"
            )

    except Exception as error:

        raise ConversionError(
            "Unable to read uploaded image."
        ) from error

    image = resize_image(
        image
    )

    encoded = image_to_base64(
        image
    )

    return {
        "type": "image",
        "source": "upload",
        "filename": path.name,
        "mime_type": "image/jpeg",
        "width": image.width,
        "height": image.height,
        "base64": encoded,
    }


# ============================================================
# CONVERT UPLOADED FILE
# ============================================================

def convert_file(
    file_path: str | Path,
) -> dict[str, Any]:
    """
    Automatically convert a supported file into the correct
    AI payload.
    """

    path = Path(
        file_path
    )

    file_type = detect_file_type(
        path.name
    )

    if file_type == "text":

        return read_text_file(
            path
        )

    if file_type == "image":

        return read_image_file(
            path
        )

    raise ConversionError(
        f"Unsupported file type: {path.suffix}"
    )


# ============================================================
# CODE -> AI PAYLOAD
# ============================================================

def code_to_ai_payload(
    code: str,
    filename: str | None = None,
    language: str | None = None,
) -> dict[str, Any]:
    """
    Convert editor code into a consistent AI request structure.
    """

    normalized_code = normalize_code(
        code
    )

    detected_language = (
        language
        or language_from_filename(
            filename
        )
    )

    return {
        "type": "code",
        "filename": (
            safe_filename(filename)
            if filename
            else None
        ),
        "language": detected_language,
        "content": normalized_code,
    }


# ============================================================
# CHAT MESSAGE -> AI FORMAT
# ============================================================

def chat_message_to_ai_format(
    role: str,
    message: str,
) -> dict[str, str]:
    """
    Normalize a chat message before sending it to an LLM.
    """

    allowed_roles = {
        "system",
        "user",
        "assistant",
    }

    if role not in allowed_roles:
        role = "user"

    message = normalize_text(
        message
    ).strip()

    return {
        "role": role,
        "content": message,
    }


# ============================================================
# CHAT HISTORY -> AI FORMAT
# ============================================================

def conversation_to_ai_format(
    messages: list[Any],
    limit: int = 20,
) -> list[dict[str, str]]:
    """
    Convert CodeSession chat history into a standard LLM-style
    conversation format.

    Supports dictionaries and ChatRecord-like objects.
    """

    converted = []

    for message in messages[-limit:]:

        if isinstance(
            message,
            dict,
        ):

            role = message.get(
                "role",
                "user",
            )

            content = (
                message.get("message")
                or message.get("content")
                or ""
            )

        else:

            role = getattr(
                message,
                "role",
                "user",
            )

            content = getattr(
                message,
                "message",
                "",
            )

        converted.append(
            chat_message_to_ai_format(
                role=role,
                message=content,
            )
        )

    return converted


# ============================================================
# ANALYSIS RESULT -> JSON
# ============================================================

def analysis_to_json(
    analysis: dict[str, Any],
    pretty: bool = False,
) -> str:
    """
    Serialize an analysis result.
    """

    return json.dumps(
        analysis,
        ensure_ascii=False,
        indent=2 if pretty else None,
        default=str,
    )


# ============================================================
# JSON -> DICTIONARY
# ============================================================

def json_to_dict(
    data: str | bytes,
) -> dict[str, Any]:
    """
    Convert JSON input into a Python dictionary.
    """

    data = normalize_text(
        data
    )

    try:

        result = json.loads(
            data
        )

    except json.JSONDecodeError as error:

        raise ConversionError(
            "Invalid JSON data."
        ) from error

    if not isinstance(
        result,
        dict,
    ):
        raise ConversionError(
            "JSON root must be an object."
        )

    return result


# ============================================================
# CREATE MULTIMODAL AI PAYLOAD
# ============================================================

def create_multimodal_payload(
    prompt: str,
    code: str | None = None,
    filename: str | None = None,
    language: str | None = None,
    image_base64: str | None = None,
    image_source: str | None = None,
) -> dict[str, Any]:
    """
    Build a generic multimodal request.

    The provider/model layer can later translate this generic
    structure into the exact format required by the chosen
    multimodal AI model.
    """

    payload: dict[str, Any] = {
        "prompt": normalize_text(
            prompt
        ).strip(),
        "inputs": [],
    }

    if code:

        payload["inputs"].append(
            code_to_ai_payload(
                code=code,
                filename=filename,
                language=language,
            )
        )

    if image_base64:

        payload["inputs"].append(
            {
                "type": "image",
                "source": (
                    image_source
                    or "unknown"
                ),
                "mime_type": "image/jpeg",
                "base64": image_base64,
            }
        )

    return payload


# ============================================================
# SESSION -> AI PAYLOAD
# ============================================================

def session_to_ai_payload(
    coding_session: Any,
    prompt: str,
    message_limit: int = 10,
) -> dict[str, Any]:
    """
    Convert a CodeSession object into a payload for the
    AI/model layer.
    """

    payload: dict[str, Any] = {
        "session_id": getattr(
            coding_session,
            "id",
            None,
        ),

        "prompt": normalize_text(
            prompt
        ).strip(),

        "project": {
            "id": getattr(
                coding_session,
                "project_id",
                None,
            ),

            "name": getattr(
                coding_session,
                "project_name",
                None,
            ),
        },

        "current_file": None,

        "conversation": [],

        "media": {
            "screen_sharing": getattr(
                coding_session,
                "screen_sharing",
                False,
            ),

            "camera_active": getattr(
                coding_session,
                "camera_active",
                False,
            ),

            "voice_active": getattr(
                coding_session,
                "voice_active",
                False,
            ),
        },
    }

    code = getattr(
        coding_session,
        "code",
        "",
    )

    if code:

        payload["current_file"] = (
            code_to_ai_payload(
                code=code,

                filename=getattr(
                    coding_session,
                    "filename",
                    None,
                ),

                language=getattr(
                    coding_session,
                    "language",
                    None,
                ),
            )
        )

    messages = getattr(
        coding_session,
        "messages",
        [],
    )

    payload["conversation"] = (
        conversation_to_ai_format(
            messages,
            limit=message_limit,
        )
    )

    return payload


# ============================================================
# GET MIME TYPE
# ============================================================

def get_mime_type(
    filename: str,
) -> str:
    """
    Determine MIME type from filename.
    """

    mime_type, _ = mimetypes.guess_type(
        filename
    )

    return (
        mime_type
        or "application/octet-stream"
    )


# ============================================================
# DEVELOPMENT TEST
# ============================================================

if __name__ == "__main__":

    example_code = """
def calculate_total(price, tax):
    total = price + taxes
    return total
"""

    payload = code_to_ai_payload(
        code=example_code,
        filename="example.py",
    )

    print(
        analysis_to_json(
            payload,
            pretty=True,
        )
    )