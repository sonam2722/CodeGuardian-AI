# CodeGuardian-AI

## AI-Powered Smart Code Auditor & Bug Fixer

CodeGuardian-AI is an AI-powered code analysis project that helps developers identify programming issues, analyze code, and understand possible improvements.

The project also includes **Vaani**, a voice-based assistant that allows users to interact with the system using natural speech.

## Features

- Python code analysis
- Syntax error detection
- Code quality analysis using Pylint
- AI-based code explanation
- Code fixing support
- Voice-based interaction using Vaani
- Speech recognition
- Voice responses
- Natural Hindi/Hinglish interaction
- Automatic Vaani startup in VS Code

## Technologies Used

- Python
- Pylint
- AST / Python code analysis
- SpeechRecognition
- SoundDevice
- Edge-TTS
- OpenAI API
- ONNX model
- VS Code
- Git & GitHub

## Project Structure

```text
AI-Code-Auditor/
│
├── input_code/
│   └── test.py
│
├── models/
│   ├── jarvis-medium.onnx
│   └── jarvis-medium.onnx.json
│
├── src/
│   ├── analyzer/
│   ├── fixer/
│   ├── agent/
│   ├── voice/
│   ├── main.py
│   ├── vaani_chat.py
│   ├── vaani_code_chat.py
│   └── vaani_unified.py
│
├── .vscode/
│   └── tasks.json
│
├── .gitignore
└── README.md