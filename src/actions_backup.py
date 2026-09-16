import subprocess
import webbrowser
from pathlib import Path


def perform_action(command):
    command = command.lower().strip()

    # Open Chrome
    if "open chrome" in command:
        subprocess.Popen(
            r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        )
        return "Opening Chrome, Boss."

    # Open VS Code
    if "open vs code" in command or "open visual studio code" in command:
        subprocess.Popen("code", shell=True)
        return "Opening Visual Studio Code, Boss."

    # Open YouTube
    if "open youtube" in command:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube, Boss."

    # Open Google
    if "open google" in command:
        webbrowser.open("https://www.google.com")
        return "Opening Google, Boss."

    # Search Google
    if command.startswith("search "):
        query = command[7:].strip()

        if query:
            webbrowser.open(
                "https://www.google.com/search?q=" +
                query.replace(" ", "+")
            )
            return f"Searching Google for {query}, Boss."

    # Open Calculator
    if "open calculator" in command or "open calculator app" in command:
        subprocess.Popen("calc.exe")
        return "Opening Calculator, Boss."

    return None