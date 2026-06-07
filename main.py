"""Delve Taxonomy Generator — CLI entry point.

Usage:
    # From a corpus file (one document per line for .txt, or JSON array for .json):
    python main.py --corpus my_corpus.txt
    python main.py --corpus documents.json

    # With custom model:
    python main.py --corpus my_corpus.txt --model openai/gpt-5.4-nano

    # With custom config file:
    python main.py --corpus my_corpus.txt --config /path/to/config.yaml
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.callbacks import BaseCallbackHandler
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from taxonomy_generator import graph, strings_to_docs
from taxonomy_generator.configuration import Configuration, init_settings

logger = logging.getLogger(__name__)
console = Console()

# ── Pipeline step display configuration ──────────────────────────────────
STEP_INFO = {
    "load_corpus": ("📂", "Loading corpus"),
    "summarize": ("📝", "Generating summaries"),
    "get_minibatches": ("📦", "Creating minibatches"),
    "generate_taxonomy": ("🧠", "Generating initial taxonomy"),
    "update_taxonomy": ("🔄", "Updating taxonomy"),
    "review_taxonomy": ("🔍", "Reviewing taxonomy"),
    "label_documents": ("🏷️", "Labeling documents"),
}


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

    return parser.parse_args()


def _display_taxonomy(clusters: list, explanations: list, configuration: Configuration) -> None:
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

    for cluster in final_taxonomy:
        table.add_row(
            str(cluster.get("id", "?")),
            cluster.get("name", "Unnamed"),
            cluster.get("description", "No description"),
        )

    console.print()
    console.print(table)

    # Summary footer
    summary = Text()
    summary.append("  Total categories: ", style="bold")
    summary.append(str(len(final_taxonomy)), style="cyan bold")
    summary.append("  ·  Iterations: ", style="bold")
    summary.append(str(len(clusters)), style="cyan bold")
    console.print(summary)

    # Show all explanations/rationale across iterations
    if explanations and any(explanations):
        parts = []
        for i, explanation in enumerate(explanations):
            if explanation:
                if i == 0:
                    label = "Generation"
                elif i == len(explanations) - 1:
                    label = "Review"
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
        f"[dim]({len(final_taxonomy)} categories, {len(documents)} documents)[/dim]",
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

    # Build config overrides from CLI flags
    configurable = {}
    if args.model:
        configurable["model"] = args.model
        logger.info("Overriding main model: %s", args.model)
    if args.fast_model:
        configurable["fast_llm"] = args.fast_model
        logger.info("Overriding fast model: %s", args.fast_model)
    if args.name:
        configurable["name"] = args.name
        logger.info("Overriding taxonomy name: %s", args.name)
    config = {"configurable": configurable} if configurable else {}

    # Resolve effective configuration for display
    effective_config = Configuration.from_runnable_config(config or None)

    # Show model info (always visible, even in quiet mode)
    taxonomy_name = effective_config.name
    console.print(Panel(
        f"[bold]Starting taxonomy generation pipeline...[/bold]\n\n"
        f"[dim]Taxonomy:[/dim] [cyan]{taxonomy_name}[/cyan]\n"
        f"[dim]Model:[/dim] [cyan]{effective_config.model}[/cyan]\n"
        f"[dim]Fast LLM:[/dim] [cyan]{effective_config.fast_llm}[/cyan]",
        title="[bold bright_blue]🚀 Delve[/bold bright_blue]",
        border_style="bright_blue",
    ))
    logger.info("Starting taxonomy generation pipeline")

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
    explanations: list = []
    documents: list = []
    messages: list = []
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
        _display_taxonomy(clusters, explanations, effective_config)

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
                    "score": getattr(doc, "score", None),
                })
            else:
                docs_data.append(doc)

        # Save documents
        docs_output = {"taxonomy_name": effective_config.name, "documents": docs_data}
        docs_path = output_dir / f"documents_{timestamp}.json"
        with open(docs_path, "w") as f:
            json.dump(docs_output, f, indent=2, ensure_ascii=False)
        logger.info("Documents saved to: %s", docs_path)

        # Save taxonomy (all iterations paired with explanations)
        taxonomy_data = {"taxonomy_name": effective_config.name, "iterations": []}
        for i, iteration_clusters in enumerate(clusters):
            entry = {
                "explanation": explanations[i] if i < len(explanations) else "",
                "clusters": iteration_clusters,
            }
            taxonomy_data["iterations"].append(entry)
        taxonomy_path = output_dir / f"taxonomy_{timestamp}.json"
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
        msgs_path = output_dir / f"messages_{timestamp}.json"
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

            tree_path = output_dir / f"clusters_{timestamp}.json"
            with open(tree_path, "w") as f:
                json.dump(tree_data, f, indent=2, ensure_ascii=False)
            logger.info("Taxonomy tree saved to: %s", tree_path)
        else:
            tree_path = None

        # Results panel
        saved_lines = (
            f"[bold green]Documents:[/bold green]      {docs_path}\n"
            f"[bold green]Taxonomy:[/bold green]       {taxonomy_path}\n"
            f"[bold green]Messages:[/bold green]        {msgs_path}"
        )
        if tree_path:
            saved_lines += f"\n[bold green]Clusters:[/bold green]       {tree_path}"
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
    logger.info("Delve Taxonomy Generator starting")
    asyncio.run(run(args))


if __name__ == "__main__":
    main()