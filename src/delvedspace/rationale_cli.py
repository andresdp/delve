"""``ddspace rationale``: check the design rationale files coding agents write (JSON for agents, ``--table``)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, NoReturn, Optional

import typer
from rich.console import Console
from rich.markup import escape

from delvedspace import query_cli, rationale
from delvedspace.workspace import Workspace, WorkspaceError
from taxonomy_generator.wiki import query as q

app = typer.Typer(
    help="Check design rationale files (ddspace-rationale/1). JSON by default (for agents); --table for people.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
console = Console()
err = Console(stderr=True)


def _fail(message: str, table: bool) -> NoReturn:
    """Exit 2 with an error object: a usage error, an unreadable file or a graph that cannot be loaded."""
    err.print(f"[red]✗ Error:[/red] {escape(message)}")
    if not table:
        typer.echo(json.dumps({"error": message}, indent=2, ensure_ascii=False))
    raise typer.Exit(2)


def _graph_path(graph: Optional[Path]) -> Path:
    if graph is not None:
        return query_cli._graph_path(graph)
    return Workspace.find().root / "raw" / "graph.json"


def _render(result: Dict[str, Any], doc: Any) -> None:
    problems = result["problems"]
    name = doc.get("id") if isinstance(doc, dict) else None
    errors = sum(p["severity"] == "error" for p in problems)
    if not problems:
        console.print(f"[green]✓[/green] {escape(str(name or 'rationale'))}: no problems")
    else:  # one entry per problem, the message on its own line: paths are too long for a table column
        console.print(f"[bold]{escape(str(name or 'rationale'))}: {errors} errors, "
                      f"{len(problems) - errors} warnings[/bold]")
        for p in problems:
            mark = "[red]✗[/red]" if p["severity"] == "error" else "[yellow]![/yellow]"
            console.print(f"{mark} {p['code']}  {escape(p['path'] or '/')}", soft_wrap=True)
            console.print(f"  {escape(p['message'])}", soft_wrap=True)
    if result["resolved"]:
        query_cli._table("Resolved ids", ["id", "label"], [[r["id"], r["label"]] for r in result["resolved"]])


@app.command()
def check(file: Path = typer.Argument(..., help="The rationale file (ddspace-rationale/1 JSON)."),
          graph: Optional[Path] = query_cli.GraphOpt, table: bool = query_cli.TableOpt) -> None:
    """Check a rationale file: its structure, and with a space its ids, relations, evidence and graph hash.

    Exit code 0 when clean (warnings allowed), 1 on errors, 2 when the file or the space's graph cannot be read.
    """
    try:
        doc = rationale.load(file)
    except rationale.RationaleError as exc:
        _fail(str(exc), table)
    loaded, sha = None, None
    if rationale.names_space(doc):  # a file without a space (space: null) gets the structural rules only
        try:
            path = _graph_path(graph)
            loaded, sha = q.load(path), rationale.file_sha256(path)
        except WorkspaceError as exc:
            _fail(f"The file names a space, but {exc} Pass --graph <export folder>.", table)
        except (q.QueryError, OSError, ValueError) as exc:
            _fail(f"The file names a space, but its graph cannot be loaded: {exc}", table)
    result = rationale.check(doc, loaded, sha)
    if table:
        _render(result, doc)
    else:
        typer.echo(json.dumps(result, indent=2, ensure_ascii=False))
    raise typer.Exit(0 if result["ok"] else 1)
