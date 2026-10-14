"""The ``ddspace`` command line (Typer, rendered with rich)."""

from __future__ import annotations

import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List, NoReturn, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

from delvedspace import __version__, agent, query_cli, runs
from delvedspace import sources as src
from delvedspace import wiki_build as wb
from delvedspace import workspace as wsmod
from delvedspace.corpus import MAX_WORDS, MIN_WORDS, TARGET_WORDS
from delvedspace.workspace import CONFIG_NAME, Settings, Workspace, WorkspaceError
from taxonomy_generator.wiki import okf

app = typer.Typer(
    name="ddspace",
    help="DelveDSpace: mine a design space from your sources and publish it as a wiki.",
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode="rich",
)
console = Console()
app.add_typer(query_cli.app, name="query")
agent_app = typer.Typer(help="Connect a coding agent (Claude Code, GitHub Copilot) to the wiki.", no_args_is_help=True)
app.add_typer(agent_app, name="agent")
wiki_app = typer.Typer(help="Build, check and open the wiki of the current design space.", no_args_is_help=True)
app.add_typer(wiki_app, name="wiki")

DEFAULT_USE_CASE = ("Identify the design decisions practitioners face, the alternatives they consider for each, "
                    "and the outcomes they report.")


def interactive(yes: bool) -> bool:
    """Ask questions only when a person is at the terminal and ``--yes`` was not given."""
    return not yes and sys.stdin.isatty()


def fail(message: str, code: int = 1) -> NoReturn:
    """Print an error and exit."""
    console.print(f"[red]Error:[/red] {message}")
    raise typer.Exit(code)


def current_workspace() -> Workspace:
    """Return the workspace around the current folder, or exit with a hint."""
    try:
        return Workspace.find()
    except WorkspaceError as exc:
        fail(str(exc))


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
    s.batch_size = IntPrompt.ask("Minibatch size (passages per update step)", default=s.batch_size)
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


# ---------------------------------------------------------------- mine and update


def _format_duration(seconds: float) -> str:
    minutes = round(seconds / 60)
    return f"{minutes} min" if minutes < 90 else f"{minutes / 60:.1f} h"


def _confirm_run(ws: Workspace, title: str, lines: List[str], passages: int, yes: bool) -> bool:
    cfg = ws.config()
    est = runs.estimate(ws, passages, int((cfg.get("pipeline") or {}).get("batch_size") or 10))
    models = cfg.get("models") or {}
    critic = (cfg.get("evaluation") or {}).get("enabled", True)
    body = "\n".join(lines + [
        f"Passages: {passages} in about {est.batches} minibatch(es); critic {'on' if critic else 'off'}",
        f"Models: {models.get('generation_llm')} (generation), {models.get('evaluation_llm')} (evaluation)",
        f"Estimate ({est.basis}): about {est.tokens / 1e6:.1f}M tokens, {_format_duration(est.seconds)}",
    ])
    console.print(Panel(body, title=title, expand=False))
    return not interactive(yes) or Confirm.ask("Start?", default=True)


def _execute(ws: Workspace, run: runs.Run, run_dir: Path, corpus: Path, extra: List[str],
             html_report: bool) -> None:
    """Run the pipeline for ``run``, record the outcome and make a successful run current."""
    run.argv = ["--corpus", runs.relative(ws, corpus), "--config", wsmod.CONFIG_NAME,
                "--output", runs.relative(ws, run_dir), *extra]
    runs.save(run_dir, run)
    try:
        code = runs.run_pipeline(ws, run.argv)
    except KeyboardInterrupt:
        code = 130
    taxonomy = runs.find_taxonomy(run_dir)
    run.finished_at = datetime.now().isoformat(timespec="seconds")
    run.status = "ok" if code == 0 and taxonomy else "failed"
    run.taxonomy = taxonomy.name if taxonomy else None
    runs.save(run_dir, run)
    if run.status != "ok":
        fail(f"The run failed (exit code {code}); its folder {runs.relative(ws, run_dir)} is kept for inspection. "
             "The current design space is unchanged.")
    ws.set("workspace.current_run", runs.relative(ws, run_dir))
    if html_report or (ws.config().get("wiki") or {}).get("html_report"):
        runs.run_pipeline(ws, ["--html-report", runs.relative(ws, taxonomy), "--config", wsmod.CONFIG_NAME,
                               "--output", runs.relative(ws, run_dir)])
    data = wsmod.read_json(taxonomy)
    dims = wb.selected_dims(data)
    metrics = data.get("run_metrics") or {}
    _warn_if_all_dropped(data)
    console.print(Panel(
        f"Run [bold]{run.id}[/bold] ({run.kind}) is now the current design space.\n"
        f"{len(dims)} dimensions, {sum(len(d.get('values') or []) for d in dims)} values"
        + (f"; {metrics.get('total_tokens', 0):,} tokens, {_format_duration(metrics.get('elapsed_seconds', 0))}"
           if metrics else "")
        + f"\nFiles: {runs.relative(ws, run_dir)}/\n\nNext: [bold]ddspace wiki build[/bold]",
        title="Done", expand=False))


def _warn_if_all_dropped(taxonomy: dict) -> None:
    dropped = wb.dropped_count(taxonomy)
    if dropped and not wb.selected_dims(taxonomy):
        console.print(f"[yellow]![/yellow] Dimension selection dropped all {dropped} dimension(s) (see "
                      "synthesis/dropped in the wiki). With few sources, lower taxonomy.min_dimension_sources "
                      "in ddspace.yaml and run `ddspace mine --fresh`, or add sources.")


def _corpus_or_fail(ws: Workspace) -> List[dict]:
    if not ws.corpus_path.is_file():
        fail("No corpus.json yet. Run `ddspace sources` and `ddspace corpus` first.")
    corpus = runs.read_corpus(ws.corpus_path)
    if not corpus:
        fail("corpus.json is empty. Check the flags shown by `ddspace sources`.")
    in_corpus = {p.get("source_id") for p in corpus}
    newer = [s.id for s in src.load_manifest(ws) if src.usable(s) and s.id not in in_corpus]
    if newer:
        console.print(f"[yellow]![/yellow] Sources not in corpus.json yet: {', '.join(newer)}. "
                      "Run `ddspace corpus` to include them.")
    return corpus


@app.command()
def mine(
    fresh: bool = typer.Option(False, "--fresh", help="Mine from scratch even when a design space exists."),
    max_dimensions: Optional[int] = typer.Option(None, "--max-dimensions", help="Override taxonomy.max_num_clusters (0 = none)."),
    html_report: bool = typer.Option(False, "--html-report", help="Also write the pipeline's HTML report (about 7 MB)."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Start without asking."),
) -> None:
    """Generate the design space from the corpus (a new run under [bold]runs/[/bold])."""
    ws = current_workspace()
    try:
        current = runs.current_run_dir(ws)
    except WorkspaceError:
        current = None
    if current is not None and not fresh:
        fail(f"A design space exists (run {current.name}). Use `ddspace update` to refine it, "
             "or `ddspace mine --fresh` to start over from scratch.")
    corpus = _corpus_or_fail(ws)
    lines = [f"Corpus: {len(corpus)} passages from {len({p.get('source_id') for p in corpus})} source(s)"]
    if not _confirm_run(ws, "ddspace mine", lines, len(corpus), yes):
        raise typer.Exit()
    run_dir = runs.new_run_dir(ws)
    run = runs.Run(id=run_dir.name, kind="mine", started_at=datetime.now().isoformat(timespec="seconds"),
                   source_ids=src.corpus_source_ids(corpus), passages=len(corpus))
    extra = ["-k", str(max_dimensions)] if max_dimensions is not None else []
    _execute(ws, run, run_dir, ws.corpus_path, extra, html_report)


def _import_sources(ws: Workspace, files: List[Path]) -> None:
    ws.sources_dir.mkdir(parents=True, exist_ok=True)
    for f in files:
        if not f.is_file():
            fail(f"{f} is not a file.")
        if f.suffix.lower() not in wsmod.SOURCE_SUFFIXES:
            fail(f"{f.name}: unsupported type (use .md .txt .html .pdf).")
        target = ws.sources_dir / f.name
        if target.exists() and target.read_bytes() != f.read_bytes():
            fail(f"{target} already exists with other content; rename the new file.")
        if f.resolve() != target.resolve():
            shutil.copy2(f, target)


@app.command()
def update(
    feedback: Optional[str] = typer.Option(None, "--feedback", help="Your feedback on the design space (text)."),
    feedback_file: Optional[Path] = typer.Option(None, "--feedback-file", help="A file with your feedback."),
    test: bool = typer.Option(False, "--test", help="Test mode: dimensions frozen; new sources only add values."),
    new_sources: Optional[List[Path]] = typer.Option(None, "--sources", help="Test mode: new source files to add (copied into the sources folder)."),
    html_report: bool = typer.Option(False, "--html-report", help="Also write the pipeline's HTML report."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Start without asking."),
) -> None:
    """Update the current design space: with your [bold]--feedback[/bold], or with new sources in [bold]--test[/bold] mode."""
    ws = current_workspace()
    if test == bool(feedback or feedback_file):
        fail("Choose one: --feedback/--feedback-file (re-mine with your feedback) or --test (add new sources).")
    if feedback and feedback_file:
        fail("Use either --feedback or --feedback-file, not both.")
    if new_sources and not test:
        fail("--sources goes with --test.")
    try:
        seed = runs.current_taxonomy(ws)
    except WorkspaceError as exc:
        fail(str(exc))
    seed_dir = seed.parent
    seed_run = runs.load(seed_dir)
    started = datetime.now().isoformat(timespec="seconds")

    if not test:
        text = feedback if feedback else feedback_file.read_text(encoding="utf-8") if feedback_file.is_file() else None
        if not text or not text.strip():
            fail(f"No feedback text{f' in {feedback_file}' if feedback_file else ''}.")
        corpus = _corpus_or_fail(ws)
        lines = [f"Starting from run {seed_dir.name}, re-mining {len(corpus)} passages with your feedback:",
                 f"  [italic]{text.strip()[:300]}{'...' if len(text.strip()) > 300 else ''}[/italic]"]
        if not _confirm_run(ws, "ddspace update --feedback", lines, len(corpus), yes):
            raise typer.Exit()
        run_dir = runs.new_run_dir(ws)
        run = runs.Run(id=run_dir.name, kind="update-feedback", started_at=started, seed_run=seed_dir.name,
                       feedback=text.strip(), passages=len(corpus), source_ids=src.corpus_source_ids(corpus))
        _execute(ws, run, run_dir, ws.corpus_path, ["--taxonomy", runs.relative(ws, seed), "--feedback", text.strip()],
                 html_report)
        return

    if new_sources:
        _import_sources(ws, list(new_sources))
    with console.status("Extracting text..."):
        scanned = src.scan(ws)
    covered = set(seed_run.source_ids) if seed_run and seed_run.source_ids else \
        set(src.corpus_source_ids(runs.read_corpus(ws.corpus_path))) if ws.corpus_path.is_file() else set()
    new_ids = [s.id for s in scanned if src.usable(s) and s.id not in covered]
    if not new_ids:
        fail("No new sources: every usable source is already in the design space. Add files with --sources, "
             "or put them in the sources folder.")
    added = [p for s in scanned if s.id in new_ids for p in src.source_passages(ws, s)]
    lines = [f"Starting from run {seed_dir.name} (dimensions frozen); new sources: {', '.join(new_ids)}"]
    if not _confirm_run(ws, "ddspace update --test", lines, len(added), yes):
        raise typer.Exit()
    src.append_to_corpus(ws, added)
    run_dir = runs.new_run_dir(ws)
    new_corpus = run_dir / "corpus_new.json"
    runs.write_corpus(new_corpus, added)
    run = runs.Run(id=run_dir.name, kind="update-test", started_at=started, seed_run=seed_dir.name,
                   source_ids=sorted(covered | set(new_ids)), new_source_ids=new_ids, passages=len(added))
    _execute(ws, run, run_dir, new_corpus, ["--taxonomy", runs.relative(ws, seed), "--mode", "test"], html_report)


# ---------------------------------------------------------------- agent setup


@agent_app.command("setup")
def agent_setup(
    claude: bool = typer.Option(False, "--claude", help="Also write CLAUDE.md (imports AGENTS.md)."),
    copilot: bool = typer.Option(False, "--copilot", help="Also write .github/copilot-instructions.md."),
    allow: Optional[bool] = typer.Option(None, "--allow-query/--no-allow-query",
                                         help="With --claude: let Claude Code run `ddspace query` without asking each time."),
    directory: Optional[Path] = typer.Option(None, "--dir", help="Where the agent works: the workspace (default) "
                                             "or a project folder that contains it."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Take the defaults without asking."),
) -> None:
    """Write [bold]AGENTS.md[/bold] (how to query the wiki and cite it) and the files that point agents to it."""
    ws = current_workspace()
    target = (directory or ws.root).resolve()
    if ws.root != target and target not in ws.root.parents:
        fail(f"{target} does not contain the workspace {ws.root}.")
    done = [f"{agent.upsert_block(target / 'AGENTS.md', agent.guide(ws, target))} AGENTS.md"]
    if claude:
        done.append(f"{agent.upsert_block(target / 'CLAUDE.md', agent.pointer_claude())} CLAUDE.md")
        if allow is None:
            allow = not interactive(yes) or Confirm.ask(
                "Let Claude Code run `ddspace query` (read-only) without a permission prompt each time?", default=True)
        if allow:
            done.append(f"{agent.allow_query(target / '.claude' / 'settings.json')} .claude/settings.json "
                        f"({agent.QUERY_PERMISSION})")
    if copilot:
        done.append(f"{agent.upsert_block(target / '.github' / 'copilot-instructions.md', agent.pointer_copilot())} "
                    ".github/copilot-instructions.md")
    if not (ws.root / "raw" / "graph.json").is_file():
        console.print("[yellow]![/yellow] No wiki yet: run `ddspace wiki build`, then this command again for "
                      "examples with real names.")
    tools = " and ".join(t for t, on in (("Claude Code", claude), ("GitHub Copilot (agent mode)", copilot)) if on) \
        or "your coding agent"
    console.print(Panel("\n".join(done) + f"\n\nNext: open {target} in {tools} and ask, for example:\n"
                        "  [italic]What are the alternatives for <a decision>, and which sources support each? "
                        "Cite passages.[/italic]", title="Agent setup", expand=False))


# ---------------------------------------------------------------- wiki


def _wiki_options(ws: Workspace, dims: List[dict], n_sources: int, ask_all: bool, yes: bool) -> wb.Options:
    saved = ws.config().get("wiki") or {}
    ask = interactive(yes)
    opts = wb.Options()
    suggested = wb.suggest_core(n_sources)

    def need(key: str) -> bool:
        return saved.get(key) is None or ask_all

    if ask and any(need(k) for k in ("quotes", "source_summaries", "design_points", "core_min_sources")):
        console.print(Panel("A few questions about this wiki. The answers are saved in ddspace.yaml (wiki:) "
                            "and reused; `ddspace wiki build --ask` asks again.", title="ddspace wiki build",
                            expand=False))
    if need("quotes"):
        opts.quotes = Confirm.ask("Include quoted passages on value pages? They copy source text: say no if "
                                  "the wiki will be shared publicly", default=True) if ask else True
    else:
        opts.quotes = bool(saved["quotes"])
    if need("source_summaries"):
        todo = len(wb.missing_summaries(ws))
        opts.source_summaries = Confirm.ask(
            f"Generate a short summary per source? ({todo} LLM call(s) now; stored and reused)",
            default=True) if ask else False
    else:
        opts.source_summaries = bool(saved["source_summaries"])
    if need("design_points"):
        opts.design_points = Prompt.ask(
            "Design points (sampled combinations of values): none, sample, or describe "
            "(describe = one LLM call per point)", choices=list(wb.DESIGN_POINT_CHOICES),
            default="sample") if ask else "sample"
    else:
        opts.design_points = str(saved["design_points"])
    if need("core_min_sources"):
        if ask:
            console.print(f"Core dimensions have evidence from at least N sources. Suggested N = {suggested} "
                          f"({wb.core_count(dims, suggested)} of {len(dims)} dimensions would be core; "
                          f"{n_sources} sources).")
            opts.core_min_sources = IntPrompt.ask("N", default=suggested)
        else:
            opts.core_min_sources = suggested
    else:
        try:
            opts.core_min_sources = int(saved["core_min_sources"])
        except (TypeError, ValueError):
            fail(f"wiki.core_min_sources in ddspace.yaml must be a number, not {saved['core_min_sources']!r}.")
    if ask_all and ask:
        while True:
            answer = Prompt.ask("Pages count as stale after (e.g. 90d, 12w, 6m; none)", default=saved.get("stale_after") or "none")
            opts.stale_after = None if answer.strip().lower() in ("", "none") else answer.strip()
            try:
                wb.parse_period(opts.stale_after)
                break
            except ValueError as exc:
                console.print(f"  [red]{exc}[/red]")
    else:
        opts.stale_after = saved.get("stale_after")
        try:
            wb.parse_period(opts.stale_after)
        except ValueError as exc:
            fail(f"wiki.stale_after in ddspace.yaml: {exc}")
    for key in ("quotes", "source_summaries", "design_points", "core_min_sources", "stale_after"):
        ws.set(f"wiki.{key}", getattr(opts, key))
    return opts


@wiki_app.command("build")
def wiki_build_cmd(
    run: Optional[str] = typer.Option(None, "--run", help="A run folder name under runs/ (default: the current run)."),
    ask: bool = typer.Option(False, "--ask", help="Ask the questions again instead of reusing the saved answers."),
    no_llm: bool = typer.Option(False, "--no-llm", help="Make no LLM calls: use stored summaries and descriptions only."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Take the defaults without asking."),
) -> None:
    """Export the design space: [bold]wiki/[/bold] (OKF Markdown), [bold]site/[/bold] (HTML) and [bold]raw/[/bold] (query data)."""
    ws = current_workspace()
    try:
        run_dir = (ws.runs_dir / run) if run else runs.current_run_dir(ws)
    except WorkspaceError as exc:
        fail(str(exc))
    if run_dir is None or not run_dir.is_dir() or runs.find_taxonomy(run_dir) is None:
        fail("No design space to export. Run `ddspace mine` first." if run is None
             else f"{run} is not a run folder with a taxonomy under runs/.")
    taxonomy = wsmod.read_json(runs.find_taxonomy(run_dir))
    dims = wb.selected_dims(taxonomy)
    _warn_if_all_dropped(taxonomy)
    n_sources = len(wb.run_sources(dims))
    opts = _wiki_options(ws, dims, n_sources, ask, yes)
    try:
        with console.status("Building the wiki..."):
            result = wb.build_wiki(ws, run_dir, opts, llm=not no_llm)
    except ValueError as exc:
        fail(str(exc))
    extras = []
    if result.summaries_written:
        extras.append(f"{result.summaries_written} source summaries written")
    if result.descriptions_written:
        extras.append(f"{result.descriptions_written} design-point descriptions written")
    okf_line = ("OKF v0.2 check: passed" if not result.okf_errors
                else f"[red]OKF v0.2 check: {len(result.okf_errors)} problem(s); run `ddspace wiki check`[/red]")
    console.print(Panel(
        f"Run {run_dir.name}: {result.pages} pages, {result.core} core dimension(s) (≥ {opts.core_min_sources} sources)"
        + (f"; {', '.join(extras)}" if extras else "") + f"\n{okf_line}\n\n"
        f"wiki/  Markdown for agents and Obsidian (start at wiki/index.md)\nsite/  HTML for people "
        f"(site/index.html, graph at site/graph.html)\nraw/   data for `ddspace query`\n\n"
        f"Log entry:\n{result.log}\n\nNext: [bold]ddspace wiki open[/bold], [bold]ddspace agent setup --claude[/bold]",
        title="Wiki built", expand=False))


@wiki_app.command("check")
def wiki_check(directory: Optional[Path] = typer.Option(None, "--dir", help="A wiki folder (default: this workspace's wiki/).")) -> None:
    """Check the wiki against the Open Knowledge Format v0.2 (exit code 1 on errors)."""
    wiki = directory or current_workspace().root / "wiki"
    errors, warnings = okf.check(wiki)
    for w in warnings[:20]:
        console.print(f"[yellow]warning[/yellow] {w}")
    if len(warnings) > 20:
        console.print(f"[yellow]... and {len(warnings) - 20} more warnings[/yellow]")
    for e in errors:
        console.print(f"[red]error[/red] {e}")
    pages = len(list(Path(wiki).rglob("*.md"))) if Path(wiki).is_dir() else 0
    if errors:
        fail(f"{len(errors)} error(s) in {pages} files: not OKF v0.2 conformant.")
    console.print(f"[green]✓[/green] {wiki}: {pages} files conform to OKF v0.2"
                  + (f" ({len(warnings)} broken-link warning(s))" if warnings else "") + ".")


@wiki_app.command("open")
def wiki_open(print_only: bool = typer.Option(False, "--print", help="Only print the path.")) -> None:
    """Open the HTML site in the browser."""
    page = current_workspace().root / wb.HTML_DIR / "index.html"
    if not page.is_file():
        fail("No site yet. Run `ddspace wiki build` first.")
    if print_only:
        typer.echo(str(page))
        return
    import webbrowser
    webbrowser.open(page.as_uri())
    console.print(f"Opened {page}")


# ---------------------------------------------------------------- reset


def _has_content(folder: Path) -> bool:
    """Return whether the folder holds anything to archive (a wiki with only its log.md counts as empty)."""
    if not folder.is_dir():
        return False
    names = {p.name for p in folder.iterdir()}
    return bool(names - {"log.md"} if folder.name == "wiki" else names)


def _free_archive(ws: Workspace) -> Path:
    """Return an archive folder path that is not taken, even for two resets in the same second."""
    base = runs.now_id()
    for n in range(100):
        path = ws.state_dir / "archive" / (base if n == 0 else f"{base}_{n}")
        if not path.exists():
            return path
    fail("Could not create an archive folder.")


@app.command()
def reset(
    wiki_only: bool = typer.Option(False, "--wiki-only", help="Only the wiki (wiki/, site/, raw/); keep the runs."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Do not ask for confirmation."),
) -> None:
    """Start over: move the runs and the wiki to [bold].ddspace/archive/[/bold]; sources and settings stay."""
    ws = current_workspace()
    targets = ["wiki", wb.HTML_DIR, "raw"] + ([] if wiki_only else ["runs"])
    present = [t for t in targets if _has_content(ws.root / t)]
    if not present:
        console.print("Nothing to reset: no runs or wiki yet.")
        return
    archive = _free_archive(ws)
    kept = ["sources/", "sources.csv", "corpus.json", "ddspace.yaml (with the wiki answers)", ".env",
            "AGENTS.md and agent files", "stored source summaries"] + (["runs/ (the current run stays current)"]
                                                                       if wiki_only else [])
    console.print(Panel(
        "Moves to " + runs.relative(ws, archive) + "/:\n  " + "\n  ".join(f"{t}/" for t in present)
        + "\nKeeps:\n  " + "\n  ".join(kept)
        + ("" if wiki_only else "\n\nThen: `ddspace mine` starts from scratch."), title="ddspace reset", expand=False))
    if interactive(yes) and not Confirm.ask("Reset?", default=False):
        raise typer.Exit()
    if not yes and not interactive(yes):
        fail("Not a terminal: pass --yes to confirm the reset.")
    archive.mkdir(parents=True)
    for t in present:
        shutil.move(str(ws.root / t), str(archive / t))
    if not wiki_only:
        ws.runs_dir.mkdir(exist_ok=True)
        ws.set("workspace.current_run", None)
    (ws.root / "wiki").mkdir(exist_ok=True)
    wb.append_log(ws.root / "wiki" / "log.md", f"- **Reset** The previous {'wiki' if wiki_only else 'runs and wiki'} "
                  f"moved to `{runs.relative(ws, archive)}/` (restore by moving the folders back).")
    console.print(f"[green]✓[/green] Archived {', '.join(present)} in {runs.relative(ws, archive)}/. "
                  + ("Next: `ddspace wiki build`." if wiki_only else "Next: `ddspace mine`."))


if __name__ == "__main__":  # pragma: no cover
    app()
