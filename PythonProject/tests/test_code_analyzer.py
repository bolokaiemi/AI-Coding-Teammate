from ai.code_analyzer import CodeAnalyzer
from ai.error_detector import ErrorDetector


def test_python_missing_colon_detection():
    detector = ErrorDetector()

    code = """
if x == 10
    print(x)
"""

    result = detector.detect_basic_syntax(
        code,
        "python"
    )

    assert isinstance(result, list)
    assert len(result) >= 1


def test_valid_python_code():
    detector = ErrorDetector()

    code = """
if x == 10:
    print(x)
"""

    result = detector.detect_basic_syntax(
        code,
        "python"
    )

    assert isinstance(result, list)


def test_javascript_brace_detection():
    detector = ErrorDetector()

    code = """
function hello() {
    console.log("Hello");
"""

    result = detector.detect_basic_syntax(
        code,
        "javascript"
    )

    assert isinstance(result, list)
    assert len(result) >= 1


def test_valid_javascript():
    detector = ErrorDetector()

    code = """
function hello() {
    console.log("Hello");
}
"""

    result = detector.detect_basic_syntax(
        code,
        "javascript"
    )

    assert isinstance(result, list)


def test_analyzer_creation():
    analyzer = CodeAnalyzer()

    assert analyzer is not None
    assert analyzer.error_detector is not None


def test_analyzer_basic_analysis():
    analyzer = CodeAnalyzer()

    code = """
def hello():
    print("Hello")
"""

    result = analyzer.analyze(
        code=code,
        language="python",
        filename="main.py",
    )

    assert isinstance(result, dict)
    assert "success" in result