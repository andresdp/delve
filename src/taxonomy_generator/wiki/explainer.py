"""Render a checked design rationale file (``ddspace-rationale/3``) as an explainer page.

The page sits at ``<html dir>/explainers/<id>.html``, next to the wiki's HTML, or in a standalone folder
(``<out>/explainers/<id>.html`` with its own ``assets/``). It shows the requirements, one tab per alternative
plus a compare view, a radial subgraph of the dimensions involved, a details panel and, for explain, the
uncovered decisions. With a space, dimensions, values and sources link to their wiki pages (a page that does
not exist is shown without a link); evidence is passage ids with stances, never quotes (``raw/graph.json``
holds no passage text). A file with its own space (``space.dimensions``) is drawn from those dimensions and
values, with no wiki links and no sources.

The caller checks the file first (``delvedspace.rationale.check``): this module assumes a clean file.
"""

from __future__ import annotations

import html
import json
import os
import re
import shutil
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence

from taxonomy_generator.wiki.query import norm
from taxonomy_generator.wiki.render import TEMPLATES, _env, copy_images, copy_page_assets

LAYOUT_SCRIPT = TEMPLATES / "graph-layout.js"

EXPLAINERS = "explainers"
ASSETS_MARKER = ".ddspace-assets"  # in a standalone folder's assets/: ddspace created it and may overwrite it
Link = Callable[[str], Optional[str]]  # a wiki page path (``concepts/x``) or file (``index.html``) -> href or None


def wiki_links(wiki_html: Optional[Path], page_dir: Path) -> Link:
    """Return a function giving the href from ``page_dir`` to a wiki page, or None when it has no page."""
    cache: Dict[str, Optional[str]] = {}

    def link(target: str) -> Optional[str]:
        if wiki_html is None or not target:
            return None
        if target not in cache:
            name = target if target.endswith(".html") else f"{target}.html"
            path = Path(wiki_html) / name
            cache[target] = (Path(os.path.relpath(path.resolve(), Path(page_dir).resolve())).as_posix()
                             if path.is_file() else None)
        return cache[target]
    return link


# ── page data ────────────────────────────────────────────────────────────

def own_graph(space: Mapping[str, Any]) -> Dict[str, Any]:
    """Return the agent's own space (``space.dimensions``, ``space.relations``) shaped like a wiki graph."""
    nodes: List[Dict[str, Any]] = []
    for dim in space.get("dimensions") or []:
        if not isinstance(dim, dict):
            continue
        nodes.append({"id": dim.get("id"), "kind": "dimension", "label": dim.get("name") or dim.get("id")})
        for v in dim.get("values") or []:
            if isinstance(v, dict):
                nodes.append({"id": v.get("id"), "kind": "value", "label": v.get("name") or v.get("id"),
                              "dimension_id": dim.get("id")})
    edges = [{"source": r.get("source"), "target": r.get("target"), "type": "relation", "relation": r.get("type"),
              "directed": True} for r in space.get("relations") or [] if isinstance(r, dict)]
    return {"nodes": nodes, "edges": edges}


class _Space:
    """The dimensions and values the file touches, from the wiki's graph or from the file's own space.

    ``wiki`` says whether they come from a wiki (with links and sources). Files of an older schema without any
    space (``space: null``, choices naming ``decision`` and ``option``) are still drawn from the file.
    """

    def __init__(self, doc: Mapping[str, Any], graph: Optional[Mapping[str, Any]], link: Link):
        meta = doc.get("space")
        self.wiki = isinstance(meta, dict) and "dimensions" not in meta and graph is not None
        if isinstance(meta, dict) and "dimensions" in meta:
            graph, link = own_graph(meta), (lambda _target: None)
        self.graph, self.link = graph, link
        self.with_space = isinstance(meta, dict) and graph is not None
        self.dims: Dict[str, Dict[str, Any]] = {}
        self.values: Dict[str, Dict[str, Any]] = {}
        self._by_id = {n["id"]: n for n in (graph or {}).get("nodes") or []} if self.with_space else {}
        self._keys: Dict[str, str] = {}  # without a space: normalized label -> made-up id
        self._dim_values: Dict[Any, List[Dict[str, Any]]] = {}  # dimension id -> its value nodes, in node order
        self._evidence: Dict[Any, List[Dict[str, Any]]] = {}    # value id -> evidence edges, in edge order
        if self.with_space:
            for n in self._by_id.values():
                if n.get("kind") == "value":
                    self._dim_values.setdefault(n.get("dimension_id"), []).append(n)
            for e in graph.get("edges") or []:
                if e.get("type") == "evidence":
                    self._evidence.setdefault(e.get("target"), []).append(e)

    def node(self, ref: Any) -> Optional[Dict[str, Any]]:
        """Return the graph node with id ``ref`` (None without a space or when there is none)."""
        return self._by_id.get(ref)

    def dim(self, ref: Any) -> Optional[str]:
        """Register and return the id of the dimension a choice names (a graph id, or the agent's decision)."""
        if ref is None or ref == "":
            return None
        if self.with_space:
            n = self._by_id.get(ref)
            if n is None or n.get("kind") != "dimension":
                return None
            if ref not in self.dims:
                self.dims[ref] = {"id": ref, "label": n.get("label") or ref, "question": n.get("description") or "",
                                  "href": self.link(n.get("href") or ""), "core": bool(n.get("core")), "values": []}
                for v in self._dim_values.get(ref, []):
                    self._value_node(v)
            return ref
        key = norm(ref)
        if key not in self._keys:
            self._keys[key] = f"x:{len(self._keys) + 1}"
            self.dims[self._keys[key]] = {"id": self._keys[key], "label": str(ref).strip(), "question": "",
                                          "href": None, "core": False, "values": []}
        return self._keys[key]

    def _value_node(self, v: Mapping[str, Any]) -> None:
        sources = []
        for e in self._evidence.get(v["id"], []):
            if e.get("source") in self._by_id:
                s = self._by_id[e["source"]]
                sources.append({"id": s["id"], "label": s.get("label") or s["id"], "stance": e.get("stance") or "",
                                "href": self.link(s.get("href") or "")})
        self.values[v["id"]] = {"id": v["id"], "label": v.get("label") or v["id"], "dimension": v["dimension_id"],
                                "status": v.get("status") or "", "description": v.get("description") or "",
                                "href": self.link(v.get("href") or ""),
                                "passages": [{"doc": p.get("doc"), "stance": p.get("stance") or ""}
                                             for p in v.get("passages") or []],
                                "sources": sources}
        self.dims[v["dimension_id"]]["values"].append(v["id"])

    def value(self, dim: Optional[str], ref: Any) -> Optional[str]:
        if dim is None or ref is None:
            return None
        if self.with_space:
            return ref if ref in self.values else None
        key = f"{dim}::{norm(ref)}"
        if key not in self._keys:
            self._keys[key] = f"o:{len(self.values) + 1}"
            vid = self._keys[key]
            self.values[vid] = {"id": vid, "label": str(ref).strip(), "dimension": dim, "status": "",
                                "description": "", "href": None, "passages": [], "sources": []}
            self.dims[dim]["values"].append(vid)
        return self._keys[key]

    def names(self, obj: Mapping[str, Any]):
        """Return (dimension id, value id) a choice or considered entry names."""
        if self.with_space:
            d = self.dim(obj.get("dimension_id"))
            return d, self.value(d, obj.get("value_id"))
        d = self.dim(obj.get("decision"))
        return d, self.value(d, obj.get("option"))

    def decision(self, obj: Mapping[str, Any], key: str = "") -> Optional[str]:
        return self.dim(obj.get(key or ("dimension_id" if self.with_space else "decision")))

    def point(self, values: Any) -> Dict[str, str]:
        """Return ``{dimension id: value id}`` of a step's or region's ``values`` (ids, or ``{decision, option}``)."""
        out: Dict[str, str] = {}
        for item in values if isinstance(values, list) else []:
            if self.with_space:
                n = self._by_id.get(item) if isinstance(item, str) else None
                d = self.dim(n.get("dimension_id")) if n is not None and n.get("kind") == "value" else None
                v = self.value(d, item)
            elif isinstance(item, dict):
                d, v = self.names(item)
            else:
                d = v = None
            if d is not None and v is not None and d not in out:
                out[d] = v
        return out


def _trajectory(doc: Mapping[str, Any], space: _Space, alternatives: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """The steps the agent took, each with its point and what changed against its parent (or what was new)."""
    steps: List[Dict[str, Any]] = []
    by_number: Dict[Any, Dict[str, Any]] = {}
    seen: set = set()
    proposed = {a["step"]: a["id"] for a in alternatives if a.get("step") is not None}
    for s in doc.get("trajectory") or []:
        if not isinstance(s, dict):
            continue
        point = space.point(s.get("values"))
        parent = by_number.get(s.get("parent"))
        if parent is not None:
            before = parent["point"]
            changed = sorted(d for d in set(point) | set(before) if point.get(d) != before.get(d))
        else:
            changed = []
        novel = [d for d, v in point.items() if v not in seen]
        seen.update(point.values())
        record = s.get("point") if isinstance(s.get("point"), dict) else {}
        attested = []
        for ref in record.get("attested_by") or []:
            sid = ref.get("id") if isinstance(ref, dict) else ref
            n = space.node(sid) if isinstance(sid, str) else None
            attested.append({"id": str(sid), "label": (n or {}).get("label") or str(sid),
                             "href": space.link((n or {}).get("href") or "") if n else None})
        assessment = s.get("assessment") if isinstance(s.get("assessment"), dict) else {}
        step = {"step": s.get("step"), "move": s.get("move") or "", "parent": s.get("parent"),
                "round": s.get("round"), "approach": s.get("approach"),
                "why": s.get("hypothesis") or s.get("why") or "", "observation": s.get("observation") or "",
                "verdict": s.get("rating") or s.get("verdict") or "", "assessment": dict(assessment),
                "drivers": list(assessment) or list(s.get("drivers") or []),
                "point": point, "changed": changed, "novel": novel,
                "description": record.get("description") or "", "attested_by": attested,
                "alternative": proposed.get(s.get("step"))}
        steps.append(step)
        by_number[s.get("step")] = step
    return steps


def page_data(doc: Mapping[str, Any], graph: Optional[Mapping[str, Any]], link: Link,
              graph_changed: bool = False) -> Dict[str, Any]:
    """Build everything the explainer shows from a checked rationale file and the space's graph."""
    space = _Space(doc, graph, link)
    with_space = space.with_space
    problem = doc.get("problem") or {}
    alternatives = []
    for alt in doc.get("alternatives") or []:
        choices = []
        for c in alt.get("choices") or []:
            d, v = space.names(c)
            choices.append({"dimension": d, "value": v, "drivers": list(c.get("drivers") or []),
                            "reason": c.get("reason") or "", "quote": c.get("solution_quote") or "",
                            "forced": c.get("forced"),
                            "evidence": [{"doc": e.get("doc"), "stance": e.get("stance") or ""}
                                         for e in c.get("evidence") or []]})
        considered = []
        for c in alt.get("considered") or []:
            d, v = space.names(c)
            considered.append({"dimension": d, "value": v, "drivers": list(c.get("drivers") or []),
                               "reason": c.get("reason") or ""})
        open_ = [{"dimension": space.decision(o), "reason": o.get("reason") or ""} for o in alt.get("open") or []]
        relations = []
        for r in alt.get("relations") or []:
            s, t = space.dim(r.get("source")), space.dim(r.get("target"))
            relations.append({"source": s, "target": t, "source_label": str(r.get("source")),
                              "target_label": str(r.get("target")), "type": r.get("type") or "",
                              "holds": bool(r.get("holds")), "note": r.get("note") or ""})
        alternatives.append({"id": str(alt.get("id")), "name": alt.get("name") or str(alt.get("id")),
                             "summary": alt.get("summary") or "", "choices": choices, "considered": considered,
                             "open": open_, "relations": relations, "step": alt.get("step"),
                             "approach": alt.get("approach")})

    trajectory = _trajectory(doc, space, alternatives)
    by_step = {s["step"]: s for s in trajectory}
    for alt in alternatives:
        alt["point"] = (by_step.get(alt["step"]) or {}).get("description") or ""
    regions = []
    for r in doc.get("regions") or []:
        if isinstance(r, dict):
            regions.append({"id": str(r.get("id")), "name": r.get("name") or str(r.get("id")),
                            "point": space.point(r.get("values")), "step": r.get("step"),
                            "drivers": list(r.get("drivers") or []), "reason": r.get("reason") or ""})
    # The grid's rows: every dimension a step investigated, in the order the steps first name them.
    trajectory_dims: List[str] = []
    for s in trajectory:
        trajectory_dims += [d for d in s["point"] if d not in trajectory_dims]
    budget = doc.get("budget") if isinstance(doc.get("budget"), dict) else {}

    notes = {}
    for item in doc.get("comparison") or []:
        d = space.decision(item)
        if d is not None:
            notes[d] = item.get("note") or ""

    # Which values each alternative chose or considered; every other value is "offered by the space".
    for v in space.values.values():
        v["roles"] = {}
        v["steps"] = [s["step"] for s in trajectory if v["id"] in s["point"].values()]
    for alt in alternatives:
        for c in alt["choices"]:
            if c["value"]:
                space.values[c["value"]]["roles"][alt["id"]] = "chosen"
        for c in alt["considered"]:
            if c["value"]:
                space.values[c["value"]]["roles"].setdefault(alt["id"], "considered")

    involved = list(space.dims)  # first appearance order: the order the file names them
    rows = []
    for d in involved:
        cells = []
        for alt in alternatives:
            chosen = next((c for c in alt["choices"] if c["dimension"] == d), None)
            gap = next((o for o in alt["open"] if o["dimension"] == d), None)
            if chosen is not None:
                cells.append({"kind": "choice", "value": chosen["value"], "reason": chosen["reason"]})
            elif gap is not None:
                cells.append({"kind": "open", "value": None, "reason": gap["reason"]})
            else:
                cells.append({"kind": "none", "value": None, "reason": ""})
        if not any(c["kind"] != "none" for c in cells) and d not in notes:
            continue  # named only by a considered entry or a relation: no row of its own
        signature = {(c["kind"], c["value"]) for c in cells}
        rows.append({"dimension": d, "cells": cells, "differs": len(signature) > 1, "note": notes.get(d, "")})
    rows.sort(key=lambda r: not r["differs"])  # stable: differing rows first, each group in file order

    relations = []
    if with_space:
        ids = set(space.dims)
        for e in space.graph.get("edges") or []:
            if e.get("type") == "relation" and e.get("source") in ids and e.get("target") in ids:
                relations.append({"source": e["source"], "target": e["target"], "type": e.get("relation") or "",
                                  "directed": e.get("directed") is not False, "reading": e.get("reading") or ""})

    uncovered = []
    for u in doc.get("uncovered") or []:
        near = u.get("nearest_dimension_id")
        n = space.node(near) if space.wiki and near else None
        uncovered.append({"decision": u.get("decision") or "", "quote": u.get("solution_quote") or "",
                          "nearest": ({"id": near, "label": n.get("label") or near, "href": link(n.get("href") or "")}
                                      if n else None)})

    meta = doc.get("space") if isinstance(doc.get("space"), dict) else None
    return {
        "id": str(doc.get("id")), "mode": doc.get("mode"), "with_space": with_space, "wiki": space.wiki,
        "title": problem.get("title") or str(doc.get("id")), "context": problem.get("context") or "",
        "space": {"workspace": meta.get("workspace"), "run": meta.get("run"),
                  "domain": (graph or {}).get("domain") or (graph or {}).get("name") or meta.get("workspace")}
        if space.wiki else None,
        "approaches": [{"id": a.get("id"), "idea": a.get("idea") or "", "status": a.get("status") or "",
                        "dropped_because": a.get("dropped_because") or ""}
                       for a in doc.get("approaches") or [] if isinstance(a, dict)],
        "graph_changed": graph_changed,
        "requirements": [{"id": r.get("id"), "text": r.get("text") or "", "kind": r.get("kind") or "",
                          "attribute": r.get("attribute") or ""} for r in problem.get("requirements") or []],
        "alternatives": alternatives, "dimensions": space.dims, "values": space.values, "rows": rows,
        "relations": relations, "uncovered": uncovered, "trajectory": trajectory,
        "trajectory_dimensions": trajectory_dims, "regions": regions,
        "budget": {"max_points": budget.get("max_points"), "used": len(trajectory)},
        "links": {"index": link("index.html"), "graph": link("graph.html")},
    }


# ── writing ──────────────────────────────────────────────────────────────

def _render(data: Mapping[str, Any]) -> str:
    return _env().get_template("explainer.html.j2").render(
        d=data, data=json.dumps(data, ensure_ascii=False, sort_keys=True).replace("</", "<\\/"),
        assets="../assets")


def write_page(doc: Mapping[str, Any], graph: Optional[Mapping[str, Any]], root: Path, *,
               wiki_html: Optional[Path] = None, graph_changed: bool = False) -> Path:
    """Write ``<root>/explainers/<id>.html``; ``wiki_html`` is the wiki's HTML folder its links point into.

    ``root`` is the wiki's HTML folder itself (the page uses its ``assets/``) or a standalone folder (see
    ``write_standalone``). Returns the page path.
    """
    page = Path(root) / EXPLAINERS / f"{doc['id']}.html"
    page.parent.mkdir(parents=True, exist_ok=True)
    # A wiki exported before the shared layout script existed lacks it: the page would draw no graph until the next
    # export. Add the script alone; the export owns the other assets.
    layout = Path(root) / "assets" / "graph-layout.js"
    if layout.parent.is_dir() and not layout.is_file():
        shutil.copyfile(LAYOUT_SCRIPT, layout)
    data = page_data(doc, graph, wiki_links(wiki_html, page.parent), graph_changed)
    page.write_text(_render(data), encoding="utf-8")
    return page


class ForeignAssets(Exception):
    """A standalone folder already has an ``assets/`` folder that ddspace did not create (no ``ASSETS_MARKER``)."""


def foreign_assets(root: Path) -> Optional[Path]:
    """Return ``<root>/assets`` when it exists but ddspace did not create it (so it must not be overwritten)."""
    assets = Path(root) / "assets"
    return assets if assets.exists() and not (assets / ASSETS_MARKER).is_file() else None


def copy_assets(root: Path) -> None:
    """Copy what the page loads (d3, the layout script, the stylesheet, the icons) into ``<root>/assets``, so it opens offline.

    Raises ``ForeignAssets`` when ``<root>/assets`` exists without ddspace's marker file; writes the marker.
    """
    assets = Path(root) / "assets"
    if foreign_assets(root) is not None:
        raise ForeignAssets(f"{assets} exists and ddspace did not create it (no {ASSETS_MARKER}): "
                            "choose another --out folder")
    assets.mkdir(parents=True, exist_ok=True)
    (assets / ASSETS_MARKER).write_text("Written by ddspace rationale build; it may overwrite this folder.\n",
                                        encoding="utf-8")
    copy_images(assets, None)
    copy_page_assets(assets)


def write_standalone(doc: Mapping[str, Any], graph: Optional[Mapping[str, Any]], out: Path, *,
                     wiki_html: Optional[Path] = None, graph_changed: bool = False) -> Path:
    """Write ``<out>/explainers/<id>.html`` and ``<out>/assets/``; links (if any) point into ``wiki_html``."""
    copy_assets(out)
    return write_page(doc, graph, out, wiki_html=wiki_html, graph_changed=graph_changed)


# ── the index's list of explainers ───────────────────────────────────────

INDEX_REGION = re.compile(r"<!-- explainers -->.*?<!-- /explainers -->", re.S)
# where page.html.j2 puts the region: after the body, before the tags, the footer or the end of <main>
INDEX_ANCHOR = re.compile(r'<div class="tags">|<footer>|</main>')


def write_index(html_root: Path, entries: Sequence[Mapping[str, Any]]) -> bool:
    """Write the "Explainers" list into ``<html_root>/index.html`` (empty when there are none).

    ``entries`` are ``{id, title, mode, changed}`` of the rendered pages. The list sits in a marked region of the
    HTML index only (``wiki/index.md`` is left alone). An index exported before the region existed gets one,
    after the page body, where the template puts it. Returns False when there is no index or no place for it.
    """
    index = Path(html_root) / "index.html"
    try:
        original = text = index.read_text(encoding="utf-8")
    except OSError:
        return False
    if not INDEX_REGION.search(text):
        anchor = INDEX_ANCHOR.search(text)
        if anchor is None:
            return False
        text = text[:anchor.start()] + "<!-- explainers --><!-- /explainers -->" + text[anchor.start():]
    block = ""
    if entries:
        items = "".join(
            f'<li><a href="{EXPLAINERS}/{html.escape(str(e["id"]), quote=True)}.html">'
            f'{html.escape(str(e.get("title") or e["id"]))}</a> <span style="color: var(--muted)">'
            f'{"explain" if e.get("mode") == "explain" else "search"}'
            f'{" · written against an earlier graph" if e.get("changed") else ""}</span></li>'
            for e in sorted(entries, key=lambda e: str(e["id"])))
        block = ('<section class="explainers"><h2>Explainers</h2><p>Design rationale that coding agents wrote '
                 f'against this space.</p><ul>{items}</ul></section>')
    new = INDEX_REGION.sub(lambda _: f"<!-- explainers -->{block}<!-- /explainers -->", text, count=1)
    if new != original:
        index.write_text(new, encoding="utf-8")
    return True
