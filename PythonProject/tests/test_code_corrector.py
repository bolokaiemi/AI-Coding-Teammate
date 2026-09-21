from ai.code_corrector import CodeCorrector


def test_corrector_creation():
    corrector = CodeCorrector()

    assert corrector is not None


def test_problem_formatting():
    corrector = CodeCorrector()

    problems = [
        {
            "line": 2,
            "message": "Missing colon",
            "severity": "error",
        }
    ]

    formatted = corrector._format_problem(
        problems
    )

    assert isinstance(formatted, str)
    assert "Missing colon" in formatted


def test_extract_code_from_code_block():
    corrector = CodeCorrector()

    response = """
Here is the corrected code:

```python
print("Hello")