"""LLM-written texts shown in the wiki, labeled as generated: source summaries and design-point descriptions.

Shared by ``ddspace wiki build`` and the benchmark scripts (``summarize_sources.py``,
``describe_design_points.py``). Each call is one LLM request; callers store the results and reuse them.
"""

from __future__ import annotations

from typing import Any, Mapping

SUMMARY_PROMPT_VERSION = "1"
SUMMARY_MAX_WORDS = 12000
DESCRIPTION_PROMPT_VERSION = "2"   # 2: every description names its trade-off

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


DESCRIPTION_PROMPT = """{origin} Each dimension is one design decision; each value is an alternative answer. Below
is one combination of values, one per dimension.

{choices}

Write at most 90 words, in two parts:
1. In 2 sentences, the solution, or solution fragment, that this combination implies: how the chosen values would
   work together in one system.
2. One or two sentences starting with "Trade-off:": what this combination gains and what it gives up (the costs,
   risks or qualities it weakens), specific to these values rather than true of any design.
Only if two of the choices genuinely conflict (one undermines what the other is for), add one sentence saying
which and why. Combinations that are commonly used together are not in tension; most combinations have no
conflict, and then you say nothing about one. Be concrete and neutral; do not invent details beyond the values
given.

Description:"""
MINED_ORIGIN = 'A design space for "{domain}" was mined from engineering documents.'
NAMED_ORIGIN = ('The dimensions and values below were named by a designer working on "{domain}", without a design '
                'space.')
TRADEOFF_MARK = "Trade-off:"


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
        value = f"\n  Value: {s.get('label')}" + (f": {s['description']}" if s.get("description") else "")
        value += f" [status: {s['status']}]" if s.get("status") else ""
        lines.append(f"- Dimension: {s.get('dimension')}" + (f" ({question})" if question else "") + value)
    return "\n".join(lines)


async def describe(model, point: Mapping[str, Any], dims: Mapping[str, Any], domain: str, *,
                   named: bool = False) -> str:
    """Return a short description of the solution a design point implies, ending with its trade-off.

    ``named`` is for values a designer named without a design space (zero-shot): they have no descriptions.
    """
    origin = (NAMED_ORIGIN if named else MINED_ORIGIN).format(domain=domain or "a software system")
    reply = await model.ainvoke(DESCRIPTION_PROMPT.format(origin=origin, choices=choices_text(point, dims)))
    return _text(reply)
