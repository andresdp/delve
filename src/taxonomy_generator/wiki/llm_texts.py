"""LLM-written texts shown in the wiki, labeled as generated: source summaries and design-point descriptions.

Shared by ``ddspace wiki build`` and the benchmark scripts (``summarize_sources.py``,
``describe_design_points.py``). Each call is one LLM request; callers store the results and reuse them.
"""

from __future__ import annotations

from typing import Any, Mapping

SUMMARY_PROMPT_VERSION = "1"
SUMMARY_MAX_WORDS = 12000
DESCRIPTION_PROMPT_VERSION = "1"

SUMMARY_PROMPT = """Summarize the source below for a reader browsing a wiki of software-architecture design decisions.

Write 2-3 sentences, at most 60 words, in your own words (no quotations):
- what kind of document it is and which organization, system or project it concerns;
- which design problems or decisions it discusses.
Be neutral and factual; no marketing language, no evaluation of quality.

Title: {title}

Source text:
\"\"\"
{text}
\"\"\"

Summary:"""


DESCRIPTION_PROMPT = """A design space for "{domain}" was mined from engineering documents. Each dimension is one design
decision; each value is an alternative answer. Below is one combination of values, one per dimension.

{choices}

In 2-3 sentences (at most 70 words), describe the solution, or solution fragment, that this combination implies:
how the chosen values would work together in one system. If two choices are in evident tension or do not fit
together, say so briefly. Be concrete and neutral; do not invent details beyond the values given.

Description:"""


def _text(reply: Any) -> str:
    content = reply.content if isinstance(reply.content, str) else " ".join(
        part.get("text", "") for part in reply.content if isinstance(part, dict))
    return " ".join(content.split())


async def summarize(model, title: str, text: str) -> tuple[str, int]:
    """Return a 2-3 sentence summary of a source and the number of words the model read."""
    words = text.split()
    clipped = " ".join(words[:SUMMARY_MAX_WORDS])
    reply = await model.ainvoke(SUMMARY_PROMPT.format(title=title, text=clipped))
    return _text(reply), min(len(words), SUMMARY_MAX_WORDS)


def choices_text(point: Mapping[str, Any], dims: Mapping[str, Any]) -> str:
    """Return the prompt lines for a point's chosen values, one per dimension."""
    lines = []
    for s in point.get("values") or []:
        d = dims.get(str(s.get("dimension_id"))) or {}
        question = d.get("description") or ""
        lines.append(f"- Dimension: {s.get('dimension')}" + (f" ({question})" if question else "")
                     + f"\n  Value: {s.get('label')}: {s.get('description')} [status: {s.get('status')}]")
    return "\n".join(lines)


async def describe(model, point: Mapping[str, Any], dims: Mapping[str, Any], domain: str) -> str:
    """Return a 2-3 sentence description of the solution a design point implies."""
    reply = await model.ainvoke(DESCRIPTION_PROMPT.format(domain=domain or "a software system",
                                                          choices=choices_text(point, dims)))
    return _text(reply)
