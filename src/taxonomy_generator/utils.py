"""Shared helpers: model loading, prompt formatting, and merge math."""
import copy
import json
import logging
from typing import Dict, Iterable, List, Tuple

import numpy as np
from langchain.chat_models import init_chat_model
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable, RunnableConfig

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.schemas import TaxonomyOutput
from taxonomy_generator.state import Doc, State

logger = logging.getLogger(__name__)


def strings_to_docs(texts: List[str]) -> List[Doc]:
    """Convert a list of strings into Doc objects with auto-generated IDs.

    This is the primary entry point for providing an arbitrary corpus to the
    taxonomy generation pipeline. Each string becomes a Doc with a unique ID.

    Args:
        texts: A list of raw text strings representing the corpus.

    Returns:
        List[Doc]: A list of Doc objects ready for pipeline processing.
    """
    from uuid import uuid4
    return [Doc(id=str(uuid4()), content=text) for text in texts]


def docs_from_dicts(dicts: List[Dict]) -> List[Doc]:
    """Convert a list of dictionaries into Doc objects.

    Each dict should have at least 'id' and 'content' keys.
    Missing keys will use defaults.

    Args:
        dicts: A list of dictionaries with document data.

    Returns:
        List[Doc]: A list of Doc objects ready for pipeline processing.
    """
    from uuid import uuid4
    docs = []
    for d in dicts:
        if isinstance(d, Doc):
            docs.append(d)
        elif isinstance(d, dict):
            docs.append(Doc(
                id=d.get("id", str(uuid4())),
                content=d.get("content", ""),
                summary=d.get("summary"),
                explanation=d.get("explanation"),
                category=d.get("category"),
                value=d.get("value"),
            ))
        else:
            docs.append(Doc(id=str(uuid4()), content=str(d)))
    return docs


def load_chat_model(fully_specified_name: str) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'provider/model'.
    """
    provider, model = fully_specified_name.split("/", maxsplit=1)
    logger.debug("Loading chat model: provider=%s, model=%s", provider, model)
    return init_chat_model(model, model_provider=provider)


def load_embeddings_model(fully_specified_name: str) -> Embeddings:
    """Load an embeddings model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'provider/model'.

    Returns:
        An initialized LangChain ``Embeddings`` instance.
    """
    provider, model = fully_specified_name.split("/", maxsplit=1)
    logger.debug("Loading embeddings model: provider=%s, model=%s", provider, model)

    if provider == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(model=model)
    if provider == "ollama":
        from langchain_ollama import OllamaEmbeddings
        return OllamaEmbeddings(model=model)

    raise ValueError(
        f"Unsupported embeddings provider: '{provider}'. "
        "Use 'openai/<model>' or 'ollama/<model>'."
    )


def format_docs(docs: List[Doc]) -> str:
    """Format document summaries as JSON for taxonomy generation.

    Args:
        docs: List of documents to format

    Returns:
        str: JSON formatted document summaries
    """
    items = []
    for doc in docs:
        doc_id = doc["id"] if isinstance(doc, dict) else doc.id
        if isinstance(doc, dict):
            doc_summary = doc.get("summary") or doc.get("content", "")
        else:
            doc_summary = doc.summary or doc.content or ""
        items.append({"id": doc_id, "summary": doc_summary})
    return json.dumps(items, indent=2)


def format_open_codes_for_docs(docs: List[Doc], open_codes: List[Dict]) -> str:
    """Format the open codes of a batch of documents as JSON for axial coding.

    Groups accumulated open codes by ``doc_id`` restricted to the given batch.
    Documents whose open coding produced no codes fall back to their summary so
    no document is silently dropped from the taxonomy input.

    Args:
        docs: Documents in the minibatch.
        open_codes: Accumulated open-code dicts (with ``doc_id``/``label``/``rationale``/``status``).

    Returns:
        str: JSON formatted open codes, one entry per document. Each code
        carries ``status`` (accepted/rejected/outcome) so axial coding can act
        on it — see ``taxonomy_generation.md``/``taxonomy_update.md``.
    """
    codes_by_doc: Dict[str, List[Dict]] = {}
    for code in open_codes:
        doc_id = code.get("doc_id") if isinstance(code, dict) else getattr(code, "doc_id", None)
        if doc_id is None:
            continue
        entry = code if isinstance(code, dict) else {
            "doc_id": code.doc_id,
            "label": code.label,
            "rationale": code.rationale,
            "status": code.status,
        }
        codes_by_doc.setdefault(doc_id, []).append({
            "label": entry.get("label", ""),
            "rationale": entry.get("rationale", ""),
            "status": entry.get("status", "accepted"),
        })

    items = []
    for doc in docs:
        doc_id = doc["id"] if isinstance(doc, dict) else doc.id
        codes = codes_by_doc.get(doc_id, [])
        if codes:
            items.append({"id": doc_id, "codes": codes})
        else:
            # Fallback: keep code-less documents visible to axial coding.
            if isinstance(doc, dict):
                summary = doc.get("summary") or doc.get("content", "")
            else:
                summary = doc.summary or doc.content or ""
            items.append({"id": doc_id, "codes": [{"label": summary, "rationale": "No open codes extracted; summary used.", "status": "accepted"}]})
    return json.dumps(items, indent=2)


def format_taxonomy(clusters: List[Dict[str, str]], include_values: bool = True) -> str:
    """Format taxonomy clusters as JSON.

    When ``include_values`` is true and a cluster carries ``relations`` or
    ``values``, they are serialized alongside id/name/description so downstream
    steps (update, labeling) can reason over the full design space.

    Args:
        clusters: List of cluster dictionaries
        include_values: Whether to include relations and values when present.

    Returns:
        str: JSON formatted taxonomy
    """
    items = []
    for cluster in clusters:
        if isinstance(cluster, dict):
            item = {
                "id": cluster.get("id", ""),
                "name": cluster.get("name", ""),
                "description": cluster.get("description", ""),
            }
            if include_values:
                if cluster.get("relations"):
                    item["relations"] = cluster.get("relations", [])
                if cluster.get("values"):
                    item["values"] = cluster.get("values", [])
            items.append(item)
        else:
            item = {
                "id": getattr(cluster, "id", ""),
                "name": getattr(cluster, "name", ""),
                "description": getattr(cluster, "description", ""),
            }
            if include_values:
                relations = getattr(cluster, "relations", None) or []
                values = getattr(cluster, "values", None) or []
                if relations:
                    item["relations"] = [r.model_dump() if hasattr(r, "model_dump") else r for r in relations]
                if values:
                    item["values"] = [v.model_dump() if hasattr(v, "model_dump") else v for v in values]
            items.append(item)
    return json.dumps(items, indent=2)


MAX_FEEDBACK_CRITERIA = 5
MAX_REASON_CHARS = 700


def _shorten(text: str, limit: int) -> str:
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return f"{cut} …"


def format_evaluation_summary(scoreboard: Dict, exclude: Iterable[str] = ()) -> str:
    """Format an evaluation scoreboard as actionable feedback for the next pass.

    Criteria below the pass threshold come first, weakest first, each with the
    judge's reason, which names the dimensions/values at fault and the change
    that fixes them (see ``evaluation/metrics.py``). At most
    ``MAX_FEEDBACK_CRITERIA`` reasons are included, each shortened to
    ``MAX_REASON_CHARS``. When every criterion passes, the weakest one's reason
    is still given. Passing criteria are listed by score only, to be preserved.
    Criteria marked ``"evaluated": False`` (no documents for a data-grounded
    criterion) are excluded — they carry no score to act on — and so are the
    criteria named in ``exclude`` (scored and reported, but not fed back).

    Args:
        scoreboard: A scoreboard dict per ``evaluation/runner.py::run_scoreboard``
            (``{"criteria": [...], "overall": ..., "model": ..., "unavailable": ...}``).
        exclude: Names of criteria to leave out of the feedback.

    Returns:
        A multi-line feedback section, or ``""`` if there is nothing scored.
    """
    excluded = set(exclude or ())
    criteria = [
        c for c in scoreboard.get("criteria", [])
        if c.get("evaluated") is not False and isinstance(c.get("score"), (int, float))
        and c.get("name") not in excluded
    ]
    if not criteria:
        return ""

    criteria = sorted(criteria, key=lambda c: c["score"])
    threshold = criteria[0].get("threshold")
    if not isinstance(threshold, (int, float)):
        threshold = 0.5
    failing = [c for c in criteria if c["score"] < threshold]
    to_fix = (failing or criteria[:1])[:MAX_FEEDBACK_CRITERIA]
    also_failing = [c for c in failing if c not in to_fix]
    to_keep = [c for c in criteria if c not in to_fix and c not in failing]

    overall = scoreboard.get("overall")
    overall_str = f"{overall:.2f}" if isinstance(overall, (int, float)) else "n/a"
    lines = [
        f"Automated evaluation summary for the current taxonomy (overall {overall_str}, "
        f"pass threshold {threshold:.2f}).",
        "These issues concern the existing taxonomy, not the new data: fix them in this pass "
        "even if the new documents do not show them. Apply the concrete changes named below "
        "(split, merge, move values, rename, add, drop) when they are consistent with the "
        "data seen so far; move supported values rather than deleting them. Never add a "
        "dimension or value that no open code supports, even when an issue asks for it.",
        "Issues to fix (weakest criterion first):",
    ]
    for criterion in to_fix:
        name = criterion.get("name", "Unnamed criterion")
        reason = _shorten(criterion.get("reason", ""), MAX_REASON_CHARS)
        line = f"- {name}: {criterion['score']:.2f}"
        if reason:
            line += f". Judge: {reason}"
        lines.append(line)
    if also_failing:
        rest = ", ".join(f"{c.get('name', 'Unnamed criterion')} {c['score']:.2f}" for c in also_failing)
        lines.append(f"Also below the threshold (address after the issues above): {rest}.")
    if to_keep:
        kept = ", ".join(f"{c.get('name', 'Unnamed criterion')} {c['score']:.2f}" for c in to_keep)
        lines.append(f"Passing criteria (preserve what they reward): {kept}.")
    return "\n".join(lines)


def format_feedback(state: State, exclude_criteria: Iterable[str] = ()) -> str:
    """Format feedback from state into a string for taxonomy prompts.

    Merges all feedback channels when present, in order: external feedback
    (``state.external_feedback``, persistent for the whole run — CLI flag,
    feedback file, or config text), the automated saturation critic's
    content (``state.user_feedback``, rewritten every iteration), then the
    latest automated evaluation scoreboard (``state.evaluation_history``,
    written by the observe-only ``evaluate_taxonomy`` node — omitted when
    absent or marked unavailable).

    Returns ``"None."`` when no feedback is present so the LLM receives
    a clear signal to proceed with standard clustering.

    Args:
        state: Current pipeline state.
        exclude_criteria: Evaluation criteria left out of the feedback
            (``evaluation.feedback_exclude``).

    Returns:
        Formatted feedback string.
    """
    parts: List[str] = []

    external = getattr(state, "external_feedback", None)
    if external and external.feedback:
        parts.append(f"User feedback: {external.feedback}")
        if external.explanation:
            parts.append(f"Reason for modification: {external.explanation}")

    if state.user_feedback:
        parts.append(f"Previous user feedback: {state.user_feedback.feedback}")
        if state.user_feedback.explanation:
            parts.append(f"Reason for modification: {state.user_feedback.explanation}")

    history = getattr(state, "evaluation_history", None)
    latest_evaluation = history[-1] if history else None
    # Only a scoreboard of the current draft is actionable: with
    # evaluation.every_n_iterations > 1 the latest one may describe an older
    # draft whose ids and structure no longer exist.
    scored_iteration = (latest_evaluation or {}).get("iteration")
    current = scored_iteration is None or scored_iteration == len(state.clusters or [])
    if latest_evaluation and current and not latest_evaluation.get("unavailable"):
        evaluation_section = format_evaluation_summary(latest_evaluation, exclude_criteria)
        if evaluation_section:
            parts.append(evaluation_section)

    if not parts:
        return "None."
    return "\n".join(parts)


SEED_VIEWS = ("auto", "selected", "final")


def resolve_seed_view(view: str | None, mode: str | None) -> str:
    """Which view of a saved taxonomy seeds a run: ``"selected"`` or ``"final"``.

    ``auto`` (default) uses the selected view in test mode, since that is the
    design space a run reports (the final iteration still holds dimensions that
    selection dropped), and the final iteration in train mode, where refinement
    starts from the full taxonomy (the bootstrap decision).
    """
    view = view or "auto"
    if view not in SEED_VIEWS:
        raise ValueError(f"taxonomy_input_view must be one of {SEED_VIEWS}, got {view!r}")
    if view == "auto":
        return "selected" if mode == "test" else "final"
    return view


def _prune_relations(clusters: List[Dict]) -> List[Dict]:
    """Drop relations whose target dimension is not in ``clusters``."""
    ids = {str(c.get("id")) for c in clusters}
    pruned = []
    for cluster in clusters:
        cluster = dict(cluster)
        if cluster.get("relations"):
            cluster["relations"] = [
                r for r in cluster["relations"]
                if not isinstance(r, dict) or str(r.get("target_id")) in ids
            ]
        pruned.append(cluster)
    return pruned


def load_seed_taxonomy(path: str, view: str = "final") -> List[Dict]:
    """Load a saved taxonomy JSON as the clusters of a starting taxonomy.

    Accepts either the format written by ``--output`` (a dict with an
    ``iterations`` list) or a bare list of cluster dicts. For the dict format,
    ``view`` picks the clusters (see ``resolve_seed_view``):

    - ``"final"``: the final iteration's clusters (all dimensions, including
      those that dimension selection dropped);
    - ``"selected"``: ``selected_clusters`` (the reported design space), with
      relations to dropped dimensions removed; falls back to the final
      iteration, with a warning, when the file has no selected view.

    Args:
        path: Path to the saved taxonomy JSON file.
        view: ``"final"`` or ``"selected"``.

    Returns:
        List[Dict]: The cluster list to seed the run with.

    Raises:
        ValueError: If the file is missing, has no iterations, or the resolved
            cluster list is empty or malformed.
    """
    try:
        with open(path) as f:
            data = json.load(f)
    except FileNotFoundError as e:
        raise ValueError(f"Taxonomy input file not found: {path}") from e
    except json.JSONDecodeError as e:
        raise ValueError(f"Taxonomy input file is not valid JSON: {path} ({e})") from e

    if isinstance(data, list):
        clusters = data
        source = "bare cluster list"
    elif isinstance(data, dict):
        iterations = data.get("iterations") or []
        if not iterations:
            raise ValueError(
                f"Taxonomy input file has no iterations: {path} "
                "(expected an 'iterations' list or a bare cluster list)"
            )
        if view == "selected" and data.get("selected_clusters"):
            clusters = _prune_relations(data["selected_clusters"])
            source = "selected view"
        else:
            if view == "selected":
                logger.warning(
                    "Taxonomy input %s has no selected view; using its final iteration instead", path
                )
            clusters = iterations[-1].get("clusters") or []
            source = f"iteration {len(iterations)} (final)"
    else:
        raise ValueError(
            f"Taxonomy input file is malformed: {path} "
            "(expected an object or a list at the top level)"
        )

    if not clusters or not all(isinstance(c, dict) for c in clusters):
        raise ValueError(
            f"Taxonomy input file has no usable clusters: {path} "
            f"(resolved from {source})"
        )

    logger.info("Loaded seed taxonomy from %s (%s): %d dimensions", path, source, len(clusters))
    return clusters


# ---------------------------------------------------------------------------
# Embedding math for value consolidation (see TAXONOMY_QUALITY_PLAN.md §6)
# ---------------------------------------------------------------------------

def l2_normalize(vectors: "np.ndarray") -> "np.ndarray":
    """L2-normalize rows of a vector matrix.

    For normalized vectors, Euclidean distance and cosine similarity are
    monotonically related (``euclidean² = 2(1 − cosine)``), so normalizing
    once keeps "distance" consistent between merging and visualization.
    """
    vectors = np.asarray(vectors, dtype=float)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vectors / norms


def pairwise_euclidean(vectors: "np.ndarray") -> "np.ndarray":
    """Return the full pairwise Euclidean distance matrix for row vectors."""
    vectors = np.asarray(vectors, dtype=float)
    if vectors.size == 0:
        return np.zeros((0, 0))
    # Efficient: ||a - b||² = ||a||² + ||b||² - 2·a·b
    sq = np.sum(vectors ** 2, axis=1)
    sq_dists = sq[:, None] + sq[None, :] - 2.0 * (vectors @ vectors.T)
    np.maximum(sq_dists, 0.0, out=sq_dists)
    return np.sqrt(sq_dists)


def connected_components(num_nodes: int, edges: List[Tuple[int, int]]) -> List[List[int]]:
    """Group node indices via union-find over the given edges.

    Deterministic connected-components resolution — no LLM cost.

    Args:
        num_nodes: Total number of nodes.
        edges: Pairs of node indices considered connected.

    Returns:
        List of components, each a sorted list of node indices.
    """
    parent = list(range(num_nodes))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for a, b in edges:
        union(a, b)

    groups: Dict[int, List[int]] = {}
    for node in range(num_nodes):
        groups.setdefault(find(node), []).append(node)

    return [sorted(members) for members in groups.values()]


def ensure_unique_ids(clusters: List[Dict]) -> Tuple[List[Dict], List[str]]:
    """Give every dimension a unique id and every value a unique ``<dim>.<n>`` id.

    The LLM assigns ids while rewriting the taxonomy, and can reuse one (two
    different dimensions both numbered ``37``). Downstream steps key on ids
    (consolidation looks values up by id, the labeler returns a dimension id,
    relations point at ids), so a collision silently mixes two dimensions.

    The first dimension keeps a duplicated id; later ones get the next free
    numeric id (or ``<id>-<k>`` for non-numeric ids). Values of a renamed
    dimension are re-prefixed, and duplicate value ids within a dimension are
    renumbered. Relations keep pointing at the first holder of an id.

    Returns:
        The fixed clusters (new dicts; the input is not mutated) and a list of
        human-readable change notes (empty when nothing changed).
    """
    dims = [c for c in clusters or [] if isinstance(c, dict)]
    numeric = [int(c["id"]) for c in dims if str(c.get("id", "")).isdigit()]
    next_id = max(numeric, default=0) + 1
    seen_dims: set = set()
    changes: List[str] = []
    fixed: List[Dict] = []
    for cluster in clusters or []:
        if not isinstance(cluster, dict):
            fixed.append(cluster)
            continue
        cluster = dict(cluster)
        old_id = str(cluster.get("id", "")).strip() or str(next_id)
        new_id = old_id
        if new_id in seen_dims:
            if old_id.isdigit():
                new_id = str(next_id)
                next_id += 1
            else:
                k = 2
                while f"{old_id}-{k}" in seen_dims:
                    k += 1
                new_id = f"{old_id}-{k}"
            changes.append(f"dimension '{cluster.get('name', '?')}' id {old_id} -> {new_id} (duplicate)")
        seen_dims.add(new_id)
        cluster["id"] = new_id

        values, seen_values = [], set()
        for value in cluster.get("values") or []:
            if not isinstance(value, dict):
                values.append(value)
                continue
            value = dict(value)
            vid = str(value.get("id", ""))
            suffix = vid.split(".", 1)[1] if "." in vid else ""
            candidate = f"{new_id}.{suffix}" if suffix else ""
            if not candidate or candidate in seen_values:
                n = 1
                while f"{new_id}.{n}" in seen_values:
                    n += 1
                candidate = f"{new_id}.{n}"
            if candidate != vid:
                changes.append(f"value '{value.get('label', '?')}' id {vid or '(none)'} -> {candidate}")
            seen_values.add(candidate)
            value["id"] = candidate
            value["dimension_id"] = new_id
            values.append(value)
        if "values" in cluster:
            cluster["values"] = values
        fixed.append(cluster)
    return fixed, changes


# Provenance fields the update/review prompts never show: evidence linking
# rebuilds them from the open codes after the loop, and re-emitting them made
# every full-taxonomy rewrite long enough that the model dropped values.
PROVENANCE_FIELDS = (
    "supporting_doc_ids", "stances", "evidence", "evidence_code_count",
    "merged_from", "unsupported_values",
)


def taxonomy_prompt_view(clusters: List[Dict]) -> List[Dict]:
    """The taxonomy without provenance fields, for prompts that rewrite it."""
    view = []
    for cluster in clusters or []:
        if not isinstance(cluster, dict):
            view.append(cluster)
            continue
        cluster = {k: v for k, v in cluster.items() if k not in PROVENANCE_FIELDS}
        if cluster.get("values"):
            cluster["values"] = [
                {k: v for k, v in value.items() if k not in PROVENANCE_FIELDS}
                if isinstance(value, dict) else value
                for value in cluster["values"]
            ]
        view.append(cluster)
    return view


def format_taxonomy_compact(clusters: List[Dict]) -> str:
    """Compact taxonomy view for tool-based updates: ids, names, statuses and relations only.

    One line per dimension (``[id] name — description (type → target; …)``) and one
    line with its values (``id label (status) · …``). Value descriptions and provenance
    are left out: the model refers to elements by id and never re-emits them.
    """
    lines = []
    for cluster in clusters or []:
        if not isinstance(cluster, dict):
            continue
        header = f"[{cluster.get('id', '')}] {cluster.get('name', '')} — {cluster.get('description', '')}"
        relations = [r for r in cluster.get("relations") or [] if isinstance(r, dict)]
        if relations:
            header += " (" + "; ".join(f"{r.get('type')} → {r.get('target_id')}" for r in relations) + ")"
        values = [v for v in cluster.get("values") or [] if isinstance(v, dict)]
        if not values:
            lines.append(header + " (no values yet)")
            continue
        lines.append(header)
        lines.append("    " + " · ".join(f"{v.get('id')} {v.get('label', '')} ({v.get('status', '')})"
                                         for v in values))
    return "\n".join(lines)


def _value_key(label: str) -> str:
    return " ".join("".join(ch if ch.isalnum() else " " for ch in (label or "").lower()).split())


def carry_over_evidence(previous: List[Dict], updated: List[Dict]) -> List[Dict]:
    """Restore the supporting documents of values the model kept.

    The model sees existing values without their document ids, so it only
    cites documents of the new batch. A kept value is recognized by its label
    (normalized), or else by its id within a dimension of the same name; its
    previous ids are unioned back in. Mutates and returns ``updated``.
    """
    by_label: Dict[str, set] = {}
    by_id: Dict[Tuple[str, str], set] = {}
    for cluster in previous or []:
        if not isinstance(cluster, dict):
            continue
        for value in cluster.get("values") or []:
            if not isinstance(value, dict):
                continue
            ids = set(value.get("supporting_doc_ids") or [])
            by_label.setdefault(_value_key(value.get("label", "")), set()).update(ids)
            by_id.setdefault((cluster.get("name", ""), str(value.get("id"))), set()).update(ids)
    for cluster in updated or []:
        if not isinstance(cluster, dict):
            continue
        for value in cluster.get("values") or []:
            if not isinstance(value, dict):
                continue
            kept = by_label.get(_value_key(value.get("label", "")))
            if kept is None:
                kept = by_id.get((cluster.get("name", ""), str(value.get("id"))), set())
            value["supporting_doc_ids"] = sorted(set(value.get("supporting_doc_ids") or []) | kept)
    return updated


def taxonomy_prompt_inputs(state: State, configuration: Configuration, mb_indices: List[int],
                           use_open_codes: bool, taxonomy_json: str) -> Dict[str, object]:
    """Prompt variables of the update/review prompts (rewrite and tools modes share them).

    The batch is rendered as open codes when the state has them (axial coding
    input), else as summaries; ``taxonomy_json`` is the taxonomy as the mode shows it.
    """
    minibatch = [state.documents[idx] for idx in mb_indices]
    if use_open_codes and state.open_codes:
        data_json = format_open_codes_for_docs(minibatch, state.open_codes)
    else:
        data_json = format_docs(minibatch)
    # When max_num_clusters is None, let the LLM determine the count from data
    max_clusters_value = configuration.max_num_clusters
    max_clusters_str = (
        str(max_clusters_value) if max_clusters_value is not None
        else "unlimited — determine the number of dimensions based on what the data naturally supports. Prefer fewer, high-quality dimensions (typically 3–8) over many narrow ones. Only add a dimension when it captures a genuinely orthogonal axis of variation that cannot be merged into an existing one."
    )
    return {
        "data_json": data_json,
        "use_case": configuration.use_case,
        "taxonomy_json": taxonomy_json,
        "suggestion_length": configuration.suggestion_length,
        "cluster_name_length": configuration.cluster_name_length,
        "cluster_description_length": configuration.cluster_description_length,
        "explanation_length": configuration.explanation_length,
        "max_num_clusters": max_clusters_str,
    }


def restore_dropped_values(previous: List[Dict], updated: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """Put back the evidence-backed values a rewrite dropped (``edit_mode: rewrite_restore``).

    A previous value with supporting documents counts as kept when any updated value
    has the same normalized label (as ``carry_over_evidence`` recognizes kept values).
    A dropped one goes back into the updated dimension with the same name (normalized),
    else into its previous dimension, recreated without its other values. Returns the
    taxonomy (new dicts, unique ids) and one record per restored value.
    """
    kept = {_value_key(v.get("label", "")) for c in updated or [] if isinstance(c, dict)
            for v in c.get("values") or [] if isinstance(v, dict)}
    clusters = [copy.deepcopy(c) for c in updated or []]
    by_name = {_value_key(c.get("name", "")): c for c in clusters if isinstance(c, dict)}
    restored: List[Dict] = []
    for dim in previous or []:
        if not isinstance(dim, dict):
            continue
        for value in dim.get("values") or []:
            if not isinstance(value, dict) or not value.get("supporting_doc_ids"):
                continue
            if _value_key(value.get("label", "")) in kept:
                continue
            target = by_name.get(_value_key(dim.get("name", "")))
            if target is None:
                target = {k: copy.deepcopy(v) for k, v in dim.items() if k != "values"}
                target["values"] = []
                numeric = [int(c["id"]) for c in clusters if str(c.get("id", "")).isdigit()]
                target["id"] = str(max(numeric, default=0) + 1)
                clusters.append(target)
                by_name[_value_key(dim.get("name", ""))] = target
            target.setdefault("values", []).append(copy.deepcopy(value))
            kept.add(_value_key(value.get("label", "")))
            restored.append({"id_before": value.get("id"), "label": value.get("label", ""),
                             "dimension": target.get("name", "")})
    if not restored:
        return clusters, []
    fixed, _changes = ensure_unique_ids(clusters)
    return fixed, restored


async def invoke_taxonomy_chain(
    chain: Runnable,
    state: State,
    config: RunnableConfig,
    mb_indices: List[int],
    use_open_codes: bool = True,
) -> Dict[str, List[List[Dict[str, str]]]]:
    """Invoke the taxonomy generation chain.

    When ``use_open_codes`` is true and the state carries accumulated open
    codes, the minibatch's data is rendered as open codes (grounded theory's
    axial coding input) instead of raw summaries. Otherwise document
    summaries are used as before.
    """
    try:
        configuration = Configuration.from_runnable_config(config)
        previous_taxonomy = state.clusters[-1] if state.clusters else []
        inputs = taxonomy_prompt_inputs(state, configuration, mb_indices, use_open_codes,
                                        format_taxonomy(taxonomy_prompt_view(previous_taxonomy)))
        logger.debug("Invoking taxonomy chain with %d documents in minibatch", len(mb_indices))
        result: TaxonomyOutput = await chain.ainvoke(inputs)

        # Convert Pydantic model to dict list for state
        clusters_list, id_changes = ensure_unique_ids([c.model_dump() for c in result.clusters])
        clusters_list = carry_over_evidence(previous_taxonomy, clusters_list)
        if id_changes:
            logger.warning("Fixed %d duplicate taxonomy ids: %s", len(id_changes), "; ".join(id_changes))
        num_clusters = len(clusters_list)
        logger.debug("Taxonomy chain returned %d clusters", num_clusters)
        return {
            "clusters": [clusters_list],
            "explanations": [result.explanation],
            "status": ["Taxonomy generated."],
        }
    except Exception as e:
        logger.error("Taxonomy generation error: %s", e)
        raise