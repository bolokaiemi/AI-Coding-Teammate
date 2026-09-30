"""
CodeCorrector tests.
"""

from ai.code_corrector import CodeCorrector


def test_corrector_initializes(
    fake_ai_client,
):
    """
    CodeCorrector should accept a shared client.
    """

    corrector = CodeCorrector(
        client=fake_ai_client
    )

    assert corrector.client is fake_ai_client


def test_empty_code(
    fake_ai_client,
):
    """
    Empty code should return a safe response.
    """

    corrector = CodeCorrector(
        client=fake_ai_client
    )

    result = corrector.correct(
        code="",
        language="python",
    )

    assert isinstance(result, dict)

    assert result["original_code"] == ""
    assert result["corrected_code"] == ""


def test_problem_formatter():
    """
    Problem dictionaries should be converted
    into readable text.
    """

    problem = {
        "line": 10,
        "message": "Missing colon.",
    }

    result = CodeCorrector._format_problem(
        problem
    )

    assert result == (
        "Line 10: Missing colon."
    )


def test_problem_formatter_without_line():
    """
    Problems without line numbers should still work.
    """

    problem = {
        "message": "Unexpected token."
    }

    result = CodeCorrector._format_problem(
        problem
    )

    assert result == "Unexpected token."


def test_extract_python_code():
    """
    Code should be extracted from Markdown fences.
    """

    content = """Here is the corrected code:

```python
print(\"Hello\")
```"""