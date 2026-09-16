import subprocess
import webbrowser
from urllib.parse import quote


def open_url(url):
    """Open a URL in the default browser."""
    webbrowser.open(url)


def perform_action(command):
    command = command.lower().strip()

    # -----------------------------------------
    # OPEN CHROME
    # -----------------------------------------
    if "open chrome" in command:
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]

        for chrome_path in chrome_paths:
            try:
                subprocess.Popen(chrome_path)
                return "Opening Chrome, Boss."
            except FileNotFoundError:
                continue

        open_url("https://www.google.com")
        return "Opening the browser, Boss."

    # -----------------------------------------
    # OPEN VS CODE
    # -----------------------------------------
    if "open vs code" in command or "open visual studio code" in command:
        subprocess.Popen("code", shell=True)
        return "Opening Visual Studio Code, Boss."

    # -----------------------------------------
    # OPEN YOUTUBE
    # -----------------------------------------
    if "open youtube" in command:
        open_url("https://www.youtube.com")
        return "Opening YouTube, Boss."

    # -----------------------------------------
    # PLAY / SEARCH YOUTUBE
    # -----------------------------------------
    youtube_triggers = [
        "play ",
        "search youtube for ",
        "search youtube ",
        "find on youtube "
    ]

    for trigger in youtube_triggers:

        if command.startswith(trigger):

            query = command[len(trigger):].strip()

            if query:

                encoded_query = quote(query)

                url = (
                    "https://www.youtube.com/results?search_query="
                    + encoded_query
                )

                open_url(url)

                return f"Searching YouTube for {query}, Boss."

    # -----------------------------------------
    # OPEN GOOGLE
    # -----------------------------------------
    if "open google" in command:
        open_url("https://www.google.com")
        return "Opening Google, Boss."

    # -----------------------------------------
    # GOOGLE SEARCH
    # -----------------------------------------
    if command.startswith("search "):

        query = command[7:].strip()

        if query:

            encoded_query = quote(query)

            url = (
                "https://www.google.com/search?q="
                + encoded_query
            )

            open_url(url)

            return f"Searching Google for {query}, Boss."

    # -----------------------------------------
    # OPEN CALCULATOR
    # -----------------------------------------
    if (
        "open calculator" in command
        or "open calculator app" in command
    ):
        subprocess.Popen("calc.exe")
        return "Opening Calculator, Boss."

    return None