"""Match a design space against an expert ground truth (C1, C2).

Validates both levels of a DelveDSpace design space (or a baseline's, through
another adapter) against the experts' design space (``benchmark/<study>/gt/``):

1. **Values vs. options** (primary). Every candidate value (outcomes excluded
   by default) is paired with every ground-truth option of the union of the
   study's views. Each item is serialized as
   ``"<dimension or decision> › <value or option>: <description>"`` (CamelCase
   names split), embedded and L2-normalized; the cosine distance
   (1 - cosine similarity, lower is closer) labels clear pairs ``same``
   or ``different`` and sends borderline pairs to a graded LLM judge
   (``same``, ``broader``, ``narrower``, ``related``, ``different``).
2. **Dimensions vs. decisions** and **placement**, derived from the value
   matches (see ``align_dimensions`` and ``compute_metrics``).

The judge is a custom deepeval metric (``GradedMatchMetric``) with fixed
instructions, served by the matching LLM (``models.matching_llm``, OpenAI). It
should differ from the generation and evaluation LLMs; when it does not, the
run says so and records the warning. It sees the two
items as "Item 1" and "Item 2" in a seeded order, never which side is the
ground truth, and compares the design options themselves regardless of the
decision or dimension they sit under (placement is scored separately).
Judge results are cached on disk, so reruns are deterministic and cheap.
"""

from __future__ import annotations

import asyncio
import csv
import dataclasses
import functools
import hashlib
import json
import logging
import random
import re
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import numpy as np
from pydantic import BaseModel

from taxonomy_generator.evaluation.judge import (  # judge also sets the deepeval telemetry opt-out
    openai_judge_model,
    resolve_judge_model,
)
from taxonomy_generator.utils import l2_normalize

logger = logging.getLogger(__name__)

LABELS = ("same", "broader", "narrower", "related", "different")
HIT_LABELS = frozenset({"same", "broader", "narrower"})
CANDIDATE_STATUSES = frozenset({"accepted", "rejected", "mixed"})

JUDGE_STEPS = (
    "Item 1 and Item 2 each describe one design option: an alternative a practitioner can choose when "
    "making an architectural design decision. Each is written as '<decision or topic> › <option>: <description>'.",
    "Compare the two design options themselves, regardless of the decision or topic they are listed under: "
    "the same option may sit under differently named or differently scoped decisions. Use the decision or "
    "topic only to understand what the option means.",
    "Answer 'same' when both name the same design option (synonyms, abbreviations or different wording of "
    "one practice).",
    "Answer 'broader' when Item 1 is a more general option that includes Item 2 as one of its forms, and "
    "'narrower' when Item 1 is a specific form of the more general Item 2.",
    "Answer 'related' when the options are different but closely connected (they are often used together, "
    "one supports the other, or they address the same concern in different ways).",
    "Answer 'different' otherwise.",
    "Give a one-sentence reason.",
)
JUDGE_VERSION = hashlib.sha256("\n".join(JUDGE_STEPS).encode()).hexdigest()[:12]


MODES = ("judge", "embeddings")


class MatcherError(ValueError):
    """The matcher cannot run with the given configuration or inputs."""


# ------------------------------------------------------------------ config

@dataclass(frozen=True)
class MatcherConfig:
    """Resolved matcher settings for one scoring run."""

    matching_llm: str | None
    generation_llm: str | None
    embedding: str
    lower_threshold: float
    upper_threshold: float
    max_candidates: int
    include_outcomes: bool
    min_alignment_share: float
    seed: int
    cache_path: str | None
    evaluation_llm: str | None = None
    mode: str = "judge"
    same_threshold: float = 0.18
    embedding_one_to_one: bool = True

    @classmethod
    def from_settings(cls, settings: Any) -> MatcherConfig:
        """Build from ``Settings``: the ``matcher`` section plus ``models`` (LLM roles, embedding).

        ``generation_llm`` is the generator of the scored run (from the run's config), kept to
        check and record the matching LLM's independence.
        """
        m = settings.matcher
        return cls(
            matching_llm=settings.models.matching_llm,
            generation_llm=settings.models.generation_llm,
            evaluation_llm=settings.models.evaluation_llm,
            embedding=m.embedding or settings.models.embedding,
            lower_threshold=float(m.lower_threshold),
            upper_threshold=float(m.upper_threshold),
            max_candidates=int(m.max_candidates),
            include_outcomes=bool(m.include_outcomes),
            min_alignment_share=float(m.min_alignment_share),
            seed=int(m.seed),
            cache_path=m.cache_path,
            mode=check_mode(m.mode),
            same_threshold=float(m.same_threshold),
            embedding_one_to_one=bool(m.embedding_one_to_one),
        )

    def as_record(self) -> dict[str, Any]:
        """Return the settings as recorded in every output, with the judge instructions version."""
        return {**dataclasses.asdict(self), "judge_version": JUDGE_VERSION}


def check_mode(mode: str) -> str:
    """Validate ``matcher.mode``: ``judge`` (embeddings + judge) or ``embeddings`` (distance only)."""
    if mode not in MODES:
        raise MatcherError(f"matcher.mode must be one of {MODES}, got {mode!r}")
    return mode


def check_matching_llm(matching_llm: str | None) -> str:
    """Require a configured OpenAI matching LLM; return the bare model name deepeval uses."""
    if not matching_llm:
        raise MatcherError("models.matching_llm is not set: set it in the YAML config or pass --matching-llm.")
    try:
        resolved = resolve_judge_model(matching_llm)
    except ValueError as exc:
        raise MatcherError(f"models.matching_llm must be an OpenAI model: {exc}") from exc
    return resolved or matching_llm


def llm_warnings(config: MatcherConfig) -> list[str]:
    """Shared-model warnings of the matching LLM against the generation and evaluation LLMs."""
    from taxonomy_generator.settings import ModelSettings, shared_llm_warnings

    models = ModelSettings(generation_llm=config.generation_llm or "", evaluation_llm=config.evaluation_llm or "",
                           matching_llm=config.matching_llm or "")
    return shared_llm_warnings(models, involving="matching_llm")


# ------------------------------------------------------------------- items

def split_camel(name: str) -> str:
    """'CUSUMSequentialTest' -> 'CUSUM Sequential Test'; names with spaces are kept."""
    name = (name or "").strip()
    if " " in name:
        return name
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", " ", name)


def serialize(parent: str, name: str, description: str) -> str:
    """'<parent> › <name>: <description>', CamelCase split, used on both sides."""
    text = f"{split_camel(parent)} › {split_camel(name)}"
    return f"{text}: {description.strip()}" if description and description.strip() else text


@dataclass
class Item:
    """One system value or ground-truth option, with its parent(s)."""

    id: str
    name: str
    description: str
    parent_ids: list[str]
    parent_name: str
    status: str = ""
    views: set[str] = field(default_factory=set)

    @property
    def text(self) -> str:
        """The serialization that is embedded and shown to the judge."""
        return serialize(self.parent_name, self.name, self.description)


def system_dimensions(clusters: Sequence[dict]) -> list[dict[str, str]]:
    """Adapter for DelveDSpace taxonomies: the dimensions (id, name, description)."""
    return [{"id": str(c.get("id")), "name": c.get("name", ""), "description": c.get("description", "")}
            for c in clusters if isinstance(c, dict)]


def system_values(clusters: Sequence[dict], include_outcomes: bool = False) -> list[Item]:
    """Adapter for DelveDSpace taxonomies: candidate values (and outcomes on request)."""
    items = []
    for cluster in clusters:
        if not isinstance(cluster, dict):
            continue
        for value in cluster.get("values") or []:
            if not isinstance(value, dict):
                continue
            status = value.get("status", "")
            if status == "outcome" and not include_outcomes:
                continue
            if status not in CANDIDATE_STATUSES and status != "outcome":
                logger.warning("Value %s has unknown status %r; kept as a candidate", value.get("id"), status)
            items.append(Item(id=str(value.get("id")), name=value.get("label", ""),
                              description=value.get("description", ""), parent_ids=[str(cluster.get("id"))],
                              parent_name=cluster.get("name", ""), status=status))
    return items


# Text of an element shared by several views (same crosswalk id): taken from the first view in
# this order, and used for every view, so view metrics differ only in which elements count
# (scope), never in wording. The paper view comes first: for C2 its option descriptions are the
# catalogue's (the richest author text); for C1 they equal the model's. Recorded in every output.
VIEW_TEXT_PRECEDENCE = ("paper", "model")


def _views_in_text_precedence(views: dict[str, dict]) -> list[tuple[str, dict]]:
    """The views ordered by ``VIEW_TEXT_PRECEDENCE`` (other views after, in their given order)."""
    rank = {name: i for i, name in enumerate(VIEW_TEXT_PRECEDENCE)}
    return sorted(views.items(), key=lambda kv: rank.get(kv[0], len(rank)))


def ground_truth_decisions(views: dict[str, dict]) -> dict[str, dict[str, Any]]:
    """Union of the views' decisions, with the views each belongs to (text per ``VIEW_TEXT_PRECEDENCE``)."""
    decisions: dict[str, dict[str, Any]] = {}
    for view_name, view in _views_in_text_precedence(views):
        for dec in view["decisions"]:
            entry = decisions.setdefault(dec["id"], {**dec, "views": set()})
            entry["views"].add(view_name)
    return decisions


def ground_truth_options(views: dict[str, dict]) -> list[Item]:
    """Union of the views' attached options (unattached ones are not scored), with view membership.

    A shared option's name and description come from the first view in ``VIEW_TEXT_PRECEDENCE``.
    """
    decisions = ground_truth_decisions(views)
    options: dict[str, Item] = {}
    for view_name, view in _views_in_text_precedence(views):
        for opt in view["options"]:
            if not opt.get("decision_ids"):
                continue
            item = options.get(opt["id"])
            if item is None:
                first = decisions[opt["decision_ids"][0]]
                item = options[opt["id"]] = Item(
                    id=opt["id"], name=opt["name"], description=opt.get("description", ""),
                    parent_ids=[], parent_name=first["name"])
            for dec_id in opt["decision_ids"]:
                if dec_id not in item.parent_ids:
                    item.parent_ids.append(dec_id)
            item.views.add(view_name)
    return list(options.values())


# ------------------------------------------------------------------- judge

class JudgeVerdict(BaseModel):
    """Structured judge answer: one graded label and a one-sentence reason."""

    label: str
    reason: str


def build_judge_prompt(first: str, second: str) -> str:
    """Build the fixed judge prompt for Item 1 vs. Item 2 (no side is named system or ground truth)."""
    steps = "\n".join(f"{i}. {step}" for i, step in enumerate(JUDGE_STEPS, 1))
    return (
        "You compare two design options from architectural design spaces.\n\n"
        f"Instructions:\n{steps}\n\n"
        f"Item 1: {first}\nItem 2: {second}\n\n"
        f"Return JSON with 'label' (one of: {', '.join(LABELS)}) and 'reason'."
    )


def orient_label(label: str, order: str) -> str:
    """Express a judge label from the system value's side (the judge saw Item 1 vs. Item 2)."""
    if order == "gt_first":
        return {"broader": "narrower", "narrower": "broader"}.get(label, label)
    return label


def _model_name(model: Any) -> str:
    """Model name of a deepeval model (or of a stand-in without ``get_model_name``)."""
    return getattr(model, "get_model_name", lambda: str(model))()


@functools.cache
def _metric_class() -> type:
    """The ``GradedMatchMetric`` class, built on first use (deepeval is a heavy import)."""
    from deepeval.metrics import BaseMetric

    class GradedMatchMetric(BaseMetric):
        """deepeval metric: one graded label for a pair of design options (Item 1 vs. Item 2).

        ``input`` holds Item 1, ``actual_output`` Item 2. The score is 1 for a
        hit (same, broader, narrower) and 0 otherwise; ``label`` and ``reason``
        keep the verdict. An answer outside the five labels is retried once,
        then recorded as ``different`` with a warning.
        """

        def __init__(self, model: Any, threshold: float = 0.5):
            self.model = model
            self.threshold = threshold
            self.evaluation_model = _model_name(model)
            self.include_reason = True
            self.async_mode = True
            self.strict_mode = False
            self.label: str | None = None
            self.warning = ""

        async def a_measure(self, test_case, *args, **kwargs) -> float:
            prompt = build_judge_prompt(test_case.input, test_case.actual_output)
            self.warning = ""
            answers = []
            model: Any = self.model
            verdict: Any = None
            for _ in range(2):
                verdict, _cost = await model.a_generate(prompt, schema=JudgeVerdict)
                label = (verdict.label or "").strip().lower()
                answers.append(label)
                if label in LABELS:
                    self.label, self.reason = label, verdict.reason
                    break
            else:
                self.label = "different"
                self.reason = verdict.reason
                self.warning = f"invalid judge labels {answers}; recorded as different"
                logger.warning("Judge returned invalid labels %s; recorded as 'different'", answers)
            self.score = 1.0 if self.label in HIT_LABELS else 0.0
            self.success = self.score >= float(self.threshold or 0.5)
            return self.score

        def measure(self, test_case, *args, **kwargs) -> float:
            return asyncio.run(self.a_measure(test_case))

        def is_successful(self) -> bool:
            return bool(self.success)

        @property
        def __name__(self):
            return "Graded option match"

    return GradedMatchMetric


def graded_match_metric(model: Any):
    """Create a fresh ``GradedMatchMetric`` served by ``model``."""
    return _metric_class()(model)


class JudgeCache:
    """Judge verdicts on disk, keyed by judge model, instructions and the ordered pair."""

    def __init__(self, path: str | None):
        """Load the cache from ``path`` when it exists; ``None`` keeps it in memory only."""
        self.path = Path(path) if path else None
        self.data: dict[str, dict[str, str]] = {}
        if self.path and self.path.exists():
            self.data = json.loads(self.path.read_text(encoding="utf-8"))

    @staticmethod
    def key(judge: str, first: str, second: str) -> str:
        """Cache key of an ordered pair for a judge model and the current instructions."""
        return hashlib.sha256(json.dumps([judge, JUDGE_VERSION, first, second]).encode()).hexdigest()

    def get(self, key: str) -> dict[str, str] | None:
        """Return the cached verdict, or ``None``."""
        return self.data.get(key)

    def put(self, key: str, verdict: dict[str, str]) -> None:
        """Store a verdict (saved on ``save``)."""
        self.data[key] = verdict

    def save(self) -> None:
        """Write the cache to disk."""
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self.data, indent=1, sort_keys=True), encoding="utf-8")


# ------------------------------------------------------------------- pairs

def pair_distances(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Cosine distances (1 - cosine similarity, in [0, 2]) between the rows of ``a`` and ``b``."""
    a, b = l2_normalize(a), l2_normalize(b)
    return np.clip(1.0 - a @ b.T, 0.0, 2.0)


def embedder_from_config(config: MatcherConfig) -> Callable[[list[str]], np.ndarray]:
    """Embedding function of the configured embedding model."""
    from taxonomy_generator.utils import load_embeddings_model
    model = load_embeddings_model(config.embedding)
    return lambda texts: np.asarray(model.embed_documents(texts), dtype=float)


def _pair_record(value: Item, option: Item, d: float, label: str, source: str, warning: str = "") -> dict[str, Any]:
    """One labeled pair, as written to the match file."""
    return {"system_id": value.id, "system_text": value.text, "gt_id": option.id, "gt_text": option.text,
            "distance": round(d, 4), "label": label, "label_source": source, "reason": "", "order": "",
            "warning": warning}


async def label_pairs(system: list[Item], options: list[Item], embed: Callable[[list[str]], np.ndarray],
                      judge_model: Any, config: MatcherConfig,
                      cache: JudgeCache | None = None, concurrency: int = 8) -> list[dict[str, Any]]:
    """Label every (system value, ground-truth option) pair exactly once.

    ``label_source`` is ``auto`` (distance at or below the lower threshold, which
    0 disables, or above the upper one), ``judge_error`` (the judge call failed; labeled
    ``different``, not cached), ``judge`` (borderline pair whose items are among each
    other's ``max_candidates`` nearest neighbours) or ``auto_rank`` (borderline
    pair outside those neighbourhoods, labeled ``different`` without the judge).
    """
    if not system or not options:
        return []
    vectors = embed([s.text for s in system] + [o.text for o in options])
    dist = pair_distances(vectors[: len(system)], vectors[len(system):])
    if config.mode == "embeddings":
        return label_pairs_by_distance(system, options, dist, config)

    from deepeval.test_case import LLMTestCase

    k = max(1, config.max_candidates)
    near_sys = np.argsort(dist, axis=1)[:, :k]      # nearest options per value
    near_opt = np.argsort(dist, axis=0)[:k, :]      # nearest values per option
    judge_name = _model_name(judge_model)

    pairs: list[dict[str, Any]] = []
    jobs: dict[str, list[tuple]] = {}   # cache key -> [(record, order, first, second)]
    for i, value in enumerate(system):
        for j, option in enumerate(options):
            d = float(dist[i, j])
            record = _pair_record(value, option, d, "different", "auto")
            pairs.append(record)
            if config.lower_threshold > 0 and d <= config.lower_threshold:  # 0 disables auto-"same"
                record["label"] = "same"
            elif d > config.upper_threshold:
                continue  # far apart: "different" without the judge
            elif j not in near_sys[i] and i not in near_opt[:, j]:
                record["label_source"] = "auto_rank"
            else:
                rng = random.Random(f"{config.seed}:{value.id}:{option.id}")
                order = "system_first" if rng.random() < 0.5 else "gt_first"
                first, second = (value.text, option.text) if order == "system_first" else (option.text, value.text)
                jobs.setdefault(JudgeCache.key(judge_name, first, second), []).append((record, order, first, second))

    semaphore = asyncio.Semaphore(max(1, concurrency))

    async def judge(key: str, first: str, second: str) -> dict[str, str]:
        verdict = cache.get(key) if cache else None
        if verdict is None:
            async with semaphore:
                metric = graded_match_metric(judge_model)  # one per call: the metric keeps the verdict
                await metric.a_measure(LLMTestCase(input=first, actual_output=second))
            verdict = {"label": metric.label, "reason": metric.reason or "", "warning": metric.warning}
            if cache:
                cache.put(key, verdict)
        return verdict

    keys = list(jobs)
    # A failed call does not abort the run: its pairs stay "different" with label source
    # "judge_error" (not cached, so a rerun retries them); every successful verdict is kept.
    verdicts = await asyncio.gather(*(judge(k, jobs[k][0][2], jobs[k][0][3]) for k in keys),
                                    return_exceptions=True)
    failures = [v for v in verdicts if isinstance(v, BaseException)]
    if keys and len(failures) == len(keys):
        raise MatcherError(f"every judge call failed ({len(keys)} calls); first error: "
                           f"{type(failures[0]).__name__}: {failures[0]}")
    if failures:
        logger.warning("%d of %d judge calls failed; their pairs are labeled 'different' with label source "
                       "'judge_error' and are retried on the next run", len(failures), len(keys))
    for key, verdict in zip(keys, verdicts):
        for record, order, _first, _second in jobs[key]:
            if isinstance(verdict, BaseException):
                record.update(label_source="judge_error", order=order,
                              warning=f"judge call failed: {type(verdict).__name__}: {verdict}")
                continue
            record.update(label=orient_label(verdict["label"], order), raw_label=verdict["label"],
                          label_source="judge", reason=verdict.get("reason", ""), order=order,
                          warning=verdict.get("warning", ""))
    return pairs


def label_pairs_by_distance(system: list[Item], options: list[Item], dist: np.ndarray,
                            config: MatcherConfig) -> list[dict[str, Any]]:
    """Embeddings-only labels (``matcher.mode: embeddings``), no LLM calls.

    At or below ``same_threshold`` a pair is ``same``; up to ``upper_threshold`` it is
    ``related``; beyond, ``different``. With ``embedding_one_to_one``, only a one-to-one
    assignment of the ``same`` pairs (most pairs, then smallest distances) stays ``same``;
    the other ``same`` pairs become ``related``, so a generic value cannot match many options.
    """
    from scipy.optimize import linear_sum_assignment

    same = dist <= config.same_threshold
    keep = same.copy()
    if config.embedding_one_to_one and same.any():
        cost = np.where(same, dist - 10.0, 0.0)  # every same pair beats any non-pair; then by distance
        rows, cols = linear_sum_assignment(cost)
        keep = np.zeros_like(same)
        for r, c in zip(rows, cols):
            keep[r, c] = same[r, c]
    pairs = []
    for i, value in enumerate(system):
        for j, option in enumerate(options):
            d = float(dist[i, j])
            label = "same" if keep[i, j] else "related" if d <= config.upper_threshold else "different"
            warning = "same by distance, not kept by the one-to-one assignment" if same[i, j] and not keep[i, j] else ""
            pairs.append(_pair_record(value, option, d, label, "embedding", warning))
    return pairs


def label_counts(pairs: Iterable[dict[str, Any]]) -> dict[str, int]:
    """Count the pairs per label source (auto, auto_rank, judge, judge_error, embedding)."""
    return dict(Counter(p["label_source"] for p in pairs))


# --------------------------------------------------------------- alignment

def _hits(pairs: Iterable[dict[str, Any]], labels: frozenset = HIT_LABELS) -> set[tuple]:
    return {(p["system_id"], p["gt_id"]) for p in pairs if p["label"] in labels}


def _prf(tp_p: int, n_p: int, tp_r: int, n_r: int) -> dict[str, Any]:
    precision = tp_p / n_p if n_p else 0.0
    recall = tp_r / n_r if n_r else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4),
            "tp_precision": tp_p, "n_precision": n_p, "tp_recall": tp_r, "n_recall": n_r}


def alignment_shares(dimensions: list[dict], values: list[Item], decisions: dict[str, dict],
                     options: list[Item], hits: set[tuple]) -> dict[tuple, dict[str, Any]]:
    """Share of each (dimension, decision) pair: matched items over the smaller side.

    The numerator is min(distinct values of the dimension, distinct options of the
    decision) among the hits between them; the denominator is min(values of the
    dimension, options of the decision), so a share is at most 1.
    """
    dim_values: dict[str, list[str]] = {d["id"]: [] for d in dimensions}
    for v in values:
        for pid in v.parent_ids:
            dim_values.setdefault(pid, []).append(v.id)
    dec_options: dict[str, list[str]] = {d: [] for d in decisions}
    for o in options:
        for pid in o.parent_ids:
            if pid in dec_options:
                dec_options[pid].append(o.id)
    value_dim = {v.id: v.parent_ids for v in values}
    option_dec = {o.id: [p for p in o.parent_ids if p in decisions] for o in options}
    matched: dict[tuple, tuple] = {}
    for sid, oid in hits:
        for dim in value_dim.get(sid, []):
            for dec in option_dec.get(oid, []):
                vs, os_ = matched.setdefault((dim, dec), (set(), set()))
                vs.add(sid)
                os_.add(oid)
    shares = {}
    for (dim, dec), (vs, os_) in matched.items():
        denom = min(len(dim_values.get(dim, [])), len(dec_options.get(dec, [])))
        if denom:
            shares[(dim, dec)] = {"share": round(min(len(vs), len(os_)) / denom, 4), "matched": min(len(vs), len(os_))}
    return shares


def align_dimensions(shares: dict[tuple, dict[str, Any]], min_share: float,
                     tie_break: dict[tuple, float] | None = None) -> dict[str, list[tuple]]:
    """Strict (one-to-one, ``linear_sum_assignment``) and lenient alignment above ``min_share``.

    ``tie_break`` maps (dimension, decision) to an embedding distance of their names
    and descriptions; a smaller distance wins between equal shares.
    """
    from scipy.optimize import linear_sum_assignment

    eligible = {k: v["share"] for k, v in shares.items() if v["share"] >= min_share}
    lenient = sorted(eligible)
    if not eligible:
        return {"strict": [], "lenient": []}
    dims = sorted({d for d, _ in eligible})
    decs = sorted({d for _, d in eligible})
    dim_index = {d: i for i, d in enumerate(dims)}
    dec_index = {d: i for i, d in enumerate(decs)}
    cost = np.zeros((len(dims), len(decs)))
    for (dim, dec), share in eligible.items():
        eps = (tie_break or {}).get((dim, dec), 1.0) * 1e-6
        cost[dim_index[dim], dec_index[dec]] = -(share - eps)
    rows, cols = linear_sum_assignment(cost)
    strict = sorted((dims[r], decs[c]) for r, c in zip(rows, cols) if (dims[r], decs[c]) in eligible)
    return {"strict": strict, "lenient": lenient}


# ----------------------------------------------------------------- metrics

def matching_size(edges: set[tuple]) -> int:
    """Size of a maximum one-to-one matching of (system, ground-truth) edges."""
    from scipy.optimize import linear_sum_assignment

    if not edges:
        return 0
    left = {a: i for i, a in enumerate(sorted({a for a, _ in edges}))}
    right = {b: i for i, b in enumerate(sorted({b for _, b in edges}))}
    weight = np.zeros((len(left), len(right)))
    for a, b in edges:
        weight[left[a], right[b]] = 1.0
    rows, cols = linear_sum_assignment(-weight)
    return int(weight[rows, cols].sum())


def jaccard(matched: int, n_system: int, n_truth: int) -> float:
    """Overlap over union, |S ∩ G| / |S ∪ G|, with ``matched`` one-to-one matched pairs."""
    union = n_system + n_truth - matched
    return round(matched / union, 4) if union > 0 else 0.0


def compute_metrics(dimensions: list[dict], values: list[Item], views: dict[str, dict], options: list[Item],
                    pairs: list[dict[str, Any]], min_alignment_share: float,
                    tie_break: dict[tuple, float] | None = None) -> dict[str, Any]:
    """Option-level, decision-level and placement metrics per view (paper plan §5.1 M7)."""
    hits = _hits(pairs)
    exact = _hits(pairs, frozenset({"same"}))
    related = _hits(pairs, frozenset({"related"}))
    all_decisions = ground_truth_decisions(views)
    union_alignment = align_dimensions(
        alignment_shares(dimensions, values, all_decisions, options, hits), min_alignment_share, tie_break)
    value_ids = [v.id for v in values]
    dim_ids = [d["id"] for d in dimensions]

    result: dict[str, Any] = {}
    for view_name in views:
        view_opts = [o for o in options if view_name in o.views]
        view_opt_ids = {o.id for o in view_opts}
        other_opt_ids = {o.id for o in options} - view_opt_ids
        view_decs = {d: info for d, info in all_decisions.items() if view_name in info["views"]}

        # Option level
        view_hits = {(s, o) for s, o in hits if o in view_opt_ids}
        hit_values = {s for s, _ in view_hits}
        only_other = {s for s, o in hits if o in other_opt_ids} - hit_values
        precision_pool = [v for v in value_ids if v not in only_other]
        option = _prf(len(hit_values), len(precision_pool), len({o for _, o in view_hits}), len(view_opts))
        option["exact_recall"] = round(len({o for s, o in exact if o in view_opt_ids}) / len(view_opts), 4) \
            if view_opts else 0.0
        related_values = {s for s, o in related if o in view_opt_ids} - hit_values
        option["related_rate"] = round(len(related_values) / len(value_ids), 4) if value_ids else 0.0
        option["model_only_matched_values"] = len(only_other)
        # Jaccard on one-to-one matchings (a generic value counts once), same pools as P and R.
        pool = set(precision_pool)
        option["jaccard"] = jaccard(matching_size({(s_, o) for s_, o in view_hits if s_ in pool}),
                                    len(precision_pool), len(view_opts))
        option["jaccard_same"] = jaccard(
            matching_size({(s_, o) for s_, o in exact if o in view_opt_ids and s_ in pool}),
            len(precision_pool), len(view_opts))

        # Decision level (alignment restricted to the view's decisions and options)
        shares = alignment_shares(dimensions, values, view_decs, view_opts, view_hits)
        alignment = align_dimensions(shares, min_alignment_share, tie_break)
        outside = {d for d in dim_ids
                   if any(dim == d for dim, _ in union_alignment["lenient"])
                   and all(dec not in view_decs for dim, dec in union_alignment["lenient"] if dim == d)}
        # A dimension aligned within the view stays in its pool (lenient covers strict), so precision <= 1.
        outside -= {d for d, _ in alignment["lenient"]}
        decision: dict[str, Any] = {}
        dim_pool = [d for d in dim_ids if d not in outside]
        for kind in ("strict", "lenient"):
            aligned = alignment[kind]
            decision[kind] = _prf(len({d for d, _ in aligned}), len(dim_pool), len({c for _, c in aligned}),
                                  len(view_decs))
        decision["dimensions_aligned_only_outside_view"] = len(outside)
        decision["jaccard"] = jaccard(len(alignment["strict"]), len(dim_pool), len(view_decs))

        # Placement: matched values whose dimension is aligned (lenient) with a decision of a matched option
        lenient = set(alignment["lenient"])
        option_decs = {o.id: [p for p in o.parent_ids if p in view_decs] for o in view_opts}
        value_dims = {v.id: v.parent_ids for v in values}
        placed = {s for s, o in view_hits
                  if any((dim, dec) in lenient for dim in value_dims.get(s, []) for dec in option_decs.get(o, []))}
        placement = {"matched_values": len(hit_values), "placed": len(placed),
                     "accuracy": round(len(placed) / len(hit_values), 4) if hit_values else None}

        result[view_name] = {"option": option, "decision": decision, "placement": placement,
                             "alignment": {k: [list(p) for p in v] for k, v in alignment.items()},
                             "shares": [{"dimension_id": d, "decision_id": c, **s} for (d, c), s in sorted(shares.items())]}
    return result


# ----------------------------------------------------------------- outputs

def write_outputs(out_dir: Path | str, stem: str, pairs: list[dict[str, Any]], metrics: dict[str, Any],
                  settings_record: dict[str, Any], names: dict[str, str] | None = None) -> dict[str, Path]:
    """Match file (every pair), alignment sheet (CSV) and metrics file (paper plan §5.1 M11)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    names = names or {}
    paths = {"match": out_dir / f"{stem}_gt_match.json", "alignment": out_dir / f"{stem}_gt_alignment.csv",
             "metrics": out_dir / f"{stem}_gt_metrics.json"}
    paths["match"].write_text(json.dumps({"settings": settings_record, "label_sources": label_counts(pairs),
                                          "pairs": pairs}, indent=1, ensure_ascii=False), encoding="utf-8")
    with paths["alignment"].open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["view", "alignment", "dimension_id", "dimension_name", "decision_id", "decision_name",
                         "share", "matched"])
        for view_name, m in metrics.items():
            shares = {(s["dimension_id"], s["decision_id"]): s for s in m["shares"]}
            for kind in ("strict", "lenient"):
                for dim, dec in m["alignment"][kind]:
                    s = shares.get((dim, dec), {})
                    writer.writerow([view_name, kind, dim, names.get(f"dim:{dim}", ""), dec,
                                     names.get(f"dec:{dec}", ""), s.get("share", ""), s.get("matched", "")])
    summary = {view: {k: v for k, v in m.items() if k not in ("shares", "alignment")} for view, m in metrics.items()}
    paths["metrics"].write_text(json.dumps({**summary, "settings": settings_record}, indent=2), encoding="utf-8")
    return paths


# ----------------------------------------------------------------- command

@functools.cache
def _gt_validator() -> Any:
    """The ground-truth validator (``benchmark/gt_format.py``) in a source checkout, else ``None``."""
    fmt = Path(__file__).resolve().parents[3] / "benchmark" / "gt_format.py"
    if not fmt.exists():
        return None
    import importlib.util
    spec = importlib.util.spec_from_file_location("gt_format", fmt)
    if spec is None or spec.loader is None:
        return None
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    return validator


def load_gt_folder(folder: Path | str) -> dict[str, dict]:
    """Load a study's ground-truth views (``gt_paper.json``, ``gt_model.json``), validated when possible."""
    folder = Path(folder)
    views = {}
    validator = _gt_validator()
    for name in ("paper", "model"):
        path = folder / f"gt_{name}.json"
        if not path.exists():
            continue
        if validator is not None:
            data, _warnings = validator.load_ground_truth(path)
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
        views[name] = data
    if not views:
        raise MatcherError(f"no gt_paper.json or gt_model.json in {folder}")
    return views


def _git_commit(path: Path) -> str:
    import subprocess
    try:
        folder = path.resolve() if path.is_dir() else path.resolve().parent
        return subprocess.run(["git", "-C", str(folder), "log", "-1", "--format=%h", "--", "."],
                              capture_output=True, text=True, check=False).stdout.strip()
    except OSError:
        return ""


async def run_match(taxonomy_path: str, gt_folder: str, settings: Any, matching_llm_override: str | None = None,
                    mode_override: str | None = None,
                    out_dir: str | None = None, view: str = "selected",
                    embed: Callable[[list[str]], np.ndarray] | None = None,
                    judge_model: Any = None) -> dict[str, Any]:
    """Score one saved taxonomy against one study's ground truth and write the three outputs."""
    from taxonomy_generator.utils import load_seed_taxonomy

    config = MatcherConfig.from_settings(settings)
    if matching_llm_override:
        config = dataclasses.replace(config, matching_llm=matching_llm_override)
    if mode_override:
        config = dataclasses.replace(config, mode=check_mode(mode_override))
    # The embeddings-only mode makes no LLM call, so it needs no matching LLM.
    bare_judge = check_matching_llm(config.matching_llm) if config.mode == "judge" else ""
    warnings = llm_warnings(config) if config.mode == "judge" else []
    for warning in warnings:
        logger.warning(warning)

    clusters = load_seed_taxonomy(taxonomy_path, view=view)
    views = load_gt_folder(gt_folder)
    dimensions = system_dimensions(clusters)
    values = system_values(clusters, include_outcomes=config.include_outcomes)
    options = ground_truth_options(views)
    embed = embed or embedder_from_config(config)
    if judge_model is None and config.mode == "judge":
        judge_model = openai_judge_model(bare_judge)
    cache = JudgeCache(config.cache_path)
    try:
        pairs = await label_pairs(values, options, embed, judge_model, config, cache=cache)
    finally:
        cache.save()

    # Tie-break for dimension alignment: distance between dimension and decision texts.
    decisions = ground_truth_decisions(views)
    dim_texts = [f"{split_camel(d['name'])}: {d['description']}" for d in dimensions]
    dec_ids = list(decisions)
    dec_texts = [f"{split_camel(decisions[d]['name'])}: {decisions[d].get('question') or decisions[d].get('description', '')}"
                 for d in dec_ids]
    tie_break: dict[tuple, float] = {}
    if dim_texts and dec_texts:
        vec = embed(dim_texts + dec_texts)
        dist = pair_distances(vec[: len(dim_texts)], vec[len(dim_texts):])
        tie_break = {(dimensions[i]["id"], dec_ids[j]): float(dist[i, j])
                     for i in range(len(dimensions)) for j in range(len(dec_ids))}

    metrics = compute_metrics(dimensions, values, views, options, pairs, config.min_alignment_share, tie_break)
    record = {**config.as_record(), "llm_warnings": warnings, "taxonomy": str(taxonomy_path), "taxonomy_view": view,
              "ground_truth": str(gt_folder), "ground_truth_commit": _git_commit(Path(gt_folder)),
              "system_values": len(values), "ground_truth_options": len(options),
              "views": {name: sum(1 for o in options if name in o.views) for name in views},
              "gt_text_precedence": [name for name, _ in _views_in_text_precedence(views)]}
    names = {f"dim:{d['id']}": d["name"] for d in dimensions}
    names.update({f"dec:{d}": info["name"] for d, info in decisions.items()})
    stem = Path(taxonomy_path).stem.replace("_taxonomy_", "_") + ("_emb" if config.mode == "embeddings" else "")
    paths = write_outputs(out_dir or Path(taxonomy_path).parent, stem, pairs, metrics, record, names)
    return {"paths": paths, "metrics": metrics, "label_sources": label_counts(pairs), "settings": record}
