import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

print("Loading Vaani real-time voice model...")

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

print("Vaani real-time voice engine is ready!")
print("Speak something...")

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

    if text:
        print("You said:", text)
    else:
        print("I didn't hear anything.")

    if text.lower() in ["exit", "quit", "stop"]:
        print("Vaani is shutting down.")
        break