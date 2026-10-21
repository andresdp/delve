"""Stage funnel (paper plan A10): where along the pipeline each expert option is lost.

For one saved run and one study's ground truth, the funnel checks every attached
expert option against each pipeline stage the run saved:

- ``open_codes``: the run's accumulated open codes;
- one stage per saved iteration: ``generate``, ``update_<k>``, ``review`` and
  ``consolidated`` (labels inferred from the run, see ``label_iterations``);
- ``selected``: the reported design space (``selected_clusters``).

An option is *present* at a stage when one of its candidates there gets a hit
label (``same``/``broader``/``narrower``) from the matcher's graded judge.
Candidates are the stage items nearest to the option (cosine distance, matcher
serialization) within the matcher's ``upper_threshold``; they are judged nearest
first, in small batches, until a hit (within ``lower_threshold``, when set, a pair is
present without the judge, as in the matcher). At the open-codes stage the number of
candidates grows with the number of codes (``code_fraction``), since one stage
holds far more items there than any taxonomy. An option is ``absent`` at a stage only
when every candidate got a verdict and none was a hit; with no candidate within the
threshold, or a failed judge call, it is ``unjudged`` there, not lost (unjudged is not
wrong). Judge errors are counted per stage, and a failed pair is retried at later stages.

The *loss stage* of an option is the first stage judged absent after its last
presence; when only unjudged stages follow, it has none and counts as unresolved.
Options absent at a stage but present later are counted as dropped then recovered. At the selected stage the funnel's verdicts are compared with the
official match file, which calibrates its candidate gate against the scored result.
"""

from __future__ import annotations

import asyncio
import csv
import json
import logging
import math
import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from taxonomy_generator.evaluation import gt_match
from taxonomy_generator.evaluation.gt_match import (
    HIT_LABELS,
    Item,
    JudgeCache,
    MatcherConfig,
)

logger = logging.getLogger(__name__)

PRESENT, ABSENT, UNJUDGED = "present", "absent", "unjudged"
JUDGE_BATCH = 5


@dataclass
class Stage:
    """One pipeline stage: a name and the items it holds."""

    name: str
    items: list[Item]


@dataclass
class FunnelSettings:
    """Funnel-specific settings on top of the matcher's."""

    k: int = 5                      # candidates per option at taxonomy stages
    code_fraction: float = 0.02     # open codes: k grows to this share of the codes
    handcheck_size: int = 20        # options exported for hand-checking the open-codes gate


@dataclass
class OptionTrace:
    """One option's status per stage, with the verdicts that decided it."""

    option: Item
    status: dict[str, str] = field(default_factory=dict)
    evidence: dict[str, dict[str, Any]] = field(default_factory=dict)


# ------------------------------------------------------------------ stages

CONSOLIDATION_MARKERS = ("Consolidated ", "Value consolidation disabled", "No values to consolidate",
                         "Merged near-duplicate dimensions")


def label_iterations(iterations: Sequence[dict], completed: bool = False) -> list[str]:
    """Stage names of the saved iterations: generate, update_<k>, review, consolidated.

    ``consolidate_values`` always appends one iteration (even when disabled), so in a
    completed run (one with a selected view) the last iteration is the consolidation
    output; otherwise it is recognized by ``stances`` on its values or by the
    consolidator's explanation. The review is the iteration just before it (or the
    last one when there is no consolidation output). A run with one iteration has only
    ``generate``. ``merged_from`` is not a marker: tools-mode updates write it too.
    """
    n = len(iterations)
    names = ["generate"] + [f"update_{k}" for k in range(1, n)]
    if n < 2:
        return names[:n]

    def consolidated(it: dict) -> bool:
        values = [v for c in it.get("clusters") or [] for v in c.get("values") or [] if isinstance(v, dict)]
        explanation = (it.get("explanation") or "").lstrip()
        return any("stances" in v for v in values) or explanation.startswith(CONSOLIDATION_MARKERS)

    review_at = n - 1
    if completed or consolidated(iterations[-1]):
        names[-1] = "consolidated"
        review_at = n - 2
    if review_at >= 1:
        names[review_at] = "review"
    return names


def open_code_items(codes: Sequence[dict]) -> list[Item]:
    """Open codes as funnel items ('<label>: <rationale>'; no parent, so no '›' prefix)."""
    items = []
    for i, code in enumerate(codes):
        if not isinstance(code, dict):
            continue
        items.append(Item(id=f"{code.get('doc_id', '?')}#{i}", name=code.get("label", ""),
                          description=code.get("rationale", ""), parent_ids=[], parent_name="",
                          status=code.get("status", "")))
    return items


def item_text(item: Item) -> str:
    """Text embedded and judged: the matcher serialization, or '<label>: <rationale>' for codes."""
    if not item.parent_name:
        return f"{item.name}: {item.description}" if item.description else item.name
    return item.text


def build_stages(run: dict, codes: Sequence[dict], include_outcomes: bool = False) -> list[Stage]:
    """Return the run's stages in pipeline order (open codes, iterations, selected view)."""
    stages = [Stage("open_codes", open_code_items(codes))]
    iterations = run.get("iterations") or []
    for name, it in zip(label_iterations(iterations, completed=bool(run.get("selected_clusters"))), iterations):
        stages.append(Stage(name, gt_match.system_values(it.get("clusters") or [], include_outcomes)))
    if run.get("selected_clusters"):
        stages.append(Stage("selected", gt_match.system_values(run["selected_clusters"], include_outcomes)))
    return stages


# ------------------------------------------------------------------ gating

def stage_k(stage: Stage, settings: FunnelSettings) -> int:
    """Candidates per option at a stage: ``k``, or a share of the codes at the open-codes stage."""
    if stage.name == "open_codes":
        return max(settings.k, math.ceil(settings.code_fraction * len(stage.items)))
    return settings.k


def candidates(dist_row: np.ndarray, k: int, upper_threshold: float) -> list[int]:
    """Return the indices of the ``k`` nearest items within ``upper_threshold``, nearest first."""
    order = np.argsort(dist_row)[:k]
    return [int(i) for i in order if dist_row[i] <= upper_threshold]


# ------------------------------------------------------------------- judge

def judge_batches(cands: list[int]) -> list[list[int]]:
    """Candidates in judging batches, nearest first: 1, then 2, then ``JUDGE_BATCH`` at a time.

    Judging stops at the first hit, so small first batches avoid paying for calls
    beyond a near hit; later batches are larger to keep latency down.
    """
    batches, start, sizes = [], 0, [1, 2]
    while start < len(cands):
        size = sizes.pop(0) if sizes else JUDGE_BATCH
        batches.append(cands[start:start + size])
        start += size
    return batches


def memo_embedder(embed: Callable[[list[str]], np.ndarray]) -> Callable[[list[str]], np.ndarray]:
    """Wrap ``embed`` so each distinct text is embedded once across all stages."""
    vectors: dict[str, np.ndarray] = {}

    def cached(texts: list[str]) -> np.ndarray:
        new = list(dict.fromkeys(t for t in texts if t not in vectors))
        if new:
            vectors.update(zip(new, embed(new)))
        return np.asarray([vectors[t] for t in texts], dtype=float)
    return cached


async def trace_options(stages: list[Stage], options: list[Item], embed: Callable[[list[str]], np.ndarray],
                        judge_model: Any, config: MatcherConfig, settings: FunnelSettings,
                        cache: JudgeCache | None = None, concurrency: int = 8) -> list[OptionTrace]:
    """Status of every option at every stage (present / absent / unjudged)."""
    embed = memo_embedder(embed)
    option_vecs = embed([o.text for o in options]) if options else np.zeros((0, 1))
    judge_name = gt_match.model_name(judge_model)
    semaphore = asyncio.Semaphore(max(1, concurrency))
    pending: dict[str, asyncio.Future] = {}

    async def verdict_for(first: str, second: str) -> dict[str, str]:
        key = JudgeCache.key(judge_name, first, second)
        future = pending.get(key)
        if future is None:  # one call per distinct ordered pair, shared across stages
            future = pending[key] = asyncio.ensure_future(
                gt_match.judge_verdict(judge_model, cache, semaphore, key, first, second))
        try:
            return await future
        except Exception:
            if pending.get(key) is future:  # forget the failure so a later stage retries the pair
                pending.pop(key, None)
            raise

    async def judge_pair(item: Item, option: Item) -> dict[str, Any]:
        order = gt_match.pair_order(config.seed, item.id, option.id)
        text = item_text(item)
        first, second = gt_match.ordered_texts(order, text, option.text)
        try:
            verdict = await verdict_for(first, second)
        except Exception as exc:  # a failed call leaves the pair unjudged, as in the matcher
            logger.warning("Judge call failed (%s: %s); pair left unjudged", type(exc).__name__, exc)
            return {"item_id": item.id, "item_text": text, "label": None, "error": str(exc)}
        return {"item_id": item.id, "item_text": text, "label": gt_match.orient_label(verdict["label"], order),
                "reason": verdict.get("reason", "")}

    traces = [OptionTrace(o) for o in options]
    for stage in stages:
        if not stage.items or not options:
            for t in traces:
                t.status[stage.name] = UNJUDGED
            continue
        dist = gt_match.pair_distances(option_vecs, embed([item_text(i) for i in stage.items]))
        k = stage_k(stage, settings)

        async def trace_one(j: int, t: OptionTrace, stage: Stage = stage, dist: np.ndarray = dist, k: int = k):
            cands = candidates(dist[j], k, config.upper_threshold)
            if cands and config.lower_threshold > 0 and dist[j, cands[0]] <= config.lower_threshold:
                hit = {"item_id": stage.items[cands[0]].id, "item_text": item_text(stage.items[cands[0]]),
                       "label": "same", "label_source": "auto", "distance": round(float(dist[j, cands[0]]), 4)}
                t.status[stage.name] = PRESENT  # as in the matcher: within lower_threshold is "same" without a judge
                t.evidence[stage.name] = {"hit": hit, "judged": 0, "candidates": len(cands), "errors": 0}
                return
            judged: list[dict[str, Any]] = []
            for batch in judge_batches(cands):
                results = await asyncio.gather(*(judge_pair(stage.items[i], t.option) for i in batch))
                for i, r in zip(batch, results):
                    r["distance"] = round(float(dist[j, i]), 4)
                judged.extend(results)
                hit = next((r for r in results if r["label"] in HIT_LABELS), None)
                if hit:
                    t.status[stage.name] = PRESENT
                    t.evidence[stage.name] = {"hit": hit, "judged": len(judged), "candidates": len(cands),
                                              "errors": sum(r["label"] is None for r in judged)}
                    return
            errors = sum(r["label"] is None for r in judged)
            # Absent only when every candidate got a verdict: a failed call could have been the hit.
            t.status[stage.name] = ABSENT if judged and not errors else UNJUDGED
            t.evidence[stage.name] = {"judged": len(judged), "candidates": len(cands), "errors": errors,
                                      "nearest": judged[0] if judged else None}

        await asyncio.gather(*(trace_one(j, t) for j, t in enumerate(traces)))
        logger.info("Stage %s: %d items, k=%d, %d options present", stage.name, len(stage.items), k,
                    sum(t.status[stage.name] == PRESENT for t in traces))
    return traces


# ---------------------------------------------------------------- analysis

def loss_stage(status: dict[str, str], stage_names: Sequence[str]) -> str | None:
    """First stage judged absent after the option's last presence; ``None`` when there is none.

    Unjudged stages are not evidence of loss: an option present until the end, or whose
    stages after its last presence are all unjudged, has no loss stage (the latter is
    counted as unresolved by ``summarize``). An option never present is lost at its first
    absent stage.
    """
    last_present = max((i for i, s in enumerate(stage_names) if status.get(s) == PRESENT), default=-1)
    return next((s for s in stage_names[last_present + 1:] if status.get(s) == ABSENT), None)


def dropped_then_recovered(status: dict[str, str], stage_names: Sequence[str]) -> bool:
    """Tell whether the option was present, then not present at some stage, then present again."""
    seen, gap = False, False
    for s in stage_names:
        if status.get(s) == PRESENT:
            if seen and gap:
                return True
            seen = True
        elif seen:
            gap = True
    return False


def official_hits(match_file: dict) -> set[str]:
    """Options with a hit label in an official match file (``*_gt_match.json``)."""
    return {p["gt_id"] for p in match_file.get("pairs", []) if p.get("label") in HIT_LABELS}


def summarize(traces: list[OptionTrace], stage_names: Sequence[str], view_names: Sequence[str],
              official: set[str] | None = None) -> dict[str, Any]:
    """Count per view and stage: presence, loss stages, recoveries, agreement with the official match."""
    summary: dict[str, Any] = {}
    for view in view_names:
        ts = [t for t in traces if view in t.option.views]
        per_stage = {s: {**{k: sum(t.status.get(s) == k for t in ts) for k in (PRESENT, ABSENT, UNJUDGED)},
                         "judge_errors": sum((t.evidence.get(s) or {}).get("errors", 0) for t in ts)}
                     for s in stage_names}
        losses: dict[str, int] = {}
        for t in ts:
            ls = loss_stage(t.status, stage_names)
            if ls is not None:
                losses[ls] = losses.get(ls, 0) + 1
        entry: dict[str, Any] = {
            "options": len(ts), "per_stage": per_stage, "loss_stage": losses,
            "never_present": sum(all(t.status.get(s) != PRESENT for s in stage_names) for t in ts),
            "dropped_then_recovered": sum(dropped_then_recovered(t.status, stage_names) for t in ts),
            "unresolved": sum(loss_stage(t.status, stage_names) is None
                              and t.status.get(stage_names[-1]) != PRESENT for t in ts),
        }
        if official is not None and "selected" in stage_names:
            funnel = {t.option.id for t in ts if t.status.get("selected") == PRESENT}
            ids = {t.option.id for t in ts}
            off = official & ids
            entry["selected_agreement"] = {"both": len(funnel & off), "funnel_only": len(funnel - off),
                                           "official_only": len(off - funnel),
                                           "neither": len(ids - funnel - off)}
        summary[view] = entry
    return summary


# ----------------------------------------------------------------- outputs

def write_outputs(out_dir: Path | str, stem: str, traces: list[OptionTrace], stage_names: Sequence[str],
                  summary: dict[str, Any], record: dict[str, Any], decisions: dict[str, dict],
                  handcheck_size: int, seed: int) -> dict[str, Path]:
    """Option x stage CSV, summary JSON, and the open-codes hand-check sheet."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {"csv": out_dir / f"{stem}_stage_funnel.csv", "json": out_dir / f"{stem}_stage_funnel.json",
             "handcheck": out_dir / f"{stem}_stage_funnel_handcheck.csv"}
    with paths["csv"].open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["option_id", "option", "decision", "views", *stage_names, "loss_stage", "dropped_then_recovered"])
        for t in traces:
            dec = decisions.get(t.option.parent_ids[0], {}).get("name", "") if t.option.parent_ids else ""
            w.writerow([t.option.id, t.option.name, dec, "+".join(sorted(t.option.views)),
                        *[t.status.get(s, "") for s in stage_names], loss_stage(t.status, stage_names) or "",
                        dropped_then_recovered(t.status, stage_names)])
    options = [{"id": t.option.id, "views": sorted(t.option.views), "status": t.status,
                "loss_stage": loss_stage(t.status, stage_names), "evidence": t.evidence} for t in traces]
    paths["json"].write_text(json.dumps({"settings": record, "stages": list(stage_names), "summary": summary,
                                         "options": options}, indent=1, ensure_ascii=False), encoding="utf-8")
    sample = random.Random(seed).sample(traces, min(handcheck_size, len(traces)))
    with paths["handcheck"].open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["option_id", "option_text", "open_codes_status", "judged", "candidates", "best_code",
                    "judge_label", "distance", "human_label (present/absent)", "notes"])
        for t in sample:
            ev = t.evidence.get("open_codes", {})
            shown = ev.get("hit") or ev.get("nearest") or {}
            w.writerow([t.option.id, t.option.text, t.status.get("open_codes", ""), ev.get("judged", ""),
                        ev.get("candidates", ""), shown.get("item_text", ""), shown.get("label", ""),
                        shown.get("distance", ""), "", ""])
    return paths


# ----------------------------------------------------------------- command

def sibling_path(taxonomy_path: Path, kind: str) -> Path:
    """Return the run's ``*_<kind>_<timestamp>.json`` next to ``*_taxonomy_<timestamp>.json``."""
    if "_taxonomy_" not in taxonomy_path.name:
        raise gt_match.MatcherError(f"not a saved taxonomy file (*_taxonomy_<timestamp>.json): {taxonomy_path}")
    return taxonomy_path.with_name(taxonomy_path.name.replace("_taxonomy_", f"_{kind}_"))


async def run_funnel(taxonomy_path: str, gt_folder: str, settings: Any, funnel: FunnelSettings | None = None,
                     matching_llm_override: str | None = None, match_file: str | None = None,
                     out_dir: str | None = None, embed: Callable[[list[str]], np.ndarray] | None = None,
                     judge_model: Any = None) -> dict[str, Any]:
    """Trace one saved run's options through its stages and write the funnel outputs."""
    import dataclasses

    funnel = funnel or FunnelSettings()
    config = MatcherConfig.from_settings(settings)
    if matching_llm_override:
        config = dataclasses.replace(config, matching_llm=matching_llm_override)
    bare_judge = gt_match.check_matching_llm(config.matching_llm)
    warnings = gt_match.llm_warnings(config)
    for w in warnings:
        logger.warning(w)

    path = Path(taxonomy_path)
    run = json.loads(path.read_text(encoding="utf-8"))
    codes_path = sibling_path(path, "open_codes")
    if not codes_path.exists():
        raise gt_match.MatcherError(f"the run has no saved open codes ({codes_path.name}); the funnel needs them")
    codes = json.loads(codes_path.read_text(encoding="utf-8")).get("open_codes", [])

    views = gt_match.load_gt_folder(gt_folder)
    options = gt_match.ground_truth_options(views)
    stages = build_stages(run, codes, config.include_outcomes)
    stage_names = [s.name for s in stages]

    embed = embed or gt_match.embedder_from_config(config)
    if judge_model is None:
        from taxonomy_generator.evaluation.judge import openai_judge_model
        judge_model = openai_judge_model(bare_judge)
    cache = JudgeCache(config.cache_path)
    try:
        traces = await trace_options(stages, options, embed, judge_model, config, funnel, cache=cache)
    finally:
        cache.save()

    stem = path.stem.replace("_taxonomy_", "_")
    official = None
    official_path = Path(match_file) if match_file else path.with_name(f"{stem}_gt_match.json")
    if official_path.exists():
        official = official_hits(json.loads(official_path.read_text(encoding="utf-8")))
    else:
        logger.warning("No official match file at %s; selected-stage agreement not reported", official_path)

    summary = summarize(traces, stage_names, list(views), official)
    record = {**config.as_record(), **dataclasses.asdict(funnel), "llm_warnings": warnings,
              "taxonomy": str(taxonomy_path), "open_codes": str(codes_path), "ground_truth": str(gt_folder),
              "official_match_file": str(official_path) if official is not None else None,
              "stage_sizes": {s.name: len(s.items) for s in stages},
              "stage_k": {s.name: stage_k(s, funnel) for s in stages}}
    decisions = gt_match.ground_truth_decisions(views)
    paths = write_outputs(out_dir or path.parent, stem, traces, stage_names, summary, record, decisions,
                          funnel.handcheck_size, config.seed)
    return {"paths": paths, "summary": summary, "stages": stage_names, "settings": record}
