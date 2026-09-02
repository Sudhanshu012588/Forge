# Forge

Forge is an AI-powered code generation tool that creates project structures and generates code based on natural language prompts using Google's Gemini models.

## Prerequisites

* Python 3.10+
* A Google Gemini API key

# Run the agent
```Bash
source .venv/bin/activate
python3 Main.py
```

## Notes

* Ensure your `GEMINI_API_KEY` is valid before running the application.
* `WORKSPACE` is the root directory for the codebase
* Install all dependencies from `requirements.txt` before starting either the API or the CLI.
* The CLI accepts natural language prompts and generates project structures and source code accordingly.
