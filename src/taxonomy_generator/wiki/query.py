"""Read-only queries over an exported design space (``raw/graph.json``), for people and coding agents.

Pure functions, no LLM calls. Every function returns plain JSON-ready data; ``ddspace query`` prints it as
JSON or as a table. A node is given by id (``d:3``, ``v:3.1``, ``s:s01``), by slug or href
(``concepts/replica-placement``), or by its label (exact, case-insensitive; or a unique partial match).
"""

from __future__ import annotations

import difflib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from taxonomy_generator.wiki.model import GRAPH_SCHEMA_VERSION, source_of

SCHEMA_VERSION = GRAPH_SCHEMA_VERSION
KIND_PREFIX = {"dimension": "d:", "value": "v:", "source": "s:", "system": "y:", "design": "p:"}
STANCES = ("accepts", "rejects", "supports", "both")

Graph = Dict[str, Any]


class QueryError(Exception):
    """The graph file is missing or unreadable."""


class NotFound(QueryError):
    """No single node matches; ``candidates`` lists the ambiguous or close matches."""

    def __init__(self, ref: str, candidates: Sequence[Mapping[str, Any]], ambiguous: bool = False):
        """Record what was asked for and what came close."""
        self.ref, self.candidates, self.ambiguous = ref, [_brief(c) for c in candidates], ambiguous
        what = "matches several nodes" if ambiguous else "matches nothing"
        hint = ("; did you mean: " + ", ".join(f"{c['label']} ({c['id']})" for c in self.candidates)
                if self.candidates else "")
        super().__init__(f"'{ref}' {what}{hint}")


# ---------------------------------------------------------------- loading and lookup


def load(path: Path) -> Graph:
    """Load ``raw/graph.json`` and index it."""
    path = Path(path)
    if not path.is_file():
        raise QueryError(f"No {path}. Build the wiki first (`ddspace wiki build`), or re-export an older wiki: "
                         "exports before the query commands did not write raw/graph.json.")
    graph = json.loads(path.read_text(encoding="utf-8"))
    if graph.get("schema_version") != SCHEMA_VERSION:
        raise QueryError(f"{path} has schema version {graph.get('schema_version')}, expected {SCHEMA_VERSION}; "
                         "re-export the wiki.")
    graph["_by_id"] = {n["id"]: n for n in graph.get("nodes") or []}
    return graph


def load_corpus(path: Path) -> Dict[str, Dict[str, Any]]:
    """Load a corpus JSON as ``{passage id: passage}`` (for ``--quotes``)."""
    return {str(p.get("id")): p for p in json.loads(Path(path).read_text(encoding="utf-8"))}


def node(graph: Graph, node_id: str) -> Dict[str, Any]:
    """Return a node by its exact id."""
    try:
        return graph["_by_id"][node_id]
    except KeyError:
        raise NotFound(node_id, []) from None


def _brief(n: Mapping[str, Any]) -> Dict[str, Any]:
    return {"id": n.get("id"), "kind": n.get("kind"), "label": n.get("label"), "href": n.get("href")}


def _norm(text: Any) -> str:
    return " ".join(str(text or "").split()).casefold()


def _nodes(graph: Graph, kinds: Optional[Iterable[str]]) -> List[Dict[str, Any]]:
    wanted = set(kinds or KIND_PREFIX)
    return [n for n in graph.get("nodes") or [] if n.get("kind") in wanted]


def resolve(graph: Graph, ref: str, kinds: Optional[Sequence[str]] = None) -> Dict[str, Any]:
    """Return the one node ``ref`` names (id, slug/href or label); raise ``NotFound`` otherwise."""
    pool = _nodes(graph, kinds)
    ref_s, key = str(ref).strip(), _norm(ref)
    if re.fullmatch(r"(s:)?s0*\d+", ref_s):  # sources: s01, s1 and s:s1 are the same
        ref_s = "s:" + source_of(ref_s.removeprefix("s:") + "_p1")
    steps = [
        lambda n: n["id"] == ref_s or any(n["id"] == p + ref_s for p in KIND_PREFIX.values()),
        lambda n: n.get("href") == ref_s.strip("/") or str(n.get("href", "")).rsplit("/", 1)[-1] == ref_s,
        lambda n: _norm(n.get("label")) == key,
        lambda n: key and key in _norm(n.get("label")),
    ]
    for match in steps:
        found = [n for n in pool if match(n)]
        if len(found) == 1:
            return found[0]
        if len(found) > 1:
            raise NotFound(ref_s, found, ambiguous=True)
    labels = {_norm(n.get("label")): n for n in pool}
    close = difflib.get_close_matches(key, list(labels), n=5, cutoff=0.6)
    raise NotFound(ref_s, [labels[c] for c in close])


def _edges(graph: Graph, etype: Optional[str] = None) -> List[Dict[str, Any]]:
    return [e for e in graph.get("edges") or [] if etype is None or e.get("type") == etype]


def _values_of(graph: Graph, dim_id: str) -> List[Dict[str, Any]]:
    return [n for n in graph.get("nodes") or [] if n.get("kind") == "value" and n.get("dimension_id") == dim_id]


def _value_summary(v: Mapping[str, Any]) -> Dict[str, Any]:
    docs = [p["doc"] for p in v.get("passages") or []]
    return {**_brief(v), "status": v.get("status"), "description": v.get("description", ""),
            "sources": len({source_of(d) for d in docs}), "passages": len(docs)}


# ---------------------------------------------------------------- commands


def info(graph: Graph) -> Dict[str, Any]:
    """Return the run, use case, core rule and counts."""
    count = defaultdict(int)
    for n in graph.get("nodes") or []:
        count[n.get("kind")] += 1
    return {
        "name": graph.get("name"), "run": graph.get("run"), "view": graph.get("view"),
        "use_case": graph.get("use_case", ""), "core_rule": graph.get("core_rule"),
        "schema_version": graph.get("schema_version"),
        "counts": {"dimensions": count["dimension"], "core_dimensions": sum(
                       bool(n.get("core")) for n in _nodes(graph, ["dimension"])),
                   "values": count["value"], "sources": count["source"], "systems": count["system"],
                   "design_points": count["design"], "relations": len(_edges(graph, "relation"))},
    }


def dims(graph: Graph, core_only: bool = False) -> List[Dict[str, Any]]:
    """Return the dimensions with value counts, evidence, relation count and core flag."""
    out = []
    for d in _nodes(graph, ["dimension"]):
        if core_only and not d.get("core"):
            continue
        values = _values_of(graph, d["id"])
        out.append({**_brief(d), "description": d.get("description", ""), "core": bool(d.get("core")),
                    "values": len(values),
                    "candidate_values": sum(v.get("status") != "outcome" for v in values),
                    "outcomes": sum(v.get("status") == "outcome" for v in values),
                    "evidence": d.get("evidence") or {},
                    "relations": sum(d["id"] in (e["source"], e["target"]) for e in _edges(graph, "relation"))})
    return out


def values(graph: Graph, dimension: str, status: Optional[str] = None) -> Dict[str, Any]:
    """Return a dimension's values (optionally only one status: accepted, rejected, mixed, outcome)."""
    d = resolve(graph, dimension, ["dimension"])
    vals = [_value_summary(v) for v in _values_of(graph, d["id"]) if status is None or v.get("status") == status]
    return {"dimension": {**_brief(d), "description": d.get("description", "")}, "values": vals}


def evidence(graph: Graph, value: str, stance: Optional[str] = None,
             corpus: Optional[Mapping[str, Mapping[str, Any]]] = None) -> Dict[str, Any]:
    """Return a value's supporting passage ids grouped by source, with each passage's stance.

    ``stance`` keeps only passages with that stance (``both`` counts as accepts and rejects). With
    ``corpus``, each passage also carries its ``text``.
    """
    v = resolve(graph, value, ["value"])
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for p in v.get("passages") or []:
        if stance and not (p["stance"] == stance or (p["stance"] == "both" and stance in ("accepts", "rejects"))):
            continue
        entry = {"id": p["doc"], "stance": p["stance"]}
        if corpus is not None:
            entry["text"] = (corpus.get(p["doc"]) or {}).get("content", "")
        grouped[source_of(p["doc"])].append(entry)
    sources = []
    for sid, passages in grouped.items():
        s = graph["_by_id"].get("s:" + sid) or {"id": "s:" + sid, "label": sid}
        sources.append({**_brief(s), "url": s.get("url", ""), "passages": passages})
    return {"value": {**_brief(v), "status": v.get("status"), "dimension": v.get("dimension"),
                      "dimension_id": v.get("dimension_id"), "description": v.get("description", "")},
            "sources": sources}


def show(graph: Graph, ref: str) -> Dict[str, Any]:
    """Return one node with all its fields and its neighbors grouped by edge type."""
    n = resolve(graph, ref)
    neighbors: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for e in graph.get("edges") or []:
        if n["id"] not in (e["source"], e["target"]):
            continue
        out = e["source"] == n["id"]
        other = graph["_by_id"].get(e["target"] if out else e["source"])
        if other is None:
            continue
        extra = {k: v for k, v in e.items() if k not in ("source", "target", "type")}
        neighbors[e["type"]].append({**_brief(other), "direction": "out" if out else "in", **extra})
    return {"node": {k: v for k, v in n.items()}, "neighbors": dict(neighbors)}


def relations(graph: Graph, frm: Optional[str] = None, rtype: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return relations between dimensions, each with its reading sentence.

    ``frm`` keeps relations going out of that dimension (and undirected ones that touch it).
    """
    start = resolve(graph, frm, ["dimension"])["id"] if frm else None
    out = []
    for e in _edges(graph, "relation"):
        if rtype and e.get("relation") != rtype:
            continue
        if start and not (e["source"] == start or (not e.get("directed", True) and e["target"] == start)):
            continue
        src, tgt = graph["_by_id"].get(e["source"], {}), graph["_by_id"].get(e["target"], {})
        out.append({"source": _brief(src), "target": _brief(tgt), "type": e.get("relation"),
                    "directed": e.get("directed", True), "reading": e.get("reading", "")})
    return out


def search(graph: Graph, text: str, kind: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return nodes whose label (first) or description contains ``text`` (case-insensitive)."""
    key = _norm(text)
    pool = _nodes(graph, [kind] if kind else None)
    by_label = [{**_brief(n), "match": "label"} for n in pool if key in _norm(n.get("label"))]
    by_desc = [{**_brief(n), "match": "description"} for n in pool
               if key not in _norm(n.get("label")) and key in _norm(n.get("description"))]
    return by_label + by_desc
