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
instructions, served by an OpenAI model that must differ from the generator
model (``matcher.judge_model``, else ``evaluation.judge_model``; never the
generator, ``models.model``). It sees the two
items as "Item 1" and "Item 2" in a seeded order, never which side is the
ground truth, and compares the design options themselves regardless of the
decision or dimension they sit under (placement is scored separately).
Judge results are cached on disk, so reruns are deterministic and cheap.
"""

from __future__ import annotations

import asyncio
import csv
import hashlib
import json
import logging
import random
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Set

import numpy as np
from pydantic import BaseModel

from taxonomy_generator.evaluation.judge import resolve_judge_model  # sets deepeval telemetry opt-out
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


class MatcherError(ValueError):
    """The matcher cannot run with the given configuration or inputs."""


# ------------------------------------------------------------------ config

@dataclass(frozen=True)
class MatcherConfig:
    judge_model: Optional[str]
    generator_model: Optional[str]
    embedding: str
    lower_threshold: float
    upper_threshold: float
    max_candidates: int
    include_outcomes: bool
    min_alignment_share: float
    seed: int
    cache_path: Optional[str]

    @classmethod
    def from_settings(cls, settings: Any) -> "MatcherConfig":
        """Build from ``Settings``: the ``matcher`` section plus the generator and embedding models.

        The judge is ``matcher.judge_model`` when set, else ``evaluation.judge_model`` (the
        configured judge of the pipeline); never ``models.model`` (the generator).
        """
        m = settings.matcher
        return cls(
            judge_model=m.judge_model or settings.evaluation.judge_model,
            generator_model=settings.models.model,
            embedding=m.embedding or settings.models.embedding,
            lower_threshold=float(m.lower_threshold),
            upper_threshold=float(m.upper_threshold),
            max_candidates=int(m.max_candidates),
            include_outcomes=bool(m.include_outcomes),
            min_alignment_share=float(m.min_alignment_share),
            seed=int(m.seed),
            cache_path=m.cache_path,
        )

    def as_record(self) -> Dict[str, Any]:
        return {**self.__dict__, "judge_version": JUDGE_VERSION}


def check_judge(judge_model: Optional[str], generator_model: Optional[str]) -> str:
    """Refuse an unset judge, a judge equal to the generator, or a non-OpenAI judge; return the bare name."""
    if not judge_model:
        raise MatcherError(
            "judge_model is not set: the matcher needs a judge model different from the generator "
            "(models.model) and never falls back to it. Set evaluation.judge_model (or matcher.judge_model) "
            "in the YAML config, or pass --judge-model."
        )

    def bare(name: Optional[str]) -> str:
        return (name or "").split("/", 1)[-1].strip().lower()

    if bare(judge_model) == bare(generator_model):
        raise MatcherError(
            f"judge model '{judge_model}' is the same model as the generator ('{generator_model}'); "
            "choose a different judge model."
        )
    try:
        resolved = resolve_judge_model(judge_model)
    except ValueError as exc:
        raise MatcherError(f"the judge model must be an OpenAI model: {exc}") from exc
    return resolved or judge_model


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
    parent_ids: List[str]
    parent_name: str
    status: str = ""
    views: Set[str] = field(default_factory=set)

    @property
    def text(self) -> str:
        return serialize(self.parent_name, self.name, self.description)


def system_dimensions(clusters: Sequence[Dict]) -> List[Dict[str, str]]:
    return [{"id": str(c.get("id")), "name": c.get("name", ""), "description": c.get("description", "")}
            for c in clusters if isinstance(c, dict)]


def system_values(clusters: Sequence[Dict], include_outcomes: bool = False) -> List[Item]:
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


def ground_truth_decisions(views: Dict[str, Dict]) -> Dict[str, Dict[str, Any]]:
    """Union of the views' decisions, with the views each belongs to."""
    decisions: Dict[str, Dict[str, Any]] = {}
    for view_name, view in views.items():
        for dec in view["decisions"]:
            entry = decisions.setdefault(dec["id"], {**dec, "views": set()})
            entry["views"].add(view_name)
    return decisions


def ground_truth_options(views: Dict[str, Dict]) -> List[Item]:
    """Union of the views' attached options (unattached ones are not scored), with view membership."""
    decisions = ground_truth_decisions(views)
    options: Dict[str, Item] = {}
    for view_name, view in views.items():
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
    label: str
    reason: str


def build_judge_prompt(first: str, second: str) -> str:
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


def _make_metric_base():
    from deepeval.metrics import BaseMetric  # imported lazily: heavy

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
            self.evaluation_model = getattr(model, "get_model_name", lambda: str(model))()
            self.include_reason = True
            self.async_mode = True
            self.strict_mode = False
            self.label: Optional[str] = None
            self.warning = ""

        async def a_measure(self, test_case, *args, **kwargs) -> float:
            prompt = build_judge_prompt(test_case.input, test_case.actual_output)
            self.warning = ""
            answers = []
            for _ in range(2):
                verdict, _cost = await self.model.a_generate(prompt, schema=JudgeVerdict)
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
            self.success = self.score >= self.threshold
            return self.score

        def measure(self, test_case, *args, **kwargs) -> float:
            import asyncio
            return asyncio.run(self.a_measure(test_case))

        def is_successful(self) -> bool:
            return bool(self.success)

        @property
        def __name__(self):
            return "Graded option match"

    return GradedMatchMetric


_METRIC_CLASS = None


def graded_match_metric(model: Any):
    global _METRIC_CLASS
    if _METRIC_CLASS is None:
        _METRIC_CLASS = _make_metric_base()
    return _METRIC_CLASS(model)


def openai_judge_model(judge_model: str):
    """deepeval OpenAIModel for the judge (temperature 1.0, as the scoreboard uses)."""
    from deepeval.models import OpenAIModel
    return OpenAIModel(model=judge_model, temperature=1.0)


class JudgeCache:
    """Judge verdicts on disk, keyed by judge model, instructions and the ordered pair."""

    def __init__(self, path: Optional[str]):
        self.path = Path(path) if path else None
        self.data: Dict[str, Dict[str, str]] = {}
        if self.path and self.path.exists():
            self.data = json.loads(self.path.read_text(encoding="utf-8"))

    @staticmethod
    def key(judge: str, first: str, second: str) -> str:
        return hashlib.sha256(json.dumps([judge, JUDGE_VERSION, first, second]).encode()).hexdigest()

    def get(self, key: str) -> Optional[Dict[str, str]]:
        return self.data.get(key)

    def put(self, key: str, verdict: Dict[str, str]) -> None:
        self.data[key] = verdict

    def save(self) -> None:
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self.data, indent=1, sort_keys=True), encoding="utf-8")


# ------------------------------------------------------------------- pairs

def pair_distances(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Cosine distances (1 - cosine similarity, in [0, 2]) between the rows of ``a`` and ``b``."""
    a, b = l2_normalize(a), l2_normalize(b)
    return np.clip(1.0 - a @ b.T, 0.0, 2.0)


def embedder_from_config(config: MatcherConfig) -> Callable[[List[str]], np.ndarray]:
    from taxonomy_generator.utils import load_embeddings_model
    model = load_embeddings_model(config.embedding)
    return lambda texts: np.asarray(model.embed_documents(texts), dtype=float)


async def label_pairs(system: List[Item], options: List[Item], embed: Callable[[List[str]], np.ndarray],
                      judge_model: Any, config: MatcherConfig,
                      cache: Optional[JudgeCache] = None, concurrency: int = 8) -> List[Dict[str, Any]]:
    """Label every (system value, ground-truth option) pair exactly once.

    ``label_source`` is ``auto`` (distance at or below the lower threshold, which
    0 disables, or above the upper one), ``judge`` (borderline pair whose items are among each
    other's ``max_candidates`` nearest neighbours) or ``auto_rank`` (borderline
    pair outside those neighbourhoods, labeled ``different`` without the judge).
    """
    from deepeval.test_case import LLMTestCase

    if not system or not options:
        return []
    vectors = embed([s.text for s in system] + [o.text for o in options])
    dist = pair_distances(vectors[: len(system)], vectors[len(system):])
    k = max(1, config.max_candidates)
    near_sys = np.argsort(dist, axis=1)[:, :k]      # nearest options per value
    near_opt = np.argsort(dist, axis=0)[:k, :]      # nearest values per option
    judge_name = getattr(judge_model, "get_model_name", lambda: str(judge_model))()

    pairs: List[Dict[str, Any]] = []
    jobs: Dict[str, List[tuple]] = {}   # cache key -> [(record, order, first, second)]
    for i, value in enumerate(system):
        for j, option in enumerate(options):
            d = float(dist[i, j])
            record = {"system_id": value.id, "system_text": value.text, "gt_id": option.id,
                      "gt_text": option.text, "distance": round(d, 4), "label": "different",
                      "label_source": "auto", "reason": "", "order": "", "warning": ""}
            pairs.append(record)
            if config.lower_threshold > 0 and d <= config.lower_threshold:  # 0 disables auto-"same"
                record["label"] = "same"
            elif d > config.upper_threshold:
                pass
            elif j not in near_sys[i] and i not in near_opt[:, j]:
                record["label_source"] = "auto_rank"
            else:
                rng = random.Random(f"{config.seed}:{value.id}:{option.id}")
                order = "system_first" if rng.random() < 0.5 else "gt_first"
                first, second = (value.text, option.text) if order == "system_first" else (option.text, value.text)
                jobs.setdefault(JudgeCache.key(judge_name, first, second), []).append((record, order, first, second))

    semaphore = asyncio.Semaphore(max(1, concurrency))

    async def judge(key: str, first: str, second: str) -> Dict[str, str]:
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
    verdicts = await asyncio.gather(*(judge(k, jobs[k][0][2], jobs[k][0][3]) for k in keys))
    for key, verdict in zip(keys, verdicts):
        for record, order, _first, _second in jobs[key]:
            record.update(label=orient_label(verdict["label"], order), raw_label=verdict["label"],
                          label_source="judge", reason=verdict.get("reason", ""), order=order,
                          warning=verdict.get("warning", ""))
    return pairs


def label_counts(pairs: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for p in pairs:
        counts[p["label_source"]] = counts.get(p["label_source"], 0) + 1
    return counts


# --------------------------------------------------------------- alignment

def _hits(pairs: Iterable[Dict[str, Any]], labels: frozenset = HIT_LABELS) -> Set[tuple]:
    return {(p["system_id"], p["gt_id"]) for p in pairs if p["label"] in labels}


def _prf(tp_p: int, n_p: int, tp_r: int, n_r: int) -> Dict[str, Any]:
    precision = tp_p / n_p if n_p else 0.0
    recall = tp_r / n_r if n_r else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4),
            "tp_precision": tp_p, "n_precision": n_p, "tp_recall": tp_r, "n_recall": n_r}


def alignment_shares(dimensions: List[Dict], values: List[Item], decisions: Dict[str, Dict],
                     options: List[Item], hits: Set[tuple]) -> Dict[tuple, Dict[str, Any]]:
    """Share of each (dimension, decision) pair: matched items over the smaller side.

    The numerator is min(distinct values of the dimension, distinct options of the
    decision) among the hits between them; the denominator is min(values of the
    dimension, options of the decision), so a share is at most 1.
    """
    dim_values: Dict[str, List[str]] = {d["id"]: [] for d in dimensions}
    for v in values:
        for pid in v.parent_ids:
            dim_values.setdefault(pid, []).append(v.id)
    dec_options: Dict[str, List[str]] = {d: [] for d in decisions}
    for o in options:
        for pid in o.parent_ids:
            if pid in dec_options:
                dec_options[pid].append(o.id)
    value_dim = {v.id: v.parent_ids for v in values}
    option_dec = {o.id: [p for p in o.parent_ids if p in decisions] for o in options}
    matched: Dict[tuple, tuple] = {}
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


def align_dimensions(shares: Dict[tuple, Dict[str, Any]], min_share: float,
                     tie_break: Optional[Dict[tuple, float]] = None) -> Dict[str, List[tuple]]:
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
    cost = np.zeros((len(dims), len(decs)))
    for (dim, dec), share in eligible.items():
        eps = (tie_break or {}).get((dim, dec), 1.0) * 1e-6
        cost[dims.index(dim), decs.index(dec)] = -(share - eps)
    rows, cols = linear_sum_assignment(cost)
    strict = sorted((dims[r], decs[c]) for r, c in zip(rows, cols) if (dims[r], decs[c]) in eligible)
    return {"strict": strict, "lenient": lenient}


# ----------------------------------------------------------------- metrics

def compute_metrics(dimensions: List[Dict], values: List[Item], views: Dict[str, Dict], options: List[Item],
                    pairs: List[Dict[str, Any]], min_alignment_share: float,
                    tie_break: Optional[Dict[tuple, float]] = None) -> Dict[str, Any]:
    """Option-level, decision-level and placement metrics per view (paper plan §5.1 M7)."""
    hits = _hits(pairs)
    exact = _hits(pairs, frozenset({"same"}))
    related = _hits(pairs, frozenset({"related"}))
    all_decisions = ground_truth_decisions(views)
    union_alignment = align_dimensions(
        alignment_shares(dimensions, values, all_decisions, options, hits), min_alignment_share, tie_break)
    value_ids = [v.id for v in values]
    dim_ids = [d["id"] for d in dimensions]

    result: Dict[str, Any] = {}
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

        # Decision level (alignment restricted to the view's decisions and options)
        shares = alignment_shares(dimensions, values, view_decs, view_opts, view_hits)
        alignment = align_dimensions(shares, min_alignment_share, tie_break)
        outside = {d for d in dim_ids
                   if any(dim == d for dim, _ in union_alignment["lenient"])
                   and all(dec not in view_decs for dim, dec in union_alignment["lenient"] if dim == d)}
        decision = {}
        for kind in ("strict", "lenient"):
            aligned = alignment[kind]
            pool = [d for d in dim_ids if d not in outside]
            decision[kind] = _prf(len({d for d, _ in aligned}), len(pool), len({c for _, c in aligned}), len(view_decs))
        decision["dimensions_aligned_only_outside_view"] = len(outside)

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

def write_outputs(out_dir: Path | str, stem: str, pairs: List[Dict[str, Any]], metrics: Dict[str, Any],
                  settings_record: Dict[str, Any], names: Optional[Dict[str, str]] = None) -> Dict[str, Path]:
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

def load_gt_folder(folder: Path | str) -> Dict[str, Dict]:
    """Load a study's ground-truth views (``gt_paper.json``, ``gt_model.json``), validated when possible."""
    folder = Path(folder)
    views = {}
    validator = None
    fmt = Path(__file__).resolve().parents[3] / "benchmark" / "gt_format.py"
    if fmt.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("gt_format", fmt)
        validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validator)
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
        return subprocess.run(["git", "log", "-1", "--format=%h", "--", str(path)], capture_output=True,
                              text=True, cwd=path if path.is_dir() else path.parent, check=False).stdout.strip()
    except OSError:
        return ""


async def run_match(taxonomy_path: str, gt_folder: str, settings: Any, judge_override: Optional[str] = None,
                    out_dir: Optional[str] = None, view: str = "selected",
                    embed: Optional[Callable[[List[str]], np.ndarray]] = None,
                    judge_model: Any = None) -> Dict[str, Any]:
    """Score one saved taxonomy against one study's ground truth and write the three outputs."""
    from taxonomy_generator.utils import load_seed_taxonomy

    config = MatcherConfig.from_settings(settings)
    if judge_override:
        config = MatcherConfig(**{**config.__dict__, "judge_model": judge_override})
    bare_judge = check_judge(config.judge_model, config.generator_model)

    clusters = load_seed_taxonomy(taxonomy_path, view=view)
    views = load_gt_folder(gt_folder)
    dimensions = system_dimensions(clusters)
    values = system_values(clusters, include_outcomes=config.include_outcomes)
    options = ground_truth_options(views)
    embed = embed or embedder_from_config(config)
    judge_model = judge_model or openai_judge_model(bare_judge)
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
    tie_break: Dict[tuple, float] = {}
    if dim_texts and dec_texts:
        vec = embed(dim_texts + dec_texts)
        dist = pair_distances(vec[: len(dim_texts)], vec[len(dim_texts):])
        tie_break = {(dimensions[i]["id"], dec_ids[j]): float(dist[i, j])
                     for i in range(len(dimensions)) for j in range(len(dec_ids))}

    metrics = compute_metrics(dimensions, values, views, options, pairs, config.min_alignment_share, tie_break)
    record = {**config.as_record(), "taxonomy": str(taxonomy_path), "taxonomy_view": view,
              "ground_truth": str(gt_folder), "ground_truth_commit": _git_commit(Path(gt_folder)),
              "system_values": len(values), "ground_truth_options": len(options),
              "views": {name: sum(1 for o in options if name in o.views) for name in views}}
    names = {f"dim:{d['id']}": d["name"] for d in dimensions}
    names.update({f"dec:{d}": info["name"] for d, info in decisions.items()})
    stem = Path(taxonomy_path).stem.replace("_taxonomy_", "_")
    paths = write_outputs(out_dir or Path(taxonomy_path).parent, stem, pairs, metrics, record, names)
    return {"paths": paths, "metrics": metrics, "label_sources": label_counts(pairs), "settings": record}
