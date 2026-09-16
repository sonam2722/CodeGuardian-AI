import subprocess
import sys
import webbrowser
from urllib.parse import quote


def open_url(url):
    """Open URL in the default browser."""
    webbrowser.open(url, new=0)


def open_chrome():
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
            video_id = video_ids[0]

            return (
                "https://www.youtube.com/watch?v="
                + video_id
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


def perform_action(command):

    command = command.lower().strip()

    # -----------------------------------------
    # OPEN CHROME
    # -----------------------------------------

    if command in [
        "open chrome",
        "start chrome",
        "launch chrome",
    ]:

        if open_chrome():
            return "Opening Chrome, Boss."

        open_url("https://www.google.com")
        return "Opening the browser, Boss."


    # -----------------------------------------
    # OPEN VS CODE
    # -----------------------------------------

    if (
        "open vs code" in command
        or "open visual studio code" in command
    ):

        subprocess.Popen("code", shell=True)

        return "Opening Visual Studio Code, Boss."


    # -----------------------------------------
    # PLAY YOUTUBE
    # -----------------------------------------

    if command.startswith("play "):

        query = command[5:].strip()

        if query:
            return play_youtube(query)


    # -----------------------------------------
    # SEARCH YOUTUBE
    # -----------------------------------------

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


    # -----------------------------------------
    # OPEN YOUTUBE
    # -----------------------------------------

    if command in [
        "open youtube",
        "launch youtube",
        "start youtube",
    ]:

        open_url("https://www.youtube.com")

        return "Opening YouTube, Boss."


    # -----------------------------------------
    # OPEN GOOGLE
    # -----------------------------------------

    if command in [
        "open google",
        "launch google",
        "start google",
    ]:

        open_url("https://www.google.com")

        return "Opening Google, Boss."


    # -----------------------------------------
    # GOOGLE SEARCH
    # -----------------------------------------

    if command.startswith("search "):

        query = command[7:].strip()

        if query:

            url = (
                "https://www.google.com/search?q="
                + quote(query)
            )

            open_url(url)

            return (
                f"Searching Google for "
                f"{query}, Boss."
            )


    # -----------------------------------------
    # OPEN CALCULATOR
    # -----------------------------------------

    if (
        "open calculator" in command
        or "open calculator app" in command
    ):

        subprocess.Popen("calc.exe")

        return "Opening Calculator, Boss."


    # -----------------------------------------
    # NO ACTION
    # -----------------------------------------

    return None