#!/usr/bin/env python3
"""Score the study designs against the C1 expert model.

Every alternative a design considers is matched to the expert model's attached options with the
ground-truth matcher (``taxonomy_generator.evaluation.gt_match``: embeddings propose pairs, the pinned judge
decides, verdicts cached). From those matches and the session summary, per session:

- decision coverage: expert decisions with at least one matched alternative, over all expert decisions. Each
  alternative counts through its best match only (``hit_levels``), so one broad alternative cannot claim many
  decisions; ``_same`` (only matches labelled "same") and ``_lenient`` (every same, broader or narrower match)
  variants are reported next to it;
- relevant-decision coverage: the same over the brief's relevant decisions (``relevant_decisions``: those whose
  options differ in summed impact on the brief's forces; see ``reference.py``);
- alternatives per decision, and the share of alternatives that match an expert option;
- driver recall: the share of the brief's (hidden) forces that the ADRs' stated decision drivers name;
- requirements fit (on the best-match hits): per touched expert decision, (chosen - worst) / (best - worst) of the summed expert impacts on
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
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Set

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
          label_sources: Optional[Dict[str, int]] = None, run: Callable = asyncio.run,
          pairs_out: Optional[list] = None) -> Dict[str, Set[str]]:
    """Return the expert options each design item matches (same, broader or narrower): the lenient hits.

    ``pairs_out`` collects the hit pairs (with their label and distance), for ``hit_levels``.

    Pass ``embed``, ``judge_model``, ``cache`` and ``options`` to reuse them across sessions; a cache created
    here is saved here, a passed one is saved by the caller. ``run`` runs the matching coroutine; pass one event
    loop's ``run_until_complete`` across sessions, so the judge's clients close on the loop that opened them.
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
    pairs = run(gt_match.label_pairs(items, options, embed, judge_model, config, cache=cache))
    if own_cache:
        cache.save()
    hits: Dict[str, Set[str]] = {i.id: set() for i in items}
    if label_sources is not None:        # auto, auto_rank, judge, judge_error: judge failures must stay visible
        for p in pairs:
            label_sources[p["label_source"]] = label_sources.get(p["label_source"], 0) + 1
    for p in pairs:
        if p["label"] in gt_match.HIT_LABELS:
            hits[p["system_id"]].add(p["gt_id"])
            if pairs_out is not None:
                pairs_out.append(p)
    return hits


def best_pair(pairs: Iterable[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
    """The best of one item's hit pairs: a "same" match first, then the smallest embedding distance."""
    return min(pairs, key=lambda p: (p["label"] != "same", p["distance"], p["gt_id"]), default=None)


def hit_levels(item_ids: Iterable[str], pairs: Iterable[Mapping[str, Any]]) -> Dict[str, Dict[str, Set[str]]]:
    """Three readings of the hit pairs, per design item.

    - ``best`` (the primary one): only the item's best match (``best_pair``), so one broad alternative cannot
      claim many expert options and decisions;
    - ``same``: only the matches the judge labelled "same" (not much stricter in practice: the judge calls
      loosely related options "same");
    - ``lenient``: every same, broader or narrower match.
    """
    by_item: Dict[str, List[Mapping[str, Any]]] = {i: [] for i in item_ids}
    for p in pairs:
        by_item.setdefault(p["system_id"], []).append(p)
    best = {i: ({best_pair(ps)["gt_id"]} if ps else set()) for i, ps in by_item.items()}
    same = {i: {p["gt_id"] for p in ps if p["label"] == "same"} for i, ps in by_item.items()}
    lenient = {i: {p["gt_id"] for p in ps} for i, ps in by_item.items()}
    return {"best": best, "same": same, "lenient": lenient}


def match_drivers(doc: Mapping[str, Any], gt: Mapping[str, Any], brief: Mapping[str, Any], config, *,
                  embed: Optional[Callable] = None, judge_model: Any = None, cache: Any = None,
                  run: Callable = asyncio.run) -> Set[str]:
    """Return the brief's forces that some stated decision driver names (same, broader or narrower match)."""
    from taxonomy_generator.evaluation import gt_match
    from taxonomy_generator.evaluation.gt_match import Item
    from taxonomy_generator.evaluation.judge import openai_judge_model
    names = {f["id"]: f.get("name") or f["id"] for f in gt.get("forces") or []}
    forces = [Item(id=f, name=names.get(f, f), description="", parent_ids=["forces"], parent_name="Requirement")
              for f in brief["forces"]]
    drivers = [Item(id=f"d{i}r{j}", name=text, description="", parent_ids=["drivers"], parent_name="Requirement")
               for i, dec in enumerate(doc["decisions"]) for j, text in enumerate(dec.get("drivers") or [])]
    if not drivers:
        return set()
    embed = embed or gt_match.embedder_from_config(config)
    if judge_model is None and config.mode == "judge":
        judge_model = openai_judge_model(gt_match.check_matching_llm(config.matching_llm))
    own_cache = cache is None
    cache = gt_match.JudgeCache(config.cache_path) if own_cache else cache
    pairs = run(gt_match.label_pairs(drivers, forces, embed, judge_model, config, cache=cache))
    if own_cache:
        cache.save()
    return {p["gt_id"] for p in pairs if p["label"] in gt_match.HIT_LABELS}


def _option_sums(gt: Mapping[str, Any], forces: List[str]) -> Dict[str, int]:
    sums = {o["id"]: 0 for o in gt.get("options") or []}
    for i in gt.get("impacts") or []:
        if i["force_id"] in forces and i["option_id"] in sums:
            sums[i["option_id"]] += IMPACT.get(str(i["impact"]).strip(), 0)
    return sums


def _options_of(gt: Mapping[str, Any]) -> Dict[str, List[str]]:
    """The attached options of each expert decision."""
    options_of: Dict[str, List[str]] = {}
    for o in gt.get("options") or []:
        if not o.get("unattached"):
            for d in o.get("decision_ids") or []:
                options_of.setdefault(d, []).append(o["id"])
    return options_of


def relevant_decisions(gt: Mapping[str, Any], forces: List[str]) -> Dict[str, Dict[str, Any]]:
    """The brief's reference (layer 1): expert decisions whose options differ in summed impact on ``forces``.

    Per relevant decision: the summed impact of each option, and the preferred options (the best sum).
    """
    sums = _option_sums(gt, forces)
    out = {}
    for d, options in _options_of(gt).items():
        scores = {o: sums[o] for o in options}
        best = max(scores.values())
        if best != min(scores.values()):
            out[d] = {"sums": scores, "preferred": sorted(o for o, v in scores.items() if v == best)}
    return out


def _fit(doc, hits, gt, brief) -> Dict[str, Any]:
    decision_of = {o["id"]: o.get("decision_ids") or [] for o in gt.get("options") or [] if not o.get("unattached")}
    options_of = _options_of(gt)
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
            rates: Optional[Mapping[str, Any]] = None, driver_hits: Optional[Set[str]] = None,
            same_hits: Optional[Mapping[str, Set[str]]] = None,
            lenient_hits: Optional[Mapping[str, Set[str]]] = None) -> Dict[str, Any]:
    """Return the study metrics of one session (see the module docstring).

    ``hits`` are the primary (best-match) hits; ``same_hits`` and ``lenient_hits``, when given, add the
    coverage of the strictest and the most lenient reading (``hit_levels``).
    """
    decisions = {d["id"] for d in gt.get("decisions") or []}
    decision_of = {o["id"]: o.get("decision_ids") or [] for o in gt.get("options") or []}
    relevant = set(relevant_decisions(gt, brief["forces"]))

    def coverage(level: Mapping[str, Set[str]], suffix: str = "") -> Dict[str, Any]:
        matched = {d for opts in level.values() for o in opts for d in decision_of.get(o, [])}
        return {f"decision_coverage{suffix}": len(matched & decisions) / len(decisions) if decisions else None,
                f"expert_decisions_matched{suffix}": len(matched & decisions),
                f"relevant_decision_coverage{suffix}": len(matched & relevant) / len(relevant) if relevant else None,
                f"relevant_decisions_matched{suffix}": len(matched & relevant)}
    alts = [len(d["alternatives"]) for d in doc["decisions"]]
    considered = [_item_id(i, j) for i, d in enumerate(doc["decisions"]) for j in range(len(d["alternatives"]))]
    out: Dict[str, Any] = {
        "decisions": len(doc["decisions"]),
        **coverage(hits),
        **(coverage(same_hits, "_same") if same_hits is not None else {}),
        **(coverage(lenient_hits, "_lenient") if lenient_hits is not None else {}),
        "alternatives_per_decision": mean(alts) if alts else 0,
        "alternatives_matched": (sum(bool(hits.get(k)) for k in considered) / len(considered)) if considered else None,
        "uncovered_listed": len(doc.get("uncovered") or []),
        "drivers_listed": sum(len(d.get("drivers") or []) for d in doc["decisions"]),
        "driver_recall": (len(set(driver_hits) & set(brief["forces"])) / len(brief["forces"])
                          if driver_hits is not None and brief.get("forces") else None),
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


NUMERIC = ("decision_coverage", "expert_decisions_matched", "relevant_decision_coverage",
           "decision_coverage_same", "relevant_decision_coverage_same",
           "decision_coverage_lenient", "relevant_decision_coverage_lenient", "alternatives_per_decision", "alternatives_matched",
           "requirements_fit", "driver_recall", "choices_matched", "choices_unmatched", "grounded_choices", "valid_citations",
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
    embed = gt_match.embedder_from_config(config)
    judge = openai_judge_model(gt_match.check_matching_llm(config.matching_llm)) if config.mode == "judge" else None
    cache = gt_match.JudgeCache(config.cache_path)
    loop = asyncio.new_event_loop()          # one loop for every session (see ``match``)
    try:
        rows = _score_sessions(args, gt, briefs, config, rates, graphs, options, embed, judge, cache,
                               loop.run_until_complete)
    finally:
        loop.close()
    rates_date = str(rates["date"]) if rates.get("date") else None      # YAML may read the date as a date
    (RESULTS / "scores.json").write_text(json.dumps({"rates_date": rates_date, "matcher": config.as_record(),
                                                     "llm_warnings": gt_match.llm_warnings(config), "sessions": rows,
                                                     "by_condition": aggregate(rows)}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(aggregate(rows), indent=2))  # noqa: T201


def _score_sessions(args, gt, briefs, config, rates, graphs, options, embed, judge, cache, run) -> List[Dict[str, Any]]:
    """Score every session with a design; export its matches when asked."""
    names = {o.id: o.name for o in options}
    rows = []
    for path in sorted((RESULTS / "designs").glob("*.json")):
        sid = path.stem
        summary = json.loads((RESULTS / "summaries" / f"{sid}.json").read_text(encoding="utf-8"))
        check_summary(summary)
        doc = json.loads(path.read_text(encoding="utf-8"))
        sources: Dict[str, int] = {}
        pairs: List[Mapping[str, Any]] = []
        lenient = match(doc, gt, config, embed=embed, judge_model=judge, cache=cache, options=options,
                        label_sources=sources, run=run, pairs_out=pairs)
        levels = hit_levels(lenient, pairs)
        hits = levels["best"]
        drivers = match_drivers(doc, gt, briefs[summary["brief"]], config, embed=embed, judge_model=judge,
                                cache=cache, run=run)
        cache.save()                        # after each session, so an interrupted run keeps its verdicts
        row = {"session": sid, "brief": summary["brief"], "condition": summary["condition"], "rep": summary["rep"],
               "model": summary["model"], "matching_model": config.matching_llm, "label_sources": sources,
               **metrics(doc, hits, gt, briefs[summary["brief"]], summary["condition"],
                         graph=graphs.get(summary["condition"]), summary=summary, rates=rates,
                         driver_hits=drivers, same_hits=levels["same"], lenient_hits=lenient)}
        rows.append(row)
        if args.export_labels:
            labels = RESULTS / "labels"
            labels.mkdir(parents=True, exist_ok=True)
            with (labels / f"{sid}.csv").open("w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["decision", "alternative", "best_match", "other_matches", "best match correct (y/n)"])
                for item in design_items(doc):
                    mine = [p for p in pairs if p["system_id"] == item.id]
                    best = best_pair(mine)
                    others = sorted((p for p in mine if p is not best),
                                    key=lambda p: (p["label"] != "same", p["distance"]))
                    w.writerow([item.parent_name, item.name,
                                f"{names[best['gt_id']]} [{best['label']}]" if best else "",
                                "; ".join(f"{names[p['gt_id']]} [{p['label']}]" for p in others), ""])
    return rows


if __name__ == "__main__":
    main()
