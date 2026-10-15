"""``ddspace check``: the workspace's configuration, what is missing, and how far each phase has progressed.

Read-only and LLM-free. Each phase is ``done``, ``stale`` (done, but an earlier phase changed since), ``pending``
(not done yet), ``failed`` or ``unavailable``; the first phase that is not done names the command to run next.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from delvedspace import runs
from delvedspace import sources as src
from delvedspace.workspace import (
    CONFIG_NAME,
    Workspace,
    WorkspaceError,
    embedding_problem,
    provider_key,
    read_json,
    source_files,
)

DONE, STALE, PENDING, FAILED, UNAVAILABLE = "done", "stale", "pending", "failed", "unavailable"


@dataclass
class Item:
    """One configuration entry or one phase."""

    name: str
    state: str
    detail: str = ""
    next: str = ""          # the command that moves it forward


@dataclass
class Report:
    """What ``ddspace check`` shows."""

    workspace: str
    config: List[Item] = field(default_factory=list)
    phases: List[Item] = field(default_factory=list)

    @property
    def next_steps(self) -> List[Item]:
        """Return what to do next: the first configuration problem, then the first phase that is not done."""
        def first(items: List[Item]) -> Optional[Item]:
            return next((i for i in items if i.state in (PENDING, STALE, FAILED) and i.next), None)
        return [i for i in (first(self.config), first(self.phases)) if i]

    def as_dict(self) -> Dict[str, Any]:
        """Return the report as plain data (for ``--json``)."""
        return {"workspace": self.workspace, "config": [asdict(i) for i in self.config],
                "phases": [asdict(i) for i in self.phases], "next": [i.next for i in self.next_steps]}


def _sha(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _mask(value: str) -> str:
    return value[:8] + "•" * max(0, len(value) - 8)


def configuration(ws: Workspace) -> List[Item]:
    """Check ddspace.yaml: readable, use case, models and their API keys, size settings."""
    try:
        cfg = ws.config()
    except WorkspaceError as exc:
        return [Item(CONFIG_NAME, FAILED, str(exc), f"fix {CONFIG_NAME}")]
    from taxonomy_generator.settings import load_settings

    items = []
    try:
        load_settings(str(ws.config_path))
        items.append(Item("Settings", DONE, f"{CONFIG_NAME} loads"))
    except Exception as exc:  # noqa: BLE001 - any parse problem is reported, not raised
        items.append(Item("Settings", FAILED, f"{CONFIG_NAME} does not load: {exc}", f"fix {CONFIG_NAME}"))
    tx, models, pl = cfg.get("taxonomy") or {}, cfg.get("models") or {}, cfg.get("pipeline") or {}
    use_case = " ".join(str(tx.get("use_case") or "").split())
    items.append(Item("Use case", DONE if use_case else PENDING, use_case[:120] + ("..." if len(use_case) > 120 else ""),
                      "" if use_case else f"set taxonomy.use_case in {CONFIG_NAME}"))
    roles = [("Generation LLM", models.get("generation_llm")), ("Evaluation LLM", models.get("evaluation_llm")),
             ("Embedding model", models.get("embedding"))]
    for label, model in roles:
        if not model:
            items.append(Item(label, PENDING, "not set", f"set it under models: in {CONFIG_NAME}"))
            continue
        problem = embedding_problem(str(model)) if label == "Embedding model" else None
        items.append(Item(label, FAILED if problem else DONE, problem or str(model),
                          f"fix models.embedding in {CONFIG_NAME}" if problem else ""))
    for key in sorted({k for k in (provider_key(str(m)) for _, m in roles if m) if k}):
        value = ws.env_value(key)
        items.append(Item(key, DONE if value else PENDING, _mask(value) if value else "not set",
                          "" if value else f"export {key}=... (or add it to .env)"))
    cap = tx.get("max_num_clusters")
    critic = (cfg.get("evaluation") or {}).get("enabled", True)
    items.append(Item("Size", DONE, (f"at most {cap} dimensions" if cap else "no cap on dimensions")
                      + f"; minibatches of {pl.get('batch_size', '?')} passages; critic {'on' if critic else 'off'}"))
    return items


def phases(ws: Workspace) -> List[Item]:
    """Check each phase: sources, corpus, mining, wiki, chat index, agent setup."""
    out: List[Item] = []

    # 1. sources
    files = source_files(ws.sources_dir)
    manifest = {s.file: s for s in src.load_manifest(ws)}
    if not files and not manifest and ws.corpus_path.is_file():
        out.append(Item("Sources", DONE, "no source files; corpus.json given directly"))
    elif not files and not manifest:
        out.append(Item("Sources", PENDING, f"no files in {ws.sources_dir.relative_to(ws.root)}/",
                        "copy files into the sources folder, then: ddspace sources"))
    else:
        rel = {p.relative_to(ws.sources_dir).as_posix(): p for p in files}
        new = [f for f in rel if f not in manifest]
        changed = [f for f, p in rel.items() if f in manifest and manifest[f].sha256 and manifest[f].sha256 != _sha(p)]
        usable = [s for s in manifest.values() if src.usable(s)]
        flagged = sorted({fl for s in manifest.values() for fl in s.flags})
        detail = f"{len(rel)} file(s); {len(usable)} usable" + (f"; flags: {', '.join(flagged)}" if flagged else "")
        if not manifest:
            out.append(Item("Sources", PENDING, f"{len(rel)} file(s), not scanned yet", "ddspace sources"))
        elif new or changed:
            extra = (f"{len(new)} new" if new else "") + (", " if new and changed else "") + \
                    (f"{len(changed)} changed" if changed else "")
            out.append(Item("Sources", STALE, f"{detail}; {extra} since the last scan", "ddspace sources"))
        else:
            out.append(Item("Sources", DONE, detail))

    # 2. corpus
    corpus = read_json(ws.corpus_path)
    usable_ids = {s.id for s in manifest.values() if src.usable(s)}
    if not corpus:
        out.append(Item("Corpus", PENDING, "no corpus.json", "ddspace sources"))
    else:
        in_corpus = set(src.corpus_source_ids(corpus))
        missing = sorted(usable_ids - in_corpus)
        detail = f"{len(corpus)} passages from {len(in_corpus)} source(s)"
        stale = missing or (ws.manifest_path.is_file() and
                            ws.manifest_path.stat().st_mtime > ws.corpus_path.stat().st_mtime + 1)
        out.append(Item("Corpus", STALE if stale else DONE,
                        detail + (f"; not yet in it: {', '.join(missing)}" if missing else
                                  "; sources were rescanned after it was built" if stale else ""),
                        "ddspace sources" if stale else ""))

    # 3. mining
    try:
        current = runs.current_run_dir(ws)
    except WorkspaceError as exc:
        current = None
        out.append(Item("Design space (mine)", FAILED, str(exc), "ddspace mine --fresh"))
    all_runs = [r for r in (runs.load(d) for d in sorted(ws.runs_dir.glob("*")) if d.is_dir()) if r]
    if not any(i.name == "Design space (mine)" for i in out):
        if current is None:
            out.append(Item("Design space (mine)", PENDING, "no run yet", "ddspace mine"))
        else:
            run = runs.load(current)
            taxonomy = runs.find_taxonomy(current)
            data = read_json(taxonomy, {}) if taxonomy else {}
            dims = data.get("selected_clusters") if "selected_clusters" in data else \
                ((data.get("iterations") or [{}])[-1].get("clusters") or [])
            detail = (f"run {current.name}{f' ({run.kind})' if run else ''}: {len(dims or [])} dimensions, "
                      f"{sum(len(d.get('values') or []) for d in dims or [])} values")
            corpus_newer = run and corpus and (set(src.corpus_source_ids(corpus)) - set(run.source_ids or []))
            if corpus_newer:
                out.append(Item("Design space (mine)", STALE, detail + f"; sources not in it yet: "
                                f"{', '.join(sorted(corpus_newer))}", "ddspace update --test"))
            else:
                out.append(Item("Design space (mine)", DONE, detail))
        later_failed = [r for r in all_runs if r.status != "ok" and (current is None or r.id > current.name)]
        if later_failed:
            last = later_failed[-1]
            out.append(Item("Last run", FAILED if last.status == "failed" else PENDING,
                            f"run {last.id} ({last.kind}) {last.status}; see runs/{last.id}/{runs.LOG_FILE}"))

    # 4. wiki
    built = read_json(ws.root / "raw" / "run.json", {})
    wiki_run = built.get("run")
    if not (ws.root / "wiki" / "index.md").is_file() or not wiki_run:
        out.append(Item("Wiki", PENDING, "not built", "ddspace wiki build" if current else ""))
    elif current is not None and wiki_run != current.name:
        out.append(Item("Wiki", STALE, f"built from run {wiki_run}; the current run is {current.name}",
                        "ddspace wiki build"))
    else:
        out.append(Item("Wiki", DONE, f"built from run {wiki_run}; wiki/, site/, raw/"))

    # 5. chat index
    from delvedspace import chat

    meta = read_json(ws.state_dir / chat.NODES_FILE, {})
    if not chat.treedex_available():
        out.append(Item("Chat index (ask)", UNAVAILABLE, 'TreeDex is not installed: pip install "delvedspace[chat]"'))
    elif not meta:
        out.append(Item("Chat index (ask)", PENDING, "not built", "ddspace wiki build" if wiki_run else ""))
    elif meta.get("run") != wiki_run:
        out.append(Item("Chat index (ask)", STALE, f"built for run {meta.get('run')}", "ddspace wiki build"))
    else:
        out.append(Item("Chat index (ask)", DONE, f"{meta.get('nodes')} nodes, run {meta.get('run')}"))

    # 6. agent setup
    from delvedspace import agent

    guide = ws.root / "AGENTS.md"
    text = guide.read_text(encoding="utf-8") if guide.is_file() else ""
    if agent.START not in text:
        out.append(Item("Agent setup", PENDING, "no AGENTS.md (optional: for coding agents)",
                        "ddspace agent setup" if wiki_run else ""))
    elif wiki_run and f"(run {wiki_run})" not in text:
        out.append(Item("Agent setup", STALE, "AGENTS.md was written for an older wiki", "ddspace agent setup"))
    else:
        files = [n for n in ("AGENTS.md", "CLAUDE.md", ".github/copilot-instructions.md") if (ws.root / n).is_file()]
        out.append(Item("Agent setup", DONE, ", ".join(files)))
    return out


def check(ws: Workspace) -> Report:
    """Return the whole report for a workspace."""
    name = str(((ws.config().get("taxonomy") or {}).get("name")) or ws.root.name) if ws.config_path.is_file() else ""
    return Report(workspace=name, config=configuration(ws), phases=phases(ws))
