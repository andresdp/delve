"""Render a checked design rationale file (``ddspace-rationale/6``) as an explainer page.

The page sits at ``<html dir>/explainers/<id>.html``, next to the wiki's HTML, or in a standalone folder
(``<out>/explainers/<id>.html`` with its own ``assets/``). It shows the requirements, one tab per alternative
plus a compare view, a radial subgraph of the dimensions involved, a details panel and, for explain, the
uncovered decisions. With a space, dimensions, values and sources link to their wiki pages (a page that does
not exist is shown without a link); evidence is passage ids with stances, never quotes (``raw/graph.json``
holds no passage text). A zero-shot file (``space: null``, ids that are the agent's own names: ``Storage``,
``Storage: Local disks``) is drawn from the names it uses, with no wiki links and no sources.

The caller checks the file first (``delvedspace.rationale.check``): this module assumes a clean file.
"""

from __future__ import annotations

import html
import json
import os
import re
import shutil
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from taxonomy_generator.wiki.llm_texts import TRADEOFF_MARK
from taxonomy_generator.wiki.query import label_node, norm
from taxonomy_generator.wiki.render import TEMPLATES, _env, copy_images, copy_page_assets

LAYOUT_SCRIPT = TEMPLATES / "graph-layout.js"

EXPLAINERS = "explainers"
GAP_REASONS = {"no_dimension": "the space has no dimension for it",
               "traded_off": "traded off for a stronger requirement",
               "budget": "the budget ran out before a point addressed it",
               "not_in_solution": "the solution does not address it"}
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

def _zero_shot(doc: Mapping[str, Any]) -> bool:
    """A file written without a space (``space: null``) whose steps name values by name, not as old-schema objects."""
    return "space" in doc and doc["space"] is None and any(
        isinstance(v, str) for s in doc.get("trajectory") or [] if isinstance(s, dict) for v in s.get("values") or [])


def label_graph(doc: Mapping[str, Any]) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """Return a zero-shot file's dimensions and values shaped like a wiki graph, and ``{name: node id}``.

    The ids the file uses are names (``Storage``, ``Storage: Local disks``, see ``query.label_node``); the
    nodes get short ids (``z:1``, ``z:1.2``) in the order the file first names them, so the page never puts the
    agent's text in an id. The relations the alternatives claim become the graph's relations.
    """
    nodes: List[Dict[str, Any]] = []
    alias: Dict[str, str] = {}
    counts: Dict[str, int] = {}

    def dimension(name: str) -> str:
        n = label_node(name, ["dimension"])
        if n is None:
            return ""
        if n["id"] not in alias:
            alias[n["id"]] = f"z:{len(counts) + 1}"
            counts[n["id"]] = 0
            nodes.append({"id": alias[n["id"]], "kind": "dimension", "label": n["label"]})
        alias.setdefault(name, alias[n["id"]])
        return alias[n["id"]]

    def value(ref: Any) -> None:
        n = label_node(ref, ["value"])
        if n is None or n["kind"] != "value":
            return
        did = dimension(n["dimension_id"])
        if n["id"] not in alias:
            counts[n["dimension_id"]] += 1
            alias[n["id"]] = f"{did}.{counts[n['dimension_id']]}"
            nodes.append({"id": alias[n["id"]], "kind": "value", "label": n["label"], "dimension_id": did})
        alias.setdefault(ref, alias[n["id"]])

    for s in doc.get("trajectory") or []:
        for v in (s.get("values") or []) if isinstance(s, dict) else []:
            value(v)
    for alt in doc.get("alternatives") or []:
        if not isinstance(alt, dict):
            continue
        for key in ("choices", "considered"):
            for c in alt.get(key) or []:
                if isinstance(c, dict):
                    if isinstance(c.get("dimension_id"), str):
                        dimension(c["dimension_id"])
                    value(c.get("value_id"))
        for o in alt.get("open") or []:
            if isinstance(o, dict) and isinstance(o.get("dimension_id"), str):
                dimension(o["dimension_id"])
    for item in [*(doc.get("points") or []), *(doc.get("regions") or []),
                 *(o for r in doc.get("adrs") or [] if isinstance(r, dict) for o in r.get("options") or [])]:
        for v in (item.get("values") or []) if isinstance(item, dict) else []:
            value(v)
    for item in doc.get("comparison") or []:
        if isinstance(item, dict) and isinstance(item.get("dimension_id"), str):
            dimension(item["dimension_id"])
    edges, seen = [], set()
    for alt in doc.get("alternatives") or []:
        for r in (alt.get("relations") or []) if isinstance(alt, dict) else []:
            if not isinstance(r, dict) or not all(isinstance(r.get(k), str) for k in ("source", "target", "type")):
                continue
            s, t_ = dimension(r["source"]), dimension(r["target"])
            if s and t_ and (s, t_, r["type"]) not in seen:
                seen.add((s, t_, r["type"]))
                edges.append({"source": s, "target": t_, "type": "relation", "relation": r["type"], "directed": True})
    return {"nodes": nodes, "edges": edges}, alias


class _Space:
    """The dimensions and values the file touches, from the wiki's graph or from a zero-shot file's names.

    ``wiki`` says whether they come from a wiki (with links and sources). Files of an older schema without any
    space (``space: null``, choices naming ``decision`` and ``option``) are still drawn from the file.
    """

    def __init__(self, doc: Mapping[str, Any], graph: Optional[Mapping[str, Any]], link: Link):
        meta = doc.get("space")
        self.wiki = isinstance(meta, dict) and graph is not None
        self._alias: Dict[str, str] = {}  # zero-shot: the file's names -> node ids
        if _zero_shot(doc):
            (graph, self._alias), link = label_graph(doc), (lambda _target: None)
        self.graph, self.link = graph, link
        self.with_space = (isinstance(meta, dict) or bool(self._alias)) and graph is not None
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

    def _id(self, ref: Any) -> Any:
        """The node id of an id the file uses (a zero-shot name maps to its node's id)."""
        return self._alias.get(ref, ref) if isinstance(ref, str) else ref

    def node(self, ref: Any) -> Optional[Dict[str, Any]]:
        """Return the graph node with id ``ref`` (None without a space or when there is none)."""
        return self._by_id.get(self._id(ref))

    def dim(self, ref: Any) -> Optional[str]:
        """Register and return the id of the dimension a choice names (a graph id, or the agent's decision)."""
        if ref is None or ref == "":
            return None
        if self.with_space:
            ref = self._id(ref)
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
            ref = self._id(ref)
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
                n = self.node(item) if isinstance(item, str) else None
                d = self.dim(n.get("dimension_id")) if n is not None and n.get("kind") == "value" else None
                v = self.value(d, item)
            elif isinstance(item, dict):
                d, v = self.names(item)
            else:
                d = v = None
            if d is not None and v is not None and d not in out:
                out[d] = v
        return out



def split_tradeoff(description: str) -> Tuple[str, str]:
    """Split a point's description into what the point is and its own trade-off (after ``Trade-off:``)."""
    body, mark, tail = description.partition(TRADEOFF_MARK)
    return (body.strip(), tail.strip()) if mark else (description, "")


def _tradeoffs(step: Mapping[str, Any], space: "_Space") -> List[Dict[str, Any]]:
    """A step's trade-offs against the requirements: the values that cause each (``causes``, resolved like the
    step's point; not ``values``, which a template would read as the dict method), the requirement ids it gains
    and costs, and a note."""
    def ids(xs: Any) -> List[str]:
        return [x for x in xs if isinstance(x, str)] if isinstance(xs, list) else []
    return [{"causes": list(space.point(ids(t.get("values"))).values()), "gains": ids(t.get("gains")),
             "costs": ids(t.get("costs")), "note": str(t.get("note") or "")}
            for t in step.get("tradeoffs") or [] if isinstance(t, dict)]

def _trajectory(doc: Mapping[str, Any], space: _Space, alternatives: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """The steps the agent took, each with its point and what changed against its parent (or what was new)."""
    steps: List[Dict[str, Any]] = []
    by_number: Dict[Any, Dict[str, Any]] = {}
    seen: set = set()
    proposed = {a["step"]: a["id"] for a in alternatives if a.get("step") is not None}
    listed = {p.get("id"): p for p in doc.get("points") or [] if isinstance(p, dict)}  # the evaluated design points
    first_step: Dict[Any, Any] = {}  # point id -> the first step that evaluated it
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
        record = s.get("point") if isinstance(s.get("point"), dict) else listed.get(s.get("point")) or {}
        attested = []
        for ref in record.get("attested_by") or []:
            sid = ref.get("id") if isinstance(ref, dict) else ref
            n = space.node(sid) if isinstance(sid, str) else None
            attested.append({"id": str(sid), "label": (n or {}).get("label") or str(sid),
                             "href": space.link((n or {}).get("href") or "") if n else None})
        assessment = s.get("assessment") if isinstance(s.get("assessment"), dict) else {}
        description, own_tradeoff = split_tradeoff(record.get("description") or "")
        step = {"step": s.get("step"), "move": s.get("move") or "", "parent": s.get("parent"),
                "round": s.get("round"), "approach": s.get("approach"),
                "why": s.get("hypothesis") or s.get("why") or "", "observation": s.get("observation") or "",
                "verdict": s.get("rating") or s.get("verdict") or "", "assessment": dict(assessment),
                "drivers": list(assessment) or list(s.get("drivers") or []),
                "point": point, "changed": changed, "novel": novel,
                "description": description, "own_tradeoff": own_tradeoff, "tradeoffs": _tradeoffs(s, space),
                "attested_by": attested,
                "alternative": proposed.get(s.get("step")),
                "point_id": s.get("point") if isinstance(s.get("point"), str) else None,
                "reuses": first_step.get(s.get("point")) if isinstance(s.get("point"), str) else None}
        if isinstance(s.get("point"), str):
            first_step.setdefault(s["point"], s.get("step"))
        steps.append(step)
        by_number[s.get("step")] = step
    return steps


def _diff(point: Mapping[str, str], before: Mapping[str, str]) -> List[Dict[str, Any]]:
    """What a step changed against its parent: ``{dimension, before, after}`` (None: not in that point)."""
    order = list(point) + [d for d in before if d not in point]
    return [{"dimension": d, "before": before.get(d), "after": point.get(d)}
            for d in order if before.get(d) != point.get(d)]


def _lanes(doc: Mapping[str, Any], trajectory: Sequence[Mapping[str, Any]],
           alternatives: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    """Search's overview: one lane per approach, one column per round, each cell the steps it took there."""
    rounds = sorted({s["round"] for s in trajectory if isinstance(s.get("round"), int)})
    listed = [a for a in doc.get("approaches") or [] if isinstance(a, dict) and a.get("id")]
    order = [str(a["id"]) for a in listed]
    order += [s["approach"] for s in trajectory if s.get("approach") and s["approach"] not in order]
    info = {str(a["id"]): a for a in listed}
    became = {a.get("approach"): a["id"] for a in alternatives if a.get("approach")}
    lanes = []
    for ap in order:
        cells = {r: [{"step": s["step"], "move": s["move"], "verdict": s["verdict"], "why": s["why"]}
                     for s in trajectory if s.get("approach") == ap and s.get("round") == r] for r in rounds}
        a = info.get(ap, {})
        lanes.append({"approach": ap, "idea": a.get("idea") or "", "status": a.get("status") or "",
                      "dropped_because": a.get("dropped_because") or "", "alternative": became.get(ap), "cells": cells})
    return {"rounds": rounds, "lanes": lanes}


def _qoc(trajectory: Sequence[Mapping[str, Any]], alternatives: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """Explain's Questions-Options-Criteria view: each dimension of the solution (a question), its options (the
    solution's value and the values contrasts tried), each judged against the requirements (the criteria) by the
    most specific step that evaluated it."""
    solution = next((s for s in trajectory if s["move"] == "solution"), None)
    if solution is None:
        return []
    forced = {c["value"]: c.get("forced") for a in alternatives for c in a["choices"] if c["value"]}
    questions = []
    for dim, value in solution["point"].items():
        regions = [s for s in trajectory if s["move"] == "region" and s["point"].get(dim) == value]
        judge = min(regions, key=lambda s: len(s["point"])) if regions else solution
        options = [{"value": value, "kind": "solution", "forced": forced.get(value), "step": judge["step"],
                    "assessment": judge["assessment"], "specific": judge is not solution}]
        for s in trajectory:
            other = s["point"].get(dim)
            if s["move"] == "contrast" and other and other != value and all(o["value"] != other for o in options):
                options.append({"value": other, "kind": "contrast", "forced": None, "step": s["step"],
                                "assessment": s["assessment"], "specific": True})
        questions.append({"dimension": dim, "options": options})
    return questions


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
                            "forced": c.get("forced"), "fit": c.get("fit") or "exact",
                            "fit_note": c.get("fit_note") or "",
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
    for s in trajectory:
        parent = by_step.get(s["parent"]) if s["parent"] is not None else None
        s["diff"] = _diff(s["point"], parent["point"] if parent else {})
    for alt in alternatives:
        alt["point"] = (by_step.get(alt["step"]) or {}).get("description") or ""
    regions = []
    for r in doc.get("regions") or []:
        if isinstance(r, dict):
            regions.append({"id": str(r.get("id")), "name": r.get("name") or str(r.get("id")),
                            "point": space.point(r.get("values")), "step": r.get("step"),
                            "drivers": list(r.get("drivers") or []), "reason": r.get("reason") or ""})
    # The ADRs: each with its options as partial points; the requirements no ADR and no choice addresses.
    adrs = []
    for r in doc.get("adrs") or []:
        if not isinstance(r, dict):
            continue
        options = [{"id": str(o.get("id")), "key": f"{r.get('id')}:{o.get('id')}", "name": o.get("name") or "",
                    "point": space.point(o.get("values")), "status": o.get("status") or "",
                    "in": [str(x) for x in o.get("in") or []], "pros": [str(x) for x in o.get("pros") or []],
                    "cons": [str(x) for x in o.get("cons") or []], "reason": o.get("reason") or "",
                    "step": o.get("step"), "fit": o.get("fit") or "exact", "fit_note": o.get("fit_note") or ""}
                   for o in r.get("options") or [] if isinstance(o, dict)]
        adrs.append({"id": str(r.get("id")), "title": r.get("title") or "", "drivers": list(r.get("drivers") or []),
                     "context": r.get("context") or "", "consequences": r.get("consequences") or "",
                     "options": options})
    quotes = {c["value"]: c["quote"] for a in alternatives for c in a["choices"] if c["value"] and c["quote"]}
    for r in adrs:  # explain: a chosen option shows the solution's own words for its values
        for o in r["options"]:
            o["quotes"] = list(dict.fromkeys(quotes[v] for v in o["point"].values()
                                             if o["status"] == "chosen" and v in quotes))  # each quote once
    # Each alternative is composed of the partial design points its ADRs choose for it: one part per chosen option.
    for alt in alternatives:
        alt["parts"] = [{"adr": r["id"], "title": r["title"], "option": o["id"], "name": o["name"], "point": o["point"],
                         "drivers": r["drivers"]}
                        for r in adrs for o in r["options"] if o["status"] == "chosen" and alt["id"] in o["in"]]
    # The gaps in the space: requirements no ADR addresses (with the file's reason), and approximate fits.
    def nearest(near: Any) -> Optional[Dict[str, Any]]:
        n = space.node(near) if near else None
        if not n:
            return None
        return {"id": near, "label": n.get("label") or near,
                "href": link(n.get("href") or "") if space.wiki else ""}

    listed = {u.get("requirement"): u for u in doc.get("unaddressed") or [] if isinstance(u, dict)}
    addressed = {d for r in adrs for d in r["drivers"]}
    unaddressed = []
    for r in problem.get("requirements") or []:
        rid = r.get("id")
        if rid in addressed and rid not in listed:
            continue
        u = listed.get(rid) or {}
        unaddressed.append({"id": rid, "text": r.get("text") or "", "reason": u.get("reason") or "",
                            "reason_text": GAP_REASONS.get(u.get("reason") or "", "no reason given"),
                            "nearest": nearest(u.get("nearest_dimension_id")), "note": u.get("note") or ""})
    loose = {c["value"] for a in alternatives for c in a["choices"] if c["fit"] == "approximate"}

    def narrowed(point: Mapping[str, str]) -> Dict[str, str]:
        """The values of an approximate option that the choices mark approximate too (all of them when none)."""
        return {d: v for d, v in point.items() if v in loose} or dict(point)

    fits = [{"where": f"{r['id']} · {o['name']}", "option": o["key"], "alt": None, "point": narrowed(o["point"]),
             "note": o["fit_note"]} for r in adrs for o in r["options"] if o["fit"] == "approximate"]
    in_options = {v for f in fits for v in f["point"].values()}
    fits += [{"where": f"{a['id']} · {a['name']}", "option": None, "alt": a["id"], "point": {c["dimension"]: c["value"]},
              "note": c["fit_note"]} for a in alternatives for c in a["choices"]
             if c["fit"] == "approximate" and c["dimension"] and c["value"] not in in_options]
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

    uncovered = [{"decision": u.get("decision") or "", "quote": u.get("solution_quote") or "",
                  "nearest": nearest(u.get("nearest_dimension_id"))}
                 for u in doc.get("uncovered") or [] if isinstance(u, dict)]

    meta = doc.get("space") if isinstance(doc.get("space"), dict) else None
    return {
        "id": str(doc.get("id")), "mode": doc.get("mode"), "with_space": with_space, "wiki": space.wiki,
        "title": problem.get("title") or str(doc.get("id")), "context": problem.get("context") or "",
        "inferred": problem.get("inferred") is True,
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
        "adrs": adrs, "unaddressed": unaddressed, "fits": fits,
        "lanes": _lanes(doc, trajectory, alternatives) if doc.get("mode") != "explain" else None,
        "qoc": _qoc(trajectory, alternatives) if doc.get("mode") == "explain" else [],
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
    # A wiki exported before the shared layout script existed, or before its current version, lacks what the page
    # calls: it would draw no graph, or the old layout, until the next export. Refresh the script alone (it stays
    # compatible with the wiki's graph page); the export owns the other assets.
    layout = Path(root) / "assets" / "graph-layout.js"
    if layout.parent.is_dir() and (not layout.is_file() or layout.read_bytes() != LAYOUT_SCRIPT.read_bytes()):
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
