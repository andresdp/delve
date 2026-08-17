"""Render a saved taxonomy view as a self-contained grounded-theory report.

Pure functions over a taxonomy view (a list of clusters/dimensions) that
produce the three sections of the markdown report: a mermaid relationship
diagram, a per-dimension catalog, and an LLM-polished narrative summary.
None of these functions know how the view was selected (an iteration's
``clusters`` vs. ``selected_clusters``) or where the assembled document is
written — that is the caller's responsibility.

The diagram and catalog (:func:`render_diagram`, :func:`render_catalog`) are
rendered verbatim from the taxonomy JSON: no LLM involvement. Only the
narrative summary (:func:`generate_narrative_summary`) goes through a model,
and only to reword/synthesize text that already exists in the taxonomy's
stored ``explanation`` and dimension descriptions.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.prompts import NARRATIVE_SUMMARY_PROMPT
from taxonomy_generator.schemas import NarrativeSummaryOutput
from taxonomy_generator.utils import load_chat_model

logger = logging.getLogger(__name__)

Cluster = Dict[str, Any]


def _cluster_id(cluster: Cluster) -> str:
    """Return a cluster's id as a string, defaulting to '?' when absent or null."""
    return str(cluster.get("id") or "?")


def _relation_target_id(relation: Dict[str, Any]) -> str:
    """Return a relation's target_id as a string, defaulting to '' when absent or null."""
    return str(relation.get("target_id") or "")


def _mermaid_node_id(cluster_id: str) -> str:
    """Build a mermaid-safe node id from a dimension id.

    Dimension ids are free-form strings from the taxonomy JSON (typically
    small integers like "1"), which are not always valid standalone mermaid
    node identifiers. Prefixing with a stable letter keeps them safe.
    """
    return f"dim_{cluster_id}"


def _escape_mermaid_label(text: str) -> str:
    """Escape characters that would break a quoted mermaid node/edge label.

    Quoted mermaid labels must stay on one physical line — an embedded
    newline splits the label mid-statement and corrupts the fenced block,
    so newlines are collapsed to spaces alongside the existing quote escape.
    """
    return text.replace('"', "'").replace("\r\n", " ").replace("\n", " ").replace("\r", " ")


def render_diagram(clusters: List[Cluster]) -> str:
    """Render the taxonomy's dimensions and relations as a mermaid diagram.

    Emits one node per dimension and one labeled directed edge per typed
    relation whose ``target_id`` is present among the rendered clusters.
    Relations pointing outside the rendered cluster set are dropped from
    the diagram (their source dimension's catalog entry still lists them,
    see :func:`render_catalog`). Values are never represented as diagram
    nodes. This is a verbatim rendering of the taxonomy JSON — no LLM
    involvement.

    Args:
        clusters: The in-scope taxonomy dimensions (clusters) to render.

    Returns:
        A fenced ``mermaid`` code block as a markdown string.
    """
    rendered_ids = {_cluster_id(cluster) for cluster in clusters}

    lines = ["```mermaid", "flowchart TB"]

    for cluster in clusters:
        cid = _cluster_id(cluster)
        name = cluster.get("name") or "Unnamed"
        node_id = _mermaid_node_id(cid)
        label = _escape_mermaid_label(f"{cid}. {name}")
        lines.append(f'    {node_id}["{label}"]')

    for cluster in clusters:
        cid = _cluster_id(cluster)
        node_id = _mermaid_node_id(cid)
        relations = cluster.get("relations") or []
        for relation in relations:
            target_id = _relation_target_id(relation)
            if target_id not in rendered_ids:
                continue
            relation_type = relation.get("type") or "related_to"
            target_node_id = _mermaid_node_id(target_id)
            edge_label = _escape_mermaid_label(str(relation_type))
            lines.append(f"    {node_id} -->|{edge_label}| {target_node_id}")

    lines.append("```")
    return "\n".join(lines)


def render_catalog(clusters: List[Cluster]) -> str:
    """Render the per-dimension catalog as markdown.

    For each dimension, lists its name, description, values (label and
    description), and outgoing relations with rationale. When a relation's
    ``target_id`` is not among the rendered clusters, the relation line is
    kept but noted as pointing outside this view rather than dropped —
    incoming relations are intentionally left to the diagram and not
    duplicated here. This is a verbatim rendering of the taxonomy JSON — no
    LLM involvement.

    Args:
        clusters: The in-scope taxonomy dimensions (clusters) to render.

    Returns:
        A markdown string with one section per dimension.
    """
    clusters_by_id = {_cluster_id(cluster): cluster for cluster in clusters}

    lines = ["## Dimension Catalog", ""]

    for cluster in clusters:
        cid = _cluster_id(cluster)
        name = cluster.get("name") or "Unnamed"
        description = cluster.get("description") or "No description."

        lines.append(f"### {cid}. {name}")
        lines.append("")
        lines.append(description)
        lines.append("")

        values = cluster.get("values") or []
        lines.append("**Values:**")
        lines.append("")
        if values:
            for value in values:
                if not isinstance(value, dict):
                    continue
                label = value.get("label") or "Unnamed value"
                value_description = value.get("description") or ""
                lines.append(f"- **{label}** — {value_description}")
        else:
            lines.append("_No values recorded._")
        lines.append("")

        relations = cluster.get("relations") or []
        lines.append("**Outgoing relations:**")
        lines.append("")
        if relations:
            for relation in relations:
                if not isinstance(relation, dict):
                    continue
                target_id = _relation_target_id(relation)
                relation_type = relation.get("type") or "related_to"
                rationale = relation.get("rationale") or ""
                target_cluster = clusters_by_id.get(target_id)
                if target_cluster is not None:
                    target_name = target_cluster.get("name") or "Unnamed"
                    lines.append(
                        f"- **{relation_type}** → {target_name} (#{target_id}): {rationale}"
                    )
                else:
                    lines.append(
                        f"- **{relation_type}** → #{target_id} "
                        f"_(target excluded from this view)_: {rationale}"
                    )
        else:
            lines.append("_No outgoing relations._")
        lines.append("")

    return "\n".join(lines)


def _format_dimensions_for_prompt(clusters: List[Cluster]) -> str:
    """Format dimension names and descriptions for the narrative-summary prompt."""
    lines = []
    for cluster in clusters:
        name = cluster.get("name") or "Unnamed"
        description = cluster.get("description") or ""
        lines.append(f"- {name}: {description}")
    return "\n".join(lines)


async def generate_narrative_summary(
    clusters: List[Cluster],
    explanation: str,
    configuration: Configuration,
) -> str | None:
    """Generate a readable narrative summary of the taxonomy via one fast-model call.

    Synthesizes the taxonomy's stored ``explanation`` and the in-scope
    dimensions' descriptions into a readable overview. The call may only
    reword or synthesize existing text — it must not alter, invent, or
    contradict any structural fact from the diagram/catalog (enforced by
    prompt instruction only, no post-hoc validation).

    On any failure (timeout, API error, no credentials, etc.) this returns
    ``None`` instead of raising, so report generation can still succeed with
    the narrative section omitted.

    Args:
        clusters: The in-scope taxonomy dimensions (clusters) whose names and
            descriptions ground the summary.
        explanation: The taxonomy iteration's stored rationale text to
            synthesize alongside the dimension descriptions.
        configuration: Pipeline configuration, used for ``fast_llm`` and
            ``use_case``.

    Returns:
        The narrative summary text, or ``None`` when generation failed or no
        model access is available.
    """
    try:
        model = load_chat_model(configuration.fast_llm)
        narrative_prompt = NARRATIVE_SUMMARY_PROMPT.partial(
            use_case=configuration.use_case,
        )
        structured_model = model.with_structured_output(NarrativeSummaryOutput)
        narrative_chain = (narrative_prompt | structured_model).with_config(
            run_name="GenerateNarrativeSummary"
        )

        result = await narrative_chain.ainvoke(
            {
                "explanation": explanation,
                "dimensions": _format_dimensions_for_prompt(clusters),
            }
        )
        if not isinstance(result, NarrativeSummaryOutput):
            raise TypeError(
                f"Expected NarrativeSummaryOutput from structured output chain, got {type(result)!r}"
            )
        return result.summary
    except Exception:
        logger.exception("Narrative summary generation failed; omitting from report.")
        return None


def assemble_report(
    clusters: List[Cluster],
    narrative_summary_or_none: str | None,
) -> str:
    """Combine the narrative summary, diagram, and catalog into one document.

    Sections are laid out narrative first, then the diagram, then the
    catalog, so a reader gets a plain-language overview before the
    structural detail. When the narrative summary is unavailable, a clearly
    worded "unavailable" note takes its place rather than failing the
    report.

    Args:
        clusters: The in-scope taxonomy dimensions (clusters) to render.
        narrative_summary_or_none: The generated narrative summary, or
            ``None`` when :func:`generate_narrative_summary` failed or was
            skipped.

    Returns:
        The complete markdown report as a single string.
    """
    lines = ["# Grounded Theory Report", ""]

    lines.append("## Narrative Summary")
    lines.append("")
    if narrative_summary_or_none:
        lines.append(narrative_summary_or_none)
    else:
        lines.append(
            "_Narrative summary unavailable — the summarization model could not "
            "be reached or no model access was configured. The diagram and "
            "catalog below are unaffected._"
        )
    lines.append("")

    lines.append("## Dimension Relationship Diagram")
    lines.append("")
    lines.append(render_diagram(clusters))
    lines.append("")

    lines.append(render_catalog(clusters))

    return "\n".join(lines)


async def generate_and_write_report(
    clusters: List[Cluster],
    explanation: str,
    configuration: Configuration,
    out_path: Path,
) -> str | None:
    """Generate the narrative summary, assemble the report, and write it to disk.

    Shared by every report-generation call site (standalone and
    auto-triggered), so the generate-assemble-write sequence lives in one
    place rather than being duplicated per caller.

    Returns:
        The generated narrative summary, or ``None`` when it was
        unavailable (see :func:`generate_narrative_summary`). The file is
        written either way — callers use the return value only to decide
        what to tell the operator.
    """
    narrative = await generate_narrative_summary(clusters, explanation, configuration)
    report_markdown = assemble_report(clusters, narrative)
    out_path.write_text(report_markdown)
    return narrative
