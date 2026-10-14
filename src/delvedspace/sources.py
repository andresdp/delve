"""Scan the workspace's source files: extract their text, keep ``sources.csv`` and flag problems."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from html import unescape
from pathlib import Path
from typing import Dict, List

from delvedspace.corpus import MAX_WORDS, MIN_WORDS, TARGET_WORDS, passages_for_source
from delvedspace.extract import clean_text, extract_html, extract_pdf, quality_flags
from delvedspace.workspace import (
    SOURCE_SUFFIXES,
    Workspace,
    WorkspaceError,
    source_files,
)

CSV_COLUMNS = ["id", "file", "title", "url", "source_type", "notes"]
NO_TEXT_LAYER_WORDS = 20  # a PDF with fewer words most likely has no text layer (scanned)

FLAG_HELP = {
    "missing": "listed in sources.csv but the file is gone",
    "empty": "no text could be extracted",
    "no_text_layer": "PDF without a text layer (scanned?): run OCR on it first, then replace the file",
    "short": "short text, possibly partial",
    "paywall": "looks like a paywall page",
    "bot_block": "looks like a bot-check page",
}

_SAVED_FROM = re.compile(r"<!--\s*saved from url=\(\d+\)(\S+?)\s*-->", re.I)
_CANONICAL = re.compile(r"<link[^>]+rel=[\"']canonical[\"'][^>]*href=[\"']([^\"']+)", re.I)
_OG_URL = re.compile(r"<meta[^>]+property=[\"']og:url[\"'][^>]*content=[\"']([^\"']+)", re.I)
_HTML_TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
_MD_HEADING = re.compile(r"^#\s+(.+)$", re.M)


@dataclass
class Source:
    """One source file and what extraction found."""

    id: str
    file: str
    format: str
    title: str = ""
    url: str = ""
    words: int = 0
    flags: List[str] = field(default_factory=list)
    sha256: str = ""


def read_csv(path: Path) -> List[Dict[str, str]]:
    """Return the rows of ``sources.csv`` (empty when the file does not exist)."""
    if not path.is_file():
        return []
    with open(path, encoding="utf-8", newline="") as fh:
        return [{k: (v or "").strip() for k, v in row.items() if k} for row in csv.DictReader(fh)]


def write_csv(path: Path, rows: List[Dict[str, str]]) -> None:
    """Write ``sources.csv``, keeping any extra columns the user added."""
    extra = [k for row in rows for k in row if k not in CSV_COLUMNS]
    columns = CSV_COLUMNS + list(dict.fromkeys(extra))
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _next_id(rows: List[Dict[str, str]]) -> str:
    numbers = [int(r["id"][1:]) for r in rows if re.fullmatch(r"s\d+", r.get("id", ""))]
    return f"s{(max(numbers) if numbers else 0) + 1:02d}"


def _html_metadata(html: str) -> Dict[str, str]:
    url = next((m.group(1) for rx in (_CANONICAL, _OG_URL, _SAVED_FROM) if (m := rx.search(html))), "")
    title = _HTML_TITLE.search(html)
    return {"url": unescape(url), "title": " ".join(unescape(title.group(1)).split()) if title else ""}


def _default_title(path: Path, text: str, html_title: str = "") -> str:
    heading = _MD_HEADING.search(text)
    if html_title:
        return html_title
    if heading:
        return heading.group(1).strip().strip("#").strip()
    return re.sub(r"[-_]+", " ", path.stem).strip().capitalize()


def extract(path: Path, url: str = "") -> tuple[str, Dict[str, str]]:
    """Return the cleaned text of one source file and any metadata found in it (HTML: url, title)."""
    fmt = SOURCE_SUFFIXES[path.suffix.lower()]
    meta: Dict[str, str] = {}
    if fmt == "pdf":
        raw = extract_pdf(path)
    elif fmt == "html":
        html = path.read_bytes().decode("utf-8", errors="replace")
        meta = _html_metadata(html)
        raw = extract_html(html, url or meta.get("url", ""))
    else:
        raw = path.read_text(encoding="utf-8", errors="replace")
    text, _removed = clean_text(raw)
    return text, meta


def scan(ws: Workspace) -> List[Source]:
    """Extract every source file, update ``sources.csv`` and the extraction manifest.

    Existing rows keep their id and the user's edits (title, url, type, notes); new files get the
    next id. Rows whose file disappeared are kept and flagged ``missing``.
    """
    rows = read_csv(ws.sources_csv)
    by_file = {r.get("file", ""): r for r in rows}
    ws.text_dir.mkdir(parents=True, exist_ok=True)
    found: Dict[str, Source] = {}

    for path in source_files(ws.sources_dir):
        rel = path.relative_to(ws.sources_dir).as_posix()
        row = by_file.get(rel)
        text, meta = extract(path, (row or {}).get("url", ""))
        if row is None:
            row = {"id": _next_id(rows), "file": rel, "title": _default_title(path, text, meta.get("title", "")),
                   "url": meta.get("url", ""), "source_type": "", "notes": ""}
            rows.append(row)
            by_file[rel] = row
        n_words = len(text.split())
        fmt = SOURCE_SUFFIXES[path.suffix.lower()]
        if fmt == "pdf" and n_words < NO_TEXT_LAYER_WORDS:
            flags = ["no_text_layer"]
        elif n_words == 0:
            flags = ["empty"]
        else:
            flags = quality_flags(text)
        (ws.text_dir / f"{row['id']}.md").write_text(text + "\n", encoding="utf-8")
        found[row["id"]] = Source(row["id"], rel, fmt, row.get("title", ""), row.get("url", ""), n_words, flags,
                                  hashlib.sha256(path.read_bytes()).hexdigest())

    for row in rows:
        if row["id"] not in found:
            suffix = Path(row.get("file", "")).suffix.lower()
            found[row["id"]] = Source(row["id"], row.get("file", ""), SOURCE_SUFFIXES.get(suffix, "?"),
                                      row.get("title", ""), row.get("url", ""), 0, ["missing"])
            (ws.text_dir / f"{row['id']}.md").unlink(missing_ok=True)

    write_csv(ws.sources_csv, rows)
    ordered = [found[r["id"]] for r in rows]
    ws.manifest_path.write_text(json.dumps([asdict(s) for s in ordered], indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8")
    return ordered


def load_manifest(ws: Workspace) -> List[Source]:
    """Return the sources recorded by the last scan (empty before the first one)."""
    if not ws.manifest_path.is_file():
        return []
    return [Source(**entry) for entry in json.loads(ws.manifest_path.read_text(encoding="utf-8"))]


def usable(source: Source) -> bool:
    """Return whether a source goes into the corpus (it has text and its file exists)."""
    return source.words > 0 and not {"missing", "empty", "no_text_layer"} & set(source.flags)


def build_corpus(ws: Workspace, target: int = TARGET_WORDS, min_words: int = MIN_WORDS,
                 max_words: int = MAX_WORDS) -> List[dict]:
    """Split every usable source's extracted text into passages and write ``corpus.json``."""
    sources = load_manifest(ws)
    if not sources:
        raise WorkspaceError("No sources scanned yet. Run `ddspace sources` first.")
    corpus = [p for s in sources for p in source_passages(ws, s, target, min_words, max_words)]
    ws.corpus_path.write_text(json.dumps(corpus, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return corpus


def source_passages(ws: Workspace, source: Source, target: int = TARGET_WORDS, min_words: int = MIN_WORDS,
                    max_words: int = MAX_WORDS) -> List[dict]:
    """Return one scanned source's passages (empty when it is not usable)."""
    text_file = ws.text_dir / f"{source.id}.md"
    if not usable(source) or not text_file.is_file():
        return []
    return passages_for_source(source.id, text_file.read_text(encoding="utf-8"), source.title, source.url,
                               from_pdf=source.format == "pdf", target=target, min_words=min_words,
                               max_words=max_words)


def append_to_corpus(ws: Workspace, source_ids: List[str]) -> List[dict]:
    """Add the passages of ``source_ids`` to ``corpus.json``; existing passages are kept as they are.

    Returns the added passages (what a test update classifies).
    """
    corpus = json.loads(ws.corpus_path.read_text(encoding="utf-8")) if ws.corpus_path.is_file() else []
    wanted = set(source_ids)
    corpus = [p for p in corpus if p.get("source_id") not in wanted]
    added = [p for s in load_manifest(ws) if s.id in wanted for p in source_passages(ws, s)]
    ws.corpus_path.write_text(json.dumps(corpus + added, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return added
