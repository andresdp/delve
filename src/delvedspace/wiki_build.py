"""``ddspace wiki build``: export the current run as a wiki, with optional LLM extras and a change log.

Writes an OKF bundle (``wiki/``), an HTML site (``site/``) and query data (``raw/``); the optional extras are
source summaries and design-point descriptions.
"""

from __future__ import annotations

import asyncio
import datetime as dt
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

from delvedspace import __version__, runs
from delvedspace import sources as src
from delvedspace.workspace import Workspace
from taxonomy_generator.evaluation.design_points import point_signature, sample_points
from taxonomy_generator.html_report import (
    _extract_narrative_summary,
    resolve_report_path,
)
from taxonomy_generator.wiki import Inputs, build, llm_texts, okf, write
from taxonomy_generator.wiki.model import load_corpus, load_sources, source_of

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
    if "selected_clusters" in taxonomy:
        return list(taxonomy.get("selected_clusters") or [])
    return list((taxonomy.get("iterations") or [{}])[-1].get("clusters") or [])


def dropped_count(taxonomy: Mapping[str, Any]) -> int:
    """Return how many dimensions of the final iteration the selection dropped."""
    final = (taxonomy.get("iterations") or [{}])[-1].get("clusters") or []
    return max(0, len(final) - len(selected_dims(taxonomy)))


def run_sources(dims: List[Mapping[str, Any]]) -> List[str]:
    """Return the sources whose passages support some value of the design space."""
    return sorted({source_of(str(doc)) for d in dims for v in d.get("values") or []
                   for doc in v.get("supporting_doc_ids") or []})


def suggest_core(dims: List[Mapping[str, Any]], n_sources: int) -> int:
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


def missing_summaries(ws: Workspace) -> List[str]:
    """Source ids without a stored summary for their current file."""
    stored = _load(ws.state_dir / SUMMARIES_FILE).get("summaries") or {}
    return [sid for sid, (_t, _x, sha) in _source_texts(ws).items()
            if (stored.get(sid) or {}).get("sha256") != sha or not (stored.get(sid) or {}).get("summary")]


def _load(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def _run_async(coro):
    return asyncio.run(coro)


def ensure_summaries(ws: Workspace, model_name: str, concurrency: int = 4) -> Tuple[Dict[str, str], str, int]:
    """Summarize the sources that have no stored summary; return (summaries, model, newly written)."""
    from taxonomy_generator.utils import load_chat_model

    path = ws.state_dir / SUMMARIES_FILE
    data = _load(path)
    stored = dict(data.get("summaries") or {})
    texts = _source_texts(ws)
    todo = missing_summaries(ws)
    if todo:
        model = load_chat_model(model_name)
        sem = asyncio.Semaphore(concurrency)

        async def one(sid):
            title, text, sha = texts[sid]
            async with sem:
                summary, n = await llm_texts.summarize(model, title, text)
            return sid, {"title": title, "summary": summary, "words_read": n, "sha256": sha}

        async def all_():
            return await asyncio.gather(*(one(sid) for sid in todo), return_exceptions=True)

        for result in _run_async(all_()):
            if not isinstance(result, BaseException):
                stored[result[0]] = result[1]
        ws.state_dir.mkdir(exist_ok=True)
        path.write_text(json.dumps({"model": model_name, "generated": dt.date.today().isoformat(),
                                    "prompt_version": llm_texts.SUMMARY_PROMPT_VERSION, "summaries": stored},
                                   indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    summaries = {sid: e["summary"] for sid, e in stored.items() if sid in texts and e.get("summary")}
    return summaries, str(data.get("model") or model_name), len(todo)


def ensure_points(run_dir: Path, dims: List[Dict[str, Any]], corpus_ids: List[str]) -> Dict[str, Any]:
    """Sample design points once per run (stored in the run folder) and return them.

    Each source acts as a "system": attested points are combinations one source describes, novel points
    combine values no single source does. The evaluation-only control group is left out.
    """
    path = run_dir / POINTS_FILE
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    doc_sources = {doc: {source_of(doc)} for doc in corpus_ids}
    samples = sample_points(dims, doc_sources, list(POINT_SIZES), POINTS_PER_GROUP, POINT_SEED)
    for sample in samples:
        sample["groups"]["control"] = []
    data = {"run": run_dir.name, "attest_by": "source", "seed": POINT_SEED, "n": POINTS_PER_GROUP,
            "samples": samples}
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return data


def all_points(points: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Every sampled point, across sizes and groups."""
    return [p for s in points.get("samples") or [] for g in (s.get("groups") or {}).values() for p in g]


def missing_descriptions(run_dir: Path, points: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Points without a stored description."""
    stored = _load(run_dir / DESCRIPTIONS_FILE).get("descriptions") or {}
    return [p for p in all_points(points) if point_signature(p) not in stored]


def ensure_descriptions(run_dir: Path, points: Mapping[str, Any], dims: List[Dict[str, Any]], domain: str,
                        model_name: str, concurrency: int = 6) -> Tuple[Dict[str, str], str, int]:
    """Describe the points that have no stored description; return (descriptions, model, newly written)."""
    from taxonomy_generator.utils import load_chat_model

    path = run_dir / DESCRIPTIONS_FILE
    data = _load(path)
    stored = dict(data.get("descriptions") or {})
    todo = missing_descriptions(run_dir, points)
    if todo:
        model = load_chat_model(model_name)
        sem = asyncio.Semaphore(concurrency)
        by_id = {str(d.get("id")): d for d in dims}

        async def one(p):
            async with sem:
                return p, await llm_texts.describe(model, p, by_id, domain)

        async def all_():
            return await asyncio.gather(*(one(p) for p in todo), return_exceptions=True)

        for result in _run_async(all_()):
            if not isinstance(result, BaseException) and result[1]:
                stored[point_signature(result[0])] = {"point_id": result[0].get("point_id"), "description": result[1]}
        path.write_text(json.dumps({"model": model_name, "generated": dt.date.today().isoformat(),
                                    "prompt_version": llm_texts.DESCRIPTION_PROMPT_VERSION, "design_points": POINTS_FILE,
                                    "descriptions": dict(sorted(stored.items()))}, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    return ({k: v["description"] for k, v in stored.items() if v.get("description")},
            str(data.get("model") or model_name), len(todo))


# ---------------------------------------------------------------- change log


def _names(graph: Mapping[str, Any]) -> Tuple[Dict[str, Dict[str, Any]], Dict[Tuple[str, str], Dict[str, Any]]]:
    norm = lambda t: " ".join(str(t or "").split()).casefold()  # noqa: E731
    dims = {norm(n["label"]): n for n in graph.get("nodes") or [] if n.get("kind") == "dimension"}
    vals = {(norm(n.get("dimension")), norm(n["label"])): n for n in graph.get("nodes") or [] if n.get("kind") == "value"}
    return dims, vals


def diff(old: Optional[Mapping[str, Any]], new: Mapping[str, Any]) -> Dict[str, List[str]]:
    """Compare two graphs by dimension name and (dimension, value label): added, removed, changed."""
    if not old:
        return {}
    od, ov = _names(old)
    nd, nv = _names(new)
    label = lambda n: f"{n['label']} ({n.get('dimension')})"  # noqa: E731
    changed = [f"{label(nv[k])}: {ov[k].get('status')} → {nv[k].get('status')}"
               for k in sorted(set(ov) & set(nv)) if ov[k].get("status") != nv[k].get("status")]
    return {
        "dimensions added": [nd[k]["label"] for k in sorted(set(nd) - set(od))],
        "dimensions removed": [od[k]["label"] for k in sorted(set(od) - set(nd))],
        "values added": [label(nv[k]) for k in sorted(set(nv) - set(ov))],
        "values removed": [label(ov[k]) for k in sorted(set(ov) - set(nv))],
        "values changed": changed,
        "_matched": [str(len(set(od) & set(nd))), str(len(od))],
    }


def log_entry(run: Optional[runs.Run], run_dir: Path, changes: Dict[str, List[str]], new: Mapping[str, Any],
              same_run: bool) -> str:
    """One log entry (Markdown list item, with sub-items for the changes)."""
    counts = f"{sum(n.get('kind') == 'dimension' for n in new['nodes'])} dimensions, " \
             f"{sum(n.get('kind') == 'value' for n in new['nodes'])} values"
    kind = run.kind if run else "run"
    if not changes:
        return f"- **Creation** Wiki built from run {run_dir.name} ({kind}): {counts}."
    if same_run:
        return f"- **Rebuild** Wiki rebuilt from the same run {run_dir.name} (export options only)."
    matched, total = changes.pop("_matched")
    head = f"- **Update** Run {run_dir.name} ({kind}" + (f", from {run.seed_run}" if run and run.seed_run else "") + \
        f"): {counts}."
    if run and run.kind == "update-feedback":
        head += f" Dimensions matched by name: {matched} of {total}."
    if run and run.new_source_ids:
        head += f" New sources: {', '.join(run.new_source_ids)}."
    lines = [head]
    for what, items in changes.items():
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
    okf_errors: Optional[List[str]] = None


def build_wiki(ws: Workspace, run_dir: Path, opts: Options, *, llm: bool = True) -> Result:
    """Export ``run_dir`` into the workspace (``wiki/``, ``site/``, ``raw/``) and log what changed.

    With ``llm=False`` stored summaries and descriptions are used but none are written.
    """
    taxonomy_path = runs.find_taxonomy(run_dir)
    taxonomy = json.loads(taxonomy_path.read_text(encoding="utf-8"))
    cfg = ws.config()
    models = {k: str(v) for k, v in (cfg.get("models") or {}).items()
              if k in ("generation_llm", "evaluation_llm", "embedding") and v}
    tx, pl = cfg.get("taxonomy") or {}, cfg.get("pipeline") or {}
    use_case = " ".join(str(tx.get("use_case") or "").split())
    name = str(tx.get("name") or taxonomy.get("taxonomy_name") or ws.root.name)
    dims = selected_dims(taxonomy)
    corpus = load_corpus(ws.corpus_path) if ws.corpus_path.is_file() else {}
    run = runs.load(run_dir)

    summaries, summary_model, n_summaries = {}, "", 0
    if opts.source_summaries:
        if llm:
            summaries, summary_model, n_summaries = ensure_summaries(ws, models.get("generation_llm", ""))
        else:
            stored = _load(ws.state_dir / SUMMARIES_FILE)
            summaries = {k: v["summary"] for k, v in (stored.get("summaries") or {}).items() if v.get("summary")}
            summary_model = str(stored.get("model") or "")
    points, descriptions, point_model, n_desc = None, {}, "", 0
    if opts.design_points in ("sample", "describe"):
        points = ensure_points(run_dir, dims, list(corpus))
        if opts.design_points == "describe" and llm:
            descriptions, point_model, n_desc = ensure_descriptions(run_dir, points, dims, name,
                                                                    models.get("generation_llm", ""))
        elif opts.design_points == "describe":
            stored = _load(run_dir / DESCRIPTIONS_FILE)
            descriptions = {k: v["description"] for k, v in (stored.get("descriptions") or {}).items()}
            point_model = str(stored.get("model") or "")

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
    old = json.loads(graph_path.read_text(encoding="utf-8")) if graph_path.is_file() else None
    old_run = _load(ws.root / "raw" / "run.json").get("run")
    period = parse_period(opts.stale_after)
    stale = (dt.datetime.now().astimezone() + period).isoformat(timespec="seconds") if period else None
    write(export, ws.root, name, html_dir=HTML_DIR, okf_by=producer(), okf_stale_after=stale)
    entry = log_entry(run, run_dir, diff(old, export.graph), export.graph, same_run=old_run == run_dir.name)
    append_log(ws.root / "wiki" / "log.md", entry)
    errors, _warnings = okf.check(ws.root / "wiki")
    return Result(pages=len(export.pages), nodes=len(export.graph["nodes"]), edges=len(export.graph["edges"]),
                  core=core_count(dims, opts.core_min_sources), log=entry, summaries_written=n_summaries,
                  descriptions_written=n_desc, okf_errors=errors)

