"""``ddspace wiki build``: export the current run as a wiki, with optional LLM extras and a change log.

Writes an OKF bundle (``wiki/``), an HTML site (``site/``) and query data (``raw/``); the optional extras are
source summaries and design-point descriptions.
"""

from __future__ import annotations

import asyncio
import datetime as dt
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

from delvedspace import __version__, runs
from delvedspace import sources as src
from delvedspace.workspace import Workspace, read_json, write_json
from taxonomy_generator.evaluation.design_points import point_signature, sample_points
from taxonomy_generator.html_report import (
    _extract_narrative_summary,
    resolve_report_path,
)
from taxonomy_generator.wiki import Inputs, build, llm_texts, okf, write
from taxonomy_generator.wiki.model import (
    load_corpus,
    load_sources,
    source_of,
    view_dimensions,
)

DESIGN_POINT_CHOICES = ("none", "sample", "describe")
POINTS_PER_GROUP, POINT_SIZES, POINT_SEED = 10, (2, 3), 42
SUMMARIES_FILE = "source_summaries.json"       # in .ddspace/ (kept by `ddspace reset`: LLM calls)
POINTS_FILE = "design_points.json"            # in the run folder
DESCRIPTIONS_FILE = "design_points_descriptions.json"
HTML_DIR = "site"


@dataclass
class Options:
    """The ``wiki:`` answers in ddspace.yaml."""

    quotes: bool = True
    source_summaries: bool = False
    design_points: str = "sample"
    core_min_sources: int = 2
    stale_after: Optional[str] = None


def producer() -> str:
    """Return the OKF ``generated.by`` actor."""
    return f"delvedspace/{__version__}"


def selected_dims(taxonomy: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Return the run's reported design space (selected view; the final iteration when there is none)."""
    return view_dimensions(taxonomy, "selected")


def dropped_count(taxonomy: Mapping[str, Any]) -> int:
    """Return how many dimensions of the final iteration the selection dropped."""
    final = (taxonomy.get("iterations") or [{}])[-1].get("clusters") or []
    return max(0, len(final) - len(selected_dims(taxonomy)))


def run_sources(dims: List[Mapping[str, Any]]) -> List[str]:
    """Return the sources whose passages support some value of the design space."""
    return sorted({source_of(str(doc)) for d in dims for v in d.get("values") or []
                   for doc in v.get("supporting_doc_ids") or []})


def suggest_core(n_sources: int) -> int:
    """Suggested core threshold: about a third of the sources (at least 2, at most the sources there are)."""
    return max(1, min(n_sources, max(2, round(n_sources / 3))))


def core_count(dims: List[Mapping[str, Any]], k: int) -> int:
    """How many dimensions have evidence from at least ``k`` sources."""
    return sum(int((d.get("evidence") or {}).get("sources") or 0) >= k for d in dims)


def parse_period(text: Optional[str]) -> Optional[dt.timedelta]:
    """Parse a refresh period such as ``90d``, ``12w`` or ``6m`` (months as 30 days)."""
    if not text:
        return None
    m = re.fullmatch(r"\s*(\d+)\s*([dwm])\s*", str(text).lower())
    if not m:
        raise ValueError(f"refresh period {text!r}: use a number and d, w or m (e.g. 90d)")
    days = int(m.group(1)) * {"d": 1, "w": 7, "m": 30}[m.group(2)]
    return dt.timedelta(days=days)


# ---------------------------------------------------------------- LLM extras (stored, reused)


def _source_texts(ws: Workspace) -> Dict[str, Tuple[str, str, str]]:
    """Source id → (title, text, sha256) for the usable scanned sources."""
    out = {}
    for s in src.load_manifest(ws):
        text_file = ws.text_dir / f"{s.id}.md"
        if src.usable(s) and text_file.is_file():
            out[s.id] = (s.title, text_file.read_text(encoding="utf-8"), s.sha256)
    return out


def _stored(path: Path, key: str) -> Tuple[Dict[str, Any], str]:
    """Return the stored entries under ``key`` and the model that wrote them."""
    data = read_json(path, {})
    return dict(data.get(key) or {}), str(data.get("model") or "")


def missing_summaries(ws: Workspace, texts: Optional[Mapping[str, Tuple[str, str, str]]] = None) -> List[str]:
    """Return the source ids without a stored summary for their current file."""
    stored, _model = _stored(ws.state_dir / SUMMARIES_FILE, "summaries")
    texts = _source_texts(ws) if texts is None else texts
    return [sid for sid, (_t, _x, sha) in texts.items()
            if (stored.get(sid) or {}).get("sha256") != sha or not (stored.get(sid) or {}).get("summary")]


def stored_summaries(ws: Workspace) -> Tuple[Dict[str, str], str]:
    """Return the stored source summaries and the model that wrote them (no LLM call)."""
    stored, model = _stored(ws.state_dir / SUMMARIES_FILE, "summaries")
    return {sid: e["summary"] for sid, e in stored.items() if e.get("summary")}, model


def stored_descriptions(run_dir: Path) -> Tuple[Dict[str, str], str]:
    """Return the stored design-point descriptions and the model that wrote them (no LLM call)."""
    stored, model = _stored(run_dir / DESCRIPTIONS_FILE, "descriptions")
    return {sig: e["description"] for sig, e in stored.items() if e.get("description")}, model


def _gather(calls: List[Any], concurrency: int) -> List[Any]:
    """Run coroutine factories with bounded concurrency; failed calls come back as exceptions."""
    async def run_all():
        sem = asyncio.Semaphore(concurrency)

        async def bounded(call):
            async with sem:
                return await call()
        return await asyncio.gather(*(bounded(c) for c in calls), return_exceptions=True)
    return asyncio.run(run_all())


@dataclass
class LlmOutcome:
    """How many LLM texts were stored in a call, how many failed, and the first error message."""

    written: int = 0
    failed: int = 0
    first_error: str = ""

    def record(self, error: BaseException) -> None:
        """Count one failed call."""
        self.failed += 1
        self.first_error = self.first_error or f"{type(error).__name__}: {error}"


def ensure_summaries(ws: Workspace, model_name: str,
                     concurrency: int = 4) -> Tuple[Dict[str, str], str, LlmOutcome]:
    """Summarize the sources that have no stored summary; return (summaries, model, outcome).

    A failed call is counted, not stored: that source is still missing, so the next build retries it.
    """
    from taxonomy_generator.utils import load_chat_model

    path = ws.state_dir / SUMMARIES_FILE
    stored, stored_model = _stored(path, "summaries")
    texts = _source_texts(ws)
    todo = missing_summaries(ws, texts)
    outcome = LlmOutcome()
    if todo:
        model = load_chat_model(model_name)

        def call(sid):
            async def one():
                title, text, sha = texts[sid]
                summary, n = await llm_texts.summarize(model, title, text)
                return sid, {"title": title, "summary": summary, "words_read": n, "sha256": sha}
            return one

        for result in _gather([call(sid) for sid in todo], concurrency):
            if isinstance(result, BaseException):
                outcome.record(result)
            else:
                stored[result[0]] = result[1]
                outcome.written += 1
        ws.state_dir.mkdir(exist_ok=True)
        write_json(path, {"model": model_name, "generated": dt.date.today().isoformat(),
                          "prompt_version": llm_texts.SUMMARY_PROMPT_VERSION, "summaries": stored})
    summaries = {sid: e["summary"] for sid, e in stored.items() if sid in texts and e.get("summary")}
    return summaries, stored_model or model_name, outcome


def ensure_points(run_dir: Path, dims: List[Dict[str, Any]], corpus_ids: List[str]) -> Dict[str, Any]:
    """Sample design points once per run (stored in the run folder) and return them.

    Each source acts as a "system": attested points are combinations one source describes, novel points
    combine values no single source does. The evaluation-only control group is left out.
    """
    path = run_dir / POINTS_FILE
    if path.is_file():
        return read_json(path)
    doc_sources = {doc: {source_of(doc)} for doc in corpus_ids}
    samples = sample_points(dims, doc_sources, list(POINT_SIZES), POINTS_PER_GROUP, POINT_SEED)
    for sample in samples:
        sample["groups"]["control"] = []
    data = {"run": run_dir.name, "attest_by": "source", "seed": POINT_SEED, "n": POINTS_PER_GROUP,
            "samples": samples}
    write_json(path, data)
    return data


def all_points(points: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Every sampled point, across sizes and groups."""
    return [p for s in points.get("samples") or [] for g in (s.get("groups") or {}).values() for p in g]


def missing_descriptions(run_dir: Path, points: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Return one point per value combination that has no stored description.

    Descriptions are keyed by the combination, so a combination sampled in two groups is described once.
    """
    stored, _model = _stored(run_dir / DESCRIPTIONS_FILE, "descriptions")
    first: Dict[str, Dict[str, Any]] = {}
    for p in all_points(points):
        first.setdefault(point_signature(p), p)
    return [p for sig, p in first.items() if sig not in stored]


def ensure_descriptions(run_dir: Path, points: Mapping[str, Any], dims: List[Dict[str, Any]], domain: str,
                        model_name: str, concurrency: int = 6) -> Tuple[Dict[str, str], str, LlmOutcome]:
    """Describe the points that have no stored description; return (descriptions, model, outcome).

    A failed or empty call is not stored: that combination is still missing, so the next build retries it.
    """
    from taxonomy_generator.utils import load_chat_model

    path = run_dir / DESCRIPTIONS_FILE
    stored, stored_model = _stored(path, "descriptions")
    todo = missing_descriptions(run_dir, points)
    outcome = LlmOutcome()
    if todo:
        model = load_chat_model(model_name)
        by_id = {str(d.get("id")): d for d in dims}

        def call(p):
            async def one():
                return p, await llm_texts.describe(model, p, by_id, domain)
            return one

        for result in _gather([call(p) for p in todo], concurrency):
            if isinstance(result, BaseException):
                outcome.record(result)
            elif result[1]:
                stored[point_signature(result[0])] = {"point_id": result[0].get("point_id"), "description": result[1]}
                outcome.written += 1
            else:
                outcome.record(ValueError("empty description"))
        write_json(path, {"model": model_name, "generated": dt.date.today().isoformat(),
                          "prompt_version": llm_texts.DESCRIPTION_PROMPT_VERSION, "design_points": POINTS_FILE,
                          "descriptions": dict(sorted(stored.items()))})
    return ({k: v["description"] for k, v in stored.items() if v.get("description")},
            stored_model or model_name, outcome)


# ---------------------------------------------------------------- change log


def _names(graph: Mapping[str, Any]) -> Tuple[Dict[str, Dict[str, Any]], Dict[Tuple[str, str], Dict[str, Any]]]:
    norm = lambda t: " ".join(str(t or "").split()).casefold()  # noqa: E731
    dims = {norm(n["label"]): n for n in graph.get("nodes") or [] if n.get("kind") == "dimension"}
    vals = {(norm(n.get("dimension")), norm(n["label"])): n for n in graph.get("nodes") or [] if n.get("kind") == "value"}
    return dims, vals


@dataclass
class Changes:
    """What changed between two builds: lists of labels per kind of change, and the dimensions matched by name."""

    items: Dict[str, List[str]]
    matched: int
    total: int


def diff(old: Optional[Mapping[str, Any]], new: Mapping[str, Any]) -> Optional[Changes]:
    """Compare two graphs by dimension name and (dimension, value label): added, removed, changed."""
    if not old:
        return None
    od, ov = _names(old)
    nd, nv = _names(new)
    label = lambda n: f"{n['label']} ({n.get('dimension')})"  # noqa: E731
    changed = [f"{label(nv[k])}: {ov[k].get('status')} → {nv[k].get('status')}"
               for k in sorted(set(ov) & set(nv)) if ov[k].get("status") != nv[k].get("status")]
    return Changes(items={
        "dimensions added": [nd[k]["label"] for k in sorted(set(nd) - set(od))],
        "dimensions removed": [od[k]["label"] for k in sorted(set(od) - set(nd))],
        "values added": [label(nv[k]) for k in sorted(set(nv) - set(ov))],
        "values removed": [label(ov[k]) for k in sorted(set(ov) - set(nv))],
        "values changed": changed,
    }, matched=len(set(od) & set(nd)), total=len(od))


def log_entry(run: Optional[runs.Run], run_dir: Path, changes: Optional[Changes], new: Mapping[str, Any],
              same_run: bool) -> str:
    """Return one log entry (a Markdown list item, with sub-items for the changes)."""
    counts = f"{sum(n.get('kind') == 'dimension' for n in new['nodes'])} dimensions, " \
             f"{sum(n.get('kind') == 'value' for n in new['nodes'])} values"
    kind = run.kind if run else "run"
    if changes is None:
        return f"- **Creation** Wiki built from run {run_dir.name} ({kind}): {counts}."
    if same_run:
        return f"- **Rebuild** Wiki rebuilt from the same run {run_dir.name} (export options only)."
    head = f"- **Update** Run {run_dir.name} ({kind}" + (f", from {run.seed_run}" if run and run.seed_run else "") + \
        f"): {counts}."
    if run and run.kind == "update-feedback":
        head += f" Dimensions matched by name: {changes.matched} of {changes.total}."
    if run and run.new_source_ids:
        head += f" New sources: {', '.join(run.new_source_ids)}."
    lines = [head]
    for what, items in changes.items.items():
        if items:
            shown = "; ".join(items[:15]) + (f"; and {len(items) - 15} more" if len(items) > 15 else "")
            lines.append(f"  - {what.capitalize()} ({len(items)}): {shown}")
    if len(lines) == 1:
        lines.append("  - No dimension or value changed.")
    return "\n".join(lines)


def append_log(path: Path, entry: str, day: Optional[str] = None) -> None:
    """Add ``entry`` under today's date heading, newest first (OKF §9)."""
    day = day or dt.date.today().isoformat()
    text = path.read_text(encoding="utf-8") if path.is_file() else "# Log\n"
    heading = f"## {day}"
    if heading in text:
        text = text.replace(heading + "\n\n", f"{heading}\n\n{entry}\n", 1)
    else:
        m = re.search(r"(?m)^## \d{4}-\d{2}-\d{2}", text)
        block = f"{heading}\n\n{entry}\n\n"
        text = text[:m.start()] + block + text[m.start():] if m else text.rstrip("\n") + "\n\n" + block
    path.write_text(text.rstrip("\n") + "\n", encoding="utf-8")


# ---------------------------------------------------------------- build


@dataclass
class Result:
    """What a build did."""

    pages: int
    nodes: int
    edges: int
    core: int
    log: str
    summaries_written: int = 0
    descriptions_written: int = 0
    summaries_failed: int = 0
    descriptions_failed: int = 0
    first_llm_error: str = ""
    okf_errors: Optional[List[str]] = None
    chat: str = ""                      # what happened to the chat index (built, or why not)


def build_wiki(ws: Workspace, run_dir: Path, opts: Options, *, llm: bool = True) -> Result:
    """Export ``run_dir`` into the workspace (``wiki/``, ``site/``, ``raw/``) and log what changed.

    With ``llm=False`` stored summaries and descriptions are used but none are written.
    """
    taxonomy_path = runs.find_taxonomy(run_dir)
    taxonomy = read_json(taxonomy_path)
    cfg = ws.config()
    models = {k: str(v) for k, v in (cfg.get("models") or {}).items()
              if k in ("generation_llm", "evaluation_llm", "embedding") and v}
    tx, pl = cfg.get("taxonomy") or {}, cfg.get("pipeline") or {}
    use_case = " ".join(str(tx.get("use_case") or "").split())
    name = str(tx.get("name") or taxonomy.get("taxonomy_name") or ws.root.name)
    dims = selected_dims(taxonomy)
    corpus_file = runs.run_corpus_path(ws, run_dir)
    corpus = load_corpus(corpus_file) if corpus_file.is_file() else {}
    run = runs.load(run_dir)

    summaries, summary_model, sum_out = {}, "", LlmOutcome()
    if opts.source_summaries:
        if llm:
            summaries, summary_model, sum_out = ensure_summaries(ws, models.get("generation_llm", ""))
        else:
            summaries, summary_model = stored_summaries(ws)
    points, descriptions, point_model, desc_out = None, {}, "", LlmOutcome()
    if opts.design_points in ("sample", "describe"):
        points = ensure_points(run_dir, dims, list(corpus))
        if opts.design_points == "describe" and llm:
            descriptions, point_model, desc_out = ensure_descriptions(run_dir, points, dims, name,
                                                                      models.get("generation_llm", ""))
        elif opts.design_points == "describe":
            descriptions, point_model = stored_descriptions(run_dir)

    m = re.search(r"_taxonomy_(\d{8}_\d{6})", taxonomy_path.name)
    run_label = m.group(1) if m else run_dir.name
    report = resolve_report_path(run_dir, taxonomy.get("taxonomy_name") or name, run_label)
    narrative = ""
    if report and report.path and Path(report.path).is_file():
        narrative = _extract_narrative_summary(Path(report.path).read_text(encoding="utf-8")) or ""
    settings = {"batch_size": pl.get("batch_size"), "edit_mode": tx.get("edit_mode"),
                "min_dimension_sources": tx.get("min_dimension_sources"),
                "min_candidate_decisions": tx.get("min_candidate_decisions"),
                "relevance_selection": tx.get("relevance_selection"),
                "open_coding_input": (cfg.get("open_coding") or {}).get("input")}
    inp = Inputs(taxonomy=taxonomy, taxonomy_name=name, run_label=run_label, corpus=corpus,
                 sources=load_sources(ws.sources_csv) if ws.sources_csv.is_file() else {},
                 design_points=points, use_case=use_case, narrative=narrative, models=models,
                 source_summaries=summaries, summary_model=summary_model,
                 point_descriptions=descriptions, point_model=point_model, settings=settings,
                 core_min_sources=opts.core_min_sources, quotes=opts.quotes)
    export = build(inp)
    export.manifest = {"producer": producer(), "run": run_dir.name, "taxonomy": runs.relative(ws, taxonomy_path),
                       "view": "selected", "quotes": opts.quotes, "source_summaries": opts.source_summaries,
                       "design_points": opts.design_points, "core_min_sources": opts.core_min_sources,
                       "stale_after": opts.stale_after, "models": models}

    graph_path = ws.root / "raw" / "graph.json"
    old = read_json(graph_path)
    old_run = read_json(ws.root / "raw" / "run.json", {}).get("run")
    period = parse_period(opts.stale_after)
    stale = (dt.datetime.now().astimezone() + period).isoformat(timespec="seconds") if period else None
    write(export, ws.root, name, html_dir=HTML_DIR, okf_by=producer(), okf_stale_after=stale)
    entry = log_entry(run, run_dir, diff(old, export.graph), export.graph, same_run=old_run == run_dir.name)
    append_log(ws.root / "wiki" / "log.md", entry)
    errors, _warnings = okf.check(ws.root / "wiki")
    chat_note = _rebuild_chat_index(ws)
    return Result(pages=len(export.pages), nodes=len(export.graph["nodes"]), edges=len(export.graph["edges"]),
                  core=core_count(dims, opts.core_min_sources), log=entry, summaries_written=sum_out.written,
                  descriptions_written=desc_out.written, summaries_failed=sum_out.failed,
                  descriptions_failed=desc_out.failed, first_llm_error=sum_out.first_error or desc_out.first_error,
                  okf_errors=errors, chat=chat_note)


def _rebuild_chat_index(ws: Workspace) -> str:
    """Re-create the chat index for ``ddspace ask`` from the new wiki; return a one-line note."""
    from delvedspace import chat

    if not chat.treedex_available():
        chat.remove_index(ws)  # an index of an older wiki would answer from stale pages
        return "skipped: TreeDex is not installed, so ddspace ask is unavailable"
    info = chat.build_index(ws)
    return f"rebuilt for ddspace ask ({info['nodes']} nodes)"
