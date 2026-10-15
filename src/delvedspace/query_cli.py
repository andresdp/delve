"""``ddspace query``: read-only questions over the current wiki (JSON for agents, ``--table`` for people)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import typer
from rich.console import Console
from rich.markup import escape

from delvedspace import runs, ui
from delvedspace.workspace import Workspace, WorkspaceError, read_json
from taxonomy_generator.wiki import query as q

app = typer.Typer(
    help="Read-only questions over the current wiki. JSON by default (for agents); --table for people.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
console = Console()
err = Console(stderr=True)

GraphOpt = typer.Option(None, "--graph", help="An export folder or its raw/graph.json (default: this workspace's).")
TableOpt = typer.Option(False, "--table", help="Print a table instead of JSON.")


def _graph_path(graph: Optional[Path]) -> Path:
    if graph is not None:
        return graph / "raw" / "graph.json" if graph.is_dir() else graph
    try:
        return Workspace.find().root / "raw" / "graph.json"
    except WorkspaceError as exc:
        err.print(f"[red]✗ Error:[/red] {exc} Or pass --graph <export folder>.")
        raise typer.Exit(1)


def _run(graph: Optional[Path], table: bool, fn: Callable[[q.Graph], Any],
         render: Callable[[Any], None]) -> None:
    try:
        data = fn(q.load(_graph_path(graph)))
    except q.NotFound as exc:
        err.print(f"[red]✗ Not found:[/red] {escape(str(exc))}")
        if not table:
            typer.echo(json.dumps({"error": str(exc), "candidates": exc.candidates}, indent=2, ensure_ascii=False))
        raise typer.Exit(2)
    except q.QueryError as exc:
        err.print(f"[red]✗ Error:[/red] {escape(str(exc))}")
        raise typer.Exit(1)
    if table:
        render(data)
    else:
        typer.echo(json.dumps(data, indent=2, ensure_ascii=False))


def _table(title: str, columns: List[str], rows: List[List[Any]]) -> None:
    numeric = {c for c in columns if c in ("values", "outcomes", "relations", "sources", "passages")}
    ui.table(escape(title), columns, [[escape("" if x is None else str(x)) for x in r] for r in rows],
             right=sorted(numeric))


def _evidence_text(ev: Dict[str, Any]) -> str:
    return f"{ev.get('sources', '?')} src, {ev.get('documents', '?')} docs"


@app.command()
def info(graph: Optional[Path] = GraphOpt, table: bool = TableOpt) -> None:
    """Show the run, use case, core rule and counts."""
    def render(d):
        _table(f"{d['name']} (run {d['run']}, {d['view']} view)", ["", ""],
               [["use case", d["use_case"]], ["core rule", d["core_rule"]]]
               + [[k.replace("_", " "), v] for k, v in d["counts"].items()])
    _run(graph, table, q.info, render)


@app.command()
def dims(core: bool = typer.Option(False, "--core", help="Only core dimensions."),
         graph: Optional[Path] = GraphOpt, table: bool = TableOpt) -> None:
    """List the dimensions with value counts, evidence, exclusivity, relations and the core flag."""
    _run(graph, table, lambda g: q.dims(g, core_only=core), lambda rows: _table(
        "Dimensions", ["id", "dimension", "core", "values", "outcomes", "evidence", "exclusivity", "relations"],
        [[d["id"], d["label"], "yes" if d["core"] else "", d["values"], d["outcomes"], _evidence_text(d["evidence"]),
          "" if d.get("exclusivity") is None else f"{d['exclusivity']:.2f}", d["relations"]] for d in rows]))


@app.command()
def show(node: str = typer.Argument(..., help="Id, slug or label of any node."),
         graph: Optional[Path] = GraphOpt, table: bool = TableOpt) -> None:
    """Show one node: its fields and its neighbors by edge type."""
    def render(d):
        n = d["node"]
        _table(f"{n.get('kind')}: {n.get('label')} ({n.get('id')})", ["field", "value"],
               [[k, v] for k, v in n.items() if k not in ("passages",)]
               + ([["passages", ", ".join(p["doc"] for p in n["passages"])]] if n.get("passages") else []))
        for etype, items in d["neighbors"].items():
            _table(etype, ["id", "label", "direction", "detail"],
                   [[i["id"], i["label"], i["direction"],
                     i.get("reading") or i.get("stance") or i.get("weight") or ""] for i in items])
    _run(graph, table, lambda g: q.show(g, node), render)


@app.command("values")
def values_cmd(dimension: str = typer.Argument(..., help="Id, slug or label of a dimension."),
               status: Optional[str] = typer.Option(None, "--status",
                                                    help="accepted, rejected, mixed or outcome."),
               graph: Optional[Path] = GraphOpt, table: bool = TableOpt) -> None:
    """List a dimension's values (alternatives and outcomes) with their support."""
    _run(graph, table, lambda g: q.values(g, dimension, status), lambda d: _table(
        f"Values of {d['dimension']['label']}", ["id", "value", "status", "sources", "passages", "includes"],
        [[v["id"], v["label"], v["status"], v["sources"], v["passages"], "; ".join(v.get("includes") or [])]
         for v in d["values"]]))


@app.command()
def evidence(value: str = typer.Argument(..., help="Id, slug or label of a value."),
             stance: Optional[str] = typer.Option(None, "--stance", help="accepts, rejects or supports."),
             quotes: bool = typer.Option(False, "--quotes", help="Include the passage text (from corpus.json)."),
             corpus: Optional[Path] = typer.Option(None, "--corpus", help="Corpus JSON for --quotes."),
             graph: Optional[Path] = GraphOpt, table: bool = TableOpt) -> None:
    """List the passages that support a value, by source, with each passage's stance."""
    texts = _corpus_for_quotes(corpus, graph) if quotes else None

    def render(d):
        v = d["value"]
        rows = [[s["label"], p["id"], p["stance"]] + ([p.get("text", "")] if texts is not None else [])
                for s in d["sources"] for p in s["passages"]]
        _table(f"{v['label']} ({v['status']}) in {v['dimension']}",
               ["source", "passage", "stance"] + (["text"] if texts is not None else []), rows)
    _run(graph, table, lambda g: q.evidence(g, value, stance, texts), render)


def _run_corpus(ws: Workspace) -> Path:
    """Return the corpus of the run the wiki was built from (the workspace corpus for older runs)."""
    run = read_json(ws.root / "raw" / "run.json", {}).get("run")
    return runs.run_corpus_path(ws, ws.runs_dir / str(run)) if run else ws.corpus_path


def _corpus_for_quotes(corpus: Optional[Path], graph: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
    path = corpus
    if path is None:
        start = None
        if graph is not None:  # an export folder, or its raw/graph.json
            start = graph if graph.is_dir() else graph.parent.parent
        try:
            ws = Workspace.find(start)
        except WorkspaceError as exc:
            err.print(f"[red]✗ Error:[/red] --quotes needs --corpus outside a workspace ({exc})")
            raise typer.Exit(1)
        if (ws.config().get("wiki") or {}).get("quotes") is False:
            err.print("[red]Error:[/red] this wiki was built without quotes (wiki.quotes: false in ddspace.yaml).")
            raise typer.Exit(1)
        path = _run_corpus(ws)
    if not path.is_file():
        err.print(f"[red]✗ Error:[/red] no corpus at {path}.")
        raise typer.Exit(1)
    return q.load_corpus(path)


@app.command("relations")
def relations_cmd(frm: Optional[str] = typer.Option(None, "--from", help="Only relations from this dimension."),
                  rtype: Optional[str] = typer.Option(None, "--type",
                                                      help="requires, affects, constrains or co_occurs_with."),
                  graph: Optional[Path] = GraphOpt, table: bool = TableOpt) -> None:
    """List the typed relations between dimensions, each as a sentence."""
    _run(graph, table, lambda g: q.relations(g, frm, rtype), lambda rows: _table(
        "Relations", ["type", "reading"], [[r["type"], r["reading"]] for r in rows]))


@app.command()
def search(text: str = typer.Argument(..., help="Words to look for in labels and descriptions."),
           kind: Optional[str] = typer.Option(None, "--kind", help="dimension, value, source, system or design."),
           graph: Optional[Path] = GraphOpt, table: bool = TableOpt) -> None:
    """Find nodes by keyword (labels first, then descriptions)."""
    _run(graph, table, lambda g: q.search(g, text, kind), lambda rows: _table(
        f"Matches for '{text}'", ["id", "kind", "label", "match"],
        [[r["id"], r["kind"], r["label"], r["match"]] for r in rows]))
