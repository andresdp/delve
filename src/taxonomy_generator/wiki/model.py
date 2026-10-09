"""Design-space wiki: the pages and graph data of one run (docs/DESIGN_SPACE_EXPLORATION.md §13).

Everything here is rendered from run data by templates, with no LLM call (R1),
and the same inputs always give the same pages (R10). Pages follow the
llmwiki-cli layout, which Obsidian also reads:

- ``concepts/``: dimensions (decision points);
- ``entities/``: dimension values (candidate decisions and outcomes);
- ``sources/``: corpus sources;
- ``synthesis/``: generated overviews (and, with a passage → system map, one page
  per system plus the system × dimension matrix);
- ``designs/``: sampled design points, only when given.

Page bodies are markdown with ``[[path|label]]`` wikilinks between pages.
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

STATUS_ORDER = ("accepted", "mixed", "rejected", "outcome")
CANDIDATE_STATUSES = ("accepted", "mixed", "rejected")
GROUP_ORDER = ("attested", "novel", "control")
SYNTHESIS_ORDER = ("synthesis/overview", "synthesis/contested", "synthesis/dropped", "synthesis/system-matrix",
                   "synthesis/design-points", "synthesis/evaluation")
MODEL_LABELS = (("generation_llm", "Generation LLM"), ("evaluation_llm", "Evaluation LLM (judge)"),
                ("embedding", "Embedding model"))
PASSAGE_ID = re.compile(r"^s(\d+)_p\d+$")


@dataclass
class Page:
    """One wiki page: ``path`` is shelf/slug (``index`` for the root page)."""

    path: str
    title: str
    frontmatter: Dict[str, Any]
    body: str
    kind: str


@dataclass
class Inputs:
    """Everything one export reads; only ``taxonomy`` is required."""

    taxonomy: Dict[str, Any]
    taxonomy_name: str
    run_label: str
    corpus: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    sources: Dict[str, Dict[str, str]] = field(default_factory=dict)
    systems: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    system_names: Dict[str, Dict[str, str]] = field(default_factory=dict)
    design_points: Optional[Dict[str, Any]] = None
    use_case: str = ""
    narrative: str = ""
    evaluation: bool = False
    models: Dict[str, str] = field(default_factory=dict)
    case_icon: bool = False
    source_summaries: Dict[str, str] = field(default_factory=dict)
    summary_model: str = ""
    point_descriptions: Dict[str, str] = field(default_factory=dict)
    point_model: str = ""
    settings: Dict[str, Any] = field(default_factory=dict)
    core_min_sources: int = 2
    core_min_systems: int = 2
    view: str = "selected"
    quotes: bool = True
    quote_words: int = 60


@dataclass
class Export:
    pages: List[Page]
    graph: Dict[str, Any]
    manifest: Dict[str, Any]
    tree: Dict[str, Any] = field(default_factory=dict)


# ── helpers ──────────────────────────────────────────────────────────────

def slugify(text: str, fallback: str = "page") -> str:
    """ASCII, lowercase, hyphenated slug."""
    norm = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", norm.lower()).strip("-")
    return slug[:80].strip("-") or fallback


def link(path: str, label: str) -> str:
    """A wikilink with a readable label (brackets and pipes removed from the label)."""
    clean = re.sub(r"[\[\]|]", " ", str(label)).strip()
    return f"[[{path}|{clean}]]"


def cell(text: Any) -> str:
    """Text safe inside a markdown table cell (wikilinks keep their pipe)."""
    out = str(text).replace("\n", " ")
    parts = re.split(r"(\[\[[^\]]*\]\])", out)
    return "".join(p if p.startswith("[[") else p.replace("|", "\\|") for p in parts)


def items(entries: Sequence[str]) -> str:
    """Several entries in one table cell: a bulleted list (HTML pages turn it into <ul>)."""
    entries = [e for e in entries if e]
    return "<br>".join(f"• {e}" for e in entries)


def source_of(doc_id: str) -> str:
    """Source id of a passage (``s03_p02`` → ``s3``); other documents are their own source."""
    m = PASSAGE_ID.match(str(doc_id))
    return f"s{int(m.group(1))}" if m else str(doc_id)


MD_SPECIAL = re.compile(r"([\\`*_{}\[\]<>#|])")


def excerpt(text: str, words: int) -> str:
    """The first ``words`` words of a passage as plain text (heading lines skipped, markdown escaped)."""
    lines = [l for l in str(text).splitlines() if not l.lstrip().startswith("#")]
    tokens = " ".join(lines).split()
    out = " ".join(tokens[:words]) + (" …" if len(tokens) > words else "")
    return MD_SPECIAL.sub(r"\\\1", out)


def load_corpus(path: Path) -> Dict[str, Dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {str(d["id"]): d for d in data if isinstance(d, dict) and "id" in d}


def load_sources(path: Path) -> Dict[str, Dict[str, str]]:
    with open(path, encoding="utf-8", newline="") as f:
        return {r["id"].strip(): r for r in csv.DictReader(f)}


def load_system_map(path: Path) -> Dict[str, Dict[str, Any]]:
    """Passage id → {"systems": [...], "primary": code} from a B7-style CSV (``#`` lines skipped)."""
    with open(path, encoding="utf-8", newline="") as f:
        lines = [line for line in f if not line.lstrip().startswith("#")]
    out = {}
    for row in csv.DictReader(lines):
        systems = [s.strip() for s in (row.get("systems") or "").split(";") if s.strip()]
        out[row["passage_id"].strip()] = {"systems": systems, "primary": (row.get("primary") or "").strip()}
    return out


def load_source_summaries(path: Path) -> Tuple[Dict[str, str], str]:
    """Source id → summary, and the model that wrote them (benchmark/summarize_sources.py output)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    summaries = {sid: (entry or {}).get("summary", "") for sid, entry in (data.get("summaries") or {}).items()}
    return {k: v for k, v in summaries.items() if v}, str(data.get("model") or "")


def load_point_descriptions(path: Path) -> Tuple[Dict[str, str], str]:
    """Design-point signature → description, and the model that wrote them (describe_design_points.py output)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    out = {sig: (entry or {}).get("description", "") for sig, entry in (data.get("descriptions") or {}).items()}
    return {k: v for k, v in out.items() if v}, str(data.get("model") or "")


def point_signature(point: Mapping[str, Any]) -> str:
    """Same key as taxonomy_generator.evaluation.design_points.point_signature."""
    return "|".join(sorted(f"{s.get('dimension_id')}={s.get('value_id')}" for s in point.get("values") or []))


def first_sentence(text: str) -> str:
    m = re.search(r"(.+?[.!?])(\s|$)", text.strip())
    return m.group(1) if m else text.strip()


def load_system_names(path: Path) -> Dict[str, Dict[str, str]]:
    with open(path, encoding="utf-8", newline="") as f:
        return {r["code"].strip(): r for r in csv.DictReader(f)}


# ── building ─────────────────────────────────────────────────────────────

class _Builder:
    def __init__(self, inp: Inputs):
        self.inp = inp
        tax = inp.taxonomy
        if inp.view == "final":
            self.dims = list((tax.get("iterations") or [{}])[-1].get("clusters") or [])
        else:
            self.dims = list(tax.get("selected_clusters") or [])
        self.dims = [d for d in self.dims if isinstance(d, dict)]
        self.dim_by_id = {str(d.get("id")): d for d in self.dims}
        self.pages: List[Page] = []
        self.nodes: List[Dict[str, Any]] = []
        self.edges: List[Dict[str, Any]] = []
        self._assign_paths()

    # paths ---------------------------------------------------------------
    def _assign_paths(self) -> None:
        used: Set[str] = set()

        def unique(base: str) -> str:
            path, n = base, 2
            while path in used:
                path, n = f"{base}-{n}", n + 1
            used.add(path)
            return path

        self.dim_path = {}
        for d in sorted(self.dims, key=lambda d: (d.get("name", ""), str(d.get("id")))):
            self.dim_path[str(d.get("id"))] = unique("concepts/" + slugify(d.get("name"), f"dimension-{d.get('id')}"))
        self.value_path = {}
        for d in self.dims:
            for v in d.get("values") or []:
                self.value_path[str(v.get("id"))] = None
        for d in sorted(self.dims, key=lambda d: (d.get("name", ""), str(d.get("id")))):
            for v in sorted(d.get("values") or [], key=lambda v: (v.get("label", ""), str(v.get("id")))):
                self.value_path[str(v.get("id"))] = unique("entities/" + slugify(v.get("label"), f"value-{v.get('id')}"))
        docs = sorted({str(doc) for d in self.dims for v in d.get("values") or []
                       for doc in v.get("supporting_doc_ids") or []})
        self.source_ids = sorted({source_of(doc) for doc in docs}, key=_natural)
        self.source_path = {s: "sources/" + slugify(s, "source") for s in self.source_ids}
        self.system_codes = sorted({p for doc in docs for p in [self.primary_system(doc)] if p})
        self.system_path = {s: "synthesis/systems/" + slugify(s, "system") for s in self.system_codes}

    # core dimensions -------------------------------------------------------
    def dim_systems(self, d: Mapping[str, Any]) -> List[str]:
        """Systems whose passages support a candidate value of this dimension (primary system)."""
        return sorted({s for v in d.get("values") or [] if v.get("status") in CANDIDATE_STATUSES
                       for doc in v.get("supporting_doc_ids") or [] for s in [self.primary_system(doc)] if s})

    def is_core(self, d: Mapping[str, Any]) -> bool:
        """Core dimension: evidence from enough sources, or (with a system map) supported by enough systems."""
        sources = int((d.get("evidence") or {}).get("sources") or 0)
        if sources >= self.inp.core_min_sources:
            return True
        return bool(self.inp.systems) and len(self.dim_systems(d)) >= self.inp.core_min_systems

    def core_rule(self) -> str:
        rule = f"evidence from ≥ {self.inp.core_min_sources} sources"
        if self.inp.systems:
            rule += f", or supported by ≥ {self.inp.core_min_systems} systems"
        return rule

    def core_rule_short(self) -> str:
        rule = f"≥ {self.inp.core_min_sources} sources"
        if self.inp.systems:
            rule += f" or ≥ {self.inp.core_min_systems} systems"
        return rule

    # lookups -------------------------------------------------------------
    def source_title(self, sid: str) -> str:
        row = self.inp.sources.get(sid)
        if row and row.get("title"):
            return row["title"]
        doc = self.inp.corpus.get(sid) or next(
            (p for p in self.inp.corpus.values() if source_of(str(p.get("id"))) == sid), None)
        return (doc or {}).get("title") or sid

    def system_title(self, code: str) -> str:
        return (self.inp.system_names.get(code) or {}).get("name") or code

    def primary_system(self, doc: str) -> Optional[str]:
        p = (self.inp.systems.get(str(doc)) or {}).get("primary")
        return p if p and p != "GENERAL" else None

    def value_systems(self, v: Mapping[str, Any]) -> List[str]:
        return sorted({s for doc in v.get("supporting_doc_ids") or [] for s in [self.primary_system(doc)] if s})

    def stance(self, v: Mapping[str, Any], doc: str) -> str:
        st = v.get("stances") or {}
        acc, rej = doc in (st.get("accepted") or []), doc in (st.get("rejected") or [])
        if acc and rej:
            return "both"
        if rej:
            return "rejects"
        if acc:
            return "accepts"
        return "rejects" if v.get("status") == "rejected" else "supports"

    def design_points(self) -> List[Dict[str, Any]]:
        dp = self.inp.design_points
        if not dp:
            return []
        points = []
        for sample in dp.get("samples") or []:
            for g in GROUP_ORDER:
                for p in (sample.get("groups") or {}).get(g) or []:
                    if p.get("point_id"):
                        points.append({**p, "k": sample.get("k", len(p.get("values") or []))})
        return sorted(points, key=lambda p: p["point_id"])

    # pages ---------------------------------------------------------------
    def add(self, path: str, title: str, kind: str, frontmatter: Dict[str, Any], body: str) -> None:
        fm = {"title": title, "type": kind, **frontmatter}
        self.pages.append(Page(path=path, title=title, frontmatter=fm, body=body.rstrip() + "\n", kind=kind))

    def build(self) -> Export:
        points = self.design_points()
        self.points_by_value: Dict[str, List[str]] = defaultdict(list)
        for p in points:
            for s in p.get("values") or []:
                self.points_by_value[str(s.get("value_id"))].append(p["point_id"])
        self.point_path = {p["point_id"]: "designs/" + slugify(p["point_id"]) for p in points}

        for d in self.dims:
            self.dimension_page(d)
            for v in d.get("values") or []:
                self.value_page(d, v)
        for sid in self.source_ids:
            self.source_page(sid)
        self.overview_page()
        self.has_evaluation = self.inp.evaluation and self.evaluation_page()
        self.contested_page()
        self.dropped_page()
        if self.system_codes:
            for code in self.system_codes:
                self.system_page(code, points)
            self.matrix_page()
        if points:
            self.design_points_page(points)
            for p in points:
                self.point_page(p)
        self.approach_page()
        self.index_page(bool(points))
        self.graph_data(points)
        self.pages.sort(key=lambda p: (p.path != "index", p.path))
        return Export(pages=self.pages, graph={"nodes": self.nodes, "edges": self.edges,
                                               "core_rule": self.core_rule_short()}, manifest={},
                      tree={**self.tree_data(), "core_rule": self.core_rule_short()})

    def dimension_page(self, d: Mapping[str, Any]) -> None:
        did = str(d.get("id"))
        values = d.get("values") or []
        counts = {s: sum(v.get("status") == s for v in values) for s in STATUS_ORDER}
        ev = d.get("evidence") or {}
        rel_out = [(r, str(r.get("target_id"))) for r in d.get("relations") or [] if str(r.get("target_id")) in self.dim_by_id]
        rel_in = [(o, r) for o in self.dims for r in o.get("relations") or [] if str(r.get("target_id")) == did]
        fm = {"id": did, "core": self.is_core(d), "values": len(values),
              "candidate_values": sum(counts[s] for s in CANDIDATE_STATUSES), "outcomes": counts["outcome"],
              "evidence": {"codes": ev.get("codes"), "documents": ev.get("documents"), "sources": ev.get("sources")},
              "relations": [f"{r.get('type')} {link(self.dim_path[t], self.dim_by_id[t].get('name'))}" for r, t in rel_out],
              "tags": ["dimension"] + (["core"] if self.is_core(d) else [])}
        if self.inp.systems:
            fm["systems"] = [link(self.system_path[s], self.system_title(s)) for s in self.dim_systems(d)]
        lines = [f"# {d.get('name')}", "", d.get("description") or "", ""]
        lines += ["## Values", "", "| Value | Status | Passages |", "|---|---|---|"]
        for v in sorted(values, key=lambda v: (STATUS_ORDER.index(v.get("status")) if v.get("status") in STATUS_ORDER else 9, v.get("label", ""))):
            lines.append(f"| {cell(link(self.value_path[str(v.get('id'))], v.get('label')))} | {v.get('status')} "
                         f"| {len(v.get('supporting_doc_ids') or [])} |")
        if rel_out or rel_in:
            lines += ["", "## Relations", ""]
            for r, t in rel_out:
                lines.append(f"- {r.get('type')} → {link(self.dim_path[t], self.dim_by_id[t].get('name'))}"
                             + (f": {r.get('rationale')}" if r.get("rationale") else ""))
            for o, r in rel_in:
                lines.append(f"- ← {r.get('type')} from {link(self.dim_path[str(o.get('id'))], o.get('name'))}")
        lines += ["", "## Evidence", "",
                  f"{ev.get('codes', '?')} open codes from {ev.get('documents', '?')} passages in {ev.get('sources', '?')} sources."]
        support = f"{ev.get('sources', 0)} source{'s' if ev.get('sources', 0) != 1 else ''}"
        if self.inp.systems:
            n_sys = len(self.dim_systems(d))
            support += f", {n_sys} system{'s' if n_sys != 1 else ''}"
        lines += ["", f"**Core dimension:** {'yes ★' if self.is_core(d) else 'no'} ({support}; "
                      f"core = {self.core_rule_short()})."]
        self.add(self.dim_path[did], d.get("name") or f"Dimension {did}", "dimension", fm, "\n".join(lines))

    def value_page(self, d: Mapping[str, Any], v: Mapping[str, Any]) -> None:
        vid, did = str(v.get("id")), str(d.get("id"))
        docs = [str(x) for x in v.get("supporting_doc_ids") or []]
        st = v.get("stances") or {}
        systems = self.value_systems(v)
        fm = {"id": vid, "status": v.get("status"), "dimension": link(self.dim_path[did], d.get("name")),
              "accepted_by": list(st.get("accepted") or []), "rejected_by": list(st.get("rejected") or []),
              "passages": len(docs)}
        if self.inp.systems:
            fm["systems"] = [link(self.system_path[s], self.system_title(s)) for s in systems]
        if self.points_by_value.get(vid):
            fm["design_points"] = [link(self.point_path[p], p) for p in sorted(self.points_by_value[vid])]
        if v.get("merged_from"):
            fm["merged_from"] = list(v.get("merged_from"))
        fm["tags"] = ["value", str(v.get("status")), slugify(d.get("name"))]
        lines = [f"# {v.get('label')}", "", v.get("description") or "", "", "## Evidence", ""]
        if not docs:
            lines.append("No supporting passage.")
        for doc in docs:
            sid = source_of(doc)
            passage = self.inp.corpus.get(doc) or {}
            section = f" · {passage.get('section')}" if passage.get("section") else ""
            lines.append(f"- **{doc}** ({self.stance(v, doc)}) · {link(self.source_path[sid], self.source_title(sid))}{section}")
            if self.inp.quotes and passage.get("content"):
                lines.append(f"  > {excerpt(passage['content'], self.inp.quote_words)}")
        if v.get("merged_from"):
            lines += ["", "## Merged from", ""] + [f"- {m}" for m in v.get("merged_from")]
        if self.points_by_value.get(vid):
            lines += ["", "## In design points", "", ", ".join(link(self.point_path[p], p) for p in sorted(self.points_by_value[vid]))]
        self.add(self.value_path[vid], v.get("label") or f"Value {vid}", "value", fm, "\n".join(lines))

    def source_page(self, sid: str) -> None:
        row = self.inp.sources.get(sid) or {}
        uses: List[Tuple[Mapping, Mapping, str, int]] = []
        for d in self.dims:
            for v in d.get("values") or []:
                docs = [str(x) for x in v.get("supporting_doc_ids") or [] if source_of(str(x)) == sid]
                if docs:
                    stances = {self.stance(v, doc) for doc in docs}
                    stance = "both" if "both" in stances or {"accepts", "rejects"} <= stances else sorted(stances)[0]
                    uses.append((d, v, stance, len(docs)))
        fm = {"id": sid, "url": row.get("url", ""), "source_type": row.get("source_type", ""),
              "values_informed": len(uses), "tags": ["source"]}
        title = self.source_title(sid)
        lines = [f"# {title}", ""]
        summary = self.inp.source_summaries.get(sid)
        if summary:
            by = f" by `{self.inp.summary_model}`" if self.inp.summary_model else ""
            lines += ["## Summary", "", summary, "",
                      f"*Summary of the source text generated{by} for this wiki; it is not part of the mining.*", ""]
        lines += ["## Decisions it informs", "", "| Dimension | Value | Stance | Passages |", "|---|---|---|---|"]
        for d, v, stance, n in sorted(uses, key=lambda u: (u[0].get("name", ""), u[1].get("label", ""))):
            lines.append(f"| {cell(link(self.dim_path[str(d.get('id'))], d.get('name')))} | "
                         f"{cell(link(self.value_path[str(v.get('id'))], v.get('label')))} | {stance} | {n} |")
        self.add(self.source_path[sid], title, "source", fm, "\n".join(lines))

    def run_summary(self) -> List[str]:
        tax = self.inp.taxonomy
        values = [v for d in self.dims for v in d.get("values") or []]
        by_status = {s: sum(v.get("status") == s for v in values) for s in STATUS_ORDER}
        m = tax.get("run_metrics") or {}
        rows = [("Run", f"{self.inp.run_label} ({self.inp.view} view)"),
                ("Dimensions", len(self.dims)),
                ("Values", f"{len(values)}: " + ", ".join(f"{by_status[s]} {s}" for s in STATUS_ORDER)),
                ("Sources", len(self.source_ids)),
                ("Iterations", len(tax.get("iterations") or [])),
                ("Dropped dimensions", len(tax.get("dropped_dimensions") or []))]
        if m.get("elapsed_seconds") is not None:
            rows.append(("Run time", f"{m['elapsed_seconds'] / 60:.0f} min"))
        for key, label in MODEL_LABELS:
            if self.inp.models.get(key):
                rows.append((label, f"`{self.inp.models[key]}`"))
        ev = tax.get("evaluation") or {}
        if isinstance(ev.get("overall"), (int, float)) and not ev.get("unavailable"):
            rows.append(("Evaluation score", f"{ev['overall']:.2f} (judge {ev.get('model', '?')})"))
        return ["| Item | Value |", "|---|---|"] + [f"| {k} | {cell(v)} |" for k, v in rows]

    def overview_page(self) -> None:
        lines = ["# Overview", ""]
        if self.inp.use_case:
            lines += ["## Use case", "", self.inp.use_case.strip(), ""]
        if self.inp.narrative:
            lines += ["## Summary", "", self.inp.narrative.strip(), "",
                      "*Narrative summary written by the pipeline at the end of the run (from its report).*", ""]
        lines += ["## Run", ""] + self.run_summary() + ["", "## Dimensions and values", "",
                  f"Core dimensions (★) have {self.core_rule()}; they are listed first.", "",
                  "| Dimension | Core | Accepted | Mixed | Rejected | Outcomes |", "|---|---|---|---|---|---|"]
        for d in sorted(self.dims, key=lambda d: (not self.is_core(d), d.get("name", ""))):
            row = [cell(link(self.dim_path[str(d.get('id'))], d.get("name"))), "★" if self.is_core(d) else ""]
            for s in STATUS_ORDER:
                row.append(cell(items([link(self.value_path[str(v.get('id'))], v.get("label"))
                                       for v in d.get("values") or [] if v.get("status") == s])))
            lines.append("| " + " | ".join(row) + " |")
        self.add("synthesis/overview", "Overview", "synthesis", {"tags": ["synthesis"]}, "\n".join(lines))

    def evaluation_page(self) -> bool:
        tax = self.inp.taxonomy
        ev = tax.get("evaluation") or {}
        criteria = ev.get("criteria") or []
        if not criteria or ev.get("unavailable"):
            return False
        overall = ev.get("overall")
        lines = ["# Evaluation", "",
                 f"Overall score **{overall:.2f}**" if isinstance(overall, (int, float)) else "Overall score: n/a",
                 f"(judge `{ev.get('model', '?')}`, {ev.get('view') or 'final view'}, {ev.get('dimensions', '?')} dimensions). "
                 "Scores are given by an LLM judge inside the pipeline; they are diagnostics, not ground truth.", "",
                 "## Criteria", "", "| Criterion | Score | Pass | Reason |", "|---|---|---|---|"]
        for c in criteria:
            if c.get("evaluated", True):
                score = c.get("score")
                score_s = f"{score:.2f}" if isinstance(score, (int, float)) else "—"
                passed = "yes" if c.get("passed") else ("no" if c.get("passed") is not None else "—")
                reason = " ".join(str(c.get("reason") or "").split())
            else:
                score_s, passed, reason = "—", "—", "Not evaluated (no documents provided)."
            lines.append(f"| **{cell(c.get('name', '?'))}** | {score_s} | {passed} | {cell(reason)} |")
        defs = [c for c in criteria if c.get("description")]
        if defs:
            lines += ["", "## What each criterion checks", ""]
            lines += [f"- **{c['name']}** (threshold {c.get('threshold', '?')}): {c['description']}" for c in defs]
        history = [h for h in tax.get("evaluation_history") or [] if isinstance(h, dict) and not h.get("unavailable")]
        if len(history) >= 2:
            names = []
            for h in history:
                for c in h.get("criteria") or []:
                    if c.get("name") and c["name"] not in names:
                        names.append(c["name"])
            lines += ["", "## Across iterations", "",
                      "Loop drafts are the raw output of each iteration; the final view is consolidated and selected, "
                      "so it is not directly comparable.", "",
                      "| Iteration | View | Dimensions | Overall | " + " | ".join(cell(n) for n in names) + " |",
                      "|---|---|---|---|" + "---|" * len(names)]
            for h in history:
                scores = {c.get("name"): c.get("score") for c in h.get("criteria") or []}
                ov = h.get("overall")
                row = [str(h.get("iteration", "?")), str(h.get("view", "")), str(h.get("dimensions", "")),
                       f"{ov:.2f}" if isinstance(ov, (int, float)) else "—"]
                row += [f"{scores[n]:.1f}" if isinstance(scores.get(n), (int, float)) else "—" for n in names]
                lines.append("| " + " | ".join(row) + " |")
        self.add("synthesis/evaluation", "Evaluation", "synthesis",
                 {"overall": round(overall, 3) if isinstance(overall, (int, float)) else None, "judge": ev.get("model"),
                  "tags": ["synthesis", "evaluation"]}, "\n".join(lines))
        return True

    def contested_page(self) -> None:
        lines = ["# Contested decisions", "",
                 "Options that some passages adopt and others reject (status `mixed`).", ""]
        found = False
        for d in sorted(self.dims, key=lambda d: d.get("name", "")):
            for v in d.get("values") or []:
                if v.get("status") != "mixed":
                    continue
                found = True
                st = v.get("stances") or {}
                lines += [f"## {link(self.value_path[str(v.get('id'))], v.get('label'))}", "",
                          f"Dimension: {link(self.dim_path[str(d.get('id'))], d.get('name'))}", "",
                          f"- Adopted by: {', '.join(st.get('accepted') or []) or '—'}",
                          f"- Rejected by: {', '.join(st.get('rejected') or []) or '—'}", ""]
        if not found:
            lines.append("No contested option in this view.")
        self.add("synthesis/contested", "Contested decisions", "synthesis", {"tags": ["synthesis"]}, "\n".join(lines))

    def dropped_page(self) -> None:
        tax = self.inp.taxonomy
        final = {str(c.get("id")): c for c in ((tax.get("iterations") or [{}])[-1].get("clusters") or []) if isinstance(c, dict)}
        lines = ["# Dropped and unsupported", ""]
        dropped = tax.get("dropped_dimensions") or []
        lines += ["## Dropped dimensions", ""]
        if not dropped:
            lines.append("None.")
        for dd in dropped:
            name = (final.get(str(dd.get("id"))) or {}).get("name") or f"Dimension {dd.get('id')}"
            lines.append(f"- **{name}**: {dd.get('rationale', '')}")
        uns = [(d, u) for d in self.dims for u in d.get("unsupported_values") or []]
        lines += ["", "## Values without supporting evidence", ""]
        if not uns:
            lines.append("None.")
        for d, u in uns:
            label = u.get("label") if isinstance(u, dict) else str(u)
            lines.append(f"- {label} ({link(self.dim_path[str(d.get('id'))], d.get('name'))})")
        self.add("synthesis/dropped", "Dropped and unsupported", "synthesis", {"tags": ["synthesis"]}, "\n".join(lines))

    def system_support(self, code: str) -> Dict[str, List[Tuple[Mapping, int]]]:
        out: Dict[str, List[Tuple[Mapping, int]]] = defaultdict(list)
        for d in self.dims:
            for v in d.get("values") or []:
                if v.get("status") not in CANDIDATE_STATUSES:
                    continue
                n = sum(self.primary_system(doc) == code for doc in v.get("supporting_doc_ids") or [])
                if n:
                    out[str(d.get("id"))].append((v, n))
        return out

    def system_page(self, code: str, points: Sequence[Mapping[str, Any]]) -> None:
        info = self.inp.system_names.get(code) or {}
        support = self.system_support(code)
        title = self.system_title(code)
        fm = {"code": code, "organization": info.get("organization", ""), "dimensions": len(support),
              "tags": ["system"]}
        lines = [f"# {title}", ""]
        if info.get("description"):
            lines += [info["description"], ""]
        lines += [f"Values supported by passages whose primary system is `{code}` (passage → system map).", "",
                  "| Dimension | Values (passages) |", "|---|---|"]
        for did in sorted(support, key=lambda i: self.dim_by_id[i].get("name", "")):
            opts = items([f"{link(self.value_path[str(v.get('id'))], v.get('label'))} ({n})"
                          for v, n in sorted(support[did], key=lambda x: (-x[1], x[0].get("label", "")))])
            lines.append(f"| {cell(link(self.dim_path[did], self.dim_by_id[did].get('name')))} | {cell(opts)} |")
        mine = [p for p in points if p.get("group") == "attested" and p.get("system") == code]
        if mine:
            lines += ["", "## Attested design points", "", ", ".join(link(self.point_path[p["point_id"]], p["point_id"]) for p in mine)]
        self.add(self.system_path[code], title, "system", fm, "\n".join(lines))

    def matrix_page(self) -> None:
        support = {c: self.system_support(c) for c in self.system_codes}
        header = "| Dimension | " + " | ".join(link(self.system_path[c], self.system_title(c)) for c in self.system_codes) + " |"
        lines = ["# System × dimension matrix", "",
                 "For each system, the values of each dimension supported by passages that mainly describe it "
                 "(number of passages; at most three per cell, the rest on the system's page). Empty cells are "
                 "dimensions the system's passages do not inform.", "",
                 header, "|---|" + "---|" * len(self.system_codes)]
        for d in sorted(self.dims, key=lambda d: d.get("name", "")):
            did = str(d.get("id"))
            row = [cell(link(self.dim_path[did], d.get("name")))]
            for c in self.system_codes:
                found = sorted(support[c].get(did, []), key=lambda x: (-x[1], x[0].get("label", "")))
                entries = [f"{link(self.value_path[str(v.get('id'))], v.get('label'))} ({n})" for v, n in found[:3]]
                if len(found) > 3:
                    entries.append(f"+{len(found) - 3} more")
                row.append(cell(items(entries)))
            lines.append("| " + " | ".join(row) + " |")
        self.add("synthesis/system-matrix", "System × dimension matrix", "synthesis", {"tags": ["synthesis"]}, "\n".join(lines))

    def design_points_page(self, points: Sequence[Mapping[str, Any]]) -> None:
        dp = self.inp.design_points or {}
        lines = ["# Design points", "",
                 "Design points combine one value from each of k dimensions, sampled with a fixed seed "
                 "(`benchmark/design_points.py`). **Attested**: one system supports every value. "
                 "**Novel**: no system supports them all; exploring such combinations is a purpose of the design space. "
                 "**Control**: built to fail (a rejected value, or a value from another dimension).", ""]
        for sample in dp.get("samples") or []:
            k = sample.get("k")
            lines += [f"## k = {k}", ""]
            for g in GROUP_ORDER:
                group = [p for p in points if p.get("k") == k and p.get("group") == g]
                if not group:
                    continue
                lines += [f"### {g.capitalize()} ({len(group)})", ""]
                for p in group:
                    tag = p.get("system") or p.get("control") or ""
                    choice = "; ".join(f"{s.get('dimension')}: {s.get('label')}" for s in p.get("values") or [])
                    lines.append(f"- {link(self.point_path[p['point_id']], p['point_id'])}{f' ({tag})' if tag else ''}: {choice}")
                lines.append("")
            diag = sample.get("diagnostics") or {}
            if diag.get("note"):
                lines += [f"*Sampler note:* {diag['note']}", ""]
        self.add("synthesis/design-points", "Design points", "synthesis",
                 {"seed": dp.get("seed"), "attest_by": dp.get("attest_by"), "tags": ["synthesis", "design-points"]},
                 "\n".join(lines))

    def point_page(self, p: Mapping[str, Any]) -> None:
        pid = p["point_id"]
        group = p.get("group")
        title = f"Design point {pid}"
        fm = {"group": group, "k": p.get("k")}
        if p.get("system"):
            fm["system"] = link(self.system_path[p["system"]], self.system_title(p["system"])) if p["system"] in self.system_path else p["system"]
        if p.get("control"):
            fm["control"] = p["control"]
        fm["tags"] = ["design-point", str(group)]
        lines = [f"# {title}", ""]  # group, k, system or control are in the frontmatter (property table)
        description = self.inp.point_descriptions.get(point_signature(p))
        if description:
            by = f" by `{self.inp.point_model}`" if self.inp.point_model else ""
            lines += ["## Description", "", description, "",
                      f"*Description of the combination generated{by} from the values below, without knowing the "
                      "point's group; it is not part of the mining.*", ""]
        lines += ["## Values", "", "| Dimension | Value | Status |", "|---|---|---|"]
        for s in p.get("values") or []:
            did, vid = str(s.get("dimension_id")), str(s.get("value_id"))
            dim = link(self.dim_path[did], s.get("dimension")) if did in self.dim_path else s.get("dimension")
            val = link(self.value_path[vid], s.get("label")) if self.value_path.get(vid) else s.get("label")
            note = ""
            if str(s.get("origin_dimension_id", did)) != did:
                origin = self.dim_by_id.get(str(s.get("origin_dimension_id")), {}).get("name", s.get("origin_dimension_id"))
                note = f" (taken from {origin})"
            lines.append(f"| {cell(dim)} | {cell(val)}{cell(note)} | {s.get('status')} |")
        rels = p.get("relations") or []
        if rels:
            lines += ["", "## Relations among its dimensions", ""]
            for r in rels:
                a, b = self.dim_by_id.get(str(r.get("source")), {}), self.dim_by_id.get(str(r.get("target")), {})
                lines.append(f"- {a.get('name', r.get('source'))} {r.get('type')} {b.get('name', r.get('target'))}")
        self.add(self.point_path[pid], title, "design", fm, "\n".join(lines))

    def index_page(self, has_points: bool) -> None:
        values = sum(len(d.get("values") or []) for d in self.dims)
        lines = ["![DelveDSpace](assets/delvedspace-logo.svg)", "", f"# {self.inp.taxonomy_name}", "",
                  "This wiki presents a **design space** mined by DelveDSpace from a corpus of documents. A design "
                  "space organizes the architectural design decisions the documents discuss: each **dimension** is "
                  "one decision a designer faces, and its **values** are the alternatives the documents describe. "
                  "Every page is generated from the run's data, without rewording, and links to the evidence behind it. "
                  f"New to design spaces or to how they are mined? Start with {link('approach', 'Approach')}.",
                  "",
                  f"Run {self.inp.run_label} ({self.inp.view} view): {len(self.dims)} dimensions, {values} values, "
                  f"{len(self.source_ids)} sources.", ""]
        if self.inp.use_case:
            lines += ["## Use case", "",
                      "*What the run was asked to find: the question that oriented the mining.*", "",
                      self.inp.use_case.strip(), ""]
        lines += ["## Dimensions", "",
                  "*A dimension is one design decision, phrased as a question a designer must answer. Its values are "
                  "the alternative answers found in the sources, each with a status: **accepted** (adopted), "
                  "**rejected** (considered and discarded), **mixed** (adopted by some sources, rejected by others) "
                  "or **outcome** (an effect of decisions, not a choice).*", ""]
        core = [d for d in sorted(self.dims, key=lambda d: d.get("name", "")) if self.is_core(d)]
        other = [d for d in sorted(self.dims, key=lambda d: d.get("name", "")) if not self.is_core(d)]
        lines += [f"**Core dimensions** ({len(core)} of {len(self.dims)}) have {self.core_rule()}: the axes "
                  "the sources share. The others rest on a single source or system.", ""]
        if core:
            lines += ["### Core", ""] + [f"- ★ {link(self.dim_path[str(d.get('id'))], d.get('name'))}: "
                                         f"{len(d.get('values') or [])} values" for d in core]
        if other:
            lines += ["", "### Other", ""] + [f"- {link(self.dim_path[str(d.get('id'))], d.get('name'))}: "
                                               f"{len(d.get('values') or [])} values" for d in other]
        synth = [("synthesis/overview", "Overview", "use case, run summary, narrative summary, and every dimension with its values by status"),
                 ("synthesis/contested", "Contested decisions", "values some sources adopt and others reject"),
                 ("synthesis/dropped", "Dropped and unsupported", "dimensions removed during selection, and values without evidence")]
        if self.system_codes:
            synth.append(("synthesis/system-matrix", "System × dimension matrix", "which value each system takes in each dimension"))
        if has_points:
            synth.append(("synthesis/design-points", "Design points", "sampled combinations of values across dimensions"))
        if getattr(self, "has_evaluation", False):
            synth.append(("synthesis/evaluation", "Evaluation", "how an LLM judge scored the design space, criterion by criterion"))
        lines += ["", "## Synthesis", "", "*Pages that look at the design space as a whole.*", ""]
        lines += [f"- {link(path, label)}: {text}" for path, label, text in synth]
        if self.system_codes:
            lines += ["", "## Systems", "",
                      "*The concrete solutions the sources describe. A system's page shows the values its passages "
                      "support, i.e. its position in the design space.*", ""]
            lines += [f"- {link(self.system_path[c], self.system_title(c))}" for c in self.system_codes]
        lines += ["", "## Sources", "",
                  "*The documents the design space was mined from. A source's page lists the decisions it informs and "
                  "whether it adopts or rejects each value.*", ""]
        for s in self.source_ids:
            summary = self.inp.source_summaries.get(s)
            lines.append(f"- {link(self.source_path[s], self.source_title(s))}"
                         + (f": {first_sentence(summary)}" if summary else ""))
        fm = {"run": self.inp.run_label, "view": self.inp.view, "dimensions": len(self.dims), "values": values,
              "sources": len(self.source_ids)}
        for key, label in MODEL_LABELS:
            if self.inp.models.get(key):
                fm[key] = self.inp.models[key]
        fm["tags"] = ["index"]
        self.add("index", self.inp.taxonomy_name, "index", fm, "\n".join(lines))

    def approach_page(self) -> None:
        """A fixed reference page: grounded theory, the agents, the workflow (same text for every run)."""
        m = self.inp.models
        lines = ["# Approach: how DelveDSpace mines a design space", "",
                 "![The DelveDSpace pipeline](assets/delve-pipeline.svg)", "",
                 "## What a design space is", "",
                 "A **design space** organizes the design decisions of a domain. Each **dimension** is one decision "
                 "point, phrased as a question a designer must answer (*where does the source of truth for a "
                 "repository live?*). Its **values** are the alternative answers found in the documents. Values carry "
                 "a **status**: *accepted* (a source adopts it), *rejected* (a source considered and declined it), "
                 "*mixed* (some sources adopt it, others reject it) or *outcome* (an effect of decisions, such as a "
                 "cost or result, rather than a choice). **Relations** link dimensions that interact "
                 "(*constrains*, *precondition*, *consequence*, *co-occurring*). Every value keeps its **evidence**: "
                 "the passages that support it.", "",
                 "## Grounded theory in brief", "",
                 "DelveDSpace follows **grounded theory**, a qualitative method that builds a theory from data instead "
                 "of testing a theory fixed in advance:", "",
                 "- **Open coding:** read the data closely and name the concepts it contains (*codes*).",
                 "- **Axial coding:** relate codes to each other and group them into categories with properties, by "
                 "**constant comparison** of each new incident with what has been found so far. Here, categories are "
                 "dimensions and properties are values.",
                 "- **Selective coding:** integrate and delimit the theory around the study's question, and validate it "
                 "against the data.",
                 "- **Theoretical saturation:** stop collecting when new data no longer adds concepts.",
                 "- **Memos:** record the reasoning behind each analytic step. Here, the explanation of each iteration "
                 "and the log of editing operations.", "",
                 "## The agents", "",
                 "The pipeline is an orchestrated multi-agent workflow. Agents are roles that share one artifact, the "
                 "design space under construction, and coordinate through it and through explicit feedback. Their "
                 "icons are the ones the command line shows while each step runs.", "",
                 "| Agent | Grounded-theory phase | What it does | What it may change |", "|---|---|---|---|",
                 "| 🔬\u00a0**Coder** | Open coding | Names the concepts of each passage as codes, with the source's stance "
                 "(adopts, rejects, or reports an outcome) | Writes codes; never touches the design space |",
                 "| 🧠\u00a0**Taxonomist** | Axial coding; final review | Folds each batch's codes into the design space and "
                 "justifies every change (add, split, merge, move, rename, relate) | Edits the design space |",
                 "| 📊\u00a0**Critic** | Throughout | Scores each draft on quality criteria and returns actionable issues; "
                 "decides whether a batch added anything new (saturation) | Reads and judges only |",
                 "| 🧲\u00a0**Integrator** | Selective coding | Merges duplicates, links evidence, selects the dimensions that "
                 "pass the support rules, labels the passages | Applies deterministic rules and bounded judgments |", "",
                 "Deterministic checks keep the agents grounded: edits are validated before they apply, evidence is "
                 "rebuilt from the codes by embedding similarity, and dimensions need enough sources and at least two "
                 "candidate decisions to be kept.", "",
                 "## The extraction workflow", "",
                 "1. 📂 📦 **Prepare the corpus.** Sources are split into passages of about 300 words (ids such as "
                 "`s03_p02`: source 3, passage 2) and shuffled into minibatches.",
                 "2. 🔬 **Open coding (Coder).** Each passage of a minibatch gets its codes and stances.",
                 "3. 🧠 🔄 **Axial coding (Taxonomist).** The first minibatch generates an initial design space; each later "
                 "minibatch updates it. In *tools* mode the Taxonomist edits through validated operations and never "
                 "drops a value that has evidence.",
                 "4. 📊 🧪 **Critique (Critic).** The draft is scored (orthogonality, clarity, one decision per dimension, "
                 "coverage, …) and the weakest criteria go back to the Taxonomist as feedback. A saturation check "
                 "compares the next batch's codes with the design space so far.",
                 "5. 🔁 **Loop or stop.** Steps 2–4 repeat for each minibatch until a run of batches adds nothing new "
                 "(saturation) or all batches are coded.",
                 "6. 🔍 **Review (Taxonomist).** A final revision of the whole design space.",
                 "7. 🧲 🎯 🔖 **Integration (Integrator).** Dimensions naming the same decision are merged; duplicate values "
                 "are consolidated (embedding distance plus an LLM judge for borderline pairs); each code is linked to "
                 "its closest value, which yields the evidence; dimensions without enough support are dropped with a "
                 "recorded rationale; passages are labeled with their main dimension.",
                 "8. 📊 **Final evaluation (Critic).** The selected design space is scored once more. Evaluation is "
                 "*observe-only*: scores never change the design space or steer the pipeline.", "",
                 "## LLM roles", "",
                 "Three roles are configured separately so that judging stays independent of what it judges: the "
                 "**generation** LLM (Coder, Taxonomist, Integrator judgments), the **evaluation** LLM (Critic) and "
                 "the **matching** LLM (comparisons with expert ground truth, outside this wiki)."]
        rows = [(label, f"`{m[key]}`") for key, label in MODEL_LABELS if m.get(key)]
        if rows:
            lines += ["", "| Role | Model in this run |", "|---|---|"] + [f"| {k} | {v} |" for k, v in rows]
        lines += ["", "## What in this wiki is not mined", "",
                  "- **Systems** (when present) come from a separate, hand-made map of which passages describe which "
                  "system; a system's position is the values its passages support.",
                  "- **Design points** are sampled combinations of values; their descriptions, and the **source "
                  "summaries**, are written by an LLM for this wiki and labeled as such.",
                  "- Everything else (dimensions, values, statuses, relations, evidence, the narrative summary) is the "
                  "pipeline's output, rendered without rewording."]
        s = self.inp.settings
        if s:
            labels = [("batch_size", "Passages per minibatch"), ("edit_mode", "Taxonomist edit mode"),
                      ("saturation_streak_threshold", "Saturated batches in a row to stop"),
                      ("saturation_min_corpus_fraction", "Share of the corpus coded before stopping"),
                      ("min_dimension_sources", "Minimum sources per dimension"),
                      ("min_candidate_decisions", "Minimum candidate decisions per dimension"),
                      ("relevance_selection", "LLM relevance filter at selection"),
                      ("merge_dimensions", "Dimension merging"), ("open_coding_input", "Open coding reads")]
            present = [(lab, s[k]) for k, lab in labels if s.get(k) is not None]
            if present:
                lines += ["", "## This run's settings", "", "| Setting | Value |", "|---|---|"]
                lines += [f"| {lab} | `{val}` |" for lab, val in present]
        self.add("approach", "Approach", "reference", {"tags": ["reference"]}, "\n".join(lines))

    # tree ----------------------------------------------------------------
    def tree_data(self) -> Dict[str, Any]:
        """Dimensions → values → supporting sources, as a nested tree (the CLI tree's shape)."""
        dims = []
        for d in sorted(self.dims, key=lambda d: d.get("name", "")):
            did, ev = str(d.get("id")), d.get("evidence") or {}
            values = []
            ordered = sorted(d.get("values") or [], key=lambda v: (
                STATUS_ORDER.index(v.get("status")) if v.get("status") in STATUS_ORDER else 9, v.get("label", "")))
            for v in ordered:
                by_source: Dict[str, List[str]] = defaultdict(list)
                for doc in v.get("supporting_doc_ids") or []:
                    by_source[source_of(str(doc))].append(self.stance(v, str(doc)))
                sources = []
                for sid in sorted(by_source, key=_natural):
                    stances = set(by_source[sid])
                    stance = "both" if "both" in stances or {"accepts", "rejects"} <= stances else sorted(stances)[0]
                    n = len(by_source[sid])
                    sources.append({"id": f"{v.get('id')}/s:{sid}", "kind": "source", "label": self.source_title(sid),
                                    "href": self.source_path[sid], "stance": stance,
                                    "meta": f"{stance}, {n} passage{'s' if n != 1 else ''}"})
                n_docs = len(v.get("supporting_doc_ids") or [])
                values.append({"id": "v:" + str(v.get("id")), "kind": "value", "label": v.get("label"),
                               "status": v.get("status"), "href": self.value_path[str(v.get("id"))],
                               "description": v.get("description") or "",
                               "meta": f"{v.get('status')} · {n_docs} passage{'s' if n_docs != 1 else ''}",
                               "children": sources})
            meta = f"{len(values)} values"
            if ev:
                docs, srcs = ev.get("documents", 0), ev.get("sources", 0)
                meta += (f" · evidence: {docs} doc{'s' if docs != 1 else ''} "
                         f"from {srcs} source{'s' if srcs != 1 else ''}")
            dims.append({"id": "d:" + did, "kind": "dimension", "label": d.get("name"), "href": self.dim_path[did],
                         "core": self.is_core(d),
                         "description": d.get("description") or "", "meta": meta, "children": values})
        values = sum(len(d["children"]) for d in dims)
        return {"id": "root", "kind": "root", "label": self.inp.taxonomy_name, "href": "index",
                "meta": f"{len(dims)} dimensions, {values} values, {len(self.source_ids)} sources", "children": dims}

    # graph ---------------------------------------------------------------
    def graph_data(self, points: Sequence[Mapping[str, Any]]) -> None:
        for d in self.dims:
            did = str(d.get("id"))
            self.nodes.append({"id": "d:" + did, "kind": "dimension", "label": d.get("name"), "href": self.dim_path[did],
                               "description": d.get("description") or "", "core": self.is_core(d)})
            for v in d.get("values") or []:
                vid = str(v.get("id"))
                self.nodes.append({"id": "v:" + vid, "kind": "value", "label": v.get("label"), "status": v.get("status"),
                                   "href": self.value_path[vid], "dimension": d.get("name"), "core": self.is_core(d),
                                   "description": v.get("description") or ""})
                self.edges.append({"source": "d:" + did, "target": "v:" + vid, "type": "has_value"})
            for r in d.get("relations") or []:
                t = str(r.get("target_id"))
                if t in self.dim_by_id and t != did:
                    self.edges.append({"source": "d:" + did, "target": "d:" + t, "type": "relation",
                                       "relation": r.get("type")})
        for sid in self.source_ids:
            node = {"id": "s:" + sid, "kind": "source", "label": self.source_title(sid), "href": self.source_path[sid]}
            if self.inp.source_summaries.get(sid):
                node.update(description=self.inp.source_summaries[sid], description_note="Generated summary of the source.")
            self.nodes.append(node)
        pairs: Dict[Tuple[str, str], Set[str]] = defaultdict(set)
        for d in self.dims:
            for v in d.get("values") or []:
                for doc in v.get("supporting_doc_ids") or []:
                    pairs[(source_of(str(doc)), str(v.get("id")))].add(self.stance(v, str(doc)))
        for (sid, vid), stances in sorted(pairs.items()):
            stance = "both" if "both" in stances or {"accepts", "rejects"} <= stances else sorted(stances)[0]
            self.edges.append({"source": "s:" + sid, "target": "v:" + vid, "type": "evidence", "stance": stance})
        for code in self.system_codes:
            self.nodes.append({"id": "y:" + code, "kind": "system", "label": self.system_title(code), "href": self.system_path[code],
                               "description": (self.inp.system_names.get(code) or {}).get("description", "")})
            for did, items in sorted(self.system_support(code).items()):
                for v, n in items:
                    self.edges.append({"source": "y:" + code, "target": "v:" + str(v.get("id")), "type": "system", "weight": n})
        for p in points:
            pid = p["point_id"]
            node = {"id": "p:" + pid, "kind": "design", "label": pid, "group": p.get("group"), "k": p.get("k"),
                    "tag": p.get("system") or p.get("control") or "", "href": self.point_path[pid]}
            if self.inp.point_descriptions.get(point_signature(p)):
                node["description"] = self.inp.point_descriptions[point_signature(p)]
                node["description_note"] = "Generated description of the combination."
            self.nodes.append(node)
            for s in p.get("values") or []:
                if self.value_path.get(str(s.get("value_id"))):
                    self.edges.append({"source": "p:" + pid, "target": "v:" + str(s.get("value_id")), "type": "design"})


def _natural(s: str):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]


def build(inp: Inputs) -> Export:
    """Pages and graph data for one run (pure function of ``inp``)."""
    return _Builder(inp).build()
