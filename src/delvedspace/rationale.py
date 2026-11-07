"""The design rationale file (``ddspace-rationale/1``) and its checker, with no ``jsonschema`` dependency.

A coding agent writes one rationale file per problem. *Search* fills two to four ``alternatives``, with what
each one ``considered``, left ``open`` and claims about ``relations``, plus a ``comparison``. *Explain* fills
one alternative (``id: "S"``, the given solution) whose choices quote the solution (``solution_quote``), plus
the ``uncovered`` decisions the space has no dimension for.

With a space (``space: {workspace, run, graph_sha256}``), choices name dimension and value ids exactly as
``ddspace query`` prints them (``d:1``, ``v:1.2``), and ``check`` also tests them against ``raw/graph.json``.
Without one (``space: null``), choices name the agent's own ``decision`` and ``option`` and only the
structural rules run. Every problem has a stable ``code`` and a JSON Pointer ``path`` into the file.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from taxonomy_generator.wiki import query as q

SCHEMA = "ddspace-rationale/1"
MODES = ("search", "explain")
SEARCH_ALTERNATIVES = (2, 4)
EXPLAIN_ID = "S"
WARNINGS = ("unmet_requires", "graph_changed")

# Field specs: name -> (kind, required). Kinds: "text" (a non-empty string), "string", "string|null", "list",
# "object", "object|null", "boolean".
_Spec = Dict[str, Tuple[str, bool]]
_TYPES = {"text": str, "string": str, "list": list, "object": dict, "boolean": bool}
_TOP: _Spec = {"schema": ("text", True), "id": ("text", True), "mode": ("text", True),
               "space": ("object|null", True), "problem": ("object", True), "alternatives": ("list", True),
               "comparison": ("list", False), "uncovered": ("list", False)}
_SPACE: _Spec = {"workspace": ("string", True), "run": ("string", True), "graph_sha256": ("text", True)}
_PROBLEM: _Spec = {"title": ("text", True), "context": ("string", False), "requirements": ("list", True)}
_REQUIREMENT: _Spec = {"id": ("text", True), "text": ("text", True), "kind": ("string", False),
                       "attribute": ("string|null", False)}
_ALTERNATIVE: _Spec = {"id": ("text", True), "name": ("string", True), "summary": ("string", False),
                       "choices": ("list", True), "considered": ("list", False), "open": ("list", False),
                       "relations": ("list", False), "point": ("object|null", False)}
_EVIDENCE: _Spec = {"doc": ("text", True), "stance": ("string", False)}
_RELATION: _Spec = {"source": ("text", True), "target": ("text", True), "type": ("text", True),
                    "holds": ("boolean", True), "note": ("string", False)}
_UNCOVERED: _Spec = {"decision": ("text", True), "solution_quote": ("text", True),
                     "nearest_dimension_id": ("string|null", False)}
_POINT: _Spec = {"description": ("string|null", False), "attested_by": ("list", False)}
# What a choice names: ids with a space, the agent's own labels without one.
_WITH_SPACE: _Spec = {"dimension_id": ("text", True), "value_id": ("text", True)}
_NO_SPACE: _Spec = {"decision": ("text", True), "option": ("text", True)}


def _decision(names: _Spec) -> _Spec:
    """Return the field that names the decision alone (``open``, ``comparison``): the dimension id, or the label."""
    key = next(iter(names))
    return {key: names[key]}


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


def names_space(doc: Any) -> bool:
    """Whether the file was written against a space (``space`` is an object), so it needs the graph."""
    return isinstance(doc, dict) and isinstance(doc.get("space"), dict)


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


class _Checker:
    """Collects problems and resolved labels while walking one rationale file."""

    def __init__(self, graph: Optional[q.Graph]):
        self.graph = graph
        self.problems: List[Dict[str, Any]] = []
        self.resolved: Dict[str, str] = {}
        self._relations: Optional[Dict[frozenset, List[Dict[str, Any]]]] = None  # {source, target} -> edges

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

    # ------------------------------------------------------------ the space

    def ref(self, obj: Mapping[str, Any], key: str, parts: Tuple[Any, ...],
            kinds: Sequence[str]) -> Optional[Dict[str, Any]]:
        """Resolve ``obj[key]`` against the graph; report unknown or non-canonical ids."""
        if self.graph is None or not self.good(obj, key):
            return None
        ref, path = obj[key], pointer(*parts, key)
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
            owner = self.graph["_by_id"].get(v.get("dimension_id"), {})
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
            self._relations = {}
            for e in self.graph.get("edges") or []:
                if e.get("type") == "relation":
                    self._relations.setdefault(frozenset((e.get("source"), e.get("target"))), []).append(e)
        between = self._relations.get(frozenset((a, b)), [])

        def matches(e: Mapping[str, Any]) -> bool:
            same_way = e.get("source") == a and e.get("target") == b
            return e.get("relation") == rel["type"] and (same_way or not e.get("directed"))

        if any(matches(e) for e in between):
            return
        found = [{"source": e.get("source"), "target": e.get("target"), "type": e.get("relation"),
                  "directed": bool(e.get("directed"))} for e in between]
        what = ("; the graph has " + ", ".join(
            f"{f['source']} {f['type']} {f['target']}" + ("" if f["directed"] else " (undirected)") for f in found)
            if found else "; the graph has no relation between them")
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
        """Check a cited passage's stance: one of ``q.STANCES`` and, with a space, the one the graph records.

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

    ``graph`` (from ``q.load``) enables the rules against the space; pass it only for a file that names a
    space (``names_space``). ``graph_sha256`` is the hash of that graph's file. Without a graph, only the
    structural rules run. ``ok`` is false when any problem is an error; warnings are allowed.
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
    with_space = isinstance(space, dict)
    if with_space and c.fields(space, ("space",), _SPACE):
        sha = space.get("graph_sha256")
        if graph_sha256 and isinstance(sha, str) and sha and sha != graph_sha256:
            c.add("graph_changed", "/space/graph_sha256",
                  f"the graph changed since the file was written (file {sha[:12]}…, graph {graph_sha256[:12]}…); "
                  "ids that still resolve are checked against the current graph")
    names = _WITH_SPACE if with_space else _NO_SPACE

    requirements = _requirements(c, doc.get("problem"))
    _alternatives(c, doc, mode, names, with_space, requirements)

    for i, item in enumerate(c.items(doc, "comparison")):
        parts = ("comparison", i)
        if c.fields(item, parts, {**_decision(names), "note": ("string", True)}):
            c.ref(item, "dimension_id", parts, ["dimension"])

    if mode == "explain" and "uncovered" not in doc:
        c.add("schema", "/uncovered", "missing uncovered (explain lists the decisions the space does not cover; "
                                      "use [] when every decision is mapped)")
    uncovered = c.items(doc, "uncovered")
    if uncovered and "space" in doc and space is None:
        c.add("schema", "/uncovered", "without a space (space: null) there is nothing to be uncovered by; "
                                      "leave uncovered empty")
    for i, item in enumerate(uncovered):
        parts = ("uncovered", i)
        if c.fields(item, parts, _UNCOVERED) and item.get("nearest_dimension_id") is not None:
            c.ref(item, "nearest_dimension_id", parts, ["dimension"])


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


def _drivers(c: _Checker, obj: Mapping[str, Any], parts: Tuple[Any, ...], requirements: set) -> None:
    for k, driver in enumerate(c.items(obj, "drivers")):
        path = pointer(*parts, "drivers", k)
        if not isinstance(driver, str):
            c.add("schema", path, f"expected a requirement id, got {_what(driver)}")
        elif driver not in requirements:
            known = ", ".join(sorted(requirements)) or "none"
            c.add("unknown_requirement", path, f"'{driver}' names no requirement (the requirements: {known})")


def _alternatives(c: _Checker, doc: Mapping[str, Any], mode: Any, names: _Spec, with_space: bool,
                  requirements: set) -> None:
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
    seen_ids: set = set()
    choice_spec: _Spec = {**names, "drivers": ("list", True), "reason": ("string", True),
                          "evidence": ("list", False), "solution_quote": ("string|null", False)}
    considered_spec: _Spec = {**names, "reason": ("string", True), "drivers": ("list", False)}
    open_spec: _Spec = {**_decision(names), "reason": ("string", True)}
    key_field = next(iter(names))
    for i, alt in enumerate(alts):
        if not c.fields(alt, ("alternatives", i), _ALTERNATIVE):
            continue
        if c.good(alt, "id"):
            if alt["id"] in seen_ids:
                c.add("schema", pointer("alternatives", i, "id"), f"duplicate alternative id '{alt['id']}'")
            seen_ids.add(alt["id"])
        if alt.get("point") is not None:
            c.fields(alt["point"], ("alternatives", i, "point"), _POINT)

        first: Dict[str, str] = {}
        value_ids: List[str] = []
        for j, choice in enumerate(c.items(alt, "choices")):
            parts = ("alternatives", i, "choices", j)
            if not c.fields(choice, parts, choice_spec):
                continue
            if mode == "explain" and "solution_quote" in choice and not c.good(choice, "solution_quote"):
                c.add("schema", pointer(*parts, "solution_quote"),
                      "explain quotes the solution on each choice: expected a non-empty string")
            elif mode == "explain" and "solution_quote" not in choice:
                c.add("schema", pointer(*parts, "solution_quote"), "missing solution_quote")
            _drivers(c, choice, parts, requirements)
            d, v = c.choice_ids(choice, parts) if with_space else (None, None)
            if v is not None:
                value_ids.append(v["id"])
            key = d["id"] if d is not None else (q.norm(choice[key_field]) if c.good(choice, key_field) else None)
            if key is not None and key in first:
                what = f"'{d.get('label')}' ({d['id']})" if d is not None else f"'{choice[key_field]}'"
                c.add("two_values_one_dimension", pointer(*parts),
                      f"a second choice for {what} in alternative '{alt.get('id')}' (the first is at "
                      f"{first[key]}): an alternative takes one value per dimension")
            elif key is not None:
                first[key] = pointer(*parts)
            for k, ev in enumerate(c.items(choice, "evidence")):
                ev_parts = (*parts, "evidence", k)
                if not c.fields(ev, ev_parts, _EVIDENCE):
                    continue
                if v is not None and c.good(ev, "doc"):
                    passages = v.get("passages") or []
                    if ev["doc"] not in {p.get("doc") for p in passages}:
                        c.add("evidence_not_on_value", pointer(*ev_parts),
                              f"passage '{ev['doc']}' is not among the passages of '{v.get('label')}' ({v['id']})",
                              [{"doc": p.get("doc"), "stance": p.get("stance")} for p in passages])
                c.stance(ev, ev_parts, v)

        for j, item in enumerate(c.items(alt, "considered")):
            parts = ("alternatives", i, "considered", j)
            if c.fields(item, parts, considered_spec):
                _drivers(c, item, parts, requirements)
                if with_space:
                    c.choice_ids(item, parts)
        for j, item in enumerate(c.items(alt, "open")):
            parts = ("alternatives", i, "open", j)
            if c.fields(item, parts, open_spec):
                c.ref(item, "dimension_id", parts, ["dimension"])
        for j, rel in enumerate(c.items(alt, "relations")):
            parts = ("alternatives", i, "relations", j)
            if c.fields(rel, parts, _RELATION) and c.graph is not None:
                c.relation(rel, parts)
        c.unmet_requires(value_ids, ("alternatives", i))


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
