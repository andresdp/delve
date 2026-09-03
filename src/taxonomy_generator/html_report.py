"""Compose a unified, self-contained HTML report from a taxonomy run's on-disk artifacts.

Given a saved taxonomy JSON, this module locates its sibling grounded-theory
report (``.md``), biplot (``.html``), evaluation scoreboard (``.json``), and
documents (``.json``) in the same directory (see :func:`discover_siblings`),
then renders a single polished HTML page combining them (see
:func:`render_html_report`). Every sibling is optional and every resolver is
fail-soft: a missing or unmatched artifact never raises, it degrades the
corresponding page section to an explicit "not available" state.
"""

from __future__ import annotations

import html as html_lib
import importlib.resources
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from taxonomy_generator import report_renderer
from taxonomy_generator.visualization import _sanitize_name

_TIMESTAMP_RE = re.compile(r"(\d{8}_\d{6})")


def sanitize_filename_component(name: str) -> str:
    """Match main.py's inline sanitizer used for report/documents/taxonomy filenames."""
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in (name or "taxonomy"))


def _extract_timestamp(path: Path) -> str | None:
    """Extract a ``YYYYMMDD_HHMMSS`` timestamp embedded in a filename, if present."""
    match = _TIMESTAMP_RE.search(path.stem)
    return match.group(1) if match else None


@dataclass
class SiblingMatch:
    """A resolved sibling artifact path, and whether the match was a best-effort tie-break.

    ``data`` carries the already-parsed JSON content when a resolver had to
    read it to decide the match (currently only the evaluation resolver), so
    a caller can reuse it instead of re-reading the file from disk.
    """

    path: Path
    approximate: bool = False
    data: Dict[str, Any] | None = None


def _pick_candidate(
    candidates: List[Path], preferred_timestamp: str | None = None
) -> SiblingMatch | None:
    """Pick one candidate per KTD1: exact-timestamp match first, else a logged tie-break.

    The tie-break prefers the candidate whose filename carries a parseable
    embedded timestamp (newest such timestamp), falling back to most-recently
    -modified only when no candidate's filename carries one -- a filesystem
    copy operation can reset modification times, so the embedded timestamp is
    the more reliable signal.
    """
    if not candidates:
        return None
    if len(candidates) == 1:
        return SiblingMatch(candidates[0], approximate=False)

    pool = candidates
    if preferred_timestamp:
        exact = [c for c in candidates if _extract_timestamp(c) == preferred_timestamp]
        if len(exact) == 1:
            return SiblingMatch(exact[0], approximate=False)
        if exact:
            pool = exact

    with_timestamp = [(c, _extract_timestamp(c)) for c in pool]
    timestamped = [(c, ts) for c, ts in with_timestamp if ts]
    if timestamped:
        best = max(timestamped, key=lambda pair: pair[1])[0]
    else:
        best = max(pool, key=lambda c: c.stat().st_mtime)
    return SiblingMatch(best, approximate=True)


def resolve_report_path(
    directory: Path, taxonomy_name: str, taxonomy_timestamp: str | None
) -> SiblingMatch | None:
    """Locate the sibling grounded-theory report ``.md`` for a taxonomy JSON."""
    pattern = f"{sanitize_filename_component(taxonomy_name)}_report_*.md"
    candidates = sorted(directory.glob(pattern))
    return _pick_candidate(candidates, preferred_timestamp=taxonomy_timestamp)


def resolve_documents_path(
    directory: Path, taxonomy_name: str, taxonomy_timestamp: str | None
) -> SiblingMatch | None:
    """Locate the sibling documents ``.json`` for a taxonomy JSON.

    ``run()`` writes the documents JSON with the exact same timestamp as the
    taxonomy JSON in the same call, so an exact-timestamp match (KTD1's
    general tie-break rule) is preferred here too, same as the report.
    """
    pattern = f"{sanitize_filename_component(taxonomy_name)}_documents_*.json"
    candidates = sorted(directory.glob(pattern))
    return _pick_candidate(candidates, preferred_timestamp=taxonomy_timestamp)


def _biplot_filename_re(taxonomy_name: str) -> re.Pattern:
    """Build a stem regex for ``taxonomy_biplot_<name>_<stage>_<iteration>_<dims>d``.

    Matches the exact naming convention ``visualization._save_biplot_html``
    writes. A glob or substring match on the iteration segment is not safe
    here: iteration ``1`` is a substring of iteration ``10``/``11``/etc., so
    the iteration segment must be matched as a whole number, not a fragment.
    """
    return re.compile(
        rf"^taxonomy_biplot_{re.escape(_sanitize_name(taxonomy_name))}_"
        r"(?P<stage>[A-Za-z]+)_(?P<iteration>\d+)_(?P<dims>\d+)d$"
    )


def resolve_biplot_path(
    directory: Path, taxonomy_name: str, iteration: int
) -> SiblingMatch | None:
    """Locate the sibling biplot ``.html`` for a taxonomy JSON's resolved iteration.

    Prefers a ``standalone``-stage match, else the newest stage. When both a
    2D and 3D variant match the same stage and iteration, prefers 3D as the
    richer view (KTD1).
    """
    stem_re = _biplot_filename_re(taxonomy_name)
    matches = []
    for candidate in sorted(directory.glob(f"taxonomy_biplot_{_sanitize_name(taxonomy_name)}_*.html")):
        match = stem_re.match(candidate.stem)
        if match and int(match.group("iteration")) == iteration:
            matches.append((candidate, match))
    if not matches:
        return None

    standalone = [c for c, m in matches if m.group("stage") == "standalone"]
    pool = standalone or [c for c, _m in matches]

    three_d = [c for c in pool if c.stem.endswith("_3d")]
    if three_d:
        pool = three_d

    return _pick_candidate(pool)


def _evaluation_matches_source(data: Dict[str, Any], taxonomy_path: Path) -> bool:
    """Compare an evaluation artifact's ``source_file`` to the given taxonomy path by basename."""
    source_file = data.get("source_file")
    if not isinstance(source_file, str) or not source_file:
        return False
    return Path(source_file).name == taxonomy_path.name


def resolve_evaluation_path(
    directory: Path, taxonomy_path: Path, taxonomy_name: str, iteration: int
) -> SiblingMatch | None:
    """Locate the sibling evaluation scoreboard ``.json`` for a taxonomy JSON.

    Prefers an exact match on the file's own ``source_file`` field, falling
    back to ``taxonomy_name`` + ``iteration`` equality. Multi-file
    consistency-mode artifacts (``source_files``/``consistency`` shape, no
    ``source_file`` key) never match this resolver and correctly fall
    through to "no match" (KTD1).

    No filename convention distinguishes an evaluation artifact from any
    other JSON in the directory (standalone ``--evaluate`` runs name it from
    the run's own configured name, not the taxonomy's), so every ``*.json``
    file must be opened to check for a ``source_file`` key -- except the
    taxonomy JSON itself, which the caller already has in memory and never
    carries that key, so it is skipped without a read.
    """
    resolved_taxonomy_path = taxonomy_path.resolve()
    data_by_path: Dict[Path, Dict[str, Any]] = {}
    for candidate in sorted(directory.glob("*.json")):
        if candidate.resolve() == resolved_taxonomy_path:
            continue
        try:
            data = json.loads(candidate.read_text())
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            continue
        if not isinstance(data, dict) or "source_file" not in data:
            continue
        data_by_path[candidate] = data

    exact = [c for c, data in data_by_path.items() if _evaluation_matches_source(data, taxonomy_path)]
    pool = exact or [
        c
        for c, data in data_by_path.items()
        if data.get("taxonomy_name") == taxonomy_name and data.get("iteration") == iteration
    ]
    if not pool:
        return None

    match = _pick_candidate(sorted(pool))
    if match is not None:
        match.data = data_by_path.get(match.path)
    return match


@dataclass
class SiblingArtifacts:
    """The four sibling artifacts resolved for one taxonomy JSON, each optional."""

    report: SiblingMatch | None
    biplot: SiblingMatch | None
    evaluation: SiblingMatch | None
    documents: SiblingMatch | None


def get_vendored_mermaid_js() -> str:
    """Read the vendored Mermaid UMD build shipped with this package (U2, KTD4)."""
    asset = importlib.resources.files("taxonomy_generator") / "assets" / "mermaid.min.js"
    return asset.read_text(encoding="utf-8")


def discover_siblings(taxonomy_path: Path, taxonomy_name: str, iteration: int) -> SiblingArtifacts:
    """Resolve all four sibling artifacts for a saved taxonomy JSON (KTD1)."""
    directory = taxonomy_path.resolve().parent
    taxonomy_timestamp = _extract_timestamp(taxonomy_path)
    return SiblingArtifacts(
        report=resolve_report_path(directory, taxonomy_name, taxonomy_timestamp),
        biplot=resolve_biplot_path(directory, taxonomy_name, iteration),
        evaluation=resolve_evaluation_path(directory, taxonomy_path, taxonomy_name, iteration),
        documents=resolve_documents_path(directory, taxonomy_name, taxonomy_timestamp),
    )


# ── HTML rendering (U3) ────────────────────────────────────────────────────
#
# Every render_* function below is pure and fail-soft: missing source data
# renders an explicit "not available" placeholder rather than raising, and a
# legitimately empty result renders a distinct "none found" state (R2, U3).


def _e(value: Any) -> str:
    """HTML-escape a value for safe embedding in the page."""
    return html_lib.escape(str(value if value is not None else ""), quote=True)




# ── Run summary ─────────────────────────────────────────────────────────


def render_dimension_table(clusters: List[Dict[str, Any]]) -> str:
    """Render the taxonomy's dimension table, mirroring main.py's _display_taxonomy."""
    if not clusters:
        return '<p class="dg-empty">No dimensions in this taxonomy.</p>'
    rows = []
    for cluster in clusters:
        values = cluster.get("values") or []
        value_labels = [v.get("label", "") for v in values if isinstance(v, dict)]
        values_str = " &middot; ".join(_e(label) for label in value_labels if label) or "&mdash;"
        rows.append(
            "<tr>"
            f'<td class="dg-num">{_e(cluster.get("id", "?"))}</td>'
            f'<td class="dg-name">{_e(cluster.get("name", "Unnamed"))}</td>'
            f'<td class="dg-desc">{_e(cluster.get("description", "No description"))}</td>'
            f'<td class="dg-values">{values_str}</td>'
            "</tr>"
        )
    return (
        '<table class="dg-table">'
        "<thead><tr><th>#</th><th>Name</th><th>Description</th><th>Values</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
    )


def render_rationale(iterations: List[Dict[str, Any]], mode: str) -> str:
    """Render per-iteration rationale, mirroring main.py's Taxonomy Rationale panel."""
    explanations = [it.get("explanation", "") for it in iterations]
    count = len(explanations)
    parts = []
    for i, explanation in enumerate(explanations):
        if not explanation:
            continue
        label = report_renderer.iteration_label(i, count, mode)
        parts.append(f"<p><strong>{i + 1}. {_e(label)}:</strong> {_e(explanation)}</p>")
    if not parts:
        return ""
    return f'<div class="dg-rationale">{"".join(parts)}</div>'


def render_document_labeling(documents_data: Dict[str, Any] | None) -> str:
    """Render the document-labeling table, mirroring main.py's _display_documents.

    ``documents_data`` is the sibling documents JSON's parsed content
    (``{"taxonomy_name": ..., "documents": [...]}"``), or ``None`` when no
    sibling was found -- distinct from an empty ``documents`` list, which is
    a legitimate "none found" result rather than "not available" (U3).
    """
    if documents_data is None:
        return '<p class="dg-unavailable">Document labeling results are not available for this run.</p>'
    documents = documents_data.get("documents") or []
    if not documents:
        return '<p class="dg-empty">No labeled documents found.</p>'
    rows = []
    for doc in documents:
        category = doc.get("category") if isinstance(doc, dict) else None
        score = doc.get("score") if isinstance(doc, dict) else None
        content = (doc.get("content") if isinstance(doc, dict) else "") or ""
        preview = content[:160]
        if len(content) > 160:
            preview += "..."
        score_str = f"{score:.2f}" if isinstance(score, (int, float)) else "&mdash;"
        rows.append(
            "<tr>"
            f'<td class="dg-category">{_e(category or "N/A")}</td>'
            f'<td class="dg-score">{score_str}</td>'
            f'<td class="dg-preview">{_e(preview)}</td>'
            "</tr>"
        )
    return (
        '<table class="dg-table dg-documents">'
        "<thead><tr><th>Category</th><th>Score</th><th>Document preview</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
    )


def render_run_metrics_line(taxonomy_data: Dict[str, Any]) -> str:
    """Render the timing/token line, or a "not recorded" note for pre-U1 taxonomy JSONs (R4)."""
    run_metrics = taxonomy_data.get("run_metrics")
    if not run_metrics:
        return '<p class="dg-unavailable">Run timing and token usage were not recorded for this run.</p>'
    elapsed = run_metrics.get("elapsed_seconds")
    total_tokens = run_metrics.get("total_tokens", 0)
    prompt_tokens = run_metrics.get("prompt_tokens", 0)
    completion_tokens = run_metrics.get("completion_tokens", 0)
    elapsed_str = f"{elapsed:.1f}s" if isinstance(elapsed, (int, float)) else "n/a"
    return (
        '<p class="dg-metrics">'
        f"Pipeline completed in <strong>{_e(elapsed_str)}</strong> &middot; "
        f"<strong>{total_tokens:,}</strong> tokens "
        f"({prompt_tokens:,} prompt + {completion_tokens:,} completion)"
        "</p>"
    )


def render_run_summary(taxonomy_data: Dict[str, Any], documents_data: Dict[str, Any] | None) -> str:
    """Compose the run-summary section: dimension table, rationale, labeling, run metrics (R3)."""
    iterations = taxonomy_data.get("iterations") or []
    final_clusters = (
        iterations[-1]["clusters"] if iterations else (taxonomy_data.get("selected_clusters") or [])
    )
    mode = taxonomy_data.get("mode") or "train"
    return (
        '<section id="run-summary" class="dg-section">'
        "<h2>Run Summary</h2>"
        f"{render_run_metrics_line(taxonomy_data)}"
        f"{render_dimension_table(final_clusters)}"
        f'<p class="dg-summary-line">Total dimensions: <strong>{len(final_clusters)}</strong> '
        f"&middot; Iterations: <strong>{len(iterations)}</strong></p>"
        f"{render_rationale(iterations, mode)}"
        "<h3>Document Labeling Results</h3>"
        f"{render_document_labeling(documents_data)}"
        "</section>"
    )


# ── Diagram ──────────────────────────────────────────────────────────────


def render_diagram_section(clusters: List[Dict[str, Any]]) -> str:
    """Embed the dimension-relationship diagram as an inline Mermaid block."""
    if not clusters:
        return (
            '<section id="dimension-diagram" class="dg-section">'
            "<h2>Dimension Diagram</h2>"
            '<p class="dg-empty">No dimensions to diagram.</p>'
            "</section>"
        )
    # render_diagram always wraps its output in a ```mermaid fence (report_renderer.py);
    # unwrap it here rather than duplicating the diagram-building logic.
    diagram_md = report_renderer.render_diagram(clusters)
    lines = diagram_md.splitlines()
    if lines and lines[0].strip() == "```mermaid":
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    mermaid_source = "\n".join(lines)
    return (
        '<section id="dimension-diagram" class="dg-section">'
        "<h2>Dimension Diagram</h2>"
        f'<pre class="mermaid" aria-label="Dimension relationship diagram">{_e(mermaid_source)}</pre>'
        "</section>"
    )


# ── Catalog and discarded dimensions ────────────────────────────────────


def _merged_from_note_html(value: Dict[str, Any]) -> str:
    """Render the inline note for a value consolidation folded into this one."""
    labels = report_renderer.merged_from_labels(value)
    if not labels:
        return ""
    quoted = ", ".join(f'"{label}"' for label in labels)
    plural = "s" if len(labels) != 1 else ""
    return (
        f' <span class="dg-merged-note">(consolidated with {len(labels)} similar value{plural} '
        f"judged the same decision: {_e(quoted)})</span>"
    )


def render_dimension_pull_quotes(clusters: List[Dict[str, Any]]) -> str:
    """Pull-quote treatment for the top 3 dimensions by value count (KTD5)."""
    if not clusters:
        return ""
    ranked = sorted(clusters, key=lambda c: len(c.get("values") or []), reverse=True)[:3]
    quotes = [
        f'<blockquote class="dg-pull-quote dg-dimension-quote"><strong>{_e(c.get("name") or "Unnamed")}</strong>'
        f' &mdash; {_e(c.get("description") or "")}</blockquote>'
        for c in ranked
    ]
    return f'<div class="dg-dimension-quotes">{"".join(quotes)}</div>'


def render_catalog_section(clusters: List[Dict[str, Any]]) -> str:
    """Render the per-dimension catalog as styled cards (KTD2: HTML-native, not markdown-converted)."""
    if not clusters:
        return (
            '<section id="dimension-catalog" class="dg-section">'
            "<h2>Dimension Catalog</h2>"
            '<p class="dg-empty">No dimensions in this taxonomy.</p>'
            "</section>"
        )
    clusters_by_id = {str(c.get("id") or "?"): c for c in clusters}
    cards = []
    for cluster in sorted(clusters, key=report_renderer._id_sort_key):
        cid = str(cluster.get("id") or "?")
        values = cluster.get("values") or []
        value_items = [
            f'<li><strong>{_e(v.get("label") or "Unnamed value")}</strong> &mdash; '
            f'{_e(v.get("description") or "")}{_merged_from_note_html(v)}</li>'
            for v in values
            if isinstance(v, dict)
        ]
        values_html = f"<ul>{''.join(value_items)}</ul>" if value_items else '<p class="dg-empty">No values recorded.</p>'

        relations = cluster.get("relations") or []
        relation_items = []
        for relation in relations:
            if not isinstance(relation, dict):
                continue
            target_id = str(relation.get("target_id") or "")
            relation_type = relation.get("type") or "related_to"
            rationale = relation.get("rationale") or ""
            target = clusters_by_id.get(target_id)
            if target is not None:
                relation_items.append(
                    f'<li><strong>{_e(relation_type)}</strong> &rarr; {_e(target.get("name") or "Unnamed")} '
                    f"(#{_e(target_id)}): {_e(rationale)}</li>"
                )
            else:
                relation_items.append(
                    f'<li><strong>{_e(relation_type)}</strong> &rarr; #{_e(target_id)} '
                    f"<em>(target excluded from this view)</em>: {_e(rationale)}</li>"
                )
        relations_html = (
            f"<ul>{''.join(relation_items)}</ul>" if relation_items else '<p class="dg-empty">No outgoing relations.</p>'
        )

        cards.append(
            '<article class="dg-card">'
            f'<h3>{_e(cid)}. {_e(cluster.get("name") or "Unnamed")}</h3>'
            f'<p>{_e(cluster.get("description") or "No description.")}</p>'
            "<h4>Values</h4>"
            f"{values_html}"
            "<h4>Outgoing relations</h4>"
            f"{relations_html}"
            "</article>"
        )
    return (
        '<section id="dimension-catalog" class="dg-section">'
        "<h2>Dimension Catalog</h2>"
        f"{render_dimension_pull_quotes(clusters)}"
        f'<div class="dg-cards">{"".join(cards)}</div>'
        "</section>"
    )


def render_discarded_section(
    dropped: List[Dict[str, Any]], all_clusters: List[Dict[str, Any]]
) -> str:
    """Render dimensions excluded during dimension selection. Omitted entirely when none (KTD5)."""
    if not dropped:
        return ""
    clusters_by_id = {str(c.get("id") or "?"): c for c in all_clusters}
    items = []
    for item in sorted(dropped, key=report_renderer._id_sort_key):
        did = str(item.get("id") or "?")
        source = clusters_by_id.get(did)
        name = (source.get("name") if source else None) or "Unnamed"
        rationale = item.get("rationale") or "No rationale recorded."
        items.append(f"<li><strong>{_e(did)}. {_e(name)}</strong> &mdash; {_e(rationale)}</li>")
    return (
        '<section id="discarded-dimensions" class="dg-section">'
        "<h2>Discarded Dimensions</h2>"
        "<p>Dimensions considered during taxonomy generation but excluded from this view during "
        "dimension selection, judged not relevant to the stated use case:</p>"
        f"<ul>{''.join(items)}</ul>"
        "</section>"
    )


# ── Evaluation ───────────────────────────────────────────────────────────


def render_evaluation_section(evaluation_data: Dict[str, Any] | None) -> str:
    """Render the evaluation scoreboard. A missing sibling and `unavailable: true` render distinct text."""
    if evaluation_data is None:
        return (
            '<section id="evaluation" class="dg-section">'
            "<h2>Evaluation</h2>"
            '<p class="dg-unavailable">No evaluation was run for this taxonomy.</p>'
            "</section>"
        )
    scoreboard = evaluation_data.get("scoreboard") or {}
    if scoreboard.get("unavailable"):
        reason = scoreboard.get("error") or "unknown error"
        return (
            '<section id="evaluation" class="dg-section">'
            "<h2>Evaluation</h2>"
            f'<p class="dg-unavailable">Evaluation unavailable: {_e(reason)}</p>'
            "</section>"
        )
    criteria = scoreboard.get("criteria") or []
    if not criteria:
        return (
            '<section id="evaluation" class="dg-section">'
            "<h2>Evaluation</h2>"
            '<p class="dg-empty">No evaluation criteria were recorded.</p>'
            "</section>"
        )
    rows = []
    for row in criteria:
        name = row.get("name") or "?"
        if row.get("evaluated", True):
            score = row.get("score")
            score_str = f"{score:.2f}" if isinstance(score, (int, float)) else "&mdash;"
            passed = row.get("passed")
            pass_str = "&#10003;" if passed else ("&#10007;" if passed is not None else "&mdash;")
            reason = " ".join((row.get("reason") or "").split())
        else:
            score_str = "&mdash;"
            pass_str = "&mdash;"
            reason = "Not evaluated -- no documents provided."
        rows.append(f"<tr><td>{_e(name)}</td><td>{score_str}</td><td>{pass_str}</td><td>{_e(reason)}</td></tr>")
    overall = scoreboard.get("overall")
    overall_str = f"{overall:.2f}" if isinstance(overall, (int, float)) else "&mdash;"
    model = scoreboard.get("model") or "default"
    return (
        '<section id="evaluation" class="dg-section">'
        "<h2>Evaluation</h2>"
        f'<p class="dg-summary-line">Overall score: <strong>{overall_str}</strong> &middot; judge {_e(model)}</p>'
        '<table class="dg-table">'
        "<thead><tr><th>Criterion</th><th>Score</th><th>Pass</th><th>Reason</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
        "</section>"
    )


# ── Narrative summary ────────────────────────────────────────────────────

_NARRATIVE_HEADING_RE = re.compile(r"^##\s+Narrative Summary\s*$", re.MULTILINE)
_NEXT_HEADING_RE = re.compile(r"^##\s+", re.MULTILINE)
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_ITALIC_RE = re.compile(r"(?<!\*)\*([^*]+?)\*(?!\*)")


def _extract_narrative_summary(report_md_text: str) -> str | None:
    """Extract the "## Narrative Summary" section's body from a report markdown."""
    match = _NARRATIVE_HEADING_RE.search(report_md_text)
    if not match:
        return None
    start = match.end()
    next_match = _NEXT_HEADING_RE.search(report_md_text, start)
    end = next_match.start() if next_match else len(report_md_text)
    return report_md_text[start:end].strip()


def _normalize_inline_markdown(text: str) -> str:
    """Mechanically convert **bold**/*italic* spans to HTML (KTD2, no markdown-parser dependency).

    Operates on already-escaped text: ``html.escape`` leaves ``*`` untouched,
    so the markdown markers survive escaping intact for this pass to find.
    """
    escaped = _e(text)
    escaped = _BOLD_RE.sub(r"<strong>\1</strong>", escaped)
    escaped = _ITALIC_RE.sub(r"<em>\1</em>", escaped)
    return escaped


def _paragraph_or_list_html(block: str) -> str:
    """Render one blank-line-separated block as a <p>, or a <ul> for '- '/'* ' list lines."""
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    if not lines:
        return ""
    if all(line.startswith(("- ", "* ")) for line in lines):
        items = "".join(f"<li>{_normalize_inline_markdown(line[2:].strip())}</li>" for line in lines)
        return f"<ul>{items}</ul>"
    return f"<p>{_normalize_inline_markdown(' '.join(lines))}</p>"


def _first_sentence(text: str) -> str:
    """Return the narrative's first sentence for pull-quote treatment (KTD5)."""
    stripped = text.strip()
    if not stripped:
        return ""
    match = re.search(r"[.!?](\s|$)", stripped)
    return stripped[: match.end()].strip() if match else stripped


def render_narrative_section(report_md_text: str | None) -> str:
    """Render the narrative summary, extracted and normalized from the sibling report .md (KTD2)."""
    narrative = _extract_narrative_summary(report_md_text) if report_md_text is not None else None
    if not narrative:
        return (
            '<section id="narrative-summary" class="dg-section">'
            "<h2>Narrative Summary</h2>"
            '<p class="dg-unavailable">No narrative summary is available for this run.</p>'
            "</section>"
        )
    blocks = re.split(r"\n\s*\n", narrative)
    body = "".join(_paragraph_or_list_html(block) for block in blocks)
    pull_quote = _first_sentence(narrative)
    pull_quote_html = (
        f'<blockquote class="dg-pull-quote">{_normalize_inline_markdown(pull_quote)}</blockquote>'
        if pull_quote
        else ""
    )
    return (
        '<section id="narrative-summary" class="dg-section">'
        "<h2>Narrative Summary</h2>"
        f"{pull_quote_html}"
        f'<div class="dg-narrative">{body}</div>'
        "</section>"
    )


# ── Biplot ───────────────────────────────────────────────────────────────

_PLOTLY_SNIPPET_RE = re.compile(
    r'(<div\s+id="[^"]+"\s+class="plotly-graph-div"[^>]*>.*?</div>\s*<script[^>]*>.*?Plotly\.newPlot\(.*?</script>)',
    re.DOTALL,
)


def _extract_plotly_snippet(biplot_html_text: str) -> str | None:
    """Extract the chart <div> and trailing Plotly.newPlot(...) <script> verbatim (KTD3)."""
    match = _PLOTLY_SNIPPET_RE.search(biplot_html_text)
    return match.group(1) if match else None


def render_biplot_section(biplot_html_text: str | None) -> str:
    """Embed the biplot chart. Missing or malformed sibling both fall back to "not available" (KTD3)."""
    snippet = _extract_plotly_snippet(biplot_html_text) if biplot_html_text is not None else None
    if snippet is not None:
        return (
            '<section id="biplot" class="dg-section">'
            "<h2>Biplot</h2>"
            f'<div class="dg-biplot" role="img" aria-label="Taxonomy biplot chart">{snippet}</div>'
            "</section>"
        )
    return (
        '<section id="biplot" class="dg-section">'
        "<h2>Biplot</h2>"
        '<p class="dg-unavailable">No biplot is available for this run.</p>'
        "</section>"
    )


# ── Page shell ───────────────────────────────────────────────────────────

_NAV_ITEMS = [
    ("run-summary", "Run Summary"),
    ("dimension-diagram", "Diagram"),
    ("dimension-catalog", "Catalog"),
    ("discarded-dimensions", "Discarded"),
    ("narrative-summary", "Narrative"),
    ("biplot", "Biplot"),
    ("evaluation", "Evaluation"),
]

_PAGE_STYLE = """<style>
:root{--dg-bg:#fdfcf9;--dg-fg:#1a1a1a;--dg-accent:#2f5233;--dg-muted:#6b6b6b;--dg-border:#e2ddd0;--dg-card:#ffffff;}
*{box-sizing:border-box;}
body{margin:0;background:var(--dg-bg);color:var(--dg-fg);font-family:Georgia,'Iowan Old Style',serif;line-height:1.6;}
.dg-layout{display:flex;max-width:1100px;margin:0 auto;}
.dg-nav{position:sticky;top:0;align-self:flex-start;width:220px;padding:2.5rem 1rem;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:0.85rem;}
.dg-nav a{display:block;padding:0.35rem 0 0.35rem 0.75rem;color:var(--dg-muted);text-decoration:none;border-left:2px solid transparent;}
.dg-nav a:hover{color:var(--dg-accent);border-left-color:var(--dg-accent);}
.dg-main{flex:1;padding:2.5rem 2rem 6rem;min-width:0;}
.dg-hero h1{font-size:2.4rem;margin:0 0 0.5rem;}
.dg-hero p{color:var(--dg-muted);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;}
.dg-section{margin:3rem 0;scroll-margin-top:1.5rem;}
.dg-section h2{font-size:1.5rem;border-bottom:1px solid var(--dg-border);padding-bottom:0.4rem;}
.dg-pull-quote{border-left:4px solid var(--dg-accent);margin:1.5rem 0;padding:0.25rem 0 0.25rem 1.25rem;font-size:1.25rem;font-style:italic;color:var(--dg-accent);}
.dg-dimension-quotes{display:flex;flex-wrap:wrap;gap:1rem;margin:1rem 0 2rem;}
.dg-dimension-quotes .dg-pull-quote{flex:1 1 220px;font-size:1rem;}
.dg-table{width:100%;border-collapse:collapse;margin:1rem 0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:0.92rem;}
.dg-table th,.dg-table td{text-align:left;padding:0.5rem 0.75rem;border-bottom:1px solid var(--dg-border);vertical-align:top;}
.dg-table th{color:var(--dg-muted);font-weight:600;}
.dg-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:1.25rem;}
.dg-card{background:var(--dg-card);border:1px solid var(--dg-border);border-radius:8px;padding:1.25rem;}
.dg-card h4{font-size:0.8rem;text-transform:uppercase;letter-spacing:0.04em;color:var(--dg-muted);margin-bottom:0.35rem;}
.dg-merged-note{color:var(--dg-muted);font-size:0.85rem;}
.dg-unavailable,.dg-empty{color:var(--dg-muted);font-style:italic;}
.dg-metrics,.dg-summary-line{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:var(--dg-muted);}
.dg-biplot{width:100%;height:640px;}
.dg-narrative p{font-size:1.05rem;}
pre.mermaid{background:var(--dg-card);border:1px solid var(--dg-border);border-radius:8px;padding:1.5rem;overflow-x:auto;}
@media (max-width:720px){
  .dg-layout{flex-direction:column;}
  .dg-nav{position:static;width:auto;display:flex;overflow-x:auto;padding:1rem;border-bottom:1px solid var(--dg-border);}
  .dg-nav a{padding:0.35rem 0.75rem;border-left:none;border-bottom:2px solid transparent;white-space:nowrap;}
  .dg-nav a:hover{border-left-color:transparent;border-bottom-color:var(--dg-accent);}
}
</style>"""


def _render_nav(present_ids: set) -> str:
    """Render the sticky in-page navigation for whichever sections are present (KTD5)."""
    links = "".join(
        f'<a href="#{anchor}">{_e(label)}</a>' for anchor, label in _NAV_ITEMS if anchor in present_ids
    )
    return f'<nav class="dg-nav" aria-label="Section navigation">{links}</nav>'


def render_html_report(
    taxonomy_name: str,
    taxonomy_data: Dict[str, Any],
    view_clusters: List[Dict[str, Any]],
    dropped_dimensions: List[Dict[str, Any]],
    all_clusters_for_dropped: List[Dict[str, Any]],
    documents_data: Dict[str, Any] | None,
    report_md_text: str | None,
    biplot_html_text: str | None,
    evaluation_data: Dict[str, Any] | None,
    mermaid_js: str,
    plotlyjs_js: str,
) -> str:
    """Compose the final self-contained HTML report page in KTD5's fixed section order.

    ``mermaid_js`` and ``plotlyjs_js`` are the vendored Mermaid source (U2)
    and ``plotly.offline.get_plotlyjs()``'s output, inlined once page-wide
    (KTD3/KTD4) so the page needs no network access (R5).
    """
    sections = {
        "run-summary": render_run_summary(taxonomy_data, documents_data),
        "dimension-diagram": render_diagram_section(view_clusters),
        "dimension-catalog": render_catalog_section(view_clusters),
        "discarded-dimensions": render_discarded_section(dropped_dimensions, all_clusters_for_dropped),
        "narrative-summary": render_narrative_section(report_md_text),
        "biplot": render_biplot_section(biplot_html_text),
        "evaluation": render_evaluation_section(evaluation_data),
    }
    present_ids = {anchor for anchor, body in sections.items() if body}
    body_html = "".join(sections[anchor] for anchor, _label in _NAV_ITEMS if sections.get(anchor))

    return (
        '<!doctype html><html lang="en"><head>'
        '<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{_e(taxonomy_name)} &mdash; Taxonomy Report</title>"
        f"<script>{mermaid_js}</script>"
        f"<script>{plotlyjs_js}</script>"
        f"{_PAGE_STYLE}"
        "</head><body>"
        '<div class="dg-layout">'
        f"{_render_nav(present_ids)}"
        '<main class="dg-main">'
        '<header class="dg-hero">'
        f"<h1>{_e(taxonomy_name)}</h1>"
        "<p>Unified taxonomy report</p>"
        "</header>"
        f"{body_html}"
        "</main>"
        "</div>"
        "<script>mermaid.initialize({startOnLoad:true});</script>"
        "</body></html>"
    )
