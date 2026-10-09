#!/usr/bin/env python3
r"""Export one Delve run as a browsable design-space wiki (docs/DESIGN_SPACE_EXPLORATION.md §13).

Writes, into ``--out`` (default ``<run folder>/<run>_wiki/``):

- ``wiki/``: markdown pages with YAML frontmatter and ``[[wikilinks]]`` in the
  llmwiki-cli layout (``concepts/`` dimensions, ``entities/`` options, ``sources/``,
  ``synthesis/`` with an overview that includes the use case, a run summary and the
  run's narrative summary; ``designs/`` when design points are given; an evaluation
  page with ``--evaluation``), also an Obsidian vault;
- ``html/``: the same pages as static HTML plus ``graph.html``, an interactive graph.
  Everything opens from ``file://`` (no server, no internet);
- ``.llmwiki.yaml``, ``SCHEMA.md``, ``raw/run.json`` (inputs and options).

No LLM calls: pages are rendered from the run data. Value pages quote the
supporting passages when ``--corpus`` is given. Those quotes are third-party
text, so such exports are gitignored; use ``--no-quotes`` for a version that can
be shared publicly.

Usage::

    python benchmark/export_wiki.py examples/c3-git-at-scale/c3-git-at-scale_taxonomy_20261008_115350.json \\
        --corpus examples/c3-git-at-scale/c3-git-at-scale_corpus.json \\
        --sources benchmark/c3-git-at-scale/sources.csv \\
        --systems benchmark/c3-git-at-scale/passage_systems.csv \\
        --system-names benchmark/c3-git-at-scale/systems.csv \\
        --design-points examples/c3-git-at-scale/c3-git-at-scale_taxonomy_20261008_115350_design_points.json \\
        --config examples/c3-git-at-scale/c3_git_at_scale_config.yaml --evaluation
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO / "src"))

import yaml  # noqa: E402

from taxonomy_generator.html_report import (  # noqa: E402
    _extract_narrative_summary, _extract_timestamp, resolve_report_path)
from taxonomy_generator.evaluation.design_points import load_system_map as dp_system_map, sample_points  # noqa: E402
from taxonomy_generator.wiki import Inputs, build, write  # noqa: E402
from taxonomy_generator.wiki.model import (  # noqa: E402
    load_corpus, load_sources, load_system_map, load_system_names)

EXPORTER_VERSION = "1"


def _rel(path) -> str | None:
    if not path:
        return None
    p = Path(path).resolve()
    try:
        return str(p.relative_to(REPO))
    except ValueError:
        return str(p)


def main(argv=None) -> int:
    """Run the command line; return the exit code."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("taxonomy", help="saved run (*_taxonomy_<timestamp>.json)")
    ap.add_argument("--corpus", help="the run's corpus JSON (passage texts for quotes and section titles)")
    ap.add_argument("--sources", help="sources.csv (id, title, url, source_type)")
    ap.add_argument("--systems", help="passage → system map (B7 CSV); adds system pages and the system matrix")
    ap.add_argument("--system-names", help="systems.csv (code, name, organization, description)")
    ap.add_argument("--design-points", help="*_design_points.json from benchmark/design_points.py (optional layer)")
    ap.add_argument("--sample-design-points", action="store_true",
                    help="sample design points now (no LLM; same sampler as benchmark/design_points.py; "
                         "attested group from --systems, by primary system) instead of reading --design-points")
    ap.add_argument("--dp-k", type=int, nargs="+", default=[2, 3], help="with --sample-design-points: dimensions per point")
    ap.add_argument("--dp-n", type=int, default=30, help="with --sample-design-points: points per group and k")
    ap.add_argument("--dp-seed", type=int, default=42, help="with --sample-design-points: seed")
    ap.add_argument("--config", help="the run's YAML config (for the use case shown on the index and overview)")
    ap.add_argument("--report", help="the run's report .md (narrative summary for the overview); "
                                     "default: the sibling *_report_<timestamp>.md, if any")
    ap.add_argument("--evaluation", action="store_true",
                    help="add a page with the run's evaluation (criteria scores, reasons, scores across iterations)")
    ap.add_argument("--case-icon", help="SVG icon of the case study (default: icon.svg in the --sources folder, if any)")
    ap.add_argument("--view", choices=["selected", "final"], default="selected")
    ap.add_argument("--no-quotes", action="store_true", help="passage ids only, no quoted text (shareable export)")
    ap.add_argument("--quote-words", type=int, default=60)
    ap.add_argument("--out", type=Path, help="output folder (default: <run folder>/<run>_wiki)")
    args = ap.parse_args(argv)
    if args.design_points and args.sample_design_points:
        ap.error("use either --design-points <file> or --sample-design-points, not both")

    path = Path(args.taxonomy)
    taxonomy = json.loads(path.read_text(encoding="utf-8"))
    m = re.search(r"_taxonomy_(\d{8}_\d{6})", path.name)
    run_label = m.group(1) if m else path.stem
    name = taxonomy.get("taxonomy_name") or path.stem.split("_taxonomy_")[0]
    use_case, models = "", {}
    if args.config:
        cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8")) or {}
        use_case = ((cfg.get("taxonomy") or {}).get("use_case") or "").strip()
        models = {k: str(v) for k, v in (cfg.get("models") or {}).items()
                  if k in ("generation_llm", "evaluation_llm", "embedding") and v}
    judge = (taxonomy.get("evaluation") or {}).get("model")
    if judge and not models.get("evaluation_llm"):
        models["evaluation_llm"] = str(judge)
    case_icon = Path(args.case_icon) if args.case_icon else None
    if case_icon is None and args.sources and (Path(args.sources).parent / "icon.svg").exists():
        case_icon = Path(args.sources).parent / "icon.svg"

    report = Path(args.report) if args.report else None
    if report is None:
        found = resolve_report_path(path.parent, name, run_label if m else None)
        # only the report of this exact run (same timestamp); never another run's narrative
        report = found.path if found and m and _extract_timestamp(found.path) == run_label else None
    narrative = ""
    if report and report.exists():
        narrative = _extract_narrative_summary(report.read_text(encoding="utf-8")) or ""

    design_points = None
    if args.design_points:
        design_points = json.loads(Path(args.design_points).read_text(encoding="utf-8"))
    elif args.sample_design_points:
        view = taxonomy.get("selected_clusters") if args.view == "selected" else \
            ((taxonomy.get("iterations") or [{}])[-1].get("clusters"))
        doc_systems = dp_system_map(Path(args.systems), "primary") if args.systems else None
        design_points = {"run": _rel(path), "systems": _rel(args.systems), "attest_by": "primary" if args.systems else None,
                         "seed": args.dp_seed, "n": args.dp_n,
                         "samples": sample_points(view or [], doc_systems, args.dp_k, args.dp_n, args.dp_seed)}

    inp = Inputs(
        taxonomy=taxonomy, taxonomy_name=name, run_label=run_label,
        corpus=load_corpus(Path(args.corpus)) if args.corpus else {},
        sources=load_sources(Path(args.sources)) if args.sources else {},
        systems=load_system_map(Path(args.systems)) if args.systems else {},
        system_names=load_system_names(Path(args.system_names)) if args.system_names else {},
        design_points=design_points,
        use_case=use_case, narrative=narrative, evaluation=args.evaluation, models=models,
        case_icon=case_icon is not None, view=args.view, quotes=not args.no_quotes, quote_words=args.quote_words)
    export = build(inp)
    export.manifest = {
        "exporter_version": EXPORTER_VERSION, "taxonomy": _rel(path), "run": run_label, "view": args.view,
        "corpus": _rel(args.corpus), "sources": _rel(args.sources), "systems": _rel(args.systems),
        "system_names": _rel(args.system_names), "design_points": _rel(args.design_points) or ("sampled at export (k=%s, n=%d, seed=%d)" % (
            " ".join(map(str, args.dp_k)), args.dp_n, args.dp_seed) if args.sample_design_points else None),
        "config": _rel(args.config), "report": _rel(report), "case_icon": _rel(case_icon), "models": models, "evaluation": args.evaluation, "quotes": not args.no_quotes, "quote_words": args.quote_words,
        "pages": len(export.pages), "graph_nodes": len(export.graph["nodes"]), "graph_edges": len(export.graph["edges"]),
    }
    out = args.out or path.parent / f"{path.with_suffix('').name}_wiki"
    write(export, out, name, case_icon)
    kinds = {}
    for p in export.pages:
        kinds[p.kind] = kinds.get(p.kind, 0) + 1
    print(f"{len(export.pages)} pages ({', '.join(f'{k} {v}' for k, v in sorted(kinds.items()))}); "
          f"graph {len(export.graph['nodes'])} nodes, {len(export.graph['edges'])} edges")
    print(f"-> {out}/html/index.html (graph: html/graph.html)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
