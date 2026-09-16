from agent.ollama_agent import ask_ai
from voice.vaani import listen, speak


print("\nVaani is ready. Say something, Boss.")


while True:
    user_text = listen()

    if not user_text:
        continue

    if any(word in user_text.lower().strip() for word in ["exit", "quit", "stop", "bye"]):
        speak("Okay Boss, see you later.")
        break

    response = ask_ai(
        f"""
You are Vaani, Boss's personal voice assistant.

Reply naturally and conversationally.
Call the user Boss.
Keep replies short, clear and helpful.
Do not introduce yourself unless Boss asks.
Do not talk about code auditing, Pylint, or this project unless Boss asks.

Boss said:

{user_text}
"""
    ).strip()

    print("Vaani:", response)

    speak(response)