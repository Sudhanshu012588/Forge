from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.status import Status
from rich.table import Table
from rich.tree import Tree

from app.core.code_writer import CodeWriter, CodeWriterError, FolderNode, ProjectSchema
from app.core.project_builder import ProjectBuilder


class ForgeCLI:
    def __init__(self, output_dir: str = "output"):
        self.console = Console()
        self.output_dir = output_dir

        try:
            self.writer = CodeWriter()
        except CodeWriterError as e:
            self.console.print(Panel(str(e), title="Setup error", border_style="red"))
            raise SystemExit(1)

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------

    def banner(self):
        self.console.print(
            Panel.fit(
                "[bold cyan]Forge CLI[/bold cyan]\n"
                "Describe a project and Forge will scaffold it for you.\n"
                "Type [green]/exit[/green] to quit.",
                border_style="cyan",
            )
        )

    def render_schema_tree(self, schema: ProjectSchema) -> Tree:
        tree = Tree(f"[bold]{schema.project_name}[/bold]")

        def add_nodes(parent_tree, nodes):
            for node in nodes:
                if isinstance(node, FolderNode):
                    branch = parent_tree.add(f"[bold blue]{node.name}/[/bold blue]")
                    add_nodes(branch, node.children)
                else:
                    parent_tree.add(f"[green]{node.name}[/green]  [dim]{node.purpose}[/dim]")

        add_nodes(tree, schema.folders)
        return tree

    def render_tech_stack(self, schema: ProjectSchema):
        table = Table(title="Tech stack", show_header=True, header_style="bold cyan")
        table.add_column("Layer")
        table.add_column("Choice")

        ts = schema.tech_stack
        table.add_row("Frontend", ts.frontend or "-")
        table.add_row("Backend", ts.backend or "-")
        table.add_row("Database", ts.database or "-")
        if ts.other:
            table.add_row("Other", ", ".join(ts.other))

        self.console.print(table)

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self):
        self.banner()

        while True:
            try:
                prompt = Prompt.ask("\n[green]You[/green]")
            except (EOFError, KeyboardInterrupt):
                self.console.print("\n[yellow]Goodbye![/yellow]")
                break

            if not prompt.strip():
                continue

            if prompt.strip().lower() in {"exit", "/exit", "quit", "/quit"}:
                self.console.print("[yellow]Goodbye![/yellow]")
                break

            self.handle_prompt(prompt)

    def handle_prompt(self, prompt: str):
        # --- 1. Plan -----------------------------------------------------
        try:
            with Status("Planning project...", console=self.console):
                schema = self.writer.get_schema(prompt)
        except CodeWriterError as e:
            self.console.print(Panel(str(e), title="Planning failed", border_style="red"))
            return

        self.console.print()
        self.console.print(self.render_schema_tree(schema))
        self.console.print()
        self.render_tech_stack(schema)

        if not Confirm.ask("\nGenerate this project?", default=True):
            self.console.print("[yellow]Cancelled.[/yellow]")
            return

        # --- 2. Build ------------------------------------------------------
        builder = ProjectBuilder(schema.project_name, output_dir=self.output_dir)
        planned_files = builder.plan_files(schema)

        if not planned_files:
            self.console.print("[yellow]The plan didn't include any files to generate.[/yellow]")
            return

        written = []
        failed = []

        with self.console.status("") as status:
            def on_start(path: str):
                status.update(f"[cyan]Generating[/cyan] {path} ({len(written) + len(failed) + 1}/{len(planned_files)})")

            def on_done(path: str, success: bool):
                if success:
                    written.append(path)
                else:
                    failed.append(path)

            builder.build(schema, self.writer, on_file_start=on_start, on_file_done=on_done)

        # --- 3. Report -------------------------------------------------
        self.console.print()
        if written:
            self.console.print(
                f"[bold green]\u2714 Generated {len(written)} file(s)[/bold green] "
                f"in [bold]{builder.root_path}[/bold]"
            )
        if failed:
            self.console.print(f"[bold red]\u2717 {len(failed)} file(s) failed:[/bold red]")
            for path in failed:
                self.console.print(f"  [red]-[/red] {path}")


def main():
    ForgeCLI().run()


if __name__ == "__main__":
    main()
