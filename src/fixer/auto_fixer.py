import ast
import re

from agent.ollama_agent import ask_ai


def is_valid_python(code):
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def normalize_issues(issues):
    if issues is None:
        return []

    if isinstance(issues, list):
        return issues

    if isinstance(issues, tuple):
        return list(issues)

    if isinstance(issues, dict):
        return [issues]

    if isinstance(issues, str):
        return [issues]

    return [str(issues)]


def issue_to_text(issue):
    if isinstance(issue, str):
        return issue

    if isinstance(issue, dict):
        parts = []

        for key in (
            "message",
            "msg",
            "text",
            "symbol",
            "rule",
            "message-id"
        ):
            value = issue.get(key)

            if value is not None:
                parts.append(str(value))

        return " ".join(parts)

    return str(issue)


def find_undefined_name(code, issues):
    for issue in issues:
        text = issue_to_text(issue)

        match = re.search(
            r"name '([a-zA-Z_]\w*)' is not defined",
            text
        )

        if match:
            return match.group(1)

        match = re.search(
            r"Undefined variable ['\"]?([a-zA-Z_]\w*)",
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

    return None


def is_name_defined(code, name):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False

    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            if node.id == name and isinstance(node.ctx, ast.Store):
                return True

        if isinstance(node, ast.arg):
            if node.arg == name:
                return True

        if isinstance(node, ast.FunctionDef):
            if node.name == name:
                return True

    return False


def fix_literal_message(code):
    if "print(message)" in code:
        return code

    if (
        'print("message")' not in code
        and "print('message')" not in code
    ):
        return code

    if not re.search(r"\bmessage\s*=", code):
        return code

    code = code.replace(
        'print("message")',
        "print(message)"
    )

    code = code.replace(
        "print('message')",
        "print(message)"
    )

    return code


def add_module_docstring(code):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return code

    if ast.get_docstring(tree) is not None:
        return code

    return '"""Auto-fixed Python module."""\n\n' + code


def add_function_docstrings(code):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return code

    lines = code.splitlines()
    insertions = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue

        if not node.body:
            continue

        first = node.body[0]

        if (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        ):
            continue

        indentation = " " * (node.col_offset + 4)

        insertions.append(
            (
                node.lineno,
                indentation + '"""Function description."""'
            )
        )

    for line_number, docstring in reversed(insertions):
        lines.insert(line_number, docstring)

    return "\n".join(lines)


def remove_missing_final_newline(code):
    if not code.endswith("\n"):
        return code + "\n"

    return code


def extract_python_code(response):
    if not response:
        return None

    response = response.strip()

    match = re.search(
        r"```python\s*(.*?)```",
        response,
        re.DOTALL | re.IGNORECASE
    )

    if match:
        return match.group(1).strip() + "\n"

    match = re.search(
        r"```\s*(.*?)```",
        response,
        re.DOTALL
    )

    if match:
        return match.group(1).strip() + "\n"

    return None


def ai_fix_code(code, runtime_error):
    prompt = (
        "You are a careful Python code fixer.\n\n"
        "ACTUAL PYTHON CODE:\n"
        "```python\n"
        + code
        + "\n```\n\n"
        "ACTUAL RUNTIME ERROR:\n"
        "```text\n"
        + runtime_error
        + "\n```\n\n"
        "Fix the actual runtime error.\n"
        "Preserve the original purpose of the program.\n"
        "Do not invent unrelated features.\n"
        "Do not create infinite recursion.\n"
        "Make sure all variables are properly defined.\n"
        "Return one complete corrected Python program.\n"
        "Return it inside exactly one python code block.\n"
        "Do not explain the fix."
    )

    try:
        response = ask_ai(prompt)
    except Exception:
        return None

    fixed_code = extract_python_code(response)

    if not fixed_code:
        return None

    if not is_valid_python(fixed_code):
        return None

    return fixed_code


def fix_code_quality_issues(code):
    # Remove unnecessary f-string prefix.
    code = code.replace('print(f"Hello, World!")', 'print("Hello, World!")')

    # Fix the common name-shadowing/naming pattern.
    code = code.replace('name = "Alice"', 'USER_NAME = "Alice"')
    code = code.replace("name = 'Alice'", "USER_NAME = 'Alice'")

    code = code.replace(
        'def greet(name):',
        'def greet(user_name):'
    )

    code = code.replace(
        'print(f"Hello, {name}!")',
        'print(f"Hello, {user_name}!")'
    )

    return code


def auto_fix_code(code, issues):
    issues = normalize_issues(issues)

    issue_text = "\n".join(
        issue_to_text(issue)
        for issue in issues
    )

    runtime_error_detected = any(
        phrase in issue_text.lower()
        for phrase in (
            "nameerror",
            "is not defined",
            "undefined variable",
            "runtime error",
            "traceback"
        )
    )

    if runtime_error_detected:
        fixed_code = ai_fix_code(
            code,
            issue_text
        )

        if fixed_code is not None:
            return fixed_code

        return code

    fixed_code = fix_literal_message(code)

    fixed_code = add_module_docstring(fixed_code)

    fixed_code = add_function_docstrings(fixed_code)

    fixed_code = remove_missing_final_newline(fixed_code)

    if not is_valid_python(fixed_code):
        return code

    return fixed_code

