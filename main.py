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
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from taxonomy_generator import graph, strings_to_docs
from taxonomy_generator.configuration import Configuration, init_settings

logger = logging.getLogger(__name__)
console = Console()


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
        title="📊 Generated Taxonomy",
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
    table.add_column("Document Preview", style="dim", min_width=40, max_width=80)

    display_docs = documents[:max_display]
    for doc in display_docs:
        label = (
            getattr(doc, "category", None)
            or (doc.get("category") if isinstance(doc, dict) else None)
        )
        content = (
            getattr(doc, "content", None)
            or (doc.get("content") if isinstance(doc, dict) else None)
            or ""
        )
        content_preview = content[:preview_length]
        table.add_row(
            label or "N/A",
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
    config = {"configurable": configurable} if configurable else {}

    # Resolve effective configuration for display
    effective_config = Configuration.from_runnable_config(config or None)

    # Show model info (always visible, even in quiet mode)
    console.print(Panel(
        f"[bold]Starting taxonomy generation pipeline...[/bold]\n\n"
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

    result = await graph.ainvoke(invoke_input, config=config or None)
    logger.info("Taxonomy generation pipeline completed")

    # Display results
    clusters = result.get("clusters", [])
    explanations = result.get("explanations", [])
    documents = result.get("documents", [])
    messages = result.get("messages", [])

    if clusters:
        logger.info("Generated taxonomy with %d categories (%d iterations)", len(clusters[-1]), len(clusters))
        _display_taxonomy(clusters, explanations, effective_config)

    if documents:
        logger.info("Labeling results: %d documents categorized", len(documents))
        _display_documents(documents, effective_config)

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
                })
            else:
                docs_data.append(doc)

        # Save documents
        docs_path = output_dir / f"documents_{timestamp}.json"
        with open(docs_path, "w") as f:
            json.dump(docs_data, f, indent=2, ensure_ascii=False)
        logger.info("Documents saved to: %s", docs_path)

        # Save taxonomy (all iterations paired with explanations)
        taxonomy_data = []
        for i, iteration_clusters in enumerate(clusters):
            entry = {
                "explanation": explanations[i] if i < len(explanations) else "",
                "clusters": iteration_clusters,
            }
            taxonomy_data.append(entry)
        taxonomy_path = output_dir / f"taxonomy_{timestamp}.json"
        with open(taxonomy_path, "w") as f:
            json.dump(taxonomy_data, f, indent=2, ensure_ascii=False)
        logger.info("Taxonomy saved to: %s", taxonomy_path)

        # Save messages
        msgs_data = []
        for msg in messages:
            msgs_data.append({
                "type": type(msg).__name__,
                "content": msg.content if hasattr(msg, "content") else str(msg),
            })
        msgs_path = output_dir / f"messages_{timestamp}.json"
        with open(msgs_path, "w") as f:
            json.dump(msgs_data, f, indent=2, ensure_ascii=False)
        logger.info("Messages saved to: %s", msgs_path)

        console.print(Panel(
            f"[bold green]Documents:[/bold green] {docs_path}\n"
            f"[bold green]Taxonomy:[/bold green]  {taxonomy_path}\n"
            f"[bold green]Messages:[/bold green]   {msgs_path}",
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