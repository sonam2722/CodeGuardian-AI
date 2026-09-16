from pathlib import Path

from analyzer.syntax_checker import check_syntax
from analyzer.pylint_checker import run_pylint
from analyzer.pylint_parser import parse_pylint_output


def get_code_context(file_path):
    """
    Read a Python file and collect its code, syntax result,
    and Pylint issues.
    """

    file_path = Path(file_path)

    code = file_path.read_text(encoding="utf-8")

    numbered_code = "\n".join(
        f"Line {number}: {line}"
        for number, line in enumerate(
            code.splitlines(),
            start=1
        )
    )

    syntax_result = check_syntax(file_path)

    pylint_result = run_pylint(file_path)

    issues = parse_pylint_output(pylint_result)

    return {
        "file_path": file_path,
        "code": code,
        "numbered_code": numbered_code,
        "syntax_result": syntax_result,
        "issues": issues,
    }


def get_issue_text(issues):
    """
    Convert detected issues into a simple readable format.
    """

    if not issues:
        return "No Pylint issues were detected."

    return "\n".join(
        f"Line {issue['line']}: "
        f"{issue['message']} "
        f"(Rule: {issue['rule']})"
        for issue in issues
    )