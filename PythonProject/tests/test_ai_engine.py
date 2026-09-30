"""
AIEngine tests.
"""

from ai.ai_engine import AIEngine


def test_engine_initializes(fake_ai_client):
    """
    AIEngine should initialize its components.
    """

    engine = AIEngine(
        client=fake_ai_client
    )

    assert engine.client is fake_ai_client

    assert engine.error_detector is not None
    assert engine.code_analyzer is not None
    assert engine.code_corrector is not None
    assert engine.code_explainer is not None
    assert engine.visual_analyzer is not None
    assert engine.project_analyzer is not None
    assert engine.conversation is not None


def test_engine_attaches_to_client(
    fake_ai_client,
):
    """
    AIEngine should attach itself to compatible clients.
    """

    engine = AIEngine(
        client=fake_ai_client
    )

    assert fake_ai_client.engine is engine


def test_engine_status(fake_ai_client):
    """
    Engine status should contain provider information.
    """

    engine = AIEngine(
        client=fake_ai_client
    )

    status = engine.status()

    assert status["engine"] == (
        "AI Coding Teammate"
    )

    assert status["provider_configured"] is True

    assert status["model"] == "test-model"

    assert "capabilities" in status


def test_engine_capabilities(fake_ai_client):
    """
    Required AI capabilities should be registered.
    """

    engine = AIEngine(
        client=fake_ai_client
    )

    capabilities = (
        engine.status()["capabilities"]
    )

    assert capabilities["chat"] is True
    assert capabilities["code_analysis"] is True
    assert capabilities["error_detection"] is True
    assert capabilities["code_correction"] is True
    assert capabilities["code_explanation"] is True


def test_engine_chat(
    fake_ai_client,
    conversation_history,
    sample_project_context,
    sample_code,
):
    """
    AIEngine should delegate conversations correctly.
    """

    engine = AIEngine(
        client=fake_ai_client
    )

    response = engine.chat(
        message="Explain my current code.",
        conversation_history=(
            conversation_history
        ),
        project_context=(
            sample_project_context
        ),
        code_context=sample_code,
    )

    assert response is not None

    assert response["type"] == "chat"

    assert (
        response["message"]
        == "Test AI teammate response."
    )


def test_engine_rejects_empty_chat(
    fake_ai_client,
):
    """
    Empty chat messages should be rejected.
    """

    engine = AIEngine(
        client=fake_ai_client
    )

    response = engine.chat("")

    assert response["success"] is False


def test_engine_health(fake_ai_client):
    """
    Health information should be available.
    """

    engine = AIEngine(
        client=fake_ai_client
    )

    health = engine.health()

    assert health["success"] is True
    assert health["engine"] == (
        "AI Coding Teammate"
    )