from pathlib import Path

from agent.ollama_agent import ask_ai
from agent.code_context import get_code_context, get_issue_text
from fixer.auto_fixer import auto_fix_code
from voice.vaani import listen, speak


BASE_DIR = Path(__file__).resolve().parent.parent

file_path = BASE_DIR / "input_code" / "test.py"
fixed_file_path = BASE_DIR / "input_code" / "fixed_test.py"


def analyze_code():
    return get_code_context(file_path)


def explain_code(context):
    issue_text = get_issue_text(context["issues"])

    return ask_ai(
        f"""
You are Vaani, Boss's Python code assistant.

Boss asked:
Analyze the current code.

ACTUAL CODE:

{context["numbered_code"]}

SYNTAX RESULT:

{context["syntax_result"]}

CONFIRMED PYLINT ISSUES:

{issue_text}

STRICT RULES:

1. Analyze only the actual code provided.
2. Use only confirmed issues.
3. Always mention the exact line number.
4. Never invent an error.
5. Never call a valid Python statement invalid.
6. print() is a built-in Python function and does not need an import.
7. If print("message") exists, explain that it prints the literal text.
8. If print(message) exists, explain that it prints the variable value.
9. Do not invent recursion unless a function actually calls itself.
10. Do not change the purpose of the program.
11. Do not provide a completely different program.
12. Keep the explanation beginner-friendly.
13. Do not claim that any file was changed.

Give Boss a short and accurate explanation.
"""
    ).strip()


def fix_code(context):
    original_code = context["code"]
    issues = context["issues"]

    if not issues:
        return None, "Boss, I could not find any confirmed issues to fix."

    fixed_code = auto_fix_code(
        original_code,
        issues
    )

    fixed_file_path.write_text(
        fixed_code,
        encoding="utf-8"
    )

    fixed_context = get_code_context(fixed_file_path)

    return fixed_context, None


print("\nVaani Code Assistant is ready. Say something, Boss.")


while True:

    user_text = listen()

    if not user_text:
        continue

    user_lower = user_text.lower().strip()

    # -------------------------------
    # EXIT
    # -------------------------------

    if any(
        word in user_lower
        for word in ["exit", "quit", "stop", "bye"]
    ):
        speak("Okay Boss, see you later.")
        break

    # -------------------------------
    # GET CURRENT CODE CONTEXT
    # -------------------------------

    context = analyze_code()

    # -------------------------------
    # FIX REQUEST
    # -------------------------------

    if (
        "fix" in user_lower
        or "correct" in user_lower
        or "repair" in user_lower
        or "isko thik" in user_lower
        or "isko fix" in user_lower
    ):

        print("\nVaani is fixing the confirmed issues...")

        fixed_context, error = fix_code(context)

        if error:
            print("\nVaani:", error)
            speak(error)
            continue

        remaining_issues = fixed_context["issues"]

        if (
            fixed_context["syntax_result"]["message"]
            == "No syntax errors found."
            and not remaining_issues
        ):
            message = (
                "Done Boss. The code has been fixed and verified. "
                "The fixed file has no remaining Pylint issues."
            )

        elif (
            fixed_context["syntax_result"]["message"]
            == "No syntax errors found."
        ):
            remaining_text = get_issue_text(
                remaining_issues
            )

            message = (
                "Boss, the code was fixed and saved, "
                "but some issues are still remaining. "
                f"{remaining_text}"
            )

        else:
            message = (
                "Boss, I created the fixed file, "
                "but the result did not pass the final syntax check."
            )

        print("\nVaani:", message)
        speak(message)

        continue

    # -------------------------------
    # NORMAL CODE QUESTION
    # -------------------------------

    response = explain_code(context)

    print("\nVaani:", response)

    speak(response)