#!/usr/bin/env python3
"""Score the study designs against the C1 expert model.

Every alternative a design considers is matched to the expert model's attached options with the
ground-truth matcher (``taxonomy_generator.evaluation.gt_match``: embeddings propose pairs, the pinned judge
decides, verdicts cached). From those matches and the session summary, per session:

- decision coverage: expert decisions with at least one matched alternative, over all expert decisions;
- alternatives per decision, and the share of alternatives that match an expert option;
- requirements fit: per touched expert decision, (chosen - worst) / (best - worst) of the summed expert impacts on
  the brief's forces (missing impact = 0; ties excluded; a choice that matches no option of that decision is
  "unmatched"), averaged over the qualifying decisions;
- grounding (M, E): share of choices with a citation, and share of citations that exist in the condition's graph;
- consistency (M, E): warnings of ``ddspace point`` on the chosen value ids, plus ids that do not exist;
- design points explored (M, E) and cost (tokens priced from a dated rate table).

Usage::

    python study/cain2027/score.py [--workspaces <folder>] [--export-labels]
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import sys
from pathlib import Path
from statistics import mean
from typing import Any, Callable, Dict, List, Mapping, Optional, Set

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import design  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
INPUTS = HERE / "inputs"
RATES = HERE / "rates.yaml"
SPACE_CONDITIONS = design.SPACE_CONDITIONS
IMPACT = {"++": 2, "+": 1, "o": 0, "+/-": 0, "-": -1, "--": -2}
SUMMARY_FIELDS = ("complete", "tokens", "points")


def _gt_items(gt: Mapping[str, Any]):
    from taxonomy_generator.evaluation.gt_match import ground_truth_options
    return ground_truth_options({"model": dict(gt)})


def check_briefs(briefs: List[Mapping[str, Any]], gt: Mapping[str, Any]) -> None:
    """Refuse briefs whose forces are not expert force ids, or touch no expert decision."""
    forces = {f["id"] for f in gt.get("forces") or []}
    attached = {o["id"] for o in gt.get("options") or [] if o.get("decision_ids") and not o.get("unattached")}
    for b in briefs:
        unknown = [f for f in b.get("forces") or [] if f not in forces]
        if unknown or not b.get("forces"):
            raise ValueError(f"brief {b['id']}: unknown or missing force ids {unknown}")
        if not any(i["force_id"] in b["forces"] and i["option_id"] in attached for i in gt.get("impacts") or []):
            raise ValueError(f"brief {b['id']}: its forces have no impact on any expert decision")


def check_summary(summary: Mapping[str, Any]) -> None:
    """Refuse a session summary without the fields scoring needs (the point events among them)."""
    missing = [f for f in SUMMARY_FIELDS if f not in summary]
    if missing:
        raise ValueError(f"session summary lacks {', '.join(missing)} (point events are required)")


def _item_id(i: int, j: int) -> str:
    """Matcher item id of alternative ``j`` of decision ``i``."""
    return f"d{i}a{j}"


def _chosen_index(dec: Mapping[str, Any]) -> Optional[int]:
    """Index of the chosen alternative among the considered ones (None when the choice is not among them)."""
    labels = [a["label"] for a in dec["alternatives"]]
    return labels.index(dec["chosen"]["label"]) if dec["chosen"]["label"] in labels else None


def design_items(doc: Mapping[str, Any]) -> list:
    """One matcher item per considered alternative (plus the chosen one when it is not among them)."""
    from taxonomy_generator.evaluation.gt_match import Item
    items = []
    for i, dec in enumerate(doc["decisions"]):
        labels = [a["label"] for a in dec["alternatives"]]
        if _chosen_index(dec) is None:
            labels.append(dec["chosen"]["label"])
        for j, label in enumerate(labels):
            items.append(Item(id=_item_id(i, j), name=label, description="", parent_ids=[f"d{i}"],
                              parent_name=dec["decision"]))
    return items


def _chosen_item(doc: Mapping[str, Any], i: int) -> str:
    dec = doc["decisions"][i]
    j = _chosen_index(dec)
    return _item_id(i, len(dec["alternatives"]) if j is None else j)


def match(doc: Mapping[str, Any], gt: Mapping[str, Any], config, *, embed: Optional[Callable] = None,
          judge_model: Any = None, cache: Any = None, options: Optional[list] = None,
          label_sources: Optional[Dict[str, int]] = None) -> Dict[str, Set[str]]:
    """Return the expert options each design item matches (same, broader or narrower).

    Pass ``embed``, ``judge_model``, ``cache`` and ``options`` to reuse them across sessions; a cache created
    here is saved here, a passed one is saved by the caller.
    """
    from taxonomy_generator.evaluation import gt_match
    from taxonomy_generator.evaluation.judge import openai_judge_model
    items = design_items(doc)
    options = options if options is not None else _gt_items(gt)
    embed = embed or gt_match.embedder_from_config(config)
    if judge_model is None and config.mode == "judge":
        judge_model = openai_judge_model(gt_match.check_matching_llm(config.matching_llm))
    own_cache = cache is None
    cache = gt_match.JudgeCache(config.cache_path) if own_cache else cache
    pairs = asyncio.run(gt_match.label_pairs(items, options, embed, judge_model, config, cache=cache))
    if own_cache:
        cache.save()
    hits: Dict[str, Set[str]] = {i.id: set() for i in items}
    if label_sources is not None:        # auto, auto_rank, judge, judge_error: judge failures must stay visible
        for p in pairs:
            label_sources[p["label_source"]] = label_sources.get(p["label_source"], 0) + 1
    for p in pairs:
        if p["label"] in gt_match.HIT_LABELS:
            hits[p["system_id"]].add(p["gt_id"])
    return hits


def _option_sums(gt: Mapping[str, Any], forces: List[str]) -> Dict[str, int]:
    sums = {o["id"]: 0 for o in gt.get("options") or []}
    for i in gt.get("impacts") or []:
        if i["force_id"] in forces and i["option_id"] in sums:
            sums[i["option_id"]] += IMPACT.get(str(i["impact"]).strip(), 0)
    return sums


def _fit(doc, hits, gt, brief) -> Dict[str, Any]:
    decision_of = {o["id"]: o.get("decision_ids") or [] for o in gt.get("options") or [] if not o.get("unattached")}
    options_of: Dict[str, List[str]] = {}
    for oid, decs in decision_of.items():
        for d in decs:
            options_of.setdefault(d, []).append(oid)
    sums = _option_sums(gt, brief["forces"])
    fit, unmatched, ties, matched = {}, 0, 0, 0
    seen: Set[str] = set()       # each expert decision is classified once, by the first design decision touching it
    for i, dec in enumerate(doc["decisions"]):
        items = [k for k in hits if k.startswith(f"d{i}a")]
        touched = []
        for k in items:
            for oid in sorted(hits[k]):
                touched += [d for d in decision_of.get(oid, []) if d not in touched]
        chosen = hits.get(_chosen_item(doc, i), set())
        for d in touched:
            if d in seen:
                continue
            seen.add(d)
            mine = [o for o in chosen if d in decision_of.get(o, [])]
            if not mine:
                unmatched += 1
                continue
            matched += 1
            scores = [sums[o] for o in options_of.get(d, [])]
            best, worst = max(scores), min(scores)
            if best == worst:
                ties += 1
                continue
            fit[d] = (mean(sums[o] for o in mine) - worst) / (best - worst)
    return {"fit_by_decision": fit, "requirements_fit": mean(fit.values()) if fit else None,
            "choices_matched": matched, "choices_unmatched": unmatched, "fit_excluded_ties": ties}


def _graph_ids(graph: Mapping[str, Any]) -> Set[str]:
    ids = {n["id"] for n in graph.get("nodes") or []}
    for n in graph.get("nodes") or []:
        ids |= {p.get("doc") for p in n.get("passages") or [] if p.get("doc")}
    return ids


def _consistency(doc, graph) -> Dict[str, Any]:
    from taxonomy_generator.wiki import query as q
    loaded = graph if "_by_id" in graph else {**graph, "_by_id": {n["id"]: n for n in graph.get("nodes") or []}}
    ids = [d["chosen"]["value_id"] for d in doc["decisions"] if d["chosen"].get("value_id")]
    known = [i for i in ids if i in loaded["_by_id"]]
    warnings = 0
    if known:
        try:
            warnings = len(q.point(loaded, known)["warnings"])
        except q.QueryError:
            pass
    return {"consistency_warnings": warnings, "unknown_value_ids": len(ids) - len(known), "value_ids_used": len(ids)}


def _cost(summary, rates) -> Optional[float]:
    rate = ((rates or {}).get("models") or {}).get(summary.get("model"))
    if not rate:
        return None
    t = summary["tokens"]
    fresh = max(0, t.get("input", 0) - t.get("cached_input", 0))
    return (fresh * rate["input"] + t.get("cached_input", 0) * rate.get("cached_input", rate["input"])
            + t.get("output", 0) * rate["output"]) / 1e6


def metrics(doc: Mapping[str, Any], hits: Mapping[str, Set[str]], gt: Mapping[str, Any], brief: Mapping[str, Any],
            condition: str, *, graph: Optional[Mapping[str, Any]] = None, summary: Optional[Mapping[str, Any]] = None,
            rates: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """Return the study metrics of one session (see the module docstring)."""
    decisions = {d["id"] for d in gt.get("decisions") or []}
    decision_of = {o["id"]: o.get("decision_ids") or [] for o in gt.get("options") or []}
    matched = {d for opts in hits.values() for o in opts for d in decision_of.get(o, [])}
    alts = [len(d["alternatives"]) for d in doc["decisions"]]
    considered = [_item_id(i, j) for i, d in enumerate(doc["decisions"]) for j in range(len(d["alternatives"]))]
    out: Dict[str, Any] = {
        "decisions": len(doc["decisions"]),
        "decision_coverage": len(matched & decisions) / len(decisions) if decisions else None,
        "expert_decisions_matched": len(matched & decisions),
        "alternatives_per_decision": mean(alts) if alts else 0,
        "alternatives_matched": (sum(bool(hits.get(k)) for k in considered) / len(considered)) if considered else None,
        "uncovered_listed": len(doc.get("uncovered") or []),
        **_fit(doc, hits, gt, brief),
    }
    space = condition in SPACE_CONDITIONS and graph is not None
    if space:
        valid = _graph_ids(graph)
        chosen_cites = []
        for d in doc["decisions"]:
            j = _chosen_index(d)
            chosen_cites.append(d["alternatives"][j]["citations"] if j is not None else [])
        cites = [c for d in doc["decisions"] for a in d["alternatives"] for c in a["citations"]]
        out["grounded_choices"] = (sum(bool(c) for c in chosen_cites) / len(chosen_cites)) if chosen_cites else None
        out["valid_citations"] = (sum(c in valid for c in cites) / len(cites)) if cites else None
        out.update(_consistency(doc, graph))
    else:
        out.update(grounded_choices=None, valid_citations=None, consistency_warnings=None, unknown_value_ids=None,
                   value_ids_used=None)
    if summary is not None:
        out["points_explored"] = len(summary.get("points") or []) if condition in SPACE_CONDITIONS else None
        out["network_flag"] = bool(summary.get("network_commands"))
        out["tokens"] = summary.get("tokens")
        out["seconds"] = summary.get("seconds")
        out["cost_usd"] = _cost(summary, rates)
    else:
        out["points_explored"] = None
    return out


NUMERIC = ("decision_coverage", "expert_decisions_matched", "alternatives_per_decision", "alternatives_matched",
           "requirements_fit", "choices_matched", "choices_unmatched", "grounded_choices", "valid_citations",
           "consistency_warnings", "unknown_value_ids", "points_explored", "cost_usd", "seconds")


def aggregate(rows: List[Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Per condition: mean, min and max of each metric over its sessions (not-applicable values left out)."""
    out: Dict[str, Dict[str, Any]] = {}
    for cond in sorted({r["condition"] for r in rows}):
        group = [r for r in rows if r["condition"] == cond]
        stats: Dict[str, Any] = {"sessions": len(group), "network_flagged": sum(bool(r.get("network_flag")) for r in group)}
        for key in NUMERIC:
            vals = [r[key] for r in group if isinstance(r.get(key), (int, float))]
            stats[key] = {"mean": mean(vals), "min": min(vals), "max": max(vals)} if vals else None
        out[cond] = stats
    return out


def main() -> None:
    """Score every session with a design and write ``results/scores.json``."""
    from taxonomy_generator.evaluation import gt_match
    from taxonomy_generator.evaluation.gt_match import MatcherConfig
    from taxonomy_generator.evaluation.judge import openai_judge_model
    from taxonomy_generator.settings import load_settings

    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--workspaces", type=Path, help="folder with M and E, for grounding and consistency")
    parser.add_argument("--export-labels", action="store_true", help="write each session's matches for hand-checking")
    args = parser.parse_args()
    gt = json.loads((INPUTS / "gt_model.json").read_text(encoding="utf-8"))
    briefs = {b["id"]: b for b in design.load_briefs()}
    check_briefs(list(briefs.values()), gt)
    settings = load_settings(str(INPUTS / "config.yaml"))
    config = MatcherConfig.from_settings(settings)
    config = MatcherConfig(**{**config.__dict__, "cache_path": str(RESULTS / "judge_cache.json")})
    rates = yaml.safe_load(RATES.read_text(encoding="utf-8")) if RATES.is_file() else {}
    graphs = {}
    if args.workspaces:
        for cond in SPACE_CONDITIONS:
            graphs[cond] = json.loads((args.workspaces / cond / "raw" / "graph.json").read_text(encoding="utf-8"))
    options = _gt_items(gt)
    names = {o.id: o.name for o in options}
    embed = gt_match.embedder_from_config(config)
    judge = openai_judge_model(gt_match.check_matching_llm(config.matching_llm)) if config.mode == "judge" else None
    cache = gt_match.JudgeCache(config.cache_path)
    rows = []
    for path in sorted((RESULTS / "designs").glob("*.json")):
        sid = path.stem
        summary = json.loads((RESULTS / "summaries" / f"{sid}.json").read_text(encoding="utf-8"))
        check_summary(summary)
        doc = json.loads(path.read_text(encoding="utf-8"))
        sources: Dict[str, int] = {}
        hits = match(doc, gt, config, embed=embed, judge_model=judge, cache=cache, options=options,
                     label_sources=sources)
        cache.save()                        # after each session, so an interrupted run keeps its verdicts
        row = {"session": sid, "brief": summary["brief"], "condition": summary["condition"], "rep": summary["rep"],
               "model": summary["model"], "matching_model": config.matching_llm, "label_sources": sources,
               **metrics(doc, hits, gt, briefs[summary["brief"]], summary["condition"],
                         graph=graphs.get(summary["condition"]), summary=summary, rates=rates)}
        rows.append(row)
        if args.export_labels:
            labels = RESULTS / "labels"
            labels.mkdir(parents=True, exist_ok=True)
            with (labels / f"{sid}.csv").open("w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["decision", "alternative", "matched_expert_options", "correct (y/n)"])
                for item in design_items(doc):
                    w.writerow([item.parent_name, item.name, "; ".join(names[o] for o in sorted(hits[item.id])), ""])
    (RESULTS / "scores.json").write_text(json.dumps({"rates_date": rates.get("date"), "matcher": config.as_record(),
                                                     "llm_warnings": gt_match.llm_warnings(config), "sessions": rows,
                                                     "by_condition": aggregate(rows)}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(aggregate(rows), indent=2))  # noqa: T201


if __name__ == "__main__":
    main()
