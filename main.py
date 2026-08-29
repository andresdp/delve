"""Delve Taxonomy Generator — CLI entry point.

Usage:
    # From a corpus file (one document per line for .txt, or JSON array for .json):
    python main.py --corpus my_corpus.txt
    python main.py --corpus documents.json

    # With custom model:
    python main.py --corpus my_corpus.txt --model openai/gpt-5.4-nano

    # With custom config file:
    python main.py --corpus my_corpus.txt --config /path/to/config.yaml

    # Render a PCA biplot from a saved taxonomy JSON (no LLM calls in uniform mode):
    python main.py --visualize my_output/taxonomy_20250101_120000.json

    # Render a self-contained grounded-theory markdown report from a saved taxonomy JSON:
    python main.py --report my_output/taxonomy_20250101_120000.json
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional, Tuple

from dotenv import load_dotenv
from langchain_core.callbacks import BaseCallbackHandler
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from taxonomy_generator import graph, report_renderer, strings_to_docs
from taxonomy_generator.configuration import Configuration, init_settings

logger = logging.getLogger(__name__)
console = Console()

# ── Pipeline step display configuration ──────────────────────────────────
STEP_INFO = {
    "load_corpus": ("📂", "Loading corpus"),
    "summarize": ("📝", "Generating summaries"),
    "get_minibatches": ("📦", "Creating minibatches"),
    "open_code_minibatch": ("🔬", "Open coding minibatch"),
    "generate_taxonomy": ("🧠", "Generating initial taxonomy"),
    "update_taxonomy": ("🔄", "Updating taxonomy"),
    "check_saturation": ("🧪", "Checking saturation"),
    "review_taxonomy": ("🔍", "Reviewing taxonomy"),
    "consolidate_values": ("🧲", "Consolidating values"),
    "select_dimensions": ("🎯", "Selecting dimensions"),
    "label_documents": ("🏷️", "Labeling documents"),
    "evaluate_taxonomy": ("🎯", "Evaluating taxonomy"),
    "aggregate_new_values": ("🧩", "Aggregating new values"),
}


def _resolve_feedback_text(args: argparse.Namespace, settings) -> Optional[str]:
    """Resolve external feedback text with CLI-over-config precedence.

    Precedence: ``--feedback`` > ``--feedback-file`` > config ``feedback.text``
    > config ``feedback.file`` > None.
    """
    if getattr(args, "feedback", None):
        return args.feedback
    if getattr(args, "feedback_file", None):
        with open(args.feedback_file) as f:
            text = f.read().strip()
        if text:
            return text
        logger.warning("Feedback file %s is empty — ignoring.", args.feedback_file)
        return None
    fb = getattr(settings, "feedback", None)
    if fb is None:
        return None
    if fb.text:
        return fb.text
    if fb.file:
        with open(fb.file) as f:
            text = f.read().strip()
        if text:
            return text
        logger.warning("Configured feedback file %s is empty — ignoring.", fb.file)
    return None


class TokenTracker(BaseCallbackHandler):
    """Accumulates token usage across all LLM calls in the pipeline."""

    def __init__(self) -> None:
        self.total_tokens: int = 0
        self.prompt_tokens: int = 0
        self.completion_tokens: int = 0

    def on_llm_end(self, response, **kwargs) -> None:
        """Extract token counts from LLM response metadata."""
        try:
            for generation in response.generations:
                for gen in generation:
                    # Chat models store token info in generation_info or message.response_metadata
                    token_info = None
                    if hasattr(gen, "message") and hasattr(gen.message, "response_metadata"):
                        token_info = gen.message.response_metadata.get("token_usage") or gen.message.response_metadata.get("usage")
                    if token_info is None and hasattr(gen, "generation_info") and gen.generation_info:
                        token_info = gen.generation_info.get("token_usage") or gen.generation_info.get("usage")
                    if token_info and isinstance(token_info, dict):
                        self.total_tokens += token_info.get("total_tokens", 0)
                        self.prompt_tokens += token_info.get("prompt_tokens", 0)
                        self.completion_tokens += token_info.get("completion_tokens", 0)
        except Exception:
            logger.debug("Could not extract token usage from LLM response", exc_info=True)


def _format_elapsed(seconds: float) -> str:
    """Format elapsed time for display."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}m {secs:.1f}s"


def load_corpus(path: str) -> list[str]:
    """Load documents from a file.

    Supports:
    - .txt: One document per line (blank lines are skipped).
    - .json: A JSON array of strings or objects with a 'content' field.
    """
    logger.info("Loading corpus from file: %s", path)
    try:
        if path.endswith(".json"):
            with open(path) as f:
                data = json.load(f)
            texts = []
            for item in data:
                if isinstance(item, str):
                    texts.append(item)
                elif isinstance(item, dict) and "content" in item:
                    texts.append(item["content"])
                else:
                    texts.append(str(item))
            logger.info("Loaded %d documents from JSON corpus", len(texts))
            return texts
        else:
            with open(path) as f:
                lines = f.readlines()
            texts = [line.strip() for line in lines if line.strip()]
            logger.info("Loaded %d documents from text corpus", len(texts))
            return texts
    except FileNotFoundError:
        logger.error("Corpus file not found: %s", path)
        raise
    except json.JSONDecodeError as e:
        logger.error("Failed to parse JSON corpus file: %s — %s", path, e)
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Delve Taxonomy Generator — Generate taxonomies from unstructured text data."
    )

    # Input mode
    input_group = parser.add_argument_group("Input source")
    input_group.add_argument(
        "--corpus",
        type=str,
        default=None,
        help="Path to a corpus file (.txt or .json). Required.",
    )
    input_group.add_argument(
        "--taxonomy",
        type=str,
        default=None,
        help="Path to a saved taxonomy JSON to start from (its final iteration "
             "is seeded as the starting taxonomy). Required for --mode test.",
    )

    # Run mode
    mode_group = parser.add_argument_group("Run mode")
    mode_group.add_argument(
        "--mode",
        choices=["train", "test"],
        default=None,
        help="train (default): build/update the taxonomy. test: freeze the "
             "seeded taxonomy's dimensions, classify new documents against "
             "them, append deduplicated new values, and report a delta summary.",
    )
    feedback_group = mode_group.add_mutually_exclusive_group()
    feedback_group.add_argument(
        "--feedback",
        type=str,
        default=None,
        help="Feedback text injected into taxonomy refinement prompts "
             "(update/review). Mutually exclusive with --feedback-file.",
    )
    feedback_group.add_argument(
        "--feedback-file",
        type=str,
        default=None,
        help="Path to a text/markdown file with feedback for taxonomy "
             "refinement. Mutually exclusive with --feedback.",
    )

    # Configuration
    config_group = parser.add_argument_group("Configuration")
    config_group.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to a YAML configuration file. Defaults to ./config.yaml.",
    )

    # Model configuration
    model_group = parser.add_argument_group("Model configuration")
    model_group.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override the main LLM model (format: provider/model-name).",
    )
    model_group.add_argument(
        "--fast-model",
        type=str,
        default=None,
        help="Override the fast LLM model (format: provider/model-name).",
    )

    # Taxonomy
    taxonomy_group = parser.add_argument_group("Taxonomy")
    taxonomy_group.add_argument(
        "--name",
        type=str,
        default=None,
        help="Name for this taxonomy (shown in output and JSON files). Defaults to 'taxonomy'.",
    )
    taxonomy_group.add_argument(
        "-k",
        "--max-clusters",
        type=int,
        default=None,
        help="Override the maximum number of dimensions/categories from the config. "
        "Pass 0 for unlimited (LLM decides).",
    )

    # Output
    output_group = parser.add_argument_group("Output")
    output_group.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to a folder where results will be saved as JSON files. "
        "If the folder does not exist, it will be created.",
    )
    output_group.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress log output — show only rich-formatted results.",
    )

    # Visualization / Reporting
    visualize_group = parser.add_argument_group("Visualization & Reporting")
    standalone_mode = visualize_group.add_mutually_exclusive_group()
    standalone_mode.add_argument(
        "--visualize",
        type=str,
        default=None,
        help="Render a PCA biplot from a saved taxonomy JSON file and exit "
             "(does not run the pipeline). Accepts any *_taxonomy_*.json output. "
             "Mutually exclusive with --report.",
    )
    standalone_mode.add_argument(
        "--report",
        type=str,
        default=None,
        help="Render a self-contained grounded-theory markdown report (narrative "
             "summary, relationship diagram, dimension catalog) from a saved "
             "taxonomy JSON file and exit (does not run the pipeline). Accepts "
             "any *_taxonomy_*.json output. Mutually exclusive with --visualize.",
    )
    standalone_mode.add_argument(
        "--evaluate",
        type=str,
        nargs="+",
        default=None,
        metavar="TAXONOMY",
        help="Evaluate saved taxonomy JSON file(s) and exit (does not run the "
             "pipeline). One file runs the judge scoreboard (optionally with "
             "--corpus to activate the data-grounded coverage criterion); two "
             "or more files run the consistency comparison. Writes an "
             "evaluation_*.json artifact next to the first taxonomy file, or "
             "under --output if given. Mutually exclusive with --visualize "
             "and --report.",
    )
    visualize_group.add_argument(
        "--iteration",
        type=int,
        default=None,
        help="With --visualize or --report: 1-based taxonomy iteration to render. "
             "Default: selected_clusters if present, else the last iteration.",
    )
    visualize_group.add_argument(
        "--axis-positions",
        choices=["auto", "embeddings", "uniform"],
        default="auto",
        help="With --visualize: how values are placed on dimension axes. "
             "'auto' follows the consolidated flag recorded in the file "
             "(uniform when absent), 'embeddings' uses the embedding model, "
             "'uniform' places every value at unit distance.",
    )
    visualize_group.add_argument(
        "--no-auto-report",
        action="store_true",
        default=False,
        help="With --output: skip automatic grounded-theory report generation "
             "(and its narrative LLM call) for this pipeline run.",
    )

    return parser.parse_args()


def _display_taxonomy(
    clusters: list, explanations: list, configuration: Configuration, mode: str = "train"
) -> None:
    """Display the generated taxonomy as a rich table."""
    if not clusters:
        return

    final_taxonomy = clusters[-1]

    table = Table(
        title=f"📊 Generated Taxonomy: {configuration.name}",
        show_lines=True,
        border_style="blue",
        title_style="bold blue",
    )
    table.add_column("#", style="cyan bold", width=4, justify="right")
    table.add_column("Name", style="bold", min_width=20, max_width=50)
    table.add_column("Description", style="dim", min_width=30, max_width=80)
    table.add_column("Values", style="green", min_width=20, max_width=45)

    for cluster in final_taxonomy:
        value_labels = [
            v.get("label", "")
            for v in (cluster.get("values") or [])
            if isinstance(v, dict)
        ]
        values_str = " · ".join(label for label in value_labels if label) or "—"
        table.add_row(
            str(cluster.get("id", "?")),
            cluster.get("name", "Unnamed"),
            cluster.get("description", "No description"),
            values_str,
        )

    console.print()
    console.print(table)

    # Summary footer
    summary = Text()
    summary.append("  Total dimensions: ", style="bold")
    summary.append(str(len(final_taxonomy)), style="cyan bold")
    summary.append("  ·  Iterations: ", style="bold")
    summary.append(str(len(clusters)), style="cyan bold")
    console.print(summary)

    # Show all explanations/rationale across iterations
    if explanations and any(explanations):
        n = len(explanations)
        tail_labels = {}
        if mode == "test":
            # Test mode: seed iteration + aggregation only.
            tail_labels = {0: "Seed"}
            if n >= 2:
                tail_labels[n - 1] = "Aggregation"
        else:
            if n >= 1:
                tail_labels[n - 1] = "Selection"
            if n >= 2:
                tail_labels[n - 2] = "Consolidation"
            if n >= 3:
                tail_labels[n - 3] = "Review"
        parts = []
        for i, explanation in enumerate(explanations):
            if explanation:
                if i in tail_labels:
                    label = tail_labels[i]
                elif mode == "test":
                    label = "Update"
                elif i == 0:
                    label = "Generation"
                else:
                    label = "Update"
                parts.append(f"[bold cyan]{i+1}. {label}:[/bold cyan] {explanation}")
        if parts:
            console.print(Panel(
                "\n\n".join(parts),
                title="[bold blue]💬 Taxonomy Rationale[/bold blue]",
                border_style="blue",
            ))

    console.print()


def _display_taxonomy_tree(clusters: list, documents: list, configuration: Configuration) -> None:
    """Display the taxonomy as a tree with categorized documents as children."""
    if not clusters or not documents:
        return

    final_taxonomy = clusters[-1]
    max_docs = configuration.max_docs_per_category_tree
    preview_length = configuration.content_preview_length

    # Group documents by category
    docs_by_category = {}
    for doc in documents:
        category = (
            getattr(doc, "category", None)
            or (doc.get("category") if isinstance(doc, dict) else None)
            or "N/A"
        )
        docs_by_category.setdefault(category, []).append(doc)

    # Build tree
    tree = Tree(
        f"📂 [bold bright_blue]{configuration.name}[/bold bright_blue]  "
        f"[dim]({len(final_taxonomy)} dimensions, {len(documents)} documents)[/dim]",
        guide_style="dim",
    )

    # Determine which category names are in the taxonomy
    taxonomy_names = {c.get("name", "Unnamed") for c in final_taxonomy}

    # Sort clusters so the fallback category always appears last
    sorted_taxonomy = sorted(
        final_taxonomy,
        key=lambda c: c.get("name", "") == configuration.fallback_category,
    )

    # If fallback category has docs but isn't in the taxonomy, add it as a virtual cluster
    fallback_name = configuration.fallback_category
    fallback_docs = docs_by_category.get(fallback_name, [])
    if fallback_docs and fallback_name not in taxonomy_names:
        sorted_taxonomy.append({
            "name": fallback_name,
            "description": "Fallback category (not part of generated taxonomy)",
        })

    for cluster in sorted_taxonomy:
        name = cluster.get("name", "Unnamed")
        description = cluster.get("description", "")
        category_docs = docs_by_category.get(name, [])

        # Category branch: name + doc count + description
        count_label = f"[dim]({len(category_docs)} docs)[/dim]"
        cat_branch = tree.add(
            f"[bold magenta]{name}[/bold magenta] {count_label}\n  [dim italic]{description}[/dim italic]"
        )

        # Add document children (limited)
        for doc in category_docs[:max_docs]:
            content = (
                getattr(doc, "content", None)
                or (doc.get("content") if isinstance(doc, dict) else None)
                or ""
            )
            score = (
                getattr(doc, "score", None)
                or (doc.get("score") if isinstance(doc, dict) else None)
            )
            content_preview = content[:preview_length].replace("\n", " ").strip()
            if len(content) > preview_length:
                content_preview += "..."
            score_str = f"{score:.2f}" if score is not None else ""
            score_label = f" [cyan]({score_str})[/cyan]" if score_str else ""
            cat_branch.add(f"[dim]📄[/dim] {content_preview}{score_label}")

        # Indicate truncated documents
        remaining = len(category_docs) - max_docs
        if remaining > 0:
            cat_branch.add(f"[dim]... and {remaining} more[/dim]")

    console.print()
    console.print(tree)
    console.print()


def _display_documents(documents: list, configuration: Configuration) -> None:
    """Display document labeling results as a rich table."""
    if not documents:
        return

    preview_length = configuration.content_preview_length
    max_display = configuration.max_displayed_documents

    table = Table(
        title="📄 Document Labeling Results",
        show_lines=False,
        border_style="green",
        title_style="bold green",
    )
    table.add_column("Category", style="magenta bold", min_width=20, max_width=45)
    table.add_column("Score", style="cyan", width=6, justify="center")
    table.add_column("Document Preview", style="dim", min_width=40, max_width=80)

    display_docs = documents[:max_display]
    for doc in display_docs:
        label = (
            getattr(doc, "category", None)
            or (doc.get("category") if isinstance(doc, dict) else None)
        )
        score = (
            getattr(doc, "score", None)
            or (doc.get("score") if isinstance(doc, dict) else None)
        )
        content = (
            getattr(doc, "content", None)
            or (doc.get("content") if isinstance(doc, dict) else None)
            or ""
        )
        content_preview = content[:preview_length]
        score_str = f"{score:.2f}" if score is not None else "—"
        table.add_row(
            label or "N/A",
            score_str,
            content_preview + "..." if len(content_preview) >= preview_length else content_preview,
        )

    console.print()
    console.print(table)

    if len(documents) > max_display:
        console.print(f"  [dim]... and {len(documents) - max_display} more documents.[/dim]")
    console.print()


def _display_messages(messages: list) -> None:
    """Display pipeline messages in a panel."""
    if not messages:
        return

    content_parts = []
    for msg in messages:
        text = msg.content if hasattr(msg, "content") else str(msg)
        content_parts.append(text)

    full_content = "\n".join(content_parts)
    console.print()
    console.print(Panel(full_content, title="[bold yellow]💬 Messages[/bold yellow]", border_style="yellow"))
    console.print()


def _select_clusters_for_visualize(data, iteration):
    """Pick the taxonomy iteration to render from a saved taxonomy JSON.

    Priority: --iteration N (1-based) > selected_clusters > last iteration.
    Returns (clusters, iteration_number).
    """
    if isinstance(data, list):
        # Bare cluster-list file.
        return data, 1

    iterations = data.get("iterations") or []
    if iteration is not None:
        if not 1 <= iteration <= len(iterations):
            raise SystemExit(
                f"--iteration {iteration} out of range (file has {len(iterations)} iterations)"
            )
        return iterations[iteration - 1].get("clusters") or [], iteration

    if data.get("selected_clusters"):
        return data["selected_clusters"], len(iterations) or 1

    if iterations:
        return iterations[-1].get("clusters") or [], len(iterations)

    raise SystemExit("No iterations or selected_clusters found in the taxonomy file")


def _explanation_for_view(data: Any, iteration_arg: Optional[int]) -> str:
    """Resolve the explanation text paired with the rendered view.

    ``_select_clusters_for_visualize`` only returns ``(clusters,
    iteration_number)`` — it does not expose which iteration's
    ``explanation`` matches the resolved view. Both selection cases resolve
    to a specific iteration's explanation directly from the loaded JSON:

    - ``--iteration N`` renders iteration N's own clusters, so its own
      explanation (``iterations[N-1]["explanation"]``) is the correct text.
    - The default view (``selected_clusters`` when present, else the last
      iteration) has no explanation of its own paired 1:1 with it, so it
      falls back to the latest iteration's explanation.

    Returns "" when no matching explanation is available (e.g. a bare
    cluster-list file, or a legacy file whose iteration entries omit
    ``explanation``).
    """
    if not isinstance(data, dict):
        return ""
    iterations = data.get("iterations") or []
    if iteration_arg is not None:
        if 1 <= iteration_arg <= len(iterations):
            return iterations[iteration_arg - 1].get("explanation") or ""
        return ""
    if iterations:
        return iterations[-1].get("explanation") or ""
    return ""


def _dropped_dimensions_for_view(
    data: Any, iteration_arg: Optional[int]
) -> Tuple[List[Any], List[Any]]:
    """Resolve discarded-dimension data for the rendered view, when applicable.

    Discarded-dimension rationale is recorded once, for the single
    dimension-selection step that produced ``selected_clusters`` from the
    taxonomy's final iteration — it only applies when that is the view
    actually being rendered (no explicit ``--iteration`` override) and the
    file recorded it (older files predating this feature have neither key).

    Returns:
        ``(dropped_dimensions, all_clusters_for_name_lookup)`` — both empty
        when discarded-dimension data doesn't apply to this render.
    """
    if iteration_arg is not None or not isinstance(data, dict):
        return [], []
    dropped = data.get("dropped_dimensions") or []
    if not dropped:
        return [], []
    iterations = data.get("iterations") or []
    all_clusters = iterations[-1].get("clusters") or [] if iterations else []
    return dropped, all_clusters


def _load_taxonomy_file(path: str) -> Any:
    """Load and parse a saved taxonomy JSON file, exiting with a clear error on failure."""
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        console.print(f"[bold red]❌ Could not load taxonomy file: {e}[/bold red]")
        raise SystemExit(1)


def _count_values(clusters: Any) -> int:
    """Count total values across a list of cluster dicts."""
    return sum(len(c.get("values") or []) for c in clusters if isinstance(c, dict))


async def _run_visualize(args: argparse.Namespace) -> None:
    """Render a PCA biplot from a saved taxonomy JSON and exit."""
    settings = init_settings(args.config)
    data = _load_taxonomy_file(args.visualize)

    clusters, iteration = _select_clusters_for_visualize(data, args.iteration)

    # 'auto': follow the consolidated flag recorded in the file; legacy files
    # without it fall back to uniform (fully offline, no API calls).
    axis_positions = args.axis_positions
    if axis_positions == "auto" and isinstance(data, dict) and "consolidated" in data:
        axis_positions = "embeddings" if data.get("consolidated") else "uniform"

    name = data.get("taxonomy_name") if isinstance(data, dict) else None
    configurable = {
        "name": name or settings.taxonomy.name,
        # Force visualization on for this invocation; honor --output.
        "visualization_enabled": True,
    }
    # Default to the taxonomy file's own folder rather than the generic
    # output dir, so 2D and 3D renders of the same file always land together.
    configurable["visualization_output_dir"] = (
        args.output if args.output else str(Path(args.visualize).resolve().parent)
    )
    configuration = Configuration.from_runnable_config({"configurable": configurable})

    n_values = _count_values(clusters)
    console.print(Panel(
        f"[bold]File:[/bold] {args.visualize}\n"
        f"[bold]Iteration:[/bold] {iteration}\n"
        f"[bold]Values:[/bold] {n_values}\n"
        f"[bold]Dimensions:[/bold] {len(clusters)}\n"
        f"[bold]Axis positions:[/bold] {axis_positions}",
        title="[bold bright_blue]📊 Taxonomy Biplot[/bold bright_blue]",
        border_style="bright_blue",
    ))

    from taxonomy_generator.visualization import render_taxonomy_biplot

    out_path = await render_taxonomy_biplot(
        configuration, clusters,
        stage="standalone", iteration_index=iteration,
        axis_positions=axis_positions,
    )
    if out_path:
        console.print(f"\n  [bold green]✅ Biplot saved to:[/bold green] {out_path}\n")
    else:
        console.print("\n  [bold red]❌ Biplot could not be rendered — see log output.[/bold red]\n")
        raise SystemExit(1)


async def _run_report(args: argparse.Namespace) -> None:
    """Render a grounded-theory markdown report from a saved taxonomy JSON and exit."""
    settings = init_settings(args.config)
    data = _load_taxonomy_file(args.report)

    clusters, iteration = _select_clusters_for_visualize(data, args.iteration)
    explanation = _explanation_for_view(data, args.iteration)
    dropped_dimensions, all_clusters_for_dropped = _dropped_dimensions_for_view(data, args.iteration)

    name = data.get("taxonomy_name") if isinstance(data, dict) else None
    configurable = {
        "name": name or settings.taxonomy.name,
    }
    # Mirror --visualize: --output (when present) overrides the standalone
    # output directory; --corpus is never read in this mode.
    if args.output:
        configurable["visualization_output_dir"] = args.output
    configuration = Configuration.from_runnable_config({"configurable": configurable})

    n_values = _count_values(clusters)
    console.print(Panel(
        f"[bold]File:[/bold] {args.report}\n"
        f"[bold]Iteration:[/bold] {iteration}\n"
        f"[bold]Values:[/bold] {n_values}\n"
        f"[bold]Dimensions:[/bold] {len(clusters)}",
        title="[bold bright_blue]📄 Grounded Theory Report[/bold bright_blue]",
        border_style="bright_blue",
    ))

    from taxonomy_generator.visualization import resolve_output_dir

    out_dir = resolve_output_dir(configuration)
    out_dir.mkdir(parents=True, exist_ok=True)

    name_prefix = "".join(c if c.isalnum() or c in "-_" else "_" for c in configuration.name)
    name_prefix = f"{name_prefix}_" if name_prefix else ""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"{name_prefix}report_{timestamp}.md"

    stored_evaluation = data.get("evaluation") if isinstance(data, dict) else None
    narrative = await report_renderer.generate_and_write_report(
        clusters, explanation, configuration, out_path,
        dropped_dimensions, all_clusters_for_dropped, stored_evaluation,
    )
    if narrative is None:
        console.print("  [dim]Narrative summary unavailable — proceeding with diagram and catalog only.[/dim]")

    console.print(f"\n  [bold green]✅ Report saved to:[/bold green] {out_path}\n")


def _display_scoreboard(scoreboard: Optional[dict], configuration: Configuration) -> None:
    """Render the evaluation scoreboard as a rich panel (observe-only results)."""
    if not scoreboard:
        return
    if scoreboard.get("unavailable"):
        console.print()
        console.print(Panel(
            f"[dim]Evaluation unavailable: {scoreboard.get('error', 'unknown error')}[/dim]",
            title="[bold bright_magenta]🎯 Taxonomy Evaluation[/bold bright_magenta]",
            border_style="bright_magenta",
        ))
        return

    table = Table(
        show_lines=False,
        border_style="bright_magenta",
        title_style="bold bright_magenta",
        expand=False,
    )
    table.add_column("Criterion", style="bold", max_width=28)
    table.add_column("Score", style="cyan", width=6, justify="center")
    table.add_column("Pass", width=4, justify="center")
    table.add_column("Reason", style="dim", max_width=60)
    for row in scoreboard.get("criteria") or []:
        if row.get("evaluated", True):
            score = row.get("score")
            score_str = f"{score:.2f}" if score is not None else "—"
            passed = row.get("passed")
            pass_str = "✓" if passed else ("✗" if passed is not None else "—")
            reason = (row.get("reason") or "").replace("\n", " ")
        else:
            score_str = "—"
            pass_str = "—"
            reason = "Not evaluated — no documents provided."
        table.add_row(row.get("name", "?"), score_str, pass_str, reason)

    legend_lines = [
        f"• [bold]{row.get('name', '?')}[/bold] — {row.get('description')}"
        for row in scoreboard.get("criteria") or []
        if row.get("description")
    ]
    panel_body = Group(table, "", Text.from_markup("\n".join(legend_lines))) if legend_lines else table

    overall = scoreboard.get("overall")
    overall_str = f"{overall:.2f}" if overall is not None else "—"
    model = scoreboard.get("model") or "default"
    console.print()
    console.print(Panel(
        panel_body,
        title="[bold bright_magenta]🎯 Taxonomy Evaluation[/bold bright_magenta]",
        subtitle=f"[dim]overall {overall_str} · judge {model} · threshold {configuration.evaluation_threshold}[/dim]",
        border_style="bright_magenta",
    ))


def _display_delta_summary(delta: dict, configuration: Configuration) -> None:
    """Render the test-mode delta summary as a rich panel."""
    if not delta:
        return
    new_values = delta.get("new_values") or []
    fallback_docs = delta.get("fallback_documents") or []

    lines: List[str] = []
    if new_values:
        table = Table(
            show_lines=False,
            border_style="cyan",
            title_style="bold cyan",
            expand=False,
        )
        table.add_column("Dimension", style="magenta bold", max_width=40)
        table.add_column("New Value", style="green bold", max_width=40)
        table.add_column("Docs", style="dim", justify="right")
        for nv in new_values:
            table.add_row(
                str(nv.get("dimension", "?")),
                str(nv.get("value", "?")),
                str(len(nv.get("supporting_doc_ids", []))),
            )
        lines.append(table)
    else:
        lines.append("[dim]No new values discovered — all documents fit existing values.[/dim]")

    if fallback_docs:
        lines.append(f"[bold]Fallback ({configuration.fallback_category}) documents:[/bold] {len(fallback_docs)}")
        for fd in fallback_docs:
            preview = (fd.get("preview") or "").replace("\n", " ")
            lines.append(f"  [dim]📄 {preview}[/dim]")

    console.print()
    console.print(Panel(
        "\n".join(str(x) for x in lines),
        title="[bold bright_cyan]🧩 Test-Mode Delta Summary[/bold bright_cyan]",
        border_style="bright_cyan",
    ))


def _display_consistency(comparison: dict) -> None:
    """Render the consistency comparison as a rich panel."""
    if not comparison:
        return
    if comparison.get("unavailable"):
        console.print()
        console.print(Panel(
            f"[dim]Consistency comparison unavailable: {comparison.get('error', 'unknown error')}[/dim]",
            title="[bold bright_magenta]🔁 Taxonomy Consistency[/bold bright_magenta]",
            border_style="bright_magenta",
        ))
        return

    lines: List[str] = []
    agreement = comparison.get("agreement")
    if agreement is not None:
        lines.append(f"[bold]Agreement:[/bold] [cyan]{agreement:.2%}[/cyan] "
                     f"([dim]aligned dimensions / max per-file dimensions[/dim])")
    else:
        lines.append("[dim]Agreement: n/a[/dim]")

    recurring = comparison.get("recurring") or []
    lines.append(f"[bold]Recurring dimensions:[/bold] {len(recurring)}")
    for group in recurring:
        names = ", ".join(
            f"{d.get('name', '?')} [dim](file {d.get('file', '?')})[/dim]"
            for d in group.get("dimensions") or []
        )
        lines.append(f"  • {names}")

    one_offs = comparison.get("one_offs") or []
    lines.append(f"[bold]One-off dimensions:[/bold] {len(one_offs)}")
    for dim in one_offs:
        lines.append(f"  • {dim.get('name', '?')} [dim](file {dim.get('file', '?')})[/dim]")

    if comparison.get("fallback"):
        lines.append(f"[dim]Alignment fallback in effect: {comparison['fallback']}[/dim]")
    if comparison.get("adjudicated_pairs"):
        lines.append(f"[dim]Borderline pairs adjudicated by judge: {comparison['adjudicated_pairs']}[/dim]")

    console.print()
    console.print(Panel(
        "\n".join(lines),
        title="[bold bright_magenta]🔁 Taxonomy Consistency[/bold bright_magenta]",
        border_style="bright_magenta",
    ))


async def _run_evaluate(args: argparse.Namespace) -> None:
    """Score or compare saved taxonomy JSONs and exit."""
    init_settings(args.config)
    files = args.evaluate

    configurable: dict = {}
    if args.output:
        configurable["visualization_output_dir"] = args.output
    configuration = Configuration.from_runnable_config({"configurable": configurable} or None)

    if args.output:
        from taxonomy_generator.visualization import resolve_output_dir

        out_dir = resolve_output_dir(configuration)
    else:
        # Default to the evaluated taxonomy's own folder rather than the
        # pipeline's generic output dir, so the report sits next to what it scores.
        out_dir = Path(files[0]).resolve().parent
    out_dir.mkdir(parents=True, exist_ok=True)
    name_prefix = "".join(c if c.isalnum() or c in "-_" else "_" for c in configuration.name)
    name_prefix = f"{name_prefix}_" if name_prefix else ""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if len(files) == 1:
        # Scoreboard mode - optionally with --corpus for the coverage tier.
        data = _load_taxonomy_file(files[0])
        clusters, iteration = _select_clusters_for_visualize(data, args.iteration)
        documents: List[dict] = []
        if args.corpus:
            texts = load_corpus(args.corpus)
            documents = [{"content": t} for t in texts]
            console.print(f"[dim]Loaded {len(documents)} documents for the coverage criterion.[/dim]")

        n_values = _count_values(clusters)
        console.print(Panel(
            f"[bold]File:[/bold] {files[0]}\n"
            f"[bold]Iteration:[/bold] {iteration}\n"
            f"[bold]Values:[/bold] {n_values}\n"
            f"[bold]Dimensions:[/bold] {len(clusters)}\n"
            f"[bold]Corpus:[/bold] {args.corpus or 'none (coverage criterion marked not evaluated)'}",
            title="[bold bright_magenta]🎯 Taxonomy Evaluation[/bold bright_magenta]",
            border_style="bright_magenta",
        ))

        from taxonomy_generator.evaluation.runner import run_scoreboard

        scoreboard = await run_scoreboard(clusters, documents, configuration)
        _display_scoreboard(scoreboard, configuration)
        if scoreboard.get("unavailable"):
            raise SystemExit(1)

        artifact = {"taxonomy_name": configuration.name, "source_file": files[0],
                    "iteration": iteration, "scoreboard": scoreboard}
    else:
        # Consistency mode - compare two or more saved taxonomies.
        if args.corpus:
            console.print("[dim]--corpus is ignored in multi-file consistency mode.[/dim]")
        views = []
        for path in files:
            data = _load_taxonomy_file(path)
            clusters, _ = _select_clusters_for_visualize(data, args.iteration)
            views.append(clusters)
        console.print(Panel(
            f"[bold]Files:[/bold] {len(views)}",
            title="[bold bright_magenta]🔁 Taxonomy Consistency[/bold bright_magenta]",
            border_style="bright_magenta",
        ))

        from taxonomy_generator.evaluation.consistency import compare_taxonomies

        comparison = await compare_taxonomies(views, configuration)
        _display_consistency(comparison)
        artifact = {"taxonomy_name": configuration.name, "source_files": files,
                    "consistency": comparison}

    out_path = out_dir / f"{name_prefix}evaluation_{timestamp}.json"
    with open(out_path, "w") as f:
        json.dump(artifact, f, indent=2, ensure_ascii=False)
    console.print(f"\n  [bold green]✅ Evaluation saved to:[/bold green] {out_path}\n")


async def run(args: argparse.Namespace) -> None:
    if not args.corpus:
        logger.error("--corpus is required")
        console.print("[bold red]❌ Error: --corpus is required. Provide a path to a .txt or .json corpus file.[/bold red]")
        sys.exit(1)

    # Load settings from YAML
    settings = init_settings(args.config)

    logger.info("Using corpus file mode: %s", args.corpus)
    texts = load_corpus(args.corpus)
    logger.info("Loaded %d documents from corpus", len(texts))
    console.print(Panel(
        f"[bold]File:[/bold] {args.corpus}\n[bold]Documents:[/bold] {len(texts)}",
        title="[bold cyan]📂 Loading Corpus[/bold cyan]",
        border_style="cyan",
    ))
    invoke_input = {"documents": strings_to_docs(texts)}

    # Run mode / seeding / external feedback (CLI over config).
    mode = args.mode or settings.pipeline.mode
    taxonomy_input = args.taxonomy or settings.pipeline.taxonomy_input
    if mode == "test" and not taxonomy_input:
        console.print("[bold red]❌ Error: --mode test requires --taxonomy (a saved taxonomy JSON).[/bold red]")
        sys.exit(1)
    feedback_text = _resolve_feedback_text(args, settings)
    if feedback_text:
        from taxonomy_generator.state import UserFeedback
        invoke_input["external_feedback"] = UserFeedback(
            decision="modify",
            explanation="External feedback provided for this run (CLI flag/file or config).",
            feedback=feedback_text,
        )
        logger.info("External feedback injected (%d chars)", len(feedback_text))

    # Build config overrides from CLI flags
    configurable = {}
    if mode:
        configurable["mode"] = mode
    if taxonomy_input:
        configurable["taxonomy_input"] = taxonomy_input
    if args.model:
        configurable["model"] = args.model
        logger.info("Overriding main model: %s", args.model)
    if args.fast_model:
        configurable["fast_llm"] = args.fast_llm
        logger.info("Overriding fast model: %s", args.fast_model)
    if args.name:
        configurable["name"] = args.name
        logger.info("Overriding taxonomy name: %s", args.name)
    if args.max_clusters is not None:
        # 0 means unlimited (None internally); any positive int caps the count
        configurable["max_num_clusters"] = args.max_clusters if args.max_clusters > 0 else None
        logger.info("Overriding max dimensions: %s", configurable["max_num_clusters"])
    # Charts and PCA-vector CSVs otherwise default to config.yaml's
    # default_output_dir ("output"), ignoring --output entirely. Default them
    # to the corpus's own folder instead, so they sit next to its input.
    configurable["visualization_output_dir"] = (
        args.output if args.output else str(Path(args.corpus).resolve().parent)
    )
    config = {"configurable": configurable} if configurable else {}

    # Resolve effective configuration for display
    effective_config = Configuration.from_runnable_config(config or None)

    # Show model info (always visible, even in quiet mode)
    taxonomy_name = effective_config.name
    max_dims_str = str(effective_config.max_num_clusters) if effective_config.max_num_clusters else "unlimited (LLM decides)"
    seed_info = ""
    if taxonomy_input:
        seed_dimensions = "unknown"
        try:
            from taxonomy_generator.utils import load_seed_taxonomy
            seed_dimensions = str(len(load_seed_taxonomy(taxonomy_input)))
        except ValueError as e:
            console.print(f"[bold red]❌ Error loading --taxonomy file: {e}[/bold red]")
            sys.exit(1)
        seed_info = f"[dim]Seed:[/dim] [cyan]{taxonomy_input}[/cyan] [dim]({seed_dimensions} dimensions)[/dim]\n"

    console.print(Panel(
        f"[bold]Starting taxonomy generation pipeline...[/bold]\n\n"
        f"[dim]Taxonomy:[/dim] [cyan]{taxonomy_name}[/cyan]\n"
        f"[dim]Mode:[/dim] [cyan]{mode}[/cyan]\n"
        f"{seed_info}"
        f"[dim]Max dimensions:[/dim] [cyan]{max_dims_str}[/cyan]\n"
        f"[dim]Model:[/dim] [cyan]{effective_config.model}[/cyan]\n"
        f"[dim]Fast LLM:[/dim] [cyan]{effective_config.fast_llm}[/cyan]",
        title="[bold bright_blue]🚀 Delve[/bold bright_blue]",
        border_style="bright_blue",
    ))
    logger.info("Starting taxonomy generation pipeline (mode=%s)", mode)

    # Export graph diagram when not in quiet mode
    if not args.quiet:
        try:
            png_bytes = graph.get_graph().draw_mermaid_png()
            graph_dir = Path(args.output) if args.output else Path(effective_config.default_output_dir)
            graph_dir.mkdir(parents=True, exist_ok=True)
            graph_path = graph_dir / effective_config.graph_filename
            with open(graph_path, "wb") as f:
                f.write(png_bytes)
            logger.info("Graph diagram saved to: %s", graph_path)
        except Exception as e:
            logger.warning("Could not export graph diagram: %s", e)

    # ── Stream pipeline execution with step-by-step display ──────────
    result: dict = {}
    clusters: list = []
    selected_clusters: list = []
    dropped_dimensions: list = []
    saturation_history: list = []
    explanations: list = []
    documents: list = []
    messages: list = []
    delta_summary: Optional[dict] = None
    evaluation: Optional[dict] = None
    total_minibatches = None

    # Token tracking callback
    token_tracker = TokenTracker()
    run_config = dict(config) if config else {}
    run_config["callbacks"] = [token_tracker]

    # Timing
    start_time = time.monotonic()

    async for event in graph.astream(invoke_input, config=run_config, stream_mode="updates"):
        for node_name, node_output in event.items():
            # Display the step to the user
            emoji, label = STEP_INFO.get(node_name, ("⚙️", node_name))

            # Track minibatch count for update_taxonomy progress display
            if node_name == "get_minibatches":
                minibatches = node_output.get("minibatches", [])
                if minibatches:
                    total_minibatches = len(minibatches)

            # Add iteration info for generate/update_taxonomy steps
            detail = ""
            if node_name == "generate_taxonomy":
                if total_minibatches is not None:
                    detail = f" (minibatch 1/{total_minibatches})"
            elif node_name == "update_taxonomy":
                if total_minibatches is not None:
                    iteration = len(clusters)  # clusters before this update
                    detail = f" (minibatch {iteration + 1}/{total_minibatches})"
                else:
                    detail = f" (iteration {len(clusters) + 1})"

            console.print(
                f"  [bold]{emoji} {label}{detail}[/bold]  [dim]✓[/dim]"
            )

            # Accumulate state updates
            if node_output:
                if "clusters" in node_output:
                    clusters.extend(node_output["clusters"])
                if "selected_clusters" in node_output:
                    selected_clusters = node_output["selected_clusters"]
                if "dropped_dimensions" in node_output:
                    dropped_dimensions = node_output["dropped_dimensions"]
                if "delta_summary" in node_output:
                    delta_summary = node_output["delta_summary"]
                if "evaluation" in node_output:
                    evaluation = node_output["evaluation"]
                if "saturation_history" in node_output:
                    saturation_history.extend(node_output["saturation_history"])
                if "explanations" in node_output:
                    explanations.extend(node_output["explanations"])
                if "documents" in node_output:
                    documents = node_output["documents"]
                if "messages" in node_output:
                    messages.extend(node_output["messages"])

                # Keep a reference to the full output for any fields we might need
                result.update(node_output)

    logger.info("Taxonomy generation pipeline completed")

    # Display elapsed time and token usage
    elapsed = time.monotonic() - start_time
    elapsed_str = _format_elapsed(elapsed)
    if token_tracker.total_tokens > 0:
        token_str = (
            f"[cyan]{token_tracker.total_tokens:,}[/cyan] tokens "
            f"([dim]{token_tracker.prompt_tokens:,} prompt + "
            f"{token_tracker.completion_tokens:,} completion[/dim])"
        )
    else:
        token_str = "[dim]N/A[/dim]"
    console.print(
        f"\n  ⏱️  [bold]Pipeline completed in[/bold] [cyan]{elapsed_str}[/cyan]"
        f"  ·  🪙 {token_str}"
    )

    if clusters:
        logger.info("Generated taxonomy with %d categories (%d iterations)", len(clusters[-1]), len(clusters))
        _display_taxonomy(clusters, explanations, effective_config, mode=mode)

    if delta_summary is not None:
        _display_delta_summary(delta_summary, effective_config)

    if evaluation is not None and not evaluation.get("unavailable"):
        _display_scoreboard(evaluation, effective_config)

    if documents:
        logger.info("Labeling results: %d documents categorized", len(documents))
        _display_documents(documents, effective_config)

    # Display taxonomy tree (categories with their documents)
    if clusters and documents:
        _display_taxonomy_tree(clusters, documents, effective_config)

    if messages:
        _display_messages(messages)

    # Save results to output folder if requested
    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Saving results to output folder: %s", output_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Sanitize taxonomy name for use as filename prefix
        name_prefix = "".join(c if c.isalnum() or c in "-_" else "_" for c in effective_config.name)
        name_prefix = f"{name_prefix}_"

        # Serialize documents
        docs_data = []
        for doc in documents:
            if hasattr(doc, "__dict__") and not isinstance(doc, dict):
                docs_data.append({
                    "id": getattr(doc, "id", ""),
                    "content": getattr(doc, "content", ""),
                    "summary": getattr(doc, "summary", ""),
                    "explanation": getattr(doc, "explanation", ""),
                    "category": getattr(doc, "category", ""),
                    "value": getattr(doc, "value", None),
                    "score": getattr(doc, "score", None),
                })
            else:
                docs_data.append(doc)

        # Save documents
        docs_output = {"taxonomy_name": effective_config.name, "documents": docs_data}
        docs_path = output_dir / f"{name_prefix}documents_{timestamp}.json"
        with open(docs_path, "w") as f:
            json.dump(docs_output, f, indent=2, ensure_ascii=False)
        logger.info("Documents saved to: %s", docs_path)

        # Save taxonomy (all iterations paired with explanations)
        taxonomy_data = {
            "taxonomy_name": effective_config.name,
            "consolidated": bool(effective_config.consolidate_values),
            "iterations": [],
        }
        if saturation_history:
            taxonomy_data["saturation_history"] = saturation_history
        if selected_clusters:
            taxonomy_data["selected_clusters"] = selected_clusters[-1]
        if dropped_dimensions:
            taxonomy_data["dropped_dimensions"] = dropped_dimensions
        if delta_summary is not None:
            taxonomy_data["delta_summary"] = delta_summary
        if evaluation is not None and not evaluation.get("unavailable"):
            taxonomy_data["evaluation"] = evaluation
        for i, iteration_clusters in enumerate(clusters):
            entry = {
                "explanation": explanations[i] if i < len(explanations) else "",
                "clusters": iteration_clusters,
            }
            taxonomy_data["iterations"].append(entry)
        taxonomy_path = output_dir / f"{name_prefix}taxonomy_{timestamp}.json"
        with open(taxonomy_path, "w") as f:
            json.dump(taxonomy_data, f, indent=2, ensure_ascii=False)
        logger.info("Taxonomy saved to: %s", taxonomy_path)

        # Save messages
        msgs_data = {"taxonomy_name": effective_config.name, "messages": []}
        for msg in messages:
            msgs_data["messages"].append({
                "type": type(msg).__name__,
                "content": msg.content if hasattr(msg, "content") else str(msg),
            })
        msgs_path = output_dir / f"{name_prefix}messages_{timestamp}.json"
        with open(msgs_path, "w") as f:
            json.dump(msgs_data, f, indent=2, ensure_ascii=False)
        logger.info("Messages saved to: %s", msgs_path)

        # Save taxonomy tree (clusters with their categorized documents)
        if clusters and documents:
            final_taxonomy = clusters[-1]

            # Group documents by category
            docs_by_cat = {}
            for doc in documents:
                cat = (
                    getattr(doc, "category", None)
                    or (doc.get("category") if isinstance(doc, dict) else None)
                    or "N/A"
                )
                docs_by_cat.setdefault(cat, []).append(doc)

            # Sort clusters so fallback appears last; add virtual fallback if needed
            taxonomy_names = {c.get("name", "Unnamed") for c in final_taxonomy}
            sorted_clusters = sorted(
                final_taxonomy,
                key=lambda c: c.get("name", "") == effective_config.fallback_category,
            )
            fallback_name = effective_config.fallback_category
            if docs_by_cat.get(fallback_name) and fallback_name not in taxonomy_names:
                sorted_clusters.append({
                    "name": fallback_name,
                    "description": "Fallback category (not part of generated taxonomy)",
                })

            tree_data = {"taxonomy_name": effective_config.name, "clusters": []}
            for cluster in sorted_clusters:
                name = cluster.get("name", "Unnamed")
                cat_docs = docs_by_cat.get(name, [])
                tree_data["clusters"].append({
                    "id": cluster.get("id"),
                    "name": name,
                    "description": cluster.get("description", ""),
                    "documents": [
                        {
                            "id": (
                                getattr(d, "id", None)
                                or (d.get("id") if isinstance(d, dict) else None)
                                or ""
                            ),
                            "content": (
                                getattr(d, "content", None)
                                or (d.get("content") if isinstance(d, dict) else None)
                                or ""
                            ),
                            "score": (
                                getattr(d, "score", None)
                                or (d.get("score") if isinstance(d, dict) else None)
                            ),
                        }
                        for d in cat_docs
                    ],
                })

            tree_path = output_dir / f"{name_prefix}clusters_{timestamp}.json"
            with open(tree_path, "w") as f:
                json.dump(tree_data, f, indent=2, ensure_ascii=False)
            logger.info("Taxonomy tree saved to: %s", tree_path)
        else:
            tree_path = None

        # Generate the grounded-theory markdown report automatically, unless
        # the operator opted out. Reuses the just-built taxonomy_data — it
        # already has the exact {"iterations": [...], "selected_clusters":
        # [...]} shape _select_clusters_for_visualize and
        # _explanation_for_view expect from a loaded taxonomy JSON, so the
        # same view-precedence helpers apply here unmodified.
        report_path = None
        if not args.no_auto_report:
            if taxonomy_data["iterations"] or taxonomy_data.get("selected_clusters"):
                try:
                    report_clusters, report_iteration = _select_clusters_for_visualize(
                        taxonomy_data, args.iteration
                    )
                except SystemExit as e:
                    # The four core --output artifacts are already saved at this
                    # point; an out-of-range --iteration should degrade the
                    # report step gracefully rather than aborting a successful run.
                    logger.warning("Skipping automatic report generation: %s", e)
                else:
                    report_explanation = _explanation_for_view(taxonomy_data, args.iteration)
                    report_dropped, report_all_clusters = _dropped_dimensions_for_view(
                        taxonomy_data, args.iteration
                    )
                    report_path = output_dir / f"{name_prefix}report_{timestamp}.md"
                    narrative = await report_renderer.generate_and_write_report(
                        report_clusters, report_explanation, effective_config, report_path,
                        report_dropped, report_all_clusters, evaluation,
                    )
                    if narrative is None:
                        logger.info("Narrative summary unavailable — report will omit it.")
                    logger.info(
                        "Report saved to: %s (iteration %s)", report_path, report_iteration
                    )
            else:
                logger.info("No taxonomy generated — skipping automatic report generation.")

        # Results panel
        saved_lines = (
            f"[bold green]Documents:[/bold green]      {docs_path}\n"
            f"[bold green]Taxonomy:[/bold green]       {taxonomy_path}\n"
            f"[bold green]Messages:[/bold green]        {msgs_path}"
        )
        if tree_path:
            saved_lines += f"\n[bold green]Clusters:[/bold green]       {tree_path}"
        if report_path:
            saved_lines += f"\n[bold green]Report:[/bold green]         {report_path}"
        console.print(Panel(
            saved_lines,
            title="[bold green]💾 Results Saved[/bold green]",
            border_style="green",
        ))

    console.print("\n[bold bright_green]✅ Done.[/bold bright_green]\n")


def main() -> None:
    load_dotenv()

    args = parse_args()

    # Configure logging
    log_level = logging.WARNING if args.quiet else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Suppress noisy HTTP request logs from httpx/openai
    logging.getLogger("httpx").setLevel(logging.WARNING)

    # Standalone biplot mode — render from a saved taxonomy JSON and exit.
    if args.visualize:
        asyncio.run(_run_visualize(args))
        return

    # Standalone report mode — render a markdown report from a saved taxonomy JSON and exit.
    if args.report:
        asyncio.run(_run_report(args))
        return

    # Standalone evaluation mode — score/compare saved taxonomy JSONs and exit.
    if args.evaluate:
        asyncio.run(_run_evaluate(args))
        return

    logger.info("Delve Taxonomy Generator starting")
    asyncio.run(run(args))


if __name__ == "__main__":
    main()