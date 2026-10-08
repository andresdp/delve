"""Design-space wiki: the pages and graph data of one run (docs/DESIGN_SPACE_EXPLORATION.md §13).

Everything here is rendered from run data by templates, with no LLM call (R1),
and the same inputs always give the same pages (R10). Pages follow the
llmwiki-cli layout, which Obsidian also reads:

- ``concepts/``: dimensions (decision points);
- ``entities/``: values (candidate decisions and outcomes);
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
    view: str = "selected"
    quotes: bool = True
    quote_words: int = 60


@dataclass
class Export:
    pages: List[Page]
    graph: Dict[str, Any]
    manifest: Dict[str, Any]


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
        self.index_page(bool(points))
        self.graph_data(points)
        self.pages.sort(key=lambda p: (p.path != "index", p.path))
        return Export(pages=self.pages, graph={"nodes": self.nodes, "edges": self.edges}, manifest={})

    def dimension_page(self, d: Mapping[str, Any]) -> None:
        did = str(d.get("id"))
        values = d.get("values") or []
        counts = {s: sum(v.get("status") == s for v in values) for s in STATUS_ORDER}
        ev = d.get("evidence") or {}
        rel_out = [(r, str(r.get("target_id"))) for r in d.get("relations") or [] if str(r.get("target_id")) in self.dim_by_id]
        rel_in = [(o, r) for o in self.dims for r in o.get("relations") or [] if str(r.get("target_id")) == did]
        fm = {"id": did, "options": len(values),
              "candidate_options": sum(counts[s] for s in CANDIDATE_STATUSES), "outcomes": counts["outcome"],
              "evidence": {"codes": ev.get("codes"), "documents": ev.get("documents"), "sources": ev.get("sources")},
              "relations": [f"{r.get('type')} {link(self.dim_path[t], self.dim_by_id[t].get('name'))}" for r, t in rel_out],
              "tags": ["dimension"]}
        lines = [f"# {d.get('name')}", "", d.get("description") or "", ""]
        lines += ["## Options", "", "| Option | Status | Passages |", "|---|---|---|"]
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
              "options_informed": len(uses), "tags": ["source"]}
        title = self.source_title(sid)
        lines = [f"# {title}", ""]
        if row.get("url"):
            lines += [f"<{row['url']}>", ""]
        lines += ["## Decisions it informs", "", "| Dimension | Option | Stance | Passages |", "|---|---|---|---|"]
        for d, v, stance, n in sorted(uses, key=lambda u: (u[0].get("name", ""), u[1].get("label", ""))):
            lines.append(f"| {cell(link(self.dim_path[str(d.get('id'))], d.get('name')))} | "
                         f"{cell(link(self.value_path[str(v.get('id'))], v.get('label')))} | {stance} | {n} |")
        self.add(self.source_path[sid], title, "source", fm, "\n".join(lines))

    def overview_page(self) -> None:
        lines = ["# Overview", "", f"{len(self.dims)} dimensions, "
                 f"{sum(len(d.get('values') or []) for d in self.dims)} options.", "",
                 "| Dimension | Accepted | Mixed | Rejected | Outcomes |", "|---|---|---|---|---|"]
        for d in sorted(self.dims, key=lambda d: d.get("name", "")):
            row = [cell(link(self.dim_path[str(d.get('id'))], d.get("name")))]
            for s in STATUS_ORDER:
                row.append(cell(", ".join(link(self.value_path[str(v.get('id'))], v.get("label"))
                                          for v in d.get("values") or [] if v.get("status") == s)))
            lines.append("| " + " | ".join(row) + " |")
        self.add("synthesis/overview", "Overview", "synthesis", {"tags": ["synthesis"]}, "\n".join(lines))

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
        lines += [f"Options supported by passages whose primary system is `{code}` (passage → system map).", "",
                  "| Dimension | Options (passages) |", "|---|---|"]
        for did in sorted(support, key=lambda i: self.dim_by_id[i].get("name", "")):
            opts = ", ".join(f"{link(self.value_path[str(v.get('id'))], v.get('label'))} ({n})"
                             for v, n in sorted(support[did], key=lambda x: (-x[1], x[0].get("label", ""))))
            lines.append(f"| {cell(link(self.dim_path[did], self.dim_by_id[did].get('name')))} | {cell(opts)} |")
        mine = [p for p in points if p.get("group") == "attested" and p.get("system") == code]
        if mine:
            lines += ["", "## Attested design points", "", ", ".join(link(self.point_path[p["point_id"]], p["point_id"]) for p in mine)]
        self.add(self.system_path[code], title, "system", fm, "\n".join(lines))

    def matrix_page(self) -> None:
        support = {c: self.system_support(c) for c in self.system_codes}
        header = "| Dimension | " + " | ".join(link(self.system_path[c], self.system_title(c)) for c in self.system_codes) + " |"
        lines = ["# System × dimension matrix", "",
                 "For each system, the options of each dimension supported by passages that mainly describe it "
                 "(number of passages; at most three per cell, the rest on the system's page). Empty cells are "
                 "dimensions the system's passages do not inform.", "",
                 header, "|---|" + "---|" * len(self.system_codes)]
        for d in sorted(self.dims, key=lambda d: d.get("name", "")):
            did = str(d.get("id"))
            row = [cell(link(self.dim_path[did], d.get("name")))]
            for c in self.system_codes:
                items = sorted(support[c].get(did, []), key=lambda x: (-x[1], x[0].get("label", "")))
                shown = ", ".join(f"{link(self.value_path[str(v.get('id'))], v.get('label'))} ({n})" for v, n in items[:3])
                if len(items) > 3:
                    shown += f", +{len(items) - 3} more"
                row.append(cell(shown))
            lines.append("| " + " | ".join(row) + " |")
        self.add("synthesis/system-matrix", "System × dimension matrix", "synthesis", {"tags": ["synthesis"]}, "\n".join(lines))

    def design_points_page(self, points: Sequence[Mapping[str, Any]]) -> None:
        dp = self.inp.design_points or {}
        lines = ["# Design points", "",
                 "Design points combine one option from each of k dimensions, sampled with a fixed seed "
                 "(`benchmark/design_points.py`). **Attested**: one system supports every option. "
                 "**Novel**: no system supports them all; exploring such combinations is a purpose of the design space. "
                 "**Control**: built to fail (a rejected option, or an option from another dimension).", ""]
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
        tag = p.get("system") or p.get("control")
        title = f"Design point {pid}"
        fm = {"group": group, "k": p.get("k")}
        if p.get("system"):
            fm["system"] = link(self.system_path[p["system"]], self.system_title(p["system"])) if p["system"] in self.system_path else p["system"]
        if p.get("control"):
            fm["control"] = p["control"]
        fm["tags"] = ["design-point", str(group)]
        lines = [f"# {title}", "", f"**Group:** {group}" + (f" ({tag})" if tag else ""), "",
                 "| Dimension | Option | Status |", "|---|---|---|"]
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
        tax = self.inp.taxonomy
        lines = [f"# {self.inp.taxonomy_name}", "",
                 f"Design space mined by Delve (run {self.inp.run_label}, {self.inp.view} view): "
                 f"{len(self.dims)} dimensions, {values} options, {len(self.source_ids)} sources.", ""]
        if self.inp.use_case:
            lines += ["## Use case", "", self.inp.use_case.strip(), ""]
        lines += ["## Dimensions", ""]
        for d in sorted(self.dims, key=lambda d: d.get("name", "")):
            lines.append(f"- {link(self.dim_path[str(d.get('id'))], d.get('name'))}: {len(d.get('values') or [])} options")
        lines += ["", "## Synthesis", "", f"- {link('synthesis/overview', 'Overview')}",
                  f"- {link('synthesis/contested', 'Contested decisions')}",
                  f"- {link('synthesis/dropped', 'Dropped and unsupported')}"]
        if self.system_codes:
            lines.append(f"- {link('synthesis/system-matrix', 'System × dimension matrix')}")
        if has_points:
            lines.append(f"- {link('synthesis/design-points', 'Design points')}")
        if self.system_codes:
            lines += ["", "## Systems", ""] + [f"- {link(self.system_path[c], self.system_title(c))}" for c in self.system_codes]
        lines += ["", "## Sources", ""] + [f"- {link(self.source_path[s], self.source_title(s))}" for s in self.source_ids]
        metrics = tax.get("run_metrics") or {}
        fm = {"run": self.inp.run_label, "view": self.inp.view, "dimensions": len(self.dims), "options": values,
              "sources": len(self.source_ids), "total_tokens": metrics.get("total_tokens"), "tags": ["index"]}
        self.add("index", self.inp.taxonomy_name, "index", fm, "\n".join(lines))

    # graph ---------------------------------------------------------------
    def graph_data(self, points: Sequence[Mapping[str, Any]]) -> None:
        for d in self.dims:
            did = str(d.get("id"))
            self.nodes.append({"id": "d:" + did, "kind": "dimension", "label": d.get("name"), "href": self.dim_path[did]})
            for v in d.get("values") or []:
                vid = str(v.get("id"))
                self.nodes.append({"id": "v:" + vid, "kind": "value", "label": v.get("label"), "status": v.get("status"),
                                   "href": self.value_path[vid], "dimension": d.get("name")})
                self.edges.append({"source": "d:" + did, "target": "v:" + vid, "type": "has_value"})
            for r in d.get("relations") or []:
                t = str(r.get("target_id"))
                if t in self.dim_by_id and t != did:
                    self.edges.append({"source": "d:" + did, "target": "d:" + t, "type": "relation",
                                       "relation": r.get("type")})
        for sid in self.source_ids:
            self.nodes.append({"id": "s:" + sid, "kind": "source", "label": self.source_title(sid), "href": self.source_path[sid]})
        pairs: Dict[Tuple[str, str], Set[str]] = defaultdict(set)
        for d in self.dims:
            for v in d.get("values") or []:
                for doc in v.get("supporting_doc_ids") or []:
                    pairs[(source_of(str(doc)), str(v.get("id")))].add(self.stance(v, str(doc)))
        for (sid, vid), stances in sorted(pairs.items()):
            stance = "both" if "both" in stances or {"accepts", "rejects"} <= stances else sorted(stances)[0]
            self.edges.append({"source": "s:" + sid, "target": "v:" + vid, "type": "evidence", "stance": stance})
        for code in self.system_codes:
            self.nodes.append({"id": "y:" + code, "kind": "system", "label": self.system_title(code), "href": self.system_path[code]})
            for did, items in sorted(self.system_support(code).items()):
                for v, n in items:
                    self.edges.append({"source": "y:" + code, "target": "v:" + str(v.get("id")), "type": "system", "weight": n})
        for p in points:
            pid = p["point_id"]
            self.nodes.append({"id": "p:" + pid, "kind": "design", "label": pid, "group": p.get("group"), "k": p.get("k"),
                               "tag": p.get("system") or p.get("control") or "", "href": self.point_path[pid]})
            for s in p.get("values") or []:
                if self.value_path.get(str(s.get("value_id"))):
                    self.edges.append({"source": "p:" + pid, "target": "v:" + str(s.get("value_id")), "type": "design"})


def _natural(s: str):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]


def build(inp: Inputs) -> Export:
    """Pages and graph data for one run (pure function of ``inp``)."""
    return _Builder(inp).build()
