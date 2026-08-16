"""Shared helpers: model loading, prompt formatting, and merge math."""
import json
import logging
from typing import Dict, List, Tuple

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
        open_codes: Accumulated open-code dicts (with ``doc_id``/``label``/``rationale``).

    Returns:
        str: JSON formatted open codes, one entry per document.
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
        }
        codes_by_doc.setdefault(doc_id, []).append({
            "label": entry.get("label", ""),
            "rationale": entry.get("rationale", ""),
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
            items.append({"id": doc_id, "codes": [{"label": summary, "rationale": "No open codes extracted; summary used."}]})
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


def format_feedback(state: State) -> str:
    """Format user feedback from state into a string for taxonomy prompts.

    Returns ``"None."`` when no feedback is present so the LLM receives
    a clear signal to proceed with standard clustering.

    Args:
        state: Current pipeline state.

    Returns:
        Formatted feedback string.
    """
    if not state.user_feedback:
        return "None."
    parts = [f"Previous user feedback: {state.user_feedback.feedback}"]
    if state.user_feedback.explanation:
        parts.append(f"Reason for modification: {state.user_feedback.explanation}")
    return "\n".join(parts)


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
        minibatch = [state.documents[idx] for idx in mb_indices]

        if use_open_codes and state.open_codes:
            data_json = format_open_codes_for_docs(minibatch, state.open_codes)
        else:
            data_json = format_docs(minibatch)

        previous_taxonomy = state.clusters[-1] if state.clusters else []
        taxonomy_json = format_taxonomy(previous_taxonomy)

        logger.debug("Invoking taxonomy chain with %d documents in minibatch", len(minibatch))
        # When max_num_clusters is None, let the LLM determine the count from data
        max_clusters_value = configuration.max_num_clusters
        max_clusters_str = (
            str(max_clusters_value) if max_clusters_value is not None
            else "unlimited — determine the number of dimensions based on what the data naturally supports. Prefer fewer, high-quality dimensions (typically 3–8) over many narrow ones. Only add a dimension when it captures a genuinely orthogonal axis of variation that cannot be merged into an existing one."
        )

        result: TaxonomyOutput = await chain.ainvoke(
            {
                "data_json": data_json,
                "use_case": configuration.use_case,
                "taxonomy_json": taxonomy_json,
                "suggestion_length": configuration.suggestion_length,
                "cluster_name_length": configuration.cluster_name_length,
                "cluster_description_length": configuration.cluster_description_length,
                "explanation_length": configuration.explanation_length,
                "max_num_clusters": max_clusters_str,
            }
        )

        # Convert Pydantic model to dict list for state
        clusters_list = [c.model_dump() for c in result.clusters]
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