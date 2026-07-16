# Forge

Forge is an AI-powered code generation tool that creates project structures and generates code based on natural language prompts using Google's Gemini models.

## Prerequisites

* Python 3.10+
* A Google Gemini API key

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd Forge/backend
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate it:

**macOS / Linux**

```bash
source .venv/bin/activate
```

**Windows**

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root and add your Gemini API key:

```env
GEMINI_API_KEY=YOUR_API_KEY
```

## Running the Application

### Start the FastAPI server

```bash
uvicorn app.Main:app --reload
```

### Run the CLI

```bash
python3 -m app.services.cli
```

## Example Prompt

```text
Create a Todo application.

Files:
- todo/
    - main.py

After creating it, modify main.py to include an interactive CLI menu for:
1. Add task
2. Delete task
3. List tasks
4. Exit

Update only the necessary files.
```

## Project Structure

```
backend/
├── app/
│   ├── core/
│   ├── services/
│   ├── Main.py
│   └── ...
├── requirements.txt
└── .env
```

## Notes

* Ensure your `GEMINI_API_KEY` is valid before running the application.
* Install all dependencies from `requirements.txt` before starting either the API or the CLI.
* The CLI accepts natural language prompts and generates project structures and source code accordingly.
