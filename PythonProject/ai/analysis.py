# ============================================================
# AI Coding Teammate
# ai/analysis.py
#
# Core code analysis logic
# ============================================================

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, asdict
from typing import Any


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class AnalysisIssue:
    """
    Represents one issue discovered during code analysis.
    """

    severity: str
    title: str
    message: str
    line: int | None = None
    column: int | None = None
    suggestion: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AnalysisResult:
    """
    Standard result returned by the analysis layer.
    """

    success: bool
    language: str
    summary: str
    issues: list[AnalysisIssue]
    corrected_code: str | None = None
    explanation: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "language": self.language,
            "summary": self.summary,
            "issues": [
                issue.to_dict()
                for issue in self.issues
            ],
            "corrected_code": self.corrected_code,
            "explanation": self.explanation,
        }


# ============================================================
# LANGUAGE DETECTION
# ============================================================

def detect_language(
    code: str,
    filename: str | None = None,
) -> str:
    """
    Detect the programming language using the filename first,
    then basic source-code patterns.
    """

    if filename:
        extension = filename.lower().split(".")[-1]

        extensions = {
            "py": "python",
            "js": "javascript",
            "ts": "typescript",
            "html": "html",
            "htm": "html",
            "css": "css",
            "json": "json",
            "sql": "sql",
            "java": "java",
            "c": "c",
            "cpp": "cpp",
            "cc": "cpp",
            "go": "go",
            "rs": "rust",
            "php": "php",
            "rb": "ruby",
            "sh": "shell",
        }

        if extension in extensions:
            return extensions[extension]

    stripped = code.strip()

    if not stripped:
        return "unknown"

    # Python
    if (
        re.search(r"^\s*def\s+\w+\s*\(", code, re.MULTILINE)
        or re.search(r"^\s*import\s+\w+", code, re.MULTILINE)
        or re.search(r"^\s*from\s+\w+\s+import", code, re.MULTILINE)
    ):
        return "python"

    # JavaScript
    if (
        "const " in code
        or "let " in code
        or "console.log" in code
        or "function " in code
    ):
        return "javascript"

    # HTML
    if (
        "<html" in code.lower()
        or "<div" in code.lower()
        or "<body" in code.lower()
    ):
        return "html"

    # CSS
    if (
        "{" in code
        and "}" in code
        and re.search(r"[.#][\w-]+\s*\{", code)
    ):
        return "css"

    # SQL
    if re.search(
        r"\b(SELECT|INSERT|UPDATE|DELETE|CREATE TABLE)\b",
        code,
        re.IGNORECASE,
    ):
        return "sql"

    return "unknown"


# ============================================================
# EMPTY CODE CHECK
# ============================================================

def validate_code(code: str) -> AnalysisIssue | None:
    """
    Perform basic validation before analysis.
    """

    if code is None:
        return AnalysisIssue(
            severity="error",
            title="No Code Provided",
            message="No source code was supplied for analysis.",
        )

    if not code.strip():
        return AnalysisIssue(
            severity="warning",
            title="Empty Code",
            message="The code editor is empty.",
            suggestion="Add some code before starting analysis.",
        )

    return None


# ============================================================
# PYTHON SYNTAX ANALYSIS
# ============================================================

def analyze_python_syntax(
    code: str,
) -> list[AnalysisIssue]:
    """
    Parse Python source code and detect syntax errors.
    """

    issues: list[AnalysisIssue] = []

    try:
        ast.parse(code)

    except SyntaxError as error:
        issues.append(
            AnalysisIssue(
                severity="error",
                title="Python Syntax Error",
                message=error.msg,
                line=error.lineno,
                column=error.offset,
                suggestion=(
                    "Check the syntax near the reported "
                    "line and column."
                ),
            )
        )

    return issues


# ============================================================
# UNDEFINED NAME ANALYSIS
# ============================================================

class PythonNameVisitor(ast.NodeVisitor):
    """
    Lightweight Python AST visitor used to find probable
    undefined variables.

    This is intentionally conservative and is not intended to
    replace a complete static-analysis engine such as Ruff,
    Pyright or Pylint.
    """

    def __init__(self):
        self.defined: set[str] = set()
        self.used: list[tuple[str, int]] = []

    def visit_FunctionDef(self, node):
        self.defined.add(node.name)

        for argument in node.args.args:
            self.defined.add(argument.arg)

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.defined.add(node.name)

        for argument in node.args.args:
            self.defined.add(argument.arg)

        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.defined.add(node.name)

        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.defined.add(node.id)

        elif isinstance(node.ctx, ast.Load):
            self.used.append(
                (
                    node.id,
                    getattr(node, "lineno", 0),
                )
            )

        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname or alias.name.split(".")[0]

            self.defined.add(name)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            name = alias.asname or alias.name

            self.defined.add(name)


# ============================================================
# PYTHON BUILTINS
# ============================================================

PYTHON_BUILTINS = {
    "print",
    "len",
    "range",
    "str",
    "int",
    "float",
    "bool",
    "list",
    "dict",
    "set",
    "tuple",
    "sum",
    "min",
    "max",
    "abs",
    "open",
    "enumerate",
    "zip",
    "map",
    "filter",
    "any",
    "all",
    "sorted",
    "reversed",
    "type",
    "isinstance",
    "super",
    "Exception",
    "ValueError",
    "TypeError",
    "KeyError",
    "IndexError",
    "True",
    "False",
    "None",
}


# ============================================================
# FIND UNDEFINED PYTHON NAMES
# ============================================================

def find_python_undefined_names(
    code: str,
) -> list[AnalysisIssue]:
    """
    Detect simple undefined-name cases.

    Example:

        def calculate_total(price, tax):
            total = price + taxes

    The analyzer can identify that 'taxes' was used but never
    defined.
    """

    issues: list[AnalysisIssue] = []

    try:
        tree = ast.parse(code)

    except SyntaxError:
        return issues

    visitor = PythonNameVisitor()

    visitor.visit(tree)

    already_reported: set[str] = set()

    for name, line in visitor.used:

        if name in visitor.defined:
            continue

        if name in PYTHON_BUILTINS:
            continue

        if name.startswith("__"):
            continue

        if name in already_reported:
            continue

        already_reported.add(name)

        issues.append(
            AnalysisIssue(
                severity="error",
                title="Possible Undefined Name",
                message=(
                    f"'{name}' is used but does not appear "
                    "to be defined."
                ),
                line=line,
                suggestion=(
                    f"Check whether '{name}' is misspelled "
                    "or needs to be defined before use."
                ),
            )
        )

    return issues


# ============================================================
# COMMON CODE QUALITY CHECKS
# ============================================================

def analyze_common_patterns(
    code: str,
    language: str,
) -> list[AnalysisIssue]:
    """
    Lightweight checks that are useful before an AI model is
    involved.
    """

    issues: list[AnalysisIssue] = []

    lines = code.splitlines()

    # --------------------------------------------------------
    # Very long lines
    # --------------------------------------------------------

    for line_number, line in enumerate(lines, start=1):

        if len(line) > 140:
            issues.append(
                AnalysisIssue(
                    severity="info",
                    title="Long Line",
                    message=(
                        "This line is longer than 140 characters."
                    ),
                    line=line_number,
                    suggestion=(
                        "Consider splitting the statement into "
                        "smaller, more readable lines."
                    ),
                )
            )

    # --------------------------------------------------------
    # Potential secret detection
    # --------------------------------------------------------

    secret_patterns = [
        r"api[_-]?key\s*=\s*[\"'][^\"']+[\"']",
        r"password\s*=\s*[\"'][^\"']+[\"']",
        r"secret[_-]?key\s*=\s*[\"'][^\"']+[\"']",
        r"access[_-]?token\s*=\s*[\"'][^\"']+[\"']",
    ]

    for pattern in secret_patterns:

        if re.search(
            pattern,
            code,
            flags=re.IGNORECASE,
        ):
            issues.append(
                AnalysisIssue(
                    severity="warning",
                    title="Possible Secret Detected",
                    message=(
                        "The code may contain a hard-coded "
                        "credential or secret."
                    ),
                    suggestion=(
                        "Store credentials in environment "
                        "variables instead of source code."
                    ),
                )
            )

            break

    return issues


# ============================================================
# SIMPLE CORRECTION ENGINE
# ============================================================

def generate_basic_correction(
    code: str,
    issues: list[AnalysisIssue],
) -> str | None:
    """
    Generate only very safe, obvious corrections.

    More complex corrections should be handled by the AI model.
    """

    corrected_code = code

    changed = False

    # --------------------------------------------------------
    # Example:
    #
    # def calculate_total(price, tax):
    #     total = price + taxes
    #
    # Can detect 'taxes' as a probable typo for 'tax'.
    # --------------------------------------------------------

    undefined_names = []

    for issue in issues:

        if issue.title == "Possible Undefined Name":

            match = re.search(
                r"'([^']+)'",
                issue.message,
            )

            if match:
                undefined_names.append(
                    match.group(1)
                )

    # --------------------------------------------------------
    # Look for a very close function parameter
    # --------------------------------------------------------

    try:
        tree = ast.parse(code)

    except SyntaxError:
        return None

    parameters: set[str] = set()

    for node in ast.walk(tree):

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):

            for argument in node.args.args:
                parameters.add(argument.arg)

    for undefined_name in undefined_names:

        for parameter in parameters:

            # Example:
            #
            # taxes -> tax
            # usernames -> username

            if (
                undefined_name.endswith("s")
                and undefined_name[:-1] == parameter
            ):
                corrected_code = re.sub(
                    rf"\b{re.escape(undefined_name)}\b",
                    parameter,
                    corrected_code,
                )

                changed = True

    if changed:
        return corrected_code

    return None


# ============================================================
# CREATE HUMAN-READABLE SUMMARY
# ============================================================

def build_summary(
    issues: list[AnalysisIssue],
) -> str:
    """
    Generate a small summary for the visualizer.
    """

    if not issues:
        return (
            "No obvious issues were detected by the "
            "local analysis engine."
        )

    errors = sum(
        1
        for issue in issues
        if issue.severity == "error"
    )

    warnings = sum(
        1
        for issue in issues
        if issue.severity == "warning"
    )

    info = sum(
        1
        for issue in issues
        if issue.severity == "info"
    )

    parts = []

    if errors:
        parts.append(
            f"{errors} error"
            f"{'s' if errors != 1 else ''}"
        )

    if warnings:
        parts.append(
            f"{warnings} warning"
            f"{'s' if warnings != 1 else ''}"
        )

    if info:
        parts.append(
            f"{info} suggestion"
            f"{'s' if info != 1 else ''}"
        )

    return (
        "Analysis completed. Found "
        + ", ".join(parts)
        + "."
    )


# ============================================================
# MAIN CODE ANALYZER
# ============================================================

def analyze_code(
    code: str,
    filename: str | None = None,
    language: str | None = None,
) -> dict[str, Any]:
    """
    Main entry point used by the rest of the application.

    Example:

        result = analyze_code(
            code=my_code,
            filename="app.py"
        )
    """

    validation_issue = validate_code(code)

    if validation_issue:

        result = AnalysisResult(
            success=False,
            language=language or "unknown",
            summary=validation_issue.message,
            issues=[validation_issue],
        )

        return result.to_dict()

    detected_language = (
        language
        or detect_language(
            code=code,
            filename=filename,
        )
    )

    issues: list[AnalysisIssue] = []

    # --------------------------------------------------------
    # Python analysis
    # --------------------------------------------------------

    if detected_language == "python":

        syntax_issues = analyze_python_syntax(
            code
        )

        issues.extend(
            syntax_issues
        )

        # Only continue AST analysis if the syntax is valid.

        if not syntax_issues:

            issues.extend(
                find_python_undefined_names(
                    code
                )
            )

    # --------------------------------------------------------
    # General checks
    # --------------------------------------------------------

    issues.extend(
        analyze_common_patterns(
            code=code,
            language=detected_language,
        )
    )

    # --------------------------------------------------------
    # Basic correction
    # --------------------------------------------------------

    corrected_code = None

    if detected_language == "python":

        corrected_code = generate_basic_correction(
            code=code,
            issues=issues,
        )

    # --------------------------------------------------------
    # Explanation
    # --------------------------------------------------------

    explanation = None

    if corrected_code:

        explanation = (
            "A probable variable-name mismatch was detected. "
            "The corrected version replaces the undefined name "
            "with the closest matching function parameter."
        )

    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    result = AnalysisResult(
        success=not any(
            issue.severity == "error"
            for issue in issues
        ),
        language=detected_language,
        summary=build_summary(issues),
        issues=issues,
        corrected_code=corrected_code,
        explanation=explanation,
    )

    return result.to_dict()


# ============================================================
# EXPLAIN CODE
# ============================================================

def explain_code(
    code: str,
    filename: str | None = None,
) -> dict[str, Any]:
    """
    Prepare basic information for the AI explanation system.

    A real LLM can later replace or extend this function.
    """

    language = detect_language(
        code=code,
        filename=filename,
    )

    analysis = analyze_code(
        code=code,
        filename=filename,
        language=language,
    )

    return {
        "language": language,
        "summary": analysis["summary"],
        "issues": analysis["issues"],
        "message": (
            f"This appears to be {language} code. "
            "The local analyzer has inspected its basic "
            "syntax, variables and common development issues."
        ),
    }


# ============================================================
# REVIEW CODE
# ============================================================

def review_code(
    code: str,
    filename: str | None = None,
) -> dict[str, Any]:
    """
    Perform a lightweight code review.

    Later this can be connected to your LLM/multimodal model.
    """

    analysis = analyze_code(
        code=code,
        filename=filename,
    )

    recommendations = []

    if not analysis["issues"]:

        recommendations.append(
            "The local analyzer found no obvious problems."
        )

    else:

        for issue in analysis["issues"]:

            if issue.get("suggestion"):

                recommendations.append(
                    issue["suggestion"]
                )

    return {
        "analysis": analysis,
        "recommendations": recommendations,
    }


# ============================================================
# FIND ERRORS
# ============================================================

def find_errors(
    code: str,
    filename: str | None = None,
) -> list[dict[str, Any]]:
    """
    Return only error-level analysis results.
    """

    result = analyze_code(
        code=code,
        filename=filename,
    )

    return [
        issue
        for issue in result["issues"]
        if issue["severity"] == "error"
    ]


# ============================================================
# CORRECT CODE
# ============================================================

def correct_code(
    code: str,
    filename: str | None = None,
) -> dict[str, Any]:
    """
    Analyze code and return any locally generated correction.

    Complex corrections should later be passed to your
    AI model provider.
    """

    result = analyze_code(
        code=code,
        filename=filename,
    )

    corrected = (
        result.get("corrected_code")
        or code
    )

    return {
        "original_code": code,
        "corrected_code": corrected,
        "changed": corrected != code,
        "explanation": result.get(
            "explanation"
        ),
        "issues": result.get(
            "issues",
            [],
        ),
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    example_code = """
def calculate_total(price, tax):
    total = price + taxes
    return total
"""

    result = analyze_code(
        code=example_code,
        filename="example.py",
    )

    print(result)