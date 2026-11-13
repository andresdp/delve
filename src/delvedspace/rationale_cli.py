"""``ddspace rationale``: check the design rationale files coding agents write, and render them as explainer pages.

JSON by default (for agents); ``check --table`` for people.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict, NoReturn, Optional, Tuple

import typer
from rich.console import Console
from rich.markup import escape

from delvedspace import query_cli, rationale
from delvedspace.wiki_build import HTML_DIR
from delvedspace.workspace import CONFIG_NAME, Workspace, WorkspaceError
from taxonomy_generator.wiki import explainer, render
from taxonomy_generator.wiki import query as q

app = typer.Typer(
    help="Check design rationale files (ddspace-rationale/6) and render them as explainer pages. "
         "JSON by default (for agents); --table for people.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
console = Console()
err = Console(stderr=True)


def _fail(message: str, table: bool) -> NoReturn:
    """Exit 2 with an error object: a usage error, an unreadable file or a graph that cannot be loaded."""
    err.print(f"[red]✗ Error:[/red] {escape(message)}")
    if not table:
        typer.echo(json.dumps({"error": message}, indent=2, ensure_ascii=False))
    raise typer.Exit(2)


def _graph_path(graph: Optional[Path]) -> Path:
    if graph is not None:
        return query_cli._graph_path(graph)
    return Workspace.find().root / "raw" / "graph.json"


def _load(file: Path, table: bool) -> Any:
    try:
        return rationale.load(file)
    except rationale.RationaleError as exc:
        _fail(str(exc), table)


def _space(doc: Any, graph: Optional[Path], table: bool) -> Tuple[Optional[q.Graph], Optional[str], Optional[Path]]:
    """Load the graph a file that names a space is checked against: (graph, its SHA-256, raw/graph.json path)."""
    if not rationale.names_space(doc):  # a zero-shot file (space: null) is checked against its own names
        return None, None, None
    try:
        path = _graph_path(graph)
        return q.load(path), rationale.file_sha256(path), path
    except WorkspaceError as exc:
        _fail(f"The file names a space, but {exc} Pass --graph <export folder>.", table)
    except (q.QueryError, OSError, ValueError) as exc:
        _fail(f"The file names a space, but its graph cannot be loaded: {exc}", table)


def _render(result: Dict[str, Any], doc: Any) -> None:
    problems = result["problems"]
    name = doc.get("id") if isinstance(doc, dict) else None
    errors = sum(p["severity"] == "error" for p in problems)
    if not problems:
        console.print(f"[green]✓[/green] {escape(str(name or 'rationale'))}: no problems")
    else:  # one entry per problem, the message on its own line: paths are too long for a table column
        console.print(f"[bold]{escape(str(name or 'rationale'))}: {errors} errors, "
                      f"{len(problems) - errors} warnings[/bold]")
        for p in problems:
            mark = "[red]✗[/red]" if p["severity"] == "error" else "[yellow]![/yellow]"
            console.print(f"{mark} {p['code']}  {escape(p['path'] or '/')}", soft_wrap=True)
            console.print(f"  {escape(p['message'])}", soft_wrap=True)
    if result["resolved"]:
        query_cli._table("Resolved ids", ["id", "label"], [[r["id"], r["label"]] for r in result["resolved"]])


@app.command()
def check(file: Path = typer.Argument(..., help="The rationale file (ddspace-rationale/6 JSON)."),
          graph: Optional[Path] = query_cli.GraphOpt, table: bool = query_cli.TableOpt) -> None:
    """Check a rationale file: its structure, and with a space its ids, relations, evidence and graph hash.

    Exit code 0 when clean (warnings allowed), 1 on errors, 2 when the file or the space's graph cannot be read.
    """
    doc = _load(file, table)
    loaded, sha, _ = _space(doc, graph, table)
    result = rationale.check(doc, loaded, sha)
    if table:
        _render(result, doc)
    else:
        typer.echo(json.dumps(result, indent=2, ensure_ascii=False))
    raise typer.Exit(0 if result["ok"] else 1)


def _check_out(out: Path) -> None:
    """Exit 2 unless ``out`` is inside the current folder and any ``out/assets`` there is ddspace's own."""
    here, target = Path.cwd().resolve(), out.resolve()
    if target != here and here not in target.parents:
        _fail(f"--out {out} is outside the current folder ({here}): pass a folder inside it.", False)
    foreign = explainer.foreign_assets(target)
    if foreign is not None:
        _fail(f"{foreign} exists and ddspace did not create it (no {explainer.ASSETS_MARKER}): "
              "choose another --out folder.", False)


def html_dir(root: Path) -> Path:
    """Return the HTML folder of the wiki in ``root``: ``site/`` (``ddspace wiki build``) or ``html/`` (an export)."""
    for name in (HTML_DIR, "html"):
        if (root / name / "index.html").is_file() or (root / name / "graph.html").is_file():
            return root / name
    return root / HTML_DIR


@app.command()
def build(file: Path = typer.Argument(..., help="The rationale file (ddspace-rationale/6 JSON)."),
          out: Optional[Path] = typer.Option(None, "--out", help="Write a standalone folder (DIR/explainers/<id>.html "
                                             "and DIR/assets/) instead of into the workspace's wiki. Required "
                                             "for a file without a space and outside a workspace. DIR must be "
                                             "inside the current folder."),
          graph: Optional[Path] = query_cli.GraphOpt) -> None:
    """Check a rationale file, then render it as an explainer page; print the page path as JSON.

    In a workspace, the file is copied to rationale/<id>.json and the page is written to
    site/explainers/<id>.html, next to the wiki pages it links to, and listed on the HTML index; every
    `ddspace wiki build` re-renders it. With --out DIR, a standalone folder is written
    (with a space, its links point into the wiki the file was checked against); run inside the space's own
    workspace (no --graph), the page also goes into the wiki, as `wiki_page`. A file with errors writes
    nothing: exit code 1 with the check result. Exit code 2 for an unreadable file, a graph that cannot be
    loaded, a missing --out, an --out DIR outside the current folder or whose assets/ ddspace did not create,
    an id that cannot name a file, or an id another file in rationale/ already declares.
    """
    doc = _load(file, False)
    if not rationale.names_space(doc) and out is None:
        _fail("A file without a space (space: null) renders outside any wiki: pass --out DIR.", False)
    if out is not None:
        _check_out(out)
    loaded, sha, graph_file = _space(doc, graph, False)
    result = rationale.check(doc, loaded, sha)
    if not result["ok"]:
        typer.echo(json.dumps(result, indent=2, ensure_ascii=False))
        raise typer.Exit(1)
    rid = str(doc["id"])
    if not rationale.safe_id(rid):
        _fail(f"The id '{rid}' cannot name a file: use letters, digits, '.', '_' and '-'.", False)
    changed = any(p["code"] == "graph_changed" for p in result["problems"])
    root = graph_file.resolve().parent.parent if graph_file is not None else None
    copied, note, page = None, None, None
    # Inside the space's own workspace (no --graph), the page always goes into its wiki, --out or not; --out then
    # also writes the standalone folder. With --graph (another workspace, as the study runner passes), --out alone.
    here = Path.cwd().resolve()
    into_wiki = out is None or (graph is None and root is not None and (root / CONFIG_NAME).is_file()
                                and (here == root or root in here.parents))
    if out is not None:
        page = explainer.write_standalone(doc, loaded, out, wiki_html=html_dir(root) if root else None,
                                          graph_changed=changed)
    wiki_page = None
    if into_wiki:
        if not (root / CONFIG_NAME).is_file():
            _fail(f"{root} is not a workspace (no {CONFIG_NAME}): pass --out DIR to write a standalone page.", False)
        copied = root / "rationale" / f"{rid}.json"
        others = rationale.declared_by(root, rid, skip=copied)
        if others and out is None:
            _fail(f"The id '{rid}' is already declared by {', '.join(str(o) for o in others)}: give the file its "
                  "own id, or remove the other file.", False)
        if others:
            copied, note = None, (f"not added to the wiki: the id '{rid}' is already declared by "
                                  f"{', '.join(str(o) for o in others)}")
        else:
            copied.parent.mkdir(parents=True, exist_ok=True)
            if not (copied.exists() and copied.samefile(file)):
                shutil.copyfile(file, copied)
            site = html_dir(root)
            wiki_page = explainer.write_page(doc, loaded, site, wiki_html=site, graph_changed=changed)
            # `ddspace wiki build` re-renders every file in rationale/, so the page is listed in raw/exported.json
            # as the build would list it (a later build that cannot render it, a broken file, then removes it).
            same = graph_file.resolve() == (root / "raw" / "graph.json").resolve()  # the graph scan would load
            entries = rationale.scan(root, site, loaded, sha) if same else rationale.scan(root, site)
            explainer.write_index(site, rationale.index_entries(entries))
            render.add_to_manifest(root, [wiki_page])
    payload = {"page": str(page or wiki_page), "rationale": str(copied) if copied else None,
               "problems": result["problems"]}
    if out is not None and wiki_page is not None:
        payload["wiki_page"] = str(wiki_page)
    if note:
        payload["note"] = note
    typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))


@app.command("list")
def list_cmd(graph: Optional[Path] = query_cli.GraphOpt, table: bool = query_cli.TableOpt) -> None:
    """List the workspace's rationale files (rationale/*.json): id, mode, alternatives, status and page.

    Status: ok; changed (clean, but written against an earlier graph: its page shows a banner); broken (errors
    in `ddspace rationale check`, an id another file also declares, or a page that failed to render:
    `ddspace wiki build` skips it). The page is null until the file is rendered. With --graph, the folder
    listed is the one that holds that raw/graph.json.
    """
    try:
        root = Workspace.find().root if graph is None else query_cli._graph_path(graph).resolve().parent.parent
    except WorkspaceError as exc:
        _fail(str(exc), table)
    entries = rationale.scan(root, html_dir(root))
    if not table:
        typer.echo(json.dumps([{k: e[k] for k in ("id", "mode", "alternatives", "status", "page", "file", "problems")}
                               for e in entries], indent=2, ensure_ascii=False))
        return
    if not entries:
        console.print(f"No rationale files in {escape(str(root / rationale.RATIONALE_DIR))}.")
        return
    query_cli._table("Rationale files", ["id", "mode", "alternatives", "status", "page"],
                     [[e["id"], e["mode"] or "", str(e["alternatives"]), e["status"],
                       str(Path(e["page"]).relative_to(root)) if e["page"] else ""] for e in entries])
