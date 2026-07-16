from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from app.core.code_writer import (
    CodeWriter,
    CodeWriterError,
    FileNode,
    FolderNode,
    ProjectSchema,
)


@dataclass
class PlannedFile:
    """A file discovered while walking the schema, before it is written."""
    rel_path: str
    purpose: str
    task: str
    dependencies: List[str] = field(default_factory=list)


@dataclass
class BuildResult:
    written: List[str] = field(default_factory=list)
    failed: List[tuple[str, str]] = field(default_factory=list)  # (path, error)


class ProjectBuilder:
    """
    Turns a validated ProjectSchema into real files/folders on disk.

    Usage:
        builder = ProjectBuilder(schema.project_name, output_dir="output")
        result = builder.build(schema, code_writer)
    """

    def __init__(self, project_name: str, output_dir: str = "output"):
        if not project_name or not project_name.strip():
            project_name = "generated_project"

        # Keep the root directory name filesystem-safe.
        safe_name = "".join(
            c if c.isalnum() or c in ("-", "_") else "_" for c in project_name.strip()
        )

        self.project_name = safe_name
        self.root_path = os.path.join(output_dir, safe_name)

    def plan_files(self, schema: ProjectSchema) -> List[PlannedFile]:
        """Walk the schema tree and flatten it into a list of files to write."""
        planned: List[PlannedFile] = []

        def walk(nodes, current_path: str):
            for node in nodes:
                if isinstance(node, FolderNode) or getattr(node, "type", None) == "folder":
                    walk(node.children, os.path.join(current_path, node.name))
                elif isinstance(node, FileNode) or getattr(node, "type", None) == "file":
                    planned.append(
                        PlannedFile(
                            rel_path=os.path.join(current_path, node.name),
                            purpose=node.purpose,
                            task=node.task,
                            dependencies=list(node.dependencies or []),
                        )
                    )

        walk(schema.folders, "")
        return planned

    def build(
        self,
        schema: ProjectSchema,
        writer: CodeWriter,
        on_file_start: Optional[Callable[[str], None]] = None,
        on_file_done: Optional[Callable[[str, bool], None]] = None,
    ) -> BuildResult:
        """
        Creates every folder/file described by `schema` under `self.root_path`,
        generating each file's contents via `writer.generate_file`.

        `on_file_start(path)` / `on_file_done(path, success)` are optional
        callbacks so a CLI can render live progress.
        """
        os.makedirs(self.root_path, exist_ok=True)

        result = BuildResult()

        for planned in self.plan_files(schema):
            full_path = os.path.join(self.root_path, planned.rel_path)

            if on_file_start:
                on_file_start(planned.rel_path)

            try:
                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                content = writer.generate_file(
                    schema=schema,
                    path=planned.rel_path,
                    purpose=planned.purpose,
                    task=planned.task,
                    dependencies=planned.dependencies,
                )

                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)

                result.written.append(planned.rel_path)

                if on_file_done:
                    on_file_done(planned.rel_path, True)

            except (CodeWriterError, OSError) as e:
                result.failed.append((planned.rel_path, str(e)))
                if on_file_done:
                    on_file_done(planned.rel_path, False)

        return result
