import ast


def check_syntax(file_path):

    try:
        with open(file_path, "r") as file:
            code = file.read()

        ast.parse(code)

        return {
            "status": "success",
            "message": "No syntax errors found."
        }

    except SyntaxError as error:
        return {
            "status": "error",
            "message": f"Syntax error found: {error}"
        }

    except FileNotFoundError:
        return {
            "status": "error",
            "message": "File not found."
        }
