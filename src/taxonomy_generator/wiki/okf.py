"""Open Knowledge Format (OKF v0.2) view of a design-space wiki, and a conformance check.

The wiki model renders pages with ``[[wikilinks]]`` and Delve's own frontmatter (the HTML site and the
benchmark exports use that form). ``write`` converts the pages into an OKF bundle:

- every concept page has a descriptive ``type`` (Design Decision, Design Alternative, Outcome, Source, ...)
  and a ``description``; Delve's ``status`` of a value becomes ``stance`` (OKF reserves ``status`` for the
  lifecycle: draft, stable, deprecated);
- links are standard Markdown links with bundle-relative paths (``/concepts/x.md``), in the body and in
  frontmatter values;
- ``index.md`` files list each folder's pages (no frontmatter; the root one declares ``okf_version``); the
  model's front page becomes ``overview.md``;
- ``generated`` records the producer and the run time; ``log.md`` is created empty when missing and its
  entries are left to the caller (it keeps history across builds).

Spec: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import yaml

from taxonomy_generator.wiki.model import Export, Page

OKF_VERSION = "0.2"
RESERVED = ("index.md", "log.md")
WIKILINK = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
DATE_HEADING = re.compile(r"^#{1,6}\s+(\d{4}-\d{2}-\d{2})\s*$")
FRONT = re.compile(r"\A---\n(.*?)\n---\n", re.S)

TYPES = {"dimension": "Design Decision", "source": "Source", "system": "System", "design": "Design Point",
         "synthesis": "Synthesis", "reference": "Reference", "index": "Overview"}
# Folders listed by the root index, in reading order.
FOLDERS = [("concepts", "Design decisions (dimensions)"), ("entities", "Alternatives and outcomes (values)"),
           ("synthesis", "Synthesis"), ("synthesis/systems", "Systems"), ("sources", "Sources"),
           ("designs", "Design points")]
OVERVIEW = "overview"


def okf_type(page: Page) -> str:
    """Return the OKF ``type`` of a page."""
    if page.kind == "value":
        return "Outcome" if page.frontmatter.get("status") == "outcome" else "Design Alternative"
    return TYPES.get(page.kind, page.kind.replace("-", " ").title() or "Page")


def _path(page_path: str) -> str:
    return OVERVIEW if page_path == "index" else page_path


def _link(target: str, known: Sequence[str]) -> Optional[str]:
    target = target.strip()
    if target not in known:
        return None
    return f"/{_path(target)}.md"


def convert_links(text: str, known: Sequence[str]) -> str:
    """Turn ``[[path|label]]`` into ``[label](/path.md)``; links to pages not in the bundle become plain text."""
    def sub(m: re.Match) -> str:
        label = (m.group(2) or m.group(1)).strip().replace("[", "(").replace("]", ")")
        href = _link(m.group(1), known)
        return f"[{label}]({href})" if href else label
    return WIKILINK.sub(sub, text)


def _frontmatter_value(value: Any, known: Sequence[str]) -> Any:
    """Frontmatter links become bundle paths (``/concepts/x.md``); other values stay as they are."""
    if isinstance(value, str):
        m = WIKILINK.fullmatch(value.strip())
        if m:
            return _link(m.group(1), known) or (m.group(2) or m.group(1)).strip()
        return WIKILINK.sub(lambda mm: (mm.group(2) or mm.group(1)).strip(), value)
    if isinstance(value, list):
        return [_frontmatter_value(v, known) for v in value]
    if isinstance(value, dict):
        return {k: _frontmatter_value(v, known) for k, v in value.items()}
    return value


def _first_sentence(text: str) -> str:
    text = " ".join(str(text or "").split())
    m = re.match(r"(.+?[.!?])(\s|$)", text)
    return (m.group(1) if m else text)[:300]


def frontmatter(page: Page, known: Sequence[str], description: str, generated: Mapping[str, Any]) -> Dict[str, Any]:
    """Return a page's OKF frontmatter."""
    fm = {k: _frontmatter_value(v, known) for k, v in page.frontmatter.items() if k not in ("title", "type")}
    if page.kind == "value" and "status" in fm:
        fm["stance"] = fm.pop("status")
    if page.kind == "index" and "sources" in fm:
        fm["source_count"] = fm.pop("sources")   # OKF reserves `sources` for provenance entries
    out: Dict[str, Any] = {"type": okf_type(page), "title": page.title}
    if description:
        out["description"] = description
    if page.kind == "source" and fm.get("url"):
        out["resource"] = fm["url"]
    out.update(fm)
    out["generated"] = dict(generated)
    return out


def _dump(fm: Mapping[str, Any]) -> str:
    return yaml.safe_dump(dict(fm), sort_keys=False, allow_unicode=True, width=1000).strip()


def page_text(page: Page, known: Sequence[str], description: str, generated: Mapping[str, Any],
              stale_after: Optional[str] = None) -> str:
    """Return one concept page as OKF Markdown."""
    fm = frontmatter(page, known, description, generated)
    if stale_after:
        fm["stale_after"] = stale_after
    return f"---\n{_dump(fm)}\n---\n\n{convert_links(page.body, known)}"


def _folder(path: str) -> str:
    return "synthesis/systems" if path.startswith("synthesis/systems/") else (path.rsplit("/", 1)[0] if "/" in path else "")


def index_files(pages: Sequence[Page], descriptions: Mapping[str, str], name: str) -> Dict[str, str]:
    """Return ``{relative path: text}`` for the root ``index.md`` and one ``index.md`` per folder."""
    by_folder: Dict[str, List[Page]] = {}
    for p in pages:
        by_folder.setdefault(_folder(_path(p.path)), []).append(p)

    def entry(p: Page) -> str:
        desc = descriptions.get(p.path, "")
        return f"* [{p.title}](/{_path(p.path)}.md)" + (f" - {desc}" if desc else "")

    files = {}
    for folder, label in FOLDERS:
        items = sorted(by_folder.get(folder, []), key=lambda p: p.title.casefold())
        if items:
            files[f"{folder}/index.md"] = f"# {label}\n\n" + "\n".join(entry(p) for p in items) + "\n"
    root = sorted(by_folder.get("", []), key=lambda p: (p.path != "index", p.title.casefold()))
    lines = [f'---\nokf_version: "{OKF_VERSION}"\n---\n', f"# {name}\n", "## Start here\n"]
    lines += [entry(p) for p in root] + ["* [Change log](/log.md) - What changed in each build", ""]
    lines += ["## Contents\n"]
    for folder, label in FOLDERS:
        if f"{folder}/index.md" in files:
            n = len(by_folder[folder])
            lines.append(f"* [{label}](/{folder}/index.md) - {n} page{'s' if n != 1 else ''}")
    files["index.md"] = "\n".join(lines) + "\n"
    return files


def generated_at(run_label: str) -> str:
    """ISO 8601 time (with UTC offset) of a run label ``YYYYmmdd_HHMMSS`` read as local time."""
    try:
        return datetime.strptime(run_label, "%Y%m%d_%H%M%S").astimezone().isoformat(timespec="seconds")
    except ValueError:
        return datetime.now().astimezone().isoformat(timespec="seconds")


def write(export: Export, wiki: Path, name: str, generated_by: str, run_label: str,
          stale_after: Optional[str] = None) -> None:
    """Write the pages of ``export`` into ``wiki`` as an OKF bundle (``log.md`` is not touched).

    ``stale_after`` (an ISO 8601 instant) marks every concept page stale from then on (OKF §5.5).
    """
    known = [p.path for p in export.pages]
    descriptions = {}
    for n in export.graph.get("nodes") or []:
        if n.get("description"):
            descriptions[n["href"]] = _first_sentence(n["description"])
    generated = {"by": generated_by, "at": generated_at(run_label)}
    for page in export.pages:
        path = wiki / f"{_path(page.path)}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(page_text(page, known, descriptions.get(page.path, ""), generated, stale_after),
                        encoding="utf-8")
    if not (wiki / "log.md").is_file():  # entries are added by the caller; the file is kept across builds
        (wiki / "log.md").write_text("# Log\n", encoding="utf-8")
    for rel, text in index_files(export.pages, descriptions, name).items():
        (wiki / rel).parent.mkdir(parents=True, exist_ok=True)
        (wiki / rel).write_text(text, encoding="utf-8")


# ---------------------------------------------------------------- conformance check


def _split(text: str) -> Tuple[Optional[str], str]:
    m = FRONT.match(text)
    return (m.group(1), text[m.end():]) if m else (None, text)


def check(wiki: Path) -> Tuple[List[str], List[str]]:
    """Check a bundle against OKF v0.2 §11. Return (errors, warnings); broken links are warnings only."""
    errors: List[str] = []
    warnings: List[str] = []
    wiki = Path(wiki)
    if not wiki.is_dir():
        return [f"{wiki} does not exist"], []
    for path in sorted(wiki.rglob("*.md")):
        rel = path.relative_to(wiki).as_posix()
        text = path.read_text(encoding="utf-8")
        raw, body = _split(text)
        if path.name == "index.md":
            errors += _check_index(rel, raw, body)
        elif path.name == "log.md":
            errors += _check_log(rel, body)
        else:
            if raw is None:
                errors.append(f"{rel}: no YAML frontmatter")
                continue
            try:
                fm = yaml.safe_load(raw) or {}
            except yaml.YAMLError as exc:
                errors.append(f"{rel}: frontmatter is not valid YAML ({exc.__class__.__name__})")
                continue
            if not isinstance(fm, dict) or not str(fm.get("type") or "").strip():
                errors.append(f"{rel}: frontmatter has no `type`")
        for target in MD_LINK.findall(body):
            if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                continue
            clean = target.split("#")[0]
            resolved = (wiki / clean.lstrip("/")) if clean.startswith("/") else (path.parent / clean)
            if clean and not resolved.exists():
                warnings.append(f"{rel}: broken link {target}")
    return errors, warnings


def _check_index(rel: str, raw: Optional[str], body: str) -> List[str]:
    errors = []
    if raw is not None:
        fm = yaml.safe_load(raw) or {}
        if rel != "index.md" or set(fm) - {"okf_version"}:
            errors.append(f"{rel}: index files carry no frontmatter (only the root may declare okf_version)")
    if not re.search(r"(?m)^#{1,6}\s+\S", body):
        errors.append(f"{rel}: index has no section heading")
    if not re.search(r"(?m)^\s*[*-]\s+\[[^\]]+\]\([^)]+\)", body):
        errors.append(f"{rel}: index lists no linked entries")
    return errors


def _check_log(rel: str, body: str) -> List[str]:
    dates = [m.group(1) for line in body.splitlines() if (m := DATE_HEADING.match(line))]
    other = [line for line in body.splitlines() if re.match(r"^#{2,6}\s", line) and not DATE_HEADING.match(line)]
    errors = [f"{rel}: date headings must be YYYY-MM-DD ({line.strip()})" for line in other]
    if dates != sorted(dates, reverse=True):
        errors.append(f"{rel}: entries must be newest first")
    return errors
