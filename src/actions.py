import os
import subprocess
import sys
import webbrowser
from pathlib import Path
from urllib.parse import quote


# =========================================================
# BASIC HELPERS
# =========================================================

def open_url(url):
    """Open a URL in the default browser."""
    webbrowser.open(url, new=0)


def open_chrome():
    """Open Google Chrome."""
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]

    for chrome_path in chrome_paths:
        try:
            subprocess.Popen([chrome_path])
            return True
        except (FileNotFoundError, OSError):
            continue

    return False


def open_application(command):
    """Open a Windows application using its executable."""
    try:
        subprocess.Popen(command, shell=True)
        return True
    except Exception as e:
        print("Application error:", e)
        return False


def open_folder(path):
    """Open a folder in Windows File Explorer."""
    try:
        os.startfile(path)
        return True
    except Exception as e:
        print("Folder error:", e)
        return False


# =========================================================
# YOUTUBE
# =========================================================

def get_first_youtube_video(query):
    """Get the first YouTube video URL using yt-dlp."""

    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "yt_dlp",
                f"ytsearch1:{query}",
                "--get-id",
                "--no-playlist",
                "--skip-download",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            print("YouTube error:", result.stderr.strip())
            return None

        video_ids = [
            line.strip()
            for line in result.stdout.splitlines()
            if line.strip()
        ]

        if video_ids:
            return (
                "https://www.youtube.com/watch?v="
                + video_ids[0]
            )

    except Exception as e:
        print("YouTube error:", e)

    return None


def play_youtube(query):
    """Play the first matching YouTube video."""

    video_url = get_first_youtube_video(query)

    if video_url:
        open_url(video_url)
        return f"Playing {query} on YouTube, Boss."

    search_url = (
        "https://www.youtube.com/results?search_query="
        + quote(query)
    )

    open_url(search_url)

    return (
        f"I couldn't open the video directly, "
        f"so I searched YouTube for {query}, Boss."
    )


# =========================================================
# GOOGLE SEARCH
# =========================================================

def google_search(query):
    """Search Google."""
    url = (
        "https://www.google.com/search?q="
        + quote(query)
    )

    open_url(url)

    return f"Searching Google for {query}, Boss."


# =========================================================
# SCREENSHOT
# =========================================================

def take_screenshot():
    """Take a screenshot and save it to Pictures."""

    try:
        from PIL import ImageGrab

        pictures = Path.home() / "Pictures"
        pictures.mkdir(exist_ok=True)

        screenshot_file = (
            pictures / "Vaani_Screenshot.png"
        )

        image = ImageGrab.grab()
        image.save(screenshot_file)

        return (
            f"Screenshot saved in your Pictures folder, Boss."
        )

    except Exception as e:
        print("Screenshot error:", e)
        return "I couldn't take the screenshot, Boss."


# =========================================================
# SYSTEM ACTIONS
# =========================================================

def lock_computer():
    """Lock Windows."""
    try:
        subprocess.run(
            ["rundll32.exe", "user32.dll,LockWorkStation"],
            check=False,
        )

        return "Locking the computer, Boss."

    except Exception as e:
        print("Lock error:", e)
        return "I couldn't lock the computer, Boss."


# =========================================================
# MAIN ACTION HANDLER
# =========================================================

def perform_action(command):

    command = command.lower().strip()

    # -----------------------------------------------------
    # CHROME
    # -----------------------------------------------------

    if command in [
        "open chrome",
        "start chrome",
        "launch chrome",
    ]:

        if open_chrome():
            return "Opening Chrome, Boss."

        open_url("https://www.google.com")
        return "Opening the browser, Boss."

    # -----------------------------------------------------
    # VS CODE
    # -----------------------------------------------------

    if (
        "open vs code" in command
        or "open visual studio code" in command
        or command == "start vs code"
    ):

        if open_application("code"):
            return "Opening Visual Studio Code, Boss."

        return "I couldn't open Visual Studio Code, Boss."

    # -----------------------------------------------------
    # CALCULATOR
    # -----------------------------------------------------

    if (
        command == "open calculator"
        or command == "open calculator app"
        or command == "start calculator"
        or command == "launch calculator"
    ):

        if open_application("calc.exe"):
            return "Opening Calculator, Boss."

        return "I couldn't open Calculator, Boss."

    # -----------------------------------------------------
    # NOTEPAD
    # -----------------------------------------------------

    if (
        command == "open notepad"
        or command == "start notepad"
        or command == "launch notepad"
    ):

        if open_application("notepad.exe"):
            return "Opening Notepad, Boss."

        return "I couldn't open Notepad, Boss."

    # -----------------------------------------------------
    # FILE EXPLORER
    # -----------------------------------------------------

    if command in [
        "open file explorer",
        "open explorer",
        "open files",
        "open my files",
    ]:

        if open_application("explorer.exe"):
            return "Opening File Explorer, Boss."

        return "I couldn't open File Explorer, Boss."

    # -----------------------------------------------------
    # DOWNLOADS
    # -----------------------------------------------------

    if (
        "open downloads" in command
        or "open download folder" in command
    ):

        downloads = Path.home() / "Downloads"

        if open_folder(downloads):
            return "Opening your Downloads folder, Boss."

        return "I couldn't open Downloads, Boss."

    # -----------------------------------------------------
    # DOCUMENTS
    # -----------------------------------------------------

    if (
        "open documents" in command
        or "open document folder" in command
    ):

        documents = Path.home() / "Documents"

        if open_folder(documents):
            return "Opening your Documents folder, Boss."

        return "I couldn't open Documents, Boss."

    # -----------------------------------------------------
    # DESKTOP
    # -----------------------------------------------------

    if (
        "open desktop" in command
        or "show desktop folder" in command
    ):

        desktop = Path.home() / "Desktop"

        if open_folder(desktop):
            return "Opening your Desktop folder, Boss."

        return "I couldn't open the Desktop folder, Boss."

    # -----------------------------------------------------
    # YOUTUBE PLAY
    # -----------------------------------------------------

    if command.startswith("play "):

        query = command[5:].strip()

        if query:
            return play_youtube(query)

    # -----------------------------------------------------
    # YOUTUBE SEARCH
    # -----------------------------------------------------

    youtube_triggers = [
        "search youtube for ",
        "search youtube ",
        "find on youtube ",
    ]

    for trigger in youtube_triggers:

        if command.startswith(trigger):

            query = command[len(trigger):].strip()

            if query:

                url = (
                    "https://www.youtube.com/results?search_query="
                    + quote(query)
                )

                open_url(url)

                return (
                    f"Searching YouTube for "
                    f"{query}, Boss."
                )

    # -----------------------------------------------------
    # OPEN YOUTUBE
    # -----------------------------------------------------

    if command in [
        "open youtube",
        "launch youtube",
        "start youtube",
    ]:

        open_url("https://www.youtube.com")

        return "Opening YouTube, Boss."

    # -----------------------------------------------------
    # GOOGLE
    # -----------------------------------------------------

    if command in [
        "open google",
        "launch google",
        "start google",
    ]:

        open_url("https://www.google.com")

        return "Opening Google, Boss."

    # -----------------------------------------------------
    # GOOGLE SEARCH
    # -----------------------------------------------------

    if command.startswith("search "):

        query = command[7:].strip()

        if query:
            return google_search(query)

    # -----------------------------------------------------
    # GMAIL
    # -----------------------------------------------------

    if command in [
        "open gmail",
        "start gmail",
        "launch gmail",
    ]:

        open_url("https://mail.google.com")

        return "Opening Gmail, Boss."

    # -----------------------------------------------------
    # GITHUB
    # -----------------------------------------------------

    if command in [
        "open github",
        "start github",
        "launch github",
    ]:

        open_url("https://github.com")

        return "Opening GitHub, Boss."

    # -----------------------------------------------------
    # CHATGPT
    # -----------------------------------------------------

    if command in [
        "open chatgpt",
        "start chatgpt",
        "launch chatgpt",
    ]:

        open_url("https://chatgpt.com")

        return "Opening ChatGPT, Boss."

    # -----------------------------------------------------
    # SCREENSHOT
    # -----------------------------------------------------

    if command in [
        "take screenshot",
        "take a screenshot",
        "capture screen",
        "screenshot",
    ]:

        return take_screenshot()

    # -----------------------------------------------------
    # LOCK COMPUTER
    # -----------------------------------------------------

    if command in [
        "lock computer",
        "lock my computer",
        "lock the computer",
        "lock pc",
    ]:

        return lock_computer()

    # -----------------------------------------------------
    # NO ACTION FOUND
    # -----------------------------------------------------

    return None