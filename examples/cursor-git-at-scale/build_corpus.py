#!/usr/bin/env python3
"""Flatten this folder's markdown documents into a single Delve-compatible JSON
corpus file, in the same shape as the sibling examples
(examples/campus-bike/campus_bike_architecture_decisions.json and
examples/pharmacy-food/pharmacy_food_architecture_decisions.json): a flat JSON
array, one entry per document.

Delve's corpus loader (main.load_corpus) accepts a single .json file containing
either an array of plain strings, or an array of {"content": ...} objects (other
dict keys such as id/summary/explanation/category are preserved if present, see
openwiki/pipeline/ingestion-and-preprocessing.md). The sibling examples use plain
strings, so that is this script's default output shape too.

This is packaging only: it does not analyze the documents, and it introduces no
dimensions, values, or taxonomy of its own. That is Delve's job once the output
file is fed into main.py.

Usage:
    python build_corpus.py [output_path] [--with-metadata]

    output_path       default: ./cursor_git_at_scale_architecture_decisions.json
    --with-metadata   emit {"id", "title", "content"} objects instead of plain
                      strings (still a valid Delve corpus, but a different shape
                      than the sibling examples — off by default for parity).
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Named "documents", not "architecture_decisions" like the sibling examples:
# this corpus deliberately mixes context, decisions, tradeoffs, alternatives,
# lessons, and evolution write-ups, not decisions alone (see README.md).
DEFAULT_OUT = HERE / "cursor_git_at_scale_documents.json"
SKIP_FILES = {"README.md", "references.md"}
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?\n)?---\s*\n", re.DOTALL)
TITLE_RE = re.compile(r'^title:\s*"?(.*?)"?\s*$', re.MULTILINE)


def strip_frontmatter(text):
    """Return (title, body) — title from YAML frontmatter if present, else the
    first markdown heading, else None. Body has the frontmatter block removed.
    """
    m = FRONTMATTER_RE.match(text)
    title = None
    if m:
        fm = m.group(0)
        body = text[m.end():].strip()
        tm = TITLE_RE.search(fm)
        if tm:
            title = tm.group(1).strip()
    else:
        body = text.strip()
    if title is None:
        hm = re.search(r"^#\s+(.*)$", body, re.MULTILINE)
        title = hm.group(1).strip() if hm else None
    return title, body


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    with_metadata = "--with-metadata" in sys.argv
    out_path = Path(args[0]) if args else DEFAULT_OUT

    md_files = sorted(
        p for p in HERE.rglob("*.md")
        if p.name not in SKIP_FILES
    )
    if not md_files:
        print("No markdown documents found (looked under:", HERE, ")")
        sys.exit(1)

    entries = []
    for p in md_files:
        text = p.read_text(encoding="utf-8")
        title, body = strip_frontmatter(text)
        rel = p.relative_to(HERE)
        # Re-embed the title as a heading inside the content itself (the sibling
        # examples fold an equivalent label inline, e.g. "(Repository)"), so it
        # isn't lost once the array is flattened to plain strings.
        full_content = f"# {title}\n\n{body}" if title else body
        if with_metadata:
            entries.append({"id": rel.stem, "title": title or rel.stem, "content": full_content})
        else:
            entries.append(full_content)

    out_path.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
    shape = "objects with metadata" if with_metadata else "plain strings (matches sibling examples)"
    print(f"Wrote {len(entries)} documents to {out_path}  [{shape}]")
    for p in md_files:
        print(f"  - {p.relative_to(HERE)}")


if __name__ == "__main__":
    main()
