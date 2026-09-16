import sys
from pathlib import Path

import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

# src folder ko Python path mein add karo
SRC_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC_DIR))

from vaani_unified import ask_conversation
from voice.vaani import speak


print("Loading Vaani real-time voice model...")

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

print("Vaani real-time assistant is ready!")
print("Speak to Vaani. Say 'exit' to stop.")

sample_rate = 16000
duration = 5

while True:

    print("\nListening...")

    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="float32"
    )

    sd.wait()

    audio = np.squeeze(recording)

    segments, info = model.transcribe(
        audio,
        language="en",
        vad_filter=True
    )

    text = " ".join(
        segment.text.strip()
        for segment in segments
    ).strip()

    if not text:
        print("I didn't hear anything.")
        continue

    print("You said:", text)

    if text.lower().strip() in ["exit", "quit", "stop"]:
        print("Vaani is shutting down.")
        speak("Goodbye Boss!")
        break

    try:
        response = ask_conversation(text)

        if response:
            print("Vaani:", response)
            speak(response, force_english=True)   
        else:
            print("Vaani: I couldn't generate a response.")

    except Exception as e:
        print("Vaani error:", e)