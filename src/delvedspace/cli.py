"""The ``ddspace`` command line (Typer, rendered with rich)."""

from __future__ import annotations

import json
import re
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, NoReturn, Optional

import typer
from rich.markup import escape

from delvedspace import __version__, agent, chat, importer, query_cli, runs, ui
from delvedspace import sources as src
from delvedspace import wiki_build as wb
from delvedspace import workspace as wsmod
from delvedspace.corpus import MAX_WORDS, MIN_WORDS, TARGET_WORDS
from delvedspace.workspace import CONFIG_NAME, Settings, Workspace, WorkspaceError
from taxonomy_generator.wiki import okf
from taxonomy_generator.wiki import query as q

app = typer.Typer(
    name="ddspace",
    help="DelveDSpace: mine a design space from your sources and publish it as a wiki.",
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode="rich",
)
console = ui.console
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
    """Print an error and exit (the message is plain text: brackets such as [chat] are kept)."""
    ui.error(message)
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
    ui.note("A few questions; press Enter to keep the value in brackets.")
    ui.section("Workspace")
    s.name = ui.ask_text("Name", default=s.name)
    s.use_case = ui.ask_text("Use case (what design space, for whom; one or two sentences)", default=s.use_case)
    ui.section("Models (provider/model; OpenAI by default)")
    s.generation_llm = ui.ask_text("Generation LLM, builds the design space", default=s.generation_llm)
    s.evaluation_llm = ui.ask_text("Evaluation LLM, judges it", default=s.evaluation_llm)
    while True:
        s.embedding = ui.ask_text("Embedding model, merges values and links evidence (openai/... or ollama/...)",
                                  default=s.embedding)
        problem = wsmod.embedding_problem(s.embedding)
        if not problem:
            break
        ui.warn(problem)
    ui.section("Sources and size")
    s.sources_dir = ui.ask_text("Sources folder (your downloaded .md .txt .html .pdf files)", default=s.sources_dir)
    ui.note(f"{sources_count(s.sources_dir)} source file(s) there now")
    while True:
        answer = ui.ask_text("Maximum number of dimensions (none = the LLM decides)",
                             default="none" if s.max_dimensions is None else str(s.max_dimensions))
        try:
            s.max_dimensions = _parse_max(answer)
            break
        except ValueError:
            ui.warn("Enter a number or 'none'.")
    s.batch_size = ui.ask_int("Minibatch size (passages per update step)", default=s.batch_size)
    s.critic = ui.ask_yes("Run the critic during mining? (scores each update; off is cheaper)", default=s.critic)
    return s


def _check_api_keys(ws: Workspace, s: Settings, ask: bool) -> None:
    needed = {k for k in (wsmod.provider_key(m) for m in (s.generation_llm, s.evaluation_llm, s.embedding)) if k}
    if needed:
        ui.section("API keys")
    for key in sorted(needed):
        found = ws.env_value(key)
        if found:
            ui.ok(f"{key} found ({ui.mask_secret(found)})")
            continue
        if ask and ui.ask_yes(f"{key} is not set. Write it to {ws.env_path.name} now?", default=True):
            value = ui.ask_secret(f"{key} (paste it; only the first 8 characters are shown)")
            if value:
                ws.write_env(key, value)
                ui.ok(f"{key} saved to .env ({ui.mask_secret(value)}; .env is ignored by git)")
                continue
        ui.warn(f"{key} is not set: add it to {ui.short_path(ws.env_path)} or your environment before ddspace mine")


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
    from_config: Optional[Path] = typer.Option(None, "--from-config", help="Take the use case, models, dimension "
                                               "cap and batch size from an existing pipeline config (YAML)."),
) -> None:
    """Create a workspace: folders, a commented [bold]ddspace.yaml[/bold] and a .gitignore."""
    root = directory.resolve()
    if (root / CONFIG_NAME).exists() and not force:
        fail(f"{root / CONFIG_NAME} already exists (use --force to overwrite it).")
    s = Settings(name=name or root.name, use_case=DEFAULT_USE_CASE)
    if from_config is not None:
        try:
            s = wsmod.settings_from_config(from_config, s)
        except WorkspaceError as exc:
            fail(str(exc))
    if use_case:
        s.use_case = use_case
    for attr, value in (("generation_llm", generation_llm), ("evaluation_llm", evaluation_llm),
                        ("embedding", embedding), ("sources_dir", sources_dir), ("batch_size", batch_size),
                        ("critic", critic)):
        if value is not None:
            setattr(s, attr, value)
    if max_dimensions is not None:
        s.max_dimensions = max_dimensions or None
    ask = interactive(yes)
    ui.header("init", f"Create a workspace in {ui.short_path(root)}")
    if ask:
        s = _ask_settings(s, lambda d: len(wsmod.source_files(root / d)))
    if wsmod.embedding_problem(s.embedding):
        fail(wsmod.embedding_problem(s.embedding))
    ws = wsmod.create(root, s)
    _check_api_keys(ws, s, ask)
    n = len(wsmod.source_files(ws.root / s.sources_dir))
    ui.summary("Workspace created", [
        ("Name", s.name), ("Folder", ui.short_path(ws.root)),
        ("Settings", f"{CONFIG_NAME} {ui.path('(every option commented; edit freely)')}"),
        ("Models", f"{s.generation_llm} (generation), {s.evaluation_llm} (evaluation), {s.embedding}"),
        ("Sources", f"{s.sources_dir}/ {ui.path(f'({n} file(s) there now)')}"),
    ], next_steps=[
        *([(f"cd {ui.short_path(ws.root)}", "go to the workspace")] if ws.root != Path.cwd().resolve() else []),
        (f"Copy your files into {s.sources_dir}/", ".md .txt .html .pdf (or: ddspace sources --from-json FILE)"),
        ("ddspace sources", "extract the text, draft sources.csv, flag problems, build the corpus"),
        ("ddspace mine", "generate the design space"),
    ])


# ---------------------------------------------------------------- sources and corpus


def _corpus_summary_rows(ws: Workspace, passages: List[dict]) -> List[tuple]:
    sizes = sorted(p["words"] for p in passages)
    return [("Corpus", f"{len(passages)} passages from {len({p['source_id'] for p in passages})} source(s) "
                       f"-> {ws.corpus_path.name}"),
            ("Passage size", f"{sum(sizes):,} words; min/median/max {sizes[0]}/{sizes[len(sizes) // 2]}/{sizes[-1]}")]


@app.command("sources")
def sources_cmd(
    from_json: Optional[Path] = typer.Option(None, "--from-json", help="Import a JSON corpus (a list of texts, or "
                                             "of objects with 'content', or {'documents': [...]}) as one source "
                                             "file per document, then scan."),
    no_corpus: bool = typer.Option(False, "--no-corpus", help="Only scan the sources; do not rebuild corpus.json "
                                   "(run `ddspace corpus` later, e.g. with other passage sizes)."),
) -> None:
    """Extract the text of every source file, update [bold]sources.csv[/bold], flag problems and build the corpus."""
    ws = current_workspace()
    ui.header("sources", f"Scan {ws.sources_dir.relative_to(ws.root)}/ and build the corpus")
    if from_json is not None:
        try:
            written = src.import_json(ws, from_json)
        except (OSError, ValueError) as exc:
            fail(f"Cannot import {from_json}: {exc}")
        ui.ok(f"Imported {len(written)} document(s) from {from_json.name}, one file each")
    if not ws.sources_dir.is_dir():
        fail(f"The sources folder {ws.sources_dir} does not exist.")
    with ui.status("Extracting text..."):
        found = src.scan(ws)
    if not found:
        fail(f"No source files in {ws.sources_dir} (supported: .md .txt .html .pdf).")
    ui.table(f"Sources ({len(found)})", ["id", "file", "format", "words", "title", "flags"],
             [[s.id, s.file, s.format, f"{s.words:,}", s.title, ", ".join(s.flags)] for s in found],
             styles=["red" if not src.usable(s) else ("yellow" if s.flags else "") for s in found], right=["words"])
    for flag in sorted({f for s in found for f in s.flags}):
        n = sum(flag in s.flags for s in found)
        ui.warn(f"{flag} ({n}): {src.FLAG_HELP.get(flag, '')}")
    usable = [s for s in found if src.usable(s)]
    rows = [("Usable", f"{len(usable)} of {len(found)} source(s)"),
            ("Edit", f"titles, URLs and types in {ws.sources_csv.name} {ui.path('(ids stay fixed)')}")]
    if no_corpus or not usable:
        ui.summary("Sources scanned", rows, next_steps=[("ddspace corpus", "split the sources into passages")]
                   if usable else [], style="green" if usable else "yellow")
        return
    passages = src.build_corpus(ws)
    ui.summary("Sources scanned, corpus built", rows + _corpus_summary_rows(ws, passages),
               next_steps=[("ddspace mine", "generate the design space")])


@app.command()
def corpus(
    target_words: int = typer.Option(TARGET_WORDS, help="Passage size to aim for."),
    min_words: int = typer.Option(MIN_WORDS, help="Shorter passages are merged into a neighbour."),
    max_words: int = typer.Option(MAX_WORDS, help="Hard cap before a passage is closed."),
) -> None:
    """Rebuild [bold]corpus.json[/bold] with other passage sizes (`ddspace sources` builds it with the defaults)."""
    ws = current_workspace()
    ui.header("corpus", "Split the sources into passages")
    try:
        passages = src.build_corpus(ws, target_words, min_words, max_words)
    except WorkspaceError as exc:
        fail(str(exc))
    if not passages:
        fail("No usable sources: check the flags shown by `ddspace sources`.")
    ui.summary("Corpus built", _corpus_summary_rows(ws, passages),
               next_steps=[("ddspace mine", "generate the design space")])


# ---------------------------------------------------------------- mine and update


def _format_duration(seconds: float) -> str:
    minutes = round(seconds / 60)
    if minutes < 1:
        return "under 1 min"
    return f"{minutes} min" if minutes < 90 else f"{minutes / 60:.1f} h"


def _format_tokens(tokens: int) -> str:
    return f"{tokens / 1e6:.1f}M" if tokens >= 1e6 else f"{max(1, round(tokens / 1e3))}k"


def _confirm_run(ws: Workspace, title: str, lines: List[tuple], passages: int, yes: bool) -> bool:
    cfg = ws.config()
    est = runs.estimate(ws, passages, int((cfg.get("pipeline") or {}).get("batch_size") or 10))
    models = cfg.get("models") or {}
    critic = (cfg.get("evaluation") or {}).get("enabled", True)
    ui.plan(title, list(lines) + [
        ("Passages", f"{passages} in about {est.batches} minibatch(es); critic {'on' if critic else 'off'}"),
        ("Models", f"{models.get('generation_llm')} (generation), {models.get('evaluation_llm')} (evaluation)"),
        ("Estimate", f"about {_format_tokens(est.tokens)} tokens, {_format_duration(est.seconds)} "
                     f"{ui.path(f'({est.basis})')}"),
    ])
    return not interactive(yes) or ui.ask_yes("Start?", default=True)


# Pipeline steps shown in the compact progress line (the pipeline prints these labels as it goes).
PIPELINE_STEPS = ("Loading corpus", "Generating summaries", "Creating minibatches", "Open coding minibatch",
                  "Generating initial taxonomy", "Updating taxonomy", "Checking saturation", "Reviewing taxonomy",
                  "Consolidating dimensions and values", "Selecting dimensions", "Labeling documents",
                  "Evaluating final taxonomy", "Evaluating taxonomy", "Aggregating new values", "Saving results")


def _run_compact(ws: Workspace, argv: List[str], log_path: Path, title: str) -> int:
    """Run the pipeline with one live status line (current step, elapsed time); the full output goes to the log."""
    started = time.monotonic()
    state = {"step": "Starting", "updates": 0}

    def show(status) -> None:
        elapsed = int(time.monotonic() - started)
        status.update(f"[{ui.ACCENT}]{title}[/{ui.ACCENT}]  {state['step']}  [dim]{elapsed // 60}:{elapsed % 60:02d}  "
                      f"log: {runs.relative(ws, log_path)}[/dim]")

    with ui.status(f"{title}  Starting") as status:
        def on_line(line: str) -> None:
            step = next((s for s in PIPELINE_STEPS if s.lower() in line.lower()), None)
            if step:
                state["step"] = step + (f" {state['updates'] + 1}" if step == "Updating taxonomy" else "")
                state["updates"] += step == "Updating taxonomy"
            show(status)
        return runs.run_pipeline(ws, argv, log_path=log_path, on_line=on_line)


def _execute(ws: Workspace, run: runs.Run, run_dir: Path, corpus: Path, extra: List[str],
             html_report: bool, verbose: bool = False) -> None:
    """Run the pipeline for ``run``, record the outcome and make a successful run current.

    The workspace corpus is read before the pipeline starts and saved in the run folder once the run succeeds,
    so the wiki and ``query evidence --quotes`` show the passages the design space was built from.
    """
    covered = ws.corpus_path.read_bytes() if ws.corpus_path.is_file() else None
    run.argv = ["--corpus", runs.relative(ws, corpus), "--config", wsmod.CONFIG_NAME,
                "--output", runs.relative(ws, run_dir), *extra]
    runs.save(run_dir, run)
    log_path = run_dir / runs.LOG_FILE
    try:
        code = (runs.run_pipeline(ws, run.argv) if verbose
                else _run_compact(ws, run.argv, log_path, f"Mining ({run.kind})"))
    except KeyboardInterrupt:
        code = 130
    taxonomy = runs.find_taxonomy(run_dir)
    run.finished_at = datetime.now().isoformat(timespec="seconds")
    run.status = "ok" if code == 0 and taxonomy else "failed"
    run.taxonomy = taxonomy.name if taxonomy else None
    runs.save(run_dir, run)
    if run.status != "ok":
        if not verbose and log_path.is_file():
            ui.summary(f"Last lines of {runs.relative(ws, log_path)}", text=escape(runs.log_tail(log_path)),
                       style="red")
        fail(f"The run failed (exit code {code}); its folder {runs.relative(ws, run_dir)} is kept for inspection. "
             "The current design space is unchanged.")
    if covered is not None:
        (run_dir / runs.RUN_CORPUS).write_bytes(covered)
    ws.set("workspace.current_run", runs.relative(ws, run_dir))
    if html_report or (ws.config().get("wiki") or {}).get("html_report"):
        report_argv = ["--html-report", runs.relative(ws, taxonomy), "--config", wsmod.CONFIG_NAME,
                       "--output", runs.relative(ws, run_dir)]
        if verbose:
            runs.run_pipeline(ws, report_argv)
        else:
            _run_compact(ws, report_argv, log_path, "HTML report")
    data = wsmod.read_json(taxonomy)
    dims = wb.selected_dims(data)
    metrics = data.get("run_metrics") or {}
    _warn_if_all_dropped(data)
    tokens = (f"{metrics.get('total_tokens', 0):,} tokens, {_format_duration(metrics.get('elapsed_seconds', 0))}"
              if metrics else "")
    ui.summary("Design space ready", [
        ("Run", f"{run.id} ({run.kind}), now the current design space"),
        ("Design space", f"{len(dims)} dimensions, {sum(len(d.get('values') or []) for d in dims)} values"),
        ("Cost", tokens),
        ("Files", f"{runs.relative(ws, run_dir)}/" + ("" if verbose else f" {ui.path(f'(full output: {runs.LOG_FILE})')}")),
    ], next_steps=[("ddspace wiki build", "publish it as a wiki")])


def _warn_if_all_dropped(taxonomy: dict) -> None:
    dropped = wb.dropped_count(taxonomy)
    if dropped and not wb.selected_dims(taxonomy):
        ui.warn(f"Dimension selection dropped all {dropped} dimension(s) (see synthesis/dropped in the wiki). "
                "With few sources, lower taxonomy.min_dimension_sources in ddspace.yaml and run "
                "ddspace mine --fresh, or add sources.")


def _corpus_or_fail(ws: Workspace) -> List[dict]:
    if not ws.corpus_path.is_file():
        fail("No corpus.json yet. Run `ddspace sources` first (it builds the corpus).")
    corpus = runs.read_corpus(ws.corpus_path)
    if not corpus:
        fail("corpus.json is empty. Check the flags shown by `ddspace sources`.")
    in_corpus = {p.get("source_id") for p in corpus}
    newer = [s.id for s in src.load_manifest(ws) if src.usable(s) and s.id not in in_corpus]
    if newer:
        ui.warn(f"Sources not in corpus.json yet: {', '.join(newer)}. Run ddspace sources to include them.")
    return corpus


@app.command()
def mine(
    fresh: bool = typer.Option(False, "--fresh", help="Mine from scratch even when a design space exists."),
    max_dimensions: Optional[int] = typer.Option(None, "--max-dimensions", help="Override taxonomy.max_num_clusters (0 = none)."),
    html_report: bool = typer.Option(False, "--html-report", help="Also write the pipeline's HTML report (about 7 MB)."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show the pipeline's full output (default: one progress line; the output goes to the run's pipeline.log)."),
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
    ui.header("mine", "Generate the design space from the corpus")
    corpus = _corpus_or_fail(ws)
    lines = [("Corpus", f"{len(corpus)} passages from {len({p.get('source_id') for p in corpus})} source(s)")]
    if not _confirm_run(ws, "About to mine", lines, len(corpus), yes):
        raise typer.Exit()
    run_dir = runs.new_run_dir(ws)
    run = runs.Run(id=run_dir.name, kind="mine", started_at=datetime.now().isoformat(timespec="seconds"),
                   source_ids=src.corpus_source_ids(corpus), passages=len(corpus))
    extra = ["-k", str(max_dimensions)] if max_dimensions is not None else []
    _execute(ws, run, run_dir, ws.corpus_path, extra, html_report, verbose)


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
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show the pipeline's full output (default: one progress line; the output goes to the run's pipeline.log)."),
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
        ui.header("update --feedback", "Re-mine the corpus, seeded with the current design space and your feedback")
        corpus = _corpus_or_fail(ws)
        lines = [("Starting from", f"run {seed_dir.name}"),
                 ("Feedback", f"[italic]{escape(text.strip()[:300])}{'...' if len(text.strip()) > 300 else ''}[/italic]")]
        if not _confirm_run(ws, "About to update", lines, len(corpus), yes):
            raise typer.Exit()
        run_dir = runs.new_run_dir(ws)
        run = runs.Run(id=run_dir.name, kind="update-feedback", started_at=started, seed_run=seed_dir.name,
                       feedback=text.strip(), passages=len(corpus), source_ids=src.corpus_source_ids(corpus))
        _execute(ws, run, run_dir, ws.corpus_path, ["--taxonomy", runs.relative(ws, seed), "--feedback", text.strip()],
                 html_report, verbose)
        return

    ui.header("update --test", "Add new sources; the dimensions stay as they are")
    if new_sources:
        _import_sources(ws, list(new_sources))
    with ui.status("Extracting text..."):
        scanned = src.scan(ws)
    covered = set(seed_run.source_ids) if seed_run and seed_run.source_ids else \
        set(src.corpus_source_ids(runs.read_corpus(ws.corpus_path))) if ws.corpus_path.is_file() else set()
    new_ids = [s.id for s in scanned if src.usable(s) and s.id not in covered]
    if not new_ids:
        fail("No new sources: every usable source is already in the design space. Add files with --sources, "
             "or put them in the sources folder.")
    added = [p for s in scanned if s.id in new_ids for p in src.source_passages(ws, s)]
    lines = [("Starting from", f"run {seed_dir.name} (dimensions frozen)"), ("New sources", ", ".join(new_ids))]
    if not _confirm_run(ws, "About to update", lines, len(added), yes):
        raise typer.Exit()
    src.append_to_corpus(ws, added)
    run_dir = runs.new_run_dir(ws)
    new_corpus = run_dir / "corpus_new.json"
    runs.write_corpus(new_corpus, added)
    run = runs.Run(id=run_dir.name, kind="update-test", started_at=started, seed_run=seed_dir.name,
                   source_ids=sorted(covered | set(new_ids)), new_source_ids=new_ids, passages=len(added))
    _execute(ws, run, run_dir, new_corpus, ["--taxonomy", runs.relative(ws, seed), "--mode", "test"], html_report, verbose)


# ---------------------------------------------------------------- import


@app.command("import")
def import_cmd(
    path: Path = typer.Argument(..., help="A run's taxonomy JSON, or a decision model (gt_model.json)."),
    kind: str = typer.Option("run", "--kind", help="run (a mined taxonomy) or decision-model (expert decisions and options)."),
    corpus: Optional[Path] = typer.Option(None, "--corpus", help="kind run: the corpus JSON, for quotes and design points."),
    sources: Optional[Path] = typer.Option(None, "--sources", help="kind run: sources.csv (id, title, url)."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Replace the current run without asking."),
) -> None:
    """Make a design space built elsewhere the current run: a mined [bold]run[/bold] or an expert [bold]decision-model[/bold]."""
    ws = current_workspace()
    if kind not in importer.KINDS:
        fail(f"--kind must be one of: {', '.join(importer.KINDS)}.")
    if kind == "decision-model" and (corpus or sources):
        fail("--corpus and --sources go with --kind run; a decision model has no passages.")
    try:
        current = runs.current_run_dir(ws)
    except WorkspaceError:
        current = None
    ui.header("import", f"Import {ui.short_path(path.resolve())} as a design space")
    if current is not None and not yes:
        if not interactive(yes):
            fail(f"A design space exists (run {current.name}). Use --yes to replace it as the current run.")
        if not ui.ask_yes(f"Replace the current run {current.name}? (it stays under runs/)", default=False):
            raise typer.Exit()
    try:
        run_dir = importer.import_space(ws, path, kind, corpus=corpus, sources=sources)
    except WorkspaceError as exc:
        fail(str(exc))
    dims = wb.selected_dims(wsmod.read_json(runs.find_taxonomy(run_dir)))
    if kind == "decision-model":
        evidence = "none (a decision model)"
    elif corpus:
        evidence = "quotes from the corpus"
    else:
        evidence = "passage ids, no quotes"
    ui.summary("Imported", [
        ("Run", f"{run_dir.name} ({importer.RUN_KINDS[kind]})"),
        ("Design space", f"{len(dims)} dimensions, {sum(len(d.get('values') or []) for d in dims)} values"),
        ("Evidence", evidence),
    ], next_steps=[("ddspace wiki build", "publish it"), ("ddspace agent setup", "let a coding agent use it")])


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
    ui.header("agent setup", "Let a coding agent use the wiki")
    install = agent.install_info()
    done = [f"{agent.upsert_block(target / 'AGENTS.md', agent.guide(ws, target, install))} AGENTS.md"]
    if claude:
        done.append(f"{agent.upsert_block(target / 'CLAUDE.md', agent.pointer_claude())} CLAUDE.md")
        if allow is None:
            allow = not interactive(yes) or ui.ask_yes(
                "Let Claude Code run ddspace query (read-only) without a permission prompt each time?", default=True)
        if allow:
            rules = agent.query_permissions(install)
            done.append(f"{agent.allow_query(target / '.claude' / 'settings.json', rules)} .claude/settings.json "
                        f"({', '.join(rules)})")
    if copilot:
        done.append(f"{agent.upsert_block(target / '.github' / 'copilot-instructions.md', agent.pointer_copilot())} "
                    ".github/copilot-instructions.md")
    if not (ws.root / "raw" / "graph.json").is_file():
        ui.warn("No wiki yet: run ddspace wiki build, then this command again for examples with real names.")
    for line in done:
        ui.ok(line)
    tools = " and ".join(t for t, on in (("Claude Code", claude), ("GitHub Copilot (agent mode)", copilot)) if on) \
        or "your coding agent"
    ui.summary("Agent setup done", [("Folder", ui.short_path(target)), ("Agents", tools)],
               text="Open the folder in the agent and ask, for example:\n  [italic]What are the alternatives for "
                    "<a decision>, and which sources support each? Cite passages.[/italic]")


# ---------------------------------------------------------------- wiki


def _wiki_options(ws: Workspace, dims: List[dict], n_sources: int, ask_all: bool, yes: bool) -> wb.Options:
    saved = ws.config().get("wiki") or {}
    ask = interactive(yes)
    opts = wb.Options()
    suggested = wb.suggest_core(n_sources)

    def need(key: str) -> bool:
        return saved.get(key) is None or ask_all

    if ask and any(need(k) for k in ("quotes", "source_summaries", "design_points", "core_min_sources")):
        ui.note("A few questions; the answers are saved in ddspace.yaml (wiki:) and reused. "
                "ddspace wiki build --ask asks again.")
    if need("quotes"):
        opts.quotes = ui.ask_yes("Quote the supporting passages on value pages? (copies source text: say no for a "
                                 "public wiki)", default=True) if ask else True
    else:
        opts.quotes = bool(saved["quotes"])
    if need("source_summaries"):
        todo = len(wb.missing_summaries(ws))
        opts.source_summaries = ui.ask_yes(
            f"Write a short summary per source? ({todo} LLM call(s) now; stored and reused)",
            default=True) if ask else False
    else:
        opts.source_summaries = bool(saved["source_summaries"])
    if need("design_points"):
        opts.design_points = ui.ask_text(
            "Design points, sampled combinations of values (describe = one LLM call per point)",
            choices=list(wb.DESIGN_POINT_CHOICES), default="sample") if ask else "sample"
    else:
        opts.design_points = str(saved["design_points"])
    if need("core_min_sources"):
        if ask:
            opts.core_min_sources = ui.ask_int(
                f"Core dimensions need evidence from at least N sources; N = {suggested} makes "
                f"{wb.core_count(dims, suggested)} of {len(dims)} dimensions core ({n_sources} sources). N",
                default=suggested)
        else:
            opts.core_min_sources = suggested
    else:
        try:
            opts.core_min_sources = int(saved["core_min_sources"])
        except (TypeError, ValueError):
            fail(f"wiki.core_min_sources in ddspace.yaml must be a number, not {saved['core_min_sources']!r}.")
    if ask_all and ask:
        while True:
            answer = ui.ask_text("Pages count as stale after (e.g. 90d, 12w, 6m; none)",
                                 default=saved.get("stale_after") or "none")
            opts.stale_after = None if answer.strip().lower() in ("", "none") else answer.strip()
            try:
                wb.parse_period(opts.stale_after)
                break
            except ValueError as exc:
                ui.warn(str(exc))
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
    ui.header("wiki build", f"Publish run {run_dir.name} as a wiki")
    _warn_if_all_dropped(taxonomy)
    n_sources = len(wb.run_sources(dims))
    opts = _wiki_options(ws, dims, n_sources, ask, yes)
    try:
        with ui.status("Building the wiki..."):
            result = wb.build_wiki(ws, run_dir, opts, llm=not no_llm)
    except ValueError as exc:
        fail(str(exc))
    failed = [(result.summaries_failed, "source summaries", result.summaries_written + result.summaries_failed),
              (result.descriptions_failed, "design-point descriptions",
               result.descriptions_written + result.descriptions_failed)]
    for n_failed, what, total in failed:
        if n_failed:
            ui.warn(f"{n_failed} of {total} {what} failed (first error: {escape(result.first_llm_error)}); "
                    "run ddspace wiki build again to retry.")
    extras = [f"{result.summaries_written} source summaries" if result.summaries_written else "",
              f"{result.descriptions_written} design-point descriptions" if result.descriptions_written else ""]
    check = ("[green]passed[/green]" if not result.okf_errors
             else f"[red]{len(result.okf_errors)} problem(s); run ddspace wiki check[/red]")
    ui.summary("Wiki built", [
        ("Run", run_dir.name),
        ("Pages", f"{result.pages}; {result.core} core dimension(s) (evidence from {opts.core_min_sources}+ sources)"),
        ("Written by the LLM", ", ".join(e for e in extras if e)),
        ("OKF v0.2 check", check),
        ("Chat index", result.chat),
        ("wiki/", f"Markdown for agents and Obsidian {ui.path('(start at wiki/index.md)')}"),
        ("site/", f"HTML for people {ui.path('(site/index.html; graph: site/graph.html)')}"),
        ("raw/", "data for ddspace query"),
        ("Change log", escape(re.sub(r"\*\*(\w+)\*\* ", r"\1: ", result.log.split(chr(10))[0].lstrip("- ")))),
    ], next_steps=[("ddspace wiki open", "browse it"), ("ddspace ask \"...\"", "ask it a question"),
                   ("ddspace agent setup --claude", "let a coding agent use it")])


@wiki_app.command("check")
def wiki_check(directory: Optional[Path] = typer.Option(None, "--dir", help="A wiki folder (default: this workspace's wiki/).")) -> None:
    """Check the wiki against the Open Knowledge Format v0.2 (exit code 1 on errors)."""
    wiki = directory or current_workspace().root / "wiki"
    ui.header("wiki check", "Check the wiki against the Open Knowledge Format v0.2")
    errors, warnings = okf.check(wiki)
    for w in warnings[:20]:
        ui.warn(escape(w))
    if len(warnings) > 20:
        ui.warn(f"... and {len(warnings) - 20} more broken links")
    for e in errors:
        console.print(f"  [red]✗[/red] {escape(e)}")
    pages = len(list(Path(wiki).rglob("*.md"))) if Path(wiki).is_dir() else 0
    if errors:
        fail(f"{len(errors)} error(s) in {pages} files: not OKF v0.2 conformant.")
    ui.ok(f"{pages} files in {ui.short_path(wiki)} conform to OKF v0.2"
          + (f" ({len(warnings)} broken-link warning(s))" if warnings else ""))


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
    ui.ok(f"Opened {ui.short_path(page)}")


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


# Derived from the sources (rebuilt by `ddspace sources`); removed by `reset --all`. Stored source summaries cost
# LLM calls to recreate.
SOURCE_DERIVED = ("corpus.json", ".ddspace/text", ".ddspace/sources.json", ".ddspace/source_summaries.json")


def _present(ws: Workspace, rel: str) -> bool:
    path = ws.root / rel
    return _has_content(path) if path.is_dir() else path.is_file()


@app.command()
def reset(
    wiki_only: bool = typer.Option(False, "--wiki-only", help="Only the wiki (wiki/, site/, raw/); keep the runs."),
    all_: bool = typer.Option(False, "--all", help="Also everything built from the sources: corpus.json, extracted "
                              "texts, stored source summaries. Your sources, sources.csv and settings stay."),
    purge: bool = typer.Option(False, "--purge", help="Delete everything in the workspace except ddspace.yaml and .env: "
                               "sources (your files too), sources.csv, corpus, runs, wiki and .ddspace/ (archives "
                               "included). Asks first; cannot be undone."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Do not ask for confirmation."),
) -> None:
    """Start over: move the runs and the wiki (with [bold]--all[/bold], also the corpus) to [bold].ddspace/archive/[/bold]."""
    ws = current_workspace()
    if wiki_only and (all_ or purge):
        fail("--wiki-only cannot be combined with --all or --purge.")
    if purge:
        _purge(ws, yes)
        return
    targets = ["wiki", wb.HTML_DIR, "raw"] + ([] if wiki_only else ["runs"]) + (list(SOURCE_DERIVED) if all_ else [])
    scope = "the wiki" if wiki_only else "runs, wiki and everything built from the sources" if all_ else "runs and wiki"
    ui.header("reset", f"Archive {scope}; your sources and settings stay")
    present = [t for t in targets if _present(ws, t)]
    if not present:
        ui.note("Nothing to reset.")
        return
    archive = _free_archive(ws)
    kept = ["sources/", "sources.csv", "ddspace.yaml", ".env", "AGENTS.md and agent files"]
    kept += [] if all_ else ["corpus.json", "stored source summaries"]
    kept += ["runs/ (the current run stays current)"] if wiki_only else []
    ui.plan("About to reset", [("Moves", ", ".join(f"{t}/" if (ws.root / t).is_dir() else t for t in present)),
                               ("To", f"{runs.relative(ws, archive)}/ {ui.path('(undo by moving them back)')}"),
                               ("Keeps", ", ".join(kept))])
    if interactive(yes) and not ui.ask_yes("Reset?", default=False):
        raise typer.Exit()
    if not yes and not interactive(yes):
        fail("Not a terminal: pass --yes to confirm the reset.")
    for t in present:
        (archive / t).parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(ws.root / t), str(archive / t))
    if not wiki_only:
        ws.runs_dir.mkdir(exist_ok=True)
        ws.set("workspace.current_run", None)
    chat.remove_index(ws)  # built from the old wiki; rebuilt by the next wiki build
    (ws.root / "wiki").mkdir(exist_ok=True)
    wb.append_log(ws.root / "wiki" / "log.md", f"- **Reset** The previous {scope}: moved to "
                  f"`{runs.relative(ws, archive)}/` (restore by moving them back).")
    ui.summary("Reset done", [("Archived", ", ".join(present)), ("Archive", f"{runs.relative(ws, archive)}/")],
               next_steps=[("ddspace wiki build", "rebuild the wiki")] if wiki_only
               else [("ddspace sources", "scan the sources and build the corpus again")] if all_
               else [("ddspace mine", "mine from scratch")])


# Kept by `reset --purge`: the settings, the API keys, and the .gitignore written by init.
PURGE_KEEPS = (CONFIG_NAME, ".env", ".gitignore")


def _purge(ws: Workspace, yes: bool) -> None:
    """Delete everything ddspace manages in the workspace except ddspace.yaml and .env (``reset --purge``)."""
    ui.header("reset --purge", "Delete everything in the workspace except ddspace.yaml and .env")
    sources_rel = ws.sources_dir.relative_to(ws.root).as_posix() if ws.sources_dir.is_relative_to(ws.root) else None
    managed = [t for t in (sources_rel, "sources.csv", "corpus.json", "runs", "wiki", wb.HTML_DIR, "raw",
                           wsmod.STATE_DIR) if t]
    present = [t for t in managed if (ws.root / t).exists()]
    agent_files = [t for t in ("AGENTS.md", "CLAUDE.md", ".github/copilot-instructions.md", ".claude/settings.json")
                   if (ws.root / t).is_file()]
    known = set(managed) | set(PURGE_KEEPS) | {".github", ".claude", "AGENTS.md", "CLAUDE.md"}
    others = sorted(p.name for p in ws.root.iterdir() if p.name not in known)
    if not present and not agent_files:
        ui.note("Nothing to delete.")
        return
    n_sources = len(wsmod.source_files(ws.sources_dir))
    ui.plan("About to delete for good", [
        ("[red]Deletes[/red]", ", ".join(f"{t}/" if (ws.root / t).is_dir() else t for t in present)
         + (f" {ui.path(f'(including {n_sources} source file(s))')}" if n_sources else "")),
        ("Cleans", ", ".join(agent_files) + f" {ui.path('(only what ddspace wrote)')}" if agent_files else ""),
        ("Keeps", ", ".join(t for t in PURGE_KEEPS if (ws.root / t).exists())),
        ("Leaves alone", ", ".join(others) + f" {ui.path('(not created by ddspace)')}" if others else ""),
    ])
    if interactive(yes) and not ui.ask_yes("Delete for good? This cannot be undone", default=False):
        raise typer.Exit()
    if not yes and not interactive(yes):
        fail("Not a terminal: pass --yes to confirm the purge.")
    for t in present:
        path = ws.root / t
        shutil.rmtree(path) if path.is_dir() else path.unlink()
    cleaned: List[str] = []
    for t in agent_files:
        action = agent.disallow_query(ws.root / t) if t.endswith(".json") else agent.remove_block(ws.root / t)
        if action:
            cleaned.append(f"{t} ({action})")
    for folder in (".github", ".claude"):
        path = ws.root / folder
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()
    ws.sources_dir.mkdir(parents=True, exist_ok=True)
    ws.runs_dir.mkdir(exist_ok=True)
    ws.set("workspace.current_run", None)
    ui.summary("Workspace purged", [("Deleted", ", ".join(present)), ("Cleaned", ", ".join(cleaned)),
                                    ("Kept", ", ".join(t for t in PURGE_KEEPS if (ws.root / t).exists()))],
               next_steps=[(f"Copy your files into {ws.sources_dir.relative_to(ws.root)}/", ".md .txt .html .pdf"),
                           ("ddspace sources", "scan them and build the corpus")])


# ---------------------------------------------------------------- check


CHECK_MARKS = {"done": "[green]✓[/green]", "stale": "[yellow]![/yellow]", "pending": "[dim]○[/dim]",
               "failed": "[red]✗[/red]", "unavailable": "[dim]–[/dim]"}


@app.command("check")
def check_cmd(as_json: bool = typer.Option(False, "--json", help="Print the report as JSON.")) -> None:
    """Show the configuration, what is missing, and how far each phase (sources to agent setup) has got."""
    from rich.table import Table

    from delvedspace import check as chk

    ws = current_workspace()
    report = chk.check(ws)
    if as_json:
        import json as _json

        typer.echo(_json.dumps(report.as_dict(), indent=2, ensure_ascii=False))
        return
    ui.header("check", f"Workspace {report.workspace} in {ui.short_path(ws.root)}")
    for title, items, numbered in (("Configuration", report.config, False), ("Pipeline", report.phases, True)):
        ui.section(title)
        grid = Table.grid(padding=(0, 2))
        grid.add_column(no_wrap=True)
        grid.add_column(no_wrap=True)
        grid.add_column(no_wrap=True)
        grid.add_column(overflow="fold")
        for i, item in enumerate(items, start=1):
            label = f"{i}. {item.name}" if numbered and item.name != "Last run" else item.name
            state = f"[dim]{item.state}[/dim]" if item.state == "done" else item.state
            detail = escape(item.detail)
            grid.add_row(f"  {CHECK_MARKS.get(item.state, '')}", label, state,
                         f"[dim]{detail}[/dim]" if item.state in ("pending", "unavailable") else detail)
        console.print(grid)
    steps = report.next_steps
    if not steps:
        ui.summary("All set", text="Every phase is up to date.",
                   next_steps=[("ddspace ask \"...\"", "ask the wiki a question"),
                               ("ddspace update --feedback \"...\"", "refine the design space")])
    else:
        ui.summary("What to do next", next_steps=[(i.next, f"{i.name} ({i.state})") for i in steps],
                   style="yellow" if any(i.state in ("stale", "failed") for i in steps) else ui.ACCENT)


# ---------------------------------------------------------------- ask


@app.command()
def ask(
    question: str = typer.Argument(..., help="Your question about the design space, in quotes."),
    as_json: bool = typer.Option(False, "--json", help="Print the answer, pages and cited passages as JSON."),
    show_context: bool = typer.Option(False, "--why", help="Also show why these wiki pages were picked."),
) -> None:
    """Answer one question from the wiki with the mining LLM (two LLM calls: pick pages, then answer)."""
    ws = current_workspace()
    if not as_json:
        ui.header("ask", escape(question))
    try:
        with ui.status("Reading the wiki...") if not as_json else _nullcontext():
            answer = chat.ask(ws, question)
    except (chat.ChatError, WorkspaceError) as exc:
        fail(str(exc))
    if as_json:
        typer.echo(chat.answer_json(answer))
        return
    from rich.markdown import Markdown
    from rich.panel import Panel

    console.print(Panel(Markdown(answer.answer), title="[bold]Answer[/bold]", title_align="left",
                        border_style=ui.ACCENT, expand=False, padding=(0, 1)))
    if answer.pages:
        ui.section("Wiki pages used")
        from rich.table import Table

        grid = Table.grid(padding=(0, 2))
        grid.add_column(no_wrap=True)
        grid.add_column(style="dim", overflow="fold")
        for page in answer.pages:
            grid.add_row(f"  {ui.BULLET} {escape(page['title'])}", escape(page["path"]))
        console.print(grid)
    if answer.cited_passages:
        ui.section("Passages cited")
        console.print(f"  {', '.join(answer.cited_passages)}  "
                      f"{ui.path('(ddspace query evidence <value> --quotes shows them)')}")
    if show_context and answer.reasoning:
        ui.section("Why these pages")
        ui.note(escape(answer.reasoning))
    console.print()
    ui.note(f"{answer.llm_calls} LLM calls, {_format_tokens(answer.tokens)} tokens; wiki of run {answer.run}")


# ---------------------------------------------------------------- point


@app.command()
def point(
    values: List[str] = typer.Argument(..., help="The values to combine, one per dimension: a value's id or label, "
                                       "or Dimension=Value when the label is not unique."),
    no_llm: bool = typer.Option(False, "--no-llm", help="Only the checks; no description is generated."),
    model: Optional[str] = typer.Option(None, "--model", help="Model for the description "
                                        "(default: the one that wrote the wiki's descriptions)."),
    graph: Optional[Path] = query_cli.GraphOpt,
    table: bool = query_cli.TableOpt,
) -> None:
    """Interpret a design point (one value per dimension). Returns the wiki's description when it has this point,
    else generates one with one LLM call. Nothing is stored; the design space and the wiki do not change."""
    from delvedspace import point as pt

    path = query_cli._graph_path(graph)
    try:
        if table:
            with ui.status("Describing the design point..." if not no_llm else "Checking the design point..."):
                data = pt.point(path, values, llm=not no_llm, model_override=model)
        else:
            data = pt.point(path, values, llm=not no_llm, model_override=model)
    except q.NotFound as exc:
        query_cli.err.print(f"[red]✗ Not found:[/red] {escape(str(exc))}")
        if not table:
            typer.echo(json.dumps({"error": str(exc), "candidates": exc.candidates}, indent=2, ensure_ascii=False))
        raise typer.Exit(2)
    except (q.QueryError, pt.PointError) as exc:
        fail(str(exc))
    if not table:
        typer.echo(json.dumps(data, indent=2, ensure_ascii=False))
        return
    ui.table("Design point", ["dimension", "value", "status"],
             [[escape(v["dimension"]), escape(v["label"]), v["status"]] for v in data["values"]])
    ex = data["existing"]
    ui.note(f"In the wiki as {ex['label']} ({ex['group']})" if ex else "Not one of the wiki's design points")
    ui.note("Attested by " + (", ".join(escape(str(s["label"])) for s in data["attested_by"]) if data["attested_by"]
                              else "no source: no source adopts every value (novel)"))
    for r in data["relations"]:
        ui.note(escape(r["reading"]))
    for w in data["warnings"]:
        ui.warn(escape(w))
    if data["description"]:
        from rich.panel import Panel

        title = "Description (stored)" if data["description_source"] == "stored" else "Description (generated)"
        console.print(Panel(escape(data["description"]), title=f"[bold]{title}[/bold]", title_align="left",
                            border_style=ui.ACCENT, expand=False, padding=(0, 1)))
        if data.get("note"):
            ui.note(data["note"])


class _nullcontext:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


if __name__ == "__main__":  # pragma: no cover
    app()
