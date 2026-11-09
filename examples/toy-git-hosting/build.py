#!/usr/bin/env python3
r"""Build the toy Git-hosting design space from ``spec.yaml``: a run file, then a workspace with its wiki.

The dimensions and values are curated by hand (``spec.yaml``); each value inherits the passages and stances of
the C3 mined values it names in ``from``, so the evidence is the pipeline's, not ours.

Usage::

    # write toy-git-hosting_taxonomy_<stamp>.json next to this file (needs the C3 mined run in output/)
    python examples/toy-git-hosting/build.py taxonomy
    # build a workspace from it (outside the repository), with the C3 source list
    python examples/toy-git-hosting/build.py workspace --out ~/Documents/GitHub/ddspace-sandboxes/toy-git-hosting
"""

from __future__ import annotations

import argparse
import glob
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SPEC = HERE / "spec.yaml"
STAMP = "20261109_000000"   # fixed, so the file name is stable across rebuilds


def _mined(spec: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    found = glob.glob(str(REPO / spec["mined_run"] / "*_taxonomy_*.json"))
    if len(found) != 1:
        sys.exit(f"expected one mined taxonomy in {spec['mined_run']}, found {len(found)}")
    taxonomy = json.loads(Path(found[0]).read_text(encoding="utf-8"))
    return {v["id"]: v for c in taxonomy["selected_clusters"] for v in c["values"]}


def _value(v: Dict[str, Any], dim: str, mined: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    docs: List[str] = []
    accepted: List[str] = []
    rejected: List[str] = []
    for ref in v["from"]:
        if ref not in mined:
            sys.exit(f"value {v['id']}: no mined value {ref}")
        m = mined[ref]
        stances = m.get("stances") or {}
        for d in m.get("supporting_doc_ids") or []:
            if d not in docs:
                docs.append(d)
            in_acc, in_rej = d in (stances.get("accepted") or []), d in (stances.get("rejected") or [])
            if not stances:   # no recorded stance: the mined value's status decides it
                in_rej, in_acc = m.get("status") == "rejected", m.get("status") != "rejected"
            if in_acc and d not in accepted:
                accepted.append(d)
            if in_rej and d not in rejected:
                rejected.append(d)
    status = v.get("status") or ("mixed" if accepted and rejected else "rejected" if rejected else "accepted")
    out = {"id": v["id"], "dimension_id": dim, "label": v["label"], "description": v["description"],
           "supporting_doc_ids": docs, "merged_from": [], "status": status,
           "evidence_code_count": len(v["from"])}
    stances = {k: x for k, x in (("accepted", accepted), ("rejected", rejected)) if x}
    if stances:
        out["stances"] = stances
    return out


def taxonomy(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Return the run file: the curated dimensions as selected clusters, with inherited evidence."""
    mined = _mined(spec)
    clusters = []
    for d in spec["dimensions"]:
        values = [_value(v, d["id"], mined) for v in d["values"]]
        docs = {x for v in values for x in v["supporting_doc_ids"]}
        relations = [{"target_id": r["target"], "type": r["type"], "reading": r["reading"],
                      "rationale": r["rationale"]} for r in spec["relations"] if r["source"] == d["id"]]
        clusters.append({"id": d["id"], "name": d["name"], "description": d["description"],
                         "relations": relations, "values": values,
                         "evidence": {"codes": sum(v["evidence_code_count"] for v in values),
                                      "documents": len(docs), "sources": len({x.split("_")[0] for x in docs})}})
    return {"taxonomy_name": spec["name"], "run_metrics": {}, "selected_clusters": clusters,
            "dropped_dimensions": [], "evaluation": {}, "iterations": [{"explanation": spec["title"],
                                                                         "clusters": clusters}]}


def _ddspace(cwd: Path, *args: str) -> None:
    cmd = [sys.executable, "-c", "from delvedspace.cli import app; app()", *args]
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit(f"ddspace {' '.join(args)} failed in {cwd}:\n{proc.stdout}\n{proc.stderr}")


def workspace(spec: Dict[str, Any], run_file: Path, out: Path) -> Path:
    """Build a workspace at ``out`` from the run file: import, wiki (no LLM, no quotes), agent guide."""
    out = out.expanduser().resolve()
    if REPO in out.parents or out == REPO:
        sys.exit("Build the workspace outside the repository, so agents working in it cannot read the repository.")
    shutil.rmtree(out, ignore_errors=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    _ddspace(out.parent, "init", str(out), "--yes", "--name", spec["name"])
    _ddspace(out, "import", str(run_file), "--kind", "run", "--sources", str(REPO / spec["sources"]), "--yes")
    from delvedspace.workspace import Workspace
    w = Workspace(out)
    for key, value in (("design_points", "none"), ("quotes", False), ("source_summaries", False)):
        w.set(f"wiki.{key}", value)
    _ddspace(out, "wiki", "build", "--yes", "--no-llm")
    _ddspace(out, "agent", "setup", "--yes")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("taxonomy", help="write the run file next to this script")
    ws = sub.add_parser("workspace", help="build a workspace from the run file")
    ws.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    spec = yaml.safe_load(SPEC.read_text(encoding="utf-8"))
    run_file = HERE / f"{spec['name']}_taxonomy_{STAMP}.json"
    if args.cmd == "taxonomy":
        run_file.write_text(json.dumps(taxonomy(spec), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(run_file)
    else:
        if not run_file.is_file():
            sys.exit(f"no {run_file.name}: run the taxonomy step first")
        print(workspace(spec, run_file, args.out))


if __name__ == "__main__":
    main()
