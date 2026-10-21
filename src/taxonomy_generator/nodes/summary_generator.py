"""Node for generating summaries of documents."""

import logging
from typing import Any, Dict, List
from uuid import uuid4

from langchain_core.runnables import RunnableConfig, RunnableLambda, RunnablePassthrough

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.prompts import SUMMARY_GENERATION_PROMPT
from taxonomy_generator.schemas import SummaryOutput
from taxonomy_generator.state import State
from taxonomy_generator.utils import load_chat_model

logger = logging.getLogger(__name__)


def _get_content(state: Dict[str, List]) -> List[Dict[str, str]]:
    """Extract content from documents for summarization.
    
    Args:
        state: State dictionary containing documents
        
    Returns:
        List of document contents formatted for summarization
    """
    docs = state["documents"]
    return [
        {
            "content": (
                doc["content"] if isinstance(doc, dict) 
                else doc.content
            )
        }
        for doc in docs
    ]


def _as_documents(documents: List[Any]) -> List[Dict[str, Any]]:
    """Return the documents as dicts with ``id`` and ``content``, keeping the ids they have.

    ``Doc`` objects (what the corpus loader produces) keep their id, e.g. a passage id
    ``s03_p02``, so open codes and values stay traceable to their source.
    """
    out = []
    for doc in documents:
        if isinstance(doc, str):
            out.append({"id": str(uuid4()), "content": doc})
        elif isinstance(doc, dict):
            out.append({**doc, "id": doc.get("id") or str(uuid4())})
        elif hasattr(doc, "content"):
            out.append({"id": getattr(doc, "id", None) or str(uuid4()), "content": doc.content})
        else:
            out.append({"id": str(uuid4()), "content": str(doc)})
    return out


def _reduce_summaries(combined: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """Combine documents with their summaries.
    
    Args:
        combined: Dictionary containing documents and their summaries
        
    Returns:
        dict: Documents enriched with summaries and explanations
    """
    summaries = combined["summaries"]
    documents = combined["documents"]
    return {
        "documents": [
            {
                "id": doc.get("id", str(uuid4())),
                "content": doc.get("content", ""),
                "summary": summ_info.summary,
                "explanation": summ_info.explanation,
            }
            for doc, summ_info in zip(documents, summaries)
        ],
        "status": ["Summarized successfully."],
    }


async def generate_summaries(
    state: State,
    config: RunnableConfig,
) -> dict:
    """Generate summaries for a collection of documents."""
    configuration = Configuration.from_runnable_config(config)
    logger.info("Generating summaries for %d documents using model: %s", len(state.documents), configuration.generation_llm)

    # Initialize the model and prompt
    model = load_chat_model(configuration.generation_llm)
    summary_prompt = SUMMARY_GENERATION_PROMPT.partial(
        use_case=configuration.use_case,
        summary_length=configuration.summary_length,
        explanation_length=configuration.summary_explanation_length,
    )

    # Create the summary chain with structured output
    structured_model = model.with_structured_output(SummaryOutput)
    summary_chain = (
        summary_prompt 
        | structured_model
    ).with_config(run_name="GenerateSummary")

    # Create the full chain with map-reduce, bounded concurrency
    max_conc = configuration.summary_max_concurrency

    async def _abatch_with_concurrency(inputs):
        return await summary_chain.abatch(
            inputs, config={"max_concurrency": max_conc}
        )

    map_reduce_chain = (
        RunnablePassthrough.assign(
            summaries=_get_content
            | RunnableLambda(
                func=summary_chain.batch,
                afunc=_abatch_with_concurrency,
            )
        )
        | _reduce_summaries
    )

    processed_docs = _as_documents(state.documents)
    logger.info("Processing %d documents through summary chain", len(processed_docs))
    result = await map_reduce_chain.ainvoke({"documents": processed_docs})
    logger.info("Summaries generated successfully for %d documents", len(result.get("documents", [])))
    return result
