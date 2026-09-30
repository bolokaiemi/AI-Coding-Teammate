"""
Shared pytest fixtures for AI Coding Teammate.
"""

import os

import pytest


@pytest.fixture(autouse=True)
def test_environment(monkeypatch):
    """
    Configure a safe test environment.

    Real OpenAI requests must never be made by the test suite.
    """

    monkeypatch.setenv("TESTING", "true")
    monkeypatch.delenv(
        "OPENAI_API_KEY",
        raising=False,
    )

    monkeypatch.setenv(
        "OPENAI_MODEL",
        "test-model",
    )


@pytest.fixture
def sample_code():
    """Return valid Python source code."""

    return """
def greet(name):
    return f"Hello, {name}!"

print(greet("Developer"))
""".strip()


@pytest.fixture
def invalid_python_code():
    """Return intentionally invalid Python-like code."""

    return """
def greet(name)
    return f"Hello, {name}!"
""".strip()


@pytest.fixture
def sample_project_context():
    """Return example project information."""

    return {
        "name": "Test Project",
        "description": (
            "Project used by the automated test suite."
        ),
        "language": "Python",
        "framework": "Flask",
        "files": [
            "app.py",
            "requirements.txt",
            "README.md",
        ],
    }


@pytest.fixture
def conversation_history():
    """Return sample AI conversation history."""

    return [
        {
            "role": "user",
            "content": "Can you inspect this project?",
        },
        {
            "role": "assistant",
            "content": (
                "Yes. Send me the code you want "
                "to inspect."
            ),
        },
    ]


class FakeAIClient:
    """
    Test replacement for AIClient.

    This prevents network requests during tests.
    """

    def __init__(self):
        self.engine = None

    def status(self):
        return {
            "configured": True,
            "provider": "test",
            "model": "test-model",
        }

    def ask(self, prompt):
        return {
            "success": True,
            "content": (
                "Test AI analysis response."
            ),
            "model": "test-model",
            "processing_time": 0.01,
        }

    def chat(self, messages):
        return {
            "success": True,
            "content": (
                "Test AI teammate response."
            ),
            "model": "test-model",
            "processing_time": 0.01,
        }


@pytest.fixture
def fake_ai_client():
    """Return the fake AI provider client."""

    return FakeAIClient()