"""The design rationale file (``ddspace-rationale/5``) and its checker, with no ``jsonschema`` dependency.

A dimension is a design concern, a value one option for it, and a design point a set of values, at most one per
dimension. A coding agent writes one rationale file per problem, with the ``trajectory`` of design points it
evaluated (at most ``budget.max_points``). Each step records its ``hypothesis``, its ``assessment`` (``meets``,
``partly`` or ``misses`` per requirement) and its ``observation``.

*Search* works in rounds over ``approaches`` (each a "what if" idea, ``live`` or ``dropped``): its steps
(``seed``, ``exploit``, ``explore``, ``ablate``) carry a ``round``, an ``approach`` and a ``rating`` (``strong``,
``mixed``, ``weak``), and it proposes the best point of two to four live approaches as ``alternatives``, with what
each one ``considered``, left ``open`` and claims about ``relations``, plus a ``comparison``. *Explain* maps the
given solution to one point (the ``solution`` step and the alternative ``id: "S"``, whose choices quote the
solution and say whether the requirements ``force`` them), evaluates partial points of it (``region``,
``contrast``) with a ``verdict``, and names the 1-3 ``regions`` that best justify it, plus the ``uncovered``
decisions a wiki has no dimension for.

Every design point the agent evaluated is recorded once in ``points`` (``P1``, ``P2``, ...: its values, its
description and the sources that attest it); a step names its point by id, so a point evaluated again is reused,
not described again, and a description is changed in one place.

Both modes describe their solution(s) as ``adrs``: architecture decision records, each addressing a few related
requirements (``drivers``) with ``options``, partial design points that are ``chosen`` (``in`` the alternatives
that take them) or ``discarded``, each with its ``pros`` and ``cons``. Every value an alternative takes is in a
chosen option of some ADR.

Where the space falls short, the file says so instead of forcing a fit. Every requirement is either a driver of some
ADR or listed in ``unaddressed`` with a ``reason`` (``no_dimension``: the space has no dimension for it;
``traded_off``; ``budget``; ``not_in_solution``, in explain). A choice or an ADR option whose value only roughly
matches what it stands for carries ``fit: "approximate"`` and a ``fit_note``. The agent never changes the space to
close a gap: a wiki is read only, and the agent's own space is fixed once written.

Every file names its values by id (``d:1``, ``v:1.2``) against a space. Either the space is a DelveDSpace wiki
(``space: {workspace, run, graph_sha256}``), and ``check`` tests the ids against ``raw/graph.json`` when it is
given the graph; or the agent built its own (``space: {dimensions, relations}``), and ``check`` tests the ids
against those. Every problem has a stable ``code`` and a JSON Pointer ``path`` into the file.
"""

from __future__ import annotations

import difflib
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from taxonomy_generator.wiki import query as q

SCHEMA = "ddspace-rationale/5"
MODES = ("search", "explain")
SEARCH_ALTERNATIVES = (2, 4)
EXPLAIN_ID = "S"
MOVES = {"search": ("seed", "exploit", "explore", "ablate"), "explain": ("solution", "region", "contrast")}
RATINGS = ("strong", "mixed", "weak")                 # a search step's rating
VERDICTS = ("grounded", "partial", "ungrounded")      # an explain step's verdict
ASSESSMENTS = ("meets", "partly", "misses")           # a step's judgment of one requirement
STATUSES = ("live", "dropped")                        # a search approach
OPTION_STATUSES = ("chosen", "discarded")             # an ADR option
UNADDRESSED_REASONS = ("no_dimension", "traded_off", "budget", "not_in_solution")  # why no ADR addresses a requirement
FITS = ("exact", "approximate")                       # how well a choice's or option's values match it
ROOT_MOVES = ("seed", "solution")                     # a step without a parent
PARENT_MOVES = ("exploit", "ablate", "region", "contrast")  # a step that needs one (explore may name one or not)
SAME_APPROACH_MOVES = ("exploit", "ablate")           # a search step that stays in its parent's approach
MAX_POINTS = {"search": 20, "explain": 12}     # the most design points a mode may evaluate
DEFAULT_POINTS = {"search": 12, "explain": 8}  # what the skills set when the user names no budget
REGIONS = (1, 3)
WARNINGS = ("unmet_requires", "graph_changed", "unused_point")

# Field specs: name -> (kind, required). Kinds: "text" (a non-empty string), "string", "string|null", "list",
# "object", "object|null", "boolean", "boolean|null", "integer", "integer|null".
_Spec = Dict[str, Tuple[str, bool]]
_TYPES = {"text": str, "string": str, "list": list, "object": dict, "boolean": bool, "integer": int}
_TOP: _Spec = {"schema": ("text", True), "id": ("text", True), "mode": ("text", True),
               "space": ("object", True), "problem": ("object", True), "budget": ("object", True),
               "trajectory": ("list", True), "alternatives": ("list", True), "adrs": ("list", True),
               "points": ("list", True), "approaches": ("list", False),
               "comparison": ("list", False), "regions": ("list", False), "uncovered": ("list", False),
               "unaddressed": ("list", True)}
_BUDGET: _Spec = {"max_points": ("integer", True)}
_STEP: _Spec = {"step": ("integer", True), "move": ("text", True), "parent": ("integer|null", False),
                "values": ("list", True), "hypothesis": ("string", True), "assessment": ("object", True),
                "observation": ("string", True), "point": ("text", True)}
_SEARCH_STEP: _Spec = {"round": ("integer", True), "approach": ("text", True), "rating": ("text", True)}
_EXPLAIN_STEP: _Spec = {"verdict": ("text", True)}
_APPROACH: _Spec = {"id": ("text", True), "idea": ("text", True), "status": ("text", True),
                    "dropped_because": ("string|null", False)}
_REGION: _Spec = {"id": ("text", True), "name": ("string", True), "values": ("list", True),
                  "step": ("integer", True), "drivers": ("list", True), "reason": ("string", True)}
_ADR: _Spec = {"id": ("text", True), "title": ("text", True), "drivers": ("list", True), "context": ("string", True),
               "options": ("list", True), "consequences": ("string", False)}
_OPTION: _Spec = {"id": ("text", True), "name": ("text", True), "values": ("list", True), "status": ("text", True),
                  "in": ("list", False), "pros": ("list", True), "cons": ("list", True), "reason": ("string", True),
                  "step": ("integer|null", False), "fit": ("text", False), "fit_note": ("string", False)}
_WIKI: _Spec = {"workspace": ("string", True), "run": ("string", True), "graph_sha256": ("text", True)}
_OWN: _Spec = {"dimensions": ("list", True), "relations": ("list", False)}
_OWN_DIMENSION: _Spec = {"id": ("text", True), "name": ("text", True), "values": ("list", True)}
_OWN_VALUE: _Spec = {"id": ("text", True), "name": ("text", True)}
_OWN_RELATION: _Spec = {"source": ("text", True), "target": ("text", True), "type": ("text", True)}
_PROBLEM: _Spec = {"title": ("text", True), "context": ("string", False), "requirements": ("list", True)}
_REQUIREMENT: _Spec = {"id": ("text", True), "text": ("text", True), "kind": ("string", False),
                       "attribute": ("string|null", False)}
_ALTERNATIVE: _Spec = {"id": ("text", True), "name": ("string", True), "summary": ("string", False),
                       "step": ("integer", True), "choices": ("list", True), "considered": ("list", False),
                       "open": ("list", False), "relations": ("list", False)}
_IDS: _Spec = {"dimension_id": ("text", True), "value_id": ("text", True)}
_CHOICE: _Spec = {**_IDS, "drivers": ("list", True), "reason": ("string", True), "evidence": ("list", False),
                  "fit": ("text", False), "fit_note": ("string", False)}
_CONSIDERED: _Spec = {**_IDS, "reason": ("string", True), "drivers": ("list", False)}
_OPEN: _Spec = {"dimension_id": ("text", True), "reason": ("string", True)}
_COMPARISON: _Spec = {"dimension_id": ("text", True), "note": ("string", True)}
_EVIDENCE: _Spec = {"doc": ("text", True), "stance": ("string", False)}
_RELATION: _Spec = {"source": ("text", True), "target": ("text", True), "type": ("text", True),
                    "holds": ("boolean", True), "note": ("string", False)}
_UNCOVERED: _Spec = {"decision": ("text", True), "solution_quote": ("text", True),
                     "nearest_dimension_id": ("string|null", False)}
_UNADDRESSED: _Spec = {"requirement": ("text", True), "reason": ("text", True),
                       "nearest_dimension_id": ("string|null", False), "note": ("string", True)}
_POINT: _Spec = {"id": ("text", True), "values": ("list", True), "description": ("string|null", True),
                 "attested_by": ("list", False)}


class RationaleError(Exception):
    """The rationale file is missing, unreadable or not JSON."""


def load(path: Path) -> Any:
    """Return the parsed rationale file; raise ``RationaleError`` when it cannot be read or parsed."""
    path = Path(path)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise RationaleError(f"No rationale file {path}.") from None
    except (OSError, UnicodeDecodeError) as exc:
        raise RationaleError(f"Cannot read {path}: {exc}") from None
    except json.JSONDecodeError as exc:
        raise RationaleError(f"{path} is not JSON: {exc}") from None


def own_space(doc: Any) -> bool:
    """Whether the file carries the agent's own space (``space.dimensions``) instead of naming a wiki."""
    return isinstance(doc, dict) and isinstance(doc.get("space"), dict) and "dimensions" in doc["space"]


def names_space(doc: Any) -> bool:
    """Whether the file names a wiki's space (``space`` is ``{workspace, run, graph_sha256}``), so it needs the graph."""
    return isinstance(doc, dict) and isinstance(doc.get("space"), dict) and not own_space(doc)


def file_sha256(path: Path) -> str:
    """Hex SHA-256 of a file's bytes (``graph_sha256`` is this, over ``raw/graph.json``)."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pointer(*parts: Any) -> str:
    """Return a JSON Pointer (RFC 6901) to ``parts`` ("" is the whole file)."""
    return "".join("/" + str(p).replace("~", "~0").replace("/", "~1") for p in parts)


def _brief(n: Mapping[str, Any]) -> Dict[str, Any]:
    return {"id": n.get("id"), "kind": n.get("kind"), "label": n.get("label"), "href": n.get("href")}


def _kind_ok(value: Any, kind: str) -> bool:
    if value is None:
        return kind.endswith("|null")
    expected = _TYPES[kind.split("|")[0]]
    if isinstance(value, bool) and expected is not bool:
        return False
    return isinstance(value, expected) and (kind != "text" or bool(value.strip()))


def _what(value: Any) -> str:
    return {dict: "object", list: "list", str: "string", bool: "boolean", type(None): "null"}.get(
        type(value), type(value).__name__)


def _integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


class _Checker:
    """Collects problems and resolved labels while walking one rationale file.

    Ids resolve against the wiki's ``graph`` or, for a file with its own space, against ``own`` (``{id: node}``,
    nodes shaped like the graph's: ``id``, ``kind``, ``label``, ``dimension_id`` for a value). With neither,
    ids are not resolved and only the structural rules run.
    """

    def __init__(self, graph: Optional[q.Graph]):
        self.graph = graph
        self.own: Optional[Dict[str, Dict[str, Any]]] = None
        self.own_edges: List[Dict[str, Any]] = []
        self.problems: List[Dict[str, Any]] = []
        self.resolved: Dict[str, str] = {}
        self._relations: Optional[Dict[frozenset, List[Dict[str, Any]]]] = None  # {source, target} -> edges

    @property
    def resolves(self) -> bool:
        """Whether ids can be resolved (a wiki graph or the file's own space)."""
        return self.graph is not None or self.own is not None

    def node(self, ident: Any) -> Dict[str, Any]:
        table = self.own if self.own is not None else (self.graph or {}).get("_by_id", {})
        return table.get(ident) or {}

    def add(self, code: str, path: str, message: str, candidates: Sequence[Any] = ()) -> None:
        self.problems.append({"code": code, "severity": "warning" if code in WARNINGS else "error",
                              "path": path, "message": message, "candidates": list(candidates)})

    # ------------------------------------------------------------ structure

    def fields(self, obj: Any, parts: Tuple[Any, ...], spec: _Spec) -> bool:
        """Check ``obj`` is an object with the fields of ``spec``; return whether it is an object."""
        if not isinstance(obj, dict):
            self.add("schema", pointer(*parts), f"expected an object, got {_what(obj)}")
            return False
        for key, (kind, required) in spec.items():
            if key not in obj:
                if required:
                    self.add("schema", pointer(*parts, key), f"missing {key}")
            elif not _kind_ok(obj[key], kind):
                want = "a non-empty string" if kind == "text" else kind.replace("|", " or ")
                self.add("schema", pointer(*parts, key), f"{key}: expected {want}, got {_what(obj[key])}")
        return True

    def items(self, obj: Mapping[str, Any], key: str) -> List[Any]:
        """Return the list under ``key`` (empty when absent, null or not a list: ``fields`` reports the shape)."""
        value = obj.get(key)
        return value if isinstance(value, list) else []

    def good(self, obj: Mapping[str, Any], key: str, kind: str = "text") -> bool:
        return key in obj and obj[key] is not None and _kind_ok(obj[key], kind)

    def one_of(self, obj: Mapping[str, Any], key: str, parts: Tuple[Any, ...], allowed: Sequence[str],
               what: str) -> None:
        if self.good(obj, key) and obj[key] not in allowed:
            self.add("schema", pointer(*parts, key), f"{what} are {', '.join(allowed)}, got {json.dumps(obj[key])}")

    # ------------------------------------------------------------ the space

    def ref(self, obj: Mapping[str, Any], key: str, parts: Tuple[Any, ...],
            kinds: Sequence[str]) -> Optional[Dict[str, Any]]:
        """Resolve ``obj[key]`` against the space; report unknown or non-canonical ids."""
        if not self.resolves or not self.good(obj, key):
            return None
        return self.resolve(obj[key], pointer(*parts, key), kinds)

    def resolve(self, ref: str, path: str, kinds: Sequence[str]) -> Optional[Dict[str, Any]]:
        """Resolve one id against the space; report it when unknown or not canonical."""
        if self.own is not None:
            n = self.own.get(ref)
            if n is None or n["kind"] not in kinds:
                same_kind = [x for x in self.own.values() if x["kind"] in kinds]
                close = difflib.get_close_matches(ref, [x["id"] for x in same_kind], n=5, cutoff=0.5)
                shown = [_brief(self.own[i]) for i in close] or [_brief(x) for x in same_kind[:5]]
                self.add("unknown_id", path, f"'{ref}' is not a {' or '.join(kinds)} id of the file's space "
                                             f"(space.dimensions)", shown)
                return None
            self.resolved.setdefault(n["id"], n.get("label", ""))
            return n
        try:
            n = q.resolve(self.graph, ref, kinds)
        except q.NotFound as exc:
            self.add("unknown_id", path, f"{exc} (expected a {' or '.join(kinds)} id)", exc.candidates)
            return None
        self.resolved.setdefault(n["id"], n.get("label", ""))
        if n["id"] != ref:
            self.add("not_canonical", path,
                     f"'{ref}' is not a canonical id; did you mean `{n['id']}` ({n.get('label')})?", [_brief(n)])
        return n

    def choice_ids(self, obj: Mapping[str, Any], parts: Tuple[Any, ...]) -> Tuple[Optional[dict], Optional[dict]]:
        """Resolve a dimension and value pair, and check the value belongs to the dimension."""
        d = self.ref(obj, "dimension_id", parts, ["dimension"])
        v = self.ref(obj, "value_id", parts, ["value"])
        if d is not None and v is not None and v.get("dimension_id") != d["id"]:
            owner = self.node(v.get("dimension_id"))
            self.add("value_not_in_dimension", pointer(*parts, "value_id"),
                     f"'{v.get('label')}' ({v['id']}) is a value of '{owner.get('label', v.get('dimension'))}' "
                     f"({v.get('dimension_id')}), not of '{d.get('label')}' ({d['id']})",
                     [_brief(owner)] if owner else [])
        return d, v

    def relation(self, rel: Mapping[str, Any], parts: Tuple[Any, ...]) -> None:
        src = self.ref(rel, "source", parts, ["dimension"])
        tgt = self.ref(rel, "target", parts, ["dimension"])
        if src is None or tgt is None or not self.good(rel, "type"):
            return
        a, b = src["id"], tgt["id"]
        if self._relations is None:
            edges = self.own_edges if self.own is not None else [
                e for e in (self.graph or {}).get("edges") or [] if e.get("type") == "relation"]
            self._relations = {}
            for e in edges:
                self._relations.setdefault(frozenset((e.get("source"), e.get("target"))), []).append(e)
        between = self._relations.get(frozenset((a, b)), [])

        def matches(e: Mapping[str, Any]) -> bool:
            same_way = e.get("source") == a and e.get("target") == b
            return e.get("relation") == rel["type"] and (same_way or not e.get("directed"))

        if any(matches(e) for e in between):
            return
        found = [{"source": e.get("source"), "target": e.get("target"), "type": e.get("relation"),
                  "directed": bool(e.get("directed"))} for e in between]
        where = "the graph" if self.own is None else "the file's space (space.relations)"
        what = (f"; {where} has " + ", ".join(
            f"{f['source']} {f['type']} {f['target']}" + ("" if f["directed"] else " (undirected)") for f in found)
            if found else f"; {where} has no relation between them")
        self.add("relation_mismatch", pointer(*parts),
                 f"no '{rel['type']}' relation from {a} ({src.get('label')}) to {b} ({tgt.get('label')}){what}",
                 found)

    def unmet_requires(self, value_ids: List[str], parts: Tuple[Any, ...]) -> None:
        if self.graph is None or not value_ids:
            return
        try:
            unmet = q.point(self.graph, value_ids).get("unmet_requires") or []
        except q.QueryError:  # the values were resolved above; nothing more to report
            return
        by_id = self.graph["_by_id"]
        for u in unmet:
            src, tgt = (by_id.get(u["dimension_id"], {}), by_id.get(u["requires_id"], {}))
            self.add("unmet_requires", pointer(*parts),
                     f"'{src.get('label', u['dimension_id'])}' ({u['dimension_id']}) requires a choice on "
                     f"'{tgt.get('label', u['requires_id'])}' ({u['requires_id']}), which the alternative leaves out",
                     [_brief(tgt)] if tgt else [])

    def stance(self, ev: Mapping[str, Any], parts: Tuple[Any, ...], v: Optional[Mapping[str, Any]]) -> None:
        """Check a cited passage's stance: one of ``q.STANCES`` and, with a wiki, the one the graph records.

        A passage the graph records as ``both`` (it accepts and rejects the value) backs a claim of ``accepts``,
        ``rejects`` or ``both``; any other recorded stance backs only itself. No stance: nothing to check.
        """
        if "stance" not in ev or not isinstance(ev["stance"], str):
            return  # absent, or the wrong type (``fields`` reported it)
        claim = ev["stance"]
        if claim not in q.STANCES:
            self.add("schema", pointer(*parts, "stance"),
                     f"stance: expected one of {', '.join(q.STANCES)}, got {json.dumps(claim)}")
            return
        if v is None or not self.good(ev, "doc"):
            return
        recorded = [p for p in v.get("passages") or [] if p.get("doc") == ev["doc"]]
        if not recorded:
            return  # evidence_not_on_value reports it
        if any(p.get("stance") == claim or (p.get("stance") == "both" and claim in ("accepts", "rejects"))
               for p in recorded):
            return
        self.add("evidence_stance_mismatch", pointer(*parts),
                 f"passage '{ev['doc']}' {' or '.join(str(p.get('stance')) for p in recorded)} "
                 f"'{v.get('label')}' ({v['id']}), not '{claim}' (cite the stance `ddspace query evidence` prints)",
                 [{"doc": p.get("doc"), "stance": p.get("stance")} for p in recorded])


def check(doc: Any, graph: Optional[q.Graph] = None, graph_sha256: Optional[str] = None) -> Dict[str, Any]:
    """Check a parsed rationale file; return ``{ok, graph_sha256, problems, resolved}``.

    ``graph`` (from ``q.load``) enables the rules against a wiki's space; it is used only for a file that names
    one (``names_space``). ``graph_sha256`` is the hash of that graph's file. A file with its own space is
    checked against it; a file that names a wiki, checked without its graph, gets the structural rules only.
    ``ok`` is false when any problem is an error; warnings are allowed.
    """
    c = _Checker(graph if names_space(doc) else None)
    _check(c, doc, graph_sha256 if c.graph is not None else None)
    return {"ok": not any(p["severity"] == "error" for p in c.problems),
            "graph_sha256": graph_sha256 if c.graph is not None else None,
            "problems": c.problems,
            "resolved": [{"id": i, "label": label} for i, label in c.resolved.items()]}


def _check(c: _Checker, doc: Any, graph_sha256: Optional[str]) -> None:
    if not c.fields(doc, (), _TOP):
        return
    if doc.get("schema") is not None and doc.get("schema") != SCHEMA:
        c.add("schema", "/schema", f"expected '{SCHEMA}', got {json.dumps(doc.get('schema'))}")
    mode = doc.get("mode")
    if mode is not None and mode not in MODES:
        c.add("schema", "/mode", f"expected one of {', '.join(MODES)}, got {json.dumps(mode)}")
    space = doc.get("space")
    if own_space(doc):
        _own_space(c, space)
    elif isinstance(space, dict) and c.fields(space, ("space",), _WIKI):
        sha = space.get("graph_sha256")
        if graph_sha256 and isinstance(sha, str) and sha and sha != graph_sha256:
            c.add("graph_changed", "/space/graph_sha256",
                  f"the graph changed since the file was written (file {sha[:12]}…, graph {graph_sha256[:12]}…); "
                  "ids that still resolve are checked against the current graph")

    requirements = _requirements(c, doc.get("problem"))
    approaches = _approaches(c, doc, mode)
    points = _points(c, doc)
    steps = _trajectory(c, doc, mode, requirements, approaches)
    _step_points(c, doc, points, steps)
    _alternatives(c, doc, mode, requirements, steps, approaches)
    _regions(c, doc, mode, requirements, steps)
    _adrs(c, doc, mode, requirements, steps)
    _unaddressed(c, doc, mode, requirements)

    for i, item in enumerate(c.items(doc, "comparison")):
        parts = ("comparison", i)
        if c.fields(item, parts, _COMPARISON):
            c.ref(item, "dimension_id", parts, ["dimension"])

    if mode == "explain" and "uncovered" not in doc:
        c.add("schema", "/uncovered", "missing uncovered (explain lists the decisions the space does not cover; "
                                      "use [] when every decision is mapped)")
    uncovered = c.items(doc, "uncovered")
    if uncovered and own_space(doc):
        c.add("schema", "/uncovered", "a file with its own space (space.dimensions) maps every decision onto it; "
                                      "leave uncovered empty")
    for i, item in enumerate(uncovered):
        parts = ("uncovered", i)
        if c.fields(item, parts, _UNCOVERED) and item.get("nearest_dimension_id") is not None:
            c.ref(item, "nearest_dimension_id", parts, ["dimension"])


def _own_space(c: _Checker, space: Mapping[str, Any]) -> None:
    """Check the agent's own space and make it the table ids resolve against."""
    c.own = {}
    if not c.fields(space, ("space",), _OWN):
        return
    for i, dim in enumerate(c.items(space, "dimensions")):
        parts = ("space", "dimensions", i)
        if not c.fields(dim, parts, _OWN_DIMENSION) or not c.good(dim, "id"):
            continue
        if dim["id"] in c.own:
            c.add("schema", pointer(*parts, "id"), f"duplicate id '{dim['id']}' in the space")
            continue
        c.own[dim["id"]] = {"id": dim["id"], "kind": "dimension", "label": dim.get("name") or dim["id"]}
        values = c.items(dim, "values")
        if not values:
            c.add("schema", pointer(*parts, "values"), "a dimension has at least one value")
        for j, value in enumerate(values):
            vparts = (*parts, "values", j)
            if not c.fields(value, vparts, _OWN_VALUE) or not c.good(value, "id"):
                continue
            if value["id"] in c.own:
                c.add("schema", pointer(*vparts, "id"), f"duplicate id '{value['id']}' in the space")
                continue
            c.own[value["id"]] = {"id": value["id"], "kind": "value", "label": value.get("name") or value["id"],
                                  "dimension_id": dim["id"], "dimension": dim.get("name")}
    for i, rel in enumerate(c.items(space, "relations")):
        parts = ("space", "relations", i)
        if not c.fields(rel, parts, _OWN_RELATION):
            continue
        src = c.ref(rel, "source", parts, ["dimension"])
        tgt = c.ref(rel, "target", parts, ["dimension"])
        if src is not None and tgt is not None and c.good(rel, "type"):
            c.own_edges.append({"source": src["id"], "target": tgt["id"], "relation": rel["type"], "directed": True})


def _requirements(c: _Checker, problem: Any) -> set:
    ids: set = set()
    if not c.fields(problem, ("problem",), _PROBLEM):
        return ids
    for i, req in enumerate(c.items(problem, "requirements")):
        parts = ("problem", "requirements", i)
        if c.fields(req, parts, _REQUIREMENT) and c.good(req, "id"):
            if req["id"] in ids:
                c.add("schema", pointer(*parts, "id"), f"duplicate requirement id '{req['id']}'")
            ids.add(req["id"])
    return ids


def _unknown_requirement(c: _Checker, rid: Any, path: str, requirements: set) -> None:
    if not isinstance(rid, str):
        c.add("schema", path, f"expected a requirement id, got {_what(rid)}")
    elif rid not in requirements:
        known = ", ".join(sorted(requirements)) or "none"
        c.add("unknown_requirement", path, f"'{rid}' names no requirement (the requirements: {known})")


def _drivers(c: _Checker, obj: Mapping[str, Any], parts: Tuple[Any, ...], requirements: set) -> None:
    for k, driver in enumerate(c.items(obj, "drivers")):
        _unknown_requirement(c, driver, pointer(*parts, "drivers", k), requirements)


def _assessment(c: _Checker, step: Mapping[str, Any], parts: Tuple[Any, ...], requirements: set) -> None:
    assessment = step.get("assessment")
    if not isinstance(assessment, dict):
        return  # ``fields`` reported it
    if not assessment:
        c.add("schema", pointer(*parts, "assessment"), "the assessment judges at least one requirement")
    for rid, judged in assessment.items():
        path = pointer(*parts, "assessment", rid)
        _unknown_requirement(c, rid, path, requirements)
        if judged not in ASSESSMENTS:
            c.add("schema", path, f"a requirement is judged {', '.join(ASSESSMENTS)}, got {json.dumps(judged)}")


def _point_values(c: _Checker, values: List[Any], parts: Tuple[Any, ...], owner: str) -> Optional[frozenset]:
    """Check a design point's ``values`` (value ids); return its key, the set of canonical value ids.

    The key is None when a value could not be resolved against a space that resolves ids. One value per
    dimension, as in an alternative.
    """
    if not values:
        c.add("schema", pointer(*parts), f"{owner}: a design point names at least one value")
        return None
    key: set = set()
    first: Dict[Any, str] = {}
    complete = True
    for k, item in enumerate(values):
        path = pointer(*parts, k)
        if not isinstance(item, str) or not item.strip():
            c.add("schema", path, f"expected a value id (v:…), got {_what(item)}")
            complete = False
            continue
        v = c.resolve(item, path, ["value"]) if c.resolves else None
        if v is None:
            complete = complete and not c.resolves
            key.add(item)
            continue
        dim = v.get("dimension_id")
        if dim in first:
            c.add("two_values_one_dimension", path,
                  f"'{v.get('label')}' ({v['id']}) is a second value for one dimension in {owner} (the first is at "
                  f"{first[dim]}): a design point takes one value per dimension")
        else:
            first[dim] = path
        key.add(v["id"])
    return frozenset(key) if complete else None


def _approaches(c: _Checker, doc: Mapping[str, Any], mode: Any) -> Dict[str, Dict[str, Any]]:
    """Check search's approaches; return ``{id: approach}``."""
    found: Dict[str, Dict[str, Any]] = {}
    approaches = c.items(doc, "approaches")
    if mode == "explain":
        if approaches:
            c.add("schema", "/approaches", "approaches belong to search; explain starts from the given solution")
        return found
    if mode == "search" and "approaches" not in doc:
        c.add("schema", "/approaches", "missing approaches (search works out two or more \"what if\" approaches)")
    for i, item in enumerate(approaches):
        parts = ("approaches", i)
        if not c.fields(item, parts, _APPROACH):
            continue
        c.one_of(item, "status", parts, STATUSES, "approach statuses")
        if item.get("status") == "dropped" and not c.good(item, "dropped_because"):
            c.add("schema", pointer(*parts, "dropped_because"),
                  "a dropped approach says why (dropped_because): later rounds must not repeat the reason")
        if c.good(item, "id"):
            if item["id"] in found:
                c.add("schema", pointer(*parts, "id"), f"duplicate approach id '{item['id']}'")
            found[item["id"]] = item
    return found


def _trajectory(c: _Checker, doc: Mapping[str, Any], mode: Any, requirements: set,
                approaches: Mapping[str, Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    """Check the budget and the trajectory; return ``{step number: {step, key}}`` for the well-formed steps."""
    steps: Dict[int, Dict[str, Any]] = {}
    known = mode in MODES
    budget = doc.get("budget")
    limit = None
    if c.fields(budget, ("budget",), _BUDGET) and c.good(budget, "max_points", "integer"):
        limit = budget["max_points"]
        if limit < 1 or (known and limit > MAX_POINTS[mode]):
            c.add("budget", "/budget/max_points",
                  f"max_points is {limit}: {mode} evaluates 1 to {MAX_POINTS.get(mode)} design points"
                  if known else f"max_points is {limit}: expected at least 1")
    trajectory = doc.get("trajectory")
    if not isinstance(trajectory, list):
        return steps
    if not trajectory:
        c.add("schema", "/trajectory", "the trajectory lists at least one step (the design points evaluated)")
    if limit is not None and len(trajectory) > limit:
        c.add("budget", "/trajectory",
              f"the trajectory has {len(trajectory)} steps, over the budget of {limit} design points")
    spec = {**_STEP, **(_SEARCH_STEP if mode == "search" else _EXPLAIN_STEP if mode == "explain" else {})}
    solutions = 0
    last_round = 1
    for i, step in enumerate(trajectory):
        parts = ("trajectory", i)
        if not c.fields(step, parts, spec):
            continue
        number = step.get("step")
        if c.good(step, "step", "integer") and number != i + 1:
            c.add("bad_step", pointer(*parts, "step"), f"steps are numbered 1, 2, … in order: expected {i + 1}, "
                                                        f"got {number}")
        move = step.get("move")
        if known and c.good(step, "move") and move not in MOVES[mode]:
            c.add("bad_step", pointer(*parts, "move"),
                  f"{mode} moves are {', '.join(MOVES[mode])}, got {json.dumps(move)}")
        if mode == "search":
            c.one_of(step, "rating", parts, RATINGS, "search ratings")
        elif mode == "explain":
            c.one_of(step, "verdict", parts, VERDICTS, "explain verdicts")
        solutions += move == "solution"
        parent = step.get("parent")
        parent_entry = None
        if _integer(parent):
            if not 1 <= parent <= i:
                c.add("bad_step", pointer(*parts, "parent"),
                      f"the parent {parent} is not an earlier step (steps before this one: 1 to {i})"
                      if i else "the first step has no earlier step to name as its parent")
            elif move in ROOT_MOVES:
                c.add("bad_step", pointer(*parts, "parent"), f"a {move} step starts the trajectory: it has no parent")
            else:
                parent_entry = steps.get(parent)
        elif move in PARENT_MOVES:
            c.add("bad_step", pointer(*parts, "parent"), f"a {move} step names the step it starts from (parent)")
        if mode == "search":
            last_round = _search_step(c, step, parts, approaches, parent_entry, last_round)
        _assessment(c, step, parts, requirements)
        key = _point_values(c, c.items(step, "values"), (*parts, "values"), f"step {i + 1}")
        if c.good(step, "step", "integer") and number == i + 1:
            steps[number] = {"step": step, "key": key}
    if mode == "explain" and trajectory and solutions != 1:
        c.add("bad_step", "/trajectory", f"explain has exactly one solution step (the given solution as a design "
                                         f"point), got {solutions}")
    return steps


def _search_step(c: _Checker, step: Mapping[str, Any], parts: Tuple[Any, ...],
                 approaches: Mapping[str, Dict[str, Any]], parent: Optional[Mapping[str, Any]], last_round: int) -> int:
    """Check a search step's round and approach; return the round reached so far."""
    rnd = step.get("round")
    if _integer(rnd):
        if rnd < last_round or rnd > last_round + 1 or rnd < 1:
            c.add("bad_step", pointer(*parts, "round"),
                  f"rounds start at 1 and go up one at a time: after round {last_round}, expected {last_round} or "
                  f"{last_round + 1}, got {rnd}")
        else:
            last_round = rnd
        if step.get("move") == "seed" and rnd != 1:
            c.add("bad_step", pointer(*parts, "round"), "seed steps are round 1; a new approach later is an explore step")
    approach = step.get("approach")
    if c.good(step, "approach") and approaches and approach not in approaches:
        c.add("step_mismatch", pointer(*parts, "approach"),
              f"the approach '{approach}' is not in approaches (they are {', '.join(approaches)})", list(approaches))
    if parent is not None and step.get("move") in SAME_APPROACH_MOVES and c.good(step, "approach"):
        theirs = parent["step"].get("approach")
        if theirs != approach:
            c.add("bad_step", pointer(*parts, "approach"),
                  f"an {step.get('move')} step stays in its parent's approach: step {parent['step'].get('step')} is "
                  f"approach '{theirs}', this step says '{approach}'")
    return last_round


def _same_point(c: _Checker, owner: Mapping[str, Any], key: Optional[frozenset], parts: Tuple[Any, ...],
                steps: Mapping[int, Dict[str, Any]], what: str, moves: Sequence[str] = ()) -> Optional[Mapping]:
    """Check ``owner.step`` names a step whose values are ``key`` (and, optionally, its move); return the step."""
    number = owner.get("step")
    if not _integer(number):
        return None  # ``fields`` reported it
    entry = steps.get(number)
    path = pointer(*parts, "step")
    if entry is None:
        c.add("step_mismatch", path, f"{what} names step {number}, which the trajectory does not have")
        return None
    step = entry["step"]
    if moves and step.get("move") not in moves:
        c.add("step_mismatch", path, f"{what} names step {number}, a {step.get('move')} step: expected a "
                                     f"{' or '.join(moves)} step")
    if key is not None and entry["key"] is not None and key != entry["key"]:
        c.add("step_mismatch", path, f"{what} takes {', '.join(sorted(key)) or 'none'}, but step {number} evaluated "
                                     f"{', '.join(sorted(entry['key'])) or 'none'}: they must be the same design point",
              sorted(entry["key"]))
    return step


def _regions(c: _Checker, doc: Mapping[str, Any], mode: Any, requirements: set,
             steps: Mapping[int, Dict[str, Any]]) -> None:
    regions = c.items(doc, "regions")
    if mode == "search" and regions:
        c.add("schema", "/regions", "search proposes alternatives; regions belong to explain")
        return
    if mode != "explain":
        return
    if not REGIONS[0] <= len(regions) <= REGIONS[1]:
        c.add("schema", "/regions", f"explain names {REGIONS[0]} to {REGIONS[1]} regions (the partial design points "
                                    f"that best justify the solution), got {len(regions)}")
    solution = next((e["key"] for e in steps.values() if e["step"].get("move") == "solution"), None)
    seen: set = set()
    for i, region in enumerate(regions):
        parts = ("regions", i)
        if not c.fields(region, parts, _REGION):
            continue
        if c.good(region, "id"):
            if region["id"] in seen:
                c.add("schema", pointer(*parts, "id"), f"duplicate region id '{region['id']}'")
            seen.add(region["id"])
        _drivers(c, region, parts, requirements)
        key = _point_values(c, c.items(region, "values"), (*parts, "values"), f"region {i + 1}")
        if key is not None and solution is not None and not key <= solution:
            c.add("region_not_in_solution", pointer(*parts, "values"),
                  f"a region is a partial design point of the solution's values; the solution does not take "
                  f"{', '.join(sorted(key - solution))}")
        _same_point(c, region, key, parts, steps, f"region '{region.get('id')}'", ("region", "solution"))


def _alternatives(c: _Checker, doc: Mapping[str, Any], mode: Any, requirements: set,
                  steps: Mapping[int, Dict[str, Any]], approaches: Mapping[str, Dict[str, Any]]) -> None:
    alts = doc.get("alternatives")
    if not isinstance(alts, list):
        return
    if mode == "search" and not SEARCH_ALTERNATIVES[0] <= len(alts) <= SEARCH_ALTERNATIVES[1]:
        c.add("schema", "/alternatives",
              f"search returns {SEARCH_ALTERNATIVES[0]} to {SEARCH_ALTERNATIVES[1]} alternatives, got {len(alts)}")
    if mode == "explain":
        if len(alts) != 1:
            c.add("schema", "/alternatives",
                  f"explain has exactly one alternative (the solution, id '{EXPLAIN_ID}'), got {len(alts)}")
        elif isinstance(alts[0], dict) and c.good(alts[0], "id") and alts[0]["id"] != EXPLAIN_ID:
            c.add("schema", "/alternatives/0/id", f"the explained solution has id '{EXPLAIN_ID}', got '{alts[0]['id']}'")
    alt_spec = {**_ALTERNATIVE, "approach": ("text", True)} if mode == "search" else _ALTERNATIVE
    choice_spec = ({**_CHOICE, "solution_quote": ("text", True), "forced": ("boolean|null", True)}
                   if mode == "explain" else _CHOICE)
    seen_ids: set = set()
    seen_approaches: Dict[str, int] = {}
    for i, alt in enumerate(alts):
        if not c.fields(alt, ("alternatives", i), alt_spec):
            continue
        if c.good(alt, "id"):
            if alt["id"] in seen_ids:
                c.add("schema", pointer("alternatives", i, "id"), f"duplicate alternative id '{alt['id']}'")
            seen_ids.add(alt["id"])
        first: Dict[str, str] = {}
        value_ids: List[str] = []
        point_key: set = set()
        complete = True
        for j, choice in enumerate(c.items(alt, "choices")):
            parts = ("alternatives", i, "choices", j)
            if not c.fields(choice, parts, choice_spec):
                complete = False
                continue
            _drivers(c, choice, parts, requirements)
            _fit(c, choice, parts)
            d, v = c.choice_ids(choice, parts)
            if v is not None:
                value_ids.append(v["id"])
                point_key.add(v["id"])
            elif c.resolves or not c.good(choice, "value_id"):
                complete = False
            else:
                point_key.add(choice["value_id"])
            dim = d["id"] if d is not None else (choice["dimension_id"] if c.good(choice, "dimension_id") else None)
            if dim is not None and dim in first:
                what = f"'{d.get('label')}' ({d['id']})" if d is not None else f"'{dim}'"
                c.add("two_values_one_dimension", pointer(*parts),
                      f"a second choice for {what} in alternative '{alt.get('id')}' (the first is at "
                      f"{first[dim]}): an alternative takes one value per dimension")
            elif dim is not None:
                first[dim] = pointer(*parts)
            for k, ev in enumerate(c.items(choice, "evidence")):
                ev_parts = (*parts, "evidence", k)
                if not c.fields(ev, ev_parts, _EVIDENCE):
                    continue
                wiki_value = v if c.graph is not None else None
                if wiki_value is not None and c.good(ev, "doc"):
                    passages = wiki_value.get("passages") or []
                    if ev["doc"] not in {p.get("doc") for p in passages}:
                        c.add("evidence_not_on_value", pointer(*ev_parts),
                              f"passage '{ev['doc']}' is not among the passages of '{v.get('label')}' ({v['id']})",
                              [{"doc": p.get("doc"), "stance": p.get("stance")} for p in passages])
                c.stance(ev, ev_parts, wiki_value)

        for j, item in enumerate(c.items(alt, "considered")):
            parts = ("alternatives", i, "considered", j)
            if c.fields(item, parts, _CONSIDERED):
                _drivers(c, item, parts, requirements)
                c.choice_ids(item, parts)
        for j, item in enumerate(c.items(alt, "open")):
            parts = ("alternatives", i, "open", j)
            if c.fields(item, parts, _OPEN):
                c.ref(item, "dimension_id", parts, ["dimension"])
        for j, rel in enumerate(c.items(alt, "relations")):
            parts = ("alternatives", i, "relations", j)
            if c.fields(rel, parts, _RELATION) and c.resolves:
                c.relation(rel, parts)
        c.unmet_requires(value_ids, ("alternatives", i))
        resolved = frozenset(point_key) if complete else None
        if mode == "explain":
            _same_point(c, alt, resolved, ("alternatives", i), steps, f"the solution '{alt.get('id')}'", ("solution",))
            continue
        step = _same_point(c, alt, resolved, ("alternatives", i), steps, f"alternative '{alt.get('id')}'")
        if mode == "search":
            _alternative_approach(c, alt, i, step, approaches, seen_approaches)


def _alternative_approach(c: _Checker, alt: Mapping[str, Any], i: int, step: Optional[Mapping[str, Any]],
                          approaches: Mapping[str, Dict[str, Any]], seen: Dict[str, int]) -> None:
    """Check a search alternative is the point of one live approach, one alternative per approach, never weak."""
    path = pointer("alternatives", i, "approach")
    approach = alt.get("approach")
    if not c.good(alt, "approach"):
        return
    if approach in seen:
        c.add("step_mismatch", path, f"alternatives {seen[approach] + 1} and {i + 1} both come from approach "
                                     f"'{approach}': propose the best point of each approach")
    seen.setdefault(approach, i)
    known = approaches.get(approach)
    if approaches and known is None:
        c.add("step_mismatch", path, f"the approach '{approach}' is not in approaches", list(approaches))
    elif known is not None and known.get("status") == "dropped":
        c.add("step_mismatch", path, f"the approach '{approach}' was dropped; propose points of live approaches")
    if step is None:
        return
    if step.get("approach") != approach:
        c.add("step_mismatch", pointer("alternatives", i, "step"),
              f"alternative '{alt.get('id')}' says approach '{approach}', but step {step.get('step')} is approach "
              f"'{step.get('approach')}'")
    if step.get("rating") == "weak":
        c.add("step_mismatch", pointer("alternatives", i, "step"),
              f"step {step.get('step')} is rated weak: propose only strong or mixed points")


def _points(c: _Checker, doc: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Check the list of design points; return ``{id: {point, key}}``. Two entries with the same values are an
    error (``duplicate_point``): the agent reuses the first instead of describing the point again."""
    found: Dict[str, Dict[str, Any]] = {}
    by_key: Dict[frozenset, str] = {}
    for i, item in enumerate(c.items(doc, "points")):
        parts = ("points", i)
        if not c.fields(item, parts, _POINT) or not c.good(item, "id"):
            continue
        if item["id"] in found:
            c.add("schema", pointer(*parts, "id"), f"duplicate point id '{item['id']}'")
            continue
        key = _point_values(c, c.items(item, "values"), (*parts, "values"), f"point '{item['id']}'")
        if key is not None and key in by_key:
            c.add("duplicate_point", pointer(*parts, "values"),
                  f"point '{item['id']}' has the same values as point '{by_key[key]}': reuse '{by_key[key]}' "
                  "instead of evaluating and describing it again", [by_key[key]])
        elif key is not None:
            by_key[key] = item["id"]
        found[item["id"]] = {"point": item, "key": key}
    return found


def _step_points(c: _Checker, doc: Mapping[str, Any], points: Mapping[str, Dict[str, Any]],
                 steps: Mapping[int, Dict[str, Any]]) -> None:
    """Each step names a point of the list with exactly its values; every point is named by some step."""
    used: set = set()
    for i, step in enumerate(c.items(doc, "trajectory")):
        if not isinstance(step, dict) or not c.good(step, "point"):
            continue
        path = pointer("trajectory", i, "point")
        entry = points.get(step["point"])
        if entry is None:
            c.add("unknown_point", path, f"'{step['point']}' is not in points (the list of evaluated design points)",
                  sorted(points))
            continue
        used.add(step["point"])
        number = step.get("step")
        mine = steps.get(number, {}).get("key") if _integer(number) else None
        if mine is not None and entry["key"] is not None and mine != entry["key"]:
            c.add("point_mismatch", path,
                  f"step {number} takes {', '.join(sorted(mine))}, but point '{step['point']}' is "
                  f"{', '.join(sorted(entry['key']))}: a step names the point with exactly its values")
    for i, item in enumerate(c.items(doc, "points")):
        if isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"] in points and item["id"] not in used:
            c.add("unused_point", pointer("points", i), f"no step names point '{item['id']}'")


def _alternative_values(doc: Mapping[str, Any]) -> Dict[str, List[Tuple[int, int, str]]]:
    """Return ``{alternative id: [(alternative index, choice index, value id)]}`` for the well-formed choices."""
    found: Dict[str, List[Tuple[int, int, str]]] = {}
    for i, alt in enumerate(doc.get("alternatives") or []):
        if not isinstance(alt, dict) or not isinstance(alt.get("id"), str):
            continue
        for j, choice in enumerate(alt.get("choices") or []):
            if isinstance(choice, dict) and isinstance(choice.get("value_id"), str):
                found.setdefault(alt["id"], []).append((i, j, choice["value_id"]))
    return found


def _adrs(c: _Checker, doc: Mapping[str, Any], mode: Any, requirements: set,
          steps: Mapping[int, Dict[str, Any]]) -> None:
    """Check the ADRs: drivers, options as partial design points, chosen options inside the alternatives that
    take them, and every alternative's values in some chosen option (``not_in_adr``)."""
    adrs = doc.get("adrs")
    if not isinstance(adrs, list):
        return
    if not adrs:
        c.add("schema", "/adrs", "the solution(s) are described as at least one ADR")
    alt_values = _alternative_values(doc)
    taken = {a: {v for _, _, v in vs} for a, vs in alt_values.items()}
    covered: set = set()  # (alternative id, value id) in some chosen option that names the alternative
    seen: set = set()
    for i, adr in enumerate(adrs):
        parts = ("adrs", i)
        if not c.fields(adr, parts, _ADR):
            continue
        if c.good(adr, "id"):
            if adr["id"] in seen:
                c.add("schema", pointer(*parts, "id"), f"duplicate ADR id '{adr['id']}'")
            seen.add(adr["id"])
        if not c.items(adr, "drivers") and isinstance(adr.get("drivers"), list):
            c.add("schema", pointer(*parts, "drivers"), "an ADR addresses at least one requirement")
        _drivers(c, adr, parts, requirements)
        options = c.items(adr, "options")
        chosen = 0
        option_ids: set = set()
        for j, option in enumerate(options):
            oparts = (*parts, "options", j)
            if not c.fields(option, oparts, _OPTION):
                continue
            if c.good(option, "id"):
                if option["id"] in option_ids:
                    c.add("schema", pointer(*oparts, "id"), f"duplicate option id '{option['id']}' in the ADR")
                option_ids.add(option["id"])
            c.one_of(option, "status", oparts, OPTION_STATUSES, "option statuses")
            _fit(c, option, oparts)
            for key in ("pros", "cons"):
                for k, item in enumerate(c.items(option, key)):
                    if not isinstance(item, str) or not item.strip():
                        c.add("schema", pointer(*oparts, key, k), f"expected a non-empty string, got {_what(item)}")
            key = _point_values(c, c.items(option, "values"), (*oparts, "values"), f"option '{option.get('id')}'")
            names = [a for a in c.items(option, "in") if isinstance(a, str)]
            if option.get("status") == "chosen":
                chosen += 1
                if not names:
                    c.add("schema", pointer(*oparts, "in"), "a chosen option names the alternatives that take it (in)")
                if mode == "explain" and names and names != [EXPLAIN_ID]:
                    c.add("adr_mismatch", pointer(*oparts, "in"),
                          f"in explain, the chosen option is the solution's: in is ['{EXPLAIN_ID}']")
                for k, name in enumerate(names):
                    if name not in taken:
                        c.add("adr_mismatch", pointer(*oparts, "in", k),
                              f"'{name}' is not an alternative (the alternatives: {', '.join(taken) or 'none'})",
                              list(taken))
                        continue
                    for v in c.items(option, "values"):
                        if isinstance(v, str) and v not in taken[name]:
                            c.add("adr_mismatch", pointer(*oparts, "values"),
                                  f"alternative '{name}' does not take {v}: a chosen option is part of the "
                                  f"alternatives it names", sorted(taken[name]))
                        elif isinstance(v, str):
                            covered.add((name, v))
            elif option.get("status") == "discarded" and names:
                c.add("schema", pointer(*oparts, "in"), "a discarded option is in no alternative: leave in empty")
            number = option.get("step")
            if _integer(number):
                entry = steps.get(number)
                if entry is None:
                    c.add("step_mismatch", pointer(*oparts, "step"),
                          f"option '{option.get('id')}' names step {number}, which the trajectory does not have")
                elif key is not None and entry["key"] is not None and not key <= entry["key"]:
                    c.add("step_mismatch", pointer(*oparts, "step"),
                          f"step {number} did not evaluate {', '.join(sorted(key - entry['key']))}: an option's "
                          "step evaluated a point that takes all its values")
        if not options and isinstance(adr.get("options"), list):
            c.add("schema", pointer(*parts, "options"), "an ADR weighs at least one option")
        elif options and not chosen:
            c.add("schema", pointer(*parts, "options"), "an ADR records a decision: at least one option is chosen")
        elif mode == "explain" and chosen > 1:
            c.add("schema", pointer(*parts, "options"), "in explain, an ADR has one chosen option, the solution's")
    for name, values in alt_values.items():
        for i, j, v in values:
            if (name, v) not in covered:
                c.add("not_in_adr", pointer("alternatives", i, "choices", j),
                      f"alternative '{name}' takes {v}, but no ADR has a chosen option with it in '{name}': "
                      "describe every decision in an ADR")


def _fit(c: _Checker, obj: Mapping[str, Any], parts: Tuple[Any, ...]) -> None:
    """Check a choice's or option's ``fit``: an approximate fit says why (``fit_note``)."""
    c.one_of(obj, "fit", parts, FITS, "fits")
    if obj.get("fit") != "approximate":
        return
    if not c.good(obj, "fit_note"):
        c.add("schema", pointer(*parts, "fit_note"),
              "an approximate fit says in fit_note what the value leaves out or stretches")


def _unaddressed(c: _Checker, doc: Mapping[str, Any], mode: Any, requirements: set) -> None:
    """Every requirement is a driver of some ADR or listed in ``unaddressed`` with a reason, never both."""
    driven = {d for adr in c.items(doc, "adrs") if isinstance(adr, dict)
              for d in c.items(adr, "drivers") if isinstance(d, str)}
    listed: Dict[str, int] = {}
    for i, item in enumerate(c.items(doc, "unaddressed")):
        parts = ("unaddressed", i)
        if not c.fields(item, parts, _UNADDRESSED):
            continue
        c.one_of(item, "reason", parts, UNADDRESSED_REASONS, "reasons")
        if item.get("reason") == "not_in_solution" and mode == "search":
            c.add("schema", pointer(*parts, "reason"), "not_in_solution belongs to explain: search designs the "
                                                       "solution (no_dimension, traded_off or budget)")
        if item.get("nearest_dimension_id") is not None:
            c.ref(item, "nearest_dimension_id", parts, ["dimension"])
        rid = item.get("requirement")
        if not c.good(item, "requirement"):
            continue
        _unknown_requirement(c, rid, pointer(*parts, "requirement"), requirements)
        if rid in listed:
            c.add("schema", pointer(*parts, "requirement"), f"'{rid}' is listed twice in unaddressed")
        listed.setdefault(rid, i)
        if rid in driven:
            c.add("unaddressed_mismatch", pointer(*parts, "requirement"),
                  f"'{rid}' is a driver of an ADR, so it is addressed: remove it from unaddressed")
    problem = doc.get("problem") if isinstance(doc.get("problem"), dict) else {}
    for i, req in enumerate(c.items(problem, "requirements")):
        rid = req.get("id") if isinstance(req, dict) else None
        if isinstance(rid, str) and rid not in driven and rid not in listed:
            c.add("unaccounted_requirement", pointer("problem", "requirements", i),
                  f"no ADR has '{rid}' among its drivers and unaddressed does not list it: address it in an ADR, "
                  "or list it in unaddressed with a reason (no_dimension when the space has no dimension for it; "
                  "do not force it onto one)")


# ---------------------------------------------------------------- the workspace's rationale/ folder

SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")  # an id that can name a file (use ``safe_id``: fullmatch)
RATIONALE_DIR = "rationale"
OK, CHANGED, BROKEN = "ok", "changed", "broken"  # a rationale file's status (``scan``)


def safe_id(rid: Any) -> bool:
    """Whether ``rid`` can name a page file: letters, digits, '.', '_' and '-', not starting with a symbol."""
    return isinstance(rid, str) and SAFE_ID.fullmatch(rid) is not None


def _broken(entry: Dict[str, Any], code: str, message: str, path: str = "", candidates: Sequence[Any] = ()) -> None:
    """Mark a scan entry broken (not rendered) with one more error."""
    entry["problems"].append({"code": code, "severity": "error", "path": path, "message": message,
                              "candidates": list(candidates)})
    entry["status"], entry["doc"], entry["page"] = BROKEN, None, None


def _status(path: Path, graph: Optional[q.Graph], sha: Optional[str], html: Path) -> Dict[str, Any]:
    """One ``rationale/*.json`` file: ``{file, id, mode, title, alternatives, status, page, problems, doc}``.

    ``broken``: unreadable, check errors, an id that cannot name a page, or a space but no graph to check it
    against. ``changed``: clean, but written against an earlier graph (KTD7). ``ok`` otherwise.
    """
    entry: Dict[str, Any] = {"file": str(path), "id": path.stem, "mode": None, "title": None, "alternatives": 0,
                             "status": BROKEN, "page": None, "problems": [], "doc": None}
    try:
        doc = load(path)
    except RationaleError as exc:
        entry["problems"] = [{"code": "unreadable", "severity": "error", "path": "", "message": str(exc)}]
        return entry
    if isinstance(doc, dict):
        entry["_declares"] = True  # the id is the file's own (``_scan`` compares them), not the stem fallback
        entry["id"] = str(doc.get("id") or path.stem)
        entry["mode"] = doc.get("mode")
        problem = doc.get("problem")
        entry["title"] = problem.get("title") if isinstance(problem, dict) else None
        alts = doc.get("alternatives")
        entry["alternatives"] = len(alts) if isinstance(alts, list) else 0
    page = html / "explainers" / f"{entry['id']}.html"
    entry["page"] = str(page) if safe_id(entry["id"]) and page.is_file() else None
    if names_space(doc) and graph is None:
        entry["problems"] = [{"code": "no_graph", "severity": "error", "path": "/space",
                              "message": "the file names a space, but the workspace has no raw/graph.json"}]
        return entry
    result = check(doc, graph, sha)
    entry["problems"] = result["problems"]
    if not safe_id(entry["id"]):
        entry["problems"].append({"code": "schema", "severity": "error", "path": "/id",
                                  "message": f"the id '{entry['id']}' cannot name a file"})
    elif result["ok"]:
        entry["status"] = CHANGED if any(p["code"] == "graph_changed" for p in result["problems"]) else OK
        entry["doc"] = doc
    return entry


def _graph(root: Path) -> Tuple[Optional[q.Graph], Optional[str]]:
    path = Path(root) / "raw" / "graph.json"
    try:
        return q.load(path), file_sha256(path)
    except (q.QueryError, OSError, ValueError):
        return None, None


def _public(entry: Mapping[str, Any]) -> Dict[str, Any]:
    """Return a scan entry without its ``doc`` key and private (``_``) keys."""
    return {k: v for k, v in entry.items() if k != "doc" and not k.startswith("_")}


def scan(root: Path, html: Path, graph: Optional[q.Graph] = None, sha: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return the status of every ``<root>/rationale/*.json`` against ``<root>/raw/graph.json`` (no ``doc`` key).

    ``graph`` and ``sha``, when given, are that graph already loaded and its file's SHA-256.
    """
    return [_public(e) for e in _scan(root, html, graph, sha)[1]]


def _scan(root: Path, html: Path, graph: Optional[q.Graph] = None, sha: Optional[str] = None):
    folder = Path(root) / RATIONALE_DIR
    files = sorted(folder.glob("*.json")) if folder.is_dir() else []
    if graph is None:
        graph, sha = _graph(root) if files else (None, None)
    entries = [_status(f, graph, sha, Path(html)) for f in files]
    by_id: Dict[str, List[Dict[str, Any]]] = {}
    for e in entries:
        if e.get("_declares"):
            by_id.setdefault(e["id"], []).append(e)
    for rid, same in by_id.items():
        if len(same) > 1:  # one page per id: none of them is rendered until the ids differ
            for e in same:
                others = [Path(o["file"]).name for o in same if o is not e]
                _broken(e, "duplicate_id", f"the id '{rid}' is also declared by {', '.join(others)}: "
                        "each file in rationale/ needs its own id", "/id", others)
    return graph, entries


def declared_by(root: Path, rid: str, skip: Optional[Path] = None) -> List[Path]:
    """Return the ``<root>/rationale/*.json`` files (other than ``skip``) whose declared id is ``rid``."""
    folder = Path(root) / RATIONALE_DIR
    found = []
    for f in sorted(folder.glob("*.json")) if folder.is_dir() else []:
        if skip is not None and f.resolve() == Path(skip).resolve():
            continue
        try:
            doc = load(f)
        except RationaleError:
            continue
        if isinstance(doc, dict) and str(doc.get("id") or f.stem) == rid:
            found.append(f)
    return found


def index_entries(entries: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """Return the rendered pages among ``entries`` (scan results), as the HTML index lists them."""
    return [{"id": e["id"], "title": e.get("title"), "mode": e.get("mode"), "changed": e["status"] == CHANGED}
            for e in entries if e["status"] != BROKEN and e.get("page")]


def render_workspace(root: Path, html: Path) -> List[Dict[str, Any]]:
    """Check, then re-render, every ``<root>/rationale/*.json`` into ``<html>/explainers/`` (``wiki build``).

    A broken file is skipped (its old page is then removed as stale by the export); a changed one renders with
    the graph-changed banner. The HTML index lists the rendered pages. Returns the scan results.
    """
    from taxonomy_generator.wiki import explainer

    graph, entries = _scan(root, html)
    for e in entries:
        if e["status"] == BROKEN:
            e["page"] = None  # not rendered again: the export removes the old page
            continue
        try:
            e["page"] = str(explainer.write_page(e["doc"], graph, Path(html), wiki_html=Path(html),
                                                 graph_changed=e["status"] == CHANGED))
        except Exception as exc:  # noqa: BLE001 -- one page that cannot render must not stop the wiki build
            _broken(e, "render_failed", f"the explainer page could not be rendered: {type(exc).__name__}: {exc}")
    explainer.write_index(Path(html), index_entries(entries))
    return [_public(e) for e in entries]
