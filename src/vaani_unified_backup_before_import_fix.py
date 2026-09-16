from pathlib import Path
import re
import subprocess

from agent.ollama_agent import ask_ai, ask_conversation
from agent.code_context import get_code_context, get_issue_text
from fixer.auto_fixer import auto_fix_code, extract_python_code, is_valid_python, fix_code_quality_issues
from voice.vaani import listen, speak


BASE_DIR = Path(__file__).resolve().parent.parent

file_path = BASE_DIR / "input_code" / "test.py"
fixed_file_path = BASE_DIR / "input_code" / "fixed_test.py"


# ==================================================
# CONVERSATION MEMORY
# ==================================================

conversation_history = []
last_requested_line = None
last_code_request = False
last_runtime_error = None


def add_to_memory(role, text):
    conversation_history.append(
        {
            "role": role,
            "content": text
        }
    )

    if len(conversation_history) > 12:
        conversation_history.pop(0)


def get_conversation_text():
    if not conversation_history:
        return "No previous conversation."

    return "\n".join(
        f"{item['role'].upper()}: {item['content']}"
        for item in conversation_history
    )


# ==================================================
# CODE REQUEST DETECTION
# ==================================================

def is_code_request(text):
    text = text.lower().strip()

    # --------------------------------------------------
    # LINE-SPECIFIC QUESTIONS
    # --------------------------------------------------

    if re.search(
        r"\b(?:line|online)\s*(?:number|no\.?)?\s*\d+\b",
        text
    ):
        return True

    # --------------------------------------------------
    # STRONG CODE PHRASES
    # --------------------------------------------------

    strong_code_phrases = [
        "show me the code",
        "explain the code",
        "could you explain",
        "can you explain the code",
        "please explain the code",
        "check the code",
        "check my code",
        "check my python",
        "check python",
        "analyze the code",
        "analyze my code",

        # RUN
        "run the code",
        "run code",
        "execute the code",
        "execute code",
        "run the program",
        "execute the program",
        "code chalao",
        "code run karo",
        "program chalao",
        "program run karo",
        "run it",
        "run",

        # FIX
        "fix the code",
        "fix my code",
        "correct the code",
        "correct my code",
        "repair the code",
        "repair my code",
        "debug the code",
        "debug my code",
        "what is wrong with the code",
        "what is wrong with my code",
        "what is wrong in the code",
        "what is wrong in my code",
        "code mein problem",
        "code me problem",
        "code mein error",
        "code me error",
        "code ko fix",
        "code ko correct",
        "code ko thik",
        "code ko theek",
        "isko fix",
        "isko correct",
        "isko thik",
        "isko theek",
        "pylint",
        "syntax error",
        "python error",
        "python code",
        "python program",
        "program mein error",
        "program me error"
    ]

    if any(
        phrase in text
        for phrase in strong_code_phrases
    ):
        return True

    # --------------------------------------------------
    # WORD-BASED DETECTION
    # --------------------------------------------------

    words = re.findall(
        r"\b[a-zA-Z]+\b",
        text
    )

    if "pylint" in words:
        return True

    if "python" in words and any(
        word in words
        for word in [
            "code",
            "program",
            "error",
            "bug",
            "function",
            "variable",
            "syntax",
            "debug",
            "fix",
            "check",
            "run",
            "execute"
        ]
    ):
        return True

    return False


# ==================================================
# LINE NUMBER
# ==================================================

def get_requested_line(text):
    text = text.lower()

    patterns = [
        r"\bline\s*(?:number|no\.?)?\s*(\d+)\b",
        r"\bonline\s*(?:number|no\.?)?\s*(\d+)\b",
        r"\blinenumber\s*(\d+)\b"
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            return int(match.group(1))

    return None


# ==================================================
# CODE ANALYSIS
# ==================================================

def analyze_code():
    return get_code_context(file_path)


# ==================================================
# EXIT DETECTION
# ==================================================

def contains_exit_request(text):
    text = text.lower().strip()

    if any(
        phrase in text
        for phrase in [
            "band ho jao",
            "band karo",
            "close vaani",
            "close bani",
            "close vani"
        ]
    ):
        return True

    words = re.findall(
        r"\b[a-zA-Z]+\b",
        text
    )

    return any(
        word in words
        for word in [
            "exit",
            "quit",
            "stop",
            "bye"
        ]
    )


def is_only_exit_command(text):
    text = text.lower().strip()

    allowed = [
        "exit",
        "quit",
        "stop",
        "bye",
        "exit vaani",
        "exit bani",
        "exit vani",
        "bye vaani",
        "bye bani",
        "bye vani",
        "band ho jao",
        "band karo",
        "close vaani",
        "close bani",
        "close vani"
    ]

    return text in allowed


# ==================================================
# NATURAL CONVERSATION
# ==================================================

def normal_conversation(user_text):
    text = user_text.lower().strip()

    # --------------------------------------------------
    # GREETING + HOW ARE YOU
    # --------------------------------------------------

    english_greeting = re.search(
        r"\b(hi|hello|hey|hii)\b",
        text
    )

    asks_how_are_you_english = any(
        phrase in text
        for phrase in [
            "how are you",
            "how r you",
            "how are u"
        ]
    )

    if english_greeting and asks_how_are_you_english:
        return (
            "Hi Boss! I'm doing great. How are you?"
        )

    # --------------------------------------------------
    # HINDI GREETING
    # --------------------------------------------------

    hindi_greeting = re.search(
        r"\b(hi|hello|hey|hii)\b",
        text
    )

    asks_how_are_you_hindi = any(
        phrase in text
        for phrase in [
            "kaise ho",
            "kaisi ho",
            "kaisa ho",
            "kaisi hai"
        ]
    )

    if hindi_greeting and asks_how_are_you_hindi:
        return (
            "Hi Boss! Main bilkul theek hoon. "
            "Tum kaise ho?"
        )

    # --------------------------------------------------
    # SIMPLE GREETING
    # --------------------------------------------------

    if re.fullmatch(
        r"(hi|hello|hey|hii|"
        r"hi vaani|hello vaani|hey vaani|"
        r"hi bani|hello bani|hey bani|"
        r"hi vani|hello vani|hey vani)",
        text
    ):
        return "Hi Boss! How are you?"

    # --------------------------------------------------
    # NAMASTE
    # --------------------------------------------------

    if text in [
        "namaste",
        "namaste vaani",
        "namaste bani",
        "namaste vani"
    ]:
        return "Namaste Boss! Kaise ho?"

    # --------------------------------------------------
    # HINDI FINE
    # --------------------------------------------------

    hindi_fine = any(
        phrase in text
        for phrase in [
            "main theek hun",
            "main theek hoon",
            "mai theek hun",
            "mai theek hoon",
            "main thik hun",
            "main thik hoon",
            "mai thik hun",
            "mai thik hoon"
        ]
    )

    # --------------------------------------------------
    # ENGLISH FINE
    # --------------------------------------------------

    english_fine = any(
        phrase in text
        for phrase in [
            "i am fine",
            "i'm fine",
            "i am good",
            "i'm good",
            "i am okay",
            "i'm okay",
            "i am ok",
            "i'm ok"
        ]
    )

    if hindi_fine:
        return "Achha Boss, sunke achha laga."

    if english_fine:
        return "Glad to hear that, Boss."

    # --------------------------------------------------
    # WHAT ARE YOU DOING
    # --------------------------------------------------

    if any(
        phrase in text
        for phrase in [
            "what are you doing",
            "what r you doing",
            "what are u doing"
        ]
    ):
        return "I'm talking to you, Boss."

    if any(
        phrase in text
        for phrase in [
            "tum kya kar rahi ho",
            "tum kya kr rahi ho",
            "kya kar rahi ho"
        ]
    ):
        return (
            "Main tumse baat kar rahi hoon, Boss."
        )

    # --------------------------------------------------
    # WHO ARE YOU
    # --------------------------------------------------

    if any(
        phrase in text
        for phrase in [
            "what are you",
            "who are you"
        ]
    ):
        return (
            "I'm Vaani, your personal AI assistant, Boss."
        )

    if any(
        phrase in text
        for phrase in [
            "tum kaun ho",
            "aap kaun ho"
        ]
    ):
        return (
            "Main Vaani hoon, tumhari personal AI assistant."
        )

    # --------------------------------------------------
    # NAME
    # --------------------------------------------------

    if any(
        phrase in text
        for phrase in [
            "what is your name",
            "what's your name",
            "what is ur name"
        ]
    ):
        return "I'm Vaani, Boss."

    if any(
        phrase in text
        for phrase in [
            "tumhara naam kya hai",
            "tumhara name kya hai",
            "aapka naam kya hai"
        ]
    ):
        return "Mera naam Vaani hai, Boss."

    # --------------------------------------------------
    # THANK YOU
    # --------------------------------------------------

    if any(
        phrase in text
        for phrase in [
            "thank you",
            "thanks",
            "thanku",
            "thank u"
        ]
    ):
        return "You're welcome, Boss."

    if "dhanyawad" in text:
        return "Koi baat nahi, Boss."

    # --------------------------------------------------
    # SIMPLE CONFIRMATION
    # --------------------------------------------------

    if text in [
        "okay",
        "ok",
        "acha",
        "achha",
        "haan",
        "hmm",
        "hmmm",
        "theek hai",
        "thik hai"
    ]:
        return "Theek hai, Boss."

    # ==================================================
    # GENERAL CONVERSATION
    # ==================================================

    history = get_conversation_text()

    english_words = {
        "what", "why", "how", "when", "where", "who",
        "which", "can", "could", "would", "should",
        "do", "does", "did", "is", "are", "am",
        "you", "your", "i", "me", "my", "we", "they",
        "hello", "hi", "thanks", "please", "tell",
        "give", "help", "doing", "think", "know",
        "want", "need", "feel", "like"
    }

    hindi_words = {
        "main", "mai", "mujhe", "mera", "meri", "mere",
        "tum", "tumhe", "tumhara", "aap", "aapko",
        "kya", "kaise", "kaisa", "kaisi", "hai", "hoon",
        "hun", "hain", "ho", "tha", "thi", "the",
        "kar", "karo", "karna", "krna", "nahi", "nahin",
        "haan", "acha", "achha", "accha", "abhi",
        "kyun", "kyon", "isko", "usko", "yeh", "ye",
        "woh", "wo", "kuch", "bahut", "aaj", "kal",
        "bol", "bolo", "bata", "batao", "chahiye",
        "sahi", "galat", "thik", "theek"
    }

    words = re.findall(
        r"\b[a-zA-Z]+\b",
        text
    )

    english_count = sum(
        1
        for word in words
        if word in english_words
    )

    hindi_count = sum(
        1
        for word in words
        if word in hindi_words
    )

    if hindi_count > english_count:
        language_instruction = """
The current message is Hindi/Hinglish.

Reply naturally in Hindi/Hinglish.

Do not switch to English unless necessary.
"""

    elif english_count > 0:
        language_instruction = """
The current message is English.

Reply ONLY in natural English.

DO NOT use Hindi.
DO NOT use Hinglish.
DO NOT translate the English message into Hindi.
"""

    else:
        language_instruction = """
The language is unclear.

Reply naturally using the most appropriate language
based on the current message and recent conversation.
"""

    prompt = f"""
You are Vaani, Boss's personal voice assistant.

Previous conversation:

{history}

Current message from Boss:

{user_text}

LANGUAGE INSTRUCTION:

{language_instruction}

IMPORTANT RULES:

1. Understand the complete current message.
2. Answer the current message directly.
3. The current message language has priority.
4. Do not translate Boss's message.
5. Do not repeat Boss's message.
6. Do not explain what Boss meant.
7. Do not give textbook-style replies.
8. Do not give robotic replies.
9. Do not randomly change the topic.
10. Do not talk about coding unless Boss asks about coding.
11. Keep the answer short and natural.
12. Call the user Boss naturally.
13. Do not use Boss in every sentence.
14. Do not start every response with "Arre".
15. Do not say that you are an AI or language model unless Boss asks.
16. If Boss asks a question, answer that question.
17. Return ONLY the sentence Vaani should speak aloud.

Final answer:
"""

    response = ask_conversation(prompt)

    return response.strip()


# ==================================================
# LINE EXPLANATION
# ==================================================

def explain_line(context, line_number, user_text):
    lines = context["code"].splitlines()

    if line_number < 1 or line_number > len(lines):
        return (
            f"Boss, Line {line_number} does not exist "
            f"in the current file."
        )

    selected_line = lines[line_number - 1].strip()

    # --------------------------------------------------
    # PRINT MESSAGE
    # --------------------------------------------------

    if re.fullmatch(
        r'print\s*\(\s*["\']message["\']\s*\)',
        selected_line
    ):
        return (
            f'Boss, Line {line_number} has a logical problem. '
            'It prints the literal text "message" because '
            '"message" is inside quotes. It does not print '
            "the value stored in the message variable. "
            "If the intention is to print the greeting, "
            "this line should use print(message)."
        )

    # --------------------------------------------------
    # PRINT VARIABLE
    # --------------------------------------------------

    if re.fullmatch(
        r"print\s*\(\s*message\s*\)",
        selected_line
    ):
        return (
            f"Boss, Line {line_number} is correct. "
            "It prints the value stored in the message variable."
        )

    # --------------------------------------------------
    # FUNCTION DEFINITION
    # --------------------------------------------------

    function_match = re.match(
        r"def\s+([a-zA-Z_]\w*)\s*\(",
        selected_line
    )

    if function_match:
        function_name = function_match.group(1)

        return (
            f"Boss, Line {line_number} defines the "
            f"{function_name} function. There is no syntax error "
            "on this line. Pylint may report a missing function "
            "docstring here, which is a code-quality issue."
        )

    # --------------------------------------------------
    # VARIABLE ASSIGNMENT
    # --------------------------------------------------

    assignment_match = re.match(
        r"([a-zA-Z_]\w*)\s*=",
        selected_line
    )

    if assignment_match:
        variable_name = assignment_match.group(1)

        if variable_name == "message":
            if any(
                re.fullmatch(
                    r'print\s*\(\s*["\']message["\']\s*\)',
                    line.strip()
                )
                for line in lines
            ):
                return (
                    f"Boss, Line {line_number} creates the "
                    "message variable correctly. The problem is "
                    "that the variable is not actually used later "
                    'because print("message") uses the literal '
                    'word "message". That is why Pylint reports '
                    "message as unused."
                )

        return (
            f"Boss, Line {line_number} assigns a value to "
            f"the variable {variable_name}. "
            "There is no confirmed syntax error on this line."
        )

    # --------------------------------------------------
    # CHECK FOR SELF-RECURSION
    # --------------------------------------------------

    function_name = None

    for index in range(
        line_number - 1,
        -1,
        -1
    ):
        previous_line = lines[index].strip()

        match = re.match(
            r"def\s+([a-zA-Z_]\w*)\s*\(",
            previous_line
        )

        if match:
            function_name = match.group(1)
            break

    if function_name:
        call_match = re.fullmatch(
            rf"{re.escape(function_name)}\s*\(.*\)",
            selected_line
        )

        if call_match:
            return (
                f"Boss, Line {line_number} has a logical problem. "
                f"It calls {function_name}() from inside the same "
                f"{function_name}() function. That creates "
                "recursion because the function keeps calling "
                "itself."
            )

    # --------------------------------------------------
    # FALLBACK TO AI
    # --------------------------------------------------

    issue_text = get_issue_text(
        context["issues"]
    )

    response = ask_ai(
        f"""
You are Vaani, Boss's Python code assistant.

Boss asked:

{user_text}

Boss specifically wants Line {line_number}.

ACTUAL LINE:

Line {line_number}: {selected_line}

FULL ACTUAL CODE:

{context["numbered_code"]}

SYNTAX RESULT:

{context["syntax_result"]}

CONFIRMED PYLINT ISSUES:

{issue_text}

STRICT RULES:

1. Analyze only the actual code above.
2. Never invent a syntax error.
3. Never invent a typo.
4. Never invent a missing comma.
5. Never claim an error that is not visible.
6. Always use the exact requested line number.
7. Explain what the line actually does.
8. If the line is valid, say that it is valid.
9. Check surrounding code when necessary.
10. Keep the explanation beginner-friendly.
11. Do not provide corrected code unless Boss asks.
12. Do not contradict the actual code.
13. Return ONLY a short spoken answer.
"""
    )

    return response.strip()


# ==================================================
# FULL CODE EXPLANATION
# ==================================================
def explain_code(context, user_text):
    """
    Explain the actual Python code using the real execution output.
    """

    numbered_code = context.get("numbered_code", "")
    syntax_result = context.get("syntax_result", {})
    issues = context.get("issues", [])
    file_path = context.get("file_path")

    issue_text = get_issue_text(issues)

    print("\n===== CODE SENT TO AI =====")
    print(numbered_code)
    print("===========================\n")

    # Get the REAL program output instead of asking AI to guess it.
    execution_output = "Could not execute the code."

    try:
        result = subprocess.run(
            ["python", str(file_path)],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            execution_output = result.stdout.strip()
            if not execution_output:
                execution_output = "The program produced no console output."
        else:
            execution_output = (
                "Program execution failed.\n"
                + result.stderr.strip()
            )

    except Exception as error:
        execution_output = f"Could not execute the program: {error}"

    syntax_text = str(syntax_result)

    prompt = f"""
You are Vaani, a careful Python code explanation assistant.

The numbered code below is the ONLY source of truth for the code.

The REAL EXECUTION OUTPUT is also provided below.
You MUST use that exact output.
Never invent or add any output.

==================================================
ACTUAL NUMBERED CODE
==================================================

{numbered_code}

==================================================
REAL EXECUTION OUTPUT
==================================================

{execution_output}

==================================================
SYNTAX RESULT
==================================================

{syntax_text}

==================================================
PYLINT ISSUES
==================================================

{issue_text}

==================================================
STRICT RULES
==================================================

1. Explain only the code shown above.

2. Never use an older version of the code.

3. Do not invent functions, variables, function calls,
   parameters, line numbers, or output.

4. A function definition only defines a function.
   It does NOT execute the function body.

5. A print statement inside a function contributes to the
   program output ONLY if that function is actually called.

6. Do not include output from an uncalled function.

7. The REAL EXECUTION OUTPUT section is authoritative.
   Copy only the output that actually appears there.

8. Do not add expected output, possible output, or guessed output.

9. Explain every actual function definition.

10. Explain every actual variable assignment.

11. Explain every actual function call.

12. Follow execution from top to bottom.

13. Distinguish positional arguments from keyword arguments.

14. Do not claim an assignment is a function call.

15. Do not claim a function was called if there is no actual call.

16. Do not call Pylint warnings syntax errors unless they
    actually are syntax errors.

17. Explain Pylint issues according to their actual rule
    and message.

18. If there are no Pylint issues, clearly say so.

19. Do not claim the module performs something that is not
    actually present in the code.

20. Keep the explanation beginner-friendly and concise.

==================================================
RESPONSE FORMAT
==================================================

Start with:

Boss, let's break down the actual code step by step.

Then explain:

1. Module purpose
2. Function definitions
3. Variable assignments
4. Function calls
5. Execution order
6. Pylint issues
7. Actual output

For Actual output, use ONLY the REAL EXECUTION OUTPUT
provided above.

==================================================
USER REQUEST
==================================================

{user_text}
"""

    return ask_ai(prompt)


# ==================================================
# FIX CODE
# ==================================================

def fix_code(original_code, issues):
    normalized_issues = []

    if isinstance(issues, list):
        for issue in issues:
            if isinstance(issue, dict):
                normalized_issues.append(issue)
            else:
                normalized_issues.append({
                    "line": 0,
                    "message": str(issue),
                    "symbol": ""
                })
    elif isinstance(issues, dict):
        normalized_issues.append(issues)
    elif isinstance(issues, str):
        normalized_issues.append({
            "line": 0,
            "message": issues,
            "symbol": ""
        })

    issue_text = get_issue_text(normalized_issues)

    undefined_match = re.search(r"Undefined variable ([a-zA-Z_][a-zA-Z0-9_]*)", issue_text, re.IGNORECASE)





    if undefined_match:
        variable_name = undefined_match.group(1)
        return (
            None,
            f"Boss, the variable '{variable_name}' is actually undefined. "
            "I will not guess its value."
        )

    if not normalized_issues:
        return (
            None,
            "Boss, I could not find any confirmed issues to fix."
        )

    prompt = (
        "You are Vaani, a careful Python code fixer.\n\n"
        "ACTUAL PYTHON CODE:\n"
        "```python\n"
        + original_code
        + "\n```\n\n"
        "CONFIRMED PYLINT ISSUES:\n"
        + issue_text
        + "\n\n"
        "Fix ALL confirmed issues. Do not leave C0103, E0102, or W0621 unresolved.\n"
        "Return one complete corrected Python program.\n"
        "Preserve the original purpose and behavior.\n"
        "Do not invent unrelated features.\n\n"
        "C0103: Fix the naming-style issue by using a meaningful valid Python name.\n"
        "E0102: Remove duplicate function definitions while preserving behavior.\n"
        "W0621: The function parameter must not shadow the outer/module-level variable.\n"
        "Rename the parameter and update its uses inside the function.\n"
        "If the outer variable is not actually needed, remove it safely.\n"
        "Keep function calls and program behavior correct.\n"
        "Do not claim that these issues cannot be safely fixed.\n"
        "Actually change the code to resolve every confirmed issue.\n"
        "Return ONLY one Python code block."
    )

    try:
        response = ask_ai(prompt)
    except Exception as exc:
        return None, f"Boss, the AI fixer could not be reached: {exc}"

    fixed_code = extract_python_code(response)

    if not fixed_code:
        return None, "Boss, the AI fixer did not return corrected Python code."

    fixed_code = fix_code_quality_issues(fixed_code)

    if not is_valid_python(fixed_code):
        return None, "Boss, the AI-generated fix was rejected because it is not valid Python."

    if fixed_code.strip() == original_code.strip():
        return None, "Boss, the confirmed issues were not changed."

    fixed_file_path.write_text(fixed_code, encoding="utf-8")
    fixed_context = get_code_context(fixed_file_path)

    return fixed_context, None


def fix_specific_line(line_number):
    global last_requested_line

    context = analyze_code()

    lines = context["code"].splitlines()

    if line_number < 1 or line_number > len(lines):
        return (
            f"Boss, Line {line_number} does not exist."
        )

    selected_line = lines[line_number - 1].strip()

    # --------------------------------------------------
    # FIX print("message")
    # --------------------------------------------------

    if re.fullmatch(
        r'print\s*\(\s*["\']message["\']\s*\)',
        selected_line
    ):
        indentation = (
            lines[line_number - 1]
            [
                :len(lines[line_number - 1])
                - len(lines[line_number - 1].lstrip())
            ]
        )

        lines[line_number - 1] = (
            indentation + "print(message)"
        )

        new_code = "\n".join(lines) + "\n"

        file_path.write_text(
            new_code,
            encoding="utf-8"
        )

        last_requested_line = None

        return (
            f"Done Boss. Line {line_number} is fixed. "
            'Changed print("message") to print(message).'
        )

    # --------------------------------------------------
    # FIND FUNCTION FOR RECURSION FIX
    # --------------------------------------------------

    function_name = None
    function_start = None

    for i in range(
        line_number - 1,
        -1,
        -1
    ):
        line = lines[i]

        match = re.match(
            r"^(\s*)def\s+([a-zA-Z_]\w*)\s*\(",
            line
        )

        if match:
            function_name = match.group(2)
            function_start = i
            break

    # --------------------------------------------------
    # FIX RECURSIVE CALL
    # --------------------------------------------------

    if function_name is not None:
        line_indent = (
            len(lines[line_number - 1])
            - len(lines[line_number - 1].lstrip())
        )

        function_indent = (
            len(lines[function_start])
            - len(lines[function_start].lstrip())
        )

        if (
            line_indent > function_indent
            and re.fullmatch(
                rf"{re.escape(function_name)}\s*\(.*\)",
                selected_line
            )
        ):
            recursive_call = (
                lines.pop(line_number - 1).strip()
            )

            lines.append(recursive_call)

            new_code = "\n".join(lines) + "\n"

            file_path.write_text(
                new_code,
                encoding="utf-8"
            )

            last_requested_line = None

            return (
                f"Done Boss. Line {line_number} is fixed. "
                f"The recursive {function_name}() call was moved "
                "outside the function body."
            )

    # --------------------------------------------------
    # NO SAFE SPECIFIC FIX
    # --------------------------------------------------

    return (
        f"Boss, I can explain Line {line_number}, "
        "but I do not want to change it blindly. "
        "For this line, use the full code fix command."
    )


# ==================================================
# RUN CODE
# ==================================================

def run_code():
    global last_runtime_error

    last_runtime_error = None

    try:
        python_exe = (
            BASE_DIR
            / "venv"
            / "Scripts"
            / "python.exe"
        )

        result = subprocess.run(
            [
                str(python_exe),
                str(file_path)
            ],
            capture_output=True,
            text=True,
            timeout=15
        )

        # --------------------------------------------------
        # SUCCESS
        # --------------------------------------------------

        if result.returncode == 0:
            output = result.stdout.strip()

            if output:
                return (
                    "Done Boss. Code ran successfully. "
                    f"Output: {output}"
                )

            return (
                "Done Boss. Code ran successfully. "
                "There was no output."
            )

        # --------------------------------------------------
        # ERROR
        # --------------------------------------------------

        error = result.stderr.strip()

        if error:
            last_runtime_error = error

            error_lower = error.lower()

            if "nameerror" in error_lower:
                return (
                    "Boss, the code has a runtime error. "
                    "A variable or name is being used before "
                    "it was defined. "
                    f"Error: {error}"
                )

            if "typeerror" in error_lower:
                return (
                    "Boss, the code has a runtime error. "
                    "The code is using an incorrect data type "
                    "or operation. "
                    f"Error: {error}"
                )

            if "indexerror" in error_lower:
                return (
                    "Boss, the code has a runtime error. "
                    "The code is trying to access an invalid "
                    "list position. "
                    f"Error: {error}"
                )

            if "keyerror" in error_lower:
                return (
                    "Boss, the code has a runtime error. "
                    "The requested dictionary key does not exist. "
                    f"Error: {error}"
                )

            if "zerodivisionerror" in error_lower:
                return (
                    "Boss, the code has a runtime error. "
                    "The code is trying to divide by zero. "
                    f"Error: {error}"
                )

            if "attributeerror" in error_lower:
                return (
                    "Boss, the code has a runtime error. "
                    "An object does not have the requested "
                    "attribute or method. "
                    f"Error: {error}"
                )

            return (
                "Boss, the code has a runtime error. "
                f"Error: {error}"
            )

        return (
            "Boss, the code could not run successfully."
        )

    except subprocess.TimeoutExpired:
        return (
            "Boss, the code took too long to run "
            "and was stopped."
        )

    except Exception as e:
        last_runtime_error = str(e)

        return (
            f"Boss, I could not run the code. Error: {e}"
        )


# ==================================================
# CODE REQUEST HANDLER
# ==================================================

def handle_code_request(user_text):
    global last_requested_line
    global last_code_request
    global last_runtime_error

    context = analyze_code()

    user_lower = user_text.lower()

    requested_line = get_requested_line(
        user_text
    )

    # ==================================================
    # RUN CODE
    # ==================================================

    run_request = any(
        phrase in user_lower
        for phrase in [
            "run the code",
            "run code",
            "execute the code",
            "execute code",
            "run the program",
            "execute the program",
            "code chalao",
            "code run karo",
            "program chalao",
            "program run karo",
            "run it",
            "run"
        ]
    )

    if run_request:
        last_code_request = True

        return run_code()

    # ==================================================
    # FIX RUNTIME ERROR
    # ==================================================

    fix_runtime_request = any(
        phrase in user_lower
        for phrase in [
            "fix it",
            "fix the error",
            "fix this error",
            "fix runtime error",
            "fix the runtime error",
            "error fix karo",
            "isko fix karo",
            "ise fix karo"
        ]
    )

    if fix_runtime_request:
        if not last_runtime_error:
            return (
                "Boss, I do not have a recent runtime error "
                "to fix. Please run the code first."
            )

        context = analyze_code()

        runtime_issue = (
            "Runtime error detected during execution:\n"
            f"{last_runtime_error}"
        )

        runtime_context = {
            "code": context["code"],
            "issues": [
                runtime_issue
            ]
        }

        fixed_context, fix_message = fix_code(
            runtime_context
        )

        if fix_message:
            return fix_message

        if fixed_context is None:
            return (
                "Boss, I could not create a safe fix "
                "for this runtime error."
            )

        if (
            fixed_context["code"].strip()
            == context["code"].strip()
        ):
            return (
                "Boss, I cannot safely fix this runtime error "
                "automatically because the correct value or "
                "definition for the undefined variable is not "
                "clear from the code."
            )

        file_path.write_text(
            fixed_context["code"],
            encoding="utf-8"
        )

        verification_result = run_code()

        if last_runtime_error:
            return (
                "Boss, I attempted to fix the runtime error, "
                "but the code still has an error. "
                f"{verification_result}"
            )

        return (
            "Done Boss. I fixed the runtime error "
            "and verified the code successfully. "
            f"{verification_result}"
        )

    # ==================================================
    # LINE-SPECIFIC REQUEST
    # ==================================================

    if requested_line is not None:
        last_requested_line = requested_line
        last_code_request = True

        is_fix_request = any(
            phrase in user_lower
            for phrase in [
                "fix",
                "correct",
                "repair",
                "thik",
                "theek"
            ]
        )

        if is_fix_request:
            return fix_specific_line(
                requested_line
            )

        return explain_line(
            context,
            requested_line,
            user_text
        )

    # ==================================================
    # FOLLOW-UP FIX
    # ==================================================

    if last_requested_line is not None:
        follow_up_fix = any(
            phrase in user_lower
            for phrase in [
                "correct it",
                "fix it",
                "repair it",
                "thik it",
                "theek it",
                "correct this",
                "fix this",
                "repair this",
                "isko correct",
                "isko fix",
                "isko thik",
                "isko theek"
            ]
        )

        if follow_up_fix:
            return fix_specific_line(
                last_requested_line
            )

    # ==================================================
    # FULL CODE FIX
    # ==================================================

    full_fix_request = any(
        phrase in user_lower
        for phrase in [
            "fix the code",
            "fix my code",
            "correct the code",
            "correct my code",
            "repair the code",
            "repair my code",
            "debug the code",
            "debug my code",
            "isko fix",
            "isko correct",
            "isko thik",
            "isko theek",
            "code ko fix",
            "code ko correct"
        ]
    )

    if full_fix_request:
        print(
            "\nVaani is fixing the confirmed issues..."
        )

        fixed_context, error = fix_code(
             context["code"],
             context["issues"]
)
    

        # --------------------------------------------------
        # SAFE FIX NOT POSSIBLE
        # --------------------------------------------------

        if error:
            return error

        if fixed_context is None:
            return (
                "Boss, I could not create a safe fixed version."
            )

        remaining_issues = fixed_context["issues"]

        # --------------------------------------------------
        # FULLY FIXED
        # --------------------------------------------------

        if (
            fixed_context["syntax_result"]["message"]
            == "No syntax errors found."
            and not remaining_issues
        ):
            file_path.write_text(
                fixed_context["code"],
                encoding="utf-8"
            )

            return (
                "Done Boss. The code has been fixed "
                "and verified successfully."
            )

        # --------------------------------------------------
        # SYNTAX OK BUT ISSUES REMAIN
        # --------------------------------------------------

        if (
            fixed_context["syntax_result"]["message"]
            == "No syntax errors found."
        ):
            remaining_text = get_issue_text(
                remaining_issues
            )

            original_text = context["code"].strip()
            fixed_text = fixed_context["code"].strip()

            if original_text != fixed_text:
                file_path.write_text(
                    fixed_context["code"],
                    encoding="utf-8"
                )

                return (
                    "Boss, I fixed the safe code-quality issues, "
                    "but some problems cannot be fixed safely "
                    "without knowing the intended code. "
                    f"Remaining issue: {remaining_text}"
                )

            return (
                "Boss, I could not safely fix the remaining "
                "problem automatically. "
                f"Remaining issue: {remaining_text}"
            )

        # --------------------------------------------------
        # FINAL SYNTAX FAILURE
        # --------------------------------------------------

        return (
            "Boss, I created a fixed file, "
            "but it did not pass the final syntax check."
        )

    # ==================================================
    # GENERAL CODE EXPLANATION
    # ==================================================

    last_code_request = True

    return explain_code(
        context,
        user_text
    )


# ==================================================
# MAIN LOOP
# ==================================================

print(
    "\nVaani Unified Assistant is ready. Say something, Boss."
)


while True:
    user_text = listen()

    if not user_text:
        continue

    user_lower = user_text.lower().strip()

    # --------------------------------------------------
    # DIRECT EXIT
    # --------------------------------------------------

    if is_only_exit_command(user_text):
        speak(
            "Okay Boss, see you later."
        )
        break

    # --------------------------------------------------
    # SAVE BOSS MESSAGE
    # --------------------------------------------------

    add_to_memory(
        "Boss",
        user_text
    )

    # --------------------------------------------------
    # REQUEST ROUTING
    # --------------------------------------------------

    if is_code_request(user_text):
        response = handle_code_request(
            user_text
        )

    elif last_code_request and any(
        phrase in user_lower
        for phrase in [
            "correct it",
            "fix it",
            "repair it",
            "correct this",
            "fix this",
            "repair this",
            "isko fix",
            "isko correct",
            "isko thik",
            "isko theek"
        ]
    ):
        response = handle_code_request(
            user_text
        )

    else:
        response = normal_conversation(
            user_text
        )

    # --------------------------------------------------
    # EXIT INCLUDED WITH ANOTHER SENTENCE
    # --------------------------------------------------

    should_exit_after_response = (
        contains_exit_request(user_text)
        and not is_only_exit_command(user_text)
    )

    # --------------------------------------------------
    # SHOW RESPONSE
    # --------------------------------------------------

    print(
        "\nVaani:",
        response
    )

    # --------------------------------------------------
    # SAVE RESPONSE
    # --------------------------------------------------

    add_to_memory(
        "Vaani",
        response
    )

    # --------------------------------------------------
    # SPEAK RESPONSE
    # --------------------------------------------------

    speak(response, force_english=is_code_request(user_text))

    # --------------------------------------------------
    # EXIT AFTER RESPONSE
    # --------------------------------------------------

    if should_exit_after_response:
        goodbye = "Okay Boss, see you later."

        print(
            "\nVaani:",
            goodbye
        )

        speak(goodbye)

        break



