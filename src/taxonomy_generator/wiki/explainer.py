"""Render a checked design rationale file (``ddspace-rationale/1``) as an explainer page.

The page sits at ``<html dir>/explainers/<id>.html``, next to the wiki's HTML, or in a standalone folder
(``<out>/explainers/<id>.html`` with its own ``assets/``). It shows the requirements, one tab per alternative
plus a compare view, a radial subgraph of the dimensions involved, a details panel and, for explain, the
uncovered decisions. With a space, dimensions, values and sources link to their wiki pages (a page that does
not exist is shown without a link); evidence is passage ids with stances, never quotes (``raw/graph.json``
holds no passage text). Without a space (``space: null``), the page draws the agent's own decisions and
options and has no wiki links.

The caller checks the file first (``delvedspace.rationale.check``): this module assumes a clean file.
"""

from __future__ import annotations

import html
import importlib.resources
import json
import os
import re
import shutil
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence

from taxonomy_generator.wiki.render import TEMPLATES, _env, copy_images

EXPLAINERS = "explainers"
Link = Callable[[str], Optional[str]]  # a wiki page path (``concepts/x``) or file (``index.html``) -> href or None


def _norm(text: Any) -> str:
    return " ".join(str(text or "").split()).casefold()


def wiki_links(wiki_html: Optional[Path], page_dir: Path) -> Link:
    """Return a function giving the href from ``page_dir`` to a wiki page, or None when it has no page."""
    def link(target: str) -> Optional[str]:
        if wiki_html is None or not target:
            return None
        name = target if target.endswith(".html") else f"{target}.html"
        path = Path(wiki_html) / name
        if not path.is_file():
            return None
        return Path(os.path.relpath(path.resolve(), Path(page_dir).resolve())).as_posix()
    return link


# ── page data ────────────────────────────────────────────────────────────

class _Space:
    """The dimensions and values the file touches, from the graph (with a space) or from the file (without)."""

    def __init__(self, doc: Mapping[str, Any], graph: Optional[Mapping[str, Any]], link: Link):
        self.graph, self.link = graph, link
        self.with_space = isinstance(doc.get("space"), dict) and graph is not None
        self.dims: Dict[str, Dict[str, Any]] = {}
        self.values: Dict[str, Dict[str, Any]] = {}
        self._by_id = {n["id"]: n for n in (graph or {}).get("nodes") or []} if self.with_space else {}
        self._keys: Dict[str, str] = {}  # without a space: normalized label -> made-up id

    def dim(self, ref: Any) -> Optional[str]:
        """Register and return the id of the dimension a choice names (a graph id, or the agent's decision)."""
        if ref is None or ref == "":
            return None
        if self.with_space:
            n = self._by_id.get(ref)
            if n is None or n.get("kind") != "dimension":
                return None
            if ref not in self.dims:
                self.dims[ref] = {"id": ref, "label": n.get("label", ref), "question": n.get("description") or "",
                                  "href": self.link(n.get("href") or ""), "core": bool(n.get("core")), "values": []}
                for v in (x for x in self._by_id.values() if x.get("kind") == "value" and x.get("dimension_id") == ref):
                    self._value_node(v)
            return ref
        key = _norm(ref)
        if key not in self._keys:
            self._keys[key] = f"x:{len(self._keys) + 1}"
            self.dims[self._keys[key]] = {"id": self._keys[key], "label": str(ref).strip(), "question": "",
                                          "href": None, "core": False, "values": []}
        return self._keys[key]

    def _value_node(self, v: Mapping[str, Any]) -> None:
        sources = []
        for e in (self.graph or {}).get("edges") or []:
            if e.get("type") == "evidence" and e.get("target") == v["id"] and e.get("source") in self._by_id:
                s = self._by_id[e["source"]]
                sources.append({"id": s["id"], "label": s.get("label", s["id"]), "stance": e.get("stance", ""),
                                "href": self.link(s.get("href") or "")})
        self.values[v["id"]] = {"id": v["id"], "label": v.get("label", v["id"]), "dimension": v["dimension_id"],
                                "status": v.get("status", ""), "description": v.get("description") or "",
                                "href": self.link(v.get("href") or ""),
                                "passages": [{"doc": p.get("doc"), "stance": p.get("stance", "")}
                                             for p in v.get("passages") or []],
                                "sources": sources}
        self.dims[v["dimension_id"]]["values"].append(v["id"])

    def value(self, dim: Optional[str], ref: Any) -> Optional[str]:
        if dim is None or ref is None:
            return None
        if self.with_space:
            return ref if ref in self.values else None
        key = f"{dim}::{_norm(ref)}"
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
                            "evidence": [{"doc": e.get("doc"), "stance": e.get("stance", "")}
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
                             "open": open_, "relations": relations,
                             "point": (alt.get("point") or {}).get("description") or ""})

    notes = {}
    for item in doc.get("comparison") or []:
        d = space.decision(item)
        if d is not None:
            notes[d] = item.get("note") or ""

    # Which values each alternative chose or considered; every other value is "offered by the space".
    for v in space.values.values():
        v["roles"] = {}
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
        for e in graph.get("edges") or []:
            if e.get("type") == "relation" and e.get("source") in ids and e.get("target") in ids:
                relations.append({"source": e["source"], "target": e["target"], "type": e.get("relation", ""),
                                  "directed": e.get("directed") is not False, "reading": e.get("reading", "")})

    uncovered = []
    for u in doc.get("uncovered") or []:
        near = u.get("nearest_dimension_id")
        n = space._by_id.get(near) if with_space and near else None
        uncovered.append({"decision": u.get("decision") or "", "quote": u.get("solution_quote") or "",
                          "nearest": ({"id": near, "label": n.get("label", near), "href": link(n.get("href") or "")}
                                      if n else None)})

    meta = doc.get("space") if isinstance(doc.get("space"), dict) else None
    return {
        "id": str(doc.get("id")), "mode": doc.get("mode"), "with_space": with_space,
        "title": problem.get("title") or str(doc.get("id")), "context": problem.get("context") or "",
        "space": {"workspace": meta.get("workspace"), "run": meta.get("run"),
                  "domain": (graph or {}).get("domain") or (graph or {}).get("name") or meta.get("workspace")}
        if meta else None,
        "graph_changed": graph_changed,
        "requirements": [{"id": r.get("id"), "text": r.get("text") or "", "kind": r.get("kind") or "",
                          "attribute": r.get("attribute") or ""} for r in problem.get("requirements") or []],
        "alternatives": alternatives, "dimensions": space.dims, "values": space.values, "rows": rows,
        "relations": relations, "uncovered": uncovered,
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
    data = page_data(doc, graph, wiki_links(wiki_html, page.parent), graph_changed)
    page.write_text(_render(data), encoding="utf-8")
    return page


def copy_assets(root: Path) -> None:
    """Copy what the page loads (d3, the stylesheet, the icons) into ``<root>/assets``, so it opens offline."""
    assets = Path(root) / "assets"
    copy_images(assets, None)
    shutil.copyfile(TEMPLATES / "style.css", assets / "style.css")
    d3 = importlib.resources.files("taxonomy_generator") / "assets" / "d3.min.js"
    (assets / "d3.min.js").write_text(d3.read_text(encoding="utf-8"), encoding="utf-8")


def write_standalone(doc: Mapping[str, Any], graph: Optional[Mapping[str, Any]], out: Path, *,
                     wiki_html: Optional[Path] = None, graph_changed: bool = False) -> Path:
    """Write ``<out>/explainers/<id>.html`` and ``<out>/assets/``; links (if any) point into ``wiki_html``."""
    copy_assets(out)
    return write_page(doc, graph, out, wiki_html=wiki_html, graph_changed=graph_changed)


# ── the index's list of explainers ───────────────────────────────────────

INDEX_REGION = re.compile(r"<!-- explainers -->.*?<!-- /explainers -->", re.S)


def write_index(html_root: Path, entries: Sequence[Mapping[str, Any]]) -> bool:
    """Write the "Explainers" list into ``<html_root>/index.html`` (empty when there are none).

    ``entries`` are ``{id, title, mode, changed}`` of the rendered pages. The list sits in a marked region of the
    HTML index only (``wiki/index.md`` is left alone). Returns False when the index has no such region.
    """
    index = Path(html_root) / "index.html"
    try:
        text = index.read_text(encoding="utf-8")
    except OSError:
        return False
    if not INDEX_REGION.search(text):
        return False
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
    if new != text:
        index.write_text(new, encoding="utf-8")
    return True
