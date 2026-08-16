"""Node for open coding a minibatch (grounded theory, stage 1).

Extracts fine-grained per-document concept/decision labels before any
grouping. These open codes are the raw material the axial-coding steps
(``generate_taxonomy`` / ``update_taxonomy``) organize into dimensions,
values, and relations.
"""

import asyncio
import logging
from typing import List

from langchain_core.runnables import RunnableConfig

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.prompts import OPEN_CODING_PROMPT
from taxonomy_generator.schemas import OpenCodesOutput
from taxonomy_generator.state import State
from taxonomy_generator.utils import load_chat_model

logger = logging.getLogger(__name__)


def _setup_open_coding_chain(configuration: Configuration):
    """Set up the chain for per-document open coding."""
    model = load_chat_model(configuration.fast_llm)
    structured_model = model.with_structured_output(OpenCodesOutput)
    prompt = OPEN_CODING_PROMPT.partial(use_case=configuration.use_case)
    return (prompt | structured_model).with_config(run_name="OpenCodeDocs")


async def _code_single_doc(chain, doc_id: str, content: str, semaphore: asyncio.Semaphore) -> OpenCodesOutput:
    """Open-code a single document with concurrency control."""
    async with semaphore:
        return await chain.ainvoke({"doc_id": doc_id, "content": content})


def _doc_input(doc) -> str:
    """Prefer the summary (when present) over raw content, as axial coding does."""
    if isinstance(doc, dict):
        return doc.get("summary") or doc.get("content", "")
    return doc.summary or doc.content or ""


async def open_code_minibatch(
    state: State,
    config: RunnableConfig,
) -> dict:
    """Open-code the next minibatch of documents.

    Codes the batch at ``state.open_code_batch_index`` and advances that
    index so the following axial-coding node consumes the same batch.
    """
    configuration = Configuration.from_runnable_config(config)

    batch_idx = state.open_code_batch_index
    mb_indices = state.minibatches[batch_idx]
    minibatch = [state.documents[idx] for idx in mb_indices]

    logger.info(
        "Open coding minibatch %d/%d (%d documents, model: %s)",
        batch_idx + 1, len(state.minibatches), len(minibatch), configuration.fast_llm,
    )

    chain = _setup_open_coding_chain(configuration)
    semaphore = asyncio.Semaphore(configuration.summary_max_concurrency)

    tasks = [
        _code_single_doc(
            chain,
            doc["id"] if isinstance(doc, dict) else doc.id,
            _doc_input(doc),
            semaphore,
        )
        for doc in minibatch
    ]
    results: List[OpenCodesOutput] = await asyncio.gather(*tasks)

    new_codes: List[dict] = []
    for result in results:
        for code in result.codes:
            new_codes.append(code.model_dump())

    logger.info("Open coding complete — %d codes extracted from %d documents", len(new_codes), len(minibatch))

    return {
        "open_codes": new_codes,
        "open_code_batch_index": batch_idx + 1,
        "status": [f"Open coded {len(new_codes)} concepts from minibatch {batch_idx + 1}."],
    }