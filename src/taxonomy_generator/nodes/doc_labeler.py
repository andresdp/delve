"""Node for labeling documents using the generated taxonomy."""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Tuple

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.prompts import LABELER_PROMPT
from taxonomy_generator.schemas import LabelOutput
from taxonomy_generator.state import Doc, State
from taxonomy_generator.utils import format_taxonomy, load_chat_model

logger = logging.getLogger(__name__)


def _get_field(doc, field: str, default=""):
    """Safely get a field from a Doc object or dict."""
    if isinstance(doc, dict):
        return doc.get(field, default)
    return getattr(doc, field, default)


def _format_results(docs: List[Doc]) -> str:
    """Format labeled documents in a readable way.

    Args:
        docs: List of labeled documents (Doc objects or dicts)

    Returns:
        str: Formatted string showing document previews and their labels
    """
    result = "Document Classification Results:\n\n"
    for doc in docs:
        content = _get_field(doc, "content", "")
        category = _get_field(doc, "category", "N/A")
        value = _get_field(doc, "value", None)
        score = _get_field(doc, "score", None)
        preview = content[:400].replace('\n', ' ').strip()
        if len(content) > 200:
            preview += "..."

        score_str = f" ({score:.2f})" if score is not None else ""
        result += f"🔖 Category: {category}{score_str}\n"
        if value:
            result += f"   Value: {value}\n"
        result += f"📄 Document: {preview}\n"
        result += "─" * 80 + "\n\n"

    return result


def _setup_classification_chain(configuration: Configuration):
    """Set up the chain for document labeling."""
    model = load_chat_model(configuration.generation_llm)
    structured_model = model.with_structured_output(LabelOutput)
    labeler_prompt = LABELER_PROMPT.partial(
        fallback_category=configuration.fallback_category,
        use_case=configuration.use_case,
    )

    return (
        labeler_prompt
        | structured_model
    ).with_config(run_name="LabelDocs")


def _normalize_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (name or "").lower()).strip()


_NULL_STRINGS = {"", "null", "none", "n/a", "na", "nil"}


def _optional(text: Optional[str]) -> Optional[str]:
    """Treat placeholder strings the model sometimes writes ("null", "none", "") as absent."""
    if text is None:
        return None
    stripped = str(text).strip()
    return None if stripped.lower() in _NULL_STRINGS else stripped


def _resolve_category(
    clusters: List[Dict], label_result: LabelOutput, fallback_category: str
) -> Tuple[Optional[Dict], bool]:
    """Map a labeler answer to a dimension of the taxonomy.

    Resolution order: ``category_id``, then the exact name, then the name
    ignoring case and punctuation. Returns ``(cluster, is_fallback)``;
    ``(None, False)`` means the answer names no dimension (invalid).
    """
    dims = [c for c in clusters if isinstance(c, dict)]
    wanted = _optional(label_result.category_id)
    if wanted is not None:
        for cluster in dims:
            if str(cluster.get("id", "")).strip() == wanted:
                return cluster, False
    for cluster in dims:
        if cluster.get("name") == label_result.category:
            return cluster, False
    normalized = _normalize_name(label_result.category)
    for cluster in dims:
        if _normalize_name(cluster.get("name", "")) == normalized:
            return cluster, False
    if normalized == _normalize_name(fallback_category):
        return None, True
    return None, False


async def _label_single_doc(
    labeling_chain,
    doc_content: str,
    taxonomy_json: str,
    semaphore: asyncio.Semaphore,
    clusters: List[Dict],
    fallback_category: str,
) -> Tuple[LabelOutput, Optional[Dict]]:
    """Label one document; retry once when the answer names no dimension of the taxonomy.

    Returns the label result and the resolved dimension (``None`` for the
    fallback category). An answer that is still invalid after the retry is
    recorded as the fallback category, with the reason kept in ``reasoning``.
    """
    async with semaphore:
        result: Optional[LabelOutput] = None
        for attempt in range(2):
            result = await labeling_chain.ainvoke({
                "content": doc_content,
                "taxonomy_json": taxonomy_json,
            })
            cluster, is_fallback = _resolve_category(clusters, result, fallback_category)
            if cluster is not None or is_fallback:
                return result, cluster
            logger.warning(
                "Labeler named no dimension of the taxonomy (category_id=%r, category=%r)%s",
                result.category_id, result.category, " — retrying" if attempt == 0 else "",
            )
    invalid = result.model_copy(update={
        "category": fallback_category, "category_id": None, "value_id": None,
        "proposed_value_label": None, "score": 0.0,
        "reasoning": (f"Labeler answered {result.category!r} (id {result.category_id!r}), which is not a "
                      f"dimension of the taxonomy, twice; recorded as {fallback_category}. "
                      f"Original reasoning: {result.reasoning}"),
    })
    return invalid, None


def _resolve_value_label(cluster: Optional[Dict], label_result: LabelOutput) -> Optional[str]:
    """Resolve the value text for a labeled document.

    Prefers the chosen existing value's label (looked up by ``value_id`` in the
    resolved dimension). Falls back to the proposed label when the model flagged
    that no existing value fits. Returns None for fallback-category documents
    and value-less matches.
    """
    if cluster is None:
        return None
    value_id = _optional(label_result.value_id)
    if value_id:
        for value in cluster.get("values") or []:
            if isinstance(value, dict) and str(value.get("id")) == value_id:
                return value.get("label")
        # Unknown value_id — fall through to the proposal if present.
        logger.warning(
            "Labeler returned unknown value_id %r for category %r",
            value_id, cluster.get("name"),
        )
    return _optional(label_result.proposed_value_label)


def _labeling_taxonomy(state: State) -> Optional[List[Dict]]:
    """The taxonomy documents are labeled against.

    The use-case-selected view when dimension selection ran (so labels match
    the dimensions shown in reports), else the latest complete taxonomy
    (e.g. test mode, which labels against the frozen seed).
    """
    selected = getattr(state, "selected_clusters", None) or []
    if selected and isinstance(selected[-1], list) and selected[-1]:
        return selected[-1]
    for clusters in reversed(state.clusters):
        if isinstance(clusters, list) and clusters:
            return clusters
    if state.clusters:
        return [state.clusters[-1]] if isinstance(state.clusters[-1], dict) else state.clusters[-1]
    return None


async def label_documents(
    state: State,
    config: RunnableConfig,
) -> dict:
    """Label documents using the generated taxonomy."""
    configuration = Configuration.from_runnable_config(config)
    labeling_chain = _setup_classification_chain(configuration)

    max_concurrency = configuration.summary_max_concurrency
    semaphore = asyncio.Semaphore(max_concurrency)

    latest_clusters = _labeling_taxonomy(state)

    if not latest_clusters:
        logger.error("No valid clusters found in state for document labeling")
        raise ValueError("No valid clusters found in state")

    taxonomy_json = format_taxonomy(latest_clusters)

    logger.info(
        "Labeling %d documents using taxonomy with %d categories (concurrency: %d, model: %s)",
        len(state.documents), len(latest_clusters), max_concurrency, configuration.generation_llm,
    )

    # Process all documents in parallel with concurrency control
    tasks = [
        _label_single_doc(
            labeling_chain,
            doc["content"] if isinstance(doc, dict) else doc.content,
            taxonomy_json,
            semaphore,
            latest_clusters,
            configuration.fallback_category,
        )
        for doc in state.documents
    ]
    labeled: List[Tuple[LabelOutput, Optional[Dict]]] = await asyncio.gather(*tasks)

    # Update documents with labels, scores, reasoning, and values
    updated_docs = [
        Doc(
            id=doc["id"] if isinstance(doc, dict) else doc.id,
            content=doc["content"] if isinstance(doc, dict) else doc.content,
            summary=doc.get("summary", "") if isinstance(doc, dict) else (doc.summary or ""),
            explanation=label_result.reasoning,
            # The taxonomy's own name for the resolved dimension, never a paraphrase.
            category=cluster.get("name") if cluster is not None else configuration.fallback_category,
            value=_resolve_value_label(cluster, label_result),
            score=label_result.score,
        )
        for doc, (label_result, cluster) in zip(state.documents, labeled)
    ]

    results_display = _format_results(updated_docs)
    message = AIMessage(content=f"✅ Documents have been labeled!\n\n{results_display}")

    logger.info("Successfully labeled %d documents", len(updated_docs))

    return {
        "documents": updated_docs,
        "messages": [message],
        "status": ["Documents labeled successfully"],
    }