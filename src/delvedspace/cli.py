"""The ``ddspace`` command line (Typer, rendered with rich)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from delvedspace import __version__
from delvedspace import sources as src
from delvedspace import workspace as wsmod
from delvedspace.corpus import MAX_WORDS, MIN_WORDS, TARGET_WORDS
from delvedspace.workspace import CONFIG_NAME, Settings, Workspace, WorkspaceError

app = typer.Typer(
    name="ddspace",
    help="DelveDSpace: mine a design space from your sources and publish it as a wiki.",
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode="rich",
)
console = Console()

DEFAULT_USE_CASE = ("Identify the design decisions practitioners face, the alternatives they consider for each, "
                    "and the outcomes they report.")


def interactive(yes: bool) -> bool:
    """Ask questions only when a person is at the terminal and ``--yes`` was not given."""
    return not yes and sys.stdin.isatty()


def fail(message: str, code: int = 1) -> None:
    """Print an error and exit."""
    console.print(f"[red]Error:[/red] {message}")
    raise typer.Exit(code)


def current_workspace() -> Workspace:
    """Return the workspace around the current folder, or exit with a hint."""
    try:
        return Workspace.find()
    except WorkspaceError as exc:
        fail(str(exc))
        raise  # unreachable; keeps type checkers happy


def version_callback(value: bool) -> None:
    """Print the version and exit (``--version``)."""
    if value:
        console.print(f"ddspace {__version__}")
        raise typer.Exit()


@app.callback()
def main(version: bool = typer.Option(False, "--version", callback=version_callback, is_eager=True,
                                      help="Show the version and exit.")) -> None:
    """DelveDSpace: mine a design space from your sources and publish it as a wiki."""


# ---------------------------------------------------------------- init


def _parse_max(value: str) -> Optional[int]:
    value = value.strip().lower()
    if value in ("", "none", "null", "0", "no limit"):
        return None
    if not value.isdigit():
        raise ValueError(value)
    return int(value)


def _ask_settings(s: Settings, sources_count) -> Settings:
    console.print(Panel("A few questions to set up the workspace. Press Enter to keep the default.",
                        title="ddspace init", expand=False))
    s.name = Prompt.ask("Workspace name", default=s.name)
    s.use_case = Prompt.ask("Use case: what design space, for whom (one or two sentences)", default=s.use_case)
    console.print("\n[bold]Models[/bold] (provider/model; OpenAI by default)")
    s.generation_llm = Prompt.ask("  Generation LLM (builds the design space)", default=s.generation_llm)
    s.evaluation_llm = Prompt.ask("  Evaluation LLM (judges it)", default=s.evaluation_llm)
    s.embedding = Prompt.ask("  Embedding model", default=s.embedding)
    s.sources_dir = Prompt.ask("\nSources folder (your downloaded files: .md .txt .html .pdf)", default=s.sources_dir)
    console.print(f"  {sources_count(s.sources_dir)} source file(s) there now.")
    while True:
        answer = Prompt.ask("Maximum number of dimensions (none = the LLM decides)",
                            default="none" if s.max_dimensions is None else str(s.max_dimensions))
        try:
            s.max_dimensions = _parse_max(answer)
            break
        except ValueError:
            console.print("  [red]Enter a number or 'none'.[/red]")
    s.batch_size = int(Prompt.ask("Minibatch size (passages per update step)", default=str(s.batch_size)))
    s.critic = Confirm.ask("Run the critic during mining? (scores each update; off is cheaper)", default=s.critic)
    return s


def _check_api_keys(ws: Workspace, s: Settings, ask: bool) -> None:
    needed = {k for k in (wsmod.provider_key(m) for m in (s.generation_llm, s.evaluation_llm, s.embedding)) if k}
    for key in sorted(needed):
        if ws.env_value(key):
            console.print(f"[green]✓[/green] {key} found.")
            continue
        if ask and Confirm.ask(f"{key} is not set. Write it to {ws.env_path.name} now?", default=True):
            value = Prompt.ask(f"  {key}", password=True)
            if value.strip():
                ws.write_env(key, value.strip())
                console.print(f"[green]✓[/green] {key} written to .env (ignored by git).")
                continue
        console.print(f"[yellow]![/yellow] {key} is not set: add it to {ws.env_path} or your environment "
                      "before `ddspace mine`.")


@app.command()
def init(
    directory: Path = typer.Argument(Path("."), help="Workspace folder (created if missing)."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Take the defaults without asking (for scripts and agents)."),
    force: bool = typer.Option(False, "--force", help=f"Overwrite an existing {CONFIG_NAME}."),
    name: Optional[str] = typer.Option(None, help="Workspace name (default: the folder name)."),
    use_case: Optional[str] = typer.Option(None, "--use-case", help="What design space, for whom."),
    generation_llm: Optional[str] = typer.Option(None, "--generation-llm", help="provider/model that builds it."),
    evaluation_llm: Optional[str] = typer.Option(None, "--evaluation-llm", help="provider/model that judges it."),
    embedding: Optional[str] = typer.Option(None, "--embedding", help="provider/model for embeddings."),
    sources_dir: Optional[str] = typer.Option(None, "--sources-dir", help="Folder with the source files."),
    max_dimensions: Optional[int] = typer.Option(None, "--max-dimensions", help="Cap on dimensions (0 = none)."),
    batch_size: Optional[int] = typer.Option(None, "--batch-size", help="Passages per update step."),
    critic: Optional[bool] = typer.Option(None, "--critic/--no-critic", help="Run the critic during mining."),
) -> None:
    """Create a workspace: folders, a commented [bold]ddspace.yaml[/bold] and a .gitignore."""
    root = directory.resolve()
    if (root / CONFIG_NAME).exists() and not force:
        fail(f"{root / CONFIG_NAME} already exists (use --force to overwrite it).")
    s = Settings(name=name or root.name, use_case=use_case or DEFAULT_USE_CASE)
    for attr, value in (("generation_llm", generation_llm), ("evaluation_llm", evaluation_llm),
                        ("embedding", embedding), ("sources_dir", sources_dir), ("batch_size", batch_size),
                        ("critic", critic)):
        if value is not None:
            setattr(s, attr, value)
    if max_dimensions is not None:
        s.max_dimensions = max_dimensions or None
    ask = interactive(yes)
    if ask:
        s = _ask_settings(s, lambda d: len(wsmod.source_files(root / d)))
    ws = wsmod.create(root, s)
    _check_api_keys(ws, s, ask)
    n = len(wsmod.source_files(ws.root / s.sources_dir))
    console.print(Panel(
        f"Workspace [bold]{s.name}[/bold] created in {ws.root}\n"
        f"Settings: {CONFIG_NAME} (every option is commented; edit freely)\n\n"
        "Next:\n"
        f"  1. Put your source files in {s.sources_dir}/ ({n} there now)\n"
        "  2. ddspace sources   [dim]# extract text, draft sources.csv, flag problems[/dim]\n"
        "  3. ddspace corpus    [dim]# split the sources into passages[/dim]\n"
        "  4. ddspace mine      [dim]# generate the design space[/dim]",
        title="Done", expand=False))


# ---------------------------------------------------------------- sources and corpus


@app.command("sources")
def sources_cmd() -> None:
    """Extract the text of every source file, draft or update [bold]sources.csv[/bold] and flag problems."""
    ws = current_workspace()
    if not ws.sources_dir.is_dir():
        fail(f"The sources folder {ws.sources_dir} does not exist.")
    with console.status("Extracting text..."):
        found = src.scan(ws)
    if not found:
        fail(f"No source files in {ws.sources_dir} (supported: .md .txt .html .pdf).")
    table = Table(title=f"Sources ({ws.sources_dir.relative_to(ws.root)}/)")
    for col, kw in (("id", {}), ("file", {"overflow": "fold"}), ("format", {}), ("words", {"justify": "right"}),
                    ("title", {"overflow": "fold"}), ("flags", {})):
        table.add_column(col, **kw)
    for s in found:
        style = "red" if not src.usable(s) else ("yellow" if s.flags else "")
        table.add_row(s.id, s.file, s.format, f"{s.words:,}", s.title, ", ".join(s.flags), style=style)
    console.print(table)
    flagged = sorted({f for s in found for f in s.flags})
    for flag in flagged:
        console.print(f"  [yellow]{flag}[/yellow]: {src.FLAG_HELP.get(flag, '')}")
    usable = [s for s in found if src.usable(s)]
    console.print(f"\n{len(usable)} of {len(found)} source(s) usable. Titles, URLs and types can be edited in "
                  f"{ws.sources_csv.name}; ids stay fixed. Next: [bold]ddspace corpus[/bold]")


@app.command()
def corpus(
    target_words: int = typer.Option(TARGET_WORDS, help="Passage size to aim for."),
    min_words: int = typer.Option(MIN_WORDS, help="Shorter passages are merged into a neighbour."),
    max_words: int = typer.Option(MAX_WORDS, help="Hard cap before a passage is closed."),
) -> None:
    """Split the sources into passages and write [bold]corpus.json[/bold]."""
    ws = current_workspace()
    try:
        passages = src.build_corpus(ws, target_words, min_words, max_words)
    except WorkspaceError as exc:
        fail(str(exc))
    if not passages:
        fail("No usable sources: check the flags shown by `ddspace sources`.")
    sizes = sorted(p["words"] for p in passages)
    console.print(f"{len(passages)} passages from {len({p['source_id'] for p in passages})} source(s) "
                  f"({sum(sizes):,} words; min/median/max {sizes[0]}/{sizes[len(sizes) // 2]}/{sizes[-1]}) "
                  f"-> {ws.corpus_path.name}\nNext: [bold]ddspace mine[/bold]")


if __name__ == "__main__":  # pragma: no cover
    app()
