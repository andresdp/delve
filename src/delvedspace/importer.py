"""``ddspace import``: make a design space built elsewhere the workspace's current run.

Three kinds of input. ``run`` is a taxonomy JSON from an earlier mining run (with its corpus and sources
when available). ``decision-model`` is an expert decision model in the ground-truth format
(``benchmark/gt_format.py``): decisions become dimensions, options become values and decision links become
relations. Forces and impacts are not imported, and there are no passages, so the wiki shows the model
without evidence. ``space`` is a design space written by hand, in YAML or JSON (:func:`space_to_taxonomy`):
a name and dimensions with their values (relations between dimensions are optional); it has no passages either.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from delvedspace import runs
from delvedspace.wiki_build import run_sources, selected_dims
from delvedspace.workspace import Workspace, WorkspaceError, read_json
from taxonomy_generator.relations import clean_relations

KINDS = ("run", "decision-model", "space")
RUN_KINDS = {"run": runs.IMPORT_RUN, "decision-model": runs.IMPORT_MODEL,   # run.json marker per input kind
             "space": runs.IMPORT_SPACE}
NO_PASSAGES = ("decision-model", "space")
LINK_TYPE = "affects"   # expert links ("consider B once A is decided") advise; they do not require
# Wiki settings for a model without passages: nothing to quote, no systems to sample points from, and every
# dimension is core (no evidence counts to rank them by).
MODEL_WIKI = {"quotes": False, "design_points": "none", "core_min_sources": 0}


def _read(path: Path) -> Any:
    if not path.is_file():
        raise WorkspaceError(f"{path} is not a file.")
    if path.suffix.lower() in (".yaml", ".yml"):
        import yaml
        try:
            return yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise WorkspaceError(f"{path} is not valid YAML: {exc}") from exc
    try:
        return read_json(path)
    except ValueError as exc:
        raise WorkspaceError(f"{path} is not valid JSON: {exc}") from exc


def _taxonomy_file(path: Path, name: str, run_id: str) -> str:
    """Keep a run's file name when ``runs.find_taxonomy`` would find it, else name it like a pipeline run."""
    if runs.is_taxonomy_name(path.name):
        return path.name
    for stem in (name, "import"):     # a name with an artifact marker (e.g. "_metrics") would hide the file
        candidate = f"{stem}_taxonomy_{run_id}.json"
        if runs.is_taxonomy_name(candidate):
            return candidate
    return f"import_taxonomy_{run_id}.json"


def model_to_taxonomy(model: Dict[str, Any], name: str) -> Dict[str, Any]:
    """Return a decision model as a run taxonomy (the inverse of ``evaluation_report.taxonomy_to_gt``)."""
    decisions = model.get("decisions") or []
    dim_ids = {d["id"]: str(i) for i, d in enumerate(decisions, 1)}
    dims: List[Dict[str, Any]] = [
        {"id": dim_ids[d["id"]], "name": d.get("name") or d["id"],
         "description": d.get("description") or d.get("question") or "",
         "relations": [], "evidence": {"codes": 0, "documents": 0, "sources": 0}, "values": [],
         "external_id": d["id"]}
        for d in decisions]
    by_id = {d["external_id"]: d for d in dims}
    for option in model.get("options") or []:
        if option.get("unattached"):
            continue
        for decision_id in option.get("decision_ids") or []:
            dim = by_id.get(decision_id)
            if dim is None:
                continue
            dim["values"].append({"id": f"{dim['id']}.{len(dim['values']) + 1}", "label": option.get("name") or option["id"],
                                  "description": option.get("description") or "", "status": "accepted",
                                  "supporting_doc_ids": [], "external_id": option["id"]})
    for link in model.get("decision_links") or []:
        source, target = by_id.get(link.get("from")), by_id.get(link.get("to"))
        if source is not None and target is not None and source is not target:
            source["relations"].append({"target_id": target["id"], "type": LINK_TYPE,
                                        "rationale": link.get("label") or ", ".join(link.get("stereotypes") or [])})
    dims, dropped = clean_relations(dims)       # opposite pairs and duplicates are dropped, and counted
    return {"taxonomy_name": name, "selected_clusters": dims, "iterations": [{"clusters": dims}],
            "dropped_dimensions": [], "provenance": {"kind": "decision model", "study": model.get("study"),
                                                     "relations_dropped": len(dropped)}}


def space_to_taxonomy(spec: Dict[str, Any], name: str) -> Dict[str, Any]:
    """Return a hand-written design space as a run taxonomy; raise :class:`WorkspaceError` with what is wrong.

    The file has a ``name`` and ``dimensions``, each with a ``name`` and its ``values``; descriptions, ids and
    ``relations`` are optional::

        name: git-hosting
        dimensions:
          - id: storage                       # optional; relations may name a dimension by id or by name
            name: Source of truth for repository state
            description: Where the authoritative copy of each repository lives.
            values:
              - name: Repository files on server disks
                description: Plain Git repositories on local disks are the authority.
              - Write-ahead log in object storage          # a value may be just its name
        relations:
          - {from: replication, to: storage, type: requires, note: What is replicated follows from where state lives.}

    Relation types: ``requires``, ``constrains``, ``affects``, ``co_occurs_with``.
    """
    if not isinstance(spec, dict) or not isinstance(spec.get("dimensions"), list) or not spec["dimensions"]:
        raise WorkspaceError("a design space file needs a list of dimensions (see `ddspace import --help`).")
    dims: List[Dict[str, Any]] = []
    keys: Dict[str, Dict[str, Any]] = {}
    for i, d in enumerate(spec["dimensions"], 1):
        if not isinstance(d, dict) or not str(d.get("name") or "").strip():
            raise WorkspaceError(f"dimension {i} has no name.")
        values, labels = [], set()
        for j, v in enumerate(d.get("values") or [], 1):
            v = {"name": v} if isinstance(v, str) else (v or {})
            label = str(v.get("name") or v.get("label") or "").strip()
            if not label:
                raise WorkspaceError(f"dimension {d['name']!r}: value {j} has no name.")
            if label.lower() in labels:
                raise WorkspaceError(f"dimension {d['name']!r}: value {label!r} appears twice.")
            labels.add(label.lower())
            values.append({"id": f"{i}.{j}", "label": label, "description": str(v.get("description") or ""),
                           "status": "accepted", "supporting_doc_ids": []})
        if not values:
            raise WorkspaceError(f"dimension {d['name']!r} has no values: a dimension needs its alternatives.")
        dim = {"id": str(i), "name": str(d["name"]).strip(),
               "description": str(d.get("description") or d.get("question") or ""), "relations": [],
               "evidence": {"codes": 0, "documents": 0, "sources": 0}, "values": values}
        for key in (d.get("id"), d["name"]):
            if key is not None:
                if keys.get(str(key).strip().lower(), dim) is not dim:
                    raise WorkspaceError(f"two dimensions are called {str(key)!r}.")
                keys[str(key).strip().lower()] = dim
        dims.append(dim)
    for k, r in enumerate(spec.get("relations") or [], 1):
        if not isinstance(r, dict):
            raise WorkspaceError(f"relation {k} is not a mapping with from, to and type.")
        source, target = (keys.get(str(r.get(end) or "").strip().lower()) for end in ("from", "to"))
        if source is None or target is None:
            missing = r.get("from") if source is None else r.get("to")
            raise WorkspaceError(f"relation {k}: no dimension called {missing!r}.")
        source["relations"].append({"target_id": target["id"], "type": r.get("type"),
                                    "rationale": str(r.get("note") or r.get("rationale") or "")})
    dims, dropped = clean_relations(dims)
    bad = [d for d in dropped if "unknown relation type" in str(d.get("reason", ""))]
    if bad:
        raise WorkspaceError(f"{bad[0].get('reason')}: use requires, constrains, affects or co_occurs_with.")
    return {"taxonomy_name": str(spec.get("name") or name), "selected_clusters": dims,
            "iterations": [{"clusters": dims}], "dropped_dimensions": [],
            "provenance": {"kind": "curated", "relations_dropped": len(dropped)}}


def import_space(ws: Workspace, path: Path, kind: str, corpus: Optional[Path] = None,
                 sources: Optional[Path] = None) -> Path:
    """Import ``path`` as the current run; return the new run folder."""
    if kind not in KINDS:
        raise WorkspaceError(f"Unknown kind {kind!r}: use one of {', '.join(KINDS)}.")
    if kind in NO_PASSAGES and (corpus or sources):
        raise WorkspaceError(f"--corpus and --sources go with --kind run; a {kind} has no passages.")
    if sources is not None and not sources.is_file():
        raise WorkspaceError(f"{sources} is not a file.")
    passages = _read(corpus) if corpus is not None else []        # validated before anything is written
    if not isinstance(passages, list):
        raise WorkspaceError(f"{corpus} is not a corpus (a JSON list of passages).")
    data = _read(path)
    name = path.stem.split("_taxonomy_")[0] or ws.root.name
    if kind == "run":
        if not selected_dims(data):
            raise WorkspaceError(f"{path} has no design space (no selected_clusters or iterations).")
        taxonomy = data
    elif kind == "space":
        taxonomy = space_to_taxonomy(data, name=name)
        if str((data or {}).get("name") or "").strip():               # the file names its space
            ws.set("taxonomy.name", str(data["name"]).strip())
    else:
        if not data.get("decisions"):
            raise WorkspaceError(f"{path} has no decisions; is it a decision model (ground-truth format)?")
        taxonomy = model_to_taxonomy(data, name=name)
    run_id = runs.now_id()
    run_dir = runs.adopt(ws, taxonomy, _taxonomy_file(path, name, run_id), RUN_KINDS[kind],
                         run_sources(selected_dims(taxonomy)), passages=passages)
    if sources is not None and sources.resolve() != ws.sources_csv.resolve():
        shutil.copy2(sources, ws.sources_csv)
    for key, value in MODEL_WIKI.items():   # model-only answers; a run import asks (or defaults) again
        ws.set(f"wiki.{key}", value if kind in NO_PASSAGES else None)
    return run_dir
