"""Node for labeling documents using the generated taxonomy."""

import asyncio
import logging
from typing import List
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage

from taxonomy_generator.state import State, Doc
from taxonomy_generator.utils import load_chat_model, format_taxonomy
from taxonomy_generator.configuration import Configuration
from taxonomy_generator.schemas import LabelOutput
from taxonomy_generator.prompts import LABELER_PROMPT

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
        score = _get_field(doc, "score", None)
        preview = content[:400].replace('\n', ' ').strip()
        if len(content) > 200:
            preview += "..."

        score_str = f" ({score:.2f})" if score is not None else ""
        result += f"🔖 Category: {category}{score_str}\n"
        result += f"📄 Document: {preview}\n"
        result += "─" * 80 + "\n\n"

    return result


def _setup_classification_chain(configuration: Configuration):
    """Set up the chain for document labeling."""
    model = load_chat_model(configuration.fast_llm)
    structured_model = model.with_structured_output(LabelOutput)
    labeler_prompt = LABELER_PROMPT.partial(
        fallback_category=configuration.fallback_category,
        use_case=configuration.use_case,
    )

    return (
        labeler_prompt
        | structured_model
    ).with_config(run_name="LabelDocs")


async def _label_single_doc(labeling_chain, doc_content: str, taxonomy_json: str, semaphore: asyncio.Semaphore) -> LabelOutput:
    """Label a single document with concurrency control."""
    async with semaphore:
        return await labeling_chain.ainvoke({
            "content": doc_content,
            "taxonomy_json": taxonomy_json,
        })


async def label_documents(
    state: State,
    config: RunnableConfig,
) -> dict:
    """Label documents using the generated taxonomy."""

    configuration = Configuration.from_runnable_config(config)
    labeling_chain = _setup_classification_chain(configuration)

    max_concurrency = configuration.summary_max_concurrency
    semaphore = asyncio.Semaphore(max_concurrency)

    # Get latest complete set of clusters
    latest_clusters = None
    for clusters in reversed(state.clusters):
        if isinstance(clusters, list) and clusters:
            latest_clusters = clusters
            break

    if not latest_clusters and state.clusters:
        latest_clusters = [state.clusters[-1]] if isinstance(state.clusters[-1], dict) else state.clusters[-1]

    if not latest_clusters:
        logger.error("No valid clusters found in state for document labeling")
        raise ValueError("No valid clusters found in state")

    taxonomy_json = format_taxonomy(latest_clusters)

    logger.info(
        "Labeling %d documents using taxonomy with %d categories (concurrency: %d, model: %s)",
        len(state.documents), len(latest_clusters), max_concurrency, configuration.fast_llm,
    )

    # Process all documents in parallel with concurrency control
    tasks = [
        _label_single_doc(
            labeling_chain,
            doc["content"] if isinstance(doc, dict) else doc.content,
            taxonomy_json,
            semaphore,
        )
        for doc in state.documents
    ]
    labeled_results: List[LabelOutput] = await asyncio.gather(*tasks)

    # Update documents with labels, scores, and reasoning
    updated_docs = [
        Doc(
            id=doc["id"] if isinstance(doc, dict) else doc.id,
            content=doc["content"] if isinstance(doc, dict) else doc.content,
            summary=doc.get("summary", "") if isinstance(doc, dict) else (doc.summary or ""),
            explanation=label_result.reasoning,
            category=label_result.category,
            score=label_result.score,
        )
        for doc, label_result in zip(state.documents, labeled_results)
    ]

    results_display = _format_results(updated_docs)
    message = AIMessage(content=f"✅ Documents have been labeled!\n\n{results_display}")

    logger.info("Successfully labeled %d documents", len(updated_docs))

    return {
        "documents": updated_docs,
        "messages": [message],
        "status": ["Documents labeled successfully"],
    }