import re
import sys
from pathlib import Path

import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel


SRC_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC_DIR))


from vaani_unified import ask_conversation
from voice.vaani import speak
from actions import perform_action
from computer_control import type_text, press_key, hotkey


def perform_computer_command(command):
    command = command.lower().strip()

    # Type text
    if command.startswith("type "):
        text = command[5:].strip()

        if text:
            return type_text(text)

    # Enter
    if command in [
        "press enter",
        "hit enter",
        "press the enter key",
    ]:
        return press_key("enter")

    # Escape
    if command in [
        "press escape",
        "press esc",
        "hit escape",
    ]:
        return press_key("esc")

    # Copy
    if command in [
        "copy",
        "press control c",
        "press ctrl c",
    ]:
        return hotkey("ctrl", "c")

    # Paste
    if command in [
        "paste",
        "press control v",
        "press ctrl v",
    ]:
        return hotkey("ctrl", "v")

    # Save
    if command in [
        "save",
        "save the file",
        "press control s",
        "press ctrl s",
    ]:
        return hotkey("ctrl", "s")

    return None


print("Loading Vaani real-time voice model...")


model = WhisperModel(
    "base.en",
    device="cpu",
    compute_type="int8",
)


print("Vaani real-time assistant is ready!")
print("Speak naturally. Say 'exit' to stop.")


SAMPLE_RATE = 16000
RECORD_SECONDS = 4


while True:

    print("\nListening...")

    recording = sd.rec(
        int(RECORD_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
    )

    sd.wait()

    audio = np.squeeze(recording)

    segments, info = model.transcribe(
        audio,
        language="en",
        task="transcribe",
        beam_size=5,
        best_of=5,
        temperature=0,
        vad_filter=True,
        vad_parameters={
            "min_silence_duration_ms": 500,
        },
        condition_on_previous_text=False,
    )

    text = " ".join(
        segment.text.strip()
        for segment in segments
    ).strip()

    if not text:
        continue

    print("You said:", text)

    command = text.lower().strip()

    # -----------------------------
    # EXIT COMMANDS
    # -----------------------------

    clean_command = re.sub(
        r"[^a-zA-Z\s]",
        "",
        command,
    ).strip()

    exit_commands = [
        "exit",
        "quit",
        "stop",
        "goodbye",
        "exit for now",
        "quit for now",
        "stop for now",
        "goodbye for now",
        "no exit for now",
        "yes exit",
    ]

    is_exit_command = (
        clean_command in exit_commands
        or clean_command.endswith(" exit")
        or clean_command.endswith(" quit")
        or clean_command.endswith(" stop")
        or clean_command.endswith(" goodbye")
    )

    # Do not treat "open exit" as an exit command
    if clean_command.startswith("open exit"):
        is_exit_command = False

    if is_exit_command:

        print("Vaani is shutting down.")

        speak(
            "Goodbye Boss!",
            force_english=True,
        )

        break

    # -----------------------------
    # COMPUTER KEYBOARD COMMANDS
    # -----------------------------

    try:

        computer_response = perform_computer_command(text)

        if computer_response:

            print(
                "Vaani:",
                computer_response,
            )

            speak(
                computer_response,
                force_english=True,
            )

            continue

        # -----------------------------
        # NORMAL COMPUTER ACTIONS
        # -----------------------------

        action_response = perform_action(text)

        if action_response:

            print(
                "Vaani:",
                action_response,
            )

            speak(
                action_response,
                force_english=True,
            )

            continue

        # -----------------------------
        # NORMAL AI CONVERSATION
        # -----------------------------

        response = ask_conversation(text)

        if response:

            print(
                "Vaani:",
                response,
            )

            speak(
                response,
                force_english=True,
            )

    except Exception as e:

        print(
            "Vaani error:",
            e,
        )
        