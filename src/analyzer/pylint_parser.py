import re


def parse_pylint_output(output):
    issues = []

    pattern = r"(.+):(\d+):(\d+): ([A-Z]\d+): (.+) \((.+)\)"

    for line in output.splitlines():
        match = re.match(pattern, line.strip())

        if match:
            file_path, line_no, column, rule, message, category = match.groups()

            issues.append({
                "file": file_path,
                "line": int(line_no),
                "column": int(column),
                "rule": rule,
                "message": message,
                "category": category
            })

    return issues