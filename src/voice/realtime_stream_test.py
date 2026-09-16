import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

print("Loading Vaani real-time voice model...")

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

print("Vaani real-time streaming engine is ready!")
print("Speak naturally. Say 'exit' to stop.")

SAMPLE_RATE = 16000
CHUNK_SECONDS = 2

while True:

    print("\nListening...")

    recording = sd.rec(
        int(CHUNK_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
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
        print("...")
        continue

    print("You said:", text)

    if text.lower().strip() in ["exit", "quit", "stop"]:
        print("Vaani is shutting down.")
        break