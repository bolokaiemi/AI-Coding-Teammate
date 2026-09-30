"""
Tests for the AI Coding Teammate VisualAnalyzer.

These tests verify that the visual analysis layer:
- initializes correctly
- accepts the shared AI client
- exposes image analysis
- exposes screen analysis
- exposes camera analysis
- handles empty visual data safely

No real camera, screen capture, image upload,
or OpenAI API request is performed.
"""

import pytest

from ai.visual_analyzer import VisualAnalyzer


# ----------------------------------------------------------------------
# Initialization
# ----------------------------------------------------------------------

def test_visual_analyzer_initializes(fake_ai_client):
    """
    VisualAnalyzer should initialize with the supplied AI client.
    """

    analyzer = VisualAnalyzer(
        client=fake_ai_client
    )

    assert analyzer is not None
    assert analyzer.client is fake_ai_client


# ----------------------------------------------------------------------
# Required Methods
# ----------------------------------------------------------------------

def test_visual_analyzer_has_image_method(fake_ai_client):
    """
    VisualAnalyzer should expose analyze_image().
    """

    analyzer = VisualAnalyzer(
        client=fake_ai_client
    )

    assert hasattr(
        analyzer,
        "analyze_image",
    )

    assert callable(
        analyzer.analyze_image
    )


def test_visual_analyzer_has_screen_method(fake_ai_client):
    """
    VisualAnalyzer should expose analyze_screen().
    """

    analyzer = VisualAnalyzer(
        client=fake_ai_client
    )

    assert hasattr(
        analyzer,
        "analyze_screen",
    )

    assert callable(
        analyzer.analyze_screen
    )


def test_visual_analyzer_has_camera_method(fake_ai_client):
    """
    VisualAnalyzer should expose analyze_camera().
    """

    analyzer = VisualAnalyzer(
        client=fake_ai_client
    )

    assert hasattr(
        analyzer,
        "analyze_camera",
    )

    assert callable(
        analyzer.analyze_camera
    )


# ----------------------------------------------------------------------
# Image Analysis
# ----------------------------------------------------------------------

def test_analyze_image_returns_response(fake_ai_client):
    """
    analyze_image() should return a response dictionary.
    """

    analyzer = VisualAnalyzer(
        client=fake_ai_client
    )

    fake_image_data = (
        "data:image/png;base64,"
        "dGVzdC1pbWFnZQ=="
    )

    result = analyzer.analyze_image(
        image_data=fake_image_data,
        context="Developer IDE screenshot",
    )

    assert result is not None
    assert isinstance(result, dict)


def test_analyze_image_without_context(fake_ai_client):
    """
    Image analysis should work without optional context.
    """

    analyzer = VisualAnalyzer(
        client=fake_ai_client
    )

    fake_image_data = (
        "data:image/png;base64,"
        "dGVzdC1pbWFnZQ=="
    )

    result = analyzer.analyze_image(
        image_data=fake_image_data
    )

    assert result is not None
    assert isinstance(result, dict)


# ----------------------------------------------------------------------
# Screen Analysis
# ----------------------------------------------------------------------

def test_analyze_screen_returns_response(
    fake_ai_client,
    sample_code,
):
    """
    Screen analysis should return a response dictionary.
    """

    analyzer = VisualAnalyzer(
        client=fake_ai_client
    )

    fake_frame = (
        "data:image/jpeg;base64,"
        "dGVzdC1zY3JlZW4="
    )

    result = analyzer.analyze_screen(
        frame_data=fake_frame,
        code_context=sample_code,
    )

    assert result is not None
    assert isinstance(result, dict)


def test_analyze_screen_without_code_context(
    fake_ai_client,
):
    """
    Screen analysis should support missing code context.
    """

    analyzer = VisualAnalyzer(
        client=fake_ai_client
    )

    fake_frame = (
        "data:image/jpeg;base64,"
        "dGVzdC1zY3JlZW4="
    )

    result = analyzer.analyze_screen(
        frame_data=fake_frame
    )

    assert result is not None
    assert isinstance(result, dict)


# ----------------------------------------------------------------------
# Camera Analysis
# ----------------------------------------------------------------------

def test_analyze_camera_returns_response(
    fake_ai_client,
    sample_code,
):
    """
    Camera analysis should return a response dictionary.
    """

    analyzer = VisualAnalyzer(
        client=fake_ai_client
    )

    fake_frame = (
        "data:image/jpeg;base64,"
        "dGVzdC1jYW1lcmE="
    )

    result = analyzer.analyze_camera(
        frame_data=fake_frame,
        code_context=sample_code,
    )

    assert result is not None
    assert isinstance(result, dict)


def test_analyze_camera_without_code_context(
    fake_ai_client,
):
    """
    Camera analysis should support missing code context.
    """

    analyzer = VisualAnalyzer(
        client=fake_ai_client
    )

    fake_frame = (
        "data:image/jpeg;base64,"
        "dGVzdC1jYW1lcmE="
    )

    result = analyzer.analyze_camera(
        frame_data=fake_frame
    )

    assert result is not None
    assert isinstance(result, dict)


# ----------------------------------------------------------------------
# Empty Input Handling
# ----------------------------------------------------------------------

def test_analyze_image_empty_data(fake_ai_client):
    """
    Empty image data should be handled without crashing.
    """

    analyzer = VisualAnalyzer(
        client=fake_ai_client
    )

    result = analyzer.analyze_image(
        image_data=""
    )

    assert result is not None
    assert isinstance(result, dict)


def test_analyze_screen_empty_data(fake_ai_client):
    """
    Empty screen data should be handled without crashing.
    """

    analyzer = VisualAnalyzer(
        client=fake_ai_client
    )

    result = analyzer.analyze_screen(
        frame_data=""
    )

    assert result is not None
    assert isinstance(result, dict)


def test_analyze_camera_empty_data(fake_ai_client):
    """
    Empty camera data should be handled without crashing.
    """

    analyzer = VisualAnalyzer(
        client=fake_ai_client
    )

    result = analyzer.analyze_camera(
        frame_data=""
    )

    assert result is not None
    assert isinstance(result, dict)


# ----------------------------------------------------------------------
# Response Structure
# ----------------------------------------------------------------------

def test_image_response_contains_expected_structure(
    fake_ai_client,
):
    """
    Visual analysis should return frontend-friendly data.
    """

    analyzer = VisualAnalyzer(
        client=fake_ai_client
    )

    fake_image_data = (
        "data:image/png;base64,"
        "dGVzdA=="
    )

    result = analyzer.analyze_image(
        image_data=fake_image_data,
        context="Test screenshot",
    )

    assert isinstance(result, dict)

    # VisualAnalyzer responses may contain these
    # frontend-oriented fields.
    expected_fields = {
        "message",
        "observations",
        "errors",
        "suggestions",
    }

    assert any(
        field in result
        for field in expected_fields
    )