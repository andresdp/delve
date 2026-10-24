"""``ddspace import``: make a design space built elsewhere the workspace's current run.

Two kinds of input. ``run`` is a taxonomy JSON from an earlier mining run (with its corpus and sources
when available). ``decision-model`` is an expert decision model in the ground-truth format
(``benchmark/gt_format.py``): decisions become dimensions, options become values and decision links become
relations. Forces and impacts are not imported, and there are no passages, so the wiki shows the model
without evidence.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from delvedspace import runs
from delvedspace.wiki_build import run_sources, selected_dims
from delvedspace.workspace import Workspace, WorkspaceError, read_json
from taxonomy_generator.relations import clean_relations

KINDS = ("run", "decision-model")
RUN_KINDS = {"run": "import-run", "decision-model": "import-model"}  # run.json marker per input kind
LINK_TYPE = "affects"   # expert links ("consider B once A is decided") advise; they do not require
# Wiki settings for a model without passages: nothing to quote, no systems to sample points from, and every
# dimension is core (no evidence counts to rank them by).
MODEL_WIKI = {"quotes": False, "design_points": "none", "core_min_sources": 0}


def _read(path: Path) -> Any:
    if not path.is_file():
        raise WorkspaceError(f"{path} is not a file.")
    try:
        return read_json(path)
    except ValueError as exc:
        raise WorkspaceError(f"{path} is not valid JSON: {exc}") from exc


def _taxonomy_file(path: Path, name: str, run_id: str) -> str:
    """Keep a run's file name when ``runs.find_taxonomy`` would find it, else name it like a pipeline run."""
    probe = Path(path.name)
    if probe.match("*_taxonomy_*.json") and not any(m in probe.stem for m in runs._ARTIFACT_MARKERS):
        return path.name
    return f"{name}_taxonomy_{run_id}.json"


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
    dims, _dropped = clean_relations(dims)
    return {"taxonomy_name": name, "selected_clusters": dims, "iterations": [{"clusters": dims}],
            "dropped_dimensions": [], "provenance": {"kind": "decision model", "study": model.get("study")}}


def import_space(ws: Workspace, path: Path, kind: str, corpus: Optional[Path] = None,
                 sources: Optional[Path] = None) -> Path:
    """Import ``path`` as the current run; return the new run folder."""
    if kind not in KINDS:
        raise WorkspaceError(f"Unknown kind {kind!r}: use one of {', '.join(KINDS)}.")
    for extra in (corpus, sources):
        if extra is not None and not extra.is_file():
            raise WorkspaceError(f"{extra} is not a file.")
    data = _read(path)
    name = path.stem.split("_taxonomy_")[0] or ws.root.name
    if kind == "run":
        if not selected_dims(data):
            raise WorkspaceError(f"{path} has no design space (no selected_clusters or iterations).")
        taxonomy = data
    else:
        if not data.get("decisions"):
            raise WorkspaceError(f"{path} has no decisions; is it a decision model (ground-truth format)?")
        taxonomy = model_to_taxonomy(data, name=name)
    run_id = runs.now_id()
    if sources is not None and sources.resolve() != ws.sources_csv.resolve():
        shutil.copy2(sources, ws.sources_csv)
    run_dir = runs.adopt(ws, taxonomy, _taxonomy_file(path, name, run_id), RUN_KINDS[kind],
                         run_sources(selected_dims(taxonomy)), corpus=corpus)
    if kind == "decision-model":
        for key, value in MODEL_WIKI.items():
            ws.set(f"wiki.{key}", value)
    return run_dir
