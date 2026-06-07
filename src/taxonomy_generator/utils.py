import json
import logging
from typing import List, Optional, Dict, Union
from langchain_core.runnables import Runnable, RunnableConfig

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from taxonomy_generator.state import Doc, State
from taxonomy_generator.configuration import Configuration
from taxonomy_generator.schemas import TaxonomyOutput

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


def format_taxonomy(clusters: List[Dict[str, str]]) -> str:
    """Format taxonomy clusters as JSON.

    Args:
        clusters: List of cluster dictionaries

    Returns:
        str: JSON formatted taxonomy
    """
    items = []
    for cluster in clusters:
        if isinstance(cluster, dict):
            items.append({
                "id": cluster.get("id", ""),
                "name": cluster.get("name", ""),
                "description": cluster.get("description", ""),
            })
        else:
            items.append({
                "id": getattr(cluster, "id", ""),
                "name": getattr(cluster, "name", ""),
                "description": getattr(cluster, "description", ""),
            })
    return json.dumps(items, indent=2)


async def invoke_taxonomy_chain(
    chain: Runnable,
    state: State,
    config: RunnableConfig,
    mb_indices: List[int],
) -> Dict[str, List[List[Dict[str, str]]]]:
    """Invoke the taxonomy generation chain."""
    try:
        configuration = Configuration.from_runnable_config(config)
        minibatch = [state.documents[idx] for idx in mb_indices]
        data_json = format_docs(minibatch)

        previous_taxonomy = state.clusters[-1] if state.clusters else []
        taxonomy_json = format_taxonomy(previous_taxonomy)

        # Format feedback if it exists
        feedback = "No previous feedback provided."
        if state.user_feedback:
            feedback = f"Previous user feedback: {state.user_feedback.feedback}"
            if state.user_feedback.explanation:
                feedback += f"\nReason for modification: {state.user_feedback.explanation}"

        logger.debug("Invoking taxonomy chain with %d documents in minibatch", len(minibatch))
        result: TaxonomyOutput = await chain.ainvoke(
            {
                "data_json": data_json,
                "use_case": configuration.use_case,
                "taxonomy_json": taxonomy_json,
                "feedback": feedback,
                "suggestion_length": configuration.suggestion_length,
                "cluster_name_length": configuration.cluster_name_length,
                "cluster_description_length": configuration.cluster_description_length,
                "explanation_length": configuration.explanation_length,
                "max_num_clusters": configuration.max_num_clusters,
            }
        )

        # Convert Pydantic model to dict list for state
        clusters_list = [c.model_dump() for c in result.clusters]
        num_clusters = len(clusters_list)
        logger.debug("Taxonomy chain returned %d clusters", num_clusters)
        return {
            "clusters": [clusters_list],
            "status": ["Taxonomy generated.."],
        }
    except Exception as e:
        logger.error("Taxonomy generation error: %s", e)
        raise
