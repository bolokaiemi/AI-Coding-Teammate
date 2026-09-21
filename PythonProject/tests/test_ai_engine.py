from ai.ai_engine import AIEngine


def test_ai_engine_creation():
    engine = AIEngine()

    assert engine is not None


def test_ai_engine_has_components():
    engine = AIEngine()

    assert engine.client is not None
    assert engine.error_detector is not None
    assert engine.code_analyzer is not None
    assert engine.code_corrector is not None
    assert engine.code_explainer is not None
    assert engine.visual_analyzer is not None
    assert engine.project_analyzer is not None
    assert engine.conversation is not None


def test_ai_engine_status():
    engine = AIEngine()

    status = engine.status()

    assert isinstance(status, dict)
    assert "configured" in status
    assert "capabilities" in status


def test_ai_chat_without_api_key(monkeypatch):
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        ""
    )

    engine = AIEngine()

    result = engine.chat(
        "Explain Python functions."
    )

    assert isinstance(result, dict)
    assert "success" in result


def test_code_analysis_without_api_key(monkeypatch):
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        ""
    )

    engine = AIEngine()

    result = engine.analyze_code(
        code="print('Hello')",
        language="python",
    )

    assert isinstance(result, dict)


def test_code_explanation_without_api_key(monkeypatch):
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        ""
    )

    engine = AIEngine()

    result = engine.explain_code(
        code="x = 10",
        language="python",
    )

    assert isinstance(result, dict)