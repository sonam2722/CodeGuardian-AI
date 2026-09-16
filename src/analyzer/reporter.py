def generate_report(file_path, syntax_result, issues):
    report = []

    report.append("=" * 55)
    report.append("              AI CODE AUDITOR")
    report.append("=" * 55)

    report.append(f"\nOriginal File: {file_path.name}")

    # Syntax Check
    report.append("\n[1] SYNTAX CHECK")
    if syntax_result["message"] == "No syntax errors found.":
        report.append("✓ No syntax errors")
    else:
        report.append(f"✗ {syntax_result['message']}")

    # Issue Summary
    report.append("\n[2] CODE QUALITY")

    errors = 0
    warnings = 0
    code_quality = 0

    for issue in issues:
        rule = issue["rule"]

        if rule.startswith("E"):
            errors += 1
        elif rule.startswith("W"):
            warnings += 1
        elif rule.startswith("C"):
            code_quality += 1

    total_issues = len(issues)

    report.append(f"Total Issues: {total_issues}")
    report.append(f"Errors: {errors}")
    report.append(f"Warnings: {warnings}")
    report.append(f"Code Quality Issues: {code_quality}")

    # Detailed Issues
    report.append("\n[3] DETECTED ISSUES")

    if not issues:
        report.append("✓ No issues found.")
    else:
        for index, issue in enumerate(issues, start=1):
            report.append(f"\nIssue {index}")
            report.append(f"  Line     : {issue['line']}")
            report.append(f"  Rule     : {issue['rule']}")
            report.append(f"  Message  : {issue['message']}")
            report.append(f"  Category : {issue['category']}")

    report.append("\n" + "=" * 55)

    return "\n".join(report)