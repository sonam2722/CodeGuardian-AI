import asyncio
import os
import tempfile

import edge_tts
from playsound3 import playsound
import sounddevice as sd
import speech_recognition as sr
import scipy.io.wavfile as wav


HINDI_VOICE = "hi-IN-MadhurNeural"
ENGLISH_VOICE = "en-US-ChristopherNeural"


def is_hindi_or_hinglish(text):
    hindi_words = [
        "main", "mein", "mera", "meri", "mere", "mujhe",
        "tum", "tumhe", "aap", "aapko", "kya", "kaise",
        "kaisa", "hai", "hain", "ho", "tha", "thi", "the",
        "kar", "karo", "karna", "krna", "nahi", "nahin",
        "haan", "acha", "achha", "accha", "abhi", "kyun",
        "kyon", "isko", "usko", "yeh", "ye", "woh", "wo",
        "kuch", "bahut", "aaj", "kal", "bol", "bolo",
        "bata", "batao", "chahiye", "sahi", "galat",
        "problem", "thik", "theek", "please"
    ]

    words = text.lower().split()

    if any("\u0900" <= char <= "\u097f" for char in text):
        return True

    hindi_count = sum(
        1
        for word in words
        if word.strip(".,!?") in hindi_words
    )

    return hindi_count >= 1


def speak(text, force_english=False):
    if not text:
        return

    if force_english:
        voice = ENGLISH_VOICE
        rate = "+5%"

    elif is_hindi_or_hinglish(text):
        voice = HINDI_VOICE
        rate = "+5%"

    else:
        voice = ENGLISH_VOICE
        rate = "+5%"

    async def generate_voice(audio_file):
        try:
            communicate = edge_tts.Communicate(
                text,
                voice,
                rate=rate
            )

            await communicate.save(audio_file)
            return True

        except Exception as e:
            print("Voice generation error:", e)
            return False

    temp_file = tempfile.NamedTemporaryFile(
        suffix=".mp3",
        delete=False
    )

    audio_file = temp_file.name
    temp_file.close()

    try:
        success = asyncio.run(
            generate_voice(audio_file)
        )

        if not success:
            return

        if not os.path.exists(audio_file):
            print("Voice generation error: audio file was not created.")
            return

        if os.path.getsize(audio_file) == 0:
            print("Voice generation error: audio file is empty.")
            return

        playsound(audio_file)

    except Exception as e:
        print("Audio playback error:", e)

    finally:
        if os.path.exists(audio_file):
            try:
                os.remove(audio_file)
            except OSError:
                pass


def listen():
    recognizer = sr.Recognizer()

    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True

    recognizer.operation_timeout = 10

    sample_rate = 16000
    duration = 5

    print("Vaani is listening...")

    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16"
    )

    sd.wait()

    with tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    ) as temp_file:
        audio_file = temp_file.name

    wav.write(
        audio_file,
        sample_rate,
        recording
    )

    try:
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio)

        print("You said:", text)

        return text

    except sr.UnknownValueError:
        print("Vaani could not understand what you said.")
        return ""

    except sr.RequestError:
        print("Speech recognition service is unavailable.")
        return ""

    except (TimeoutError, OSError):
      return ""

    finally:
        if os.path.exists(audio_file):
            os.remove(audio_file)


if __name__ == "__main__":
    print("Vaani microphone test started.")

    text = listen()

    print("Final result:", text)