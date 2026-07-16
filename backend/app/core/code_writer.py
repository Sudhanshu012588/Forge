from __future__ import annotations

import os
from typing import List, Literal, Optional

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field, ValidationError

load_dotenv()


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
# NOTE: We rely on `with_structured_output`, which forces the model to return
# data that already matches these Pydantic models. That means we never have
# to call `json.loads` on raw model output ourselves, which is where most
# "type errors in the JSON" (missing keys, wrong types, trailing commas,
# markdown fences around the JSON, etc.) used to come from.


class TechStack(BaseModel):
    frontend: str = ""
    backend: str = ""
    database: str = ""
    other: List[str] = Field(default_factory=list)


class FileNode(BaseModel):
    name: str  # must include the correct extension, e.g. "main.py", "package.json"
    type: Literal["file"]
    purpose: str = ""
    task: str = ""
    dependencies: List[str] = Field(default_factory=list)


class FolderNode(BaseModel):
    name: str
    type: Literal["folder"]
    children: List["Node"] = Field(default_factory=list)


Node = FolderNode | FileNode
FolderNode.model_rebuild()


class ProjectSchema(BaseModel):
    project_name: str
    description: str = ""
    tech_stack: TechStack = Field(default_factory=TechStack)
    # Root-level entries can be folders OR files (e.g. a top-level
    # README.md, .env.example, requirements.txt). Restricting this to
    # List[FolderNode] was a bug -- any project with a root-level file
    # would raise a pydantic ValidationError.
    folders: List[Node] = Field(default_factory=list)


class CodeWriterError(Exception):
    """Raised when the model fails to produce a usable schema or file."""

class CodeWriter:
    def __init__(self, model: str = "gemini-2.5-flash"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise CodeWriterError(
                "GEMINI_API_KEY is not set. Add it to your .env file."
            )

        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=0,
        )

    def get_schema(self, user_prompt: str) -> ProjectSchema:
        """
        Generates the complete project schema.
        Returns a validated Pydantic object -- never raw/partial JSON.
        """
        structured_llm = self.llm.with_structured_output(ProjectSchema)

        messages = [
            SystemMessage(
                content=(
                    "You are an expert software architect.\n"
                    "Generate a complete, buildable project architecture.\n"
                    "Every file name MUST include the correct file extension "
                    "(e.g. 'main.py', 'index.js', 'package.json', 'README.md').\n"
                    "Keep the folder tree reasonably small (max ~20 files) "
                    "unless the user explicitly asks for more."
                )
            ),
            HumanMessage(
                content=f"""
Create a complete project plan for the following request.

Project description:
{user_prompt}

Generate every folder and file required.
Each file must include:
- purpose
- task
- dependencies
"""
            ),
        ]

        try:
            result = structured_llm.invoke(messages)
        except ValidationError as e:
            raise CodeWriterError(f"Model returned an invalid project schema: {e}") from e
        except Exception as e:  # network / API errors
            raise CodeWriterError(f"Failed to generate project schema: {e}") from e

        if result is None or not isinstance(result, ProjectSchema):
            raise CodeWriterError("Model did not return a valid ProjectSchema.")

        return result

    def generate_file(
        self,
        schema: ProjectSchema,
        path: str,
        purpose: str,
        task: str,
        dependencies: List[str],
    ) -> str:
        """
        Generates the complete contents for a single file.
        Always returns a plain string (never None) so callers can safely
        write it straight to disk.
        """
        messages = [
            SystemMessage(
                content=(
                    "You are an expert software engineer.\n"
                    "Return ONLY the raw source code for the requested file.\n"
                    "Do not wrap the code in markdown fences.\n"
                    "Do not add any commentary before or after the code."
                )
            ),
            HumanMessage(
                content=f"""
Project:
{schema.model_dump_json(indent=2)}

Current file:
{path}

Purpose:
{purpose}

Task:
{task}

Dependencies:
{dependencies}

Write the COMPLETE file. Return only the code.
"""
            ),
        ]

        try:
            response = self.llm.invoke(messages)
        except Exception as e:
            raise CodeWriterError(f"Failed to generate '{path}': {e}") from e

        content = getattr(response, "content", None)

        if content is None:
            raise CodeWriterError(f"Model returned empty content for '{path}'.")

        # Some providers return a list of content blocks instead of a plain
        # string -- normalize that here so callers never see a type error.
        if isinstance(content, list):
            content = "\n".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in content
            )

        return self._strip_markdown_fence(str(content))

    @staticmethod
    def _strip_markdown_fence(code: str) -> str:
        """Defensively remove ```lang / ``` fences if the model adds them anyway."""
        text = code.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines:
                lines = lines[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines)
        return text

    def stream_schema_notes(self, user_prompt: str):
        """
        Optional: streams free-form planning commentary (not the schema
        itself) for display purposes only, e.g. in a CLI status line.
        """
        messages = [
            SystemMessage(content="You are an expert software architect."),
            HumanMessage(content=user_prompt),
        ]

        for chunk in self.llm.stream(messages):
            if chunk.content:
                yield chunk.content
