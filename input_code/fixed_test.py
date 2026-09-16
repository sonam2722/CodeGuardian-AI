"""Auto-fixed Python module."""

def greet_world():
    """Function description."""
    print("Hello, world!")

def greet(greeting_name):
    """Function description."""
    print(f"{greeting_name}!")

USER_NAME = "Alice"
greet(greeting_name="Alice")  # Fixed shadowing issue
greet(greeting_name="World")
