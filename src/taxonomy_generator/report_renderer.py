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
from typing import Any, Dict, List, Tuple

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


def _id_sort_key(cluster: Cluster) -> Tuple[int, Any]:
    """Sort key placing dimensions in numeric id order (1, 2, ..., 10, 11).

    Dimension ids are stored as strings, so a plain string sort would put
    "10" before "2". Falls back to the raw string for a non-numeric id so
    rendering never errors on unexpected data — it just sorts after every
    numeric id, in string order.
    """
    cid = _cluster_id(cluster)
    try:
        return (0, int(cid))
    except ValueError:
        return (1, cid)


def _in_id_order(clusters: List[Cluster]) -> List[Cluster]:
    """Return clusters sorted into numeric dimension-id order.

    The order clusters arrive in reflects how the view was selected (e.g.
    ``selected_clusters`` preserves the model's relevance ordering, not
    dimension-id order) — every rendered section of the report presents
    dimensions in the same id order regardless of that upstream ordering.
    """
    return sorted(clusters, key=_id_sort_key)


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
    clusters = _in_id_order(clusters)
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


def merged_from_labels(value: Dict[str, Any]) -> List[str]:
    """Extract the draft-value labels a consolidated value's ``merged_from`` stands in for.

    Value consolidation (when enabled) merges draft values judged to
    represent the same decision, keeping the nearest-to-centroid value's
    label/description as canonical. Shared by both the markdown catalog
    (:func:`_merged_from_note`) and the HTML catalog (``html_report.py``),
    so the "how do we read merged_from" rule has one owner.

    Returns:
        The merged-away drafts' labels (or id, if label is absent), or an
        empty list when this value was not the product of a merge.
    """
    merged_from = value.get("merged_from") or []
    if not isinstance(merged_from, list):
        return []
    return [
        m.get("label") or m.get("id", "?")
        for m in merged_from
        if isinstance(m, dict)
    ]


def _merged_from_note(value: Dict[str, Any]) -> str:
    """Build the inline note for a value consolidation folded into this one.

    The merged-away drafts are not silently dropped — this renders which
    ones a catalog entry now stands in for, so a reader sees the
    consolidation rather than an unexplained value count.

    Args:
        value: A single value dict from a dimension's ``values`` list.

    Returns:
        A parenthetical markdown note, or "" when this value was not the
        product of a merge (``merged_from`` absent or empty).
    """
    labels = merged_from_labels(value)
    if not labels:
        return ""
    quoted = ", ".join(f'"{label}"' for label in labels)
    return f"_(consolidated with {len(labels)} similar value{'s' if len(labels) != 1 else ''} judged the same decision: {quoted})_"


def render_catalog(clusters: List[Cluster]) -> str:
    """Render the per-dimension catalog as markdown.

    For each dimension, lists its name, description, values (label and
    description), and outgoing relations with rationale. When a relation's
    ``target_id`` is not among the rendered clusters, the relation line is
    kept but noted as pointing outside this view rather than dropped —
    incoming relations are intentionally left to the diagram and not
    duplicated here. A value produced by value consolidation (see
    :func:`_merged_from_note`) is annotated with the similar draft values it
    now stands in for. This is a verbatim rendering of the taxonomy JSON —
    no LLM involvement.

    Args:
        clusters: The in-scope taxonomy dimensions (clusters) to render.

    Returns:
        A markdown string with one section per dimension.
    """
    clusters_by_id = {_cluster_id(cluster): cluster for cluster in clusters}
    clusters = _in_id_order(clusters)

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
                line = f"- **{label}** — {value_description}"
                merged_note = _merged_from_note(value)
                if merged_note:
                    line += f" {merged_note}"
                lines.append(line)
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


def render_discarded_dimensions(dropped: List[Cluster], all_clusters: List[Cluster]) -> str:
    """Render the dimensions dimension-selection excluded from this view.

    Verbatim rendering — no LLM involvement. Discarded dimensions are by
    definition absent from the rendered/selected view, so their name is
    looked up from ``all_clusters`` (the full, pre-selection cluster list)
    rather than from the view being rendered.

    Args:
        dropped: Discarded-dimension records (``id``, ``rationale``) from
            the taxonomy's dimension-selection step.
        all_clusters: The full cluster list to resolve discarded names from.

    Returns:
        A markdown string, or "" when there is nothing to render (no
        discarded dimensions recorded, or not applicable to this view).
    """
    if not dropped:
        return ""

    clusters_by_id = {_cluster_id(c): c for c in all_clusters}

    lines = [
        "## Discarded Dimensions",
        "",
        "Dimensions considered during taxonomy generation but excluded from "
        "this view during dimension selection, judged not relevant to the "
        "stated use case:",
        "",
    ]
    for item in _in_id_order(dropped):
        did = _cluster_id(item)
        source = clusters_by_id.get(did)
        name = (source.get("name") if source else None) or "Unnamed"
        rationale = item.get("rationale") or "No rationale recorded."
        lines.append(f"- **{did}. {name}** — {rationale}")

    return "\n".join(lines)


def render_evaluation(scoreboard: Dict[str, Any] | None) -> str:
    """Render the stored evaluation scoreboard as a deterministic markdown section.

    Verbatim rendering of stored scores — no model calls. Returns "" when
    there is nothing to render (``None``, empty, or unavailable — the
    section is omitted rather than rendered as failed).
    """
    if not scoreboard or scoreboard.get("unavailable"):
        return ""

    criteria = scoreboard.get("criteria") or []
    if not criteria:
        return ""

    out = [
        "## Evaluation",
        "",
        f"_Observe-only LLM-as-judge scoreboard (judge: {scoreboard.get('model') or 'default'}). "
        "Pass flags are display-only — nothing gates on them._",
        "",
        "| Criterion | Score | Pass | Reason |",
        "|---|---|---|---|",
    ]
    for row in criteria:
        name = str(row.get("name") or "?")
        if row.get("evaluated", True):
            score = row.get("score")
            score_str = f"{score:.2f}" if score is not None else "—"
            passed = row.get("passed")
            pass_str = "✓" if passed else ("✗" if passed is not None else "—")
            reason = " ".join(str(row.get("reason") or "").split())
        else:
            score_str = "—"
            pass_str = "—"
            reason = "Not evaluated — no documents provided."
        out.append(f"| {name} | {score_str} | {pass_str} | {reason} |")

    overall = scoreboard.get("overall")
    if overall is not None:
        out.append("")
        out.append(f"**Overall score:** {overall:.2f} (mean of evaluated criteria)")

    return "\n".join(out)


def iteration_label(index: int, count: int, mode: str) -> str:
    """Name one taxonomy iteration's rationale for display (console table or HTML report).

    Shared by ``main.py``'s console rationale panel and ``html_report.py``'s
    run-summary section so the label rule has one owner. ``train`` mode
    labels the last iterations Selection/Consolidation/Review (in that
    tail order) and the first Generation, everything else Update. ``test``
    mode labels the first Seed and, when more than one iteration exists,
    the last Aggregation, everything else Update.
    """
    if mode == "test":
        if index == 0:
            return "Seed"
        if count >= 2 and index == count - 1:
            return "Aggregation"
        return "Update"

    tail_labels: Dict[int, str] = {}
    if count >= 1:
        tail_labels[count - 1] = "Selection"
    if count >= 2:
        tail_labels[count - 2] = "Consolidation"
    if count >= 3:
        tail_labels[count - 3] = "Review"
    if index in tail_labels:
        return tail_labels[index]
    return "Generation" if index == 0 else "Update"


def _format_dimensions_for_prompt(clusters: List[Cluster]) -> str:
    """Format dimension names and descriptions for the narrative-summary prompt."""
    lines = []
    for cluster in _in_id_order(clusters):
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
    dropped_dimensions: List[Cluster] | None = None,
    all_clusters_for_dropped: List[Cluster] | None = None,
    evaluation: Dict[str, Any] | None = None,
) -> str:
    """Combine the narrative summary, diagram, catalog, and discarded-dimension list into one document.

    Sections are laid out narrative first, then the diagram, then the
    catalog, then discarded dimensions last, so a reader gets a
    plain-language overview before the structural detail. When the narrative
    summary is unavailable, a clearly worded "unavailable" note takes its
    place rather than failing the report. The discarded-dimensions section
    is omitted entirely when there is nothing to show (see
    :func:`render_discarded_dimensions`).

    Args:
        clusters: The in-scope taxonomy dimensions (clusters) to render.
        narrative_summary_or_none: The generated narrative summary, or
            ``None`` when :func:`generate_narrative_summary` failed or was
            skipped.
        dropped_dimensions: Discarded-dimension records for this view, or
            ``None``/empty when not applicable (see
            :func:`render_discarded_dimensions`).
        all_clusters_for_dropped: The full, pre-selection cluster list used
            to resolve discarded dimensions' names.

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

    discarded = render_discarded_dimensions(dropped_dimensions or [], all_clusters_for_dropped or [])
    if discarded:
        lines.append("")
        lines.append(discarded)

    evaluation_section = render_evaluation(evaluation)
    if evaluation_section:
        lines.append("")
        lines.append(evaluation_section)

    return "\n".join(lines)


async def generate_and_write_report(
    clusters: List[Cluster],
    explanation: str,
    configuration: Configuration,
    out_path: Path,
    dropped_dimensions: List[Cluster] | None = None,
    all_clusters_for_dropped: List[Cluster] | None = None,
    evaluation: Dict[str, Any] | None = None,
) -> str | None:
    """Generate the narrative summary, assemble the report, and write it to disk.

    Shared by every report-generation call site (standalone and
    auto-triggered), so the generate-assemble-write sequence lives in one
    place rather than being duplicated per caller.

    Args:
        dropped_dimensions: Discarded-dimension records for this view, or
            ``None``/empty when not applicable — see
            :func:`render_discarded_dimensions`.
        all_clusters_for_dropped: The full, pre-selection cluster list used
            to resolve discarded dimensions' names.

    Returns:
        The generated narrative summary, or ``None`` when it was
        unavailable (see :func:`generate_narrative_summary`). The file is
        written either way — callers use the return value only to decide
        what to tell the operator.
    """
    narrative = await generate_narrative_summary(clusters, explanation, configuration)
    report_markdown = assemble_report(
        clusters, narrative, dropped_dimensions, all_clusters_for_dropped, evaluation
    )
    out_path.write_text(report_markdown)
    return narrative
