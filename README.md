# CodeGuardian-AI

## AI-Powered Smart Code Auditor, Bug Fixer & Vaani Voice Assistant

CodeGuardian-AI is a Python-based AI code analysis system designed to help developers detect programming issues, understand code problems, and generate possible code improvements.

The project also includes **Vaani**, a voice-based assistant that allows users to interact with the system using natural speech and receive AI-powered responses.

## Features

- Python code analysis
- Syntax error detection
- Code quality analysis using Pylint
- Python AST-based analysis
- AI-based code explanation
- Code fixing support
- Code validation
- Voice-based interaction using Vaani
- Speech recognition
- Voice responses
- Hindi/Hinglish interaction
- VS Code integration

## Technologies Used

- Python
- Python AST
- Pylint
- OpenAI API
- SpeechRecognition
- SoundDevice
- Edge-TTS
- ONNX
- Visual Studio Code
- Git & GitHub

## Project Structure

```text
CodeGuardian-AI/
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


##How It Works
Python Code
     ↓
Code Analysis
     ↓
Syntax & Quality Checks
     ↓
Issue Detection
     ↓
AI Explanation
     ↓
Code Fixing
     ↓
Validation

#Vaani Voice Assistant

Vaani provides a voice-based interface for interacting with CodeGuardian-AI.

Voice Input
     ↓
Speech Recognition
     ↓
Command / Intent Detection
     ↓
AI / Code Assistant
     ↓
Action / Response
     ↓
##Voice Output

#Vaani Features
-Natural voice interaction
-Speech recognition
-AI-powered conversation
-Code-related voice queries
-Hindi/Hinglish support
-Voice responses

#Installation

Clone the repository:

git clone https://github.com/sonam272/CodeGuardian-AI.git

#Navigate to the project:

cd CodeGuardian-AI

#Create a virtual environment:

python -m venv venv

#Activate the virtual environment on Windows:

venv\Scripts\activate

#Install dependencies:

pip install -r requirements.txt
Environment Variables

#Create a .env file and add the required API key:

OPENAI_API_KEY=your_api_key_here

Do not upload your API key or .env file to GitHub.

Running the Project

#Run the main CodeGuardian analyzer:

python src/main.py

#Run the Vaani assistant:

python src/vaani_unified.py
Example Workflow
Input Python Code
       ↓
CodeGuardian analyzes the code
       ↓
Issues are detected
       ↓
AI explains the issues
       ↓
Possible fixes are generated
       ↓
Code is validated

#Future Improvements
-Web-based interface
-Support for multiple programming languages
-Advanced AI-powered debugging
-Automatic code optimization
-GitHub repository analysis
-Improved voice command handling
-VS Code extension
-Real-time code assistance

#Author
Developed as a final-year BTech CSE project.

#License
This project is developed for educational and learning purposes.
